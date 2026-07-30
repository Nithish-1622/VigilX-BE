from __future__ import annotations

import sys
from pathlib import Path
import pytest

_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from ml_studio.datasets.cleaner import clean_text, clean_dataset_rows
from ml_studio.datasets.pii_detector import PIIDetector
from ml_studio.datasets.tokenizer import estimate_token_count, analyze_sequence_lengths, truncate_row
from ml_studio.datasets.detector import classify_dataset, DatasetDomainType


class TestCleaner:
    def test_strip_html_and_control_chars(self):
        dirty = "<p>Hello <b>World</b>!</p>\x00\x07"
        cleaned = clean_text(dirty)
        assert "Hello World!" in cleaned
        assert "<p>" not in cleaned
        assert "\x00" not in cleaned

    def test_fix_whitespace_and_quotes(self):
        text = "“Special”   \n\n\n   text — dash."
        cleaned = clean_text(text)
        assert '"Special"' in cleaned
        assert "text - dash." in cleaned
        assert "\n\n\n" not in cleaned

    def test_clean_dataset_rows(self):
        rows = [{"prompt": "<h1>Question?</h1>", "completion": "<div>Answer</div>"}]
        cleaned = clean_dataset_rows(rows)
        assert cleaned[0]["prompt"] == "Question?"
        assert cleaned[0]["completion"] == "Answer"


class TestPIIDetector:
    def test_detect_pan_and_aadhaar(self):
        detector = PIIDetector()
        text = "Aadhaar: 3679 1234 5678, PAN: ABCDE1234F"
        res = detector.scan_and_redact(text)
        assert res.pii_found is True
        assert "[REDACTED_AADHAAR]" in res.redacted_text
        assert "[REDACTED_PAN]" in res.redacted_text
        assert res.counts["aadhaar"] == 1
        assert res.counts["pan"] == 1

    def test_detect_email_and_phone(self):
        detector = PIIDetector()
        text = "Contact suspect at officer@vigilx.ai or +91-9876543210"
        res = detector.scan_and_redact(text)
        assert res.pii_found is True
        assert "[REDACTED_EMAIL]" in res.redacted_text
        assert "[REDACTED_PHONE]" in res.redacted_text

    def test_redact_dataset_rows(self):
        detector = PIIDetector()
        rows = [{"prompt": "User email is test@domain.com", "completion": "Phone: 9876543210"}]
        redacted_rows, counts = detector.redact_dataset_rows(rows)
        assert "[REDACTED_EMAIL]" in redacted_rows[0]["prompt"]
        assert "[REDACTED_PHONE]" in redacted_rows[0]["completion"]
        assert counts["email"] == 1
        assert counts["phone"] == 1


class TestTokenizer:
    def test_estimate_token_count(self):
        tokens = estimate_token_count("What is the penalty for cyber crime?")
        assert tokens > 0

    def test_analyze_sequence_lengths(self):
        rows = [{"prompt": "Q " * 50, "completion": "A " * 100} for _ in range(10)]
        stats = analyze_sequence_lengths(rows, max_seq_length=50)
        assert stats.total_samples == 10
        assert stats.exceeds_max_len_count > 0

    def test_truncate_row(self):
        long_row = {"prompt": "P " * 1000, "completion": "C " * 1000}
        truncated = truncate_row(long_row, max_seq_length=50)
        assert "truncated" in truncated["prompt"]
        assert "truncated" in truncated["completion"]


class TestDetector:
    def test_classify_legal_dataset(self):
        rows = [
            {"prompt": "What is Section 420 IPC?", "completion": "Section 420 deals with cheating and dishonestly inducing delivery of property."}
        ]
        res = classify_dataset(rows)
        assert res.domain_type == DatasetDomainType.LEGAL_POLICY
        assert res.recommended_system_prompt_type == "legal"

    def test_classify_financial_dataset(self):
        rows = [
            {"prompt": "Audit bank transaction account 1002", "completion": "Suspicious hawala transfer of 50 lakh detected."}
        ]
        res = classify_dataset(rows)
        assert res.domain_type == DatasetDomainType.FINANCIAL_FRAUD
        assert res.recommended_system_prompt_type == "finance"
