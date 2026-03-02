import asyncio
import os
import threading
import json
from dotenv import load_dotenv
from bullmq import Worker
from flask import Flask
from core.graph import app as graph_app
from core.state import AgentState
from redis.asyncio import Redis

load_dotenv()

# --- 1. SAFE REDIS CONNECTION ---
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
    # --- 🚨 THE ULTIMATE GHOST BUSTER 🚨 ---
    # We force the library to use a clean string so it saves to the correct Node.js folder!
    if isinstance(job.id, bytes):
        job.id = job.id.decode('utf-8')
        
    job_id_str = str(job.id)
    job_key = f"bull:analysis-queue:{job_id_str}"
    
    ticker = None
    try:
        raw_hash = await redis_conn.hgetall(job_key)
        if raw_hash and b'data' in raw_hash:
            data_str = raw_hash[b'data'].decode('utf-8')
            parsed_data = json.loads(data_str)
            ticker = parsed_data.get("ticker")
    except Exception as e:
        print(f"Manual fetch failed: {str(e)}", flush=True)

    if not ticker:
        print(f"CRITICAL: Job {job_id_str} has no ticker.", flush=True)
        return {"error": "No ticker found"}

    # --- THE ANALYSIS LOGIC ---
    print(f"Starting analysis on ticker: {ticker}...", flush=True)
    
    try:
        initial_state: AgentState = {
            "ticker": ticker,
            "user_query": (
                f"Analyze {ticker}. 🚨 CRITICAL DATA SANITY CHECK: "
                "1. If 'currentPrice' is 0 or N/A, do NOT assume bankruptcy. It is a data feed error for OTC/International stocks. "
                "2. Check if the price/market cap is in USD or local currency (e.g., ₩ KRW for Samsung). "
                "3. Samsung (SSNLF) is NOT at 0; its real price is ~₩85,000 KRW or ~$65 USD. "
                "4. If data looks impossible (like a 100% drop), search for the REAL current price manually before giving a verdict."
            ),
            "financial_data": {},
            "agent_scratchpad": [],
            "final_recommendation": None
        }
        
        result = await graph_app.ainvoke(initial_state)
        recommendation = result.get("final_recommendation")
        
        # FORCE THE AI OBJECT INTO A PLAIN STRING
        final_text = str(recommendation)
        
        print(f"SUCCESS: Analysis finished for {ticker}. Verdict: {final_text}", flush=True)
        
        # BullMQ will now save this to the CORRECT key because we fixed job.id!
        return final_text 
        
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}", flush=True)
        raise e

async def main():
    print(f"Initializing Final Production Worker...", flush=True)
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
