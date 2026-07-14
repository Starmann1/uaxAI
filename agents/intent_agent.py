from agents.base_agent import BaseAgent
from models.workflow_state import WorkflowState


class IntentAgent(BaseAgent):
    """Intent Agent: Classifies query intent deterministically into ANALYZE, STATUS, EXPLAIN, SUMMARY, or UNSUPPORTED."""
    
    @property
    def name(self) -> str:
        return "IntentAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        query_lower = state.query.lower()
        
        # Determine intent based on keywords
        if any(kw in query_lower for kw in ["explain", "why", "cause", "reason", "understand"]):
            intent = "EXPLAIN"
        elif any(kw in query_lower for kw in ["analyze", "calculation", "metric", "measure", "value", "oee", "yield", "sum", "average", "total", "count"]):
            intent = "ANALYZE"
        elif any(kw in query_lower for kw in ["status", "health", "condition", "how is"]):
            intent = "STATUS"
        elif any(kw in query_lower for kw in ["summary", "overview", "describe", "list"]):
            intent = "SUMMARY"
        elif any(kw in query_lower for kw in ["predict", "sales", "forecast", "price", "market"]):
            intent = "UNSUPPORTED"
        else:
            # Fallback to UNSUPPORTED for non-matching queries to fail safe
            intent = "UNSUPPORTED"
            
        state.intent = intent
        return state
