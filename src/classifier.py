"""Intent classifier implementations used by the baselines and agent."""

from __future__ import annotations

from dataclasses import dataclass

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