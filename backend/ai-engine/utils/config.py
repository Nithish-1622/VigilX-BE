from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("AI_ENGINE_APP_NAME", "Crime Intelligence AI Engine")
    app_version: str = os.getenv("AI_ENGINE_APP_VERSION", "0.1.0")
    log_level: str = os.getenv("AI_ENGINE_LOG_LEVEL", "INFO")

    llm_provider: str = os.getenv("AI_ENGINE_LLM_PROVIDER", "ollama")
    llm_model: str = os.getenv("AI_ENGINE_LLM_MODEL", "qwen3")
    llm_base_url: str = os.getenv("AI_ENGINE_LLM_BASE_URL", "http://localhost:11434")
    llm_api_key: str = os.getenv("AI_ENGINE_LLM_API_KEY", "")

    api_gateway_base_url: str = os.getenv("AI_ENGINE_API_GATEWAY_BASE_URL", "")
    api_gateway_timeout_seconds: int | None = (
        int(os.getenv("AI_ENGINE_API_GATEWAY_TIMEOUT_SECONDS", ""))
        if os.getenv("AI_ENGINE_API_GATEWAY_TIMEOUT_SECONDS", "").strip()
        else None
    )
    downstream_service_token: str = os.getenv("AI_ENGINE_DOWNSTREAM_SERVICE_TOKEN", "")

    rest_api_base_url: str = os.getenv("AI_ENGINE_REST_BASE_URL", "")
    rest_api_timeout_seconds: int | None = (
        int(os.getenv("AI_ENGINE_REST_TIMEOUT_SECONDS", ""))
        if os.getenv("AI_ENGINE_REST_TIMEOUT_SECONDS", "").strip()
        else None
    )
    rest_api_max_retries: int = int(os.getenv("AI_ENGINE_REST_MAX_RETRIES", "2"))
    rest_api_backoff_seconds: float = float(os.getenv("AI_ENGINE_REST_BACKOFF_SECONDS", "0.5"))

    max_context_items: int = int(os.getenv("AI_ENGINE_MAX_CONTEXT_ITEMS", "8"))
    max_history_items: int = int(os.getenv("AI_ENGINE_MAX_HISTORY_ITEMS", "12"))
    summarize_history_trigger_items: int = int(
        os.getenv("AI_ENGINE_SUMMARIZE_HISTORY_TRIGGER_ITEMS", "6")
    )
    min_citations_default: int = int(os.getenv("AI_ENGINE_MIN_CITATIONS_DEFAULT", "1"))
    min_citations_case_lookup: int = int(
        os.getenv("AI_ENGINE_MIN_CITATIONS_CASE_LOOKUP", "1")
    )
    min_citations_timeline_query: int = int(
        os.getenv("AI_ENGINE_MIN_CITATIONS_TIMELINE_QUERY", "2")
    )
    min_citations_suspect_query: int = int(
        os.getenv("AI_ENGINE_MIN_CITATIONS_SUSPECT_QUERY", "2")
    )
    min_citations_victim_query: int = int(
        os.getenv("AI_ENGINE_MIN_CITATIONS_VICTIM_QUERY", "2")
    )
    conversation_store_path: str = os.getenv(
        "AI_ENGINE_CONVERSATION_STORE_PATH",
        str(Path(__file__).resolve().parent.parent / "services" / "conversation_history.json"),
    )


settings = Settings()
