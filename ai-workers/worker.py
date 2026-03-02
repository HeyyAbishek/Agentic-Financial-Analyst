import asyncio
import os
import time
import threading
import json
from dotenv import load_dotenv
from bullmq import Worker
from flask import Flask
from core.graph import app as graph_app
from core.state import AgentState

# --- NEW IMPORT FOR REDIS KEEP-ALIVE ---
from redis.asyncio import Redis

load_dotenv()

# --- 1. GLOBAL REDIS CONNECTION (The Source of Truth) ---
redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
# We make this global so process_job can manually fetch data from it
redis_conn = Redis.from_url(
    redis_url,
    health_check_interval=30
)

# --- THE DUMMY WEB SERVER HACK ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "AI Worker is alive and running!", 200

def run_dummy_server():
    # Render binds to port 10000 by default
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Start the dummy server on a separate background thread
threading.Thread(target=run_dummy_server, daemon=True).start()
# ---------------------------------

async def process_job(job, job_token):
    # --- MANUAL REDIS DATA FETCH ---
    # Since the library is returning {}, we fetch it manually from the Hash
    ticker = None
    try:
        # 1. Get the raw hash from Redis using the Job ID
        # The key in Redis is usually 'bull:analysis-queue:<ID>'
        job_key = f"bull:analysis-queue:{job.id}"
        raw_hash = await redis_conn.hgetall(job_key)
        
        # 2. Extract the 'data' field from the hash
        if raw_hash and b'data' in raw_hash:
            data_str = raw_hash[b'data'].decode('utf-8')
            parsed_data = json.loads(data_str)
            ticker = parsed_data.get("ticker")
            
    except Exception as e:
        print(f"Manual fetch failed: {str(e)}", flush=True)

    # --- FALLBACK TO LIBRARY DATA ---
    if not ticker:
        ticker = job.data.get("ticker") if isinstance(job.data, dict) else None

    if not ticker:
        print(f"DEBUG: Job {job.id} is STILL empty even after manual fetch.", flush=True)
        return {"error": "No ticker found"}

    # --- THE REST OF YOUR LOGIC ---
    print(f"Cooling down API for 2 seconds before starting {ticker}...", flush=True)
    await asyncio.sleep(2) 
    print(f"Starting analysis on ticker: {ticker}", flush=True)
    
    try:
        initial_state: AgentState = {
            "ticker": ticker,
            "user_query": f"Analyze {ticker}",
            "financial_data": {},
            "agent_scratchpad": [],
            "final_recommendation": None
        }
        result = await graph_app.ainvoke(initial_state)
        recommendation = result.get("final_recommendation")
        print(f"Analysis finished for {ticker}. Recommendation: {recommendation}", flush=True)
        return recommendation
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}", flush=True)
        raise e

async def main():
    print(f"Initializing Worker for 'analysis-queue' with Upstash...", flush=True)
    
    # 2. BullMQ Worker with 5-Minute Lock using the global connection
    worker = Worker(
        "analysis-queue", 
        process_job, 
        {
            "connection": redis_conn,
            "lockDuration": 300000, # 5 Minutes
            "maxStalledCount": 0    
        }
    )
    # ----------------------
    
    print("Worker is running and listening for jobs...", flush=True)
    
    # Keep process active and logs visible
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped manually", flush=True)
