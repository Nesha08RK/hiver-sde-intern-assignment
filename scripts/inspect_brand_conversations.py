import csv
from collections import defaultdict
from pathlib import Path


DATA_PATH = Path("data/raw/twcs/twcs.csv")

BRAND = "AmazonHelp"
NUM_CONVERSATIONS = 10


def inspect_conversations():
    print("=" * 80)
    print(f"REAL CONVERSATIONS — {BRAND}")
    print("=" * 80)

    tweets = {}

    with open(DATA_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tweets[row["tweet_id"]] = row

    # Find tweets directly replied to by our brand
    conversations = []

    for row in tweets.values():

        response_ids = row["response_tweet_id"]

        if not response_ids:
            continue

        ids = response_ids.split(",")

        brand_replies = []

        for response_id in ids:
            response_id = response_id.strip()

            if response_id in tweets:
                response = tweets[response_id]

                if response["author_id"] == BRAND:
                    brand_replies.append(response)

        if (
            row["inbound"] == "True"
            and brand_replies
        ):
            conversations.append(
                (row, brand_replies)
            )

    print(f"\nFound {len(conversations):,} customer interactions.")

    print(
        f"\nShowing first {NUM_CONVERSATIONS} conversations:\n"
    )

    for index, (customer, replies) in enumerate(
        conversations[:NUM_CONVERSATIONS],
        start=1,
    ):

        print("=" * 80)
        print(f"CONVERSATION {index}")
        print("=" * 80)

        print("\nCUSTOMER:")
        print(customer["text"])

        for reply in replies:
            print("\nAMAZONHELP:")
            print(reply["text"])

        print()


if __name__ == "__main__":
    inspect_conversations()