import csv
from collections import Counter
from pathlib import Path


DATA_PATH = Path("data/raw/twcs/twcs.csv")


def find_support_accounts():
    print("=" * 70)
    print("SUPPORT ACCOUNT ANALYSIS")
    print("=" * 70)

    outbound_counts = Counter()

    print("\nReading dataset...")

    with open(DATA_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["inbound"] == "False":
                outbound_counts[row["author_id"]] += 1

    print("\nTop support accounts:")
    print("-" * 70)

    print(f"{'Support Account':<30}{'Outbound Tweets':>20}")
    print("-" * 70)

    for account, count in outbound_counts.most_common(50):
        print(f"{account:<30}{count:>20,}")


if __name__ == "__main__":
    find_support_accounts()