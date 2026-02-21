from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.graph import app as graph_app
from core.state import AgentState

router = APIRouter()

class AnalyzeRequest(BaseModel):
    ticker: str

@router.post("/worker/analyze")
async def analyze_stock(request: AnalyzeRequest):
    """
    Endpoint to trigger the AI analysis workflow.
    """
    try:
        # Initialize state
        initial_state: AgentState = {
            "ticker": request.ticker,
            "user_query": f"Analyze {request.ticker}",
            "financial_data": {},
            "agent_scratchpad": [],
            "final_recommendation": None
        }

        # Run the workflow
        # invoke returns the final state
        result = await graph_app.ainvoke(initial_state)

        return {
            "status": "success",
            "ticker": request.ticker,
            "financial_data": result.get("financial_data"),
            "recommendation": result.get("final_recommendation"),
            "scratchpad": result.get("agent_scratchpad")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
