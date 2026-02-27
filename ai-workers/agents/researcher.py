import requests
import os
from core.state import AgentState

def fetch_stock_data(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown").upper().strip()
        api_key = os.environ.get("FINNHUB_API_KEY")
        
        # 1. SMART TICKER HANDLING
        # If the user typed DELHIVERY, we automatically try DELHIVERY.NS
        if ".NS" not in ticker and ".BO" not in ticker:
            # You can add a list of common US tickers to ignore this, 
            # or just let the first attempt fail and retry with .NS
            search_ticker = f"{ticker}.NS"
        else:
            search_ticker = ticker

        # 2. Fetch LIVE Price
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
        quote_resp = requests.get(quote_url).json()
        
        # If .NS failed, try the original (maybe it's a US stock like AAPL)
        if quote_resp.get("c") == 0 or quote_resp.get("c") is None:
            search_ticker = ticker
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
            quote_resp = requests.get(quote_url).json()

        live_price = quote_resp.get("c", "N/A")

        # 3. Fetch Metrics
        metric_url = f"https://finnhub.io/api/v1/stock/metric?symbol={search_ticker}&metric=all&token={api_key}"
        metric_resp = requests.get(metric_url).json()
        metrics = metric_resp.get("metric", {})

        # Extract metrics safely
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
        
        pe_ratio = metrics.get("peTTM", metrics.get("peNormalizedAnnual", "N/A"))
        high_52 = metrics.get("52WeekHigh", "N/A")
        low_52 = metrics.get("52WeekLow", "N/A")

        # Construct the dossier with the guaranteed live_price
        dossier = (
            f"Current Price: ₹{live_price} (Live Quote)\n"
            f"Market Cap: ₹{market_cap}\n"
            f"P/E Ratio: {pe_ratio}\n"
            f"52-Week High: ₹{high_52}\n"
            f"52-Week Low: ₹{low_52}"
        )
        return {"financial_data": dossier}
        
    except Exception as e:
        error_msg = (
            f"TECHNICAL SYSTEM ERROR: Unable to pull live numbers. "
            f"CRITICAL: Do NOT invent prices. Rely on pre-trained knowledge for {ticker}."
        )
        return {"financial_data": error_msg}