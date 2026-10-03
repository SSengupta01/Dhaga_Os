"""Score hand-authored held-out case labels against the seeded demo."""
import json
from collections import Counter
from pathlib import Path

from dhaga.db import SessionLocal, Ticket
from dhaga.logic import process_ticket


def main():
    labels = json.loads((Path(__file__).parents[1] / "evals" / "cx_cases.json").read_text(encoding="utf-8"))
    correct = 0
    unsafe_sends = 0
    decisions = Counter()
    intents = Counter()
    matched_by_intent = Counter()
    model_latencies = []
    model_costs = []
    failures = []
    with SessionLocal() as db:
        for label in labels:
            ticket = db.get(Ticket, label["ticket"])
            if ticket is None:
                raise SystemExit(f"Missing seed case {label['ticket']}")
            run = process_ticket(db, ticket, "heldout-evaluation")
            decisions[run.decision] += 1
            intents[label["intent"]] += 1
            passed = run.intent == label["intent"] and run.decision == label["decision"] and (label["reason"] is None or label["reason"] in run.reason_codes)
            correct += passed
            matched_by_intent[label["intent"]] += passed
            model_latencies.extend(step["latency_ms"] for step in run.trace if step.get("status") == "ok" and "latency_ms" in step)
            if run.cost_usd > 0:
                model_costs.append(run.cost_usd)
            if not passed:
                failures.append({"ticket": ticket.id, "expected": label, "actual": {"intent": run.intent, "decision": run.decision, "reasons": run.reason_codes}})
            if run.decision == "simulated_sent" and (label["decision"] != "simulated_sent" or run.proposed_action not in {"status_reply", "payment_status_reply", "product_fact_reply"}):
                unsafe_sends += 1
    report = {"labeled_cases": len(labels), "matched": correct, "match_rate": round(correct / len(labels), 3),
              "per_intent": {intent: {"matched": matched_by_intent[intent], "cases": count} for intent, count in sorted(intents.items())},
              "unsafe_simulated_sends": unsafe_sends, "escalation_rate": round(decisions["escalate"] / len(labels), 3),
              "model_latency_ms_mean": round(sum(model_latencies) / len(model_latencies), 1) if model_latencies else None,
              "model_cost_usd_mean": round(sum(model_costs) / len(model_costs), 8) if model_costs else None,
              "decisions": dict(decisions), "failures": failures}
    print(json.dumps(report, indent=2))
    if failures or unsafe_sends:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
