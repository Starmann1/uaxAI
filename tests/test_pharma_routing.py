from unittest.mock import MagicMock

from graph.workflow import create_workflow
from models.llm_models import LLMResponse
from services.base_llm_service import BaseLLMService


def test_pharma_average_yield_workflow():
    # 1. average batch yield follows data -> analytics -> explainability -> response
    mock_llm = MagicMock(spec=BaseLLMService)
    mock_llm.generate.return_value = LLMResponse(
        generated_text="Mocked response for average yield.",
        prompt_tokens=40,
        candidate_tokens=15
    )
    workflow = create_workflow(llm_service=mock_llm)
    
    result = workflow.invoke({
        "query": "What is the average batch yield?",
        "industry": "pharma",
        "requested_metric_id": "average_batch_yield"
    })
    
    assert result["intent"] == "ANALYZE"
    assert result["execution_plan"]["requires_data"] is True
    assert result["execution_plan"]["requires_analytics"] is True
    assert result["execution_plan"]["explanation_required"] is True
    
    # Verify execution history
    history = result["execution_history"]
    assert "SupervisorAgent" in history
    assert "IntentAgent" in history
    assert "PlannerAgent" in history
    assert "DomainAgent" in history
    assert "DataAgent" in history
    assert "AnalyticsAgent" in history
    assert "ExplainabilityAgent" in history
    assert "ResponseAgent" in history
    
    # Assert correct computation (8 pharma records sum to 721.2, average is 90.15)
    assert result["analytics_result"]["result_value"] == 90.15
    assert result["correlation_id"] is not None
    assert result["execution_trace"] is not None


def test_pharma_unsupported_query_routing():
    # 2. unsupported query does not invoke DataAgent or AnalyticsAgent
    mock_llm = MagicMock(spec=BaseLLMService)
    mock_llm.generate.return_value = LLMResponse(
        generated_text="I cannot predict sales.",
        prompt_tokens=40,
        candidate_tokens=15
    )
    workflow = create_workflow(llm_service=mock_llm)
    
    result = workflow.invoke({
        "query": "Predict next month's medicine sales.",
        "industry": "pharma"
    })
    
    assert result["intent"] == "UNSUPPORTED"
    assert result["status"] == "UNSUPPORTED"
    assert result["execution_plan"]["requires_data"] is False
    assert result["execution_plan"]["requires_analytics"] is False
    assert result["execution_plan"]["explanation_required"] is False
    
    # Verify execution history skips data & analytics
    history = result["execution_history"]
    assert "SupervisorAgent" in history
    assert "IntentAgent" in history
    assert "PlannerAgent" in history
    assert "ResponseAgent" in history
    assert "DataAgent" not in history
    assert "AnalyticsAgent" not in history
    assert "ExplainabilityAgent" not in history


def test_pharma_explain_without_metric_routing():
    # 3. explain query without metric does not invoke AnalyticsAgent
    mock_llm = MagicMock(spec=BaseLLMService)
    mock_llm.generate.return_value = LLMResponse(
        generated_text="Autoclave sterilization time refers to temperature cycles.",
        prompt_tokens=40,
        candidate_tokens=15
    )
    workflow = create_workflow(llm_service=mock_llm)
    
    result = workflow.invoke({
        "query": "Explain what autoclave sterilization time means.",
        "industry": "pharma"
    })
    
    assert result["intent"] == "EXPLAIN"
    assert result["execution_plan"]["requires_data"] is True
    assert result["execution_plan"]["requires_analytics"] is False
    assert result["execution_plan"]["explanation_required"] is True
    
    # Verify execution history runs data but NOT analytics
    history = result["execution_history"]
    assert "SupervisorAgent" in history
    assert "DataAgent" in history
    assert "ExplainabilityAgent" in history
    assert "ResponseAgent" in history
    assert "AnalyticsAgent" not in history


def test_pharma_invalid_query_terminates():
    # 4. invalid query gracefully terminates
    workflow = create_workflow()
    
    result = workflow.invoke({
        "query": "",
        "industry": "pharma"
    })
    
    assert result["status"] == "FAILED"
    assert "Failure in SupervisorAgent" in result["final_response"]
    assert "DataAgent" not in result["execution_history"]
    assert "ResponseAgent" not in result["execution_history"]
