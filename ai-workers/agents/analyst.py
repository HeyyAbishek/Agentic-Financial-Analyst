import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from core.state import AgentState

def analyze_growth(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown")
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-8b-instant"
        )
        prompt = ChatPromptTemplate.from_template(
            "You are a bullish financial analyst. Write a highly optimistic 1-paragraph investment "
            "thesis for the stock {ticker}. Focus on growth, market dominance, and future opportunities."
        )
        chain = prompt | llm
        response = chain.invoke({"ticker": ticker})
        return {"bull_thesis": response.content}
    except Exception as e:
        return {"bull_thesis": f"Error: {str(e)}"}