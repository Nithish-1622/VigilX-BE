from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from threading import RLock

from schemas.conversation import MessageRecord
from utils.config import settings


class ConversationService:
    def __init__(self, store_path: str | Path | None = None, max_items: int | None = None) -> None:
        self._store_path = Path(store_path or settings.conversation_store_path)
        self._max_items = max_items or settings.max_history_items
        self._lock = RLock()
        self._store: dict[str, list[MessageRecord]] = defaultdict(list)
        self._load()

    def _key(self, user_id: str, session_id: str) -> str:
        return f"{user_id}:{session_id}"

    def add_user_message(self, user_id: str, session_id: str, content: str) -> None:
        with self._lock:
            key = self._key(user_id, session_id)
            self._store[key].append(MessageRecord(role="user", content=content))
            self._trim(key)
            self._persist()

    def add_assistant_message(self, user_id: str, session_id: str, content: str) -> None:
        with self._lock:
            key = self._key(user_id, session_id)
            self._store[key].append(MessageRecord(role="assistant", content=content))
            self._trim(key)
            self._persist()

    def get_history(self, user_id: str, session_id: str) -> list[MessageRecord]:
        with self._lock:
            key = self._key(user_id, session_id)
            return self._store.get(key, []).copy()

    def summarize(self, user_id: str, session_id: str) -> str:
        history = self.get_history(user_id, session_id)
        if not history:
            return "No prior conversation context."

        recent = history[-4:]
        parts = [f"{item.role}: {item.content}" for item in recent]
        return " | ".join(parts)

    def _load(self) -> None:
        if not self._store_path.exists():
            return

        try:
            raw = json.loads(self._store_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return

            loaded: dict[str, list[MessageRecord]] = defaultdict(list)
            for key, items in raw.items():
                if not isinstance(key, str) or not isinstance(items, list):
                    continue

                records: list[MessageRecord] = []
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    try:
                        records.append(MessageRecord.model_validate(item))
                    except Exception:  # noqa: BLE001
                        continue

                if records:
                    loaded[key] = records[-self._max_items :]

            self._store = loaded
        except Exception:  # noqa: BLE001
            self._store = defaultdict(list)

    def _persist(self) -> None:
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {
            key: [message.model_dump() for message in messages]
            for key, messages in self._store.items()
        }
        temp_path = self._store_path.with_suffix(self._store_path.suffix + ".tmp")
        temp_path.write_text(json.dumps(serializable, ensure_ascii=True, indent=2), encoding="utf-8")
        temp_path.replace(self._store_path)

    def _trim(self, key: str) -> None:
        if len(self._store[key]) > self._max_items:
            self._store[key] = self._store[key][-self._max_items :]
