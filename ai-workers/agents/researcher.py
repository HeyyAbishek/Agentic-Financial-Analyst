import yfinance as yf
from core.state import AgentState

def researcher_node(state: AgentState) -> AgentState:
    """
    Fetches financial data for the given ticker using yfinance.
    """
    ticker_symbol = state["ticker"]
    
    # Initialize scratchpad if it doesn't exist
    scratchpad = state.get("agent_scratchpad", [])
    scratchpad.append(f"Researcher: Fetching data for {ticker_symbol}...")
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Extract relevant data
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        market_cap = info.get("marketCap")
        fifty_two_week_high = info.get("fiftyTwoWeekHigh")
        fifty_two_week_low = info.get("fiftyTwoWeekLow")
        currency = info.get("currency", "USD")
        
        financial_data = {
            "current_price": current_price,
            "market_cap": market_cap,
            "fifty_two_week_high": fifty_two_week_high,
            "fifty_two_week_low": fifty_two_week_low,
            "currency": currency
        }
        
        scratchpad.append(f"Researcher: Successfully fetched data for {ticker_symbol}.")
        
        # Return updated state
        return {
            "financial_data": financial_data,
            "agent_scratchpad": scratchpad
        }
        
    except Exception as e:
        error_message = f"Researcher: Error fetching data for {ticker_symbol}: {str(e)}"
        scratchpad.append(error_message)
        return {
            "financial_data": {"error": str(e)},
            "agent_scratchpad": scratchpad
        }
