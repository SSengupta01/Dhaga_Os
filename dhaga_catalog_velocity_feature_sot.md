# Dhaga-OS — Catalog Velocity & Category Visibility Feature

**Document Type:** Feature Source of Truth (SOT) / Codex Build Context  
**Product:** Dhaga-OS  
**Feature:** Catalog Velocity & Category Visibility  
**Primary Business Problem:** Sample-to-live cycle is 6–9 days because catalog creation starts late, depends on manual entry of ~60 attributes per SKU, manual copywriting, fragmented vendor inputs, and manual QA.  
**Primary Users:** Listing Lead, Listing Team, Category Head, Merchandising, Sourcing, Operations  
**Secondary Users:** CTO, Data Analyst, Vendor/Sourcing Managers  
**Status:** Ready for MVP design and Codex implementation planning

---

# 1. Feature Purpose

Build a focused Dhaga-OS capability that reduces catalog creation latency by moving product setup upstream, normalizing messy vendor/product data, generating controlled product copy, validating catalog readiness, and surfacing drop-risk before Tuesday/Friday collection launches.

This feature is not a full vendor-management suite. Vendor functionality is included only where it directly improves catalog speed, data completeness, or listing quality.

The intended operating model is:

```text
PO confirmed / product identified
        ↓
Digital product draft created early
        ↓
Vendor/spec data ingested
        ↓
Attributes normalized and validated
        ↓
Sample + photoshoot progress tracked
        ↓
Images attached
        ↓
AI-assisted enrichment + copy generation
        ↓
Deterministic QA + evaluator checks
        ↓
Human review only where required
        ↓
Ready-to-publish catalog record
        ↓
Product live
```

The core product principle is:

> Shift the listing team from manual construction of every listing to exception-based review, correction, approval, and publishing.

---

# 2. Source-of-Truth Business Context

Use the following client facts as fixed constraints for this feature:

- Dhaga & Co. carries roughly **14,000 live SKUs**.
- Roughly **400 new SKUs** arrive each week.
- New collections drop on **Tuesday and Friday**.
- A product that has not sold in six weeks is pulled, so launch timing matters.
- A **six-person listing team** manually types attributes into an internal admin and writes product copy by hand.
- Sample-to-live currently takes **6–9 days**.
- Catalogue records have roughly **60 attributes each**.
- Colour has been entered in about **90 different ways**.
- Fabric is free text.
- Size charts differ by vendor.
- About **200 product descriptions per week** are manually written by four people.
- Tone varies between writers and older listings were not consistently revisited.
- Vendor purchase orders are split across spreadsheets and WhatsApp confirmations.
- Around forty vendor partners are used.
- Dhaga has sixteen engineers and no ML engineer, so the solution must remain operable by a small team.
- The MVP must use realistic input and visibly handle failures.

Do not invent exact values for the full 60-field catalog schema, current internal admin API, workflow timestamps, vendor system, or publishing endpoint unless provided later. Treat those as discovery dependencies.

---

# 3. Problem Statement

## Client-language problem

Dhaga processes around 400 new SKUs per week, but its catalog workflow starts too late and relies on a six-person listing team to manually enter dozens of attributes and write product copy after sample and studio processing. This contributes to a 6–9 day sample-to-live cycle and creates a risk of missing Tuesday and Friday collection drops.

## Underlying operational problem

The delay is not one task. It is a pipeline problem composed of:

1. product information arriving late or in inconsistent formats;
2. no canonical product record created early;
3. repeated manual entry of structured attributes;
4. messy taxonomy and vendor naming;
5. manual product copy generation;
6. manual checks for missing/conflicting fields;
7. unclear ownership of blockers;
8. no single view of catalog readiness or launch risk.

## What not to do

Do not solve this first by building a large vendor-management system. A large VMS may improve procurement governance but does not automatically reduce sample-to-live time.

Instead, include a **Vendor Product Intake** capability only where it accelerates product creation or improves catalog completeness.

---

# 4. Product Goal

Create a **Catalog Velocity Engine** that can:

1. create digital product drafts before samples are fully processed;
2. ingest vendor/product data from CSV/Excel/manual entry;
3. map messy values into canonical taxonomy;
4. identify missing mandatory attributes;
5. attach and process product images after the photoshoot;
6. generate controlled product descriptions and merchandising metadata;
7. detect contradictions and unsupported claims;
8. calculate catalog readiness using deterministic rules;
9. expose blocked/at-risk products in an operational queue;
10. show Tuesday/Friday drop readiness;
11. allow listing staff to approve/correct exceptions;
12. retain evidence and auditability for every AI-generated field.

---

# 5. Primary User Personas

## 5.1 Listing Lead

Primary operator and likely MVP owner.

Needs to know:

- Which products are ready?
- Which products are blocked?
- Why are they blocked?
- What must the team fix now?
- Which SKUs are at risk of missing the next drop?
- Where in the workflow is time being lost?

## 5.2 Listing Team

Moves from manual data-entry mode to review/approval mode.

Needs:

- pre-filled product records;
- highlighted missing fields;
- suggested normalized values;
- generated copy;
- visible evidence/source values;
- conflict resolution actions;
- ability to edit before approval.

## 5.3 Category Head / Merchandising

Needs:

- portfolio readiness for upcoming drop;
- products blocked by catalog issue;
- category-level delay patterns;
- product quality/completeness overview;
- clear view of whether a drop is launch-ready.

## 5.4 Sourcing / Vendor Operations

Needs:

- visibility into vendors repeatedly submitting incomplete or inconsistent product data;
- missing size charts/specifications;
- vendor-caused catalog delay signals;
- optional follow-up workflow for missing data.

---

# 6. Core Product Experience

The feature should feel like an **operations workspace**, not an AI chatbot.

Primary navigation:

```text
Overview
Products
Product Detail
Drop Readiness
Blocked / Needs Review
Vendor Intake
Taxonomy
Settings / Rules
```

Optional later pages:

```text
Vendor Performance
Workflow Analytics
Audit Logs
Templates
```

---

# 7. End-to-End Workflow

```text
Vendor / Internal Product Source
        ↓
PO confirmed or SKU identified
        ↓
Create Draft Product Record
        ↓
Ingest raw product specification
        ↓
Validate required identifiers
        ↓
Normalize known aliases deterministically
        ↓
Route unknown/messy values to LLM mapper
        ↓
Validate structured model output
        ↓
Create canonical product record
        ↓
Identify missing mandatory fields
        ↓
Create tasks / blockers for missing data
        ↓
Track sample arrival
        ↓
Track photoshoot
        ↓
Attach studio images
        ↓
Image-supported attribute suggestions
        ↓
Conflict detection
        ↓
Generate controlled product copy
        ↓
Evaluator + deterministic factual checks
        ↓
Catalog QA
        ↓
Calculate readiness score
        ↓
Ready / Needs Review / Blocked
        ↓
Human approval
        ↓
Export / Publish-ready payload
        ↓
Product live
        ↓
Log publication timestamp
```

---

# 8. Critical Pre-Implementation Discovery

Before coding production logic, obtain or create representative samples of the following.

## 8.1 Required real or realistic datasets

### A. Product master / internal catalog export

Minimum fields needed:

- product_id
- sku
- vendor_id if available
- category
- subcategory
- existing attributes
- title
- description
- status
- live date
- created date

Need at least a realistic sample of the actual 60-field schema.

### B. Vendor product specification files

Representative inputs from multiple vendors, including:

- Excel sheets;
- Google Sheet-like exports;
- inconsistent column names;
- missing fields;
- raw colour names;
- free-text fabric descriptions;
- size-chart references;
- vendor SKUs;
- product names.

### C. Product images

For realistic MVP testing:

- multiple categories;
- different backgrounds;
- full-body and close-up shots;
- duplicate images;
- missing image cases;
- ambiguous colours;
- corrupted or unsupported file cases.

### D. Existing product-copy examples

Needed to define:

- Dhaga tone;
- title style;
- description length;
- bullets;
- prohibited claims;
- occasion language;
- category conventions.

### E. Taxonomy dictionary

At minimum:

- canonical colours;
- canonical fabrics;
- categories;
- subcategories;
- sleeve types;
- neck styles;
- patterns;
- fit types;
- occasion tags;
- size names.

### F. Workflow timestamps

If available, obtain:

- po_confirmed_at
- sample_dispatched_at
- sample_received_at
- shoot_started_at
- shoot_completed_at
- images_ready_at
- catalog_started_at
- catalog_completed_at
- qa_started_at
- qa_completed_at
- published_at

These timestamps are required to prove where the 6–9 day cycle is actually spent.

### G. Publishing constraints

Need to know:

- internal admin APIs if any;
- CSV upload format;
- mandatory fields;
- image requirements;
- validation rules;
- approval workflow;
- whether the MVP will publish directly or only create a publish-ready payload.

For the MVP, direct production publishing is not required unless a safe sandbox endpoint exists.

---

# 9. Recommended MVP Dataset

Use at least **50 realistic SKUs** across multiple vendors/categories.

Recommended demo set:

- 50 SKUs;
- 3–5 vendors;
- 5–8 categories/subcategories;
- complete and incomplete products;
- known and unknown colours;
- clean and messy fabric text;
- valid and invalid size charts;
- missing images;
- conflicting image/text colours;
- duplicate SKU;
- copy-generation edge cases.

Do not use only three curated rows.

---

# 10. Canonical Product Data Model

The exact Dhaga schema must be learned from the client. For the MVP, use an extensible structure.

```yaml
Product:
  product_id: string
  sku: string
  vendor_id: string | null
  vendor_sku: string | null
  status: enum
  target_drop_date: date | null

  category:
    raw: string | null
    canonical: string | null
    confidence: float | null

  subcategory:
    raw: string | null
    canonical: string | null
    confidence: float | null

  attributes:
    colour:
      raw: string | null
      canonical: string | null
      confidence: float | null
      source: enum
    fabric:
      raw: string | null
      canonical: string | null
      confidence: float | null
      source: enum
    sleeve_type: object
    neck_type: object
    pattern: object
    fit: object
    occasion: object
    wash_care: object
    country_of_origin: object
    measurements: object
    size_chart: object

  pricing:
    mrp: decimal | null
    cost: decimal | null

  images:
    - image_id: string
      url: string
      status: enum
      metadata: object

  generated_copy:
    title: string | null
    short_description: string | null
    long_description: string | null
    bullets: array
    search_keywords: array
    occasion_aliases: array

  readiness:
    score: integer
    status: enum
    blockers: array
    warnings: array

  audit:
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | null
    published_at: datetime | null
```

---

# 11. Data Provenance Model

Every important field must retain provenance.

Example:

```json
{
  "field": "colour",
  "raw_value": "Dark Wine",
  "canonical_value": "Maroon",
  "source": "vendor_csv",
  "resolution_method": "llm_normalization",
  "confidence": 0.94,
  "human_approved": true,
  "approved_by": "user_123",
  "approved_at": "2026-10-03T12:00:00Z"
}
```

Allowed source types:

```text
vendor_csv
vendor_manual
internal_admin
image_model
llm_inference
human_edit
rule_engine
legacy_catalog
```

This is mandatory for auditability and conflict resolution.

---

# 12. Vendor Product Intake

Do not build a complete vendor-management system initially.

Build only the minimum intake capability required for catalog creation.

## Inputs

- CSV upload;
- Excel upload;
- manual entry;
- optional paste-from-sheet;
- later: vendor portal/API.

## Intake steps

```text
Upload
  ↓
Detect columns
  ↓
Map source columns → canonical schema
  ↓
Validate required identifiers
  ↓
Validate data types
  ↓
Store raw payload
  ↓
Normalize values
  ↓
Create product drafts
  ↓
Show intake report
```

Example intake summary:

```text
50 rows received
47 valid product IDs
3 rows blocked
2 duplicate SKUs
41 colour values matched deterministically
7 mapped by model
2 require human review
```

---

# 13. Taxonomy Normalization Engine

## Objective

Convert inconsistent vendor/internal values into controlled canonical attributes without destroying raw source data.

## Resolution strategy

```text
Raw value
   ↓
Exact canonical match?
   ├─ Yes → deterministic mapping
   ↓ No
Alias dictionary match?
   ├─ Yes → deterministic mapping
   ↓ No
Fuzzy deterministic match above threshold?
   ├─ Yes → suggestion + confidence
   ↓ No
LLM structured normalization
   ↓
Schema validation
   ↓
Confidence threshold
   ├─ High → accept as suggested value
   └─ Low  → human review
```

## Example

```text
burgandy → Burgundy
wine red → Maroon
3 quarter → Three-quarter Sleeve
cottn → Cotton
```

The production taxonomy itself must be approved by Dhaga. The model must not invent new canonical categories automatically.

---

# 14. Controlled Attribute Taxonomy

Create versioned dictionaries.

Suggested MVP taxonomy groups:

```text
COLOUR
FABRIC
CATEGORY
SUBCATEGORY
PATTERN
SLEEVE TYPE
NECK TYPE
FIT
LENGTH
OCCASION
SIZE
WASH CARE
```

Every taxonomy table should support:

```text
canonical_id
canonical_label
aliases[]
active
version
created_at
updated_at
```

Do not overwrite raw values.

---

# 15. AI-Assisted Attribute Enrichment

Use image/text inference only for attributes that can reasonably be observed or inferred.

## Candidate attributes

Potentially safe as suggestions:

- visible colour;
- garment category;
- sleeve type;
- neck style;
- visible pattern;
- silhouette;
- visible length class;
- occasion suggestion.

## Attributes that must never be guessed from image alone

- exact fabric composition;
- material percentages;
- GSM;
- exact measurement values;
- MRP;
- cost;
- vendor;
- country of origin;
- wash-care instructions;
- inventory;
- compliance values.

If source evidence is absent, return null and a blocker/warning.

Example:

```json
{
  "fabric": null,
  "status": "MISSING_REQUIRED_DATA",
  "reason": "No authoritative source provided"
}
```

---

# 16. Attribute Conflict Engine

Detect contradictions among vendor data, legacy catalog, image inference, and human edits.

Example:

```text
Vendor colour: Navy
Image suggestion: Black
```

System output:

```text
Conflict: COLOUR
Authoritative source: not resolved
Action: Human review required
```

Conflict rule priority must be configurable.

Suggested initial hierarchy:

```text
human-approved source
    > authoritative vendor spec
    > existing verified catalog
    > deterministic inference
    > model/image suggestion
```

Do not silently overwrite authoritative values.

---

# 17. Product Copy Generation

## Inputs

- canonical product attributes;
- approved brand/tone rules;
- approved vocabulary;
- category-specific template;
- optional product images;
- occasion tags;
- search-language requirements.

## Outputs

```json
{
  "title": "...",
  "short_description": "...",
  "long_description": "...",
  "bullets": ["..."],
  "search_keywords": ["..."],
  "occasion_aliases": ["..."]
}
```

## Generation requirements

- never invent unsupported product facts;
- no claims about fabric, comfort, breathability, durability, etc. unless supported by approved attributes;
- preserve brand tone;
- consistent style across categories;
- output structured schema;
- generation temperature lower than creative marketing copy if factual fidelity is the priority;
- all generated copy must remain editable by humans.

---

# 18. Factual Claim Guardrail

Every factual phrase in generated copy should map to a structured attribute or approved inference.

Bad:

```text
Made from breathable pure cotton.
```

when fabric source is missing.

Allowed:

```text
Floral kurti with three-quarter sleeves.
```

if those values are verified.

Recommended implementation:

```text
Generated copy
   ↓
Claim extractor
   ↓
Claim-to-attribute verifier
   ↓
Unsupported claim?
   ├─ Yes → reject / regenerate
   └─ No  → continue
```

---

# 19. Catalog QA Engine

Catalog QA should combine deterministic validation and model-based evaluation.

## Deterministic checks

- SKU present;
- duplicate SKU detection;
- mandatory field completion;
- valid taxonomy values;
- price type/range checks;
- image count requirement;
- image format validation;
- size chart requirement;
- required compliance fields;
- target drop assigned where required;
- product title length;
- unsupported nulls;
- data-type constraints;
- payload schema validation.

## Model/evaluator checks

- inconsistent copy vs attributes;
- unsupported language claims;
- confusing or low-quality description;
- inappropriate occasion suggestion;
- possible image/attribute contradiction;
- tone mismatch.

## QA output

```json
{
  "status": "NEEDS_REVIEW",
  "errors": [],
  "warnings": [],
  "model_findings": [],
  "blocking_count": 2,
  "warning_count": 3
}
```

---

# 20. Catalog Readiness Score

The score must be deterministic and explainable.

Example components:

```text
Identity / SKU                10
Core product attributes       20
Vendor attributes             10
Images                        15
Size / measurement data       15
Taxonomy validity             10
Copy generated + validated    10
QA / compliance               10
--------------------------------
Total                         100
```

The exact weights are configurable.

Initial status logic:

```text
>=95  → READY FOR APPROVAL
80–94 → NEEDS REVIEW
<80   → BLOCKED
```

A product can also be BLOCKED regardless of score if a critical required field is missing.

Critical blocker examples:

- missing SKU;
- missing MRP;
- missing required size chart;
- no publishable image;
- invalid category;
- unsupported compliance field;
- unresolved critical conflict.

---

# 21. Catalog Command Center

Main operational overview.

Example cards:

```text
Weekly SKUs: 400
Ready: 248
Needs Review: 72
Blocked: 38
Photoshoot Pending: 42
```

Pipeline visualization:

```text
Intake
Sample Awaited
Photoshoot
Images Ready
AI Processing
Human Review
Ready to Publish
Live
Blocked
```

Each stage must be clickable/filterable.

---

# 22. Product List View

Recommended columns:

```text
SKU
Product Name
Category
Vendor
Target Drop
Current Stage
Readiness Score
Missing Fields
Warnings
Blockers
Time in Stage
Drop Risk
Assignee
Last Updated
```

Filters:

```text
Target Drop
Status
Vendor
Category
Readiness
Blocked reason
Stage
Assignee
Risk
```

---

# 23. Product Detail View

Sections:

```text
Header / identifiers
Workflow timeline
Raw vendor inputs
Canonical attributes
Images
AI suggestions
Generated copy
QA findings
Readiness score
Conflicts
Audit history
Actions
```

Actions:

```text
Approve value
Reject suggestion
Edit field
Regenerate copy
Resolve conflict
Mark blocker resolved
Approve product
Export publish payload
```

---

# 24. Tuesday / Friday Drop Readiness

This should be a first-class view because launch timing is commercially important.

Example:

```text
Tuesday Drop
205 target SKUs
187 ready
18 at risk
```

At-risk breakdown:

```text
7 missing vendor data
5 photoshoot pending
4 QA conflicts
2 missing size chart
```

For each SKU show:

```text
Target Drop
Current Stage
Time Remaining
Expected Remaining Time
Risk Status
Primary Blocker
Owner
```

---

# 25. Drop-Risk Engine

Do not use an LLM for the core risk calculation.

Use deterministic workflow data.

Inputs can include:

```text
current stage
time in current stage
time remaining until target drop
historical median stage completion time
number of blockers
critical blocker presence
```

MVP rule example:

```text
IF expected_remaining_time > time_until_drop
THEN risk = HIGH
```

Future version may use historical prediction models once enough reliable workflow data exists.

---

# 26. Workflow Instrumentation

Do not promise that 6–9 days will become 3–4 days without measuring the current stages.

Store timestamps for every state transition.

Required events:

```text
product_draft_created
vendor_data_received
sample_dispatched
sample_received
shoot_started
shoot_completed
images_ready
normalization_completed
copy_generated
qa_started
qa_completed
human_review_started
human_review_completed
publish_ready
published
```

From these compute:

```text
PO → Sample Received
Sample Received → Shoot Start
Shoot Start → Images Ready
Images Ready → Catalog Ready
Catalog Ready → QA Complete
QA Complete → Published
Total Sample → Live
```

Metrics must include P50 and P90, not only averages.

---

# 27. Operational Analytics

Track:

- P50 sample-to-live;
- P90 sample-to-live;
- time per stage;
- percentage of SKUs ready before target drop;
- average manual touches per SKU;
- percentage fields auto-normalized;
- percentage fields requiring human review;
- taxonomy mapping accuracy;
- copy acceptance rate;
- QA failure rate;
- blocker categories;
- vendor completeness rate;
- catalog correction rate after generation.

These are stronger success metrics than “number of AI descriptions generated.”

---

# 28. Vendor Visibility — Scope for This Feature

Vendor functionality should answer only catalog-relevant questions.

MVP vendor metrics:

```text
Vendor
Products submitted
Average attribute completeness
Missing size-chart rate
Unknown taxonomy values
Average catalog blocker count
Average time to provide missing data
Products delayed by vendor-data issue
```

Do not include contracts, payments, invoicing, full PO lifecycle, vendor settlement, or procurement approvals in this feature unless explicitly requested later.

---

# 29. Future Vendor Performance View

Later, after Catalog Velocity and Review Intelligence exist, combine:

```text
Vendor
  ↓
Product intake quality
  ↓
Catalog delay
  ↓
Product review complaints
  ↓
Return reasons
  ↓
Vendor quality intelligence
```

Example future dashboard metrics:

```text
POs supplied
Average missing attributes
Average sample delay
Catalog correction rate
Size-chart mismatch count
Return rate
Fit complaint rate
```

Do not implement this full view in MVP unless data is available.

---

# 30. AI vs Deterministic Responsibility

| Task | Method |
|---|---|
| SKU lookup | deterministic code / SQL |
| required-field validation | deterministic |
| duplicate detection | deterministic |
| pricing validation | deterministic |
| taxonomy alias match | deterministic |
| readiness score | deterministic |
| deadline calculation | deterministic |
| drop-risk threshold | deterministic |
| unknown colour normalization | LLM only after rule failure |
| messy attribute mapping | LLM |
| product description generation | LLM |
| search-keyword generation | LLM |
| occasion interpretation | LLM |
| image-visible attribute suggestion | multimodal model |
| copy evaluation | LLM + deterministic rules |
| unsupported-claim detection | rules + evaluator |

Models must be used for judgment, language, messy mapping, and interpretation — not arithmetic, lookup, thresholds, or schema validation.

---

# 31. Required AI Patterns

Use patterns intentionally.

## 31.1 Prompt chaining

```text
Raw product data
   ↓
Normalize
   ↓
Generate copy
   ↓
Evaluate copy
   ↓
Optimize if needed
```

## 31.2 Parallelization

After canonicalization, independent tasks may run concurrently:

```text
                 Canonical product
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
Image analysis   Copy generation   Search aliases
        ↓             ↓             ↓
        └─────────────┼─────────────┘
                      ↓
                    QA
```

## 31.3 Routing

```text
Value received
   ↓
Known alias?
   ├─ Yes → deterministic mapping
   └─ No  → model mapper
             ↓
       confidence threshold
             ↓
     human review if low
```

## 31.4 Evaluator–optimizer

```text
Generated copy
   ↓
Evaluator
   ↓
Pass?
 ├─ Yes → QA
 └─ No  → Optimizer / regenerate
             ↓
          Evaluator
```

Set a maximum retry count.

---

# 32. Structured Model Boundaries

Every model call must return schema-validated structured output.

Example normalization schema:

```json
{
  "raw_value": "dark wine",
  "canonical_value": "Maroon",
  "canonical_id": "CLR_MAROON",
  "confidence": 0.94,
  "reason": "Closest approved taxonomy value",
  "requires_review": false
}
```

Example copy schema:

```json
{
  "title": "Mustard Floral Cotton Kurti",
  "short_description": "...",
  "long_description": "...",
  "bullets": ["..."],
  "search_keywords": ["..."],
  "occasion_aliases": ["..."]
}
```

If schema validation fails:

```text
retry once with validation feedback
↓
if still invalid
↓
mark model step failed visibly
↓
route to human review
```

Never silently parse unreliable free text downstream.

---

# 33. Confidence Policy

Suggested MVP confidence policy:

```text
>= 0.90  → suggested auto-accept if non-critical and rule allows
0.75–0.89 → visible suggestion requiring review
< 0.75 → unresolved / human review
```

Critical attributes may require human approval regardless of confidence.

Examples of critical attributes:

- fabric composition;
- size measurements;
- MRP;
- compliance fields;
- country of origin.

---

# 34. Human-in-the-Loop Design

Humans should review exceptions, not every field.

Human review queue categories:

```text
Missing Required Data
Low Confidence Mapping
Image/Text Conflict
Taxonomy Unknown
Copy Rejected
Unsupported Claim
Duplicate SKU
Size Chart Missing
Critical Validation Error
```

Reviewer actions:

```text
Accept
Edit
Reject
Request data
Mark not applicable
Escalate
```

All actions must be logged.

---

# 35. Safety / Quality Guardrails

## Guardrail 1 — Never hallucinate missing facts

If authoritative data does not exist, store null and create a visible issue.

## Guardrail 2 — Model suggestions never silently overwrite verified source values

Conflicts require explicit resolution.

## Guardrail 3 — Generated copy cannot add unsupported factual claims

Use claim verification.

## Guardrail 4 — Critical attributes require stricter approval

High confidence does not equal authoritative truth.

## Guardrail 5 — Taxonomy expansion is controlled

The model cannot create production canonical values automatically.

## Guardrail 6 — Fail visibly

If image processing, schema validation, copy generation, or mapping fails, show a user-visible failure state.

## Guardrail 7 — No auto-publish in MVP

Prefer human approval followed by export/publish-ready payload unless Dhaga explicitly provides safe publishing integration.

---

# 36. Failure Cases the MVP Must Demonstrate

At minimum demonstrate these:

## Failure Case A — Missing fabric

Input has no authoritative fabric data.

Expected:

```text
fabric = null
blocker shown
copy generator prohibited from claiming material
```

## Failure Case B — Colour conflict

Vendor says Navy; image appears Black.

Expected:

```text
conflict surfaced
no automatic overwrite
human resolution required
```

## Failure Case C — Corrupted / malformed CSV

Expected:

```text
row-level validation report
valid rows still process where safe
invalid rows visibly blocked
```

## Failure Case D — Duplicate SKU

Expected:

```text
record blocked
existing SKU reference shown
user chooses merge/correct/cancel
```

## Failure Case E — Copy evaluator rejects unsupported claim

Expected:

```text
copy rejected
unsupported phrase highlighted
regeneration or human edit available
```

---

# 37. MVP Frontend Screens

## Screen 1 — Overview

Show:

- total weekly SKUs;
- ready;
- needs review;
- blocked;
- next drop readiness;
- pipeline stages;
- top blocker types;
- median catalog processing time.

## Screen 2 — Products

Filterable operational table.

## Screen 3 — Product Detail

Full evidence, attributes, copy, conflicts, readiness, and approval.

## Screen 4 — Drop Readiness

Tuesday/Friday launch status and at-risk products.

## Screen 5 — Vendor Intake

Upload/process vendor sheets and see row-level validation.

## Screen 6 — Review Queue

Exception-based HITL queue.

Optional MVP+

- taxonomy manager;
- workflow analytics.

---

# 38. Recommended Backend Services

Suggested modules:

```text
services/
  ingestion/
  schema_mapping/
  taxonomy/
  normalization/
  image_enrichment/
  copy_generation/
  claim_validation/
  qa/
  readiness/
  workflow/
  drop_risk/
  audit/
  model_gateway/
```

Do not couple UI directly to model providers.

All model calls go through `model_gateway`.

---

# 39. Suggested Repository Structure for Codex

```text
dhaga-os/
├── apps/
│   ├── web/
│   └── api/
├── features/
│   └── catalog_velocity/
│       ├── README.md
│       ├── domain/
│       │   ├── models.py
│       │   ├── enums.py
│       │   └── schemas.py
│       ├── ingestion/
│       ├── normalization/
│       ├── enrichment/
│       ├── copy/
│       ├── qa/
│       ├── readiness/
│       ├── workflow/
│       ├── drop_risk/
│       ├── audit/
│       ├── api/
│       ├── ui/
│       └── tests/
├── prompts/
│   └── catalog_velocity/
├── datasets/
│   ├── demo/
│   └── taxonomy/
├── evals/
│   └── catalog_velocity/
├── scripts/
├── docs/
└── .env.example
```

If the wider Dhaga-OS repository already has a different convention, preserve the project convention and use this only as a logical module breakdown.

---

# 40. Suggested Database Tables

Minimum logical tables:

```text
products
product_attributes
product_images
vendors
vendor_product_intakes
vendor_intake_rows
canonical_taxonomy
canonical_taxonomy_aliases
attribute_suggestions
attribute_conflicts
catalog_copy_versions
catalog_qa_runs
catalog_readiness_snapshots
workflow_events
human_review_tasks
drop_targets
audit_log
model_runs
```

Optional:

```text
size_charts
product_measurements
publish_payloads
```

---

# 41. API Surface

Suggested MVP endpoints:

```text
POST   /catalog/intake/upload
GET    /catalog/intake/{id}
GET    /catalog/products
GET    /catalog/products/{product_id}
PATCH  /catalog/products/{product_id}
POST   /catalog/products/{product_id}/normalize
POST   /catalog/products/{product_id}/generate-copy
POST   /catalog/products/{product_id}/qa
POST   /catalog/products/{product_id}/approve
GET    /catalog/review-queue
POST   /catalog/review/{task_id}/resolve
GET    /catalog/drop-readiness
GET    /catalog/overview
GET    /catalog/taxonomy
POST   /catalog/taxonomy/aliases
```

Do not expose raw model-provider endpoints to frontend clients.

---

# 42. Background Job Design

Long-running tasks should be asynchronous.

Candidate jobs:

```text
vendor_file_parse
bulk_normalization
image_analysis
copy_generation
copy_evaluation
catalog_qa
readiness_refresh
workflow_metric_refresh
```

Each job should store:

```text
job_id
status
started_at
completed_at
error
retry_count
related_product_id
```

---

# 43. Retry and Failure Strategy

For model calls:

```text
attempt 1
↓ failure
retry with same structured contract
↓ failure
mark visible error
route to review
```

For deterministic jobs:

```text
retry idempotently where safe
```

Do not create duplicate product records because of retries.

Use idempotency keys for batch uploads and product creation.

---

# 44. Model Strategy

The project brief requires at least two models in the overall MVP context.

Recommended conceptual split:

## Lower-cost / faster model

Use for:

- bulk taxonomy mapping;
- straightforward attribute normalization;
- keyword generation;
- first-pass copy generation.

## Stronger model

Use for:

- ambiguous normalization;
- copy evaluation;
- contradiction reasoning;
- difficult attribute resolution;
- evaluator/optimizer step.

Model names should be selected at implementation time based on current pricing, latency, quality, and provider availability. Do not hard-code this SOT to a specific model version unless required.

---

# 45. Temperature Guidance

Suggested intent:

```text
Normalization / extraction: low temperature
Classification / evaluation: low temperature
Copy generation: low-to-moderate temperature
Copy optimization: moderate but constrained
```

Exact numeric temperature values should be provider-specific configuration, not scattered through code.

---

# 46. Evaluation Framework

Create a hand-labelled gold set.

Recommended minimum:

- 50–100 attribute-normalization examples;
- 20–30 product-copy examples;
- known conflict cases;
- missing-data cases;
- known taxonomy aliases.

Evaluate:

## Normalization

```text
exact canonical match accuracy
review-required precision
false auto-accept rate
```

False auto-accept is especially important.

## Copy

Human rating dimensions:

```text
factual correctness
brand consistency
clarity
usefulness
unsupported claims
```

## QA

```text
critical error detection recall
false blocking rate
```

---

# 47. Success Metrics

## MVP technical metrics

- >= 95% structured-output validity after retries;
- zero silent hallucination of mandatory facts in tested gold cases;
- visible failure for invalid rows/models;
- reliable 50-SKU batch processing;
- explainable readiness score;
- all generated outputs traceable to sources/model run.

## Operational hypothesis metrics

Measure baseline first:

- P50 sample-to-live;
- P90 sample-to-live;
- manual minutes per SKU;
- manual attribute-entry count;
- copywriting time;
- percentage SKUs ready before target drop.

Then compare pilot performance.

## Target hypothesis

Reducing the current 6–9 day cycle toward **3–4 days** is a valid product hypothesis, not a guaranteed result.

It should only become a committed target after stage-level baseline timing shows that catalog/listing work is a material contributor to total delay.

---

# 48. Demo Story

Recommended live demo sequence:

```text
1. Open Tuesday Drop Readiness
2. Show several products at risk
3. Upload a realistic vendor file
4. Show row/schema validation
5. Show deterministic alias normalization
6. Show one ambiguous value routed to AI
7. Open a product detail
8. Attach/select images
9. Generate controlled product copy
10. Run QA
11. Show readiness score
12. Resolve one conflict manually
13. Show product becomes Ready
14. Show one intentional failure case
15. Return to Drop Readiness and show impact
```

Do not open the client presentation with architecture.

Open with the delay and missed-drop risk.

---

# 49. Demo Failure Case Recommendation

Best demo failure:

```text
Vendor fabric missing
+ image clearly shows a garment
```

Ask the system to process it.

Correct behavior:

```text
image suggestions may identify style/pattern
fabric remains null
copy avoids fabric claims
product is blocked for missing authoritative fabric
```

This proves the guardrail visibly.

---

# 50. MVP Acceptance Criteria

The MVP is acceptable only if all are true:

- [ ] deployed frontend exists;
- [ ] 50 realistic SKUs can be processed;
- [ ] CSV/Excel-like intake works;
- [ ] row-level validation works;
- [ ] deterministic taxonomy aliases work;
- [ ] unknown values can route to an LLM;
- [ ] structured outputs are schema validated;
- [ ] raw and canonical values are both retained;
- [ ] at least one image-supported suggestion is demonstrated;
- [ ] missing authoritative facts are never fabricated;
- [ ] product copy can be generated from approved attributes;
- [ ] unsupported claims can be detected/rejected;
- [ ] readiness score is deterministic and explainable;
- [ ] blocked/needs-review/ready states work;
- [ ] human review queue works;
- [ ] drop-readiness view exists;
- [ ] one visible failure case is demonstrated;
- [ ] model errors fail visibly;
- [ ] audit trail exists;
- [ ] README explains local startup and failure behavior;
- [ ] cost per model run/batch can be measured;
- [ ] system can be operated without an ML engineer.

---

# 51. Non-Goals for MVP

Do not attempt all of the following in the first build:

- complete vendor ERP;
- vendor contracts;
- payments;
- vendor invoicing;
- purchase-order accounting;
- live production integration without sandbox;
- automated product publishing without human approval;
- autonomous vendor decisions;
- autonomous sourcing decisions;
- demand forecasting;
- full warehouse/inventory system;
- full merchandising ranking system;
- automated photography;
- replacement of existing internal admin.

---

# 52. Security / Permissions

Recommended roles:

```text
LISTING_AGENT
LISTING_LEAD
CATEGORY_MANAGER
SOURCING_USER
ADMIN
VIEWER
```

Permissions should control:

- editing product data;
- resolving conflicts;
- approving product;
- taxonomy changes;
- vendor data access;
- model regeneration;
- audit-log visibility;
- publish/export actions.

Never allow a normal listing user to silently alter canonical taxonomy definitions if taxonomy governance matters.

---

# 53. Audit Requirements

Log:

```text
who changed a value
old value
new value
source
model version if AI
prompt/template version
confidence
approval state
timestamp
reason if human override
```

Generated copy must be versioned.

Never overwrite prior generated/approved copy without history.

---

# 54. Observability

Track:

```text
model latency
model cost
model failure rate
schema validation failure
retry count
batch processing time
normalization confidence distribution
human override rate
queue size
job backlog
```

Also track application-level failures such as:

```text
CSV parse failure
image fetch failure
missing taxonomy
DB transaction failure
background-job timeout
```

---

# 55. Cost Tracking

Every model run must record:

```text
provider
model
input tokens/output tokens where available
estimated cost
latency
operation type
product_id / batch_id
```

Dashboard should support:

```text
cost per SKU
cost per 50-SKU batch
projected weekly cost at ~400 new SKUs
```

Do not invent pricing in code. Use configurable model pricing metadata.

---

# 56. Configuration

Keep configurable:

```text
required fields by category
readiness weights
confidence thresholds
critical attributes
allowed taxonomy
brand-copy rules
model routing
maximum retries
copy lengths
image count requirements
stage SLA targets
risk thresholds
```

Do not hard-code business rules across many files.

---

# 57. Feature Flags

Recommended flags:

```text
ENABLE_IMAGE_ENRICHMENT
ENABLE_LLM_NORMALIZATION
ENABLE_COPY_GENERATION
ENABLE_COPY_EVALUATOR
ENABLE_DROP_RISK
ENABLE_AUTO_ACCEPT_NONCRITICAL
ENABLE_DIRECT_PUBLISH
```

`ENABLE_DIRECT_PUBLISH` must be false by default for MVP.

---

# 58. Codex Implementation Rules

When using this file as context, Codex should follow these instructions:

1. Treat this Markdown file as the feature-level source of truth.
2. Do not invent Dhaga production APIs, exact attribute lists, credentials, or integrations.
3. When data is unknown, implement interfaces/configuration/placeholders and clearly mark them.
4. Preserve deterministic-vs-model boundaries.
5. Use typed schemas for all model outputs.
6. Validate at every model boundary.
7. Retain raw source data and provenance.
8. Never silently overwrite verified values with model suggestions.
9. Never infer missing critical product facts.
10. Keep model-provider logic behind a gateway/adapter.
11. Make the system work with demo data locally.
12. Make background jobs idempotent.
13. Surface failures in UI.
14. Log cost/latency/model metadata.
15. Add tests for all guardrails.
16. Prefer the smallest end-to-end implementation that proves the workflow.
17. Do not build unrelated Dhaga-OS modules unless needed for an interface.
18. Do not silently change this SOT's business rules.

---

# 59. Required Tests

## Unit tests

```text
schema validation
taxonomy alias mapping
readiness calculation
critical blocker logic
duplicate detection
claim validation
risk calculation
```

## Integration tests

```text
upload → product creation
normalize → review queue
copy generation → evaluator
QA → readiness
human resolution → status change
```

## AI regression tests

Gold cases for:

```text
colour normalization
fabric ambiguity
category normalization
copy factuality
unsupported claim rejection
image/text conflict
```

## End-to-end test

```text
upload 50-SKU demo file
→ process
→ resolve review case
→ generate copy
→ QA
→ ready state
```

---

# 60. Build Order

Recommended implementation order:

## Phase 0 — Discovery + fixtures

- capture actual catalog schema;
- create taxonomy seed files;
- prepare demo dataset;
- define mandatory fields;
- define workflow stages;
- establish baseline timings if possible.

## Phase 1 — Deterministic foundation

- data model;
- ingestion;
- row validation;
- taxonomy aliases;
- product list/detail;
- readiness engine;
- audit events.

## Phase 2 — AI normalization

- model gateway;
- structured mapping;
- confidence routing;
- review queue.

## Phase 3 — Copy generation

- brand rules;
- generated copy;
- evaluator;
- factual claim verification;
- versioning.

## Phase 4 — Image enrichment

- image-processing interface;
- safe visible-attribute suggestions;
- conflict detection.

## Phase 5 — Drop readiness

- workflow events;
- target-drop dates;
- stage timing;
- risk logic;
- dashboard.

## Phase 6 — Hardening

- cost tracking;
- evals;
- retries;
- monitoring;
- security roles;
- demo failure states;
- README.

---

# 61. Key Open Questions for Dhaga

Before production implementation, ask:

1. What are the exact ~60 catalog fields?
2. Which fields are mandatory by category?
3. Which fields may be inferred and which require authoritative supplier input?
4. What is the current internal admin import/API format?
5. Can reviews/returns and vendor IDs later be joined to the same product ID?
6. When exactly does catalog work start today?
7. Does vendor data arrive before sample delivery?
8. What file formats do vendors use?
9. Who owns size-chart approval?
10. How many images are required per SKU?
11. What are the exact copywriting rules?
12. Which claims are prohibited or legally sensitive?
13. What is the actual time spent in each workflow stage?
14. How frequently do Tuesday/Friday drops miss planned SKUs?
15. What happens to a product if it misses a drop?
16. What defines “ready to publish” in the current admin?
17. Who approves a listing today?
18. Can the MVP export CSV/JSON instead of publishing directly?
19. What volume arrives in a single vendor batch?
20. Which vendor inconsistencies cause the most rework?

---

# 62. Product Hypotheses to Validate

Do not present these as verified facts yet.

## Hypothesis A

Starting product creation at PO/vendor confirmation rather than after sample/photo completion will reduce idle catalog preparation time.

## Hypothesis B

Canonical taxonomy + deterministic alias mapping will reduce manual typing and correction work.

## Hypothesis C

AI-assisted copy generation will reduce time spent writing repeated descriptions while improving tone consistency.

## Hypothesis D

Exception-based human review will require fewer manual touches per SKU than manually constructing each listing.

## Hypothesis E

Drop-readiness visibility will let the listing/category teams intervene earlier on at-risk SKUs.

## Hypothesis F

A 3–4 day sample-to-live cycle may be achievable if the listing/catalog portion represents a material share of the existing 6–9 day delay.

---

# 63. Relationship to Other Dhaga-OS Features

This feature should integrate later with Review Intelligence and Customer Support, but remains independently usable.

Long-term lifecycle:

```text
Vendor / PO
    ↓
Catalog Velocity
    ↓
Product Live
    ↓
Orders
    ↓
Reviews / Returns / Tickets
    ↓
Customer & Product Intelligence
    ↓
Vendor / Product Findings
    ↓
Next Catalog / Sourcing Decisions
```

Do not tightly couple Catalog Velocity implementation to those future modules. Use stable identifiers and events so they can connect later.

Shared identifiers should preferably include:

```text
product_id
sku
vendor_id
category_id
```

---

# 64. Event Model for Future Integration

Emit domain events such as:

```text
catalog.product.created
catalog.product.normalized
catalog.product.blocked
catalog.product.ready
catalog.product.approved
catalog.product.published
catalog.conflict.created
catalog.conflict.resolved
catalog.copy.generated
catalog.copy.approved
catalog.drop_risk.high
```

These can later feed broader Dhaga-OS workflows.

---

# 65. Final MVP Definition

The MVP is not “AI writes product descriptions.”

The MVP is:

> An end-to-end Catalog Velocity workspace where Dhaga can ingest realistic vendor product data, create canonical product drafts, normalize messy attributes, safely enrich selected fields, generate evidence-constrained copy, detect missing/conflicting data, calculate catalog readiness, route exceptions to human review, and see which SKUs are at risk of missing the next collection drop.

The user experience should demonstrate that the listing team can move from:

```text
TYPE → TYPE → TYPE → WRITE → CHECK
```

toward:

```text
REVIEW → CORRECT → APPROVE → PUBLISH
```

---

# 66. Definition of Done for Codex

Codex should consider this feature implementation complete only when:

- the app works locally from documented setup;
- realistic demo data can be loaded;
- frontend is usable without narration;
- all model outputs are structured;
- all important decisions are explainable;
- failures are visible;
- critical facts are never hallucinated;
- human override is supported;
- readiness/drop risk are deterministic;
- audit history is preserved;
- model cost can be measured;
- tests cover guardrails;
- 50-SKU demo works end-to-end;
- architecture remains maintainable by engineers without dedicated ML staff.

---

# 67. Codex Startup Prompt

When starting implementation, use this file plus the broader Dhaga-OS architecture as context and instruct Codex:

```text
Build only the Dhaga-OS Catalog Velocity & Category Visibility feature described in this SOT.

Start by producing:
1. assumptions and unresolved client dependencies;
2. domain/data model;
3. API contracts;
4. frontend screen map;
5. deterministic-vs-AI execution plan;
6. test plan;
7. phased implementation checklist.

Do not code until these outputs are internally consistent with this SOT.

When coding:
- preserve raw and canonical values;
- use structured schemas at every AI boundary;
- never invent missing critical product facts;
- route uncertainty to human review;
- keep readiness and drop-risk deterministic;
- implement a visible failure state;
- use realistic multi-row demo data;
- keep the feature modular for later integration with Review Intelligence and Customer Support.
```

---

# 68. Final Principle

The system is successful only if it improves a real operational decision:

> **What must Dhaga fix today so the right products are complete, safe, and ready before the next drop?**

That is the product. AI is only one implementation component.
