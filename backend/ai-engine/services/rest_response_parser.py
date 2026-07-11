from __future__ import annotations

from pydantic import ValidationError

from schemas.api_contracts import ApiItemsEnvelope
from schemas.rest import RestEndpointDefinition


class RestResponseParser:
    def parse_items(
        self,
        definition: RestEndpointDefinition,
        payload: dict,
    ) -> list[dict]:
        envelope = self._parse_envelope(payload)
        if envelope is None:
            return []

        return [item for item in envelope.data.items if isinstance(item, dict)]

    def _parse_envelope(self, payload: dict) -> ApiItemsEnvelope | None:
        if not isinstance(payload, dict):
            return None
        try:
            return ApiItemsEnvelope.model_validate(payload)
        except ValidationError:
            return None

