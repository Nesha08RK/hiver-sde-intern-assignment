from src.classifier import RuleClassifier, TfidfLogisticClassifier


def test_rule_classifier_handles_other():
    prediction = RuleClassifier().predict_one("Thanks")
    assert prediction.intent == "Other/Unclear/non-substantive"


def test_tfidf_classifier_predicts_seen_classes():
    model = TfidfLogisticClassifier().fit(
        ["where is my package", "my account was hacked"],
        ["Delivery and order fulfillment", "Account access and security"],
    )
    prediction = model.predict_one("where is my order")
    assert prediction.intent in {
        "Delivery and order fulfillment",
        "Account access and security",
    }
    assert 0 <= prediction.confidence <= 1