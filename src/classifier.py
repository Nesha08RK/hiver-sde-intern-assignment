"""Intent classifier implementations used by the baselines and agent."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .taxonomy import classify_weak


@dataclass
class Prediction:
    intent: str
    confidence: float


class RuleClassifier:
    name = "keyword_rules"

    def fit(self, texts: list[str], labels: list[str] | None = None) -> "RuleClassifier":
        return self

    def predict_one(self, text: str) -> Prediction:
        intent, confidence = classify_weak(text)
        return Prediction(intent, confidence)

    def predict(self, texts: list[str]) -> list[Prediction]:
        return [self.predict_one(text) for text in texts]


class TfidfLogisticClassifier:
    name = "tfidf_logistic_regression"

    def __init__(self) -> None:
        self.vectorizer = None
        self.model = None

    def fit(self, texts: list[str], labels: list[str]) -> "TfidfLogisticClassifier":
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            max_features=30000,
            sublinear_tf=True,
        )
        features = self.vectorizer.fit_transform(texts)
        self.model = LogisticRegression(max_iter=500, class_weight="balanced", random_state=42)
        self.model.fit(features, labels)
        return self

    def predict_one(self, text: str) -> Prediction:
        predictions = self.predict([text])
        return predictions[0]

    def predict(self, texts: list[str]) -> list[Prediction]:
        if self.vectorizer is None or self.model is None:
            raise RuntimeError("Classifier must be fitted before prediction")
        features = self.vectorizer.transform(texts)
        probabilities = self.model.predict_proba(features)
        labels = self.model.classes_
        return [
            Prediction(str(labels[index]), float(row[index]))
            for row in probabilities
            for index in [row.argmax()]
        ]


class HybridClassifier:
    """Use TF-IDF by default, with a narrow override for obvious delivery queries."""

    name = "hybrid_tfidf_with_delivery_override"

    def __init__(self, model: TfidfLogisticClassifier, rules: RuleClassifier | None = None) -> None:
        self.model = model
        self.rules = rules or RuleClassifier()

    @staticmethod
    def _message_only(text: str) -> str:
        return text.split("\n\nCONVERSATION CONTEXT:", 1)[0]

    @classmethod
    def _is_obvious_delivery(cls, text: str, prediction: Prediction) -> bool:
        if prediction.intent != "Delivery and order fulfillment" or prediction.confidence < 0.60:
            return False
        message = cls._message_only(text).lower()
        return bool(re.search(
            r"\b(where\s+is|tracking?\s+update|track\s+my|hasn't\s+arrived|has\s+not\s+arrived|"
            r"not\s+arrived|package|parcel|order\s+status)\b",
            message,
        ))

    def predict_one(self, text: str) -> Prediction:
        model_prediction = self.model.predict_one(text)
        rule_prediction = self.rules.predict_one(self._message_only(text))
        if self._is_obvious_delivery(text, rule_prediction):
            return rule_prediction
        return model_prediction

    def predict(self, texts: list[str]) -> list[Prediction]:
        return [self.predict_one(text) for text in texts]