from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error, request

from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ApiClient:
    base_url: str = settings.api_gateway_base_url

    async def get_json(
        self,
        path: str,
        auth_header: str | None = None,
        context_headers: dict[str, str] | None = None,
    ) -> dict:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        headers: dict[str, str] = {}
        if auth_header:
            headers["Authorization"] = auth_header
        elif settings.downstream_service_token:
            headers["Authorization"] = f"Bearer {settings.downstream_service_token}"
        if context_headers:
            headers.update(context_headers)

        req = request.Request(url=url, method="GET", headers=headers)

        try:
            with request.urlopen(req, timeout=settings.api_gateway_timeout_seconds) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload)
        except error.HTTPError as exc:
            logger.warning("API gateway HTTP error for %s: %s", url, exc.code)
            return {"success": False, "error": f"HTTP {exc.code}"}
        except Exception as exc:  # noqa: BLE001
            logger.warning("API gateway call failed for %s: %s", url, exc)
            return {"success": False, "error": "gateway_unavailable"}
