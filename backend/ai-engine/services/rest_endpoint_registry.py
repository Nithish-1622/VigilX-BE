from __future__ import annotations

import os

from schemas.rest import RestCapability, RestEndpointDefinition, RestMethod
from utils.config import settings


class RestEndpointRegistry:
    def __init__(self) -> None:
        self._base_url = settings.rest_api_base_url.strip()

    def get(self, capability: RestCapability) -> RestEndpointDefinition | None:
        path_env = self._path_env_name(capability)
        path = os.getenv(path_env, "").strip()
        if not path:
            return None

        method = RestMethod(os.getenv(self._method_env_name(capability), "GET").upper())
        timeout_raw = os.getenv(self._timeout_env_name(capability), "").strip()
        retries_raw = os.getenv(self._retries_env_name(capability), "").strip()
        backoff_raw = os.getenv(self._backoff_env_name(capability), "").strip()
        query_param = os.getenv(self._query_param_env_name(capability), "").strip() or None
        body_key = os.getenv(self._body_key_env_name(capability), "").strip() or None
        response_path = os.getenv(self._response_path_env_name(capability), "").strip()

        return RestEndpointDefinition(
            capability=capability,
            path=path,
            method=method,
            timeout_seconds=int(timeout_raw) if timeout_raw else None,
            max_retries=int(retries_raw) if retries_raw else 0,
            backoff_seconds=float(backoff_raw) if backoff_raw else 0.0,
            request_query_param=query_param,
            request_body_key=body_key,
            response_items_path=response_path.split(".") if response_path else ["data", "items"],
        )

    def base_url(self) -> str:
        return self._base_url

    def _path_env_name(self, capability: RestCapability) -> str:
        return f"AI_ENGINE_REST_{capability.value.upper()}_PATH"

    def _method_env_name(self, capability: RestCapability) -> str:
        return f"AI_ENGINE_REST_{capability.value.upper()}_METHOD"

    def _timeout_env_name(self, capability: RestCapability) -> str:
        return f"AI_ENGINE_REST_{capability.value.upper()}_TIMEOUT_SECONDS"

    def _retries_env_name(self, capability: RestCapability) -> str:
        return f"AI_ENGINE_REST_{capability.value.upper()}_MAX_RETRIES"

    def _backoff_env_name(self, capability: RestCapability) -> str:
        return f"AI_ENGINE_REST_{capability.value.upper()}_BACKOFF_SECONDS"

    def _query_param_env_name(self, capability: RestCapability) -> str:
        return f"AI_ENGINE_REST_{capability.value.upper()}_QUERY_PARAM"

    def _body_key_env_name(self, capability: RestCapability) -> str:
        return f"AI_ENGINE_REST_{capability.value.upper()}_BODY_KEY"

    def _response_path_env_name(self, capability: RestCapability) -> str:
        return f"AI_ENGINE_REST_{capability.value.upper()}_RESPONSE_ITEMS_PATH"
