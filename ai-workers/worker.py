import asyncio
import os
from dotenv import load_dotenv
from bullmq import Worker
from core.graph import app as graph_app
from core.state import AgentState

load_dotenv()

async def process_job(job, job_token):
    """
    Processes a job from the queue.
    Expects job.data to contain a 'ticker' field.
    """
    ticker = job.data.get("ticker")
    if not ticker:
        print("Error: Job received without ticker")
        return {"error": "No ticker provided"}
    
    print(f"Starting analysis on ticker: {ticker}")
    
    try:
        # Initialize state for the graph
        initial_state: AgentState = {
            "ticker": ticker,
            "user_query": f"Analyze {ticker}",
            "financial_data": {},
            "agent_scratchpad": [],
            "final_recommendation": None
        }
        
        # Invoke the LangGraph workflow
        result = await graph_app.ainvoke(initial_state)
        
        recommendation = result.get("final_recommendation")
        print(f"Analysis finished for {ticker}. Recommendation: {recommendation}")
        
        return recommendation
        
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        raise e

async def main():
    # Redis connection settings - FORCED IPv4
    redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    
    print(f"Initializing Worker for 'analysis-queue' at {redis_host}:{redis_port}...")
    
    worker = Worker(
        "analysis-queue", 
        process_job, 
        {"connection": {"host": redis_host, "port": redis_port}}
    )
    
    # Keep the script running indefinitely
    print("Worker is running and listening for jobs...")
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped manually")