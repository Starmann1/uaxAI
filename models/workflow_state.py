import uuid
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from models.data_models import (
    BatchRecord,
    ProductionRecord,
    SupplierRecord,
    MaterialRecord,
    LocationRecord,
    DeviationRecord,
    CapaRecord,
)


class AnalyticsOutput(BaseModel):
    """Schema for data analytics aggregation results."""
    metric_name: str
    result_value: float
    record_count: int


class ExplainabilityOutput(BaseModel):
    """Schema for explainability audit trail/logs."""
    trace_summary: str
    steps_executed: List[str]


class AgentTraceEvent(BaseModel):
    """Schema for a single agent's execution event trace."""
    agent_name: str = Field(..., description="Name of the agent")
    started_at: str = Field(..., description="ISO 8601 UTC timestamp of execution start")
    completed_at: str = Field(..., description="ISO 8601 UTC timestamp of execution completion")
    outcome: str = Field(..., description="SUCCESS or FAILURE")
    input_summary: str = Field(..., description="Safe, non-sensitive summary of inputs")
    output_summary: str = Field(..., description="Safe, non-sensitive summary of outputs")
    error_message: Optional[str] = Field(None, description="Error details if execution failed")


class ExecutionTrace(BaseModel):
    """Schema for the overall workflow execution trace."""
    correlation_id: str = Field(..., description="Unique transaction correlation ID")
    started_at: str = Field(..., description="ISO 8601 UTC timestamp of workflow start")
    completed_at: Optional[str] = Field(None, description="ISO 8601 UTC timestamp of workflow completion")
    status: str = Field("RUNNING", description="Overall execution status")
    events: List[AgentTraceEvent] = Field(default_factory=list, description="Sequential events log")


class EvidenceReference(BaseModel):
    """Schema referencing data origin and execution parameters."""
    dataset_reference: str = Field(..., description="Dataset path/identifier used")
    metric_id: Optional[str] = Field(None, description="ID of the metric aggregated")
    record_count: int = Field(..., description="Number of records aggregated")
    applied_filters: Dict[str, Any] = Field(default_factory=dict, description="Filters applied to query dataset")


class AnalyticsResult(BaseModel):
    """Schema for structured aggregation outputs with evidence validation."""
    metric_id: str = Field(..., description="Unique metric identifier")
    metric_name: str = Field(..., description="Human-readable name of metric")
    aggregation: str = Field(..., description="Aggregation operation used (sum, average, etc.)")
    source_field: Optional[str] = Field(None, description="Field aggregated on")
    result_value: float = Field(..., description="Computed numerical result value")
    record_count: int = Field(..., description="Number of records matching filters")
    evidence: EvidenceReference = Field(..., description="Provenance information of analytics results")


class ExecutionPlan(BaseModel):
    """Schema for the deterministic multi-agent execution plan."""
    intent: str = Field(..., description="Classified intent of the request")
    required_capabilities: List[str] = Field(default_factory=list, description="List of capabilities required for execution")
    metric_id: Optional[str] = Field(None, description="Resolved metric ID if applicable")
    requires_data: bool = Field(default=False, description="True if DataAgent needs to retrieve records")
    requires_analytics: bool = Field(default=False, description="True if AnalyticsAgent needs to execute aggregates")
    explanation_required: bool = Field(default=False, description="True if ExplainabilityAgent needs to run")
    unsupported_reason: Optional[str] = Field(None, description="Explanation if the request is not supported")


class WorkflowState(BaseModel):
    """State model tracking the state of the multi-agent cooperative loop."""
    query: str = Field(..., description="The original user query")
    industry: str = Field(..., description="The industry category ('automotive' or 'pharma')")
    intent: Optional[str] = Field(default=None, description="The classified query intent")
    status: Optional[str] = Field(default=None, description="Current workflow status set by agents")
    domain_context: Optional[List[str]] = Field(default=None, description="Key industry-specific terminology loaded from configuration")
    retrieved_data: Optional[
        Union[
            List[ProductionRecord],
            List[BatchRecord],
            List[SupplierRecord],
            List[MaterialRecord],
            List[LocationRecord],
            List[DeviationRecord],
            List[CapaRecord],
        ]
    ] = Field(default=None, description="Loaded database records")
    analytics_output: Optional[AnalyticsOutput] = Field(default=None, description="Legacy aggregate computations results")
    explainability_output: Optional[ExplainabilityOutput] = Field(default=None, description="Legacy formatted audit trace explanation")
    final_response: Optional[str] = Field(default=None, description="Final response answer text")
    execution_history: List[str] = Field(default_factory=list, description="Trace list of all executed agent names")
    
    # New Phase 2 Trace/Analytics Fields
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Transaction correlation ID")
    requested_metric_id: Optional[str] = Field(default=None, description="The configuration metric ID requested")
    requested_filters: Dict[str, Any] = Field(default_factory=dict, description="Dictionary of filters applied during analytics")
    execution_trace: Optional[ExecutionTrace] = Field(default=None, description="Detailed trace events for all agents")
    analytics_result: Optional[AnalyticsResult] = Field(default=None, description="Structured query analytics result")
    
    # New Phase 3 Planner Field
    execution_plan: Optional[ExecutionPlan] = Field(default=None, description="Deterministic multi-agent execution plan")
