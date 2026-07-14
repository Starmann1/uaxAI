from abc import ABC, abstractmethod

from models.llm_models import LLMRequest, LLMResponse


class BaseLLMService(ABC):
    """Abstract base class for LLM service interaction."""
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generates a response from the LLM based on the request parameters.
        
        Raises exceptions on API or validation failures.
        """
        pass
