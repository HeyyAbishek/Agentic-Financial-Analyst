from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    """
    State definition for the financial analyst agent workflow.
    """
    ticker: str
    user_query: str
    financial_data: Dict[str, Any]
    agent_scratchpad: List[str]
    final_recommendation: Optional[str]
