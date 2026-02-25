import asyncio
import os
import time  # Added for the delay logic
import threading
from dotenv import load_dotenv
from bullmq import Worker
from flask import Flask
from core.graph import app as graph_app
from core.state import AgentState

load_dotenv()

# --- THE DUMMY WEB SERVER HACK ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "AI Worker is alive and running!", 200

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Start the dummy server on a separate background thread
threading.Thread(target=run_dummy_server, daemon=True).start()
# ---------------------------------


async def process_job(job, job_token):
    ticker = job.data.get("ticker")
    if not ticker:
        print("Error: Job received without ticker")
        return {"error": "No ticker provided"}
    
    # --- COOL DOWN LOGIC ---
    # Giving the Gemini/Groq APIs a 2-second breather to avoid rate limits
    print(f"Cooling down API for 2 seconds before starting {ticker}...")
    await asyncio.sleep(2) 
    
    print(f"Starting analysis on ticker: {ticker}")
    
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
        print(f"Analysis finished for {ticker}. Recommendation: {recommendation}")
        
        return recommendation
        
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        raise e

async def main():
    # --- THE 2-LINE FIX ---
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
    print(f"Initializing Worker for 'analysis-queue' with Upstash...")
    
    worker = Worker(
        "analysis-queue", 
        process_job, 
        {"connection": redis_url} # BullMQ accepts the Upstash rediss:// URL directly here
    )
    # ----------------------
    
    print("Worker is running and listening for jobs...")
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped manually")