import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from core.state import AgentState

def analyze_risk(state: AgentState) -> dict:
    ticker = state.get("ticker", "Unknown")
    financial_data = state.get("financial_data", "No data available.")
    
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

    # --- Step 1: Attempt Gemini (Primary) ---
    try:
        print(f"Attempting Gemini analysis for {ticker}...")
        llm = ChatGoogleGenerativeAI(
              model=os.getenv("BEAR_MODEL_NAME","gemini-2.5-flash"),
            temperature=0.2,
            max_retries=2
        )
        chain = prompt | llm
        response = chain.invoke({"ticker": ticker, "financial_data": financial_data})
        return {"bear_thesis": response.content}

    except Exception as e:
        # --- Step 2: Fallback to Groq if Gemini fails ---
        print(f"⚠️ Gemini Bear failed, switching to Groq: {str(e)}")
        try:
            llm = ChatGroq(
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name="llama-3.3-70b-versatile",
                max_retries=3
            )
            chain = prompt | llm
            response = chain.invoke({"ticker": ticker, "financial_data": financial_data})
            return {"bear_thesis": response.content}
        except Exception as groq_e:
            print(f"❌ BOTH PROVIDERS FAILED: {str(groq_e)}")
            return {"bear_thesis": f"Analysis failed: {str(groq_e)}"}