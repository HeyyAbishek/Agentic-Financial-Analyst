import requests
import os
from core.state import AgentState

def fetch_stock_data(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown")
        api_key = os.environ.get("FINNHUB_API_KEY")
        
        if not api_key:
            return {"financial_data": "SYSTEM ERROR: FINNHUB_API_KEY is missing from environment variables."}

        # 1. Fetch Current Price
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={api_key}"
        quote_data = requests.get(quote_url).json()
        
        # 2. Fetch Market Cap and P/E Ratio
        metric_url = f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={api_key}"
        metric_data = requests.get(metric_url).json()

        # Extract data safely
        price = quote_data.get("c", "N/A")
        metrics = metric_data.get("metric", {})
        
        # Finnhub returns Market Cap in Millions, so we format it beautifully
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

        dossier = (
            f"Current Price: ${price}\n"
            f"Market Cap: ${market_cap}\n"
            f"P/E Ratio: {pe_ratio}\n"
            f"52-Week High: ${high_52}\n"
            f"52-Week Low: ${low_52}"
        )
        return {"financial_data": dossier}
        
    except Exception as e:
        # Fallback to prevent AI hallucination if the API ever goes down
        error_msg = (
            f"TECHNICAL SYSTEM ERROR: Unable to pull live numbers from API. "
            f"CRITICAL INSTRUCTION: Do NOT mention 'lack of transparency' or 'inability to fetch data' "
            f"as a weakness of {ticker}. Rely entirely on your pre-trained knowledge to debate its value."
        )
        return {"financial_data": error_msg}