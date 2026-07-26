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


import itertools
_key_cycle = None

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
        
        global _key_cycle
        if _key_cycle is None:
            keys = [k.strip() for k in settings.llm_api_key.split(",") if k.strip()]
            _key_cycle = itertools.cycle(keys) if keys else itertools.cycle([settings.llm_api_key])
        
        api_key = next(_key_cycle)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
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
                with request.urlopen(req, timeout=60) as response:
                    raw_resp = response.read().decode("utf-8")
                    with open("llm_success.log", "a") as f:
                        f.write(f"Resp: {raw_resp}\n")
                    body = json.loads(raw_resp)
                    choices = body.get("choices", [])
                    if choices:
                        return str(choices[0].get("message", {}).get("content", "")).strip()
                    return ""
            except error.HTTPError as exc:
                if exc.code in {429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                    backoff = INITIAL_BACKOFF_S * (2 ** attempt)
                    logger.warning(
                        "LLM rate-limited or unavailable (%s). Retry %d/%d after %.1fs backoff",
                        exc.code, attempt + 1, MAX_RETRIES, backoff,
                    )
                    await asyncio.sleep(backoff)
                    continue
                logger.warning("LLM provider HTTP error: %s", exc.code)
                with open("llm_errors.log", "a") as f:
                    f.write(f"HTTPError: {exc.code} {exc.reason}\n")
            except error.URLError as exc:
                if attempt < MAX_RETRIES:
                    backoff = INITIAL_BACKOFF_S * (2 ** attempt)
                    logger.warning(
                        "LLM network error/timeout (%s). Retry %d/%d after %.1fs backoff",
                        exc.reason, attempt + 1, MAX_RETRIES, backoff,
                    )
                    await asyncio.sleep(backoff)
                    continue
                logger.warning("LLM network error/timeout: %s", exc.reason)
                with open("llm_errors.log", "a") as f:
                    f.write(f"URLError: {exc.reason}\n")
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM provider unavailable: %s", exc)
                with open("llm_errors.log", "a") as f:
                    f.write(f"Exception: {exc}\n")

            break  # Non-retryable error

        return ""

