# Dhaga-OS demo

An operations demo with four workspaces: Overview, CX Support, Review Intelligence, and Catalog Velocity Engine. CX handles WISMO, returns, exchanges, refunds, cancellation, payments, and product facts. It simulates verified read-only replies. All consequential actions require a human decision and remain simulated.

**All operational records are synthetic.** The seven-day return/exchange window and pre-dispatch cancellation rule are **demo policies**, not Dhaga & Co policy. The client brief is the source for the separately labeled company figures. No real customer message, payment, refund, cancellation, or listing publication occurs.

## Five-minute local start

Prerequisites: Node.js 20.9+, Python 3.12, [uv](https://docs.astral.sh/uv/). The default database is local SQLite so the demo starts without a cloud account. Production configuration uses Postgres.

```powershell
cd D:\Dhaga_OS
cd api
uv sync --extra dev
uv run alembic upgrade head
uv run python -m dhaga.seed reset
uv run python -m dhaga.seed verify
uv run uvicorn app:app --reload --port 8000
```

In a second terminal:

```powershell
cd D:\Dhaga_OS\web
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Open `http://localhost:3000`. Visit CX Support and run `TKT00001` (normal WISMO), `TKT00002` (wrong customer), `TKT00003` (carrier timeout), `TKT00004` (return approval), or `TKT00014` (unsupported policy). The same seed contains 50 named guardrail scenarios. `uv run python -m dhaga.seed reset` restores the original demo data and removes demo actions.

The default mode needs no model key. Deterministic rules and literal read-only response templates still run. Review extraction and catalog copy generation display an unavailable-model error until a key is configured. For live LangChain calls, copy `api/.env.example` to `api/.env` and set `OPENROUTER_API_KEY`. The classifier and evaluator models can be changed with `CLASSIFIER_MODEL` and `EVALUATOR_MODEL`. Run `uv run python -m scripts.model_smoke` before accepting a model swap.

## Architecture

- `web`: Next.js/TypeScript, four-section team workspace and same-origin API proxy. Session IDs are kept in an HttpOnly cookie.
- `api`: FastAPI/Python, LangChain OpenRouter roles with Pydantic structured results, deterministic policy decisions, mock commerce adapters, review analysis, catalog QA, and audit traces.
- `api/dhaga/seed.py`: fixed-seed data generator: 750 customers, 3,000 linked orders and shipments, 750 tickets (435 WISMO), 1,000 reviews, 50 products, five vendors, and 50 named guardrail cases. All dashboard counts query database records.
- `api/dhaga/policies.json`: versioned demo policy pack. Unknown policy or facts cause abstention/escalation. Refund follows inspection, with no timing promise.
- `api/alembic`: database migrations. SQLite is the zero-setup local option; set `DATABASE_URL=postgresql+psycopg://...` for managed Postgres. Run migrations, then seed.
- `api/evals/cx_cases.json`: hand-labeled held-out outcomes, separate from generated records. `api/scripts/evaluate.py` scores them.
- `npm run types`: regenerate TypeScript request types from FastAPI OpenAPI. Commit updated `api/openapi.json` and `web/lib/openapi.generated.ts` with API changes.

The CX pipeline is intake, deduplication, classification, ownership verification, mock fact retrieval, code-based eligibility, grounded reply/proposal, evaluation, simulated send or human decision, and audit. Model output cannot authorize an order action. Each case displays facts, the policy, reason codes, trace, and estimated model cost. With no live calls, cost extrapolation is intentionally blank.

## Checks

```powershell
cd api
uv run pytest -q
uv run python -m scripts.evaluate
uv run ruff check --select E4,E7,E9,F dhaga tests scripts
cd ..\web
npm run check
npm run build
```

## GitHub and Vercel deployment

The repository is set up for two Vercel projects rooted at `web` and `api`. Create a managed Postgres database, set `DATABASE_URL` and `DEMO_SESSION_SECRET` on the API project, and run `uv run alembic upgrade head` plus `uv run python -m dhaga.seed reset` against that database before opening the frontend. Set `API_BASE_URL` to the API project's HTTPS URL and the **same** `DEMO_SESSION_SECRET` on the web project. Set `OPENROUTER_API_KEY` only on the API project if live models are desired. Add both project URLs and the GitHub commit SHA to the final review record. Never commit `.env` files.

Vercel projects and managed Postgres require the owner's account access. The API's internal token blocks direct case access on Vercel if it is unset. The public `/health` endpoint can be used for deployment checks. Use the provided [final review checklist](FINAL_REVIEW.md) before presenting.

The current [verification record](VERIFICATION.md) separates local checks from the live model and deployment checks that still need account access. Review and catalog changes share the synthetic demo database; reset restores the original records. Before a public pilot, add authentication, paid-model usage limits, and per-user isolation.

## Scope and provenance

The brief and the three feature SOT files in this directory inform the implementation. The brief's roughly 9,000 weekly support tickets and 58% WISMO share are context, not measurements from the synthetic dataset. No Dhaga row-level data, production policy handbook, or live integration credentials were provided. A pilot must have Dhaga owners confirm policy text and connect production adapters first.
