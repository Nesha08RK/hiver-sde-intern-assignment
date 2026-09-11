"""Create the reproducible golden-set template and conversation split."""

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data import DATA_PATH, SEED, build_examples, load_tweets  # noqa: E402


OUTPUT = ROOT / "evaluation"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    tweets = load_tweets(DATA_PATH)
    examples = build_examples(tweets)
    write_csv(OUTPUT / "golden_set.csv", examples)

    annotation_fields = list(examples[0]) + ["reviewer_intent", "reviewer_expected_escalation", "reviewer_notes"]
    template_rows = [{field: row.get(field, "") if field in row and field not in {"intent", "expected_escalation"} else "" for field in annotation_fields} for row in examples]
    write_csv(OUTPUT / "golden_set_annotation_template.csv", template_rows)

    split_rows = []
    for row in examples:
        split_rows.append({
            "conversation_root_id": row["conversation_root_id"],
            "split": "evaluation",
            "retrieval_exclusion": row["conversation_root_id"],
            "reason": "Golden conversations are excluded from retrieval evidence",
        })
    write_csv(OUTPUT / "conversation_split.csv", split_rows)

    print(f"Loaded {len(tweets):,} tweets")
    print(f"Wrote {len(examples)} weakly labelled examples")
    print(f"Seed: {SEED}")
    print(f"Source: {DATA_PATH}")
    print("Intent counts:")
    for intent, count in Counter(row["intent"] for row in examples).most_common():
        print(f"  {intent}: {count}")
    print("Labels are weak_rule_generated and require manual review.")


if __name__ == "__main__":
    main()