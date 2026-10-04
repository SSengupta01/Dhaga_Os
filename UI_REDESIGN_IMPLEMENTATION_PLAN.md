# Dhaga-OS UI redesign implementation plan

**Prepared:** 3 October 2026  
**Status:** Visual direction and four-section navigation validated by the user. Implementation plan prepared; application code changes await approval of the visual previews.

## 1. Approved direction

Redesign Dhaga-OS using the supplied support dashboard image as the visual reference: dark navy navigation, purple selected states and primary actions, a light lavender workspace, white cards, fine borders, restrained shadows, clear typography, and compact operational layouts.

Keep four primary sections: **Overview, CX Support, Review Intelligence, Catalog Velocity Engine**. CX uses a three-column desktop workspace: case queue, conversation/actions, and supporting evidence. Apply the same design language to Reviews and Catalog.

Use varied chart types within analytical dashboards. Choose each visual for the question it answers; chart variety should improve understanding. The everyday case workspace should prioritize reading and decisions, with deeper charts available in its Analytics view.

This is principally a frontend redesign with focused reporting API additions. Reuse the database, deterministic generator, policies, LangChain/OpenRouter roles, mock adapters, eligibility checks, and approval/audit workflows. Deployment remains Next.js plus FastAPI in two Vercel projects, backed by managed Postgres when account access is available.

## 2. Sources and boundaries

- The client engagement PDF remains the source for company facts.
- The three existing feature SOT documents in this folder govern feature behavior.
- The supplied image governs visual direction and layout inspiration. Its numbers, menu entries, and model-health claims are not product requirements or measured results.
- Keep brief facts, generated operating records, measured demo runs, and evaluation results labeled distinctly.
- The broader AI Observability, Cost Intelligence, Guardrail Control Center, and Evaluation Lab from the image remain a separately agreed expansion. Existing case traces and available cost information will be presented clearly in this redesign.

## 3. Information architecture and page composition

| Primary section | Views inside the section | Main working layout |
|---|---|---|
| Overview | Command Center; Demo data and rules inspector | Summary metrics, a varied chart grid, team attention queues, source/rule details |
| CX Support | Inbox; Human Review; Workflow; Analytics | Inbox: queue → conversation and actions → facts/policy. Human Review: pending work and reason. Workflow: selected-case graph and step details. Analytics: filtered aggregates |
| Review Intelligence | Signals; Investigations; product evidence detail | Trends and issue concentration above a product table; selected product opens evidence and investigation controls |
| Catalog Velocity Engine | Pipeline; Drop Readiness; Vendor Intake; product detail | Readiness and blocker charts above a product pipeline; selected SKU opens imagery, attributes, provenance, QA and approval |

Keep existing root URLs (`/`, `/cx`, `/reviews`, `/catalog`). Use URL parameters for selected view, record, filters and date range so refresh/back navigation preserves context and a selected case or product can be shared. The four primary items stay visible; secondary views use tabs beneath the page title.

The shared header contains the current workspace and demo status. Search is scoped to the active section in this release: case/order/customer in CX, product/SKU in Reviews, and SKU/vendor/product in Catalog. Search must query the full available dataset rather than only the first loaded page.

## 4. Visual system

Create reusable tokens for navy surfaces, purple actions, lavender canvas, borders, text, spacing, radii and shadows. Green indicates verified/successful, amber indicates attention, and red indicates blocked/error. Purple identifies selected UI and AI interpretation. All statuses also include text or icons.

- Body text should remain readable at normal browser zoom; target 14–16px for working content and at least 12px for secondary labels.
- Use a consistent type scale, restrained card titles, aligned numerical values, and clear primary/secondary actions.
- Chart categories have a stable shared palette; preserve category colours when filters change. Reserve semantic status colours for status charts.
- Sidebar shows the current section explicitly. The mobile layout uses compact accessible navigation.
- Separate AI interpretation, verified commerce facts, and policy eligibility in the case panel.
- Show environment/model availability truthfully. A configured model is not automatically a healthy or measured model.
- Add skeleton, empty, partial-data, error, disabled, processing and success states to shared components.
- Respect reduced motion. Use short transitions for navigation and panel changes; avoid decorative animation in analytical charts.

## 5. Chart and graph plan

The table defines the initial chart set. Visual previews may adjust placement or replace a chart with a clearer equivalent while retaining its business question and data contract. Aim for three complementary charts on each analytical landing view, with additional detail available through drill-downs.

| Dashboard/view | Chart or graph | Question answered | Data and interaction |
|---|---|---|---|
| Overview | Stacked area chart: case intake by day and channel | How is support demand distributed over the demo period? | Ticket timestamps/channel; select a day/channel to open the filtered CX inbox |
| Overview | Donut: support intent mix | What makes up the support workload? | Explicitly labeled synthetic seed categories; centre shows the case denominator; legend shows counts and percentages |
| Overview | Segmented horizontal bars: readiness by upcoming drop | Which drop needs listing attention? | Product target drop and canonical readiness; select a segment to open matching SKUs |
| CX Analytics | Horizontal ranked bars: detected intents | Which request types are consuming attention? | Latest run per case in the selected scope; unprocessed cases remain a separate count |
| CX Analytics | Stacked columns: case outcomes over time | How are simulated sends, human review and escalation changing? | Mutually exclusive latest outcome per case; filters open the corresponding case queue |
| CX Analytics | Histogram: model confidence | Where is the classifier uncertain? | Model-produced confidence only; deterministic rule scores are excluded; show sample count or an unavailable state |
| CX Workflow | Directed process graph with selectable nodes | What happened to this case, and why did it stop? | Stored trace stages; stage details show facts, rules and model metadata; missing stage duration stays unavailable |
| Review Signals | Line chart: selected issue prevalence over time | Is a product issue becoming more common? | Distinct reviews containing that issue / all reviews in each bucket; show numerator, denominator and sparse-sample indicators |
| Review Signals | Heatmap: category × issue | Where are issues concentrated? | Distinct review counts or rates, with an explicit toggle and legend; cells drill into supporting products/reviews |
| Review Signals | Grouped bars: sentiment by category | How do feedback patterns differ across categories? | Positive/negative/mixed/unknown from the stored extraction source; do not silently substitute star rating for sentiment |
| Catalog Drop Readiness | Stacked bars: ready, needs review and blocked by drop | How much of each drop is ready? | Product readiness, using one shared deterministic definition across cards, charts and tables |
| Catalog Pipeline | Ranked horizontal bars: blockers | Which missing inputs affect the most SKUs? | Count each SKU once per blocker; disclose that one SKU can have multiple blockers |
| Catalog product/drop detail | Workflow timeline: milestones and elapsed stages | Where has a SKU spent time, and what is incomplete? | PO/sample/image/approval timestamps; only draw known events; open stages are marked ongoing |
| Catalog vendor detail | Dot plot: specification completeness by vendor | Which vendors need follow-up for missing input? | Fraction of required input fields present, with field/SKU denominators; not a vendor quality or causation score |

**Chart behavior:** every chart has a title, unit, time window, sample count, tooltip, legend where needed, and an accessible table alternative. Selected filters affect both the chart and its detail table. Charts resize without clipped labels. Empty measurements display an explanation rather than a fabricated series.

Do not use a funnel for unrelated counts, add a second y-axis merely to fit more metrics, or show unsupported financial/quality scores. A workflow graph is a record of stored execution unless live progress events have actually been implemented.

## 6. Reporting and data work needed

The current APIs expose most case, policy, review evidence and product detail needed for the new layouts. The additional work is focused on aggregated views and consistent filtering.

| Area | Existing support | Planned change |
|---|---|---|
| Overview | Counts, client context, policy metadata and basic cost summary | Add time-bucketed intake, intent composition and drop summaries; provide source/denominator metadata |
| CX inbox | Ticket list/detail, run, decision and audit endpoints | Add search, channel/outcome/intent/date filters, stable pagination, correct filtered totals, and customer display data |
| CX Human Review | Approval/escalation decisions exist in runs | Add a query for latest pending runs in the selected demo-session scope; separate actionable review from unprocessed cases |
| CX Analytics | Runs contain intent, outcome, trace and model-call metadata | Aggregate latest runs per ticket/session; expose outcome buckets and model-confidence samples; keep all-time and date-filtered counts explicit |
| Workflow | Per-case trace is persisted | Normalize steps for graph rendering; expose existing timing/tokens/cost. Add stage instrumentation only where approved detail requires it |
| Review Signals | Product summaries and individual evidence | Add date/category/issue filtering, distinct-review trend buckets, heatmap cells and full paginated evidence |
| Catalog | Product data, blockers, milestones, provenance and target drops | Reuse a common readiness computation for all views; add milestone/completeness aggregates and filters |

Proposed read endpoints: `GET /overview/analytics`, `GET /cx/analytics`, `GET /cx/review-queue`, `GET /reviews/analytics`, and `GET /catalog/analytics`. Extend existing list endpoints where possible. These names become final when the visual previews and fields are approved.

Responses should include typed metadata such as `source_kind`, `as_of`, `timezone`, `window`, `sample_count`, `total_count`, `excluded_count` and `unavailable_reason`. Use Pydantic response models and regenerate OpenAPI frontend types rather than duplicating response shapes by hand.

### Metric integrity requirements

1. Use the fixed demo clock for seeded operational windows and actual execution timestamps for measured run windows. Show which period is selected; do not silently mix them.
2. Keep generated category labels separate from model predictions and held-out evaluation answers. Never use expected labels to claim model accuracy.
3. Scope run-based analytics consistently with the case queue. The current global run counts can include evaluation sessions; exclude those sessions from operational dashboards by default.
4. Count one latest outcome per case for workload charts. Count execution attempts separately only when the chart explicitly says runs/attempts.
5. Compute review issue prevalence using distinct reviews. Multi-issue reviews may contribute to several issue series; disclose this and show sample sizes.
6. Validate low-sample rules for both current and comparison periods before showing trend alerts. Preserve uncertainty when comparison data is insufficient.
7. Keep catalog readiness and blocker definitions identical in the summary, chart, SKU table and approval checks.
8. For money, distinguish token-based cost estimates from provider-reported charges. Use USD initially; any INR display requires an explicit conversion rate, source/date and estimate label. Do not display an unknown model's cost as free.
9. Use the existing seed wherever possible. If a reviewed chart genuinely needs additional history, extend the deterministic generator under a new version and label it synthetic. Never add arbitrary chart arrays detached from records.

## 7. Delivery phases and approval gates

### Phase 1 — Visual previews before application changes

Create desktop previews of **Overview** and **CX Support Inbox**, plus a mobile adaptation. Include the varied Overview chart grid and the CX queue/conversation/evidence layout. Show a normal case and an approval/blocked state so the design covers actual work. Supply a compact palette/component sheet.

**User gate:** approve layout, density, typography, colour, chart hierarchy and case-panel behavior. Application UI changes begin after this visual approval. The design direction already approved does not need to be re-approved.

### Phase 2 — Shared shell and components

Implement the navigation shell, header, tokens, page titles, cards, status badges, buttons, tabs, tables, filters, detail panels and shared chart wrappers. Break the current large page components into focused presentation components and data hooks. Preserve existing routes and actions.

**Completion evidence:** approved shell reproduced at desktop/tablet/mobile widths, visible keyboard focus, readable contrast, and reusable empty/error/loading states.

### Phase 3 — Overview and reporting contracts

Add the reviewed analytics response contracts and server aggregation functions. Implement summary cards, the mixed chart grid, clickable team priorities, client context cards, and the Demo data and rules inspector. Dates and source labels must be present from the first working version.

**Completion evidence:** chart totals match underlying queries; chart selections lead to correctly filtered detail views; no unmeasured model figures appear.

### Phase 4 — CX workspaces

Build the three-column Inbox, Human Review view and stored-execution Workflow graph. Wire conversation history, proposed reply, ownership evidence, policy, reason codes, audit and action eligibility into the layout. Add Analytics using the agreed bar/column/histogram charts. Filters and selection survive refresh/back navigation.

Keep core-intent coverage across WISMO, returns/exchanges, refunds, cancellation, payment and product/policy questions. Mobile shows queue, conversation and evidence as accessible selectable panels. Approval controls reflect the API's permitted decisions and prevent duplicate submissions while a request is pending.

**Completion evidence:** normal WISMO, return/cancellation approval, wrong customer, missing policy, carrier timeout, stale tracking and injection cases remain correct and understandable in the new UI.

### Phase 5 — Review Intelligence

Build trend, heatmap and sentiment views; connect all selections to product-level evidence. Keep review text, evidence spans, extraction source, issue counts and investigation status easy to inspect. Allow the team to choose an issue and update an investigation using the existing backend capabilities.

**Completion evidence:** low-information and low-sample cases render honestly; each alert/trend can be traced to review records; vendor comparisons do not imply causation.

### Phase 6 — Catalog Velocity Engine

Build drop readiness, blocker analysis, milestone timelines and vendor completeness views. Redesign the product table and detail workspace for imagery, raw/canonical attributes, provenance, corrections, QA, copy review and export approval. Preserve atomic CSV validation and visible row errors.

**Completion evidence:** chart/table counts agree, missing inputs remain visible, corrected values retain provenance, and blocked SKUs cannot be approved for export.

### Phase 7 — Final visual and functional review

Complete responsive behavior, accessibility, loading/failure states and relevant regression tests. Update the README, build note and verification record with the new navigation, chart definitions and screenshots. Deploy the approved build once the previously requested GitHub/Vercel/Postgres access is supplied.

**User gate:** review the completed four sections against the approved previews and run the acceptance scenarios below. Record any visual adjustments and the deployed commit.

## 8. Expected code areas

- `web/app/layout.tsx` and `web/app/styles.css`: shared shell and visual tokens.
- `web/components/ui.tsx`, plus new focused `layout`, `charts`, `tables` and `panels` components: reusable presentation.
- `web/app/page.tsx`, `web/app/cx/page.tsx`, `web/app/reviews/page.tsx`, `web/app/catalog/page.tsx`: section composition and secondary views.
- `web/lib/api.ts` and generated OpenAPI types: typed filters, results and chart metadata.
- `api/dhaga/main.py` and a focused analytics module: query/aggregation endpoints and filtered pagination.
- `api/dhaga/logic.py` and `api/dhaga/workflows.py`: only the shared result metadata/readiness helpers needed for consistent presentation; preserve policy enforcement.
- Migrations or seed changes only when an approved view requires data that is not already persisted. Add migrations for schema changes rather than rewriting an applied migration.

Choose one shared chart rendering approach during implementation and verify its supported APIs before adoption. Workflow nodes can use a small SVG diagram if that satisfies the approved interaction; a full graph editor is unnecessary for viewing a stored trace.

## 9. Review and acceptance

**Codex:** check aggregate arithmetic against records; date boundaries and sample denominators; filtered totals and pagination; session/evaluation exclusion; null-cost and unavailable-data handling; readiness consistency; existing approval/guardrail tests; frontend types/build; browser navigation and selected-case actions. Inspect 1440px, 1024px and approximately 390px layouts, keyboard navigation, chart table alternatives, and error/retry states. Save visual evidence for the final review.

**User:** compare the result to the approved previews; judge readability and the mix of charts; use a chart to reach its underlying records; run normal WISMO and a human approval; inspect a blocked case's facts/policy/reason; investigate a review trend; resolve a catalog input issue and confirm remaining blockers; review the mobile layout.

**Together:** confirm the GitHub commit and deployed version match, check a fresh-session flow, repeat the README start, and rehearse the presentation with brief facts, synthetic records and measured model results identified clearly.

## Execution update — 4 October 2026

The user authorized implementation after validating the visual direction. The local redesign is implemented and verified; see UI_REDESIGN_VERIFICATION.md and design-qa.md. The original preview gate is superseded by that authorization. GitHub import, Vercel deployment and the final PowerPoint are now authorized follow-on deliverables, performed after the local gate.

Reporting uses one typed /dashboard aggregation contract alongside existing resource endpoints. Review charts use the seeded date range with weekly buckets and selected-issue prevalence; arbitrary date-window filtering is a future extension. Session outcomes use a donut alongside language bars and a real-sample confidence histogram. These are explicit implementation adaptations of the proposed chart mix. A dedicated observability/evaluation suite remains future scope.

