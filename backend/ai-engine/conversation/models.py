from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConversationContext:
    user_id: str
    session_id: str
    summary: str
