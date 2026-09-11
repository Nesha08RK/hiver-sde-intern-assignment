"""Prepare the non-evaluation weak-label corpus for the TF-IDF baseline."""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data import (  # noqa: E402
    DATA_PATH,
    build_retrieval_rows,
    build_training_rows,
    load_tweets,
)


def main() -> None:
    golden_path = ROOT / "evaluation" / "golden_set.csv"
    if not golden_path.exists():
        raise SystemExit("Run python scripts/prepare_data.py first")
    with golden_path.open(encoding="utf-8", newline="") as file:
        excluded = {row["conversation_root_id"] for row in csv.DictReader(file)}
    tweets = load_tweets(DATA_PATH)
    rows = build_training_rows(tweets, excluded)
    output = ROOT / "evaluation" / "training_set.csv"
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} weakly labelled training examples to {output}")
    print("Evaluation roots were excluded from this file.")

    retrieval_rows = build_retrieval_rows(tweets, excluded)
    retrieval_output = ROOT / "evaluation" / "retrieval_set.csv"
    with retrieval_output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(retrieval_rows[0]))
        writer.writeheader()
        writer.writerows(retrieval_rows)
    print(f"Wrote {len(retrieval_rows)} historical evidence pairs to {retrieval_output}")


if __name__ == "__main__":
    main()