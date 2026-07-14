from models.workflow_state import WorkflowState


def route_after_data(state: WorkflowState) -> str:
    """Routing function executed after the Data node.
    
    If any upstream processing failed (e.g. Supervisor validation or CSV loading),
    routes directly to the graceful termination node. Otherwise, proceeds to Analytics.
    """
    if state.status == "FAILED":
        return "graceful_termination"
    return "analytics"
