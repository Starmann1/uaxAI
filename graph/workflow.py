from langgraph.graph import END, StateGraph

from graph.nodes import WorkflowNodes
from graph.routing import route_after_data
from models.workflow_state import WorkflowState
from services.base_llm_service import BaseLLMService


def create_workflow(llm_service: BaseLLMService = None):
    """Builds and compiles the orchestrated cooperative agent StateGraph."""
    nodes = WorkflowNodes(llm_service=llm_service)
    
    # Initialize the graph using WorkflowState as the schema
    builder = StateGraph(WorkflowState)
    
    # Add nodes to graph
    builder.add_node("supervisor", nodes.supervisor_node)
    builder.add_node("intent", nodes.intent_node)
    builder.add_node("domain", nodes.domain_node)
    builder.add_node("data", nodes.data_node)
    builder.add_node("analytics", nodes.analytics_node)
    builder.add_node("explainability", nodes.explainability_node)
    builder.add_node("response", nodes.response_node)
    builder.add_node("graceful_termination", nodes.graceful_termination_node)
    
    # Define linear path
    builder.set_entry_point("supervisor")
    builder.add_edge("supervisor", "intent")
    builder.add_edge("intent", "domain")
    builder.add_edge("domain", "data")
    
    # Define the single conditional edge after data retrieval
    builder.add_conditional_edges(
        "data",
        route_after_data,
        {
            "graceful_termination": "graceful_termination",
            "analytics": "analytics"
        }
    )
    
    # Define success completion path
    builder.add_edge("analytics", "explainability")
    builder.add_edge("explainability", "response")
    builder.add_edge("response", END)
    
    # Define failure completion path
    builder.add_edge("graceful_termination", END)
    
    return builder.compile()
