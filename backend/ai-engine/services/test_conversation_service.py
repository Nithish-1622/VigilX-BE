from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from services.conversation_service import ConversationService


class ConversationServicePersistenceTests(unittest.TestCase):
    def test_history_persists_across_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_path = Path(temp_dir) / "conversation_history.json"

            first = ConversationService(store_path=store_path, max_items=10)
            first.add_user_message("user-1", "sess-1", "hello")
            first.add_assistant_message("user-1", "sess-1", "world")

            second = ConversationService(store_path=store_path, max_items=10)
            history = second.get_history("user-1", "sess-1")

            self.assertEqual(len(history), 2)
            self.assertEqual(history[0].role, "user")
            self.assertEqual(history[0].content, "hello")
            self.assertEqual(history[1].role, "assistant")
            self.assertEqual(history[1].content, "world")

    def test_history_trims_and_persists_trimmed_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store_path = Path(temp_dir) / "conversation_history.json"

            service = ConversationService(store_path=store_path, max_items=2)
            service.add_user_message("user-1", "sess-1", "one")
            service.add_assistant_message("user-1", "sess-1", "two")
            service.add_user_message("user-1", "sess-1", "three")

            reloaded = ConversationService(store_path=store_path, max_items=2)
            history = reloaded.get_history("user-1", "sess-1")

            self.assertEqual(len(history), 2)
            self.assertEqual(history[0].content, "two")
            self.assertEqual(history[1].content, "three")


if __name__ == "__main__":
    unittest.main()
