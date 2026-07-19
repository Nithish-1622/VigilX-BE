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
        is_groq = settings.llm_provider == "groq"
        if is_groq:
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            payload = json.dumps({
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.llm_api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        else:
            url = f"{self.base_url.rstrip('/')}/api/generate"
            payload = json.dumps(
                {"model": self.model, "prompt": prompt, "stream": False}
            ).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

        req = request.Request(
            url=url,
            data=payload,
            method="POST",
            headers=headers,
        )

        try:
            with request.urlopen(req, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
                if is_groq:
                    choices = body.get("choices", [])
                    if choices:
                        return str(choices[0].get("message", {}).get("content", "")).strip()
                    return ""
                else:
                    return str(body.get("response", "")).strip()
        except error.HTTPError as exc:
            logger.warning("LLM provider HTTP error: %s", exc.code)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM provider unavailable: %s", exc)

        return ""
