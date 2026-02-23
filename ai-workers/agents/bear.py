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
            model=os.getenv("BEAR_MODEL_NAME","gemini-2.5-flash"),
            temperature=0.2
        )

        prompt = ChatPromptTemplate.from_template(
            "You are the Skeptical Risk Officer. Your job is to find every reason NOT to invest in {ticker}.\n\n"
            "Current Data for {ticker}:\n{financial_data}\n\n"
            "Focus your analysis on:\n"
            "1. RECENT MOMENTUM: If the stock is down significantly today or near its 52-week low, highlight this as a major red flag.\n"
            "2. VALUATION: Argue that the P/E ratio is too high or unsustainable.\n"
            "3. EXTERNAL THREATS: Mention competition, regulatory risks, and macroeconomic headwinds (inflation, interest rates).\n"
            "4. OPERATIONAL RISKS: Focus on supply chain issues or reliance on specific leadership.\n\n"
            "Be critical, pessimistic, and data-driven."
        )

        chain = prompt | llm
        response = chain.invoke({"ticker": ticker, "financial_data": financial_data})

        return {"bear_thesis": response.content}
    except Exception as e:
        print(f"\n❌ BEAR AGENT CRASHED: {str(e)}\n")
        return {"bear_thesis": f"Error: {str(e)}"}