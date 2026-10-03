# Build note (two-page brief)

## Chosen wedge and design

The client brief reports roughly 9,000 weekly support tickets with about 58% WISMO, and asks for an AI workflow that can be demonstrated quickly. Dhaga-OS makes CX Support the first complete slice, while Review Intelligence and Catalog Velocity share the same product, order, and vendor records. The interface gives each team a queue, evidence, next action, and visible exceptions.

The CX agent covers six core commerce areas: WISMO, returns/exchanges, refunds, cancellations, payments, and product/policy questions. The LangChain classifier handles ambiguous language with structured Pydantic output when OpenRouter is configured. Deterministic code checks order ownership, mock shipment freshness, inspection state, demo eligibility, and action approval. A separate evaluator checks optional model output. Model calls are recorded with role, model, prompt version, tokens, latency and estimated cost. Missing model access leaves literal, verified read-only templates usable and marks generation unavailable.

The two workflow patterns are (1) retrieval and grounded response for read-only questions and (2) human-approved action proposals. No real send, refund, cancellation, exchange, return, or publication occurs. The seed and policy pack are versioned. Policies invented for the demonstration are visibly marked **demo policy**.

## Evidence and limits

The deterministic seed produces 750 customers, 3,000 orders/shipments, 750 cases, 1,000 reviews, 50 SKUs, and five vendors. Exactly 435 cases are WISMO. Fifty named cases deliberately exercise authorization, missing IDs, stale tracking, provider timeout, prompt injection, unsupported policy, and delivery disputes. Twenty separately labeled CX cases are scored by an independent fixture; the generator does not label its own outputs as correct.

Review trends link to individual review text and require a minimum recent sample before alerting. Catalog readiness shows missing images, attributes, and conflicting colour provenance. Generated listing copy is constrained to verified fields and requires human approval before a publish-ready export is formed. These records demonstrate product behavior, not real Dhaga customer or policy data.

## Handoff

Use README for local start and two-project Vercel setup. Use FINAL_REVIEW for Codex, user, and joint acceptance. A production pilot requires Dhaga-approved policies, privacy/security review, live Freshdesk/Gupshup/commerce integrations, and measured model quality, latency and cost on permitted real cases.
