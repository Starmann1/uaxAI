from agents.base_agent import BaseAgent
from models.workflow_state import WorkflowState


class DummyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "DummyAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        state.status = "PROCESSED_BY_DUMMY"
        return state

def test_base_agent_execution():
    state = WorkflowState(query="Test Query", industry="automotive")
    agent = DummyAgent()
    result = agent.execute(state)
    
    assert result.success is True
    assert result.agent_name == "DummyAgent"
    assert result.updated_state.status == "PROCESSED_BY_DUMMY"
    assert "DummyAgent" in result.updated_state.execution_history

def test_base_agent_failure():
    class FailureAgent(BaseAgent):
        @property
        def name(self) -> str:
            return "FailureAgent"
            
        def _process(self, state: WorkflowState) -> WorkflowState:
            raise ValueError("Processing failure")
            
    state = WorkflowState(query="Test Query", industry="automotive")
    agent = FailureAgent()
    result = agent.execute(state)
    
    assert result.success is False
    assert result.agent_name == "FailureAgent"
    assert "Processing failure" in result.error_message
    assert "FailureAgent" not in result.updated_state.execution_history
