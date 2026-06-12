"""Multi-lens evaluation (DI-3).

Each lens is an independent domain judge. They run separately and do not see each
other's output, preserving independence. A lens may declare itself not applicable to
a given decision rather than be silently skipped.
"""

from __future__ import annotations

from .schemas import (
    DecisionRequest,
    EvidencePack,
    LensAssessment,
    LensName,
    ScoredLens,
    StakesTier,
)

# Each lens's domain concern, injected into its instruction.
LENS_CONCERNS: dict[LensName, str] = {
    LensName.FINANCIAL: "cost, margin, cash, and financial return of this decision.",
    LensName.STRATEGIC: "alignment with company strategy and long-term positioning.",
    LensName.RISK: "operational, security, reliability, and downside risk, including tail risk.",
    LensName.LEGAL: "legal, regulatory, compliance, and contractual exposure.",
    LensName.PEOPLE: "impact on employees, team load, morale, and on-call/burnout.",
    LensName.CUSTOMER: "impact on customers: experience, trust, churn, and commitments.",
    LensName.ESG: "environmental, social, and governance implications.",
}

# Which lenses apply to which decision type. Risk is always engaged.
APPLICABLE_LENSES: dict[str, list[LensName]] = {
    "release_go_no_go": [
        LensName.RISK,
        LensName.CUSTOMER,
        LensName.STRATEGIC,
        LensName.PEOPLE,
    ],
}
DEFAULT_LENSES = [LensName.RISK, LensName.STRATEGIC, LensName.FINANCIAL, LensName.CUSTOMER]


def lenses_for(decision_type: str) -> list[LensName]:
    return APPLICABLE_LENSES.get(decision_type, DEFAULT_LENSES)


def _lens_instruction(
    lens: LensName, request: DecisionRequest, evidence: EvidencePack
) -> str:
    evidence_block = "\n".join(
        f"- [{i.source}] {i.claim}: {i.value}" for i in evidence.items
    ) or "(no evidence gathered)"
    options = request.options or ["Proceed", "Do nothing"]
    return (
        f"Decision: {request.question}\n"
        f"Options: {', '.join(options)}\n"
        f"Context: {request.context or '(none)'}\n\n"
        f"Evidence (sufficiency: {evidence.sufficiency}):\n{evidence_block}\n\n"
        f"You are the {lens.value.upper()} lens. Judge ONLY through the concern of "
        f"{LENS_CONCERNS[lens]} Assess this decision from that single angle. "
        f"If this concern does not meaningfully apply to this decision, set "
        f"applicable=false and explain briefly."
    )


def run_lenses(gateway, request: DecisionRequest, evidence: EvidencePack, tier: StakesTier):
    """Run each applicable lens as an independent structured call."""
    results: list[ScoredLens] = []
    for lens in lenses_for(request.decision_type):
        assessment: LensAssessment = gateway.structured(
            tier=tier,
            instruction=_lens_instruction(lens, request, evidence),
            output_format=LensAssessment,
            max_tokens=1500,
        )
        results.append(ScoredLens(lens=lens, assessment=assessment))
    return results
