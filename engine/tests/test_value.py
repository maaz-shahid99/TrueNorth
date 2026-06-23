"""Value realization tests (AD-4, offline): ROI, net value, coverage, time-to-outcome."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from truenorth_engine.schemas import (
    CallUsage,
    DecisionRecord,
    DecisionRequest,
    DevilsAdvocate,
    EvidencePack,
    Outcome,
    Recommendation,
    ReviewState,
    StakesTier,
    UsageSummary,
    Verdict,
)
from truenorth_engine.value import compute_value


def _decision(did: str, dtype: str, cost: float, ago_days: int) -> DecisionRecord:
    return DecisionRecord(
        id=did,
        request=DecisionRequest(decision_type=dtype, question="Q?"),
        stakes=StakesTier.S3,
        model_used="m",
        evidence=EvidencePack(sufficiency="thin"),
        lenses=[],
        devils_advocate=DevilsAdvocate(counter_case="c"),
        recommendation=Recommendation(
            verdict=Verdict.ENDORSE, reasoning="r", confidence=0.6, minority_report="m"
        ),
        review_required=False,
        review_state=ReviewState.NOT_REQUIRED,
        usage=UsageSummary(
            calls=[CallUsage(step="s", model="m", cost_usd=cost)], total_cost_usd=cost
        ),
        created_at=datetime.now(timezone.utc) - timedelta(days=ago_days),
    )


def test_value_computes_roi_net_and_time():
    decisions = [
        _decision("d1", "discount_approval", 0.50, ago_days=10),
        _decision("d2", "release_go_no_go", 1.50, ago_days=4),
    ]
    outcomes = {
        "d1": [
            Outcome(
                decision_id="d1",
                realized="margin saved",
                success=True,
                metrics={"value_usd": "1000"},
                recorded_at=datetime.now(timezone.utc) - timedelta(days=8),
            )
        ],
        # d2 has an outcome but no value_usd metric.
        "d2": [
            Outcome(
                decision_id="d2",
                realized="shipped",
                success=True,
                recorded_at=datetime.now(timezone.utc) - timedelta(days=3),
            )
        ],
    }
    report = compute_value(decisions, outcomes)

    assert report.decisions == 2
    assert report.decisions_with_outcomes == 2
    assert report.model_spend_usd == 2.0
    assert report.realized_value_usd == 1000.0
    assert report.net_value_usd == 998.0
    assert report.roi == 500.0  # 1000 / 2
    assert report.median_days_to_outcome is not None
    assert {b.decision_type for b in report.by_type} == {"discount_approval", "release_go_no_go"}


def test_value_roi_none_without_realized_value():
    decisions = [_decision("d1", "release_go_no_go", 0.5, ago_days=1)]
    report = compute_value(decisions, {})  # no outcomes -> no realized value
    assert report.realized_value_usd == 0.0
    assert report.roi is None
    assert report.median_days_to_outcome is None
    assert report.net_value_usd == -0.5  # spend with no value


def test_value_empty_is_safe():
    report = compute_value([], {})
    assert report.decisions == 0
    assert report.model_spend_usd == 0.0
    assert report.roi is None
