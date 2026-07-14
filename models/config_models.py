from typing import List

from pydantic import BaseModel, Field


class IndustryConfig(BaseModel):
    industry_name: str = Field(..., description="The name key of the industry (e.g. automotive, pharma)")
    display_name: str = Field(..., description="Human-friendly display name of the industry")
    terminology: List[str] = Field(default_factory=list, description="3-4 terminology terms for this industry")
    entity_list: List[str] = Field(default_factory=list, description="A list of relevant entity names")
    metric: str = Field(..., description="The primary metric of interest (e.g., OEE, Batch Yield)")
    dataset_reference: str = Field(..., description="Relative or absolute path reference to the dataset CSV file")
