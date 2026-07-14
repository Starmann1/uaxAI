from agents.base_agent import BaseAgent
from models.workflow_state import AnalyticsOutput, WorkflowState


class AnalyticsAgent(BaseAgent):
    """Analytics Agent: Executes a single aggregate calculation (sum) over the retrieved records."""
    
    @property
    def name(self) -> str:
        return "AnalyticsAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        if not state.retrieved_data:
            raise ValueError("No data records available for analytics execution.")
            
        record_count = len(state.retrieved_data)
        
        # Industry-specific single sum aggregation operation
        if state.industry == "automotive":
            metric_name = "Total Units Produced"
            # sum units_produced
            total_sum = sum(float(r.units_produced) for r in state.retrieved_data)
        elif state.industry == "pharma":
            metric_name = "Sum of Batch Yield Percentages"
            # sum batch_yield_pct
            total_sum = sum(float(r.batch_yield_pct) for r in state.retrieved_data)
        else:
            raise ValueError(f"Unknown industry context: '{state.industry}'")
            
        state.analytics_output = AnalyticsOutput(
            metric_name=metric_name,
            result_value=total_sum,
            record_count=record_count
        )
        return state
