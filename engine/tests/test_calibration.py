"""Calibration tests (DI-6/DI-8, offline): the pure report + the API round-trip."""

from __future__ import annotations

from truenorth_engine.calibration import compute_calibration
from truenorth_engine.schemas import (
    DecisionRecord,
    DecisionRequest,
    DevilsAdvocate,
    EvidencePack,
    Outcome,
    Recommendation,
    ReviewState,
    StakesTier,
    Verdict,
)


def _decision(verdict: Verdict, confidence: float, did: str) -> DecisionRecord:
    return DecisionRecord(
        id=did,
        request=DecisionRequest(decision_type="release_go_no_go", question="Ship?"),
        stakes=StakesTier.S3,
        model_used="m",
        evidence=EvidencePack(sufficiency="thin"),
        lenses=[],
        devils_advocate=DevilsAdvocate(counter_case="c"),
        recommendation=Recommendation(
            verdict=verdict, reasoning="r", confidence=confidence, minority_report="m"
        ),
        review_required=False,
        review_state=ReviewState.NOT_REQUIRED,
    )


def test_calibration_computes_coverage_rates_and_brier():
    decisions = [
        _decision(Verdict.ENDORSE, 0.9, "d1"),
        _decision(Verdict.ENDORSE, 0.8, "d2"),
        _decision(Verdict.OPPOSE, 0.6, "d3"),  # no outcome
    ]
    outcomes = {
        "d1": [Outcome(decision_id="d1", realized="went well", success=True)],
        "d2": [Outcome(decision_id="d2", realized="regressed", success=False)],
    }
    report = compute_calibration(decisions, outcomes)

    assert report.total_decisions == 3
    assert report.decisions_with_outcomes == 2
    assert report.scored_outcomes == 2
    assert abs(report.outcome_coverage - 2 / 3) < 1e-9

    endorse = next(v for v in report.by_verdict if v.verdict == Verdict.ENDORSE)
    assert endorse.with_outcomes == 2
    assert endorse.success_rate == 0.5  # one success, one failure

    oppose = next(v for v in report.by_verdict if v.verdict == Verdict.OPPOSE)
    assert oppose.success_rate is None  # no scored outcome

    # Brier = mean((0.9-1)^2, (0.8-0)^2) = (0.01 + 0.64)/2 = 0.325
    assert report.brier_score == 0.325


def test_calibration_empty_is_safe():
    report = compute_calibration([], {})
    assert report.total_decisions == 0
    assert report.outcome_coverage == 0.0
    assert report.brier_score is None


def test_uses_latest_scored_outcome():
    decisions = [_decision(Verdict.CAUTION, 0.7, "d1")]
    outcomes = {
        "d1": [
            Outcome(decision_id="d1", realized="early read", success=True),
            Outcome(decision_id="d1", realized="final read", success=False),
        ]
    }
    report = compute_calibration(decisions, outcomes)
    caution = next(v for v in report.by_verdict if v.verdict == Verdict.CAUTION)
    assert caution.success_rate == 0.0  # latest outcome (failure) wins
