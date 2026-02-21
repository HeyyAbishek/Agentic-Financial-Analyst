from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.researcher import researcher_node
from agents.analyst import analyst_node

# Initialize the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("analyst", analyst_node)

# Set entry point
workflow.set_entry_point("researcher")

# Add edges
# Flow: Researcher -> Analyst -> END
workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", END)

# Compile the graph
app = workflow.compile()
