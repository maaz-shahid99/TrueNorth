"""Live model integration (PL-1/PL-4) — opt-in, real Anthropic calls, costs money.

Skipped by default so the suite and CI stay offline and free. To run:

    TRUENORTH_LIVE_TESTS=1 ANTHROPIC_API_KEY=sk-ant-... \
        conda run -n truenorth pytest engine/tests/test_live_integration.py -v

These exercise the real client.messages.parse structured-output path end to end and the
golden set against the live model — the Phase 8 "make it real" verification.
"""

from __future__ import annotations

import os

import pytest

from truenorth_engine.config import Settings
from truenorth_engine.eval.golden import GOLDEN_CASES
from truenorth_engine.eval.runner import run_eval
from truenorth_engine.pipeline import evaluate_decision
from truenorth_engine.schemas import Verdict

_LIVE = os.getenv("TRUENORTH_LIVE_TESTS") == "1"
_HAS_KEY = bool(os.getenv("ANTHROPIC_API_KEY"))

pytestmark = pytest.mark.skipif(
    not (_LIVE and _HAS_KEY),
    reason="set TRUENORTH_LIVE_TESTS=1 and ANTHROPIC_API_KEY to run live model tests",
)

_VALID_VERDICTS = {
    Verdict.ENDORSE,
    Verdict.ENDORSE_WITH_CONDITIONS,
    Verdict.CAUTION,
    Verdict.OPPOSE,
}


def test_live_single_decision_smoke():
    """One real decision flows through the pipeline and yields a well-formed verdict."""
    settings = Settings()  # picks up ANTHROPIC_API_KEY from env
    case = next(c for c in GOLDEN_CASES if c.id == "discount-deep-low-margin")

    record = evaluate_decision(
        case.request.model_copy(deep=True), settings, evidence=case.evidence
    )

    assert record.recommendation.verdict in _VALID_VERDICTS
    assert record.recommendation.minority_report.strip(), "minority report must be substantive"
    assert 0.0 <= record.recommendation.confidence <= 1.0
    assert record.lenses, "at least one lens must engage"
    assert record.usage.total_cost_usd > 0, "live calls must record a non-zero cost"


def test_live_golden_set_passes():
    """The full golden set stays within its judgment bands against the live model."""
    report = run_eval(GOLDEN_CASES, Settings())
    failed = [r.case_id for r in report.results if not r.passed]
    assert report.pass_rate >= 0.75, f"golden pass rate {report.pass_rate:.0%}; failing: {failed}"
