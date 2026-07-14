from agents.base_agent import BaseAgent
from models.workflow_state import AnalyticsOutput, WorkflowState
from services.analytics_engine import AnalyticsEngine
from services.config_loader import load_industry_config


class AnalyticsAgent(BaseAgent):
    """Analytics Agent: Executes aggregate calculations over records using AnalyticsEngine."""
    
    @property
    def name(self) -> str:
        return "AnalyticsAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        if not state.retrieved_data:
            raise ValueError("No data records available for analytics execution.")
            
        # Load config to get allowed filters and metric definitions
        config = load_industry_config(state.industry)
        
        # Determine metric to use
        metric_id = state.requested_metric_id
        if not metric_id:
            # Fallback to the first metric if none requested (keeps backward compatibility)
            if config.metrics:
                metric_id = config.metrics[0].metric_id
            else:
                raise ValueError(f"No metrics configured for industry '{state.industry}'")
                
        # Find the metric definition
        metric_def = next((m for m in config.metrics if m.metric_id == metric_id), None)
        if not metric_def:
            raise ValueError(f"Metric '{metric_id}' is not configured for industry '{state.industry}'")
            
        # Perform calculation
        result = AnalyticsEngine.calculate(
            records=state.retrieved_data,
            metric=metric_def,
            requested_filters=state.requested_filters,
            allowed_filters=config.allowed_filters,
            dataset_reference=config.dataset_reference
        )
        
        state.analytics_result = result
        
        # Populate legacy output for compatibility with legacy tests
        state.analytics_output = AnalyticsOutput(
            metric_name=result.metric_name,
            result_value=result.result_value,
            record_count=result.record_count
        )
        
        return state
