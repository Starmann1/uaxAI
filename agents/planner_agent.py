from agents.base_agent import BaseAgent
from models.workflow_state import ExecutionPlan, WorkflowState
from services.config_loader import load_industry_config


class PlannerAgent(BaseAgent):
    """Planner Agent: Deterministically creates an ExecutionPlan based on query, intent, and config."""
    
    @property
    def name(self) -> str:
        return "PlannerAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        # Load the configuration for the current industry
        config = load_industry_config(state.industry)
        
        # 1. Resolve metric_id if possible
        metric_id = state.requested_metric_id
        if not metric_id:
            query_lower = state.query.lower()
            for m in config.metrics:
                if m.metric_id.lower() in query_lower or m.display_name.lower() in query_lower:
                    metric_id = m.metric_id
                    break
                    
        # Update state requested_metric_id with the resolved one
        if metric_id:
            state.requested_metric_id = metric_id
            
        intent = state.intent or "UNKNOWN"
        requires_data = False
        requires_analytics = False
        explanation_required = False
        unsupported_reason = None
        required_capabilities = []
        
        # 2. Planning rules
        if intent in ("ANALYZE", "STATUS"):
            requires_data = True
            requires_analytics = True
            explanation_required = True
            required_capabilities = ["data_retrieval", "analytics", "explainability"]
        elif intent in ("EXPLAIN", "SUMMARY"):
            requires_data = True
            explanation_required = True
            if metric_id:
                requires_analytics = True
                required_capabilities = ["data_retrieval", "analytics", "explainability"]
            else:
                requires_analytics = False
                required_capabilities = ["data_retrieval", "explainability"]
        else:  # UNSUPPORTED or UNKNOWN
            requires_data = False
            requires_analytics = False
            explanation_required = False
            unsupported_reason = (
                f"The request query intent '{intent}' is not supported by the platform. "
                "Only standard batch analytics and documentation queries are supported."
            )
            state.status = "UNSUPPORTED"
            required_capabilities = []
            
        state.execution_plan = ExecutionPlan(
            intent=intent,
            required_capabilities=required_capabilities,
            metric_id=metric_id,
            requires_data=requires_data,
            requires_analytics=requires_analytics,
            explanation_required=explanation_required,
            unsupported_reason=unsupported_reason
        )
        
        return state
