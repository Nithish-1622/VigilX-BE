from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from schemas.common import Citation
from v2.schemas.execution_plan import ToolType


class ToolResult(BaseModel):
    """
    Standardised output from every tool agent.
    The ToolRouterAgent collects these after dispatching.
    """

    tool: ToolType
    subtask_id: str | None = None
    success: bool
    records: list[dict[str, Any]] = Field(default_factory=list)
    text: str = ""                        # Human-readable summary of findings
    citations: list[Citation] = Field(default_factory=list)
    error: str | None = None
    execution_time_ms: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AggregatedEvidence(BaseModel):
    """
    All tool results merged into a single evidence object.
    Produced by EvidenceFusionAgent after ToolRouterAgent completes.
    """

    tool_results: list[ToolResult] = Field(default_factory=list)
    merged_text: str = ""
    all_citations: list[Citation] = Field(default_factory=list)
    source_breakdown: dict[str, int] = Field(default_factory=dict)
    total_records: int = 0
