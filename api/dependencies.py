import logging
import os

from models.llm_models import LLMRequest, LLMResponse
from services.base_llm_service import BaseLLMService
from services.gemini_service import GeminiService

logger = logging.getLogger("uaxai-api")


class FakeLLMService(BaseLLMService):
    """Deterministic Fake LLM service for testing and development when API key is missing."""
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        logger.info("FakeLLMService processing request: %s", request.prompt[:100])
        return LLMResponse(
            generated_text=(
                "[Mock LLM Response] UAXAI cooperative agent trace is complete.\n\n"
                "The analysis calculation yields the exact aggregates calculated by the Analytics agent. "
                "The terminology terms provided by Domain agent are fully contextualized."
            ),
            prompt_tokens=10,
            candidate_tokens=10
        )


def get_llm_service() -> BaseLLMService:
    """Dependency provider for LLM service layer.
    
    If GEMINI_API_KEY is missing, logs a warning and returns FakeLLMService.
    """
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        logger.warning("GEMINI_API_KEY is not set in environment. Falling back to FakeLLMService for development/test.")
        return FakeLLMService()
    try:
        return GeminiService()
    except Exception as e:
        logger.error(f"Failed to initialize GeminiService: {e}. Falling back to FakeLLMService.")
        return FakeLLMService()
