from agents.base_agent import BaseAgent
from models.workflow_state import WorkflowState


class IntentAgent(BaseAgent):
    """Intent Agent: Deterministically classifies queries using keyword-matching."""
    
    @property
    def name(self) -> str:
        return "IntentAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        query_lower = state.query.lower()
        
        # Keyword mappings for the 5 specified categories
        if any(kw in query_lower for kw in ["explain", "why", "cause", "reason", "understand"]):
            intent = "EXPLAIN"
        elif any(kw in query_lower for kw in ["analyze", "calculation", "metric", "measure", "value", "oee", "yield"]):
            intent = "ANALYZE"
        elif any(kw in query_lower for kw in ["status", "health", "condition", "how is"]):
            intent = "STATUS"
        elif any(kw in query_lower for kw in ["summary", "overview", "describe", "list"]):
            intent = "SUMMARY"
        else:
            intent = "UNKNOWN"
            
        state.intent = intent
        return state
