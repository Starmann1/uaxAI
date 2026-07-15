import os
import sys
import argparse

from graph.workflow import create_workflow
from models.llm_models import LLMRequest, LLMResponse
from services.base_llm_service import BaseLLMService


class MockLLMService(BaseLLMService):
    """Fallback LLM service used if GEMINI_API_KEY is not set."""
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
    
    args = parser.parse_args()
    
    # 1. Instantiate workflow
    if os.environ.get("GEMINI_API_KEY"):
        print("[INFO] Live GEMINI_API_KEY detected. Using real GeminiService.")
        workflow = create_workflow()
    else:
        print("[INFO] No GEMINI_API_KEY env. Using MockLLMService.")
        workflow = create_workflow(llm_service=MockLLMService())
        
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
