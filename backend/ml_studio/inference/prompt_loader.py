from __future__ import annotations

from pathlib import Path
from ml_studio.config import ml_settings


def _read_prompt(file_path: Path) -> str:
    """Read a prompt file safely, returning empty string if file does not exist."""
    if file_path.exists():
        return file_path.read_text(encoding="utf-8").strip()
    return ""


class HierarchicalPromptLoader:
    """
    4-Tier Hierarchical Prompt Composer.

    Composes system prompts in this order:
        1. Base System Prompt   — Core VigilX identity and hallucination guards
        2. Security Guard       — Anti-injection and anti-disclosure directives
        3. Domain Prompt        — Domain-specialist context (legal/finance/security/faq)

    Formula:
        System Prompt = Base + Security + Domain
    """

    DOMAIN_PROMPT_FILES = {
        "legal": "domains/legal.txt",
        "finance": "domains/finance.txt",
        "security": "domains/security.txt",
        "faq": None,
        "general": None,
    }

    def __init__(self, prompt_dir: str | None = None) -> None:
        self._prompt_dir = Path(prompt_dir or ml_settings.prompt_dir)

    def compose(self, domain: str = "general") -> str:
        """
        Compose the complete 4-tier system prompt for a given domain.

        Args:
            domain: One of 'legal', 'finance', 'security', 'faq', 'general'.

        Returns:
            Full composed system prompt string.
        """
        parts: list[str] = []

        # Tier 1: Base system prompt
        base = _read_prompt(self._prompt_dir / "base_system.txt")
        if not base:
            # Fallback to legacy prompt file
            base = _read_prompt(self._prompt_dir / "ml_studio_system_v1.txt")
        if base:
            parts.append(base)

        # Tier 2: Security guard
        security = _read_prompt(self._prompt_dir / "security_system.txt")
        if security:
            parts.append(security)

        # Tier 3: Domain-specific prompt
        domain_key = domain.lower()
        domain_file = self.DOMAIN_PROMPT_FILES.get(domain_key)
        if domain_file:
            domain_prompt = _read_prompt(self._prompt_dir / domain_file)
            if domain_prompt:
                parts.append(domain_prompt)

        return "\n\n---\n\n".join(parts)
