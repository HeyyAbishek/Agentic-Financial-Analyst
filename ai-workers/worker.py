import asyncio
import os
import threading
import json
import datetime
import requests
import yfinance as yf
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

# --- 2. THE CONSOLIDATED WEB SERVER (Fixes Cron & 404) ---
app = Flask(__name__)

@app.route('/health')
def health_check():
    # Only 2 bytes - stops "Response data too big" errors
    return "ok", 200

@app.route('/')
def home():
    return "AI Worker is Online", 200

def run_dummy_server():
    # Render uses port 10000 by default; ensures service stays awake
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Start dummy server in background thread
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 3. THE GOD-TIER STOCK FETCH LOGIC ---
def fetch_stock_data(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown").upper().strip()
        api_key = os.environ.get("FINNHUB_API_KEY")
        
        if not api_key:
            return {"financial_data": "SYSTEM ERROR: FINNHUB_API_KEY is missing."}

        # Handle Indian Market Tickers (.NS for NSE)
        search_ticker = f"{ticker}.NS" if ".NS" not in ticker and ".BO" not in ticker else ticker
        source = "Finnhub API"
        
        # Phase 1: Try Finnhub
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
        res = requests.get(quote_url).json()
        live_price = res.get("c", 0)

        # Phase 2: Yahoo Finance Fallback (Trigger for $0 or Indian Stocks)
        if live_price == 0 or live_price is None or ".NS" in search_ticker:
            try:
                print(f"🔄 Switching to yfinance for {search_ticker}...", flush=True)
                stock = yf.Ticker(search_ticker)
                
                # Using fast_info to avoid slow cached 'info' object
                live_price = stock.fast_info.get('lastPrice', "N/A")
                market_cap_raw = stock.fast_info.get('marketCap', 0)
                high_52 = stock.fast_info.get('yearHigh', "N/A")
                
                # Standard info used only for P/E (often not in fast_info)
                pe_ratio = stock.info.get('trailingPE', "N/A")
                
                # Currency/Scaling Logic (yfinance returns raw units)
                if market_cap_raw >= 1_000_000_000_000:
                    market_cap = f"{market_cap_raw / 1_000_000_000_000:.2f} Trillion"
                else:
                    market_cap = f"{market_cap_raw / 1_000_000_000:.2f} Billion"
                
                source = "Yahoo Finance (Scraped)"
            except Exception as e:
                print(f"❌ Scraper failed: {e}")
                live_price, market_cap, high_52, pe_ratio = "N/A", "N/A", "N/A", "N/A"
        else:
            # Phase 3: Finnhub Metrics (If primary API worked)
            metric_url = f"https://finnhub.io/api/v1/stock/metric?symbol={search_ticker}&metric=all&token={api_key}"
            m_res = requests.get(metric_url).json()
            metrics = m_res.get("metric", {})
            
            # Finnhub provides Market Cap in Millions
            m_cap_millions = metrics.get("marketCapitalization", 0)
            market_cap = f"{m_cap_millions / 1_000_000:.2f} Trillion" if m_cap_millions >= 1000000 else f"{m_cap_millions / 1000:.2f} Billion"
            high_52 = metrics.get("52WeekHigh", "N/A")
            pe_ratio = metrics.get("peTTM", "N/A")

        # Create Sync Timestamp (IST)
        updated_at = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")

        dossier = (
            f"Data Source: {source}\n"
            f"Ticker: {search_ticker}\n"
            f"Current Price: {live_price}\n"
            f"Market Cap: {market_cap}\n"
            f"P/E Ratio: {pe_ratio}\n"
            f"52-Week High: {high_52}\n"
            f"🕒 Last Sync: {updated_at} IST (Market Delay: 15m)\n"
        )
        return {"financial_data": dossier}
        
    except Exception as e:
        return {"financial_data": f"FATAL ERROR: {str(e)}"}

# --- 4. THE ANALYSIS WORKER LOGIC ---
async def process_job(job, job_token):
    # BullMQ ID Cleanup
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

    print(f"Starting analysis on ticker: {ticker}...", flush=True)
    
    try:
        initial_state: AgentState = {
            "ticker": ticker,
            "user_query": f"Analyze {ticker} with current market conditions.",
            "financial_data": {},
            "agent_scratchpad": [],
            "final_recommendation": None
        }
        
        result = await graph_app.ainvoke(initial_state)
        recommendation = result.get("final_recommendation")
        
        final_text = str(recommendation)
        print(f"SUCCESS: Analysis finished for {ticker}.", flush=True)
        return final_text 
        
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}", flush=True)
        raise e

async def main():
    print(f"Initializing Production AI Worker...", flush=True)
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
