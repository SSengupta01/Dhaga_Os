# UI redesign — local verification

Date: 4 October 2026. Scope: the user-approved visual direction, preserving the existing four-section product and simulated actions.

## Delivered locally

- Shared navy navigation, purple active states, lavender canvas, white cards, semantic badges, keyboard focus, responsive grids and mobile navigation.
- Overview: source-backed intake area chart, intent donut with queue drilldown, team priorities, separately cited client facts, demo rules and measured-cost boundary.
- CX: searchable/paginated queue, channel and synthetic-intent filters, URL-selected cases/views, conversation/evidence workspace, approve/edit/escalate, audit history, selectable execution steps, human-review queue and measured analytics. Mobile has Queue, Conversation and Evidence panels.
- Reviews: weekly lines, selected-issue prevalence with sparse-week suppression, sentiment grouped columns, issue heatmap, evidence drilldown, investigation creation/status/notes.
- Catalog: pipeline filters, readiness stacked columns, blocker bars, vendor completeness dots, recorded milestones, provenance, normalization, QA, corrections, guarded copy, export approval/download, CSV validation/import.
- Backend: typed dashboard schema and generated frontend contract; session-scoped latest outcomes/costs; accurate filtered ticket totals; consistent catalog readiness; both review comparison periods require five samples; unknown model prices remain unavailable.

## Executed checks

- Production frontend build: passed (Next.js 16.3.8).
- TypeScript: passed.
- Python: 16 tests passed, including aggregate totals, session isolation, filter counts, evidence filtering, readiness consistency and normalization.
- Browser: all four sections loaded; normal WISMO facts/response; eligible return approval and audit; wrong-customer block; carrier-timeout escalation; workflow explorer; review heatmap drilldown, investigation creation/status; blocked catalog export rejection; catalog normalization; mobile conversation/evidence navigation.
- Console: no browser errors in final clean navigation. Expected failed action requests are presented as actionable messages.
- Responsive viewport requests: 1440x960, 1024x900, 390x844. Browser zoom produced approximately 1309x873, 931x818, 354x767 CSS pixels. No page-wide horizontal overflow in measured layouts; dense tables scroll inside their cards.

## Explicit boundaries

This is an operational synthetic demo. Live model generation is unavailable without an OpenRouter key. No live carrier, helpdesk, refund, payment or catalog write occurs. Review and catalog mutations share the demo database. Dates come from the fixed seed timeline, not a claimed live feed. Cost projections are unavailable until complete priced model samples exist. The reference collage's invented accuracy/latency/cost numbers were not copied.

## User review

1. Open Overview and inspect source labels, chart data tables and demo policy pack.
2. Follow the WISMO donut into the queue; open TKT00001 and inspect facts and workflow.
3. In a fresh browser session run TKT00004 and approve its return; inspect audit history.
4. Run TKT00002, TKT00003 and TKT00014; confirm approval is blocked and a reason is shown.
5. Click a review heatmap cell, open product evidence, create an investigation and save a decision.
6. Inspect a blocked SKU, correct a supported input, run QA, and verify remaining blockers. Validate CSV intake.
7. Inspect mobile Queue / Conversation / Evidence and the four primary navigation entries.

Deployment and presentation are the next authorized steps after this local gate. They are tracked separately from local verification.
