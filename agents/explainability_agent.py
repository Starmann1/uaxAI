from agents.base_agent import BaseAgent
from models.workflow_state import ExplainabilityOutput, WorkflowState


class ExplainabilityAgent(BaseAgent):
    """Explainability Agent: Deterministically builds an audit trace of execution history (no LLM)."""
    
    @property
    def name(self) -> str:
        return "ExplainabilityAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        # Generate a list of current execution steps, adding this agent itself
        steps = list(state.execution_history)
        if self.name not in steps:
            steps.append(self.name)
            
        trace_lines = ["UAIX Platform Execution Trace Audit:"]
        for idx, step in enumerate(steps, 1):
            trace_lines.append(f"  Step {idx}: {step} executed successfully.")
            
        trace_summary = "\n".join(trace_lines)
        
        state.explainability_output = ExplainabilityOutput(
            trace_summary=trace_summary,
            steps_executed=steps
        )
        return state
