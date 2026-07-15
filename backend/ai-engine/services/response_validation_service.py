from __future__ import annotations

from pydantic import BaseModel, ValidationError

from schemas.api_contracts import (
    ApiItemsEnvelope,
    CaseRecord,
    RetrievalItem,
    SuspectRecord,
    TimelineRecord,
    VictimRecord,
)


class ResponseValidationService:
    def extract_sql_items(self, payload: dict) -> list[dict]:
        envelope = self._parse_envelope(payload)
        if envelope is None:
            return []
        return [item for item in envelope.data.items if isinstance(item, dict)]

    def extract_sql_items_for_endpoint(self, endpoint_path: str, payload: dict) -> list[dict]:
        envelope = self._parse_envelope(payload)
        if envelope is None:
            return []

        if endpoint_path.startswith("cases/search"):
            return self._extract_typed_items(envelope, CaseRecord)
        if endpoint_path.startswith("suspects/search"):
            return self._extract_typed_items(envelope, SuspectRecord)
        if endpoint_path.startswith("victims/search"):
            return self._extract_typed_items(envelope, VictimRecord)
        if endpoint_path.startswith("cases/timeline"):
            return self._extract_typed_items(envelope, TimelineRecord)

        return [item for item in envelope.data.items if isinstance(item, dict)]

    def extract_retrieval_items(self, payload: dict) -> list[RetrievalItem]:
        envelope = self._parse_envelope(payload)
        if envelope is None:
            return []

        valid_items: list[RetrievalItem] = []
        for item in envelope.data.items:
            if not isinstance(item, dict):
                continue
            try:
                valid_items.append(RetrievalItem.model_validate(item))
            except ValidationError:
                continue
        return valid_items

    def _parse_envelope(self, payload: dict) -> ApiItemsEnvelope | None:
        if not isinstance(payload, dict):
            return None
        try:
            return ApiItemsEnvelope.model_validate(payload)
        except ValidationError:
            return None

    def _extract_typed_items(self, envelope: ApiItemsEnvelope, model: type[BaseModel]) -> list[dict]:
        valid_items: list[dict] = []
        for item in envelope.data.items:
            if not isinstance(item, dict):
                continue
            try:
                valid_items.append(model.model_validate(item).model_dump())
            except ValidationError:
                continue
        return valid_items
