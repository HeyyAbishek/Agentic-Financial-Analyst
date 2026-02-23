from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    """
    State definition for the financial analyst agent workflow.
    """
    ticker: str
    user_query: str
    financial_data: str  # Changed to str as requested for easier prompt injection
    agent_scratchpad: List[str]
    bull_thesis: Optional[str]
    bear_thesis: Optional[str]
    final_recommendation: Optional[str]
