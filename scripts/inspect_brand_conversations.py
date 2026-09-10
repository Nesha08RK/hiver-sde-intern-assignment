import csv
from pathlib import Path


DATA_PATH = Path("data/raw/twcs/twcs.csv")

BRAND = "AmazonHelp"
NUM_CONVERSATIONS = 10


def load_tweets():
    """Load all tweets into a dictionary keyed by tweet ID."""
    tweets = {}

    with open(DATA_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tweets[row["tweet_id"]] = row

    return tweets


def build_children_map(tweets):
    """Map each tweet to the tweets that directly reply to it."""
    children_map = {}

    for tweet in tweets.values():
        parent_id = tweet["in_response_to_tweet_id"]

        if parent_id:
            children_map.setdefault(parent_id, []).append(
                tweet["tweet_id"]
            )

    return children_map


def find_conversation_roots(tweets):
    """
    Find customer tweets that start a conversation with AmazonHelp.

    A root is an inbound customer tweet that:
    - has no parent tweet in the dataset, OR
    - has a parent tweet that is not part of the same conversation.
    """

    roots = []

    for tweet in tweets.values():

        if tweet["inbound"] != "True":
            continue

        parent_id = tweet["in_response_to_tweet_id"]

        # If this tweet has a parent, it is not a root.
        if parent_id and parent_id in tweets:
            continue

        # Check whether AmazonHelp directly replies to it.
        response_ids = tweet["response_tweet_id"]

        if not response_ids:
            continue

        for response_id in response_ids.split(","):
            response_id = response_id.strip()

            if response_id in tweets:
                response = tweets[response_id]

                if response["author_id"] == BRAND:
                    roots.append(tweet)
                    break

    return roots


def print_thread(tweet_id, tweets, children_map, visited, level=0):
    """Recursively print a complete conversation thread."""

    if tweet_id in visited:
        return

    if tweet_id not in tweets:
        return

    visited.add(tweet_id)

    tweet = tweets[tweet_id]

    if tweet["author_id"] == BRAND:
        speaker = "AMAZONHELP"
    elif tweet["inbound"] == "True":
        speaker = "CUSTOMER"
    else:
        speaker = "OTHER"

    indent = "  " * level

    print(f"\n{indent}{speaker}:")
    print(f"{indent}{tweet['text']}")

    for child_id in children_map.get(tweet_id, []):
        print_thread(
            child_id,
            tweets,
            children_map,
            visited,
            level + 1,
        )


def get_thread_ids(tweet_id, tweets, children_map, visited=None):
    """Return all tweet IDs belonging to a conversation thread."""

    if visited is None:
        visited = set()

    if tweet_id in visited or tweet_id not in tweets:
        return visited

    visited.add(tweet_id)

    for child_id in children_map.get(tweet_id, []):
        get_thread_ids(
            child_id,
            tweets,
            children_map,
            visited,
        )

    return visited


def inspect_conversations():
    print("=" * 80)
    print(f"UNIQUE CONVERSATION THREADS — {BRAND}")
    print("=" * 80)

    print("\nLoading dataset...")

    tweets = load_tweets()

    print(f"Loaded {len(tweets):,} tweets.")

    children_map = build_children_map(tweets)

    roots = find_conversation_roots(tweets)

    print(f"\nFound {len(roots):,} conversation roots.")

    print(
        f"\nShowing first {NUM_CONVERSATIONS} unique conversation threads:\n"
    )

    for index, root in enumerate(
        roots[:NUM_CONVERSATIONS],
        start=1,
    ):

        visited = set()

        thread_ids = get_thread_ids(
            root["tweet_id"],
            tweets,
            children_map,
        )

        print("=" * 80)
        print(f"CONVERSATION {index}")
        print(f"THREAD LENGTH: {len(thread_ids)}")
        print("=" * 80)

        print_thread(
            root["tweet_id"],
            tweets,
            children_map,
            visited,
        )

        print()


if __name__ == "__main__":
    inspect_conversations()