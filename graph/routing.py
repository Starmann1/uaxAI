from models.workflow_state import WorkflowState


def route_after_planner(state: WorkflowState) -> str:
    """Routes after the Planner node.
    
    If the planner fails, routes to graceful_termination.
    Otherwise routes to domain (if data is required) or response (if not).
    """
    if state.status == "FAILED":
        return "graceful_termination"
    
    if state.execution_plan:
        if state.execution_plan.requires_data:
            return "domain"
        return "response"
        
    # Legacy default
    return "domain"


def route_after_data(state: WorkflowState) -> str:
    """Routes after the Data node.
    
    If data loading failed, routes to graceful_termination.
    Otherwise, routes to analytics (if required) or explainability/response.
    """
    if state.status == "FAILED":
        return "graceful_termination"
        
    if state.execution_plan:
        if state.execution_plan.requires_analytics:
            return "analytics"
        if state.execution_plan.explanation_required:
            return "explainability"
        return "response"
        
    # Legacy default
    return "analytics"


def route_after_analytics(state: WorkflowState) -> str:
    """Routes after the Analytics node.
    
    If analytics failed, routes to graceful_termination.
    Otherwise, routes to explainability (if required) or response.
    """
    if state.status == "FAILED":
        return "graceful_termination"
        
    if state.execution_plan:
        if state.execution_plan.explanation_required:
            return "explainability"
        return "response"
        
    # Legacy default
    return "explainability"
