"""Eval runner (PL-4): execute the golden set through the real pipeline and grade it.

Pass a ScriptedGateway for an offline dry run; pass nothing for a live run (requires a
configured ANTHROPIC_API_KEY). Evidence is taken from each golden case, so connectors
never run during evaluation.
"""

from __future__ import annotations

from pydantic import BaseModel

from ..config import Settings, get_settings
from ..model_gateway import ModelGateway
from ..pipeline import evaluate_decision
from .golden import GoldenCase
from .grader import CaseResult, grade_case


class EvalReport(BaseModel):
    total: int
    passed: int
    pass_rate: float
    results: list[CaseResult]


def run_eval(
    cases: list[GoldenCase],
    settings: Settings | None = None,
    *,
    gateway: ModelGateway | None = None,
) -> EvalReport:
    settings = settings or get_settings()
    results: list[CaseResult] = []
    for case in cases:
        record = evaluate_decision(
            case.request.model_copy(deep=True),
            settings,
            gateway=gateway,
            evidence=case.evidence,
        )
        results.append(grade_case(case, record))

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    return EvalReport(
        total=total,
        passed=passed,
        pass_rate=(passed / total) if total else 1.0,
        results=results,
    )
