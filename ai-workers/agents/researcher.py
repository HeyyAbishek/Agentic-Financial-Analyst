import yfinance as yf
from core.state import AgentState

def fetch_stock_data(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown")
        stock = yf.Ticker(ticker)
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
        return {"financial_data": f"Failed to fetch data: {str(e)}"}