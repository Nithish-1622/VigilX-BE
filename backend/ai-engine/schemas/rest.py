from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RestCapability(str, Enum):
    CRIME_RECORDS = "crime_records"
    FIR_RECORDS = "fir_records"
    ACCUSED_RECORDS = "accused_records"
    VICTIM_RECORDS = "victim_records"
    CASE_SEARCH = "case_search"
    CRIMINAL_HISTORY = "criminal_history"
    INVESTIGATION_STATUS = "investigation_status"
    CASE_SUMMARY = "case_summary"


class RestMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class StructuredQuery(BaseModel):
    capability: RestCapability
    intent: str
    question: str
    user_id: str | None = None
    session_id: str | None = None
    correlation_id: str | None = None
    query_text: str | None = None
    identifiers: dict[str, Any] = Field(default_factory=dict)
    filters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)


class RestEndpointDefinition(BaseModel):
    capability: RestCapability
    path: str = ""
    method: RestMethod = RestMethod.GET
    timeout_seconds: int | None = None
    max_retries: int = 0
    backoff_seconds: float = 0.0
    request_mode: str = "structured_json"
    request_query_param: str | None = None
    request_body_key: str | None = None
    response_items_path: list[str] = Field(default_factory=lambda: ["data", "items"])


class RestInvocationRequest(BaseModel):
    definition: RestEndpointDefinition
    query: StructuredQuery
    auth_header: str | None = None
    context_headers: dict[str, str] = Field(default_factory=dict)


class RestInvocationResponse(BaseModel):
    capability: RestCapability
    success: bool
    status_code: int | None = None
    attempts: int = 0
    payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
