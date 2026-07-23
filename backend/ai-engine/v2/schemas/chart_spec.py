from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChartType(str, Enum):
    TIMELINE = "timeline"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    NETWORK = "network"
    HEATMAP = "heatmap"
    GEO = "geo"
    TREE = "tree"
    SANKEY = "sankey"
    LINE = "line"


class ChartSpec(BaseModel):
    """
    Frontend-consumable chart specification.
    VisualizationAgent generates specs, not images.
    The React frontend renders these using Recharts / D3 / Leaflet.
    """

    chart_id: str
    chart_type: ChartType
    title: str
    description: str
    data: list[dict[str, Any]] = Field(default_factory=list)
    x_axis: str | None = None
    y_axis: str | None = None
    color_by: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""                  # Why this chart type was chosen
