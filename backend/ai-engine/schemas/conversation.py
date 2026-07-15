from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    question: str = Field(min_length=1, max_length=5000)


class MessageRecord(BaseModel):
    role: str
    content: str


class AskData(BaseModel):
    answer: str
    intent: str
    summary: str | None = None
    case_summary: dict[str, Any] | None = None
    evidence_used: int = 0
