import os
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import create_workflow
from models.llm_models import LLMRequest, LLMResponse
from services.base_llm_service import BaseLLMService


# Mock LLM Service for local pipeline test run
class MockLLMService(BaseLLMService):
    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            generated_text="[Mock LLM Response] Based on OEE terminology, total sum calculated is 940 units.",
            prompt_tokens=100,
            candidate_tokens=20
        )

def run_graph_pipeline(industry: str, query: str):
    print("\n==================================================")
    print(f"Executing LangGraph for Industry: '{industry}'")
    print(f"Query: '{query}'")
    print("==================================================")
    
    # 1. Instantiate compiled StateGraph workflow
    if os.environ.get("GEMINI_API_KEY"):
        print("[INFO] Live GEMINI_API_KEY detected. Using real GeminiService.")
        workflow = create_workflow()
    else:
        print("[INFO] No GEMINI_API_KEY env. Using MockLLMService.")
        workflow = create_workflow(llm_service=MockLLMService())
        
    # 2. Invoke workflow with dictionary state
    result = workflow.invoke({
        "query": query,
        "industry": industry
    })
    
    print("\n>>> LangGraph Execution Complete! State Outcomes:")
    print(f"Status: {result.get('status')}")
    print(f"Intent Classified: {result.get('intent')}")
    print(f"Domain Context: {result.get('domain_context')}")
    print(f"Retrieved Records Count: {len(result.get('retrieved_data')) if result.get('retrieved_data') else 0}")
    
    analytics = result.get('analytics_output')
    if analytics:
        print(f"Analytics: {analytics.get('metric_name')} = {analytics.get('result_value')} (count: {analytics.get('record_count')})")
        
    explainability = result.get('explainability_output')
    if explainability:
        print("\n--- Explainability Audit Trail ---")
        print(explainability.get('trace_summary'))
        
    print("\n--- Final Response Answer ---")
    print(result.get('final_response'))
    print("-----------------------------")

def main():
    # 1. Happy Path Automotive
    run_graph_pipeline(
        industry="automotive", 
        query="What is the OEE metric value sum for Assembly Line 1?"
    )
    
    # 2. Happy Path Pharma
    run_graph_pipeline(
        industry="pharma", 
        query="Calculate aggregate yield percentage."
    )
    
    # 3. Graceful Failure path (empty query)
    run_graph_pipeline(
        industry="automotive", 
        query=""
    )

if __name__ == "__main__":
    main()
