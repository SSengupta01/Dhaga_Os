# Final review checklist

## Codex verification

1. Reset and verify the seed twice; compare counts and stable IDs, check foreign keys, linked order lines and shipment history, and confirm 50 deliberate guardrail cases.
2. Inspect every rendered demo policy label and ensure no synthetic eligibility rule reads as approved Dhaga policy.
3. Run unit/integration tests, the separate held-out CX evaluation, OpenAPI type generation, frontend type check and production build.
4. With an OpenRouter key, run the model smoke test for both configured models, test malformed/provider-failure paths, and record per-intent quality, unsafe simulated sends, escalation rate, latency, token count and estimated cost. Without a key, mark live-model evidence pending; do not substitute deterministic results for it.
5. Browse Overview, CX, Reviews, and Catalog at desktop and mobile widths. Check keyboard navigation, readable contrast, empty/loading/error states, review evidence, low-sample alert suppression, catalog blockers and human approval.
6. Record GitHub commit SHA, both Vercel URLs, migration version, seed and policy versions, and the database reset time. Inspect deployment logs and `/health`.

## User acceptance on deployed URL

1. In a fresh session, open **Overview → Demo data and rules** and separate verified brief figures from synthetic operational counts.
2. In **CX Support**, run normal WISMO (`TKT00001`) and inspect ownership, tracking evidence, policy and trace. Approve the return proposal (`TKT00004`); inspect the audit and confirm no real order change occurred.
3. Run wrong customer (`TKT00002`), missing policy (`TKT00014`), carrier timeout (`TKT00003`), and a missing-ID/stale-scan/disputed-delivery case from the scenario queue. Check facts, reason codes, and blocked actions.
4. In **Review Intelligence**, open an alert, inspect linked review text, and create an investigation without assuming the vendor caused the issue.
5. In **Catalog Velocity**, inspect a blocked SKU, normalize a field, run QA, and confirm publish approval stays blocked until source facts and generated copy are ready. Validate a CSV intake with an invalid row.

## Joint signoff and presentation

- Confirm deployed commit equals GitHub commit. Cold-start from README against a clean database. Rehearse one happy path and one deliberate failure.
- Review cost math: measured mean cost per case × 9,000 weekly tickets and × 5,220 estimated WISMO tickets. A missing live sample stays blank, not zero.
- In the presentation, identify each number as brief fact, demo assumption, measured test result, or future pilot hypothesis. Show the policy validation and live integration work needed before a production pilot.
