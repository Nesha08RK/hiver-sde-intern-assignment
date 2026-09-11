"""Modular AmazonHelp support agent."""

from __future__ import annotations

import csv
from pathlib import Path

from .classifier import Prediction, RuleClassifier, TfidfLogisticClassifier
from .escalation import decide
from .generator import generate_reply
from .retriever import Evidence, TfidfRetriever


class SupportAgent:
    def __init__(self, retriever: TfidfRetriever, classifier=None) -> None:
        self.retriever = retriever
        self.classifier = classifier or RuleClassifier()

    @classmethod
    def from_project_files(
        cls,
        retrieval_path: Path,
        training_path: Path,
        human_training_path: Path | None = None,
    ) -> "SupportAgent":
        with training_path.open(encoding="utf-8", newline="") as file:
            training_rows = list(csv.DictReader(file))
        labels = [row["intent"] for row in training_rows]
        if human_training_path is not None:
            with human_training_path.open(encoding="utf-8", newline="") as file:
                human_rows = list(csv.DictReader(file))
            if not human_rows or not cls.human_training_ready(human_training_path):
                raise ValueError("Human training requires reviewer_intent for every candidate")
            training_rows = human_rows
            labels = [row["reviewer_intent"] for row in human_rows]
        classifier = TfidfLogisticClassifier().fit(
            [cls.classification_text(row["customer_message"], row.get("context", "")) for row in training_rows],
            labels,
        )
        return cls(TfidfRetriever.from_csv(retrieval_path), classifier)

    @staticmethod
    def classification_text(text: str, context: str = "") -> str:
        if not context.strip():
            return text
        return f"{text}\n\nCONVERSATION CONTEXT:\n{context}"

    @staticmethod
    def human_training_ready(path: Path) -> bool:
        if not path.exists():
            return False
        with path.open(encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))
        return bool(rows) and all(row.get("reviewer_intent", "").strip() for row in rows)

    def predict(self, text: str, context: str = "", top_k: int = 3) -> dict:
        prediction: Prediction = self.classifier.predict_one(self.classification_text(text, context))
        evidence: list[Evidence] = self.retriever.retrieve(text, top_k)
        reply, generation_mode = generate_reply(text, prediction.intent, evidence)
        decision, reason = decide(text, prediction.intent, prediction.confidence)
        return {
            "input": text,
            "intent": prediction.intent,
            "confidence": prediction.confidence,
            "evidence": evidence,
            "draft_reply": reply,
            "decision": decision,
            "reason": reason,
            "generation_mode": generation_mode,
        }