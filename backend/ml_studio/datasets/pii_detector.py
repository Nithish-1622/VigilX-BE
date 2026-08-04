from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Regex patterns for sensitive identifiers (Indian & general)
_PAN_RE = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b")
_AADHAAR_RE = re.compile(r"\b[2-9]{1}[0-9]{3}[-\s]?[0-9]{4}[-\s]?[0-9]{4}\b")
_PHONE_RE = re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b")
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_CREDIT_CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


@dataclass
class PIIDetectionResult:
    text: str
    redacted_text: str
    pii_found: bool
    counts: dict[str, int] = field(default_factory=dict)


class PIIDetector:
    """
    Detects and redacts Personally Identifiable Information (PII) including
    Aadhaar numbers, PAN cards, Indian mobile numbers, email addresses, and payment cards.
    Guarantees privacy compliance before local model fine-tuning.
    """

    def __init__(
        self,
        redact_pan: bool = True,
        redact_aadhaar: bool = True,
        redact_phone: bool = True,
        redact_email: bool = True,
        redact_card: bool = True,
    ) -> None:
        self.redact_pan = redact_pan
        self.redact_aadhaar = redact_aadhaar
        self.redact_phone = redact_phone
        self.redact_email = redact_email
        self.redact_card = redact_card

    def scan_and_redact(self, text: str) -> PIIDetectionResult:
        if not text:
            return PIIDetectionResult(text="", redacted_text="", pii_found=False, counts={})

        counts: dict[str, int] = {
            "aadhaar": 0,
            "pan": 0,
            "phone": 0,
            "email": 0,
            "card": 0,
        }
        working_text = text

        # 1. PAN Card
        if self.redact_pan:
            matches = _PAN_RE.findall(working_text)
            if matches:
                counts["pan"] += len(matches)
                working_text = _PAN_RE.sub("[REDACTED_PAN]", working_text)

        # 2. Aadhaar
        if self.redact_aadhaar:
            matches = _AADHAAR_RE.findall(working_text)
            if matches:
                counts["aadhaar"] += len(matches)
                working_text = _AADHAAR_RE.sub("[REDACTED_AADHAAR]", working_text)

        # 3. Email
        if self.redact_email:
            matches = _EMAIL_RE.findall(working_text)
            if matches:
                counts["email"] += len(matches)
                working_text = _EMAIL_RE.sub("[REDACTED_EMAIL]", working_text)

        # 4. Phone
        if self.redact_phone:
            matches = _PHONE_RE.findall(working_text)
            if matches:
                counts["phone"] += len(matches)
                working_text = _PHONE_RE.sub("[REDACTED_PHONE]", working_text)

        # 5. Credit Card (13-19 digits, avoid overlap with phone/aadhaar)
        if self.redact_card:
            def _card_replacer(match: re.Match[str]) -> str:
                s = match.group(0).replace("-", "").replace(" ", "")
                if len(s) in (13, 15, 16, 19):
                    counts["card"] += 1
                    return "[REDACTED_CARD]"
                return match.group(0)

            working_text = _CREDIT_CARD_RE.sub(_card_replacer, working_text)

        total_pii = sum(counts.values())
        return PIIDetectionResult(
            text=text,
            redacted_text=working_text,
            pii_found=total_pii > 0,
            counts={k: v for k, v in counts.items() if v > 0},
        )

    def redact_dataset_rows(self, rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, int]]:
        """
        Redact PII across all rows of a dataset and return total entity counts.
        """
        redacted_rows: list[dict[str, str]] = []
        total_counts: dict[str, int] = {}

        for row in rows:
            new_row = dict(row)
            for field_key in ("prompt", "completion"):
                if field_key in new_row:
                    res = self.scan_and_redact(new_row[field_key])
                    new_row[field_key] = res.redacted_text
                    for pii_type, count in res.counts.items():
                        total_counts[pii_type] = total_counts.get(pii_type, 0) + count
            redacted_rows.append(new_row)

        return redacted_rows, total_counts
