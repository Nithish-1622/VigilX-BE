"""
Tests for LocalInferenceClient — mocked Ollama responses.
Run: pytest backend/ml_studio/tests/test_inference_client.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))


# ── Helpers ────────────────────────────────────────────────────────────────────

def _mock_ollama_response(answer: str, tokens: int = 42) -> MagicMock:
    """Build a mock httpx.Response that Ollama would return."""
    body = {
        "choices": [{"message": {"role": "assistant", "content": answer}}],
        "usage": {"total_tokens": tokens, "completion_tokens": tokens // 2},
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = body
    return mock_resp


def _mock_http_error(status_code: int) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.text = f"HTTP {status_code} error"
    return mock_resp


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def client_with_active_model(tmp_path, monkeypatch):
    """Client with a mocked active model in the registry."""
    monkeypatch.setenv("ML_STUDIO_REGISTRY_DIR", str(tmp_path))
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")

    from ml_studio.core.model_registry import ModelRegistry
    from ml_studio.schemas.model import ModelStatus, RegisteredModel
    from datetime import datetime
    import uuid

    reg = ModelRegistry()
    model = RegisteredModel(
        model_id=str(uuid.uuid4()),
        model_name="test-finetune",
        ollama_model_name="vigilx-test-v1",
        base_model="llama3.1",
        job_id="job-test",
        adapter_path="/tmp/adapter",
        status=ModelStatus.ACTIVE,
        is_active=True,
        training_steps=100,
        created_at=datetime.utcnow(),
        activated_at=datetime.utcnow(),
    )
    reg.create(model)
    reg.activate(model.model_id)

    from ml_studio.core.inference_client import LocalInferenceClient
    return LocalInferenceClient(), model.ollama_model_name


# ── generate() tests ───────────────────────────────────────────────────────────

class TestGenerate:

    @pytest.mark.asyncio
    async def test_successful_inference(self, client_with_active_model):
        client, model_name = client_with_active_model
        expected_answer = "The accused Rajesh Kumar was arrested on 2025-03-15."

        with patch("httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_http
            mock_http.post = AsyncMock(return_value=_mock_ollama_response(expected_answer))

            result = await client.generate("Who was arrested in FIR-2025-001?")

        assert result["answer"] == expected_answer
        assert result["model_used"] == model_name
        assert result["tokens_used"] == 42
        assert result["latency_ms"] > 0

    @pytest.mark.asyncio
    async def test_model_override_respected(self, client_with_active_model):
        client, _ = client_with_active_model

        with patch("httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_http
            mock_http.post = AsyncMock(return_value=_mock_ollama_response("override answer"))

            result = await client.generate(
                "test question",
                model_override="custom-model:7b",
            )

        assert result["model_used"] == "custom-model:7b"

    @pytest.mark.asyncio
    async def test_no_active_model_raises(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ML_STUDIO_REGISTRY_DIR", str(tmp_path))

        from ml_studio.core.inference_client import LocalInferenceClient
        client = LocalInferenceClient()

        with pytest.raises(RuntimeError, match="No active local model"):
            await client.generate("test question")

    @pytest.mark.asyncio
    async def test_retries_on_503(self, client_with_active_model):
        client, _ = client_with_active_model

        responses = [
            _mock_http_error(503),
            _mock_http_error(503),
            _mock_ollama_response("recovered answer"),
        ]

        call_count = 0

        async def _post(*args, **kwargs):
            nonlocal call_count
            resp = responses[min(call_count, len(responses) - 1)]
            call_count += 1
            return resp

        with patch("httpx.AsyncClient") as mock_cls:
            with patch("asyncio.sleep", new_callable=AsyncMock):
                mock_http = AsyncMock()
                mock_cls.return_value.__aenter__.return_value = mock_http
                mock_http.post = _post

                result = await client.generate("retry question")

        assert result["answer"] == "recovered answer"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_system_context_injected(self, client_with_active_model):
        client, _ = client_with_active_model
        captured_payload = {}

        async def _post(url, json=None, **kwargs):
            captured_payload.update(json or {})
            return _mock_ollama_response("context-aware answer")

        with patch("httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_http
            mock_http.post = _post

            await client.generate(
                "What happened?",
                system_context="FIR-2025-042: Theft of electronics worth ₹5L.",
            )

        messages = captured_payload.get("messages", [])
        system_messages = [m for m in messages if m.get("role") == "system"]
        assert any("FIR-2025-042" in m["content"] for m in system_messages)


# ── health_check() tests ────────────────────────────────────────────────────────

class TestHealthCheck:

    @pytest.mark.asyncio
    async def test_health_when_ollama_up(self, client_with_active_model):
        client, model_name = client_with_active_model

        with patch("httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_http
            mock_http.get = AsyncMock(return_value=MagicMock(status_code=200))

            health = await client.health_check()

        assert health["ollama_reachable"] is True
        assert health["active_model"] == model_name

    @pytest.mark.asyncio
    async def test_health_when_ollama_down(self, client_with_active_model):
        client, _ = client_with_active_model

        import httpx as real_httpx

        with patch("httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_http
            mock_http.get = AsyncMock(side_effect=real_httpx.ConnectError("refused"))

            health = await client.health_check()

        assert health["ollama_reachable"] is False
