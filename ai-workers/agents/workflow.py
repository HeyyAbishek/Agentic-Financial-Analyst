from langgraph.graph import StateGraph, END
from core.state import AgentState

# Dummy node
def start_analysis(state: AgentState):
    """
    Initial dummy node that just acknowledges the request.
    """
    return {
        "agent_scratchpad": ["Analysis started"],
        "final_recommendation": "Hold (Analysis Pending)"
    }

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("start_node", start_analysis)

# Set entry point
workflow.set_entry_point("start_node")

# Add edges
workflow.add_edge("start_node", END)

# Compile the graph
app = workflow.compile()
