import asyncio
import os
import time
import threading
from dotenv import load_dotenv
from bullmq import Worker
from flask import Flask
from core.graph import app as graph_app
from core.state import AgentState

# --- NEW IMPORT FOR REDIS KEEP-ALIVE ---
from redis.asyncio import Redis

load_dotenv()

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
    # --- BRUTE FORCE DATA CHECK ---
    # We check every possible place BullMQ hides data
    raw_data = job.data
    ticker = None
    
    # Check 1: Standard data object
    if isinstance(raw_data, dict):
        ticker = raw_data.get("ticker")
    
    # Check 2: Nested data object (Common in Node -> Python)
    if not ticker and isinstance(raw_data, dict) and isinstance(raw_data.get("data"), dict):
        ticker = raw_data.get("data").get("ticker")
        
    # Check 3: The "Raw Dictionary" fallback (Library bypass)
    if not ticker:
        raw_dict = getattr(job, "__dict__", {})
        data_attr = raw_dict.get("data")
        if isinstance(data_attr, dict):
            ticker = data_attr.get("ticker")
        elif isinstance(data_attr, str):
            # Sometimes data arrives as a stringified JSON
            try:
                import json
                ticker = json.loads(data_attr).get("ticker")
            except:
                pass

    if not ticker:
        print(f"DEBUG: Job {job.id} is still empty. Full Raw Job Data: {raw_data}", flush=True)
        return {"error": "No ticker found"}

    # --- ANALYSIS LOGIC ---
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
    # --- THE PRODUCTION FIXES ---
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
    print(f"Initializing Worker for 'analysis-queue' with Upstash...", flush=True)
    
    # 1. Custom Redis connection with 30-second heartbeat
    redis_conn = Redis.from_url(
        redis_url,
        health_check_interval=30
    )
    
    # 2. BullMQ Worker with 5-Minute Lock
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
