"""Eval-harness tests (offline, scripted gateway).

Verify the grader actually discriminates good judgments from bad ones — otherwise the
golden set would be a rubber stamp.
"""

from __future__ import annotations

from truenorth_engine.eval import GOLDEN_CASES, ScriptedGateway, run_eval
from truenorth_engine.schemas import Verdict


def _case(case_id: str):
    return [c for c in GOLDEN_CASES if c.id == case_id]


def test_dry_run_reports_every_case():
    report = run_eval(GOLDEN_CASES, gateway=ScriptedGateway())
    assert report.total == len(GOLDEN_CASES)
    assert len(report.results) == len(GOLDEN_CASES)


def test_unacceptable_verdict_fails_grader():
    # The risky case forbids a clean Endorse; a gateway that returns one must fail.
    gateway = ScriptedGateway(verdict=Verdict.ENDORSE, with_conditions=False)
    report = run_eval(_case("release-risky-many-bugs"), gateway=gateway)
    result = report.results[0]
    assert result.passed is False
    bad = next(c for c in result.checks if c.name == "verdict-acceptable")
    assert bad.passed is False


def test_acceptable_verdict_passes_grader():
    gateway = ScriptedGateway(verdict=Verdict.CAUTION, with_conditions=False)
    report = run_eval(_case("release-risky-many-bugs"), gateway=gateway)
    assert report.results[0].passed is True


def test_conditional_without_conditions_fails():
    gateway = ScriptedGateway(verdict=Verdict.ENDORSE_WITH_CONDITIONS, with_conditions=False)
    report = run_eval(_case("release-clean"), gateway=gateway)
    result = report.results[0]
    failed = next(c for c in result.checks if c.name == "conditions-present-for-conditional")
    assert failed.passed is False
    assert result.passed is False


def test_confidence_ceiling_enforced_on_thin_evidence():
    gateway = ScriptedGateway(verdict=Verdict.CAUTION, confidence=0.95, with_conditions=False)
    report = run_eval(_case("release-thin-evidence"), gateway=gateway)
    result = report.results[0]
    failed = next(c for c in result.checks if c.name == "confidence-at-or-below-ceiling")
    assert failed.passed is False
