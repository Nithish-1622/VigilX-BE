from __future__ import annotations

"""
ML Studio — Local Inference Client
====================================
Queries a locally running Ollama model using its OpenAI-compatible API.

This client intentionally mirrors the interface of ai-engine/llm/client.py
so responses are structurally identical — same StandardResponse shape,
same system prompt behaviour, same temperature.

Endpoint used:
    POST http://localhost:11434/v1/chat/completions

The Ollama model used is either:
  - The currently ACTIVE model in ModelRegistry (auto-selected)
  - An explicit model name passed via InferenceRequest.model_override
"""

import asyncio
import logging
import time
from typing import Optional

import httpx

from ml_studio.config import ml_settings
from ml_studio.core.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_BACKOFF_S = 1.0


class LocalInferenceClient:
    """
    Sends chat completion requests to a locally running Ollama instance.

    Usage:
        client = LocalInferenceClient()
        result = await client.generate(question="What is FIR-2025-042?")
    """

    def __init__(self) -> None:
        self._model_reg = ModelRegistry()
        self._base_url = ml_settings.ollama_base_url.rstrip("/")

    # ── Primary method ─────────────────────────────────────────────────────────

    async def generate(
        self,
        question: str,
        model_override: Optional[str] = None,
        system_context: Optional[str] = None,
    ) -> dict:
        """
        Send a question to the active local Ollama model.

        Args:
            question:        The user's input question.
            model_override:  Ollama model name (overrides active model).
            system_context:  Optional extra system context injected into
                             the system message (e.g. retrieved evidence).

        Returns:
            dict with keys: answer (str), model_used (str), tokens_used (int|None),
                            latency_ms (float).

        Raises:
            RuntimeError: If no active model is found and no override given,
                          or if Ollama is unreachable after retries.
        """
        model_name = model_override or self._resolve_active_model()
        endpoint = f"{self._base_url}/v1/chat/completions"

        # ── Build messages ────────────────────────────────────────────────────
        messages = self._build_messages(question, system_context)

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": ml_settings.inference_temperature,
            "stream": False,
        }

        # ── HTTP request with retries ──────────────────────────────────────────
        t_start = time.perf_counter()
        async with httpx.AsyncClient(timeout=120.0) as client:
            for attempt in range(MAX_RETRIES + 1):
                try:
                    resp = await client.post(endpoint, json=payload)
                    if resp.status_code == 200:
                        body = resp.json()
                        latency_ms = round((time.perf_counter() - t_start) * 1000, 1)
                        choices = body.get("choices", [])
                        answer = ""
                        if choices:
                            answer = str(
                                choices[0].get("message", {}).get("content", "")
                            ).strip()
                        usage = body.get("usage", {})
                        tokens = usage.get("total_tokens") or usage.get("completion_tokens")
                        return {
                            "answer": answer,
                            "model_used": model_name,
                            "tokens_used": tokens,
                            "latency_ms": latency_ms,
                        }

                    elif resp.status_code in {429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                        backoff = INITIAL_BACKOFF_S * (2 ** attempt)
                        logger.warning(
                            "Ollama HTTP %s on attempt %d/%d — retrying in %.1fs",
                            resp.status_code, attempt + 1, MAX_RETRIES, backoff,
                        )
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        err_body = resp.text[:300]
                        logger.error("Ollama inference error %s: %s", resp.status_code, err_body)
                        raise RuntimeError(
                            f"Ollama returned HTTP {resp.status_code}: {err_body}"
                        )

                except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError) as exc:
                    if attempt < MAX_RETRIES:
                        backoff = INITIAL_BACKOFF_S * (2 ** attempt)
                        logger.warning(
                            "Ollama network error (%s) attempt %d/%d — retrying in %.1fs",
                            exc, attempt + 1, MAX_RETRIES, backoff,
                        )
                        await asyncio.sleep(backoff)
                        continue
                    raise RuntimeError(
                        f"Ollama is unreachable at {self._base_url} after {MAX_RETRIES} retries. "
                        "Is Ollama running? (run: ollama serve)"
                    ) from exc

                break  # Non-retryable path

        # Should never reach here — added for type safety
        raise RuntimeError("Inference failed after all retries.")

    # ── Health check ───────────────────────────────────────────────────────────

    async def health_check(self) -> dict:
        """Return Ollama connectivity status and active model info."""
        active = self._model_reg.get_active()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._base_url}/")
                ollama_up = resp.status_code < 500
        except Exception:
            ollama_up = False

        return {
            "ollama_reachable": ollama_up,
            "ollama_base_url": self._base_url,
            "active_model": active.ollama_model_name if active else None,
            "active_model_id": active.model_id if active else None,
        }

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _resolve_active_model(self) -> str:
        active = self._model_reg.get_active()
        if active is None or not active.ollama_model_name:
            raise RuntimeError(
                "No active local model found. "
                "Upload a dataset, train a model, and activate it via POST /ml/models/{id}/activate."
            )
        return active.ollama_model_name

    @staticmethod
    def _build_messages(question: str, system_context: Optional[str]) -> list[dict]:
        """
        Build the messages list for the chat completions API.
        The system message is embedded in the Modelfile (via OllamaBridge),
        so here we only add optional extra context and the user message.
        """
        messages: list[dict] = []

        if system_context and system_context.strip():
            # Inject retrieved evidence or other context as a system-role addendum
            messages.append({
                "role": "system",
                "content": (
                    "Additional context for this query:\n"
                    + system_context.strip()
                ),
            })

        messages.append({"role": "user", "content": question})
        return messages
