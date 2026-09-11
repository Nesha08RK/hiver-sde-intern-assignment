"""Calculate agreement after the reviewer fills the annotation template."""

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sklearn.metrics import cohen_kappa_score  # noqa: E402
from src.agent import SupportAgent  # noqa: E402


EXPECTED_EXAMPLES = 150


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def evaluate_rows(rows: list[dict[str, str]], agent: SupportAgent) -> dict[str, float | int]:
    predictions = [agent.predict(row["customer_message"], row.get("context", "")) for row in rows]
    model_intents = [prediction["intent"] for prediction in predictions]
    reviewer_intents = [row["reviewer_intent"] for row in rows]
    model_escalations = [prediction["decision"] for prediction in predictions]
    reviewer_escalations = [row["reviewer_expected_escalation"] for row in rows]

    return {
        "reviewed_examples": len(rows),
        "intent_cohen_kappa": cohen_kappa_score(reviewer_intents, model_intents),
        "intent_percentage_agreement": sum(
            reviewer == model for reviewer, model in zip(reviewer_intents, model_intents)
        )
        / len(rows),
        "escalation_cohen_kappa": cohen_kappa_score(reviewer_escalations, model_escalations),
        "escalation_percentage_agreement": sum(
            reviewer == model for reviewer, model in zip(reviewer_escalations, model_escalations)
        )
        / len(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate human annotation agreement.")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=ROOT / "evaluation" / "golden_set_150.csv",
        help="annotated CSV file (default: evaluation/golden_set_150.csv)",
    )
    path = parser.parse_args().input
    if not path.is_absolute():
        path = ROOT / path
    rows = read_rows(path)
    if len(rows) != EXPECTED_EXAMPLES:
        raise SystemExit(f"expected {EXPECTED_EXAMPLES} golden examples, found {len(rows)}")
    missing = [
        row["example_id"]
        for row in rows
        if not row["reviewer_intent"].strip() or not row["reviewer_expected_escalation"].strip()
    ]
    if missing:
        print("pending: reviewer intent and escalation labels are required for all 150 examples")
        return
    if not rows:
        print("pending: no reviewer labels are present; no agreement score generated")
        return
    retrieval_path = ROOT / "evaluation" / "retrieval_set.csv"
    training_path = ROOT / "evaluation" / "training_set.csv"
    human_training_path = ROOT / "evaluation" / "human_training_set.csv"
    if not retrieval_path.exists() or not training_path.exists():
        raise SystemExit("Run python scripts/prepare_data.py and python scripts/train_baselines.py first")
    metrics = evaluate_rows(
        rows,
        SupportAgent.from_project_files(
            retrieval_path,
            training_path,
            human_training_path if SupportAgent.human_training_ready(human_training_path) else None,
        ),
    )
    print("human_vs_model_agreement")
    print(f"reviewed_examples={metrics['reviewed_examples']}")
    print(f"intent_cohen_kappa={metrics['intent_cohen_kappa']:.4f}")
    print(f"intent_percentage_agreement={metrics['intent_percentage_agreement']:.4f}")
    print(f"escalation_cohen_kappa={metrics['escalation_cohen_kappa']:.4f}")
    print(f"escalation_percentage_agreement={metrics['escalation_percentage_agreement']:.4f}")


if __name__ == "__main__":
    main()