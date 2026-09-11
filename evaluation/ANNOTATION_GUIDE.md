# AmazonHelp Golden-Set Annotation Guide

## Purpose

This file explains how to manually review the 200 AmazonHelp examples in `golden_set_annotation_template.csv`.

The file contains:

- The customer message and reconstructed conversation context.
- Existing weak labels in `intent` and `expected_escalation`.
- Empty reviewer fields for the human decision.

The weak labels are automatically generated suggestions. They are not human labels and must not be copied automatically. Manual annotations belong only in:

- `reviewer_intent`
- `reviewer_expected_escalation`
- `reviewer_notes`

Use exactly the nine intent names and the two escalation values shown below. Do not edit the original message, context, weak label, label source, or annotation status columns.

## Intent Labels

### 1. Delivery and order fulfillment

**Definition:** Problems or questions about an order's shipment, delivery progress, delivery attempt, destination, fulfillment cancellation, or missing package.

**Include:** Late or undelivered orders, tracking problems, conflicting delivery dates, claimed delivery that did not happen, wrong delivery address, failed delivery attempts, dispatch or pre-order fulfillment, and order-status requests.

**Exclude:** A damaged, defective, used, or incorrect item after delivery; a refund or charge question where money movement is central; a Prime membership complaint where membership value is central; and generic dissatisfaction without a recoverable order issue.

### 2. Customer service escalation and feedback

**Definition:** A request to reach, escalate to, or complain about customer support when no more specific operational issue is the primary issue.

**Include:** Requests for a human, senior agent, manager, direct contact, complaint handling, or escalation; repeated unresolved-support complaints; and feedback about the service interaction itself.

**Exclude:** Messages with a clear delivery, refund, product, account, security, or technical issue. Keep the concrete issue as the intent and treat the support complaint as secondary.

### 3. Product condition, item accuracy, and seller issues

**Definition:** Problems with the physical item received, including its condition, correctness, packaging, warranty, or seller conduct.

**Include:** Damaged, defective, used, opened, wrong-size, wrong-item, incomplete, or poorly packaged products; warranty complaints; suspected counterfeit items; and specific seller conduct affecting the order or item.

**Exclude:** A package that is missing or late before receipt; a standalone refund-status problem; a pre-purchase price or availability question; and a technical problem with an Amazon app, device, or digital product.

### 4. Digital products, devices, and apps

**Definition:** Technical support for Amazon digital content, applications, streaming, Kindle, Alexa, Fire devices, or related website/app behavior.

**Include:** Playback or HD problems, app crashes, Kindle purchase or reading problems, Alexa behavior, Fire-device problems, broken pages, download failures, and digital-product feature problems.

**Exclude:** Login failure or suspected account compromise; a defect in a separately purchased physical item; and ordinary order or delivery problems.

### 5. Prime membership and benefits

**Definition:** Questions or complaints about Prime membership, trials, fees, or promised Prime benefits.

**Include:** Trial continuation or cancellation, Prime charges or membership value, and delivery complaints where the central point is that a Prime benefit was not received.

**Exclude:** A normal shipment-status question where Prime is only mentioned incidentally; a delivery failure with no membership or benefit concern; and general product pricing or discount questions.

### 6. Returns, refunds, and charges

**Definition:** Post-purchase money movement or return handling that is not primarily a Prime-membership issue.

**Include:** Refund status, refund requests, return processing, return pickup, cancellation with payment consequences, unexpected charges, and payment or cashback issues where money has already moved or is expected back.

**Exclude:** A Prime fee or trial as the central issue; a product defect where the item's condition is the main issue; and a pre-purchase price or discount question.

### 7. Pricing, offers, and product availability

**Definition:** Pre-purchase questions or complaints about price, discounts, exchange offers, shipping cost, product availability, or purchase options.

**Include:** Misleading discounts, price matching, exchange availability, product availability, added shipping charges shown before purchase, release-date or availability questions, and purchase-option requests.

**Exclude:** A charge already taken, refund, or cashback dispute; Prime fees; a specific missing or late order; and a defective item.

### 8. Account access and security

**Definition:** Problems accessing an Amazon account or concerns about unauthorized account, card, review, or scam activity.

**Include:** Login failure, locked or changed account credentials, hacked accounts, unauthorized reviews or card information, phishing, impersonation, suspicious messages, and suspected fraud.

**Exclude:** A normal order or payment problem without an account or security signal; ordinary website/app malfunction without an access concern; and a general privacy or feature request.

### 9. Other/Unclear/non-substantive

**Definition:** A deliberate fallback for messages that do not provide a reliable substantive support intent.

**Include:** Thanks, acknowledgements, praise, emoji-only messages, insults without a recoverable issue, link-only or order-number-only messages, incomplete follow-ups, unrelated requests, and text that cannot be interpreted reliably because of missing context, language, or encoding corruption.

**Exclude:** Any message where the customer has a clear recoverable support issue. Do not use this label merely because the issue is unusual or written in another language if the context makes the intent clear.

## How to Use Conversation Context

1. Read the `customer_message` first and form an initial label.
2. Read the complete `context` before finalizing. The context may clarify what “it,” “this,” “done,” or a link refers to.
3. Label the customer's underlying support issue, not AmazonHelp's reply.
4. Use the earliest clear customer issue as the primary intent when the selected message is a follow-up.
5. If the context reveals that the issue was already resolved but the selected message is only thanks or acknowledgement, use `Other/Unclear/non-substantive`.
6. If context is still insufficient, use `Other/Unclear/non-substantive` rather than guessing.
7. Do not use personal information in the context as a reason for a label. Order numbers, phone numbers, email redactions, and URLs are evidence only when the surrounding text establishes the issue.

## Ambiguous-Case Rules

Use one primary intent per example. Apply these rules in order when categories overlap:

1. A Prime complaint is **Prime membership and benefits** when membership value, Prime fees, trials, or a promised Prime benefit is central. A normal late delivery remains **Delivery and order fulfillment** when Prime is incidental.
2. A product defect, wrong item, damaged item, used item, or packaging problem is **Product condition, item accuracy, and seller issues** even if the customer also asks for a refund, when the item condition is the main issue.
3. A refund, charge, payment, return, cashback, or money movement already in progress is **Returns, refunds, and charges** when the money or return process is central.
4. A pre-purchase price, discount, exchange, release, shipping-cost, or availability question is **Pricing, offers, and product availability**.
5. Login, account lockout, unauthorized activity, suspicious messages, or suspected compromise is **Account access and security**.
6. A technical problem with an Amazon app, website feature, device, Kindle, Alexa, Prime Video, or other digital product is **Digital products, devices, and apps**.
7. Generic dissatisfaction is **Customer service escalation and feedback** only when no concrete underlying delivery, product, refund, account, security, or technical issue can be recovered.
8. If the message is too incomplete, irrelevant, acknowledgement-only, emoji-only, link-only, or otherwise impossible to classify reliably, use **Other/Unclear/non-substantive**.

Sentiment is not an intent. A message saying “worst service” with a clear late order is Delivery; the same complaint without a recoverable issue is Customer service escalation and feedback or Other/Unclear depending on whether it explicitly requests support or is only an insult.

## Expected Escalation

Enter exactly one of:

- `AUTO_HANDLE`
- `ESCALATE`

This is the expected routing decision for the message, not a judgment about whether AmazonHelp historically escalated it.

### Use `ESCALATE` when

- The message indicates account compromise, phishing, fraud, unauthorized access, or sensitive security risk.
- The customer makes a legal, police, court, lawyer, regulatory, or consumer-forum threat.
- The message involves a sensitive payment dispute, unauthorized charge, bank/card concern, or substantial financial risk.
- The customer reports repeated failed support attempts or an unresolved case requiring a human investigation.
- The message lacks enough information to safely answer, including `Other/Unclear/non-substantive` cases.
- The situation is high-impact or safety-sensitive and cannot be resolved with a general informational response.

### Use `AUTO_HANDLE` when

- The intent is clear and a concise informational response or ordinary troubleshooting step is appropriate.
- The customer asks a routine delivery, product, digital, Prime, refund, or pricing question with enough context and no security, legal, payment-risk, or repeated-resolution signal.
- The message is a straightforward request that does not require account-level investigation.

When uncertain between the two escalation values, choose `ESCALATE` and explain the reason in `reviewer_notes`.

## Annotation Procedure

For every row:

1. Read `customer_message`.
2. Read `context`.
3. Choose exactly one taxonomy label and enter it in `reviewer_intent`.
4. Choose exactly one escalation value and enter it in `reviewer_expected_escalation`.
5. Add a short explanation in `reviewer_notes` only for ambiguous, context-dependent, multilingual, security-sensitive, or escalation-heavy cases.
6. Leave all original weak-label columns unchanged.
7. Do not add new labels, alternate spellings, confidence values, or human scores.

The expected review set contains 200 examples. Manual review is complete when all 200 `reviewer_intent` and all 200 `reviewer_expected_escalation` cells are non-empty and each value exactly matches this guide.