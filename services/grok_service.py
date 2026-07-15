import os
import httpx
from services.base_llm_service import BaseLLMService
from models.llm_models import LLMRequest, LLMResponse


class GrokService(BaseLLMService):
    """xAI Grok API Service calling Grok models using an OpenAI-compatible endpoint."""
    
    def __init__(self, model: str = "grok-2-1212"):
        self.model = model
        self.api_key = os.environ.get("XAI_API_KEY")
        self.base_url = "https://api.x.ai/v1/chat/completions"
        
    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            raise ValueError("XAI_API_KEY environment variable is not set.")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            generated_text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            candidate_tokens = usage.get("completion_tokens", 0)
            
            return LLMResponse(
                generated_text=generated_text,
                prompt_tokens=prompt_tokens,
                candidate_tokens=candidate_tokens
            )
