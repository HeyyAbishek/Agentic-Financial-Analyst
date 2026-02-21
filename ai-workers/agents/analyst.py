from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from core.state import AgentState
import os

def analyst_node(state: AgentState) -> AgentState:
    """
    Analyzes the financial data and generates an investment thesis using Groq.
    """
    ticker = state["ticker"]
    financial_data = state["financial_data"]
    
    # Initialize scratchpad if it doesn't exist
    scratchpad = state.get("agent_scratchpad", [])
    
    # Check if we have valid financial data
    if "error" in financial_data:
        scratchpad.append(f"Analyst: Skipping analysis due to missing data for {ticker}.")
        return {
            "final_recommendation": "Analysis Failed: Missing Data",
            "agent_scratchpad": scratchpad
        }

    scratchpad.append(f"Analyst: Generating investment thesis for {ticker}...")
    
    try:
        # Initialize LLM
        llm = ChatGroq(model="llama-3.3-70b-versatile")
        
        # Prepare the prompt
        system_prompt = """You are an elite hedge fund analyst. 
        Your task is to analyze the provided financial data and formulate a concise investment thesis.
        
        You must provide:
        1. A clear recommendation: Bullish, Bearish, or Hold.
        2. A brief justification based on the data (Market Cap, Price, 52-Week High/Low).
        3. Key risks or opportunities.
        
        Keep your response professional, data-driven, and under 200 words."""
        
        user_message = f"""
        Ticker: {ticker}
        Current Price: {financial_data.get('current_price')} {financial_data.get('currency')}
        Market Cap: {financial_data.get('market_cap')}
        52-Week High: {financial_data.get('fifty_two_week_high')}
        52-Week Low: {financial_data.get('fifty_two_week_low')}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_message)
        ])
        
        # Invoke LLM
        chain = prompt | llm
        response = chain.invoke({})
        thesis = response.content
        
        scratchpad.append(f"Analyst: Thesis generated for {ticker}.")
        
        return {
            "final_recommendation": thesis,
            "agent_scratchpad": scratchpad
        }
        
    except Exception as e:
        error_message = f"Analyst: Error generating thesis: {str(e)}"
        scratchpad.append(error_message)
        return {
            "final_recommendation": f"Error: {str(e)}",
            "agent_scratchpad": scratchpad
        }
