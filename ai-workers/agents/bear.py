import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.state import AgentState

def analyze_risk(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown")
        financial_data = state.get("financial_data", "No data available.")

        # Hardcoded to the exact Gemini model string
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2
        )

        prompt = ChatPromptTemplate.from_template(
            "You are a bearish, pessimistic financial risk manager. Write a highly critical 1-paragraph risk assessment for {ticker}.\n\n"
            "Use this live market data to support your claims:\n{financial_data}\n\n"
            "Focus strictly on vulnerabilities, fierce competition, high valuation, and macroeconomic threats."
        )

        chain = prompt | llm
        response = chain.invoke({"ticker": ticker, "financial_data": financial_data})

        return {"bear_thesis": response.content}
    except Exception as e:
        return {"bear_thesis": f"Error: {str(e)}"}