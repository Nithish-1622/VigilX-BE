from __future__ import annotations

import asyncio
import json
import itertools
from dataclasses import dataclass
import httpx

from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 3
INITIAL_BACKOFF_S = 1.0  # 1s, 2s, 4s

_key_cycle = None

@dataclass
class LLMClient:
    base_url: str = settings.llm_base_url
    model: str = settings.llm_model

    async def generate(self, prompt: str) -> str:
        # Always use Groq (Cloud LLM)
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        
        global _key_cycle
        if _key_cycle is None:
            keys = [k.strip() for k in settings.llm_api_key.split(",") if k.strip()]
            _key_cycle = itertools.cycle(keys) if keys else itertools.cycle([settings.llm_api_key])
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            for attempt in range(MAX_RETRIES + 1):
                api_key = next(_key_cycle)
                headers["Authorization"] = f"Bearer {api_key}"

                try:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        body = resp.json()
                        choices = body.get("choices", [])
                        if choices:
                            return str(choices[0].get("message", {}).get("content", "")).strip()
                        return ""
                    elif resp.status_code in {429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                        backoff = INITIAL_BACKOFF_S * (2 ** attempt)
                        logger.warning(
                            "LLM rate-limited or unavailable (%s). Trying next key, retry %d/%d after %.1fs backoff",
                            resp.status_code, attempt + 1, MAX_RETRIES, backoff,
                        )
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        logger.warning("LLM provider HTTP error: %s - %s", resp.status_code, resp.text[:200])
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    if attempt < MAX_RETRIES:
                        backoff = INITIAL_BACKOFF_S * (2 ** attempt)
                        logger.warning(
                            "LLM network error/timeout (%s). Trying next key, retry %d/%d after %.1fs backoff",
                            exc, attempt + 1, MAX_RETRIES, backoff,
                        )
                        await asyncio.sleep(backoff)
                        continue
                    logger.warning("LLM network error/timeout: %s", exc)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("LLM provider error: %s", exc)

                break  # Non-retryable error

        return ""
