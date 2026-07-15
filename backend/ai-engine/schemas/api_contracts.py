from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ApiItemsData(BaseModel):
    items: list[object] = Field(default_factory=list)


class ApiItemsEnvelope(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool | None = None
    data: ApiItemsData = Field(default_factory=ApiItemsData)


class RetrievalItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    source: str
    snippet: str
    id: str | int | None = None
    score: float | None = None


class CaseRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | int | None = None
    case_id: str | int | None = None
    status: str | None = None
    summary: str | None = None
    timestamp: str | None = None


class SuspectRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | int | None = None
    suspect_id: str | int | None = None
    case_id: str | int | None = None
    name: str | None = None
    status: str | None = None


class VictimRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | int | None = None
    victim_id: str | int | None = None
    case_id: str | int | None = None
    name: str | None = None
    injury_status: str | None = None


class TimelineRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | int | None = None
    case_id: str | int | None = None
    timestamp: str | None = None
    event_type: str | None = None
    description: str | None = None
