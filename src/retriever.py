"""Lightweight TF-IDF retrieval over non-evaluation historical conversations."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Evidence:
    customer_message: str
    amazonhelp_response: str
    conversation_root_id: str
    score: float


class TfidfRetriever:
    def __init__(self, rows: list[dict[str, str]]) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.rows = rows
        self.vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=30000)
        self.matrix = self.vectorizer.fit_transform([row["customer_message"] for row in rows])

    @classmethod
    def from_csv(cls, path: Path) -> "TfidfRetriever":
        with path.open(encoding="utf-8", newline="") as file:
            return cls(list(csv.DictReader(file)))

    def retrieve(self, text: str, top_k: int = 3) -> list[Evidence]:
        from sklearn.metrics.pairwise import cosine_similarity

        query = self.vectorizer.transform([text])
        scores = cosine_similarity(query, self.matrix).ravel()
        indexes = scores.argsort()[::-1][:top_k]
        return [
            Evidence(
                self.rows[index]["customer_message"],
                self.rows[index]["amazonhelp_response"],
                self.rows[index]["conversation_root_id"],
                float(scores[index]),
            )
            for index in indexes
        ]