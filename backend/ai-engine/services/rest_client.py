from __future__ import annotations

import json
import time
from dataclasses import dataclass
from urllib import error, parse, request

from schemas.rest import RestEndpointDefinition, RestInvocationRequest, RestInvocationResponse, RestMethod, StructuredQuery
from services.rest_endpoint_registry import RestEndpointRegistry
from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RestClient:
    registry: RestEndpointRegistry

    def invoke(self, invocation: RestInvocationRequest) -> RestInvocationResponse:
        definition = invocation.definition
        base_url = self.registry.base_url().strip()
        if not base_url:
            return RestInvocationResponse(
                capability=definition.capability,
                success=False,
                error="rest_base_url_not_configured",
            )

        timeout_seconds = definition.timeout_seconds
        if timeout_seconds is None:
            timeout_seconds = self._default_timeout_seconds()
        if timeout_seconds is None:
            return RestInvocationResponse(
                capability=definition.capability,
                success=False,
                error="timeout_not_configured",
            )

        url = self._compose_url(base_url, definition.path, invocation.query, definition)
        headers = dict(invocation.context_headers)
        if invocation.auth_header:
            headers["Authorization"] = invocation.auth_header

        headers.setdefault("Accept", "application/json")

        data = self._build_body(definition, invocation)
        attempts = max(0, definition.max_retries) + 1
        last_error: str | None = None

        for attempt in range(1, attempts + 1):
            try:
                req = request.Request(url=url, method=definition.method.value, headers=headers, data=data)
                with request.urlopen(req, timeout=timeout_seconds) as response:
                    payload = response.read().decode("utf-8")
                    parsed = json.loads(payload) if payload else {}
                    return RestInvocationResponse(
                        capability=definition.capability,
                        success=True,
                        status_code=getattr(response, "status", 200),
                        attempts=attempt,
                        payload=parsed if isinstance(parsed, dict) else {"data": parsed},
                    )
            except error.HTTPError as exc:
                last_error = f"HTTP {exc.code}"
                logger.warning("REST HTTP error for %s: %s", url, exc.code)
                if attempt < attempts:
                    time.sleep(definition.backoff_seconds)
                    continue
                return RestInvocationResponse(
                    capability=definition.capability,
                    success=False,
                    status_code=exc.code,
                    attempts=attempt,
                    error=last_error,
                )
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                logger.warning("REST invocation failed for %s: %s", url, exc)
                if attempt < attempts:
                    time.sleep(definition.backoff_seconds)
                    continue
                return RestInvocationResponse(
                    capability=definition.capability,
                    success=False,
                    attempts=attempt,
                    error=last_error,
                )

        return RestInvocationResponse(
            capability=definition.capability,
            success=False,
            attempts=attempts,
            error=last_error or "rest_call_failed",
        )

    def _compose_url(
        self,
        base_url: str,
        path: str,
        query: StructuredQuery,
        definition: RestEndpointDefinition,
    ) -> str:
        normalized = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        if definition.method != RestMethod.GET:
            return normalized

        query_params: dict[str, str] = {}
        if definition.request_query_param and query.query_text:
            query_params[definition.request_query_param] = query.query_text
        if query.identifiers:
            query_params.update({key: str(value) for key, value in query.identifiers.items() if value is not None})
        if query.filters:
            query_params.update({key: str(value) for key, value in query.filters.items() if value is not None})

        if not query_params:
            return normalized

        return f"{normalized}?{parse.urlencode(query_params)}"

    def _build_body(self, definition: RestEndpointDefinition, invocation: RestInvocationRequest) -> bytes | None:
        if definition.method == RestMethod.GET:
            return None

        body = invocation.query.model_dump()
        if definition.request_body_key:
            body = {definition.request_body_key: body}
        return json.dumps(body, ensure_ascii=True).encode("utf-8")

    def _default_timeout_seconds(self) -> int | None:
        return settings.rest_api_timeout_seconds
