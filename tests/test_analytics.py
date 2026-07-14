import pytest

from agents.analytics_agent import AnalyticsAgent
from agents.base_agent import BaseAgent
from agents.explainability_agent import ExplainabilityAgent
from models.config_models import MetricDefinition
from models.data_models import BatchRecord
from models.workflow_state import WorkflowState
from services.analytics_engine import AnalyticsEngine, AnalyticsEngineError

# Sample test data
BATCH_RECORDS = [
    BatchRecord(
        timestamp="2026-07-12",
        batch_id="BAT-001",
        reactor_id="Bioreactor Alpha",
        critical_temp=37.0,
        critical_ph=6.8,
        batch_yield_pct=90.0,
        quality_status="Pass"
    ),
    BatchRecord(
        timestamp="2026-07-12",
        batch_id="BAT-002",
        reactor_id="Bioreactor Alpha",
        critical_temp=36.5,
        critical_ph=7.0,
        batch_yield_pct=95.0,
        quality_status="Pass"
    ),
    BatchRecord(
        timestamp="2026-07-13",
        batch_id="BAT-003",
        reactor_id="Bioreactor Alpha",
        critical_temp=37.2,
        critical_ph=6.9,
        batch_yield_pct=88.5,
        quality_status="Pass"
    ),
    BatchRecord(
        timestamp="2026-07-13",
        batch_id="BAT-004",
        reactor_id="Bioreactor Beta",
        critical_temp=38.0,
        critical_ph=6.5,
        batch_yield_pct=40.0,
        quality_status="Fail"
    ),
]


def test_analytics_engine_average():
    metric = MetricDefinition(
        metric_id="average_batch_yield",
        operation="average",
        target_field="batch_yield_pct",
        display_name="Average Batch Yield"
    )
    # Average of Bioreactor Alpha batches
    result = AnalyticsEngine.calculate(
        records=BATCH_RECORDS,
        metric=metric,
        requested_filters={"reactor_id": "Bioreactor Alpha"},
        allowed_filters=["reactor_id"],
        dataset_reference="data/pharma/batches.csv"
    )
    assert result.result_value == (90.0 + 95.0 + 88.5) / 3
    assert result.record_count == 3
    assert result.evidence.applied_filters == {"reactor_id": "Bioreactor Alpha"}


def test_analytics_engine_failed_count():
    metric = MetricDefinition(
        metric_id="failed_batch_count",
        operation="count",
        filter_field="quality_status",
        filter_value="Fail",
        display_name="Failed Batch Count"
    )
    result = AnalyticsEngine.calculate(
        records=BATCH_RECORDS,
        metric=metric,
        requested_filters={},
        allowed_filters=["reactor_id"],
        dataset_reference="data/pharma/batches.csv"
    )
    assert result.result_value == 1.0  # BAT-004 failed
    assert result.record_count == 1
    assert result.evidence.applied_filters == {"quality_status": "Fail"}


def test_analytics_engine_disallowed_filter():
    metric = MetricDefinition(
        metric_id="batch_count",
        operation="count",
        display_name="Batch Count"
    )
    with pytest.raises(AnalyticsEngineError) as exc_info:
        AnalyticsEngine.calculate(
            records=BATCH_RECORDS,
            metric=metric,
            requested_filters={"critical_temp": 37.0},
            allowed_filters=["reactor_id"],
            dataset_reference="data/pharma/batches.csv"
        )
    assert "not allowed in configuration" in str(exc_info.value)


def test_analytics_engine_nonexistent_filter_field():
    metric = MetricDefinition(
        metric_id="batch_count",
        operation="count",
        display_name="Batch Count"
    )
    with pytest.raises(AnalyticsEngineError) as exc_info:
        AnalyticsEngine.calculate(
            records=BATCH_RECORDS,
            metric=metric,
            requested_filters={"nonexistent": "value"},
            allowed_filters=["nonexistent"],
            dataset_reference="data/pharma/batches.csv"
        )
    assert "does not exist on schema" in str(exc_info.value)


def test_analytics_agent_pharma():
    agent = AnalyticsAgent()
    state = WorkflowState(
        query="average batch yield",
        industry="pharma",
        requested_metric_id="average_batch_yield",
        requested_filters={"reactor_id": "Bioreactor Alpha"},
        retrieved_data=BATCH_RECORDS
    )
    res = agent.execute(state)
    assert res.success is True
    assert res.updated_state.analytics_result is not None
    assert res.updated_state.analytics_result.result_value == (90.0 + 95.0 + 88.5) / 3
    assert res.updated_state.analytics_output.result_value == (90.0 + 95.0 + 88.5) / 3


def test_analytics_agent_unknown_metric():
    agent = AnalyticsAgent()
    state = WorkflowState(
        query="unknown metric",
        industry="pharma",
        requested_metric_id="unknown_metric_id",
        retrieved_data=BATCH_RECORDS
    )
    res = agent.execute(state)
    assert res.success is False
    assert "is not configured for industry" in res.error_message


def test_explainability_agent_evidence():
    agent = ExplainabilityAgent()
    metric = MetricDefinition(
        metric_id="average_batch_yield",
        operation="average",
        target_field="batch_yield_pct",
        display_name="Average Batch Yield"
    )
    result = AnalyticsEngine.calculate(
        records=BATCH_RECORDS,
        metric=metric,
        requested_filters={"reactor_id": "Bioreactor Alpha"},
        allowed_filters=["reactor_id"],
        dataset_reference="data/pharma/batches.csv"
    )
    state = WorkflowState(
        query="explain average batch yield",
        industry="pharma",
        analytics_result=result,
        execution_history=["AnalyticsAgent"]
    )
    res = agent.execute(state)
    assert res.success is True
    summary = res.updated_state.explainability_output.trace_summary
    assert "Analytics Evidence Provenance:" in summary
    assert "Dataset: data/pharma/batches.csv" in summary
    assert "Metric ID: average_batch_yield" in summary
    assert "Applied Filters: reactor_id=Bioreactor Alpha" in summary


def test_base_agent_trace_failure():
    class FailureAgent(BaseAgent):
        @property
        def name(self) -> str:
            return "FailureAgent"
        def _process(self, state: WorkflowState) -> WorkflowState:
            raise RuntimeError("Artificial failure")
            
    agent = FailureAgent()
    state = WorkflowState(query="Test failure", industry="pharma")
    res = agent.execute(state)
    assert res.success is False
    assert state.execution_trace is not None
    assert state.execution_trace.status == "FAILED"
    assert len(state.execution_trace.events) == 1
    assert state.execution_trace.events[0].outcome == "FAILURE"
    assert state.execution_trace.events[0].error_message == "Artificial failure"
