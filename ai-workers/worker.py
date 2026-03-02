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

from redis.asyncio import Redis

load_dotenv()

# --- 1. GLOBAL REDIS CONNECTION ---
redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
redis_conn = Redis.from_url(redis_url, health_check_interval=30)

# --- THE DUMMY WEB SERVER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "AI Worker is alive!", 200

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_dummy_server, daemon=True).start()

async def process_job(job, job_token):
    ticker = None
    
    # 1. FIX THE BYTES ISSUE: Decode the ID into a pure string
    job_id_str = job.id.decode('utf-8') if isinstance(job.id, bytes) else str(job.id)
    job_key = f"bull:analysis-queue:{job_id_str}"
    
    print(f"DEBUG: Searching Redis for exact key: {job_key}", flush=True)

    try:
        # 2. Pull the raw hash directly from Redis
        raw_hash = await redis_conn.hgetall(job_key)
        
        if not raw_hash:
            print(f"DEBUG: Redis returned NOTHING for key: {job_key}", flush=True)
        else:
            # 3. Extract the 'data' field
            if b'data' in raw_hash:
                data_str = raw_hash[b'data'].decode('utf-8')
                print(f"DEBUG: Found data string in Redis: {data_str}", flush=True)
                
                # Parse the JSON string Node.js sent
                parsed_data = json.loads(data_str)
                ticker = parsed_data.get("ticker")
            else:
                print(f"DEBUG: Hash found, but no 'data' field. Hash contents: {raw_hash}", flush=True)
                
    except Exception as e:
        print(f"Manual fetch failed: {str(e)}", flush=True)

    # --- FALLBACK ---
    if not ticker:
        ticker = job.data.get("ticker") if isinstance(job.data, dict) else None

    if not ticker:
        print(f"CRITICAL: Job {job_id_str} completely failed to find a ticker.", flush=True)
        return {"error": "No ticker found"}

    # --- THE ANALYSIS LOGIC ---
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
    print(f"Initializing Worker...", flush=True)
    worker = Worker(
        "analysis-queue", 
        process_job, 
        {
            "connection": redis_conn,
            "lockDuration": 300000, 
            "maxStalledCount": 0    
        }
    )
    print("Worker is live. Waiting for jobs...", flush=True)
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped manually", flush=True)
