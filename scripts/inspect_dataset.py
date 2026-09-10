import csv
from pathlib import Path

DATA_PATH = Path("data/raw/twcs/twcs.csv")


def inspect_dataset():
    print("=" * 60)
    print("DATASET INSPECTION")
    print("=" * 60)

    print(f"\nFile: {DATA_PATH}")
    print(f"Exists: {DATA_PATH.exists()}")

    if not DATA_PATH.exists():
        print("ERROR: Dataset file not found.")
        return

    print("\nReading header...")

    with open(DATA_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)

        header = next(reader)

        print("\nColumns:")
        for i, column in enumerate(header, start=1):
            print(f"{i}. {column}")

        print("\nFirst 5 rows:\n")

        for i, row in enumerate(reader):
            print(f"Row {i + 1}:")
            for column, value in zip(header, row):
                print(f"  {column}: {value}")
            print()

            if i == 4:
                break


if __name__ == "__main__":
    inspect_dataset()