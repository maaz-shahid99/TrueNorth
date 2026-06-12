"""Minimal CLI so you can judge a decision from the terminal without the web stack.

    truenorth "Should we ship release 2.4 tonight?" --repo owner/name --type release_go_no_go
"""

from __future__ import annotations

import argparse
import sys

from .pipeline import evaluate_decision
from .schemas import DecisionRequest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="truenorth", description="Judge a decision.")
    parser.add_argument("question", help="The decision, in one sentence.")
    parser.add_argument("--type", default="release_go_no_go", dest="decision_type")
    parser.add_argument("--repo", default=None, help="owner/name for the GitHub connector.")
    parser.add_argument("--context", default="")
    parser.add_argument("--option", action="append", default=[], dest="options")
    args = parser.parse_args(argv)

    request = DecisionRequest(
        decision_type=args.decision_type,
        question=args.question,
        options=args.options,
        context=args.context,
        repo=args.repo,
    )
    record = evaluate_decision(request)
    rec = record.recommendation
    print(f"\nVERDICT: {rec.verdict.value}   (stakes {record.stakes.value}, "
          f"model {record.model_used}, confidence {rec.confidence:.2f})\n")
    print(f"Reasoning: {rec.reasoning}\n")
    if rec.conditions:
        print("Conditions:")
        for c in rec.conditions:
            print(f"  - {c.text}")
        print()
    print(f"Minority report: {rec.minority_report}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
