import requests
import os
import yfinance as yf
from core.state import AgentState

def fetch_stock_data(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown").upper().strip()
        api_key = os.environ.get("FINNHUB_API_KEY")
        
        if not api_key:
            return {"financial_data": "SYSTEM ERROR: FINNHUB_API_KEY is missing."}

        # 1. TRY FINNHUB FIRST
        search_ticker = f"{ticker}.NS" if ".NS" not in ticker and ".BO" not in ticker else ticker
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
        res = requests.get(quote_url).json()

        # Fallback to original ticker for US markets
        if res.get("c") == 0 or res.get("c") is None:
            search_ticker = ticker.replace(".NS", "").replace(".BO", "")
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
            res = requests.get(quote_url).json()

        live_price = res.get("c", 0)

        # 2. 🚨 THE "GOD TIER" FALLBACK (If Finnhub is 0 or it's Indian Stock)
        if live_price == 0 or live_price == 0.0 or ".NS" in ticker:
            print(f"Finnhub failed for {ticker}. Initiating Yahoo Finance Scraper...", flush=True)
            try:
                stock = yf.Ticker(ticker)
                fast = stock.fast_info
                
                live_price = fast.get('lastPrice', 0)
                market_cap_raw = fast.get('marketCap', 0)
                high_52 = fast.get('yearHigh', "N/A")
                pe_ratio = stock.info.get('trailingPE', "N/A")
                
                # Format Market Cap
                if market_cap_raw >= 1_000_000_000_000:
                    market_cap = f"{market_cap_raw / 1_000_000_000_000:.2f} Trillion"
                else:
                    market_cap = f"{market_cap_raw / 1_000_000_000:.2f} Billion"
                
                source = "Yahoo Finance (Scraped)"
            except Exception as e:
                return {"financial_data": f"SCRAPER ERROR: {str(e)}"}
        else:
            # 3. IF FINNHUB WORKED, GET METRICS
            metric_url = f"https://finnhub.io/api/v1/stock/metric?symbol={search_ticker}&metric=all&token={api_key}"
            m_res = requests.get(metric_url).json()
            metrics = m_res.get("metric", {})
            
            market_cap_raw = metrics.get("marketCapitalization", 0)
            market_cap = f"{market_cap_raw / 1000:.2f} Billion" if market_cap_raw > 0 else "N/A"
            high_52 = metrics.get("52WeekHigh", "N/A")
            pe_ratio = metrics.get("peTTM", "N/A")
            source = "Finnhub API"

        # 4. FINAL DOSSIER
        dossier = (
            f"Data Source: {source}\n"
            f"Ticker: {ticker}\n"
            f"Current Price: {live_price}\n"
            f"Market Cap: {market_cap}\n"
            f"P/E Ratio: {pe_ratio}\n"
            f"52-Week High: {high_52}\n"
            "NOTE: Compare Current Price vs 52-Week High carefully for currency/scaling."
        )
        return {"financial_data": dossier}
        
    except Exception as e:
        return {"financial_data": f"FATAL ERROR: {str(e)}"}
