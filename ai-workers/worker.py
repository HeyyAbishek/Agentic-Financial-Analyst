import asyncio
import os
import time  # Added for the delay logic
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
    # Use 10000 as default to match Render's environment
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Start the dummy server on a separate background thread
threading.Thread(target=run_dummy_server, daemon=True).start()
# ---------------------------------

async def process_job(job, job_token):
    ticker = job.data.get("ticker")
    if not ticker:
        print("Error: Job received without ticker", flush=True)
        return {"error": "No ticker provided"}
    
    # --- COOL DOWN LOGIC ---
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
        
        # This is where the heavy AI agent work happens
        result = await graph_app.ainvoke(initial_state)
        recommendation = result.get("final_recommendation")
        
        print(f"Analysis finished for {ticker}. Recommendation: {recommendation}", flush=True)
        return recommendation
        
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}", flush=True)
        raise e

async def main():
    # --- THE FIX: Custom Redis connection with 30-second heartbeat ---
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
    print(f"Initializing Worker for 'analysis-queue' with Upstash...", flush=True)
    
    # 1. Create the robust connection to prevent "Zombies"
    redis_conn = Redis.from_url(
        redis_url,
        health_check_interval=30
    )
    
    # 2. Pass the custom connection object directly to BullMQ
    worker = Worker(
        "analysis-queue", 
        process_job, 
        {
            "connection": redis_conn,
            "lockDuration": 300000, # 5 Minutes (gives plenty of time for AI debate)
            "maxStalledCount": 0    # Don't retry stalled jobs automatically
        }
    )
    # ----------------------
    
    print("Worker is running and listening for jobs...", flush=True)
    
    # Better than asyncio.Future() for Render log visibility
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped manually", flush=True)
