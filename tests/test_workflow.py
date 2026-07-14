from unittest.mock import MagicMock

from graph.workflow import create_workflow
from models.llm_models import LLMResponse
from services.base_llm_service import BaseLLMService


def test_automotive_workflow_run():
    # Mock LLM Service to avoid network dependencies
    mock_llm = MagicMock(spec=BaseLLMService)
    mock_llm.generate.return_value = LLMResponse(
        generated_text="Mocked Automotive output answer.",
        prompt_tokens=40,
        candidate_tokens=15
    )
    
    workflow = create_workflow(llm_service=mock_llm)
    
    # Execute the graph
    result = workflow.invoke({
        "query": "What is the OEE metric value sum for Assembly Line 1?",
        "industry": "automotive"
    })
    
    # Assert successful flow, intent classification, analytics, history, and response
    assert result["status"] == "VALIDATED"
    assert result["intent"] == "ANALYZE"
    assert len(result["retrieved_data"]) == 8
    assert result["analytics_output"]["result_value"] == 940.0
    assert "SupervisorAgent" in result["execution_history"]
    assert "ResponseAgent" in result["execution_history"]
    assert result["final_response"] == "Mocked Automotive output answer."

def test_pharma_workflow_run():
    mock_llm = MagicMock(spec=BaseLLMService)
    mock_llm.generate.return_value = LLMResponse(
        generated_text="Mocked Pharma output answer.",
        prompt_tokens=40,
        candidate_tokens=15
    )
    
    workflow = create_workflow(llm_service=mock_llm)
    
    result = workflow.invoke({
        "query": "Calculate aggregate batch yield percentage.",
        "industry": "pharma"
    })
    
    assert result["status"] == "VALIDATED"
    assert result["intent"] == "ANALYZE"
    assert len(result["retrieved_data"]) == 8
    assert result["analytics_output"]["result_value"] == 721.2
    assert "ResponseAgent" in result["execution_history"]
    assert result["final_response"] == "Mocked Pharma output answer."

def test_forced_failure_graceful_termination():
    # Empty query triggers a SupervisorAgent validation failure
    workflow = create_workflow()
    
    result = workflow.invoke({
        "query": "",
        "industry": "automotive"
    })
    
    # Should terminate gracefully without crashing, returning status FAILED and diagnostic info
    assert result["status"] == "FAILED"
    assert "Failure in SupervisorAgent" in result["final_response"]
    assert "Query cannot be empty" in result["final_response"]
    assert "ResponseAgent" not in result["execution_history"]
