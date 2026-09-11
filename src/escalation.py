"""Explicit escalation policy for the support agent."""

from .taxonomy import should_escalate_weak


def decide(text: str, intent: str, confidence: float) -> tuple[str, str]:
    return should_escalate_weak(text, intent, confidence)