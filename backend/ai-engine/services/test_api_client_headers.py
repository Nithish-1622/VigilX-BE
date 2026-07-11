from __future__ import annotations

import unittest
from unittest.mock import patch

from services.api_client import ApiClient


class _DummyResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return b'{"success": true, "data": {"items": []}}'


class ApiClientHeaderTests(unittest.IsolatedAsyncioTestCase):
    async def test_forward_auth_and_context_headers(self) -> None:
        client = ApiClient(base_url="http://localhost:8000/api")

        with patch("services.api_client.request.urlopen", return_value=_DummyResponse()) as mocked:
            await client.get_json(
                "cases/search?q=x",
                auth_header="Bearer abc",
                context_headers={"x-session-id": "sess-1", "x-user-id": "user-1"},
            )

            req = mocked.call_args[0][0]
            normalized = {k.lower(): v for k, v in req.headers.items()}
            self.assertEqual(normalized.get("authorization"), "Bearer abc")
            self.assertEqual(normalized.get("x-session-id"), "sess-1")
            self.assertEqual(normalized.get("x-user-id"), "user-1")


if __name__ == "__main__":
    unittest.main()
