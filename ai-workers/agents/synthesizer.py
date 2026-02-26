import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from core.state import AgentState

def synthesize_debate(state: AgentState) -> dict:
    try:
        bull_thesis = state.get("bull_thesis", "No bull thesis provided.")
        bear_thesis = state.get("bear_thesis", "No bear thesis provided.")
        ticker = state.get("ticker", "Unknown")

        # Initialize the Groq model (The Judge)
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("JUDGE_MODEL_NAME","llama-3.3-70b-versatile"),
            max_retries=3,
        )
        # Notice how we only use {} for the exact variables we are passing in
        prompt = ChatPromptTemplate.from_template(
           "You are a bold, decisive Lead Investment Hedge Fund Manager. "
            "Your job is to review the Bull and Bear theses for {ticker} and make a definitive call. "
            "Do not be overly cautious. Avoid 'Neutral' unless the data is perfectly balanced. "
            "If the growth potential is massive, go Bullish. If the risks are too high, go Bearish.\n\n"
            "CRITICAL RULE: You MUST explicitly cite the specific Current Price, Market Cap, and P/E Ratio in your final justification. Do not make generic statements about valuation without quoting the exact numbers.\n\n"
            "Bull Thesis:\n{bull_thesis}\n\n"
            "Bear Thesis:\n{bear_thesis}\n\n"
            "You MUST use this EXACT format:\n"
            "**Final Recommendation:** [Bullish, Bearish, or Neutral]\n\n"
            "**Justification:**\n"
            "[Your detailed, decisive, and data-backed reasoning here]"
        )


        chain = prompt | llm
        
        # We pass exactly the three variables the prompt expects
        response = chain.invoke({
            "ticker": ticker,
            "bull_thesis": bull_thesis,
            "bear_thesis": bear_thesis
        })

        return {"final_recommendation": response.content}
        
    except Exception as e:
        return {"final_recommendation": f"Synthesis Failed: {str(e)}"}