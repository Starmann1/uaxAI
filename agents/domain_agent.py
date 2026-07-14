from agents.base_agent import BaseAgent
from models.workflow_state import WorkflowState
from services.config_loader import load_industry_config


class DomainAgent(BaseAgent):
    """Domain Agent: Populates state with industry-specific terminology loaded from configuration."""
    
    @property
    def name(self) -> str:
        return "DomainAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        # Load config dynamically using config loader
        config = load_industry_config(state.industry)
        
        # Populate domain context
        state.domain_context = config.terminology
        return state
