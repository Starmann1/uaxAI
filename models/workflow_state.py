from typing import List, Optional, Union

from pydantic import BaseModel, Field

from models.data_models import BatchRecord, ProductionRecord


class AnalyticsOutput(BaseModel):
    """Schema for data analytics aggregation results."""
    metric_name: str
    result_value: float
    record_count: int

class ExplainabilityOutput(BaseModel):
    """Schema for explainability audit trail/logs."""
    trace_summary: str
    steps_executed: List[str]

class WorkflowState(BaseModel):
    """State model tracking the state of the multi-agent cooperative loop."""
    query: str = Field(..., description="The original user query")
    industry: str = Field(..., description="The industry category ('automotive' or 'pharma')")
    intent: Optional[str] = Field(default=None, description="The classified query intent")
    status: Optional[str] = Field(default=None, description="Current workflow status set by agents")
    domain_context: Optional[List[str]] = Field(default=None, description="Key industry-specific terminology loaded from configuration")
    retrieved_data: Optional[Union[List[ProductionRecord], List[BatchRecord]]] = Field(default=None, description="Loaded database records")
    analytics_output: Optional[AnalyticsOutput] = Field(default=None, description="Aggregate computations results")
    explainability_output: Optional[ExplainabilityOutput] = Field(default=None, description="Formatted audit trace explanation")
    final_response: Optional[str] = Field(default=None, description="Final response answer text")
    execution_history: List[str] = Field(default_factory=list, description="Trace list of all executed agent names")
