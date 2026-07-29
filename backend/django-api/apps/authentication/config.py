"""
CatalystConfig — Centralized configuration for Zoho Catalyst Authentication.

All Catalyst identifiers, OAuth secrets, and provider settings are loaded
from environment variables. Never hardcode credentials.
"""
import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CatalystConfig:
    """Immutable config snapshot loaded from environment at startup."""

    # Catalyst project identifiers
    project_id: str = ""
    environment: str = "Development"

    # OAuth credentials (for server-side flows if needed)
    client_id: str = ""
    client_secret: str = ""

    # Comma-separated list of enabled sign-in providers
    # e.g. "email,google,zoho"
    enabled_providers_raw: str = "email"

    @property
    def enabled_providers(self) -> list[str]:
        return [p.strip().lower() for p in self.enabled_providers_raw.split(",") if p.strip()]

    @property
    def is_google_enabled(self) -> bool:
        return "google" in self.enabled_providers

    @property
    def is_zoho_enabled(self) -> bool:
        return "zoho" in self.enabled_providers

    @property
    def is_email_enabled(self) -> bool:
        return "email" in self.enabled_providers

    @classmethod
    def from_env(cls) -> "CatalystConfig":
        """Load config from environment variables."""
        return cls(
            project_id=os.getenv("CATALYST_PROJECT_ID", ""),
            environment=os.getenv("CATALYST_ENVIRONMENT", "Development"),
            client_id=os.getenv("CATALYST_CLIENT_ID", ""),
            client_secret=os.getenv("CATALYST_CLIENT_SECRET", ""),
            enabled_providers_raw=os.getenv("ENABLED_AUTH_PROVIDERS", "email,google,zoho"),
        )


# Singleton — loaded once at module import
catalyst_config = CatalystConfig.from_env()
