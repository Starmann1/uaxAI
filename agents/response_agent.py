from agents.base_agent import BaseAgent
from models.llm_models import LLMRequest
from models.workflow_state import WorkflowState
from services.base_llm_service import BaseLLMService
from services.gemini_service import GeminiService


class ResponseAgent(BaseAgent):
    """Response Agent: Integrates state query, analytics calculations, and domain metadata, calling GeminiService to write the final response."""
    
    def __init__(self, llm_service: BaseLLMService = None):
        """Initializes the ResponseAgent, optionally injecting a custom or mock LLM service."""
        self.llm_service = llm_service
        
    @property
    def name(self) -> str:
        return "ResponseAgent"
        
    def _process(self, state: WorkflowState) -> WorkflowState:
        # Lazy initialization of live service if not injected
        if not self.llm_service:
            self.llm_service = GeminiService()
            
        terminology_text = ", ".join(state.domain_context) if state.domain_context else "None"
        
        analytics_text = "No analytics calculated."
        if state.analytics_output:
            analytics_text = (
                f"Metric: {state.analytics_output.metric_name}, "
                f"Aggregate Value: {state.analytics_output.result_value}, "
                f"Record Count: {state.analytics_output.record_count}"
            )
            
        prompt = (
            f"You are UAIX, a configuration-driven AI platform.\n"
            f"Provide a concise final answer to the user query utilizing the provided data analytics and domain terminology.\n\n"
            f"User Query: {state.query}\n"
            f"Industry: {state.industry}\n"
            f"Domain Terminology: {terminology_text}\n"
            f"Data Analytics Summary: {analytics_text}\n\n"
            f"Answer:"
        )
        
        request = LLMRequest(prompt=prompt, temperature=0.3, max_output_tokens=300)
        response = self.llm_service.generate(request)
        
        state.final_response = response.generated_text.strip()
        return state
