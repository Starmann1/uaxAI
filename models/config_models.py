from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class MetricDefinition(BaseModel):
    metric_id: str = Field(..., description="Unique metric identifier")
    operation: Literal["sum", "average", "count", "min", "max"] = Field(..., description="Aggregation operation")
    target_field: Optional[str] = Field(None, description="The record field to aggregate")
    filter_field: Optional[str] = Field(None, description="Optional record field to filter on before aggregation")
    filter_value: Optional[str] = Field(None, description="Optional value to filter on before aggregation")
    display_name: str = Field(..., description="Human-readable name of the metric")


class IndustryConfig(BaseModel):
    industry_name: str = Field(..., description="The name key of the industry (e.g. automotive, pharma)")
    display_name: str = Field(..., description="Human-friendly display name of the industry")
    terminology: List[str] = Field(default_factory=list, description="3-4 terminology terms for this industry")
    entity_list: List[str] = Field(default_factory=list, description="A list of relevant entity names")
    metric: str = Field(..., description="The primary metric of interest (e.g., OEE, Batch Yield)")
    dataset_reference: str = Field(..., description="Relative or absolute path reference to the dataset CSV file")
    record_schema: Optional[str] = Field(None, description="Optional record schema identifier (e.g., pharmaceutical_batch)")
    supported_capabilities: List[str] = Field(default_factory=list, description="List of supported intents/capabilities")
    allowed_filters: List[str] = Field(default_factory=list, description="List of fields allowed for filtering")
    metrics: List[MetricDefinition] = Field(default_factory=list, description="Configured metrics for the industry")
