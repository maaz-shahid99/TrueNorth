"""CLI for the eval harness (PL-4).

    truenorth-eval --dry-run        # offline, scripted gateway (CI smoke)
    truenorth-eval                  # live run against the configured model

Exit code is non-zero when the pass rate falls below --min-pass-rate, so this doubles as
a CI gate.
"""

from __future__ import annotations

import argparse
import sys

from ..config import get_settings
from .fakes import ScriptedGateway
from .golden import GOLDEN_CASES
from .runner import run_eval


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="truenorth-eval", description="Run the golden-set evaluation (PL-4)."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Use a scripted gateway (no API calls)."
    )
    parser.add_argument("--min-pass-rate", type=float, default=1.0)
    args = parser.parse_args(argv)

    settings = get_settings()
    gateway = ScriptedGateway() if args.dry_run else None
    if gateway is None and not settings.anthropic_api_key:
        print("No ANTHROPIC_API_KEY set. Use --dry-run to exercise the harness offline.")
        return 2

    report = run_eval(GOLDEN_CASES, settings, gateway=gateway)
    for r in report.results:
        print(f"[{'PASS' if r.passed else 'FAIL'}] {r.case_id}  -> {r.verdict.value}")
        for c in r.checks:
            if not c.passed:
                print(f"        x {c.name}: {c.detail}")

    print(f"\n{report.passed}/{report.total} cases passed (pass rate {report.pass_rate:.0%}).")
    if args.dry_run:
        print("(dry run: scripted gateway — validates harness plumbing, not model quality.)")
    return 0 if report.pass_rate >= args.min_pass_rate else 1


if __name__ == "__main__":
    sys.exit(main())
