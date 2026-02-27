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
        "You are a sophisticated, objective Investment Committee Chair. "
        "Your job is to critically evaluate the conflicting arguments from the Bull and Bear researchers for {ticker}. "
        "Do not simply agree with the most confident-sounding agent. Weigh the hard data against the risks.\n\n"
    
        "CRITICAL RULE: You MUST explicitly cite the Current Price, Market Cap, and P/E Ratio provided. "
        "If the P/E ratio is extreme (e.g., over 100), you must explain why that risk is or isn't acceptable.\n\n"
    
        "TRUST RULE: If the Researcher provides a 'Live Quote' price, you MUST use that price and ignore any other conflicting prices mentioned in the Bull or Bear theses.\n\n"
    
        "Bull Thesis:\n{bull_thesis}\n\n"
        "Bear Thesis:\n{bear_thesis}\n\n"
    
        "You MUST use this EXACT format for maximum readability:\n"
        "**Final Recommendation:** [Bullish, Bearish, or Neutral]\n\n"
        "**Justification:**\n"
        "📊 **The Math:** [Cite Current Price, Market Cap, and P/E Ratio]\n"
        "✅ **Bull Case:** [One sentence on the strongest growth driver identified]\n"
        "⚠️ **Bear Case:** [One sentence on the biggest specific risk factor identified]\n"
        "⚖️ **The Verdict:** [2-3 sentences explaining your final balanced conclusion. If the valuation is too high, do not be afraid to stay Bearish or Neutral.]"
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