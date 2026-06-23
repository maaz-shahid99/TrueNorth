"""Value realization / decision-ROI attribution (AD-4).

Pure analytics: weigh the value decisions realized (a numeric ``value_usd`` metric that
recorders attach to outcomes) against the engine's own model spend, and report ROI, net
value, coverage, and time-to-outcome. Deterministic and dependency-free; ROI is reported
only when both realized value and spend are present, so it never fabricates a ratio.
"""

from __future__ import annotations

from statistics import median

from .schemas import DecisionRecord, Outcome, ValueByType, ValueReport


def _to_number(raw: str | None) -> float | None:
    if raw is None:
        return None
    try:
        return float(str(raw).replace(",", "").replace("$", "").strip())
    except (TypeError, ValueError):
        return None


def compute_value(
    decisions: list[DecisionRecord], outcomes_by_id: dict[str, list[Outcome]]
) -> ValueReport:
    spend = sum(d.usage.total_cost_usd for d in decisions)
    realized = 0.0
    with_outcomes = 0
    days_to_outcome: list[float] = []
    by_type: dict[str, dict[str, float]] = {}

    for d in decisions:
        bucket = by_type.setdefault(d.request.decision_type, {"decisions": 0.0, "spend": 0.0})
        bucket["decisions"] += 1
        bucket["spend"] += d.usage.total_cost_usd

        outcomes = outcomes_by_id.get(d.id, [])
        if not outcomes:
            continue
        with_outcomes += 1
        latest = outcomes[-1]
        value = _to_number(latest.metrics.get("value_usd")) if latest.metrics else None
        if value is not None:
            realized += value
        delta_days = (latest.recorded_at - d.created_at).total_seconds() / 86400
        if delta_days >= 0:
            days_to_outcome.append(delta_days)

    net = realized - spend
    roi = round(realized / spend, 2) if spend > 0 and realized > 0 else None
    by_type_list = [
        ValueByType(decision_type=k, decisions=int(v["decisions"]), spend_usd=round(v["spend"], 4))
        for k, v in by_type.items()
    ]
    by_type_list.sort(key=lambda x: x.decisions, reverse=True)

    return ValueReport(
        decisions=len(decisions),
        decisions_with_outcomes=with_outcomes,
        model_spend_usd=round(spend, 4),
        realized_value_usd=round(realized, 2),
        net_value_usd=round(net, 2),
        roi=roi,
        median_days_to_outcome=round(median(days_to_outcome), 1) if days_to_outcome else None,
        by_type=by_type_list,
    )
