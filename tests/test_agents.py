from unittest.mock import MagicMock

from agents.analytics_agent import AnalyticsAgent
from agents.data_agent import DataAgent
from agents.domain_agent import DomainAgent
from agents.explainability_agent import ExplainabilityAgent
from agents.intent_agent import IntentAgent
from agents.response_agent import ResponseAgent
from agents.supervisor_agent import SupervisorAgent
from models.data_models import BatchRecord, ProductionRecord
from models.llm_models import LLMResponse
from models.workflow_state import AnalyticsOutput, WorkflowState
from services.base_llm_service import BaseLLMService


# 1. Supervisor Agent Test
def test_supervisor_agent():
    agent = SupervisorAgent()
    
    # Happy Path
    state = WorkflowState(query="What is the OEE calculation?", industry="automotive")
    result = agent.execute(state)
    assert result.success is True
    assert result.updated_state.status == "VALIDATED"
    
    # Failure Path (empty query)
    state_fail = WorkflowState(query="", industry="automotive")
    result_fail = agent.execute(state_fail)
    assert result_fail.success is False
    assert "Query cannot be empty" in result_fail.error_message

# 2. Intent Agent Test
def test_intent_agent():
    agent = IntentAgent()
    
    # Test ANALYZE intent
    state = WorkflowState(query="What is the OEE metric for Assembly Line 1?", industry="automotive")
    result = agent.execute(state)
    assert result.success is True
    assert result.updated_state.intent == "ANALYZE"
    
    # Test EXPLAIN intent
    state = WorkflowState(query="Why did the yield drop?", industry="pharma")
    result = agent.execute(state)
    assert result.success is True
    assert result.updated_state.intent == "EXPLAIN"

# 3. Domain Agent Test
def test_domain_agent():
    agent = DomainAgent()
    state = WorkflowState(query="Explain terminology", industry="automotive")
    result = agent.execute(state)
    assert result.success is True
    assert result.updated_state.domain_context is not None
    assert "Overall Equipment Effectiveness (OEE)" in result.updated_state.domain_context

# 4. Data Agent Test
def test_data_agent():
    agent = DataAgent()
    state = WorkflowState(query="Load data", industry="pharma")
    result = agent.execute(state)
    assert result.success is True
    assert result.updated_state.retrieved_data is not None
    assert len(result.updated_state.retrieved_data) == 14
    assert isinstance(result.updated_state.retrieved_data[0], BatchRecord)

# 5. Analytics Agent Test
def test_analytics_agent():
    agent = AnalyticsAgent()
    
    # Hand-built records
    records = [
        ProductionRecord(timestamp="2026-07-12", line_id="Line 1", units_produced=100, defects=2, downtime_minutes=0.0, oee=90.0),
        ProductionRecord(timestamp="2026-07-12", line_id="Line 1", units_produced=150, defects=5, downtime_minutes=10.0, oee=85.0)
    ]
    
    state = WorkflowState(query="Calculate OEE sum", industry="automotive", retrieved_data=records)
    result = agent.execute(state)
    assert result.success is True
    assert result.updated_state.analytics_output is not None
    assert result.updated_state.analytics_output.metric_name == "Total Units Produced"
    assert result.updated_state.analytics_output.result_value == 250.0  # 100 + 150
    assert result.updated_state.analytics_output.record_count == 2

# 6. Explainability Agent Test
def test_explainability_agent():
    agent = ExplainabilityAgent()
    state = WorkflowState(
        query="Trace history", 
        industry="automotive", 
        execution_history=["SupervisorAgent", "IntentAgent", "DomainAgent"]
    )
    result = agent.execute(state)
    assert result.success is True
    assert result.updated_state.explainability_output is not None
    trace = result.updated_state.explainability_output.trace_summary
    assert "SupervisorAgent executed successfully" in trace
    assert "ExplainabilityAgent executed successfully" in trace
    assert result.updated_state.explainability_output.steps_executed[-1] == "ExplainabilityAgent"

# 7. Response Agent Test
def test_response_agent():
    # Setup Mock LLM Service
    mock_llm = MagicMock(spec=BaseLLMService)
    mock_llm.generate.return_value = LLMResponse(
        generated_text="Concise final answer matching query and metrics context.",
        prompt_tokens=50,
        candidate_tokens=15
    )
    
    agent = ResponseAgent(llm_service=mock_llm)
    state = WorkflowState(
        query="What is OEE total?", 
        industry="automotive",
        domain_context=["OEE", "Downtime"],
        analytics_output=AnalyticsOutput(metric_name="Total Units Produced", result_value=1200, record_count=8)
    )
    
    result = agent.execute(state)
    assert result.success is True
    assert result.updated_state.final_response == "Concise final answer matching query and metrics context."
    mock_llm.generate.assert_called_once()
