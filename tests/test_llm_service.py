from unittest.mock import MagicMock, patch

import pytest

from models.llm_models import LLMRequest
from services.gemini_service import GeminiService


def test_missing_api_key_initialization(monkeypatch):
    # Remove key if present
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc_info:
        GeminiService()
    assert "GEMINI_API_KEY environment variable is missing" in str(exc_info.value)

@patch("google.generativeai.configure")
@patch("google.generativeai.GenerativeModel")
def test_valid_llm_generation(mock_generative_model_class, mock_configure_func, monkeypatch):
    # Set dummy API key
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key_val")
    
    # Setup model mock
    mock_model_instance = MagicMock()
    mock_generative_model_class.return_value = mock_model_instance
    
    # Setup response mock
    mock_response = MagicMock()
    mock_response.text = "Mocked explanation text output."
    
    # Mock usage metadata attributes
    mock_usage = MagicMock()
    mock_usage.prompt_token_count = 15
    mock_usage.candidates_token_count = 35
    mock_response.usage_metadata = mock_usage
    
    mock_model_instance.generate_content.return_value = mock_response
    
    # Initialize service
    service = GeminiService(model_name="gemini-2.5-flash")
    
    # Verify setup calls
    mock_configure_func.assert_called_once_with(api_key="dummy_key_val")
    mock_generative_model_class.assert_called_once_with("gemini-2.5-flash")
    
    # Generate content
    request = LLMRequest(prompt="Explain OEE calculation", temperature=0.2, max_output_tokens=500)
    response = service.generate(request)
    
    # Verify outputs and usage details
    assert response.generated_text == "Mocked explanation text output."
    assert response.prompt_tokens == 15
    assert response.candidate_tokens == 35
    
    mock_model_instance.generate_content.assert_called_once()
