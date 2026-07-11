from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error, request

from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LLMClient:
    base_url: str = settings.llm_base_url
    model: str = settings.llm_model

    async def generate(self, prompt: str) -> str:
        url = f"{self.base_url.rstrip('/')}/api/generate"
        payload = json.dumps(
            {"model": self.model, "prompt": prompt, "stream": False}
        ).encode("utf-8")

        req = request.Request(
            url=url,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )

        try:
            with request.urlopen(req, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
                return str(body.get("response", "")).strip()
        except error.HTTPError as exc:
            logger.warning("LLM provider HTTP error: %s", exc.code)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM provider unavailable: %s", exc)

        return ""
