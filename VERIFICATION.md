# Local verification — 3 October 2026

## Completed

- Fresh Alembic migration and reset on a new SQLite database: 750 customers, 3,000 linked orders/shipments, 750 cases, 1,000 reviews, 50 products, five vendors; 435 WISMO cases and 50 named guardrail cases.
- Foreign keys enabled in local SQLite and verified by joins from tickets through customers/orders, shipments, products, and reviews.
- Backend: 12 tests passed; Ruff passed. Held-out fixture: 20/20 decisions/intents/reasons matched, with zero unsafe simulated sends. The 65% escalation rate is for deliberately failure-heavy evaluation cases, not an estimate of live traffic.
- Frontend: TypeScript check and Next.js production build passed. Overview, Reviews, and Catalog were inspected in the local browser; a normal CX WISMO case was inspected earlier. Mobile catalog had no document overflow at 390px width.
- Generated OpenAPI request types are committed. Git commit was created locally.

## Pending external verification

- OpenRouter key is unavailable. Live LangChain model schema, swap, latency, token usage, and cost remain unmeasured. The app displays “Awaiting live sample” instead of extrapolating zero cost.
- No GitHub remote/credential, Vercel login, or managed Postgres connection was available. No GitHub push, Vercel URL, or deployed user review has occurred. Those steps follow the owner's access setup.
- Catalog and Review mutations currently affect the shared synthetic demo database; `seed reset` restores them. Before a public pilot, add authentication, usage limits for paid model calls, and per-user isolation.
