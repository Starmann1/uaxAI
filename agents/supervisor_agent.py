from agents.base_agent import BaseAgent
from models.workflow_state import WorkflowState
from services.config_loader import list_industries


class SupervisorAgent(BaseAgent):
    """Supervisor Agent: Validates the workflow state contains query and industry values."""
    
    @property
    def name(self) -> str:
        return "SupervisorAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        if not state.query or not state.query.strip():
            raise ValueError("Query cannot be empty.")
            
        allowed_industries = list_industries()
        if not state.industry or state.industry.strip() not in allowed_industries:
            raise ValueError(
                f"Invalid or empty industry value: '{state.industry}'. "
                f"Must be one of: {allowed_industries}"
            )
            
        state.status = "VALIDATED"
        return state
