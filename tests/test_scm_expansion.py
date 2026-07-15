from unittest.mock import MagicMock
from graph.workflow import create_workflow
from models.llm_models import LLMResponse
from services.base_llm_service import BaseLLMService
from services.config_loader import load_industry_config


def test_scm_deviations_workflow():
    mock_llm = MagicMock(spec=BaseLLMService)
    mock_llm.generate.return_value = LLMResponse(
        generated_text="Mocked Deviations response.",
        prompt_tokens=40,
        candidate_tokens=15
    )
    
    workflow = create_workflow(llm_service=mock_llm)
    
    result = workflow.invoke({
        "query": "How many major deviations have been reported?",
        "industry": "pharma_deviations",
        "requested_metric_id": "major_deviations"
    })
    
    assert result["status"] == "VALIDATED"
    assert result["intent"] == "ANALYZE"
    assert len(result["retrieved_data"]) == 3
    assert result["analytics_result"]["result_value"] == 2.0  # 2 major deviations
    assert "ResponseAgent" in result["execution_history"]
    assert result["final_response"] == "Mocked Deviations response."


def test_scm_capas_workflow():
    mock_llm = MagicMock(spec=BaseLLMService)
    mock_llm.generate.return_value = LLMResponse(
        generated_text="Mocked CAPA response.",
        prompt_tokens=40,
        candidate_tokens=15
    )
    
    workflow = create_workflow(llm_service=mock_llm)
    
    result = workflow.invoke({
        "query": "What is the total number of CAPA records?",
        "industry": "pharma_capas",
        "requested_metric_id": "total_capas"
    })
    
    assert result["status"] == "VALIDATED"
    assert result["intent"] == "ANALYZE"
    assert len(result["retrieved_data"]) == 2
    assert result["analytics_result"]["result_value"] == 2.0  # 2 total capas
    assert result["final_response"] == "Mocked CAPA response."
