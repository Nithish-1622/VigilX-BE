from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from v2.schemas.execution_plan import DependencyType, ToolType


class ToolInputSchema(BaseModel):
    """Describes what parameters a tool accepts — exposed to the Planning Agent."""

    required: list[str] = Field(default_factory=list)
    optional: list[str] = Field(default_factory=list)
    example: dict[str, Any] = Field(default_factory=dict)


class ToolCapability(BaseModel):
    """
    Complete descriptor for a registered tool.
    The PlanningAgent queries these to decide WHICH tools to include in ExecutionPlan.
    New tools can be registered without touching any agent code.
    """

    tool_type: ToolType
    name: str
    description: str
    input_schema: ToolInputSchema = Field(default_factory=ToolInputSchema)
    output_description: str = ""
    supported_intents: list[str] = Field(default_factory=list)
    is_optional: bool = False            # Optional tools excluded from core pipeline
    default_dependency: DependencyType = DependencyType.INDEPENDENT
    average_latency_ms: int = 500
    enabled: bool = True
