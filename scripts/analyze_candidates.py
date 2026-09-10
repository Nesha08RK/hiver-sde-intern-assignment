import csv
from collections import Counter, defaultdict
from pathlib import Path


DATA_PATH = Path("data/raw/twcs/twcs.csv")

CANDIDATES = {
    "AmazonHelp",
    "AppleSupport",
    "Uber_Support",
    "SpotifyCares",
    "TMobileHelp",
}


def analyze_candidates():
    print("=" * 80)
    print("CANDIDATE BRAND ANALYSIS")
    print("=" * 80)

    # tweet_id -> tweet information
    tweets = {}

    # tweet_id -> list of tweets that directly respond to it
    responses = defaultdict(list)

    print("\nReading dataset...")

    with open(DATA_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tweet_id = row["tweet_id"]

            tweets[tweet_id] = {
                "author": row["author_id"],
                "inbound": row["inbound"],
                "response_to": row["in_response_to_tweet_id"],
            }

            response_to = row["in_response_to_tweet_id"]

            if response_to:
                responses[response_to].append(tweet_id)

    print(f"Tweets loaded: {len(tweets):,}")

    results = {}

    for brand in CANDIDATES:

        customer_messages = 0
        conversations = 0
        multi_turn = 0

        conversation_lengths = []

        # Find customer tweets directly answered by this brand
        for tweet_id, reply_ids in responses.items():

            if tweet_id not in tweets:
                continue

            original = tweets[tweet_id]

            if (
                original["inbound"] == "True"
                and brand in {
                    tweets[r]["author"]
                    for r in reply_ids
                    if r in tweets
                }
            ):
                customer_messages += 1

                # Build a small local conversation
                conversation = [tweet_id]

                for reply_id in reply_ids:
                    if reply_id in tweets:
                        conversation.append(reply_id)

                conversations += 1

                if len(conversation) >= 3:
                    multi_turn += 1

                conversation_lengths.append(len(conversation))

        results[brand] = {
            "customer_messages": customer_messages,
            "conversations": conversations,
            "multi_turn": multi_turn,
            "avg_length": (
                sum(conversation_lengths) / len(conversation_lengths)
                if conversation_lengths
                else 0
            ),
        }

    print("\nResults:")
    print("-" * 80)

    print(
        f"{'Brand':<20}"
        f"{'Customer Msgs':>18}"
        f"{'Conversations':>18}"
        f"{'Multi-turn':>15}"
        f"{'Avg Length':>12}"
    )

    print("-" * 80)

    for brand, stats in results.items():
        print(
            f"{brand:<20}"
            f"{stats['customer_messages']:>18,}"
            f"{stats['conversations']:>18,}"
            f"{stats['multi_turn']:>15,}"
            f"{stats['avg_length']:>12.2f}"
        )


if __name__ == "__main__":
    analyze_candidates()