# 150-Example Golden-Set Annotation Guide

Use this guide while reviewing `golden_set_150.csv`. The file is a deterministic subset of the existing 200-example AmazonHelp annotation template: rows 1 through 150 in the original file order.

The full definitions, inclusion and exclusion criteria, context rules, ambiguity precedence, and escalation policy are in [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md). Use that guide as the source of truth.

Fill only these three columns:

- `reviewer_intent`: exactly one of the nine taxonomy labels.
- `reviewer_expected_escalation`: exactly `AUTO_HANDLE` or `ESCALATE`.
- `reviewer_notes`: brief reasoning for ambiguous or escalation-heavy cases.

Do not modify `customer_message`, `context`, or any weak-label columns. The existing values in `intent`, `expected_escalation`, `escalation_reason`, `label_source`, and `annotation_status` are automatic suggestions or metadata, not human labels. Do not copy them automatically.

The nine allowed intents are:

1. Delivery and order fulfillment
2. Customer service escalation and feedback
3. Product condition, item accuracy, and seller issues
4. Digital products, devices, and apps
5. Prime membership and benefits
6. Returns, refunds, and charges
7. Pricing, offers, and product availability
8. Account access and security
9. Other/Unclear/non-substantive

Review the customer message first, then use the conversation context to resolve references and follow-ups. Use `Other/Unclear/non-substantive` when the message remains incomplete, irrelevant, acknowledgement-only, emoji-only, link-only, or impossible to classify reliably. Use `ESCALATE` for security, legal, sensitive payment, repeated unresolved support, insufficient-information, or high-risk cases; otherwise use `AUTO_HANDLE` when a clear routine response is appropriate.

Manual review is complete when all 150 `reviewer_intent` and all 150 `reviewer_expected_escalation` fields are non-empty and use only the allowed values.
