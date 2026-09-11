# Decision Log

## Decision 1 — Select AmazonHelp as the target brand

### Decision
We selected `AmazonHelp` as the target customer-support account.

### Alternatives considered
We initially considered:

- AmazonHelp
- AppleSupport
- TMobileHelp
- SpotifyCares
- Uber_Support

### Why AmazonHelp
AmazonHelp provides a large volume of customer-support interactions and a diverse range of support scenarios.

Initial inspection showed examples involving:

- Order and delivery problems
- Shipping and pre-order issues
- Device troubleshooting
- Prime Video playback problems
- Account-related requests
- Customer complaints
- Product/content feedback
- Human-support escalation

This diversity is useful for building and evaluating an agent that must classify intent, generate a grounded response, and determine whether the issue should be escalated.

### Evidence
The dataset contains a large number of AmazonHelp customer interactions, and manual inspection of sampled conversations showed that the account contains both simple support requests and cases requiring escalation.

### Trade-off
AmazonHelp's large and multilingual conversation set introduces additional preprocessing challenges, including language variation, noisy tweets, and incomplete conversation context.

We therefore prioritize a reproducible subset of the data rather than attempting to process the entire dataset during evaluation.

## Decision 2 — Intent taxonomy for AmazonHelp discovery sample

### Scope and method

The discovery script was reviewed together with the raw dataset and its reproducible sample:

- Dataset: `data/raw/twcs/twcs.csv`
- Brand: `AmazonHelp`
- Conversation roots found by the script: 76,962
- Sample size: 200 customer messages
- Random seed: 42
- Sampling unit: inbound customer messages found inside AmazonHelp-rooted threads

The frequencies below are approximate counts from this one reviewed sample, not dataset-wide prevalence and not ground-truth labels. Each message was assigned one primary category for counting. Where a message mentioned more than one issue, the most actionable issue took precedence in this order: product/item issue, Prime, account/security, digital/device/app, refund/charge, pricing/offer, delivery/order, service escalation, then Other/Unclear.

### Proposed final taxonomy

#### 1. Delivery and order fulfillment

**Definition:** Problems or questions about an order's shipment, delivery progress, delivery attempt, destination, cancellation during fulfillment, or missing package.

**Belongs:** Late or undelivered orders, inconsistent tracking or delivery dates, claimed delivery that did not happen, wrong delivery address, failed delivery attempt, dispatch/pre-order fulfillment, and requests for an order status.

**Does not belong:** A damaged, defective, used, or incorrect item after delivery; a refund or charge question without a delivery issue; Prime membership complaints where the main request is membership value; or a generic complaint with no recoverable order issue.

**Examples:**

- Sample 22: “Got an email from Amazon saying my package was delivered. It's not on my porch or at the post office.”
- Sample 77: “Order tracking says delivery by 8pm today but order details say delivery by 9pm tomorrow. Which is it?”
- Sample 192: “Why can’t the order be reissued if it’s location is unknown. Surely the carrier must know where it is.”

**Approximate reviewed-sample frequency:** 62/200 (31%).

#### 2. Customer service escalation and feedback

**Definition:** A request to reach, escalate to, or complain about support when no more specific operational issue can be reliably identified.

**Belongs:** Requests for a human, senior agent, direct contact, complaint handling, or escalation; repeated unresolved-support complaints; and feedback focused on the service interaction itself.

**Does not belong:** A message where the underlying delivery, refund, product, account, or technical problem is clear. Those messages retain the concrete issue as the primary intent, with escalation treated as a secondary attribute.

**Examples:**

- Sample 37: “can you initiate a dm”
- Sample 126: “why don't you allow the customer, access to your customer care representatives before placing an order”
- Sample 163: “How do I get a direct email or Telephone number for your senior U.K. Legal people?”

**Approximate reviewed-sample frequency:** 26/200 (13%).

#### 3. Product condition, item accuracy, and seller issues

**Definition:** Problems with the physical item received, its condition, correctness, packaging, warranty, or a seller's handling of the item/order.

**Belongs:** Damaged, defective, used, opened, wrong-size, wrong-item, incomplete, or poorly packaged products; warranty complaints; and specific seller conduct such as manipulating cancellations or reviews.

**Does not belong:** A package that is missing or late before receipt; a pure refund-status question; product discovery or price questions; or a technical fault in an Amazon app/device when the purchased physical item is not the issue.

**Examples:**

- Sample 84: “I've had my new Fire 10 tablet for five minutes and it's already freezing and not opening things.”
- Sample 110: “They shipped me USED GARMENTS priced as new.”
- Sample 175: “I have received the headset broken.”

**Approximate reviewed-sample frequency:** 17/200 (8.5%).

#### 4. Digital products, devices, and apps

**Definition:** Technical support for Amazon digital content, apps, streaming, Kindle, Alexa, Fire devices, or related site/app behavior.

**Belongs:** Playback or HD problems, app crashes, Kindle purchase or reading problems, Alexa behavior, Fire-device problems, broken pages, and feature behavior in Amazon digital products.

**Does not belong:** Account login or suspected account/card compromise; a physical-product defect; or a general order/delivery problem.

**Examples:**

- Sample 33: “I say play blippi and it keeps trying to set up a pandora station.”
- Sample 90: “After I start up an app it likes kicking me out.”
- Sample 177: “my amazon prime video has stopped playing anything in HD on Wi-fi on my iPhone 7+.”

**Approximate reviewed-sample frequency:** 14/200 (7%).

#### 5. Prime membership and benefits

**Definition:** Questions or complaints about Prime membership, trials, fees, or promised Prime benefits.

**Belongs:** Trial continuation or cancellation, Prime charges, membership value, and complaints specifically about Prime delivery benefits.

**Does not belong:** A normal shipment-status issue where Prime is only mentioned incidentally; a standalone delivery failure without a membership question; or a general pricing/discount question.

**Examples:**

- Sample 25: “Will this commit me to an annual membership or can I cancel again after the trial?”
- Sample 86: “I've had 4 orders after that was late. Yesterday's was 3 days late.”
- Sample 169: “I now wants to get a refund of the 500 bucks I paid for Prime.”

**Approximate reviewed-sample frequency:** 9/200 (4.5%).

#### 6. Returns, refunds, and charges

**Definition:** Post-purchase money movement or return handling that is not primarily a Prime-membership issue.

**Belongs:** Refund status, requesting a refund, return processing, cancellation with payment consequences, and an order charge or payment that needs resolution.

**Does not belong:** A Prime fee or trial; a product defect where the main message is about the item itself; or a price/discount question before purchase.

**Examples:**

- Sample 4: “Can't be refunded until the order is despatched and then I'll have to ring back and request a refund.”
- Sample 140: “Process my return-refund via mobile no.”
- Sample 182: “Still awaiting for my refund.. More than 60days now...”

**Approximate reviewed-sample frequency:** 9/200 (4.5%).

#### 7. Pricing, offers, and product availability

**Definition:** Pre-purchase questions or complaints about price, discounts, exchange offers, shipping cost, availability, or product/fulfillment options.

**Belongs:** Discount or price-transparency complaints, price matching, exchange availability, product availability, shipping charges shown at purchase, and requests for delivery-carrier or alert options before or during purchase.

**Does not belong:** A charge already taken from the customer; Prime fees; a specific missing or late order; or a defective item.

**Examples:**

- Sample 30: “Why there is moto c plus in mobile exchange list.”
- Sample 104: “It says it's giving 69%off ... But the actual rate itself is 499/-.”
- Sample 157: “Would Amazon price match a deal on Amazon fresh with a code?”

**Approximate reviewed-sample frequency:** 9/200 (4.5%).

#### 8. Account access and security

**Definition:** Problems accessing an Amazon account or concerns about unauthorized account, card, review, or scam activity.

**Belongs:** Login failure, suspicious account activity, unauthorized reviews or card information, and messages identifying phishing or impersonation attempts.

**Does not belong:** A normal order or payment issue with no account-security signal; a website or app malfunction with no access/security concern; or a general privacy feature request.

**Examples:**

- Sample 36: “someone is posting product reviews from my account?”
- Sample 55: “a scam email ... asking me to pay outstanding money” (translated Japanese message in the sample).
- Sample 94: “I cannot login to my amazon account even if my password is correct.”

**Approximate reviewed-sample frequency:** 5/200 (2.5%).

#### Other/Unclear/non-substantive

This is a deliberate handling bucket, not a substantive support intent. It covers thanks, acknowledgements, emojis, praise, insults without a recoverable issue, link-only or order-number-only follow-ups, multilingual or encoding-corrupted text that cannot be interpreted reliably, incomplete context, and requests unrelated to Amazon customer support. It contains 49/200 messages (24.5%) in the reviewed sample.

Examples include Sample 8 (“Thanks”), Sample 35 (emoji-only), and Sample 72 (order number only). These should be excluded from substantive intent training or retained as a separate rejection/unclear class. They should not be forced into a support category.

### Overlap and ambiguous cases

- Delivery, Prime, and service escalation overlap frequently. A late delivery with a clear Prime-membership complaint is Prime; a late delivery with only frustration remains Delivery; a complaint about support with no recoverable operational issue is Service escalation.
- Product defects often lead to a refund request. Use Product condition when the item condition is the main issue, and Returns/refunds when the money or return process is the main issue.
- Pricing and payment language can look similar. “Shipping added” or “discount is misleading” is Pricing; money already charged, refunded, or held is Returns/refunds.
- Digital-device and account issues overlap around login, apps, and Fire devices. Use Account/security for access or compromise, Digital for product/app behavior after access is available.
- Several messages are follow-ups whose intent depends on earlier thread context. The sample contains “Done,” “I already replied,” “USPS,” and order-number-only messages; the classifier should allow Other/Unclear when the message alone does not establish an issue.
- The sample is multilingual and includes visibly corrupted character encoding. A message that cannot be translated or interpreted with confidence should remain Other/Unclear rather than receive a fabricated label.

### Important observations about the AmazonHelp data

- The reviewed messages are not all initial customer questions. They include follow-ups, acknowledgements, reactions, complaints, and messages whose meaning depends on earlier turns.
- Delivery and fulfillment dominates the substantive sample, but nearly one quarter of the reviewed rows are non-substantive or too incomplete to classify safely.
- Customer sentiment is often strong, but sentiment is not an intent. “Worst service” should inherit a concrete delivery/product/refund intent when one is present; otherwise it belongs to Service escalation or Other/Unclear.
- The dataset contains multiple languages, mojibake, emojis, URLs, redacted contact details, order numbers, and occasional irrelevant employment/legal/product-feedback requests. These are data-quality and routing signals, not reasons to create many narrow intent classes.
- The current discovery script samples deterministically but previously failed while printing some Unicode messages under the Windows default console encoding. Its stdout is now explicitly configured as UTF-8 so the complete seed-42 sample can be reproduced.

### Decision

Use the eight substantive intents above plus `Other/Unclear/non-substantive` for the next discovery-stage artifact. Do not split delivery into many carrier/status subcategories, do not create separate sentiment classes, and do not force context-dependent or noisy messages into substantive intents. No ML model, chatbot, retriever, generator, evaluation system, or fabricated statistics are part of this decision.

## Decision 3 — Conversation-aware golden set

Select 200 AmazonHelp conversation roots with seed 42 so evaluation examples are independent conversation units rather than arbitrary tweets. Store the customer message, root ID, and bounded thread context for review.

## Decision 4 — Weak labels are not human labels

Generate provisional labels with transparent keyword rules only to make the pipeline runnable. Mark every generated row `weak_rule_generated` and `needs_manual_review`; do not describe these labels or their metrics as human performance.

## Decision 5 — Other/Unclear remains a real class

Keep acknowledgements, incomplete follow-ups, security-sensitive ambiguity, and uninterpretable text in the explicit Other/Unclear class instead of forcing them into a substantive intent.

## Decision 6 — Leakage prevention by conversation root

Exclude every golden conversation root from training and retrieval. Record the exclusion in `evaluation/conversation_split.csv` so an evaluation message cannot retrieve its own historical response.

## Decision 7 — Rule baseline

Use ordered regular-expression rules as the explainable baseline. Its score against labels generated by the same rules is known to be circular and is reported only as a pipeline smoke test.

## Decision 8 — Statistical baseline

Use word and bigram TF-IDF features with class-balanced logistic regression. This is inexpensive, reproducible, and inspectable for a first model, while its results remain provisional until manual labels exist.

## Decision 9 — Historical retrieval

Use TF-IDF cosine similarity over non-evaluation customer messages paired with direct AmazonHelp replies. Return top-k evidence with similarity scores rather than inventing unsupported facts.

## Decision 10 — Deterministic fallback generation

Use concise intent-specific fallback replies when no LLM API is configured. Replies request missing order or product details and do not claim that an action was performed.

## Decision 11 — Escalation policy

Escalate account/security concerns, legal threats, sensitive payment disputes, low-confidence predictions, and unclear messages. Return both a machine-readable decision and a short reason.

## Decision 12 — Optional LLM judge

Do not generate judge scores without an available API and configured adapter. The judge command writes an explicit unavailable status instead.

## Decision 13 — Human-vs-model agreement completed

Complete human-vs-model agreement on the 150-example golden set using the manually reviewed intent and escalation labels. The recorded results are:

- Intent Cohen's kappa: 0.0624
- Intent percentage agreement: 18.67%
- Escalation Cohen's kappa: 0.0000
- Escalation percentage agreement: 55.33%

These are actual model comparisons against human labels, separate from the weak-label baseline metrics. No human agreement is fabricated.

## Decision 14 — Evaluation outputs

Write actual metrics, per-class reports, confusion matrices, and observed mismatches to `evaluation/results/`. Clearly identify their weak-label source and avoid treating them as final quality claims.

## Decision 15 — Reproducibility

Keep all sampling seeds, paths, schemas, and commands in code and documentation. Do not commit the raw dataset, virtual environment, API keys, or generated result directory.