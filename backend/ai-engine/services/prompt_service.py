from __future__ import annotations

from pathlib import Path

from utils.logging import get_logger

logger = get_logger(__name__)


class PromptService:
    def __init__(self, prompt_dir: Path) -> None:
        self._prompt_dir = prompt_dir
        self._cache: dict[str, str] = {}

    def get_template(self, template_name: str) -> str:
        if template_name in self._cache:
            return self._cache[template_name]

        template_path = self._prompt_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {template_name}")

        content = template_path.read_text(encoding="utf-8")
        self._cache[template_name] = content
        return content

    def render(self, template_name: str, **kwargs: str) -> str:
        template = self.get_template(template_name)
        try:
            return template.format(**kwargs)
        except KeyError as exc:
            logger.exception("Missing template placeholder")
            raise ValueError(f"Missing prompt parameter: {exc}") from exc
