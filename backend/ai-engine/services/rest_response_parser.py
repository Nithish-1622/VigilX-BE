from __future__ import annotations

from typing import Any
from pydantic import ValidationError

from schemas.api_contracts import ApiItemsEnvelope
from schemas.rest import RestEndpointDefinition


class RestResponseParser:
    def parse_items(
        self,
        definition: RestEndpointDefinition,
        payload: Any,
    ) -> list[dict]:
        if not payload:
            return []

        # 1. If payload is already a list, return it
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]

        if not isinstance(payload, dict):
            return []

        # 2. Try configured response_items_path first
        path = definition.response_items_path
        current = payload
        found = True
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                found = False
                break
        if found:
            if isinstance(current, list):
                return [item for item in current if isinstance(item, dict)]
            if isinstance(current, dict) and "items" in current and isinstance(current["items"], list):
                return [item for item in current["items"] if isinstance(item, dict)]

        # 3. Fallback heuristics for common Django / DRF responses
        if "results" in payload and isinstance(payload["results"], list):
            return [item for item in payload["results"] if isinstance(item, dict)]

        if "data" in payload:
            data = payload["data"]
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        return [item for item in v if isinstance(item, dict)]
                if "items" in data and isinstance(data["items"], list):
                    return [item for item in data["items"] if isinstance(item, dict)]

        for k, v in payload.items():
            if isinstance(v, list) and k not in {"errors", "messages"}:
                return [item for item in v if isinstance(item, dict)]

        return []

    def _parse_envelope(self, payload: dict) -> ApiItemsEnvelope | None:
        if not isinstance(payload, dict):
            return None
        try:
            return ApiItemsEnvelope.model_validate(payload)
        except ValidationError:
            return None


