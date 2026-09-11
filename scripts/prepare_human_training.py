"""Create a balanced, non-golden pool for human-reviewed intent training."""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.taxonomy import INTENTS  # noqa: E402


OUTPUT = ROOT / "evaluation" / "human_training_set.csv"
GOLDEN = ROOT / "evaluation" / "golden_set.csv"
WEAK_TRAINING = ROOT / "evaluation" / "training_set.csv"
SEED = 45


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def main() -> None:
    if not GOLDEN.exists() or not WEAK_TRAINING.exists():
        raise SystemExit("Run python scripts/prepare_data.py and python scripts/train_baselines.py first")
    golden = read_rows(GOLDEN)
    excluded = {row["conversation_root_id"] for row in golden}
    weak_rows = read_rows(WEAK_TRAINING)
    if excluded & {row["conversation_root_id"] for row in weak_rows}:
        raise SystemExit("training_set.csv contains golden conversation roots")

    grouped = {intent: [] for intent in INTENTS}
    for row in weak_rows:
        grouped[row["intent"]].append(row)
    rng = random.Random(SEED)
    candidates = []
    for intent in INTENTS:
        if len(grouped[intent]) < 10:
            raise SystemExit(f"training_set.csv has fewer than 10 candidates for {intent!r}")
        for row in rng.sample(grouped[intent], 10):
            candidates.append({
                "example_id": f"human-train-{len(candidates) + 1:04d}",
                "conversation_root_id": row["conversation_root_id"],
                "tweet_id": row["tweet_id"],
                "customer_message": row["customer_message"],
                "context": row["context"],
                "weak_intent": intent,
                "reviewer_intent": "",
                "reviewer_notes": "",
            })

    existing = {}
    if OUTPUT.exists():
        existing = {
            row["conversation_root_id"]: row
            for row in read_rows(OUTPUT)
        }
    for row in candidates:
        previous = existing.get(row["conversation_root_id"], {})
        row["reviewer_intent"] = previous.get("reviewer_intent", "")
        row["reviewer_notes"] = previous.get("reviewer_notes", "")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(candidates[0]))
        writer.writeheader()
        writer.writerows(candidates)
    print(f"Wrote {len(candidates)} human-training candidates to {OUTPUT}")
    print("Reviewer intent remains blank until manual annotation.")
    print("Golden conversation roots were excluded.")


if __name__ == "__main__":
    main()