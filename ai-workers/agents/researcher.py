import yfinance as yf
import requests
from core.state import AgentState

def fetch_stock_data(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown")
        
        # 1. Trick Yahoo into thinking Render is a normal browser
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        stock = yf.Ticker(ticker, session=session)
        info = stock.info

        # Safely grab the live data
        price = info.get("currentPrice", info.get("regularMarketPrice", "N/A"))
        market_cap = info.get("marketCap", "N/A")
        pe_ratio = info.get("trailingPE", "N/A")
        high_52 = info.get("fiftyTwoWeekHigh", "N/A")
        low_52 = info.get("fiftyTwoWeekLow", "N/A")

        dossier = (
            f"Current Price: ${price}\n"
            f"Market Cap: ${market_cap}\n"
            f"P/E Ratio: {pe_ratio}\n"
            f"52-Week High: ${high_52}\n"
            f"52-Week Low: ${low_52}"
        )
        return {"financial_data": dossier}
    
    except Exception as e:
        # 2. Stop the AI from hallucinating if the API fails again
        error_msg = (
            f"TECHNICAL SYSTEM ERROR: Unable to pull live numbers. "
            f"CRITICAL INSTRUCTION: Do NOT mention 'lack of transparency', 'inability to fetch data', "
            f"or 'fragility' as a weakness of {ticker}. This is a backend API issue, not a company issue. "
            f"Rely entirely on your pre-trained knowledge of {ticker} to debate its value."
        )
        return {"financial_data": error_msg}