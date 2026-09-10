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