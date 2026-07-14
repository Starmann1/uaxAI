from typing import Optional

from pydantic import BaseModel, Field

from models.workflow_state import WorkflowState


class AgentRequest(BaseModel):
    """Encapsulates a request input for an agent."""
    state: WorkflowState = Field(..., description="The workflow state to be processed")

class AgentResult(BaseModel):
    """Represents the output result of an agent execution."""
    success: bool = Field(..., description="Execution status indication")
    updated_state: WorkflowState = Field(..., description="Mutated workflow state")
    error_message: Optional[str] = Field(default=None, description="Error message details if failed")
    agent_name: str = Field(..., description="The name identifier of the executing agent")
