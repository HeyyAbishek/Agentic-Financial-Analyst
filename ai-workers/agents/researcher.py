import requests
import os
from core.state import AgentState

def fetch_stock_data(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown").upper().strip()
        api_key = os.environ.get("FINNHUB_API_KEY")
        
        if not api_key:
            return {"financial_data": "SYSTEM ERROR: FINNHUB_API_KEY is missing from environment variables."}

        # 1. TRY PRIMARY (NSE for Indian context)
        search_ticker = f"{ticker}.NS" if ".NS" not in ticker and ".BO" not in ticker else ticker
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
        res = requests.get(quote_url).json()

        # 2. FALLBACK (If NSE fails or returns 0, try original ticker for US markets)
        if res.get("c") == 0 or res.get("c") is None:
            search_ticker = ticker.replace(".NS", "").replace(".BO", "")
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
            res = requests.get(quote_url).json()

        # 3. GATHER DATA
        price = res.get("c", "N/A")
        
        metric_url = f"https://finnhub.io/api/v1/stock/metric?symbol={search_ticker}&metric=all&token={api_key}"
        m_res = requests.get(metric_url).json()
        metrics = m_res.get("metric", {})

        # Extract and format market cap
        market_cap_raw = metrics.get("marketCapitalization", "N/A")
        if market_cap_raw != "N/A":
            if market_cap_raw >= 1000000:
                market_cap = f"{market_cap_raw / 1000000:.2f} Trillion"
            elif market_cap_raw >= 1000:
                market_cap = f"{market_cap_raw / 1000:.2f} Billion"
            else:
                market_cap = f"{market_cap_raw:.2f} Million"
        else:
            market_cap = "N/A"

        # 4. FINAL DOSSIER (With Debug Info for Transparency)
        dossier = (
            f"DEBUG INFO: Final Ticker Used: {search_ticker}\n"
            f"Current Price: ₹{price} (Live Quote)\n"
            f"Market Cap: ₹{market_cap}\n"
            f"P/E Ratio: {metrics.get('peTTM', metrics.get('peNormalizedAnnual', 'N/A'))}\n"
            f"52-Week High: ₹{metrics.get('52WeekHigh', 'N/A')}\n"
            f"52-Week Low: ₹{metrics.get('52WeekLow', 'N/A')}"
        )
        return {"financial_data": dossier}
        
    except Exception as e:
        # Fallback to prevent AI hallucination
        return {"financial_data": f"FATAL API ERROR for {ticker}: {str(e)}"}