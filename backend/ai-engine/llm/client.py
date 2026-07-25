from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from urllib import error, request

from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 3
INITIAL_BACKOFF_S = 2.0  # 2s, 4s, 8s


@dataclass
class LLMClient:
    base_url: str = settings.llm_base_url
    model: str = settings.llm_model

    async def generate(self, prompt: str) -> str:
        # Always use Groq (Cloud LLM)
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

        for attempt in range(MAX_RETRIES + 1):
            req = request.Request(
                url=url,
                data=payload,
                method="POST",
                headers=headers,
            )

            try:
                with request.urlopen(req, timeout=30) as response:
                    body = json.loads(response.read().decode("utf-8"))
                    choices = body.get("choices", [])
                    if choices:
                        return str(choices[0].get("message", {}).get("content", "")).strip()
                    return ""
            except error.HTTPError as exc:
                if exc.code == 429 and attempt < MAX_RETRIES:
                    backoff = INITIAL_BACKOFF_S * (2 ** attempt)
                    logger.warning(
                        "LLM rate-limited (429). Retry %d/%d after %.1fs backoff",
                        attempt + 1, MAX_RETRIES, backoff,
                    )
                    await asyncio.sleep(backoff)
                    continue
                logger.warning("LLM provider HTTP error: %s", exc.code)
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM provider unavailable: %s", exc)

            break  # Non-retryable error

        return ""

