import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.state import AgentState

def analyze_risk(state: AgentState) -> dict:
    try:
        ticker = state.get("ticker", "Unknown")
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2 # Lower temperature for more analytical/pessimistic tone
        )
        prompt = ChatPromptTemplate.from_template(
            "You are a bearish, pessimistic financial risk manager. "
            "Write a highly critical 1-paragraph risk assessment for the stock {ticker}. "
            "Focus strictly on vulnerabilities, fierce competition, macroeconomic threats, and regulatory risks."
        )
        chain = prompt | llm
        response = chain.invoke({"ticker": ticker})
        return {"bear_thesis": response.content}
    except Exception as e:
        return {"bear_thesis": f"Error: {str(e)}"}