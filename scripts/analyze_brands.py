import csv
from collections import Counter
from pathlib import Path


DATA_PATH = Path("data/raw/twcs/twcs.csv")


def analyze_brands():
    print("=" * 70)
    print("BRAND ANALYSIS")
    print("=" * 70)

    if not DATA_PATH.exists():
        print(f"Dataset not found: {DATA_PATH}")
        return

    brand_stats = Counter()
    inbound_stats = Counter()
    outbound_stats = Counter()

    print("\nReading dataset...")

    with open(DATA_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            author = row["author_id"]
            inbound = row["inbound"]

            if inbound == "True":
                inbound_stats[author] += 1
            else:
                outbound_stats[author] += 1

    print("\nAnalysis complete.")

    # Combine all authors
    authors = set(inbound_stats) | set(outbound_stats)

    for author in authors:
        brand_stats[author] = (
            inbound_stats[author] + outbound_stats[author]
        )

    print("\nTop authors by total tweets:")
    print("-" * 70)

    print(
        f"{'Author':<30}"
        f"{'Total':>12}"
        f"{'Inbound':>12}"
        f"{'Outbound':>12}"
    )

    print("-" * 70)

    for author, total in brand_stats.most_common(30):
        print(
            f"{author:<30}"
            f"{total:>12}"
            f"{inbound_stats[author]:>12}"
            f"{outbound_stats[author]:>12}"
        )


if __name__ == "__main__":
    analyze_brands()