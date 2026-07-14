import datetime
from abc import ABC, abstractmethod

from models.agent_models import AgentResult
from models.workflow_state import AgentTraceEvent, ExecutionTrace, WorkflowState


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
        started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Ensure execution_trace is initialized
        if not state.execution_trace:
            state.execution_trace = ExecutionTrace(
                correlation_id=state.correlation_id,
                started_at=started_at,
                status="RUNNING"
            )
            
        try:
            # Create a deep copy of the workflow state for isolation
            state_copy = state.model_copy(deep=True)
            
            # Execute concrete agent processing logic
            updated_state = self._process(state_copy)
            
            # Record agent execution in history
            if self.name not in updated_state.execution_history:
                updated_state.execution_history.append(self.name)
                
            completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            # Safe input/output summaries
            input_summary = f"Query: '{state.query[:100]}...'" if len(state.query) > 100 else f"Query: '{state.query}'"
            output_summary = f"Status: {updated_state.status}"
            if updated_state.analytics_result:
                output_summary += f", Result: {updated_state.analytics_result.result_value}"
            
            event = AgentTraceEvent(
                agent_name=self.name,
                started_at=started_at,
                completed_at=completed_at,
                outcome="SUCCESS",
                input_summary=input_summary,
                output_summary=output_summary
            )
            updated_state.execution_trace.events.append(event)
            updated_state.execution_trace.completed_at = completed_at
            updated_state.execution_trace.status = "COMPLETED"
                
            return AgentResult(
                success=True,
                updated_state=updated_state,
                agent_name=self.name
            )
        except Exception as e:
            completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            input_summary = f"Query: '{state.query[:100]}...'" if len(state.query) > 100 else f"Query: '{state.query}'"
            error_msg = str(e)
            
            event = AgentTraceEvent(
                agent_name=self.name,
                started_at=started_at,
                completed_at=completed_at,
                outcome="FAILURE",
                input_summary=input_summary,
                output_summary="Failed to execute process logic",
                error_message=error_msg
            )
            state.execution_trace.events.append(event)
            state.execution_trace.completed_at = completed_at
            state.execution_trace.status = "FAILED"
            
            return AgentResult(
                success=False,
                updated_state=state,
                error_message=error_msg,
                agent_name=self.name
            )
            
    @abstractmethod
    def _process(self, state: WorkflowState) -> WorkflowState:
        """Subclass implementation of agent execution logic mutating state.
        
        Must return the updated state.
        """
        pass
