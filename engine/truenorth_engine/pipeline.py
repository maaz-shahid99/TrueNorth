"""Decision pipeline orchestration (the DI engine loop).

Code-controlled workflow — the sequence is fixed and auditable:
  intake/stakes (DI-1) -> evidence (DI-2) -> lenses (DI-3) -> devil's advocate (DI-5)
  -> synthesis (DI-4) -> decision record (GV-3 audit artifact).

This is deliberately NOT an open-ended agent: every step is a discrete, logged call.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .config import Settings, get_settings
from .evidence import gather_evidence
from .lenses import run_lenses
from .model_gateway import ModelGateway
from .review import review_required
from .schemas import (
    DecisionRecord,
    DecisionRequest,
    DevilsAdvocate,
    EvidencePack,
    Recommendation,
    ReviewState,
    StakesTier,
)
from .telemetry import Telemetry


class _StakesClassification(BaseModel):
    stakes: StakesTier
    rationale: str = Field(description="One sentence on why this tier.")


def _classify_stakes(gateway: ModelGateway, request: DecisionRequest) -> StakesTier:
    if request.stakes is not None:
        return request.stakes
    result: _StakesClassification = gateway.structured(
        tier=StakesTier.S4,  # classification is cheap; run on the fast model
        instruction=(
            f"Classify the stakes of this decision into S1 (existential/board), "
            f"S2 (executive), S3 (departmental), or S4 (team/routine). When uncertain, "
            f"round UP to the higher-stakes tier.\n\n"
            f"Decision: {request.question}\nContext: {request.context or '(none)'}"
        ),
        output_format=_StakesClassification,
        max_tokens=400,
        step="stakes-classification",
    )
    return result.stakes


def _gather_evidence(request: DecisionRequest, settings: Settings) -> EvidencePack:
    return gather_evidence(request, settings)


def _run_devils_advocate(gateway, request, evidence, lenses, tier) -> DevilsAdvocate:
    lens_summary = "\n".join(
        f"- {sl.lens.value}: {sl.assessment.leaning.value} — {sl.assessment.rationale}"
        for sl in lenses
    )
    return gateway.structured(
        tier=tier,
        instruction=(
            f"Decision: {request.question}\n\nLens assessments so far:\n{lens_summary}\n\n"
            f"Build the STRONGEST good-faith case that this decision is a mistake. Identify "
            f"the conditions under which it fails and flag any decision-PROCESS biases "
            f"(groupthink, sunk-cost, anchoring). Do not score individuals."
        ),
        output_format=DevilsAdvocate,
        max_tokens=1500,
        step="devils-advocate",
    )


def _synthesize(gateway, request, evidence, lenses, devil, tier, settings) -> Recommendation:
    lens_summary = "\n".join(
        f"- {sl.lens.value} (conf {sl.assessment.confidence:.2f}): "
        f"{sl.assessment.leaning.value} — {sl.assessment.rationale}"
        for sl in lenses
        if sl.assessment.applicable
    )
    use_thinking = _tier_rank(tier) <= _tier_rank(settings.synthesis_thinking_min_tier)
    return gateway.structured(
        tier=tier,
        instruction=(
            f"Decision: {request.question}\n"
            f"Evidence sufficiency: {evidence.sufficiency}\n\n"
            f"Independent lens assessments:\n{lens_summary}\n\n"
            f"Devil's advocate counter-case: {devil.counter_case}\n"
            f"Flagged biases: {', '.join(devil.bias_flags) or 'none'}\n\n"
            f"Synthesize ONE verdict on the canonical scale. Cite the lenses that drove it. "
            f"If positive but contingent, use Endorse-with-conditions and give specific, "
            f"checkable conditions. Set confidence honestly — lower it when evidence is thin "
            f"or lenses disagree. ALWAYS include a substantive minority_report: the strongest "
            f"argument against your own verdict."
        ),
        output_format=Recommendation,
        max_tokens=2500,
        use_thinking=use_thinking,
        step="synthesis",
    )


def _tier_rank(tier: StakesTier) -> int:
    return {StakesTier.S1: 1, StakesTier.S2: 2, StakesTier.S3: 3, StakesTier.S4: 4}[tier]


def evaluate_decision(
    request: DecisionRequest,
    settings: Settings | None = None,
    *,
    gateway: ModelGateway | None = None,
    evidence: EvidencePack | None = None,
) -> DecisionRecord:
    """Run the full pipeline and return the auditable decision record.

    `gateway` and `evidence` may be injected for deterministic evaluation (PL-4); when
    omitted the engine builds a real model gateway and gathers evidence via connectors.
    """
    settings = settings or get_settings()
    telemetry = Telemetry()
    gateway = gateway or ModelGateway(settings, telemetry=telemetry)

    if not request.options:
        request.options = ["Proceed", "Do nothing"]

    tier = _classify_stakes(gateway, request)
    model_used = settings.model_for_tier(tier)
    if evidence is None:
        evidence = _gather_evidence(request, settings)
    lenses = run_lenses(gateway, request, evidence, tier)
    devil = _run_devils_advocate(gateway, request, evidence, lenses, tier)
    recommendation = _synthesize(gateway, request, evidence, lenses, devil, tier, settings)

    needs_review = review_required(tier, settings)
    return DecisionRecord(
        request=request,
        stakes=tier,
        model_used=model_used,
        evidence=evidence,
        lenses=lenses,
        devils_advocate=devil,
        recommendation=recommendation,
        review_required=needs_review,
        review_state=ReviewState.PENDING if needs_review else ReviewState.NOT_REQUIRED,
        usage=telemetry.summary(),
    )
