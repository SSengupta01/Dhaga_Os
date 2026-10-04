# Submission deployment review — 4 October 2026

- Product URL: https://dhaga-os.vercel.app
- Public repository: https://github.com/SSengupta01/Dhaga_Os
- One Vercel project: `dhaga-os`, in `ssengupta731-1335s-projects`.
- Verified application release: `e1f0471b5f6bfcfbb37a6c9285067053ea575e59`.
- Production deployment: `dpl_4qtH1xR82D5Vka1hNkMkG4DjEF4V`, state READY.
- GitHub checks: https://github.com/SSengupta01/Dhaga_Os/actions/runs/37169129747 — success.

## Deployment configuration

Root `vercel.json` uses Vercel Services to build Next.js and FastAPI together. All public traffic goes to Next.js; its API proxy calls FastAPI through a private service binding. The project has a generated internal API secret and a free Neon Postgres resource, `dhaga-os-demo`, in Singapore. Credentials stay in Vercel environment settings and ignored local files.

Database migrations succeeded against Postgres. The generator loaded and verified 750 customers, 3,000 orders, 3,000 shipments, 750 tickets (435 WISMO), 1,000 reviews, 50 products, and five vendors. No local development database was reset during deployment.

## Verified on the production URL

- Anonymous HTTP request to `/api/health`: 200; database connected.
- Overview loads database counts, area/donut charts, policy provenance, and separate client-brief facts.
- Browser WISMO `TKT00001`: grounded status reply simulated; ownership and carrier facts visible.
- Browser wrong-customer `TKT00002`: ORDER_CUSTOMER_MISMATCH; no order facts exposed; approve/edit disabled.
- API scenario checks: carrier timeout `TKT00003` escalates with TRACKING_UNAVAILABLE; unknown policy `TKT00014` escalates with POLICY_UNKNOWN.
- Return `TKT00004`: approval_required; human approval becomes simulated_approved and writes an audit record.
- Blocked catalog SKU `PROD0011`: approval/export rejected with HTTP 422.
- Review page loads 1,000 synthetic reviews, evidence, trends, sentiment and issue heatmap.
- Catalog page loads 50 drafts; readiness charts show 36 ready, three requiring review and 11 blocked.
- Dashboard, review overview/evidence and catalog overview API responses: 200.
- Public GitHub metadata confirms `private: false`; main matches the application release above.

All actions remain synthetic and simulated. Operational counts are calculated from demo records; they do not measure Dhaga's live performance.

## Remaining model check

OPENROUTER_API_KEY is not configured at the time of verification. Deterministic CX, seeded review signals and catalog rules operate without it. Live review re-analysis and guarded catalog copy generation require the key. Model accuracy, latency and cost have not been measured, and the UI reports this limitation.

The owner should add the key to the production environment of `dhaga-os`, then redeploy. Codex should run a real classifier/evaluator schema check, review re-analysis, guarded catalog copy and model-swap smoke check, and record measured costs before the final presentation.

## User acceptance and deck gate

Open the product URL in a fresh browser session. Inspect Demo data and rules, run a WISMO case, approve a return, and try the wrong-customer/carrier-timeout/unknown-policy cases. Review a product issue and a blocked SKU.

The pitch deck has not been created. Its creation requires a separate user approval after the product review, as requested on 4 October 2026.
