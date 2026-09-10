import csv
import random
from pathlib import Path


DATA_PATH = Path("data/raw/twcs/twcs.csv")

BRAND = "AmazonHelp"
SAMPLE_SIZE = 200
RANDOM_SEED = 42


def load_tweets():
    """Load all tweets into a dictionary."""
    tweets = {}

    with open(DATA_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tweets[row["tweet_id"]] = row

    return tweets


def build_children_map(tweets):
    """Map each tweet to its direct replies."""
    children_map = {}

    for tweet in tweets.values():
        parent_id = tweet["in_response_to_tweet_id"]

        if parent_id:
            children_map.setdefault(parent_id, []).append(
                tweet["tweet_id"]
            )

    return children_map


def is_amazonhelp_reply(tweet_id, tweets):
    """Check whether a tweet has a direct AmazonHelp reply."""
    if tweet_id not in tweets:
        return False

    response_ids = tweets[tweet_id]["response_tweet_id"]

    if not response_ids:
        return False

    for response_id in response_ids.split(","):
        response_id = response_id.strip()

        if response_id in tweets:
            if tweets[response_id]["author_id"] == BRAND:
                return True

    return False


def find_customer_roots(tweets):
    """
    Find inbound customer tweets that start an AmazonHelp conversation.

    A root has no parent tweet available in the dataset and receives
    a direct reply from AmazonHelp.
    """
    roots = []

    for tweet in tweets.values():

        if tweet["inbound"] != "True":
            continue

        parent_id = tweet["in_response_to_tweet_id"]

        if parent_id and parent_id in tweets:
            continue

        if is_amazonhelp_reply(tweet["tweet_id"], tweets):
            roots.append(tweet)

    return roots


def get_thread_ids(tweet_id, tweets, children_map, visited=None):
    """Return all tweet IDs belonging to a thread."""
    if visited is None:
        visited = set()

    if tweet_id in visited:
        return visited

    if tweet_id not in tweets:
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


def get_customer_messages(thread_ids, tweets):
    """Extract substantive inbound customer messages from a thread."""
    messages = []

    for tweet_id in thread_ids:
        tweet = tweets[tweet_id]

        if tweet["inbound"] != "True":
            continue

        text = tweet["text"].strip()

        if not text:
            continue

        messages.append(tweet)

    return messages


def sample_customer_messages(roots, tweets, children_map):
    """
    Build a pool of customer messages from unique conversation threads
    and randomly sample from that pool.
    """
    message_pool = []

    for root in roots:
        thread_ids = get_thread_ids(
            root["tweet_id"],
            tweets,
            children_map,
        )

        customer_messages = get_customer_messages(
            thread_ids,
            tweets,
        )

        for message in customer_messages:
            message_pool.append(
                {
                    "tweet_id": message["tweet_id"],
                    "root_id": root["tweet_id"],
                    "text": message["text"],
                    "created_at": message["created_at"],
                    "thread_length": len(thread_ids),
                }
            )

    random.seed(RANDOM_SEED)

    sample_size = min(
        SAMPLE_SIZE,
        len(message_pool),
    )

    return random.sample(
        message_pool,
        sample_size,
    )


def main():
    print("=" * 80)
    print(f"INTENT DISCOVERY — {BRAND}")
    print("=" * 80)

    print("\nLoading dataset...")

    tweets = load_tweets()

    print(f"Loaded {len(tweets):,} tweets.")

    children_map = build_children_map(tweets)

    roots = find_customer_roots(tweets)

    print(f"Found {len(roots):,} unique conversation roots.")

    sampled = sample_customer_messages(
        roots,
        tweets,
        children_map,
    )

    print(
        f"Sampled {len(sampled)} customer messages "
        f"from AmazonHelp conversation threads."
    )

    print(f"Random seed: {RANDOM_SEED}")

    print("\n" + "=" * 80)
    print("SAMPLED CUSTOMER MESSAGES")
    print("=" * 80)

    for index, message in enumerate(sampled, start=1):

        print("\n" + "-" * 80)
        print(f"EXAMPLE {index}")
        print(f"Tweet ID: {message['tweet_id']}")
        print(f"Conversation Root: {message['root_id']}")
        print(f"Thread Length: {message['thread_length']}")
        print(f"Created: {message['created_at']}")
        print(f"Customer: {message['text']}")


if __name__ == "__main__":
    main()