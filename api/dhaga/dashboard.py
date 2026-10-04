"""Read-only dashboard aggregates. Seed facts and session outcomes stay separate."""
from collections import Counter, defaultdict
from sqlalchemy import select
from pydantic import BaseModel
from .db import Product, Review, Run, Ticket
from .seed import NOW

class CountPoint(BaseModel):
    label: str
    value: int

class IntakePoint(BaseModel):
    label: str
    freshdesk: int
    whatsapp: int

class HeatRow(BaseModel):
    label: str
    values: list[int]

class HeatmapData(BaseModel):
    rows: list[HeatRow]
    columns: list[str]

class SentimentPoint(BaseModel):
    label: str
    positive: int = 0
    negative: int = 0
    mixed: int = 0
    unknown: int = 0

class TrendPoint(BaseModel):
    label: str
    reviews: int
    negative: int
    prevalence: float | None

class ConfidencePoint(BaseModel):
    label: str
    count: int

class ReviewQueueItem(BaseModel):
    ticket_id: str
    intent: str
    decision: str
    reasons: list[str]

class DashboardResponse(BaseModel):
    source: str
    as_of: str
    confidence_count: int
    confidence: list[ConfidencePoint]
    intake: list[IntakePoint]
    languages: list[CountPoint]
    outcomes: list[CountPoint]
    processed: int
    review_issues: list[CountPoint]
    review_heatmap: HeatmapData
    review_sentiment: list[SentimentPoint]
    review_trend: list[TrendPoint]
    review_queue: list[ReviewQueueItem]
    vendor_completeness: list[CountPoint]


def dashboard_data(db, session_id, category="", issue=""):
    tickets = db.scalars(select(Ticket)).all()
    products = db.scalars(select(Product)).all()
    reviews = db.scalars(select(Review)).all()
    if category:
        product_ids = {p.id for p in products if p.category == category}
        reviews = [r for r in reviews if r.product_id in product_ids]
    latest = {}
    for run in db.scalars(select(Run).where(Run.session_id == session_id).order_by(Run.created_at.desc(), Run.id)):
        latest.setdefault(run.ticket_id, run)
    intake = defaultdict(Counter)
    for ticket in tickets:
        intake[ticket.created_at.date().isoformat()][ticket.channel] += 1
    categories = {p.id: p.category for p in products}
    issues = Counter(i for r in reviews for i in set((r.analysis or {}).get("issues", [])))
    issue_names = [i for i, _ in issues.most_common(6)]
    heatmap = []
    sentiment = []
    for category in sorted(set(categories.values())):
        rows = [r for r in reviews if categories[r.product_id] == category]
        heatmap.append({"label": category, "values": [sum(i in (r.analysis or {}).get("issues", []) for r in rows) for i in issue_names]})
        counts = Counter((r.analysis or {}).get("sentiment", "unknown") for r in rows)
        sentiment.append({"label": category, **counts})
    weeks = defaultdict(list)
    for r in reviews:
        weeks[r.reviewed_at.strftime("%Y-W%W")].append(r)
    trend = [{"label": week, "reviews": len(rows), "negative": sum(r.rating <= 2 for r in rows), "prevalence": round(100 * sum(issue in (r.analysis or {}).get("issues", []) for r in rows) / len(rows), 1) if len(rows) >= 5 and issue else None} for week, rows in sorted(weeks.items())]
    outcomes = Counter(r.decision for r in latest.values())
    confidence = [s["confidence"] for r in latest.values() for s in r.trace if s.get("stage") == "classification" and s.get("kind") == "model" and isinstance(s.get("confidence"), (int, float))]
    return {"source": "Synthetic seed records; outcomes are latest run per ticket in this browser session", "as_of": NOW.isoformat(),
            "confidence_count": len(confidence), "confidence": [{"label": label, "count": sum(low <= v < high for v in confidence)} for label, low, high in [("0–49%", 0, .5), ("50–74%", .5, .75), ("75–89%", .75, .9), ("90–100%", .9, 1.01)]],
            "intake": [{"label": day, "freshdesk": counts["FRESHDESK"], "whatsapp": sum(counts.values()) - counts["FRESHDESK"]} for day, counts in sorted(intake.items())],
            "languages": [{"label": k, "value": v} for k, v in Counter(t.language for t in tickets).items()],
            "outcomes": [{"label": k, "value": v} for k, v in outcomes.items()], "processed": len(latest),
            "review_issues": [{"label": k, "value": v} for k, v in issues.most_common()],
            "review_heatmap": {"rows": heatmap, "columns": issue_names}, "review_sentiment": sentiment, "review_trend": trend,
            "review_queue": [{"ticket_id": r.ticket_id, "intent": r.intent, "decision": r.decision, "reasons": r.reason_codes} for r in latest.values() if r.decision in {"approval_required", "escalate"}],
            "vendor_completeness": [{"label": vendor, "value": round(100 * sum(bool(value) for p in products if p.vendor_id == vendor for value in [p.colour, p.fabric, p.images, p.raw_attributes.get("size_chart")]) / (4 * sum(p.vendor_id == vendor for p in products)))} for vendor in sorted({p.vendor_id for p in products})]}
