"""Deterministic grader (PL-4).

Given a golden case and the DecisionRecord the engine produced, score it against the
case's expectation bands. Pure logic — no model, no network — so it is fully testable
offline and serves as the regression oracle.
"""

from __future__ import annotations

from pydantic import BaseModel

from ..schemas import DecisionRecord, Verdict
from .golden import GoldenCase


class CheckResult(BaseModel):
    name: str
    passed: bool
    detail: str = ""


class CaseResult(BaseModel):
    case_id: str
    passed: bool
    verdict: Verdict
    checks: list[CheckResult]


def grade_case(case: GoldenCase, record: DecisionRecord) -> CaseResult:
    rec = record.recommendation
    checks: list[CheckResult] = []

    checks.append(
        CheckResult(
            name="verdict-acceptable",
            passed=rec.verdict in case.acceptable_verdicts,
            detail=f"got {rec.verdict.value}; acceptable "
            f"{[v.value for v in case.acceptable_verdicts]}",
        )
    )

    engaged = {sl.lens for sl in record.lenses if sl.assessment.applicable}
    for lens in case.must_engage_lenses:
        checks.append(
            CheckResult(
                name=f"lens-engaged:{lens.value}",
                passed=lens in engaged,
                detail="engaged" if lens in engaged else "lens did not engage / declared N/A",
            )
        )

    checks.append(
        CheckResult(
            name="minority-report-present",
            passed=bool(rec.minority_report.strip()),
            detail="present" if rec.minority_report.strip() else "empty minority report",
        )
    )

    if rec.verdict == Verdict.ENDORSE_WITH_CONDITIONS:
        checks.append(
            CheckResult(
                name="conditions-present-for-conditional",
                passed=len(rec.conditions) > 0,
                detail=f"{len(rec.conditions)} condition(s)",
            )
        )

    if case.expect_conditions is True:
        checks.append(
            CheckResult(
                name="conditions-expected",
                passed=len(rec.conditions) > 0,
                detail=f"{len(rec.conditions)} condition(s)",
            )
        )
    elif case.expect_conditions is False:
        checks.append(
            CheckResult(
                name="conditions-not-expected",
                passed=len(rec.conditions) == 0,
                detail=f"{len(rec.conditions)} condition(s)",
            )
        )

    if case.max_confidence is not None:
        checks.append(
            CheckResult(
                name="confidence-at-or-below-ceiling",
                passed=rec.confidence <= case.max_confidence,
                detail=f"{rec.confidence:.2f} vs ceiling {case.max_confidence:.2f}",
            )
        )
    if case.min_confidence is not None:
        checks.append(
            CheckResult(
                name="confidence-at-or-above-floor",
                passed=rec.confidence >= case.min_confidence,
                detail=f"{rec.confidence:.2f} vs floor {case.min_confidence:.2f}",
            )
        )

    return CaseResult(
        case_id=case.id,
        passed=all(c.passed for c in checks),
        verdict=rec.verdict,
        checks=checks,
    )
