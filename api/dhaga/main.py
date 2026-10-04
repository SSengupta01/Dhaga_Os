import os
import csv
import io
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import Audit, Customer, Product, Review, ReviewInvestigation, Run, Ticket, Vendor, session
from .logic import POLICY_PACK, decide_run, process_ticket
from .seed import NOW, SEED_VERSION
from .workflows import analyze_review, catalog_blockers, generate_catalog_copy, normalize_colour
from .llm import evaluate
from .dashboard import DashboardResponse, dashboard_data

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(title="Dhaga-OS Demo API", version="0.1.0", description="Synthetic operations workspace. No real Dhaga data or actions.", lifespan=lifespan)


def internal_access(x_internal_token: str | None = Header(default=None)):
    secret = os.getenv("DEMO_SESSION_SECRET")
    if os.getenv("VERCEL") and (not secret or secret == "replace-me-before-deploy"):
        raise HTTPException(503, "DEMO_SESSION_SECRET must be configured for deployment")
    if secret and secret != "replace-me-before-deploy" and x_internal_token != secret:
        raise HTTPException(401, "Internal API token required")


def demo_session(x_demo_session: str | None = Header(default=None)):
    return (x_demo_session or "public")[:80]


@app.get("/dashboard", response_model=DashboardResponse, dependencies=[Depends(internal_access)])
def dashboard(category: str = "", issue: str = "", db: Session = Depends(session), session_id: str = Depends(demo_session)):
    return dashboard_data(db, session_id, category, issue)


def serialize_run(run: Run):
    return {"id": run.id, "ticket_id": run.ticket_id, "intent": run.intent, "decision": run.decision,
            "proposed_reply": run.proposed_reply, "proposed_action": run.proposed_action,
            "reason_codes": run.reason_codes, "verified_facts": run.verified_facts, "policy_id": run.policy_id,
            "trace": run.trace, "cost_usd": run.cost_usd, "created_at": run.created_at.isoformat(),
            "resolved_at": run.resolved_at.isoformat() if run.resolved_at else None}


@app.get("/health")
def health(db: Session = Depends(session)):
    try:
        db.execute(select(func.count()).select_from(Ticket)).scalar()
        return {"ok": True, "database": "connected"}
    except Exception:
        return {"ok": False, "database": "unavailable"}


@app.get("/meta", dependencies=[Depends(internal_access)])
def meta():
    return {"seed_version": SEED_VERSION, "policy_version": POLICY_PACK["version"],
            "policy_disclaimer": POLICY_PACK["disclaimer"], "policies": POLICY_PACK["policies"],
            "sources": {"verified": "FDE Academy client engagement brief", "demo": "Deterministic synthetic generator"},
            "models": {"classifier": os.getenv("CLASSIFIER_MODEL", "openai/gpt-4o-mini"), "evaluator": os.getenv("EVALUATOR_MODEL", "openai/gpt-4o")},
            "model_mode": "live" if os.getenv("OPENROUTER_API_KEY") else "deterministic demo; live model key not configured"}


@app.get("/overview", dependencies=[Depends(internal_access)])
def overview(db: Session = Depends(session), session_id: str = Depends(demo_session)):
    ticket_count = db.scalar(select(func.count()).select_from(Ticket)) or 0
    counts = {k: db.scalar(select(func.count()).select_from(Ticket).where(Ticket.expected_intent == k)) or 0 for k in ["wismo", "return", "exchange", "refund", "cancellation", "payment", "product", "unknown"]}
    product_states = Counter(catalog_dict(p)["status"] for p in db.scalars(select(Product)))
    latest = {}
    for row in db.scalars(select(Run).where(Run.session_id == session_id).order_by(Run.created_at.desc(), Run.id)):
        latest.setdefault(row.ticket_id, row)
    measured = []
    for row in latest.values():
        calls = [s for s in row.trace if s.get("model")]
        if calls and all(s.get("status") == "ok" and s.get("estimated_cost_usd") is not None for s in calls):
            measured.append(sum(s["estimated_cost_usd"] for s in calls))
    per_case = round(sum(measured) / len(measured), 8) if measured else None
    return {"demo": True, "seed_version": SEED_VERSION,
            "cx": {"total": ticket_count, "intents": counts, "pending_approval": sum(r.decision == "approval_required" for r in latest.values())},
            "reviews": {"total": db.scalar(select(func.count()).select_from(Review)) or 0, "negative": db.scalar(select(func.count()).select_from(Review).where(Review.rating <= 2)) or 0},
            "catalog": {"total": db.scalar(select(func.count()).select_from(Product)) or 0, "states": product_states},
            "cost_line": {"sampled_runs": len(measured), "mean_cost_usd": per_case,
                          "weekly_all_tickets_usd": round(per_case * 9000, 2) if per_case is not None else None,
                          "weekly_wismo_usd": round(per_case * 5220, 2) if per_case is not None else None,
                          "method": "Measured sample mean × client-brief volume; illustrative, not a production forecast"},
            "verified_context": [{"label": "Weekly support tickets", "value": "~9,000", "source": "Client brief, page 3"},
                                 {"label": "WISMO share", "value": "58%", "source": "Client brief, page 4"},
                                 {"label": "Average first response", "value": "9 hours", "source": "Client brief, page 4"},
                                 {"label": "Sample to live", "value": "6–9 days", "source": "Client brief, page 2"}]}


def ticket_dict(ticket: Ticket):
    return {"id": ticket.id, "customer_id": ticket.customer_id, "order_id": ticket.order_id, "channel": ticket.channel,
            "message": ticket.message, "language": ticket.language, "scenario": ticket.scenario, "status": ticket.status,
            "created_at": ticket.created_at.isoformat(), "messages": ticket.messages}


@app.get("/cx/tickets", dependencies=[Depends(internal_access)])
def tickets(limit: int = Query(40, ge=1, le=100), offset: int = Query(0, ge=0), intent: str | None = None,
            q: str = "", channel: str | None = None, scenario_only: bool = False, db: Session = Depends(session)):
    query = select(Ticket)
    if intent:
        query = query.where(Ticket.expected_intent == intent)
    if scenario_only:
        query = query.where(Ticket.scenario.is_not(None))
    if q:
        query = query.where(Ticket.message.ilike(f"%{q}%") | Ticket.id.ilike(f"%{q}%") | Ticket.scenario.ilike(f"%{q}%"))
    if channel:
        query = query.where(Ticket.channel == channel)
    rows = db.scalars(query.order_by(Ticket.id).limit(limit).offset(offset)).all()
    return {"items": [{**ticket_dict(row), "customer_name": db.get(Customer, row.customer_id).name} for row in rows], "total": db.scalar(select(func.count()).select_from(query.subquery())) or 0}


@app.get("/cx/tickets/{ticket_id}", dependencies=[Depends(internal_access)])
def ticket_detail(ticket_id: str, db: Session = Depends(session), session_id: str = Depends(demo_session)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    run = db.scalar(select(Run).where(Run.ticket_id == ticket_id, Run.session_id == session_id).order_by(Run.created_at.desc()))
    return {"ticket": {**ticket_dict(ticket), "customer_name": db.get(Customer, ticket.customer_id).name}, "run": serialize_run(run) if run else None}


@app.post("/cx/tickets/{ticket_id}/run", dependencies=[Depends(internal_access)])
def run_ticket(ticket_id: str, db: Session = Depends(session), session_id: str = Depends(demo_session)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    return serialize_run(process_ticket(db, ticket, session_id))


class DecisionInput(BaseModel):
    action: Literal["approve", "edit", "escalate"]
    actor: str = Field(min_length=1, max_length=80)
    edited_reply: str | None = Field(default=None, max_length=2000)


@app.post("/cx/runs/{run_id}/decision", dependencies=[Depends(internal_access)])
def decide(run_id: str, payload: DecisionInput, db: Session = Depends(session), session_id: str = Depends(demo_session)):
    run = db.get(Run, run_id)
    if not run or run.session_id != session_id:
        raise HTTPException(404, "Run not found")
    try:
        return serialize_run(decide_run(db, run, payload.action, payload.actor, payload.edited_reply))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/cx/runs/{run_id}/audit", dependencies=[Depends(internal_access)])
def audit(run_id: str, db: Session = Depends(session), session_id: str = Depends(demo_session)):
    run = db.get(Run, run_id)
    if not run or run.session_id != session_id:
        raise HTTPException(404, "Run not found")
    rows = db.scalars(select(Audit).where(Audit.run_id == run_id).order_by(Audit.created_at)).all()
    return {"items": [{"action": a.action, "actor": a.actor, "before": a.before, "after": a.after, "at": a.created_at.isoformat()} for a in rows]}


@app.get("/reviews/overview", dependencies=[Depends(internal_access)])
def reviews_overview(category: str = "", issue: str = "", db: Session = Depends(session)):
    products = db.scalars(select(Product).order_by(Product.id)).all()
    output = []
    for product in products:
        if category and product.category != category:
            continue
        rows = db.scalars(select(Review).where(Review.product_id == product.id)).all()
        if issue and not any(issue in (r.analysis or {}).get("issues", []) for r in rows):
            continue
        issues = Counter(issue for r in rows for issue in (r.analysis or {}).get("issues", []))
        negatives = sum(r.rating <= 2 for r in rows)
        current = [r for r in rows if r.reviewed_at.replace(tzinfo=timezone.utc) >= NOW - timedelta(days=30)]
        previous = [r for r in rows if NOW - timedelta(days=60) <= r.reviewed_at.replace(tzinfo=timezone.utc) < NOW - timedelta(days=30)]
        current_negative_rate = round(sum(r.rating <= 2 for r in current) / len(current), 3) if current else 0
        previous_negative_rate = round(sum(r.rating <= 2 for r in previous) / len(previous), 3) if previous else 0
        output.append({"product_id": product.id, "sku": product.sku, "name": product.name, "category": product.category,
                       "review_count": len(rows), "negative_count": negatives, "top_issue": issues.most_common(1)[0][0] if issues else None,
                       "issue_count": sum(issues.values()), "current_30d_count": len(current), "previous_30d_count": len(previous),
                       "current_negative_rate": current_negative_rate, "previous_negative_rate": previous_negative_rate,
                       "alert": len(current) >= 5 and len(previous) >= 5 and current_negative_rate >= 0.3 and current_negative_rate > previous_negative_rate * 1.5 and bool(issues)})
    output.sort(key=lambda x: (x["alert"], x["negative_count"]), reverse=True)
    return {"demo": True, "total_reviews": db.scalar(select(func.count()).select_from(Review)) or 0, "products": output}


@app.get("/reviews/products/{product_id}", dependencies=[Depends(internal_access)])
def review_product(product_id: str, issue: str = "", db: Session = Depends(session)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    rows = db.scalars(select(Review).where(Review.product_id == product_id).order_by(Review.reviewed_at.desc())).all()
    if issue:
        rows = [r for r in rows if issue in (r.analysis or {}).get("issues", [])]
    return {"product": {"id": product.id, "name": product.name, "sku": product.sku, "vendor_id": product.vendor_id},
            "evidence": [{"id": r.id, "rating": r.rating, "text": r.text, "date": r.reviewed_at.date().isoformat(), "analysis": r.analysis} for r in rows]}


@app.post("/reviews/{review_id}/analyze", dependencies=[Depends(internal_access)])
def review_analyze(review_id: str, db: Session = Depends(session)):
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    analysis, call_trace = analyze_review(review.text)
    if analysis is None:
        raise HTTPException(503, {"reason": call_trace.get("reason", "MODEL_UNAVAILABLE"), "trace": call_trace})
    review.analysis = analysis
    db.commit()
    return {"review_id": review_id, "analysis": analysis}


class InvestigationInput(BaseModel):
    product_id: str
    issue_code: str
    owner: str = Field(min_length=1, max_length=80)
    notes: str = Field(default="", max_length=2000)


@app.get("/reviews/investigations", dependencies=[Depends(internal_access)])
def investigations(db: Session = Depends(session)):
    rows = db.scalars(select(ReviewInvestigation).order_by(ReviewInvestigation.created_at.desc())).all()
    return {"items": [{"id": r.id, "product_id": r.product_id, "issue_code": r.issue_code, "status": r.status, "owner": r.owner, "notes": r.notes} for r in rows]}


@app.post("/reviews/investigations", dependencies=[Depends(internal_access)])
def create_investigation(payload: InvestigationInput, db: Session = Depends(session)):
    if not db.get(Product, payload.product_id):
        raise HTTPException(404, "Product not found")
    row = ReviewInvestigation(id=f"INV-{uuid.uuid4().hex[:12].upper()}", product_id=payload.product_id, issue_code=payload.issue_code,
                              status="open", owner=payload.owner, notes=payload.notes)
    db.add(row)
    db.commit()
    return {"id": row.id, "status": row.status}


class InvestigationUpdate(BaseModel):
    status: Literal["open", "investigating", "resolved", "dismissed"]
    notes: str = Field(max_length=2000)


@app.patch("/reviews/investigations/{investigation_id}", dependencies=[Depends(internal_access)])
def update_investigation(investigation_id: str, payload: InvestigationUpdate, db: Session = Depends(session)):
    row = db.get(ReviewInvestigation, investigation_id)
    if not row:
        raise HTTPException(404, "Investigation not found")
    row.status, row.notes = payload.status, payload.notes
    db.commit()
    return {"id": row.id, "status": row.status, "notes": row.notes}


def catalog_dict(product: Product):
    blockers = catalog_blockers(product)
    state = "blocked" if any(b.startswith("MISSING") for b in blockers) else "needs_review" if blockers else "ready"
    return {"id": product.id, "sku": product.sku, "name": product.name, "vendor_id": product.vendor_id, "category": product.category,
            "colour": product.colour, "fabric": product.fabric, "price": product.price, "inventory": product.inventory,
            "raw_attributes": product.raw_attributes, "field_provenance": product.field_provenance,
            "images": product.images, "workflow": {**product.workflow, "blockers": blockers, "readiness_score": max(0, 100 - 25 * len(blockers))}, "status": state, "target_drop": product.target_drop}


@app.get("/catalog/overview", dependencies=[Depends(internal_access)])
def catalog_overview(db: Session = Depends(session)):
    products = db.scalars(select(Product).order_by(Product.id)).all()
    records = [catalog_dict(p) for p in products]
    states = Counter(p["status"] for p in records)
    blockers = Counter(b for p in records for b in p["workflow"].get("blockers", []))
    drops = defaultdict(lambda: Counter())
    for p in records:
        drops[p["target_drop"]][p["status"]] += 1
    return {"demo": True, "total": len(products), "states": dict(states), "blockers": dict(blockers),
            "drops": [{"date": date, "states": dict(counts)} for date, counts in sorted(drops.items())],
            "products": records}


@app.get("/catalog/products/{product_id}", dependencies=[Depends(internal_access)])
def catalog_product(product_id: str, db: Session = Depends(session)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return catalog_dict(product)


def refresh_product(product: Product):
    blockers = catalog_blockers(product)
    workflow = dict(product.workflow)
    workflow["blockers"] = blockers
    workflow["readiness_score"] = max(0, 100 - 25 * len(blockers))
    product.workflow = workflow
    product.status = "blocked" if any(b.startswith("MISSING") for b in blockers) else "needs_review" if blockers else "ready"
    return blockers


@app.post("/catalog/products/{product_id}/normalize", dependencies=[Depends(internal_access)])
def normalize_product(product_id: str, db: Session = Depends(session)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    raw = str(product.raw_attributes.get("colour") or "")
    if not raw:
        raise HTTPException(422, "Raw colour missing")
    canonical, method, call_trace = normalize_colour(raw)
    if canonical and (not product.field_provenance.get("colour", {}).get("approved") or not product.colour):
        provenance = dict(product.field_provenance)
        provenance["colour"] = {"source": "vendor_csv", "raw": raw, "canonical": canonical, "resolution_method": method,
                                "approved": method != "model_suggestion"}
        product.field_provenance = provenance
        if method != "model_suggestion":
            product.colour = canonical
    blockers = refresh_product(product)
    db.commit()
    return {"product": catalog_dict(product), "suggestion": canonical, "method": method, "trace": call_trace, "blockers": blockers}


class ProductEdit(BaseModel):
    actor: str = Field(min_length=1, max_length=80)
    colour: str | None = None
    fabric: str | None = None
    approve_colour_suggestion: bool = False


@app.patch("/catalog/products/{product_id}", dependencies=[Depends(internal_access)])
def edit_product(product_id: str, payload: ProductEdit, db: Session = Depends(session)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    provenance = dict(product.field_provenance)
    if payload.colour is not None:
        product.colour = payload.colour.strip() or None
        provenance["colour"] = {"source": "human_edit", "raw": product.raw_attributes.get("colour"), "canonical": product.colour, "approved": True, "actor": payload.actor}
    elif payload.approve_colour_suggestion:
        suggestion = provenance.get("colour", {}).get("canonical")
        if not suggestion:
            raise HTTPException(422, "No colour suggestion to approve")
        product.colour = suggestion
        provenance["colour"] = {**provenance["colour"], "approved": True, "actor": payload.actor}
    if payload.fabric is not None:
        product.fabric = payload.fabric.strip() or None
        provenance["fabric"] = {"source": "human_edit", "raw": product.raw_attributes.get("fabric"), "canonical": product.fabric, "approved": True, "actor": payload.actor}
    product.field_provenance = provenance
    refresh_product(product)
    db.commit()
    return catalog_dict(product)


@app.post("/catalog/products/{product_id}/qa", dependencies=[Depends(internal_access)])
def qa_product(product_id: str, db: Session = Depends(session)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    blockers = refresh_product(product)
    db.commit()
    return {"status": product.status, "score": product.workflow["readiness_score"], "blockers": blockers}


@app.post("/catalog/products/{product_id}/generate-copy", dependencies=[Depends(internal_access)])
def generate_copy(product_id: str, db: Session = Depends(session)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    blockers = refresh_product(product)
    if blockers:
        raise HTTPException(422, {"reason": "PRODUCT_NOT_READY", "blockers": blockers})
    facts = {"name": product.name, "sku": product.sku, "category": product.category,
             "colour": product.colour, "fabric": product.fabric, "price": product.price}
    copy, call_trace = generate_catalog_copy(facts)
    if copy is None:
        raise HTTPException(503, {"reason": call_trace.get("reason", "MODEL_UNAVAILABLE"), "trace": call_trace})
    verdict, evaluator_trace = evaluate("Catalog listing copy", facts, str(copy))
    if not verdict or not (verdict.grounded and verdict.safe_to_show):
        raise HTTPException(422, {"reason": "COPY_EVALUATOR_REJECTED", "trace": evaluator_trace})
    raw = dict(product.raw_attributes)
    raw["generated_copy"] = {"value": copy, "model_trace": call_trace, "evaluator_trace": evaluator_trace, "approved": False}
    product.raw_attributes = raw
    db.commit()
    return {"copy": copy, "approved": False, "trace": [call_trace, evaluator_trace]}


class CatalogApproval(BaseModel):
    actor: str = Field(min_length=1, max_length=80)


@app.post("/catalog/products/{product_id}/approve", dependencies=[Depends(internal_access)])
def approve_product(product_id: str, payload: CatalogApproval, db: Session = Depends(session)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    if refresh_product(product) or not product.raw_attributes.get("generated_copy"):
        raise HTTPException(422, "Product requires cleared blockers and generated copy")
    raw = dict(product.raw_attributes)
    raw["generated_copy"] = {**raw["generated_copy"], "approved": True, "approved_by": payload.actor}
    product.raw_attributes = raw
    workflow = dict(product.workflow)
    workflow["approved_by"] = payload.actor
    workflow["approved_at"] = datetime.now(timezone.utc).isoformat()
    product.workflow = workflow
    db.commit()
    return {"product": catalog_dict(product), "publish_ready_payload": {"sku": product.sku, "title": raw["generated_copy"]["value"]["title"],
             "description": raw["generated_copy"]["value"]["short_description"], "colour": product.colour, "fabric": product.fabric,
             "price": product.price, "images": product.images}, "published": False}


class IntakeCSV(BaseModel):
    csv_text: str = Field(min_length=1, max_length=100000)


@app.post("/catalog/intake/preview", dependencies=[Depends(internal_access)])
def intake_preview(payload: IntakeCSV, db: Session = Depends(session)):
    reader = csv.DictReader(io.StringIO(payload.csv_text))
    required = {"sku", "vendor_id", "name", "category", "colour", "fabric", "price"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise HTTPException(422, {"reason": "MISSING_COLUMNS", "required": sorted(required)})
    rows = []
    seen_skus = set()
    for index, row in enumerate(reader, start=2):
        if index > 102:
            raise HTTPException(422, "Maximum 100 data rows per intake")
        errors = []
        if not row.get("sku") or not row.get("name"):
            errors.append("MISSING_IDENTIFIER")
        if row.get("vendor_id") and not db.get(Vendor, row["vendor_id"]):
            errors.append("UNKNOWN_VENDOR")
        if row.get("sku") and db.scalar(select(Product).where(Product.sku == row["sku"])):
            errors.append("DUPLICATE_SKU")
        if row.get("sku") in seen_skus:
            errors.append("DUPLICATE_IN_FILE")
        seen_skus.add(row.get("sku"))
        try:
            float(row.get("price") or "")
        except ValueError:
            errors.append("INVALID_PRICE")
        rows.append({"line": index, "sku": row.get("sku"), "errors": errors, "accepted": not errors})
    return {"rows": rows, "accepted": sum(r["accepted"] for r in rows), "rejected": sum(not r["accepted"] for r in rows), "applied": False}


@app.post("/catalog/intake/apply", dependencies=[Depends(internal_access)])
def intake_apply(payload: IntakeCSV, db: Session = Depends(session)):
    preview = intake_preview(payload, db)
    if preview["rejected"] or not preview["accepted"]:
        raise HTTPException(422, {"reason": "VALIDATION_FAILED", "rows": preview["rows"]})
    reader = csv.DictReader(io.StringIO(payload.csv_text))
    created = []
    for row in reader:
        raw_colour = row["colour"].strip()
        canonical, method, _ = normalize_colour(raw_colour)
        product = Product(
            id=f"PROD-{uuid.uuid4().hex[:10].upper()}", sku=row["sku"].strip(), vendor_id=row["vendor_id"],
            name=row["name"].strip(), category=row["category"].strip(), colour=canonical if method in {"alias_rule", "canonical_rule"} else None,
            fabric=row["fabric"].strip() or None, price=float(row["price"]), inventory={"S": 0, "M": 0, "L": 0},
            raw_attributes={"colour": raw_colour, "fabric": row["fabric"], "size_chart": None},
            field_provenance={"colour": {"source": "vendor_csv", "raw": raw_colour, "canonical": canonical, "resolution_method": method,
                                         "approved": method in {"alias_rule", "canonical_rule"}}},
            images=[], workflow={"blockers": [], "po_confirmed_at": NOW.isoformat(), "sample_received_at": None, "images_ready_at": None},
            status="blocked", target_drop="2026-10-09",
        )
        refresh_product(product)
        db.add(product)
        created.append(product.sku)
    db.commit()
    return {"created": created, "count": len(created), "applied": True, "note": "Synthetic demo catalog draft only; nothing published"}
