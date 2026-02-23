from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.researcher import fetch_stock_data
from agents.analyst import analyze_growth
from agents.bear import analyze_risk
from agents.synthesizer import synthesize_debate

# Initialize the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("fetch_stock_data", fetch_stock_data)
workflow.add_node("bull_agent", analyze_growth)
workflow.add_node("bear_agent", analyze_risk)
workflow.add_node("synthesizer", synthesize_debate)

# Set entry point
workflow.set_entry_point("fetch_stock_data")

# Define edges for sequential flow
# Researcher -> Bull -> Bear -> Synthesizer -> END
workflow.add_edge("fetch_stock_data", "bull_agent")
workflow.add_edge("bull_agent", "bear_agent")
workflow.add_edge("bear_agent", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile the graph
app = workflow.compile()
