from agents.analytics_agent import AnalyticsAgent
from agents.data_agent import DataAgent
from agents.domain_agent import DomainAgent
from agents.explainability_agent import ExplainabilityAgent
from agents.intent_agent import IntentAgent
from agents.response_agent import ResponseAgent
from agents.supervisor_agent import SupervisorAgent
from models.workflow_state import WorkflowState
from services.base_llm_service import BaseLLMService


class WorkflowNodes:
    """Wrapper class containing node functions for the LangGraph workflow, allowing LLM dependency injection."""
    
    def __init__(self, llm_service: BaseLLMService = None):
        """Initializes all cooperative agents, optionally injecting an LLM Service."""
        self.supervisor = SupervisorAgent()
        self.intent = IntentAgent()
        self.domain = DomainAgent()
        self.data = DataAgent()
        self.analytics = AnalyticsAgent()
        self.explainability = ExplainabilityAgent()
        self.response = ResponseAgent(llm_service=llm_service)
        
    def _run_agent(self, agent, state: WorkflowState) -> dict:
        """Helper to run an agent. If the workflow has already failed, skips execution."""
        # If upstream status is already FAILED, propagate without executing
        if state.status == "FAILED":
            return state.model_dump()
            
        result = agent.execute(state)
        if not result.success:
            # Set the status to FAILED and record error details
            state.status = "FAILED"
            state.final_response = f"Failure in {agent.name}: {result.error_message}"
            return state.model_dump()
            
        return result.updated_state.model_dump()

    def supervisor_node(self, state: WorkflowState) -> dict:
        return self._run_agent(self.supervisor, state)

    def intent_node(self, state: WorkflowState) -> dict:
        return self._run_agent(self.intent, state)

    def domain_node(self, state: WorkflowState) -> dict:
        return self._run_agent(self.domain, state)

    def data_node(self, state: WorkflowState) -> dict:
        return self._run_agent(self.data, state)

    def analytics_node(self, state: WorkflowState) -> dict:
        return self._run_agent(self.analytics, state)

    def explainability_node(self, state: WorkflowState) -> dict:
        return self._run_agent(self.explainability, state)

    def response_node(self, state: WorkflowState) -> dict:
        return self._run_agent(self.response, state)

    def graceful_termination_node(self, state: WorkflowState) -> dict:
        """Graceful termination node that ensures failure details are formatted in final_response."""
        if not state.final_response:
            state.final_response = f"Workflow aborted gracefully. Current status: {state.status}."
        return state.model_dump()
