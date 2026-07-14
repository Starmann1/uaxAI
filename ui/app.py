import os
import sys

import streamlit as st

# Ensure project root is on PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph.workflow import create_workflow
from models.llm_models import LLMRequest, LLMResponse
from services.base_llm_service import BaseLLMService


class MockLLMService(BaseLLMService):
    """Fallback LLM service used in the UI for mock query round-trips if GEMINI_API_KEY is not set."""
    def generate(self, request: LLMRequest) -> LLMResponse:
        # Generic response placeholder
        return LLMResponse(
            generated_text=(
                "[Mock LLM Response] UAIX cooperative agent trace is complete.\n\n"
                "The analysis calculation yields the exact aggregates calculated by the Analytics agent. "
                "The terminology terms provided by Domain agent are fully contextualized."
            ),
            prompt_tokens=120,
            candidate_tokens=40
        )

# Initialize Streamlit config
st.set_page_config(
    page_title="UAIX Platform Core Architecture Demonstration",
    page_icon="🌌",
    layout="wide"
)

# Header Section
st.title("🌌 UAIX Platform")
st.subheader("Core Architecture Demonstration (CAD)")

# Sidebar Settings
st.sidebar.header("Configuration Panel")

industry = st.sidebar.selectbox(
    "Switch Industry Context:",
    options=["automotive", "pharma"],
    format_func=lambda x: "Automotive Manufacturing" if x == "automotive" else "Pharmaceutical Manufacturing"
)

# Detect API Key in Environment
gemini_configured = "GEMINI_API_KEY" in os.environ

if gemini_configured:
    st.sidebar.success("🔑 Live Gemini API Key Configured.")
else:
    st.sidebar.warning("⚠️ No Gemini API Key. Running in Mock Mode.")

st.sidebar.write("---")
st.sidebar.info(
    "UAIX is a configuration-driven multi-agent AI system. "
    "Under the hood, all requests run through a StateGraph orchestrated by LangGraph."
)

# Main Query Area
st.write("### Query Interface")
st.write("Submit a question to trigger the multi-agent cooperative workflow:")

user_query = st.text_input(
    "Enter Query String:",
    placeholder="e.g. What is the total units produced?"
)

if st.button("Submit Query Workflow"):
    if not user_query.strip():
        st.error("Error: Query input cannot be empty.")
    else:
        with st.spinner("Executing StateGraph nodes (Supervisor -> Intent -> Domain -> Data -> Analytics -> Explainability -> Response)..."):
            try:
                # Instantiate graph workflow
                if gemini_configured:
                    workflow = create_workflow()
                else:
                    workflow = create_workflow(llm_service=MockLLMService())
                
                # Execute graph workflow
                result = workflow.invoke({
                    "query": user_query,
                    "industry": industry
                })
                
                status = result.get("status")
                
                if status == "FAILED":
                    st.error("❌ Workflow Execution Aborted Gracefully")
                    st.write(result.get("final_response"))
                else:
                    st.success("✅ Workflow Successfully Completed")
                    
                    # Final AI Output Response
                    st.write("#### 🤖 AI Assistant Response")
                    st.info(result.get("final_response"))
                    
                    # Display Intermediate Outputs
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("##### 📋 Domain Terminology Context")
                        terms = result.get("domain_context")
                        if terms:
                            for term in terms:
                                st.write(f"- {term}")
                        else:
                            st.write("No terms populated.")
                            
                    with col2:
                        st.write("##### 📊 Aggregated Metrics Data")
                        analytics = result.get("analytics_output")
                        if analytics:
                            st.metric(
                                label=analytics.get("metric_name"),
                                value=f"{analytics.get('result_value'):,.1f}",
                                delta=f"Based on {analytics.get('record_count')} CSV records"
                            )
                        else:
                            st.write("No metrics computed.")
                    
                    # Expander for Explainability
                    st.write("---")
                    with st.expander("🔍 View Explainability Execution Trace Audit"):
                        explainability = result.get("explainability_output")
                        if explainability:
                            st.code(explainability.get("trace_summary"))
                        else:
                            st.write("No execution trace available.")
                            
            except Exception as e:
                st.error(f"Platform Error: {e}")
