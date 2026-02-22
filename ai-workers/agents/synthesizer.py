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
            model_name="llama-3.1-8b-instant"
        )

        # Notice how we only use {} for the exact variables we are passing in
        prompt = ChatPromptTemplate.from_template(
            "You are a Senior Portfolio Manager at a top hedge fund. "
            "Your job is to make a final investment recommendation for {ticker}.\n\n"
            "You have received two opposing views from your analysts:\n"
            "--- BULL THESIS ---\n{bull_thesis}\n\n"
            "--- BEAR THESIS ---\n{bear_thesis}\n\n"
            "Weigh both arguments carefully. Provide a final, balanced recommendation "
            "(Bullish, Bearish, or Neutral) and a strong justification explaining why one analyst's "
            "argument outweighs the other."
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