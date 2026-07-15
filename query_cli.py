import os
import sys
import argparse

from graph.workflow import create_workflow
from models.llm_models import LLMRequest, LLMResponse
from services.base_llm_service import BaseLLMService
from services.groq_service import GroqService
from services.grok_service import GrokService


class MockLLMService(BaseLLMService):
    """Fallback LLM service used if no live API keys are set."""
    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            generated_text="[Mock LLM Response] UAXAI cooperative agent trace is complete.",
            prompt_tokens=100,
            candidate_tokens=20
        )


def main():
    parser = argparse.ArgumentParser(description="UAXAI Terminal Query CLI")
    parser.add_argument("-i", "--industry", required=True, help="Industry context key (e.g. pharma_deviations, pharma_capas)")
    parser.add_argument("-q", "--query", required=True, help="Query string to execute")
    parser.add_argument("-p", "--provider", choices=["gemini", "groq", "grok", "mock"], default=None, help="LLM provider choice")
    parser.add_argument("-m", "--model", default=None, help="Custom LLM model string")
    
    args = parser.parse_args()
    
    # 1. Resolve provider
    provider = args.provider
    if not provider:
        if os.environ.get("GEMINI_API_KEY"):
            provider = "gemini"
        elif os.environ.get("GROQ_API_KEY"):
            provider = "groq"
        elif os.environ.get("XAI_API_KEY"):
            provider = "grok"
        else:
            provider = "mock"
            
    # 2. Instantiate correct service
    if provider == "gemini":
        from services.gemini_service import GeminiService
        print("[INFO] Using GeminiService.")
        llm_service = GeminiService()
    elif provider == "groq":
        model_name = args.model or "llama-3.3-70b-versatile"
        print(f"[INFO] Using GroqService (Model: {model_name}).")
        llm_service = GroqService(model=model_name)
    elif provider == "grok":
        model_name = args.model or "grok-2-1212"
        print(f"[INFO] Using GrokService (Model: {model_name}).")
        llm_service = GrokService(model=model_name)
    else:
        print("[INFO] Using MockLLMService.")
        llm_service = MockLLMService()
        
    workflow = create_workflow(llm_service=llm_service)
        
    # 2. Invoke workflow
    try:
        result = workflow.invoke({
            "query": args.query,
            "industry": args.industry
        })
        
        print("\n" + "=" * 50)
        print(">>> UAXAI TERMINAL RUNNER RESULTS")
        print("=" * 50)
        print(f"Status: {result.get('status')}")
        print(f"Intent: {result.get('intent')}")
        print(f"Retrieved Records Count: {len(result.get('retrieved_data')) if result.get('retrieved_data') else 0}")
        
        analytics = result.get('analytics_output')
        if analytics:
            print(f"Analytics Outcome: {analytics.get('metric_name')} = {analytics.get('result_value')} (count: {analytics.get('record_count')})")
            
        explainability = result.get('explainability_output')
        if explainability:
            print("\n--- Explainability Trace ---")
            print(explainability.get('trace_summary'))
            
        print("\n--- Final Response ---")
        print(result.get('final_response'))
        print("=" * 50 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}\n")


if __name__ == "__main__":
    main()
