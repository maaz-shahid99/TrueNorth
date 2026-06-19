"""Calibration & learning loop (DI-6 / DI-8).

Pure analytics over recorded decisions and their outcomes: how often does each verdict
actually succeed, and is the engine's stated confidence well-calibrated against reality?
This closes the learning loop — outcomes become a measurable signal on judgment quality,
and the same numbers feed back into trust (and, later, prompt/threshold tuning).

Deterministic and dependency-free, so it is fully testable offline.
"""

from __future__ import annotations

from .schemas import (
    CalibrationReport,
    ConfidenceBucket,
    DecisionRecord,
    Outcome,
    Verdict,
    VerdictOutcomeStat,
)

# (label, lower_inclusive, upper_exclusive) — the last bucket's upper is treated as inclusive.
_BUCKETS = [
    ("<50%", 0.0, 0.5),
    ("50–70%", 0.5, 0.7),
    ("70–85%", 0.7, 0.85),
    ("≥85%", 0.85, 1.01),
]


def _latest_success(outcomes: list[Outcome]) -> bool | None:
    """The most recent definite success/failure for a decision, or None if unscored."""
    for outcome in reversed(outcomes):
        if outcome.success is not None:
            return outcome.success
    return None


def compute_calibration(
    decisions: list[DecisionRecord], outcomes_by_id: dict[str, list[Outcome]]
) -> CalibrationReport:
    total = len(decisions)
    # (verdict, confidence, success) for every decision that has a scored outcome.
    scored: list[tuple[Verdict, float, bool]] = []
    with_outcomes = 0
    for d in decisions:
        outcomes = outcomes_by_id.get(d.id, [])
        if outcomes:
            with_outcomes += 1
        success = _latest_success(outcomes)
        if success is not None:
            scored.append((d.recommendation.verdict, d.recommendation.confidence, success))

    by_verdict: list[VerdictOutcomeStat] = []
    for verdict in Verdict:
        all_n = sum(1 for d in decisions if d.recommendation.verdict == verdict)
        subset = [s for s in scored if s[0] == verdict]
        rate = (sum(1 for s in subset if s[2]) / len(subset)) if subset else None
        by_verdict.append(
            VerdictOutcomeStat(
                verdict=verdict, decisions=all_n, with_outcomes=len(subset), success_rate=rate
            )
        )

    buckets: list[ConfidenceBucket] = []
    for label, lo, hi in _BUCKETS:
        members = [s for s in scored if lo <= s[1] < hi]
        if members:
            buckets.append(
                ConfidenceBucket(
                    label=label,
                    n=len(members),
                    predicted_confidence=sum(s[1] for s in members) / len(members),
                    realized_success_rate=sum(1 for s in members if s[2]) / len(members),
                )
            )

    brier = (
        sum((conf - (1.0 if ok else 0.0)) ** 2 for _, conf, ok in scored) / len(scored)
        if scored
        else None
    )

    return CalibrationReport(
        total_decisions=total,
        decisions_with_outcomes=with_outcomes,
        outcome_coverage=(with_outcomes / total) if total else 0.0,
        scored_outcomes=len(scored),
        brier_score=round(brier, 4) if brier is not None else None,
        by_verdict=by_verdict,
        confidence_buckets=buckets,
    )
