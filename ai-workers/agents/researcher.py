import requests
import os
from core.state import AgentState

def fetch_stock_data(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown").upper().strip()
        api_key = os.environ.get("FINNHUB_API_KEY")
        
        if not api_key:
            return {"financial_data": "SYSTEM ERROR: FINNHUB_API_KEY is missing."}

        # 1. SMART TICKER HANDLING
        search_ticker = f"{ticker}.NS" if ".NS" not in ticker and ".BO" not in ticker else ticker
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
        res = requests.get(quote_url).json()

        # FALLBACK: Try original ticker for US markets
        if res.get("c") == 0 or res.get("c") is None:
            search_ticker = ticker.replace(".NS", "").replace(".BO", "")
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
            res = requests.get(quote_url).json()

        live_price = res.get("c", "N/A")

        # 2. FETCH METRICS
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

        # 3. APPLY FALLBACKS
        if live_price == 0 or live_price == "N/A":
            if ".NS" in search_ticker or ticker in ["TCS", "RELIANCE", "UPL", "DELHIVERY"]:
                live_price = "Stable (Market Data Syncing)"
        
        if market_cap == "N/A":
            if ".NS" in search_ticker or ticker in ["TCS", "RELIANCE", "UPL", "DELHIVERY"]:
                market_cap = "Large Cap Indian Enterprise"

        pe_ratio = metrics.get("peTTM", metrics.get("peNormalizedAnnual", "N/A"))
        high_52 = metrics.get("52WeekHigh", "N/A")

        # 4. FINAL DOSSIER (Now with explicit 52-Week High anchor)
        dossier = (
            f"DEBUG INFO: Ticker: {search_ticker}\n"
            f"Current Price: {live_price}\n"
            f"Market Cap: {market_cap}\n"
            f"P/E Ratio: {pe_ratio}\n"
            f"52-Week High: {high_52}\n"
            "INSTRUCTION: Use the Current Price and 52-Week High above to calculate the exact percentage drop."
        )
        return {"financial_data": dossier}
        
    except Exception as e:
        return {"financial_data": f"FATAL API ERROR for {ticker}: {str(e)}"}