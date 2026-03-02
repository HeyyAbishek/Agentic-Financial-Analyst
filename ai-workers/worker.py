import asyncio
import os
import threading
from dotenv import load_dotenv
from bullmq import Worker
from flask import Flask
from core.graph import app as graph_app
from core.state import AgentState
from redis.asyncio import Redis

load_dotenv()

# --- 1. CLEAN REDIS CONNECTION ---
# No decode_responses! We let BullMQ handle its own bytes internally.
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
    print(f"DEBUG: Job ID {job.id} picked up. Data: {job.data}", flush=True)
    
    # BullMQ automatically converts the JSON to a dictionary for us now!
    ticker = job.data.get("ticker") if isinstance(job.data, dict) else None

    if not ticker:
        print(f"CRITICAL: Job {job.id} has no ticker.", flush=True)
        return {"error": "No ticker"}

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
        
        print(f"SUCCESS: Analysis finished for {ticker}.", flush=True)
        return recommendation # BullMQ will successfully save this now!
        
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}", flush=True)
        raise e

async def main():
    print(f"Initializing Clean Production Worker...", flush=True)
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
