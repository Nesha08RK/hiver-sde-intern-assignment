"""The fixed AmazonHelp taxonomy and transparent weak-label rules."""

from __future__ import annotations

import re


INTENTS = [
    "Delivery and order fulfillment",
    "Customer service escalation and feedback",
    "Product condition, item accuracy, and seller issues",
    "Digital products, devices, and apps",
    "Prime membership and benefits",
    "Returns, refunds, and charges",
    "Pricing, offers, and product availability",
    "Account access and security",
    "Other/Unclear/non-substantive",
]

OTHER_INTENT = INTENTS[-1]

_RULES = {
    "Account access and security": (
        r"\b(login|log in|password|hacked|fraud|scam|phishing|unauthori|"
        r"account|card info|stolen|security)\b"
    ),
    "Digital products, devices, and apps": (
        r"\b(alexa|kindle|prime video|stream|app|tablet|fire|device|"
        r"hd|video|book|page can't|website down|crash|freez|open)\b"
    ),
    "Product condition, item accuracy, and seller issues": (
        r"\b(broken|damage|defect|wrong item|wrong size|used|open(ed)?|"
        r"packag(ing|e)\b.*(empty|torn)|warranty|seller|review system)\b"
    ),
    "Prime membership and benefits": r"\bprime\b|free trial|membership",
    "Returns, refunds, and charges": (
        r"\b(refund|return|charged|charge|payment|money back|cancel.*order)\b"
    ),
    "Pricing, offers, and product availability": (
        r"\b(price|pricing|discount|offer|coupon|cost|available|availability|"
        r"exchange|price match|shipping added)\b"
    ),
    "Delivery and order fulfillment": (
        r"\b(order|deliver|delivery|delivered|package|parcel|ship|shipping|"
        r"dispatch|tracking|track|courier|arriv|post office|address)\b"
    ),
    "Customer service escalation and feedback": (
        r"\b(agent|customer service|support|representative|human|manager|"
        r"complaint|escalat|senior|dm|direct contact|not helpful|worst service)\b"
    ),
}


def classify_weak(text: str) -> tuple[str, float]:
    """Return a reproducible heuristic label and an intentionally modest confidence."""
    normalized = text.lower().strip()
    if not normalized or len(normalized) < 12:
        return OTHER_INTENT, 0.35

    for intent in INTENTS[:-1]:
        if re.search(_RULES[intent], normalized, re.IGNORECASE):
            return intent, 0.62

    if re.search(r"(thanks|thank you|done|okay|ok|yes|no|😂|😊|👍|https?://\S+$)", normalized, re.I):
        return OTHER_INTENT, 0.45

    return OTHER_INTENT, 0.30


def should_escalate_weak(text: str, intent: str, confidence: float) -> tuple[str, str]:
    """Apply a conservative, explainable escalation policy to a message."""
    normalized = text.lower()
    if intent in {"Account access and security", OTHER_INTENT}:
        return "ESCALATE", "Security or insufficient-information risk"
    if re.search(r"\b(lawyer|court|sue|legal|police|consumer forum)\b", normalized):
        return "ESCALATE", "Legal or regulatory threat"
    if re.search(r"\b(card|bank|payment|charged)\b", normalized):
        return "ESCALATE", "Sensitive payment dispute"
    if confidence < 0.50:
        return "ESCALATE", "Low-confidence or unclear message"
    return "AUTO_HANDLE", "Concrete intent with sufficient information"