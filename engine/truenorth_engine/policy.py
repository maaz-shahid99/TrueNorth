"""Policy / decision-rights engine (GV-1 / GV-2).

Tenant-configurable rules that decide, per decision, whether human sign-off is required
beyond the default stakes threshold — and surface *why*. Conditions are attribute-based
(decision type, stakes, verdict, goal conflict, model spend), so this is the ABAC-flavoured
layer over the stakes-tiered gate. Pure and deterministic, fully testable offline.
"""

from __future__ import annotations

from .schemas import Policy, PolicyFlag, StakesTier, Verdict

_STAKES_RANK = {StakesTier.S1: 1, StakesTier.S2: 2, StakesTier.S3: 3, StakesTier.S4: 4}


def _reason(policy: Policy, stakes: StakesTier, verdict: Verdict) -> str:
    c = policy.condition
    parts: list[str] = []
    if c.decision_types:
        parts.append(f"type in {c.decision_types}")
    if c.min_stakes is not None:
        parts.append(f"stakes ≥ {c.min_stakes.value} (was {stakes.value})")
    if c.verdicts:
        parts.append(f"verdict {verdict.value}")
    if c.on_alignment_conflict:
        parts.append("conflicts with a goal")
    if c.min_cost_usd is not None:
        parts.append(f"spend ≥ ${c.min_cost_usd:g}")
    return "; ".join(parts) or "always"


def evaluate_policies(
    policies: list[Policy],
    *,
    decision_type: str,
    stakes: StakesTier,
    verdict: Verdict,
    has_alignment_conflict: bool,
    cost_usd: float,
) -> list[PolicyFlag]:
    """Return the flags for every active policy whose condition matches the decision."""
    flags: list[PolicyFlag] = []
    for policy in policies:
        if policy.status != "active":
            continue
        c = policy.condition
        if c.decision_types and decision_type not in c.decision_types:
            continue
        if c.min_stakes is not None and _STAKES_RANK[stakes] > _STAKES_RANK[c.min_stakes]:
            continue  # decision is less severe than the policy's threshold
        if c.verdicts and verdict not in c.verdicts:
            continue
        if c.on_alignment_conflict and not has_alignment_conflict:
            continue
        if c.min_cost_usd is not None and cost_usd < c.min_cost_usd:
            continue
        flags.append(
            PolicyFlag(
                policy_id=policy.id,
                name=policy.name,
                effect=policy.effect,
                required_role=policy.required_role,
                reason=_reason(policy, stakes, verdict),
            )
        )
    return flags


def requires_review(flags: list[PolicyFlag]) -> bool:
    """True if any fired policy gates the decision (effect=require_review)."""
    return any(f.effect == "require_review" for f in flags)
