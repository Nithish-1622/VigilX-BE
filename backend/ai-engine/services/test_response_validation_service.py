from __future__ import annotations

import unittest

from services.response_validation_service import ResponseValidationService


class ResponseValidationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = ResponseValidationService()

    def test_extract_case_items_filters_non_dicts(self) -> None:
        payload = {
            "success": True,
            "data": {
                "items": [
                    {"id": "1", "case_id": "C-1", "status": "open"},
                    "invalid",
                ]
            },
        }

        rows = self.validator.extract_sql_items_for_endpoint("cases/search?q=x", payload)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["case_id"], "C-1")

    def test_extract_suspect_items_accepts_expected_fields(self) -> None:
        payload = {
            "success": True,
            "data": {
                "items": [
                    {
                        "id": "S-9",
                        "suspect_id": "S-9",
                        "case_id": "C-2",
                        "name": "John Doe",
                    }
                ]
            },
        }

        rows = self.validator.extract_sql_items_for_endpoint("suspects/search?q=john", payload)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["suspect_id"], "S-9")


if __name__ == "__main__":
    unittest.main()
