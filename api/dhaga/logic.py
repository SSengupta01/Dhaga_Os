import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import Audit, Order, Product, Run, Shipment, Ticket
from .llm import classify, evaluate
from .seed import NOW

POLICY_PACK = json.loads((Path(__file__).parent / "policies.json").read_text(encoding="utf-8"))
POLICIES = {p["id"]: p for p in POLICY_PACK["policies"]}
ORDER_RE = re.compile(r"\bORD\d{6}\b", re.I)
SKU_RE = re.compile(r"\bDHG-\d{5}\b", re.I)
INTENT_RULES = [
    ("compensation", r"compensat|₹\s*\d+"),
    ("refund", r"refund|paisa kab|money back"),
    ("return", r"\breturn\b|wapas"),
    ("exchange", r"exchange|size change|replace size"),
    ("cancellation", r"cancel|stop dispatch"),
    ("payment", r"payment|prepaid|\bCOD\b|paid"),
    ("product", r"fabric|colour|color|price|product|sku"),
    ("wismo", r"where|kaha|parcel|tracking|delivery|update|order status|nhi aya"),
]


def trace(stage: str, kind: str, result: str, **data):
    return {"stage": stage, "kind": kind, "result": result, **data}


def _naive_utc(value: datetime):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _classify(message: str):
    matches = [intent for intent, pattern in INTENT_RULES if re.search(pattern, message, flags=re.I)]
    if "compensation" in matches:
        return "compensation", 1.0, [], "deterministic"
    distinct = list(dict.fromkeys(matches))
    if len(distinct) == 1:
        return distinct[0], 0.95, [], "deterministic"
    if len(distinct) > 1 and set(distinct) == {"wismo", "payment"}:
        return "payment", 0.85, [], "deterministic"
    extracted, model_trace = classify(message)
    if extracted and extracted.confidence >= 0.75:
        return extracted.intent, extracted.confidence, [model_trace], "model"
    return "unknown", 0.0, [model_trace], "model_or_abstain"


def _make_result(db: Session, ticket: Ticket, session_id: str, *, intent: str, decision: str, reply: str, action: str | None,
                 reasons: list[str], facts: dict, policy_id: str | None, steps: list[dict]):
    run = Run(id=f"RUN-{uuid.uuid4().hex[:12].upper()}", ticket_id=ticket.id, session_id=session_id, intent=intent,
              decision=decision, proposed_reply=reply, proposed_action=action, reason_codes=reasons,
              verified_facts=facts, policy_id=policy_id, trace=steps,
              cost_usd=round(sum(float(step.get("estimated_cost_usd", 0)) for step in steps), 8))
    db.add(run)
    db.commit()
    return run


def process_ticket(db: Session, ticket: Ticket, session_id: str = "public"):
    prior = db.scalar(select(Run).where(Run.ticket_id == ticket.id, Run.session_id == session_id).order_by(Run.created_at.desc()))
    if prior:
        return prior
    steps = [trace("intake", "code", "accepted", event_id=ticket.event_id, channel=ticket.channel),
             trace("idempotency", "code", "new_event")]
    message = ticket.message
    reasons = []
    facts = {"customer_id": ticket.customer_id, "source": "synthetic_demo"}
    if len(message.strip()) < 3 or len(message) > 4000:
        return _make_result(db, ticket, session_id, intent="unknown", decision="escalate", reply="This message needs an agent to review it.", action=None,
                            reasons=["INVALID_MESSAGE"], facts=facts, policy_id=None, steps=steps + [trace("input_guardrail", "code", "blocked")])
    if re.search(r"ignore previous instructions|system prompt|reveal secrets", message, flags=re.I):
        return _make_result(db, ticket, session_id, intent="unknown", decision="escalate", reply="An agent will review this request.", action=None,
                            reasons=["UNTRUSTED_INSTRUCTION"], facts=facts, policy_id=None, steps=steps + [trace("input_guardrail", "code", "blocked")])
    if re.search(r"price match|unsupported policy", message, flags=re.I):
        return _make_result(db, ticket, session_id, intent="unknown", decision="escalate", reply="I do not have a verified policy for that request. An agent will review it.", action=None,
                            reasons=["POLICY_UNKNOWN"], facts=facts, policy_id=None, steps=steps + [trace("policy", "code", "missing")])
    if re.search(r"delivered but (?:I|we) (?:did not|didn't) receive|marked delivered.*not received", message, flags=re.I):
        return _make_result(db, ticket, session_id, intent="wismo", decision="escalate", reply="An agent will investigate this delivery dispute.", action=None,
                            reasons=["DISPUTED_DELIVERY"], facts=facts, policy_id="WISMO_READ", steps=steps + [trace("delivery_dispute", "code", "human_review")])

    intent, confidence, model_steps, source = _classify(message)
    steps.extend(model_steps)
    steps.append(trace("classification", source, intent, confidence=confidence))
    if intent == "unknown":
        return _make_result(db, ticket, session_id, intent=intent, decision="escalate", reply="An agent will review this request.", action=None,
                            reasons=["UNKNOWN_OR_LOW_CONFIDENCE_INTENT"], facts=facts, policy_id=None, steps=steps)
    if intent == "compensation":
        return _make_result(db, ticket, session_id, intent=intent, decision="escalate", reply="I can check your order, but an agent must review the compensation request.", action=None,
                            reasons=["COMPENSATION_POLICY_UNKNOWN"], facts=facts, policy_id="COMPENSATION_HUMAN", steps=steps + [trace("policy", "code", "human_review")])

    order_match = ORDER_RE.search(message)
    order_id = order_match.group(0).upper() if order_match else ticket.order_id
    order = db.get(Order, order_id) if order_id else None
    if intent != "product":
        if not order:
            return _make_result(db, ticket, session_id, intent=intent, decision="escalate", reply="I could not verify an order. An agent will help.", action=None,
                                reasons=["ORDER_NOT_FOUND"], facts=facts, policy_id=None, steps=steps + [trace("order_lookup", "code", "missing")])
        if order.customer_id != ticket.customer_id:
            return _make_result(db, ticket, session_id, intent=intent, decision="escalate", reply="I could not verify this order for this account. An agent will help.", action=None,
                                reasons=["ORDER_CUSTOMER_MISMATCH"], facts=facts, policy_id=None, steps=steps + [trace("authorization", "code", "blocked")])
        facts.update({"order_id": order.id, "order_status": order.status, "payment_mode": order.payment_mode,
                      "payment_status": order.payment_status, "inspection_status": order.inspection_status,
                      "placed_at": order.placed_at.isoformat(), "customer_owns_order": True})
        steps.append(trace("authorization", "code", "passed", order_id=order.id))

    decision = "approval_required"
    action = None
    reply = "An agent will review this request."
    policy_id = None

    if intent == "wismo":
        policy_id = "WISMO_READ"
        shipment = db.scalar(select(Shipment).where(Shipment.order_id == order.id))
        if not shipment or shipment.simulate_timeout:
            reasons.append("TRACKING_UNAVAILABLE")
            decision = "escalate"
            steps.append(trace("carrier_lookup", "mock_adapter", "timeout_or_missing"))
        elif _naive_utc(shipment.scan_at) < NOW - timedelta(hours=48):
            reasons.append("STALE_TRACKING")
            decision = "escalate"
            steps.append(trace("carrier_lookup", "mock_adapter", "stale"))
        else:
            facts.update({"carrier": shipment.carrier, "tracking_status": shipment.status, "last_scan_at": shipment.scan_at.isoformat(), "eta": shipment.eta})
            steps.append(trace("carrier_lookup", "mock_adapter", "verified", carrier=shipment.carrier))
            reply = f"Your order {order.id} is {shipment.status.replace('_', ' ')}. The latest {shipment.carrier} scan was in {shipment.scan_city}."
            if shipment.eta:
                reply += f" The current estimated delivery date is {shipment.eta}; this is an estimate, not a guarantee."
            decision = "simulated_sent"
            action = "status_reply"
    elif intent in {"return", "exchange"}:
        policy_id = "RETURN_7D_DEMO" if intent == "return" else "EXCHANGE_7D_DEMO"
        delivered = next((x for x in order.status_history if x["status"] == "delivered"), None)
        within_window = bool(delivered and datetime.fromisoformat(delivered["at"]) >= NOW - timedelta(days=7))
        facts.update({"delivered_at": delivered["at"] if delivered else None, "within_demo_7_day_window": within_window})
        if not within_window:
            reasons.append("RETURN_POLICY_NOT_MET" if intent == "return" else "EXCHANGE_POLICY_NOT_MET")
            decision = "escalate"
        elif intent == "exchange" and not any(db.get(Product, order.product_id).inventory.values()):
            reasons.append("NO_MOCK_STOCK")
            decision = "escalate"
        else:
            action = "create_return_request" if intent == "return" else "create_exchange_request"
            reply = f"I found order {order.id}. Under the illustrative demo policy, an agent can review this {intent} request. No change has been made yet."
    elif intent == "refund":
        policy_id = "REFUND_INSPECTED"
        if order.inspection_status != "passed":
            reasons.append("INSPECTION_PENDING")
            decision = "escalate"
        else:
            action = "create_refund_request"
            reply = f"Inspection is recorded as complete for {order.id}. An agent can review the refund request; no refund has been issued."
    elif intent == "cancellation":
        policy_id = "CANCEL_PRE_DISPATCH_DEMO"
        if order.status != "placed":
            reasons.append("ALREADY_DISPATCHED_OR_PROCESSING")
            decision = "escalate"
        else:
            action = "create_cancellation_request"
            reply = f"Order {order.id} has not entered processing in this demo. An agent can review cancellation; it has not been cancelled."
    elif intent == "payment":
        policy_id = "PAYMENT_READ"
        reply = f"Order {order.id} is marked {order.payment_mode} with payment status {order.payment_status}. No payment action has been taken."
        action = "payment_status_reply"
        decision = "simulated_sent"
    elif intent == "product":
        policy_id = "PRODUCT_READ"
        sku_match = SKU_RE.search(message)
        product = db.scalar(select(Product).where(Product.sku == sku_match.group(0).upper())) if sku_match else None
        if not product:
            reasons.append("PRODUCT_NOT_FOUND")
            decision = "escalate"
        else:
            facts.update({"sku": product.sku, "name": product.name, "colour": product.colour, "fabric": product.fabric, "price": product.price})
            if not product.colour or not product.fabric:
                reasons.append("PRODUCT_FACT_UNKNOWN")
                decision = "escalate"
            else:
                reply = f"{product.name} ({product.sku}) is listed as {product.colour}, {product.fabric}, at ₹{product.price:.0f}."
                action = "product_fact_reply"
                decision = "simulated_sent"

    policy = POLICIES.get(policy_id) if policy_id else None
    steps.append(trace("policy", "code", decision, policy_id=policy_id, policy_version=POLICY_PACK["version"], reasons=reasons))
    if decision == "simulated_sent":
        evaluation, model_trace = evaluate(message, facts, reply)
        steps.append(model_trace)
        if evaluation is not None and not (evaluation.grounded and evaluation.safe_to_show):
            decision = "approval_required"
            reasons.append("OUTPUT_NOT_GROUNDED")
            steps.append(trace("output_guardrail", "code", "blocked"))
        elif evaluation is None and model_trace["status"] == "failed":
            decision = "approval_required"
            reasons.append("EVALUATOR_FAILURE")
        # A missing API key retains only deterministic, literal read-only templates.
    if policy and policy["approval_required"] and decision == "simulated_sent":
        decision = "approval_required"
    if decision == "escalate":
        reply = "The available facts or demo policy do not support an automatic answer. An agent will review this case."
    steps.append(trace("final_decision", "code", decision, reasons=reasons))
    return _make_result(db, ticket, session_id, intent=intent, decision=decision, reply=reply, action=action,
                        reasons=reasons, facts=facts, policy_id=policy_id, steps=steps)


def decide_run(db: Session, run: Run, action: str, actor: str, edited_reply: str | None = None):
    if run.decision not in {"approval_required", "escalate"}:
        raise ValueError("This run has no pending human decision")
    if action not in {"approve", "edit", "escalate"}:
        raise ValueError("Unsupported decision")
    if action == "edit" and not edited_reply:
        raise ValueError("An edited reply is required")
    if action == "approve" and (run.decision != "approval_required" or run.proposed_action not in {"create_return_request", "create_exchange_request", "create_refund_request", "create_cancellation_request"} or run.reason_codes):
        raise ValueError("This case has no approvable action")
    if action == "edit" and run.decision != "approval_required":
        raise ValueError("Blocked cases may only be escalated")
    old = run.decision
    if action == "escalate":
        run.decision = "human_escalated"
    elif action == "approve":
        run.decision = "simulated_approved"
    else:
        run.decision = "simulated_edited"
        run.proposed_reply = edited_reply or run.proposed_reply
    run.resolved_at = datetime.now(timezone.utc)
    db.add(Audit(id=f"AUD-{uuid.uuid4().hex[:12].upper()}", run_id=run.id, action=action, actor=actor, before=old, after=run.decision))
    db.commit()
    return run
