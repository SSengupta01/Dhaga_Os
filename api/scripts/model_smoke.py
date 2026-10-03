"""Live model compatibility check. Run with OPENROUTER_API_KEY configured."""
import os
import sys

from dhaga.llm import classify, evaluate


def main():
    if not os.getenv("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY is required for the live model smoke test", file=sys.stderr)
        return 2
    extraction, first = classify("Mera order ORD000001 kaha hai?")
    if extraction is None or extraction.intent != "wismo":
        print({"classifier": first}, file=sys.stderr)
        return 1
    verdict, second = evaluate("Where is ORD000001?", {"order_id": "ORD000001", "status": "packed"}, "Order ORD000001 is packed.")
    if verdict is None or not verdict.grounded:
        print({"evaluator": second}, file=sys.stderr)
        return 1
    print({"classifier": first, "evaluator": second})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
