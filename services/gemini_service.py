import os

import google.generativeai as genai

from models.llm_models import LLMRequest, LLMResponse
from services.base_llm_service import BaseLLMService


class GeminiService(BaseLLMService):
    """Gemini API implementation of the LLM service layer."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """Initializes the Gemini service, verifying that the API key is present in environment.
        
        Raises ValueError if the API key is missing.
        """
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing or empty.")
            
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        # GenerativeModel is initialized lazily or on construction
        self.model = genai.GenerativeModel(self.model_name)
        
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Sends generation prompt to Gemini model.
        
        Raises RuntimeError on API failure.
        """
        try:
            config = genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_output_tokens,
            )
            response = self.model.generate_content(
                request.prompt,
                generation_config=config
            )
            
            # Safely fetch usage metadata from the response object
            prompt_tokens = 0
            candidate_tokens = 0
            usage = getattr(response, "usage_metadata", None)
            if usage:
                prompt_tokens = getattr(usage, "prompt_token_count", 0)
                candidate_tokens = getattr(usage, "candidates_token_count", 0)
                
            return LLMResponse(
                generated_text=response.text,
                prompt_tokens=prompt_tokens,
                candidate_tokens=candidate_tokens
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")
