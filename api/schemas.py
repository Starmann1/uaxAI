from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Schema for incoming queries to the platform."""
    query: str = Field(..., min_length=1, max_length=1000, description="The user query text")
    industry: str = Field(..., description="The industry category identifier (e.g. 'pharma')")
    metric_id: Optional[str] = Field(None, description="Optional target metric ID")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Optional filters to apply to the dataset")


class CapabilitiesResponse(BaseModel):
    """Schema showing allowed metrics and filters for an industry."""
    industry: str = Field(..., description="The industry category identifier")
    metrics: List[str] = Field(..., description="List of allowed metric IDs")
    allowed_filters: List[str] = Field(..., description="List of allowed filter fields")


class QueryResponse(BaseModel):
    """Schema for structured query responses from the API."""
    correlation_id: str = Field(..., description="Unique correlation ID for tracking")
    status: str = Field(..., description="Final execution status (e.g. COMPLETED, FAILED, UNSUPPORTED)")
    final_response: Optional[str] = Field(None, description="Human-readable response message")
    intent: Optional[str] = Field(None, description="Classified intent")
    plan: Optional[Any] = Field(None, description="Execution plan details")
    analytics_result: Optional[Any] = Field(None, description="Structured analytics calculation outputs")
    explainability_summary: Optional[str] = Field(None, description="Concise human-readable explanation trace")
    execution_trace: Optional[Any] = Field(None, description="Structured execution trace logs")
    errors: Optional[List[str]] = Field(None, description="Details of any execution or validation errors")
