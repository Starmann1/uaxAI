from agents.base_agent import BaseAgent
from models.workflow_state import WorkflowState


class SupervisorAgent(BaseAgent):
    """Supervisor Agent: Validates the workflow state contains query and industry values."""
    
    @property
    def name(self) -> str:
        return "SupervisorAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        if not state.query or not state.query.strip():
            raise ValueError("Query cannot be empty.")
            
        if not state.industry or state.industry.strip() not in ("automotive", "pharma"):
            raise ValueError(f"Invalid or empty industry value: '{state.industry}'")
            
        state.status = "VALIDATED"
        return state
