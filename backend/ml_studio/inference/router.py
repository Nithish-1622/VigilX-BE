from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class InferenceDomain(str, Enum):
    LEGAL = "legal"
    FINANCE = "finance"
    SECURITY = "security"
    FAQ = "faq"
    GENERAL = "general"


@dataclass
class RouterDecision:
    domain: InferenceDomain
    confidence: float
    matched_keywords: list[str]
    target_model_hint: str   # e.g. "Legal-v3", "Finance-v2"


# Domain keyword maps
_LEGAL_PATTERNS = re.compile(
    r"\b(section|ipc|fir|bail|court|accused|cognizable|crpc|warrant|offence|chargesheet|"
    r"penalty|jurisdiction|verdict|magistrate|convict|arrest|complaint|police|summons)\b",
    re.IGNORECASE,
)

_FINANCE_PATTERNS = re.compile(
    r"\b(account|transaction|fraud|hawala|bank|transfer|money\s*launder|suspicious|upi|"
    r"lakh|crore|swift|neft|credit\s*card|debit\s*card|suspicious\s*activity|invoice)\b",
    re.IGNORECASE,
)

_SECURITY_PATTERNS = re.compile(
    r"\b(malware|cyber|intrusion|exploit|vulnerability|phishing|ransomware|ddos|sql\s*inject|"
    r"attack|breach|unauthorized\s*access|hacking|threat\s*actor|incident\s*response)\b",
    re.IGNORECASE,
)

_FAQ_PATTERNS = re.compile(
    r"\b(what\s*is|how\s*to|explain|define|describe|who\s*is|where\s*is|when\s*did|why\s*does)\b",
    re.IGNORECASE,
)


class DomainRouter:
    """
    Runtime multi-domain model router.
    Classifies incoming query intent and routes to the most appropriate specialist model.
    """

    def __init__(
        self,
        legal_model: str = "Legal-v1",
        finance_model: str = "Finance-v1",
        security_model: str = "Security-v1",
        general_model: str = "General-v1",
    ) -> None:
        self.domain_models = {
            InferenceDomain.LEGAL: legal_model,
            InferenceDomain.FINANCE: finance_model,
            InferenceDomain.SECURITY: security_model,
            InferenceDomain.FAQ: general_model,
            InferenceDomain.GENERAL: general_model,
        }

    def route(self, query: str) -> RouterDecision:
        """
        Analyze query and return routing decision with domain classification.
        """
        legal_matches = _LEGAL_PATTERNS.findall(query)
        finance_matches = _FINANCE_PATTERNS.findall(query)
        security_matches = _SECURITY_PATTERNS.findall(query)
        faq_matches = _FAQ_PATTERNS.findall(query)

        scores = {
            InferenceDomain.LEGAL: len(legal_matches),
            InferenceDomain.FINANCE: len(finance_matches),
            InferenceDomain.SECURITY: len(security_matches),
            InferenceDomain.FAQ: len(faq_matches) * 0.5,  # Lower weight for generic FAQ
        }

        best_domain = max(scores, key=lambda d: scores[d])
        best_score = scores[best_domain]

        if best_score == 0:
            best_domain = InferenceDomain.GENERAL
            confidence = 0.5
            matched = []
        else:
            total = sum(scores.values())
            confidence = round(best_score / float(max(1.0, total)), 3)
            if best_domain == InferenceDomain.LEGAL:
                matched = [m.lower() for m in legal_matches[:5]]
            elif best_domain == InferenceDomain.FINANCE:
                matched = [m.lower() for m in finance_matches[:5]]
            elif best_domain == InferenceDomain.SECURITY:
                matched = [m.lower() for m in security_matches[:5]]
            else:
                matched = [m.lower() for m in faq_matches[:5]]

        return RouterDecision(
            domain=best_domain,
            confidence=confidence,
            matched_keywords=matched,
            target_model_hint=self.domain_models[best_domain],
        )
