import csv

import pytest

from src.agent import SupportAgent
from src.classifier import HybridClassifier, RuleClassifier, TfidfLogisticClassifier
from src.retriever import TfidfRetriever


def make_agent():
    rows = [
        {
            "conversation_root_id": "r1",
            "customer_message": "Where is my package?",
            "amazonhelp_response": "Please check your tracking page.",
        },
        {
            "conversation_root_id": "r2",
            "customer_message": "I cannot login to my account",
            "amazonhelp_response": "Please use the secure account page.",
        },
    ]
    return SupportAgent(TfidfRetriever(rows), RuleClassifier())


def test_delivery_classification_and_output_structure():
    result = make_agent().predict("Where is my Amazon order?")
    assert result["intent"] == "Delivery and order fulfillment"
    assert result["decision"] == "AUTO_HANDLE"
    assert result["evidence"]
    assert result["draft_reply"]


def test_security_message_escalates():
    result = make_agent().predict("Someone hacked my Amazon account")
    assert result["intent"] == "Account access and security"
    assert result["decision"] == "ESCALATE"


def test_retrieval_returns_historical_response():
    evidence = make_agent().retriever.retrieve("Where is my package?", top_k=1)
    assert evidence[0].amazonhelp_response == "Please check your tracking page."


def test_project_agent_uses_fitted_tfidf_classifier(tmp_path):
    retrieval_path = tmp_path / "retrieval.csv"
    with retrieval_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["conversation_root_id", "customer_message", "amazonhelp_response"],
        )
        writer.writeheader()
        writer.writerow({
            "conversation_root_id": "r1",
            "customer_message": "Where is my package?",
            "amazonhelp_response": "Check tracking.",
        })

    training_path = tmp_path / "training.csv"
    with training_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["customer_message", "intent"])
        writer.writeheader()
        writer.writerows([
            {"customer_message": "where is my package", "intent": "Delivery and order fulfillment"},
            {"customer_message": "my account was hacked", "intent": "Account access and security"},
        ])

    agent = SupportAgent.from_project_files(retrieval_path, training_path)

    assert agent.classifier.name == "hybrid_tfidf_with_delivery_override"
    assert agent.classifier.model.name == "tfidf_logistic_regression"
    assert agent.predict("where is my package")['intent'] == "Delivery and order fulfillment"


def test_human_training_requires_complete_labels_and_uses_context(tmp_path):
    retrieval_path = tmp_path / "retrieval.csv"
    with retrieval_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["conversation_root_id", "customer_message", "amazonhelp_response"],
        )
        writer.writeheader()
        writer.writerow({
            "conversation_root_id": "r1",
            "customer_message": "Where is my package?",
            "amazonhelp_response": "Check tracking.",
        })

    weak_training_path = tmp_path / "training.csv"
    with weak_training_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["customer_message", "context", "intent"])
        writer.writeheader()
        writer.writerows([
            {"customer_message": "first", "context": "delivery context", "intent": "Delivery and order fulfillment"},
            {"customer_message": "second", "context": "account context", "intent": "Account access and security"},
        ])

    human_path = tmp_path / "human_training.csv"
    with human_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["customer_message", "context", "reviewer_intent"])
        writer.writeheader()
        writer.writerows([
            {"customer_message": "first", "context": "delivery context", "reviewer_intent": ""},
            {"customer_message": "second", "context": "account context", "reviewer_intent": "Account access and security"},
        ])

    assert not SupportAgent.human_training_ready(human_path)
    with pytest.raises(ValueError, match="reviewer_intent"):
        SupportAgent.from_project_files(retrieval_path, weak_training_path, human_path)

    rows = []
    with human_path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    rows[0]["reviewer_intent"] = "Delivery and order fulfillment"
    with human_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)

    assert SupportAgent.human_training_ready(human_path)
    agent = SupportAgent.from_project_files(retrieval_path, weak_training_path, human_path)
    assert agent.classification_text("message", "prior context") == "message\n\nCONVERSATION CONTEXT:\nprior context"


def make_hybrid_agent():
    model = TfidfLogisticClassifier().fit(
        ["refund my order", "my account was hacked", "fire tv app crashes"],
        [
            "Returns, refunds, and charges",
            "Account access and security",
            "Digital products, devices, and apps",
        ],
    )
    return SupportAgent(make_agent().retriever, HybridClassifier(model))


@pytest.mark.parametrize("text", [
    "Where is my order?",
    "My package hasn't arrived",
    "Can I get a tracking update?",
])
def test_hybrid_classifier_overrides_obvious_delivery_queries(text):
    result = make_hybrid_agent().predict(text)

    assert result["intent"] == "Delivery and order fulfillment"


def test_hybrid_classifier_keeps_ambiguous_non_delivery_query_on_tfidf():
    agent = make_hybrid_agent()
    model_prediction = agent.classifier.model.predict_one("refund my order")

    result = agent.predict("I need a refund")

    assert result["intent"] == model_prediction.intent