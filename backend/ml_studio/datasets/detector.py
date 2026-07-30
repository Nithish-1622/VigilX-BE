from __future__ import annotations

import re
from enum import Enum
from dataclasses import dataclass


class DatasetDomainType(str, Enum):
    FAQ = "faq"
    CHAT = "chat"
    LEGAL_POLICY = "legal_policy"
    FINANCIAL_FRAUD = "financial_fraud"
    GENERAL = "general"


@dataclass
class DatasetClassificationResult:
    domain_type: DatasetDomainType
    confidence: float
    recommended_system_prompt_type: str
    detected_keywords: list[str]


_LEGAL_KEYWORDS = {
    "section", "fir", "ipc", "crpc", "court", "offence", "bail", "police",
    "cognizable", "warrant", "accused", "jurisdiction", "penalty", "act"
}

_FINANCIAL_KEYWORDS = {
    "account", "transaction", "amount", "hawala", "bank", "fraud", "transfer",
    "suspicious", "lakh", "crore", "swift", "laundering", "upi", "card"
}

_CHAT_KEYWORDS = {
    "user:", "assistant:", "human:", "agent:", "turn", "dialogue", "chat",
    "speaker", "transcript", "call"
}


def classify_dataset(rows: list[dict[str, str]]) -> DatasetClassificationResult:
    """
    Auto-detect domain classification of a dataset by sampling its contents.
    Returns domain type, confidence score, and recommended prompt template.
    """
    if not rows:
        return DatasetClassificationResult(
            domain_type=DatasetDomainType.GENERAL,
            confidence=0.5,
            recommended_system_prompt_type="base",
            detected_keywords=[],
        )

    legal_hits = 0
    financial_hits = 0
    chat_hits = 0
    faq_hits = 0

    found_keywords: set[str] = set()

    for row in rows[:50]:  # Sample first 50 rows
        prompt = str(row.get("prompt", "")).lower()
        completion = str(row.get("completion", "")).lower()
        combined = f"{prompt} {completion}"

        # Legal check
        for kw in _LEGAL_KEYWORDS:
            if kw in combined:
                legal_hits += 1
                found_keywords.add(kw)

        # Financial check
        for kw in _FINANCIAL_KEYWORDS:
            if kw in combined:
                financial_hits += 1
                found_keywords.add(kw)

        # Chat check
        if any(c_kw in combined for c_kw in _CHAT_KEYWORDS) or "\nuser" in combined or "\nhuman" in combined:
            chat_hits += 1

        # FAQ check (short, concise prompt ending with ?)
        if "?" in prompt and len(prompt.split()) < 30 and len(completion.split()) < 100:
            faq_hits += 1

    total_sampled = min(len(rows), 50)

    scores = {
        DatasetDomainType.LEGAL_POLICY: legal_hits / max(1.0, total_sampled * 2.0),
        DatasetDomainType.FINANCIAL_FRAUD: financial_hits / max(1.0, total_sampled * 2.0),
        DatasetDomainType.CHAT: chat_hits / float(total_sampled),
        DatasetDomainType.FAQ: faq_hits / float(total_sampled),
    }

    best_type = max(scores, key=lambda k: scores[k])
    best_score = min(1.0, scores[best_type])

    if best_score < 0.15:
        best_type = DatasetDomainType.GENERAL
        best_score = 0.5
        rec_prompt = "base"
    elif best_type == DatasetDomainType.LEGAL_POLICY:
        rec_prompt = "legal"
    elif best_type == DatasetDomainType.FINANCIAL_FRAUD:
        rec_prompt = "finance"
    elif best_type == DatasetDomainType.CHAT:
        rec_prompt = "chat"
    elif best_type == DatasetDomainType.FAQ:
        rec_prompt = "faq"
    else:
        rec_prompt = "base"

    return DatasetClassificationResult(
        domain_type=best_type,
        confidence=round(best_score, 2),
        recommended_system_prompt_type=rec_prompt,
        detected_keywords=sorted(list(found_keywords))[:10],
    )
