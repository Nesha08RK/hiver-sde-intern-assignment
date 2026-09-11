from scripts.human_agreement import evaluate_rows


class FakeAgent:
    def __init__(self, predictions):
        self.predictions = iter(predictions)

    def predict(self, text, context=""):
        return next(self.predictions)


def test_evaluate_rows_compares_intent_and_escalation():
    rows = [
        {"customer_message": "first", "reviewer_intent": "A", "reviewer_expected_escalation": "AUTO_HANDLE"},
        {"customer_message": "second", "reviewer_intent": "B", "reviewer_expected_escalation": "ESCALATE"},
    ]
    metrics = evaluate_rows(
        rows,
        FakeAgent([
            {"intent": "A", "decision": "AUTO_HANDLE"},
            {"intent": "C", "decision": "AUTO_HANDLE"},
        ]),
    )

    assert metrics["reviewed_examples"] == 2
    assert metrics["intent_percentage_agreement"] == 0.5
    assert metrics["escalation_percentage_agreement"] == 0.5