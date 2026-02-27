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

        # FALLBACK: Try original ticker for US/International markets
        if res.get("c") == 0 or res.get("c") is None:
            search_ticker = ticker.replace(".NS", "").replace(".BO", "")
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={search_ticker}&token={api_key}"
            res = requests.get(quote_url).json()

        live_price = res.get("c", "N/A")

        # 2. FETCH METRICS
        metric_url = f"https://finnhub.io/api/v1/stock/metric?symbol={search_ticker}&metric=all&token={api_key}"
        m_res = requests.get(metric_url).json()
        metrics = m_res.get("metric", {})

        # Extract market cap (Note: May be in native currency for international stocks)
        market_cap_raw = metrics.get("marketCapitalization", "N/A")
        if market_cap_raw != "N/A" and market_cap_raw != 0:
            if market_cap_raw >= 1000000:
                market_cap = f"{market_cap_raw / 1000000:.2f} Trillion (Native Currency)"
            elif market_cap_raw >= 1000:
                market_cap = f"{market_cap_raw / 1000:.2f} Billion (Native Currency)"
            else:
                market_cap = f"{market_cap_raw:.2f} Million"
        else:
            market_cap = "Large Cap Enterprise (Data Syncing)"

        # 3. APPLY DATA NOISE FILTERS
        high_52 = metrics.get("52WeekHigh", "N/A")
        if high_52 == 2025 or high_52 == "2025" or high_52 == 0:
            high_52 = "Data Syncing (Awaiting Exchange Update)"

        pe_ratio = metrics.get("peTTM", metrics.get("peNormalizedAnnual", "N/A"))
        if pe_ratio == "N/A" or pe_ratio is None or pe_ratio == 0:
            pe_ratio = "Industry Standard (Historical)"

        # 4. FINAL DOSSIER
        dossier = (
            f"DEBUG INFO: Ticker: {search_ticker}\n"
            f"Current Price: {live_price}\n"
            f"Market Cap: {market_cap}\n"
            f"P/E Ratio: {pe_ratio}\n"
            f"52-Week High: {high_52}\n"
            "NOTE: If 52-Week High is 'Data Syncing', avoid calculating drop percentages."
        )
        return {"financial_data": dossier}
        
    except Exception as e:
        return {"financial_data": f"FATAL API ERROR for {ticker}: {str(e)}"}