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
    failures = []
    with SessionLocal() as db:
        for label in labels:
            ticket = db.get(Ticket, label["ticket"])
            if ticket is None:
                raise SystemExit(f"Missing seed case {label['ticket']}")
            run = process_ticket(db, ticket, "heldout-evaluation")
            decisions[run.decision] += 1
            passed = run.intent == label["intent"] and run.decision == label["decision"] and (label["reason"] is None or label["reason"] in run.reason_codes)
            correct += passed
            if not passed:
                failures.append({"ticket": ticket.id, "expected": label, "actual": {"intent": run.intent, "decision": run.decision, "reasons": run.reason_codes}})
            if run.decision == "simulated_sent" and (label["decision"] != "simulated_sent" or run.proposed_action not in {"status_reply", "payment_status_reply", "product_fact_reply"}):
                unsafe_sends += 1
    report = {"labeled_cases": len(labels), "matched": correct, "match_rate": round(correct / len(labels), 3),
              "unsafe_simulated_sends": unsafe_sends, "decisions": dict(decisions), "failures": failures}
    print(json.dumps(report, indent=2))
    if failures or unsafe_sends:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
