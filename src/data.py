"""Conversation reconstruction and deterministic dataset preparation."""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path

from .taxonomy import classify_weak, should_escalate_weak

DATA_PATH = Path("data/raw/twcs/twcs.csv")
BRAND = "AmazonHelp"
SEED = 42


def load_tweets(path: Path = DATA_PATH) -> dict[str, dict[str, str]]:
    tweets = {}
    with path.open("r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            tweets[row["tweet_id"]] = row
    return tweets


def build_children_map(tweets: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    children = defaultdict(list)
    for tweet in tweets.values():
        parent = tweet["in_response_to_tweet_id"]
        if parent:
            children[parent].append(tweet["tweet_id"])
    return dict(children)


def is_brand_reply(tweet_id: str, tweets: dict[str, dict[str, str]]) -> bool:
    row = tweets.get(tweet_id)
    if not row or not row["response_tweet_id"]:
        return False
    return any(
        tweets.get(response_id.strip(), {}).get("author_id") == BRAND
        for response_id in row["response_tweet_id"].split(",")
    )


def find_roots(tweets: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    roots = []
    for tweet in tweets.values():
        if tweet["inbound"] != "True":
            continue
        parent = tweet["in_response_to_tweet_id"]
        if parent and parent in tweets:
            continue
        if is_brand_reply(tweet["tweet_id"], tweets):
            roots.append(tweet)
    return roots


def thread_ids(root_id: str, tweets: dict[str, dict[str, str]], children: dict[str, list[str]]) -> list[str]:
    found = []
    pending = [root_id]
    seen = set()
    while pending:
        current = pending.pop(0)
        if current in seen or current not in tweets:
            continue
        seen.add(current)
        found.append(current)
        pending[0:0] = children.get(current, [])
    return found


def format_context(ids: list[str], tweets: dict[str, dict[str, str]], limit: int = 8) -> str:
    lines = []
    for tweet_id in ids[:limit]:
        tweet = tweets[tweet_id]
        speaker = "CUSTOMER" if tweet["inbound"] == "True" else tweet["author_id"]
        text = tweet["text"].replace("\n", " ").strip()
        if text:
            lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


def build_examples(tweets: dict[str, dict[str, str]], sample_size: int = 200) -> list[dict[str, str]]:
    children = build_children_map(tweets)
    roots = find_roots(tweets)
    rng = random.Random(SEED)
    selected = rng.sample(roots, min(sample_size, len(roots)))
    examples = []
    for index, root in enumerate(selected, start=1):
        ids = thread_ids(root["tweet_id"], tweets, children)
        customer = root["text"].strip()
        intent, confidence = classify_weak(customer)
        escalation, reason = should_escalate_weak(customer, intent, confidence)
        examples.append({
            "example_id": f"amz-{index:04d}",
            "tweet_id": root["tweet_id"],
            "conversation_root_id": root["tweet_id"],
            "customer_message": customer,
            "context": format_context(ids, tweets),
            "intent": intent,
            "expected_escalation": escalation,
            "escalation_reason": reason,
            "label_source": "weak_rule_generated",
            "annotation_status": "needs_manual_review",
        })
    return examples


def build_training_rows(
    tweets: dict[str, dict[str, str]],
    excluded_roots: set[str],
    sample_size: int = 1200,
) -> list[dict[str, str]]:
    """Sample non-evaluation roots for weakly labelled model training."""
    children = build_children_map(tweets)
    candidates = [root for root in find_roots(tweets) if root["tweet_id"] not in excluded_roots]
    rng = random.Random(SEED + 1)
    selected = rng.sample(candidates, min(sample_size, len(candidates)))
    rows = []
    for root in selected:
        intent, _ = classify_weak(root["text"])
        rows.append({
            "conversation_root_id": root["tweet_id"],
            "tweet_id": root["tweet_id"],
            "customer_message": root["text"].strip(),
            "intent": intent,
            "context": format_context(thread_ids(root["tweet_id"], tweets, children), tweets),
        })
    return rows


def build_retrieval_rows(
    tweets: dict[str, dict[str, str]],
    excluded_roots: set[str],
    sample_size: int = 1200,
) -> list[dict[str, str]]:
    """Build customer-to-AmazonHelp evidence pairs outside evaluation roots."""
    children = build_children_map(tweets)
    candidates = [root for root in find_roots(tweets) if root["tweet_id"] not in excluded_roots]
    rng = random.Random(SEED + 2)
    selected = rng.sample(candidates, min(sample_size, len(candidates)))
    rows = []
    for root in selected:
        brand_replies = [
            tweets[child_id]["text"].strip()
            for child_id in children.get(root["tweet_id"], [])
            if tweets[child_id]["author_id"] == BRAND and tweets[child_id]["text"].strip()
        ]
        if not brand_replies:
            continue
        rows.append({
            "conversation_root_id": root["tweet_id"],
            "customer_message": root["text"].strip(),
            "amazonhelp_response": " ".join(brand_replies),
        })
    return rows


