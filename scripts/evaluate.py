"""Evaluate both intent baselines and the proposed agent classifier."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from src.classifier import RuleClassifier, TfidfLogisticClassifier  # noqa: E402
from src.taxonomy import INTENTS  # noqa: E402


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def evaluate_model(name: str, model, texts: list[str], labels: list[str], rows: list[dict[str, str]]) -> dict:
    predictions = model.predict(texts)
    predicted_labels = [prediction.intent for prediction in predictions]
    report = classification_report(labels, predicted_labels, labels=INTENTS, output_dict=True, zero_division=0)
    failures = []
    for row, prediction in zip(rows, predictions):
        if prediction.intent != row["intent"] and len(failures) < 5:
            failures.append({
                "example_id": row["example_id"],
                "customer_message": row["customer_message"],
                "expected": row["intent"],
                "predicted": prediction.intent,
                "confidence": prediction.confidence,
            })
    matrix = confusion_matrix(labels, predicted_labels, labels=INTENTS).tolist()
    return {
        "model": name,
        "label_source": "weak_rule_generated; needs_manual_review",
        "sample_size": len(labels),
        "accuracy": accuracy_score(labels, predicted_labels),
        "macro_f1": f1_score(labels, predicted_labels, labels=INTENTS, average="macro", zero_division=0),
        "macro_precision": precision_score(labels, predicted_labels, labels=INTENTS, average="macro", zero_division=0),
        "macro_recall": recall_score(labels, predicted_labels, labels=INTENTS, average="macro", zero_division=0),
        "per_class": report,
        "labels": INTENTS,
        "confusion_matrix": matrix,
        "failures": failures,
    }


def main() -> None:
    golden_path = ROOT / "evaluation" / "golden_set.csv"
    training_path = ROOT / "evaluation" / "training_set.csv"
    if not golden_path.exists() or not training_path.exists():
        raise SystemExit("Run python scripts/prepare_data.py and python scripts/train_baselines.py first")
    golden = read_rows(golden_path)
    training = read_rows(training_path)
    texts = [row["customer_message"] for row in golden]
    labels = [row["intent"] for row in golden]
    train_texts = [row["customer_message"] for row in training]
    train_labels = [row["intent"] for row in training]

    rule_result = evaluate_model("keyword_rules", RuleClassifier(), texts, labels, golden)
    tfidf = TfidfLogisticClassifier().fit(train_texts, train_labels)
    tfidf_result = evaluate_model("tfidf_logistic_regression", tfidf, texts, labels, golden)
    results = [rule_result, tfidf_result]

    output_dir = ROOT / "evaluation" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    summary_path = output_dir / "summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["model", "sample_size", "accuracy", "macro_f1", "macro_precision", "macro_recall", "label_source"])
        writer.writeheader()
        for result in results:
            writer.writerow({field: result[field] for field in writer.fieldnames})

    failures = []
    for result in results:
        for failure in result["failures"]:
            failures.append({"model": result["model"], **failure})
    (output_dir / "failure_analysis.json").write_text(json.dumps(failures, indent=2), encoding="utf-8")
    print(f"Evaluated {len(golden)} golden examples")
    print("WARNING: metrics use automatically generated weak labels, not human annotations.")
    print("model,accuracy,macro_f1,macro_precision,macro_recall")
    for result in results:
        print(",".join([
            result["model"],
            f"{result['accuracy']:.4f}",
            f"{result['macro_f1']:.4f}",
            f"{result['macro_precision']:.4f}",
            f"{result['macro_recall']:.4f}",
        ]))
    print(f"Results written to {output_dir}")


if __name__ == "__main__":
    main()