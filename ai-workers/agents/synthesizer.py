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
       "You are a sophisticated, objective Investment Committee Chair for {ticker}.\n\n"
    
    "DATA INTEGRITY RULE: You MUST calculate percentages yourself. "
    "If the Current Price is {price} and the 52-Week High is {high_52}, "
    "do NOT state there was a massive crash unless the math supports it.\n\n"
    
    "CRITICAL RULE: You MUST explicitly cite the Current Price, Market Cap, and P/E Ratio.\n"
    "TRUST RULE: Use the 'Live Quote' price provided by the Researcher exclusively.\n\n"
    
    "Bull Thesis:\n{bull_thesis}\n\n"
    "Bear Thesis:\n{bear_thesis}\n\n"
    
    "You MUST use this EXACT format:\n"
    "**Final Recommendation:** [Bullish, Bearish, or Neutral]\n\n"
    "**Justification:**\n"
    "📊 **The Math:** [Cite Price, Cap, and P/E]\n"
    "✅ **Bull Case:** [One sentence growth driver]\n"
    "⚠️ **Bear Case:** [One sentence risk factor]\n"
    "⚖️ **The Verdict:** [2-3 sentences. BE HONEST about the 52-week price action. If it only dropped 5%, do not say 80%.]"
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