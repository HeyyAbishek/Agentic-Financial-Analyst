import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from core.state import AgentState

def analyze_growth(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown")
        financial_data = state.get("financial_data", "No data available.")

        # Hardcoded to the correct working model!
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("BULL_MODEL_NAME","llama-3.3-70b-versatile") 
        )
        prompt = ChatPromptTemplate.from_template(
            "You are a bullish financial analyst. Write a highly optimistic 1-paragraph investment thesis for {ticker}.\n\n"
            "Use this live market data to support your claims:\n{financial_data}\n\n"
            "Focus on growth, market dominance, and future opportunities."
        )

        chain = prompt | llm
        response = chain.invoke({"ticker": ticker, "financial_data": financial_data})

        return {"bull_thesis": response.content}
    except Exception as e:
        print(f"\n❌ BULL AGENT CRASHED: {str(e)}\n")
        return {"bull_thesis": f"Error: {str(e)}"}