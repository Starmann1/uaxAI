from abc import ABC, abstractmethod

from models.agent_models import AgentResult
from models.workflow_state import WorkflowState


class BaseAgent(ABC):
    """Abstract base class representing an individual processing agent."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique string identifier name of the agent."""
        pass
        
    def execute(self, state: WorkflowState) -> AgentResult:
        """Runs the agent validation and logic on the given state.
        
        Saves execution tracing history.
        """
        try:
            # Create a deep copy of the workflow state for isolation
            state_copy = state.model_copy(deep=True)
            
            # Execute concrete agent processing logic
            updated_state = self._process(state_copy)
            
            # Record agent execution in history
            if self.name not in updated_state.execution_history:
                updated_state.execution_history.append(self.name)
                
            return AgentResult(
                success=True,
                updated_state=updated_state,
                agent_name=self.name
            )
        except Exception as e:
            return AgentResult(
                success=False,
                updated_state=state,
                error_message=str(e),
                agent_name=self.name
            )
            
    @abstractmethod
    def _process(self, state: WorkflowState) -> WorkflowState:
        """Subclass implementation of agent execution logic mutating state.
        
        Must return the updated state.
        """
        pass
