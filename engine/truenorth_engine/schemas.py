"""Canonical data model for the decision engine.

These Pydantic models ARE the L4 schema from the plan, enforced in code. The verdict
scale and stakes tiers match the immutable canon in docs/00-shared-specification.md.
The structured-output models (LensAssessment, Recommendation) are passed to
client.messages.parse() so Claude must return exactly this shape.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    ENDORSE = "Endorse"
    ENDORSE_WITH_CONDITIONS = "Endorse-with-conditions"
    CAUTION = "Caution"
    OPPOSE = "Oppose"


class StakesTier(str, Enum):
    S1 = "S1"  # existential / board-level
    S2 = "S2"  # executive
    S3 = "S3"  # departmental
    S4 = "S4"  # team / routine


class LensName(str, Enum):
    FINANCIAL = "financial"
    STRATEGIC = "strategic"
    RISK = "risk"
    LEGAL = "legal"
    PEOPLE = "people"
    CUSTOMER = "customer"
    ESG = "esg"


class ReviewState(str, Enum):
    NOT_REQUIRED = "not_required"  # stakes below the review threshold
    PENDING = "pending"  # awaiting human sign-off
    APPROVED = "approved"
    REJECTED = "rejected"


# ----- Inputs --------------------------------------------------------------------

class DecisionRequest(BaseModel):
    """What a team brings to TrueNorth. Maps to DI-1 decision capture."""

    decision_type: str = Field(description="e.g. 'release_go_no_go'")
    question: str = Field(description="The decision being made, in one sentence.")
    options: list[str] = Field(
        default_factory=list,
        description="Candidate options. 'Do nothing' is added automatically if absent.",
    )
    context: str = Field(default="", description="Free-text background from the team.")
    stakes: StakesTier | None = Field(
        default=None, description="If omitted, the engine classifies it (DI-1-3)."
    )
    # Connector hints — for release_go_no_go, the GitHub repo to gather evidence from.
    repo: str | None = Field(default=None, description="owner/name for the GitHub connector.")
    # Structured connector inputs, e.g. discount_approval deal facts (discount_pct, etc.).
    inputs: dict[str, str] = Field(default_factory=dict)


# ----- Evidence (DI-2) -----------------------------------------------------------

class EvidenceItem(BaseModel):
    claim: str
    value: str
    source: str = Field(description="Citation back to origin (DF-5 lineage).")


class EvidencePack(BaseModel):
    items: list[EvidenceItem] = Field(default_factory=list)
    sufficiency: str = Field(
        default="unknown", description="strong | adequate | thin | unavailable"
    )
    notes: str = ""


# ----- Lens assessments (DI-3) — structured-output target ------------------------

class LensAssessment(BaseModel):
    """One domain judge's independent assessment. Returned by Claude via structured output."""

    leaning: Verdict = Field(description="This lens's standalone verdict.")
    rationale: str = Field(description="2-4 sentences, grounded in the cited evidence.")
    key_risks: list[str] = Field(default_factory=list)
    cited_evidence: list[str] = Field(
        default_factory=list, description="Which evidence claims this lens relied on."
    )
    confidence: float = Field(ge=0.0, le=1.0)
    applicable: bool = Field(default=True, description="False if this lens does not apply.")


class ScoredLens(BaseModel):
    lens: LensName
    assessment: LensAssessment


# ----- Devil's advocate (DI-5) ---------------------------------------------------

class DevilsAdvocate(BaseModel):
    counter_case: str = Field(description="The strongest good-faith argument the decision fails.")
    failure_conditions: list[str] = Field(default_factory=list)
    bias_flags: list[str] = Field(
        default_factory=list, description="groupthink / sunk-cost / anchoring etc. (process only)."
    )


# ----- Recommendation (DI-4) — structured-output target --------------------------

class Condition(BaseModel):
    text: str = Field(description="Specific, checkable condition.")
    owner: str = ""
    checkpoint: str = ""


class Recommendation(BaseModel):
    """The single artifact a human reviews. Returned by Claude via structured output."""

    verdict: Verdict
    reasoning: str = Field(description="Why this verdict, citing the lenses that drove it.")
    confidence: float = Field(ge=0.0, le=1.0)
    conditions: list[Condition] = Field(
        default_factory=list, description="Required for Endorse-with-conditions."
    )
    minority_report: str = Field(
        description="The strongest argument against this verdict. Must be non-empty."
    )


# ----- Telemetry & cost (PL-6) ---------------------------------------------------

class CallUsage(BaseModel):
    step: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0


class UsageSummary(BaseModel):
    calls: list[CallUsage] = Field(default_factory=list)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    total_latency_ms: int = 0


# ----- Institutional memory / precedent (KG, deepens DI-2) -----------------------

class Precedent(BaseModel):
    """A similar past decision surfaced for the current one, with how it turned out."""

    decision_id: str
    question: str
    decision_type: str
    verdict: Verdict
    stakes: StakesTier
    created_at: datetime
    similarity: float = Field(ge=0.0, le=1.0, description="0–1 lexical similarity score.")
    outcome_summary: str = Field(
        default="", description="Short summary of the recorded outcome, if any."
    )


# ----- Goals & strategy alignment (GA) -------------------------------------------

class GoalLevel(str, Enum):
    BOARD = "board"  # board / company-level objective
    DEPARTMENT = "department"  # departmental OKR
    TEAM = "team"  # team-level goal


class Goal(BaseModel):
    """A strategic goal / OKR the org is pursuing (board -> department -> team cascade)."""

    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    title: str
    description: str = ""
    level: GoalLevel = GoalLevel.DEPARTMENT
    owner: str = ""
    parent_id: str | None = Field(default=None, description="The higher-level goal this rolls up to.")
    metric: str = Field(default="", description="How progress is measured.")
    status: Literal["active", "archived"] = "active"
    source: str = Field(default="manual", description="manual or a connector citation, e.g. jira:KEY.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GoalRequest(BaseModel):
    """Fields a caller supplies to create a goal; the id/status/timestamps are server-set."""

    title: str
    description: str = ""
    level: GoalLevel = GoalLevel.DEPARTMENT
    owner: str = ""
    parent_id: str | None = None
    metric: str = ""


class GoalLink(BaseModel):
    """How a decision relates to one goal, as judged by the alignment step."""

    goal_id: str
    title: str
    relation: Literal["advances", "conflicts", "neutral"]
    note: str = ""


class GoalAlignment(BaseModel):
    """The alignment step's structured judgment of a decision against active goals (GA-4)."""

    score: float = Field(ge=0.0, le=1.0, description="Overall strategic alignment, 0–1.")
    rationale: str = Field(default="", description="One or two sentences on the overall fit.")
    advances: list[GoalLink] = Field(default_factory=list)
    conflicts: list[GoalLink] = Field(default_factory=list)


# ----- Simulation & forecasting (SF-1 / SF-2) ------------------------------------

class Scenario(BaseModel):
    """One plausible future if the decision proceeds."""

    name: str = Field(description="Short label, e.g. 'Expected', 'Best case', 'Worst case'.")
    probability: float = Field(ge=0.0, le=1.0, description="Rough likelihood, 0–1.")
    projection: str = Field(description="What happens in this scenario and its impact.")
    drivers: list[str] = Field(default_factory=list, description="Key factors that lead here.")


class ScenarioForecast(BaseModel):
    """Structured what-if projection for a high-stakes decision (SF-1/SF-2)."""

    summary: str = Field(default="", description="One-line overall outlook.")
    scenarios: list[Scenario] = Field(default_factory=list)


# ----- Governance: policy / decision-rights engine (GV-1 / GV-2) -----------------

class PolicyCondition(BaseModel):
    """Attribute conditions that trigger a policy (all set conditions must match — AND)."""

    decision_types: list[str] = Field(default_factory=list, description="Empty = any type.")
    min_stakes: StakesTier | None = Field(
        default=None, description="Trigger when stakes are at or above this tier (S1 highest)."
    )
    verdicts: list[Verdict] = Field(default_factory=list, description="Empty = any verdict.")
    on_alignment_conflict: bool = Field(
        default=False, description="Trigger only when the decision conflicts with a goal."
    )
    min_cost_usd: float | None = Field(
        default=None, description="Trigger when the decision's model spend is at least this."
    )


class Policy(BaseModel):
    """A decision-rights rule: when its condition matches, it gates or flags the decision."""

    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str
    description: str = ""
    condition: PolicyCondition = Field(default_factory=PolicyCondition)
    effect: Literal["require_review", "flag"] = "require_review"
    required_role: Literal["reviewer", "admin"] = "reviewer"
    status: Literal["active", "archived"] = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PolicyRequest(BaseModel):
    """Fields a caller supplies to create a policy; id/status/timestamp are server-set."""

    name: str
    description: str = ""
    condition: PolicyCondition = Field(default_factory=PolicyCondition)
    effect: Literal["require_review", "flag"] = "require_review"
    required_role: Literal["reviewer", "admin"] = "reviewer"


class PolicyFlag(BaseModel):
    """A policy that fired on a decision, recorded on the decision for audit (GV-3)."""

    policy_id: str
    name: str
    effect: Literal["require_review", "flag"]
    required_role: str = ""
    reason: str = ""


# ----- Full decision record (the audit artifact, GV-3) ---------------------------

class DecisionRecord(BaseModel):
    id: str = Field(
        default_factory=lambda: uuid4().hex,
        description="Stable, citable record id; the key used by the audit store.",
    )
    request: DecisionRequest
    stakes: StakesTier
    model_used: str
    evidence: EvidencePack
    lenses: list[ScoredLens]
    devils_advocate: DevilsAdvocate
    recommendation: Recommendation
    review_required: bool = Field(
        default=False, description="Whether stakes require human sign-off (DI-7 / GV-2)."
    )
    review_state: ReviewState = ReviewState.NOT_REQUIRED
    precedents: list[Precedent] = Field(
        default_factory=list,
        description="Similar past decisions the judge was shown (KG / DI-2 institutional memory).",
    )
    alignment: GoalAlignment | None = Field(
        default=None,
        description="Strategic alignment vs. active goals (GA-4); None when no goals are set.",
    )
    forecast: ScenarioForecast | None = Field(
        default=None,
        description="What-if scenarios (SF-1/SF-2); only generated for high-stakes decisions.",
    )
    policy_flags: list[PolicyFlag] = Field(
        default_factory=list,
        description="Decision-rights policies that fired on this decision (GV-1/GV-2).",
    )
    safety_flags: list[str] = Field(
        default_factory=list,
        description="Prompt-injection / poisoning patterns detected in the inputs (SC-3).",
    )
    usage: UsageSummary = Field(default_factory=UsageSummary)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "0.1.0"


# ----- Outcome tracking (DI-8 learning loop) -------------------------------------

class OutcomeRequest(BaseModel):
    """What a human reports after the fact; the decision id comes from the URL path."""

    realized: str = Field(description="What actually happened after the decision.")
    success: bool | None = Field(
        default=None, description="Did the outcome match the recommendation's intent?"
    )
    metrics: dict[str, str] = Field(
        default_factory=dict, description="Realized metrics, e.g. {'rollback': 'no'}."
    )
    notes: str = ""
    recorded_by: str = ""


class Outcome(OutcomeRequest):
    decision_id: str = Field(description="The decision this outcome belongs to.")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ----- Audit integrity (GV-3) ----------------------------------------------------

class ChainVerification(BaseModel):
    ok: bool
    entries_checked: int
    broken_at_seq: int | None = None
    detail: str = ""


# ----- Human review / sign-off (DI-7 / GV-2) -------------------------------------

class ReviewActionInput(BaseModel):
    """What a reviewer submits; the decision id and actor come from the request."""

    action: Literal["approve", "reject"]
    note: str = ""


class ReviewAction(ReviewActionInput):
    decision_id: str
    actor: str = Field(description="The reviewer's principal subject.")
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReviewStatus(BaseModel):
    decision_id: str
    required: bool
    state: ReviewState
    history: list[ReviewAction] = Field(default_factory=list)


# ----- Meeting intelligence (MI-2: decision & commitment extraction) --------------

class ExtractedDecision(BaseModel):
    """One candidate decision lifted from a meeting transcript, for a human to confirm."""

    question: str = Field(description="The decision phrased as a question, ready to judge.")
    decision_type: str = Field(
        default="other",
        description="Best-guess type: release_go_no_go | discount_approval | hiring_approval "
        "| vendor_procurement | budget_spend | project_go_no_go | other.",
    )
    owner: str = Field(default="", description="Who owns the decision / action, if stated.")
    deadline: str = Field(default="", description="Stated deadline or timeframe, if any.")
    context: str = Field(default="", description="Short context drawn from the discussion.")
    dissent: str = Field(default="", description="Recorded disagreement or concern, if any.")


class MeetingExtraction(BaseModel):
    """Structured-output target for the extraction step (MI-2)."""

    summary: str = Field(default="", description="One or two sentences summarizing the meeting.")
    decisions: list[ExtractedDecision] = Field(default_factory=list)


# ----- Calibration & learning loop (DI-8 / DI-6) ---------------------------------

class VerdictOutcomeStat(BaseModel):
    verdict: Verdict
    decisions: int = 0  # all decisions with this verdict
    with_outcomes: int = 0  # those with a recorded success/failure
    success_rate: float | None = None  # fraction of with_outcomes that succeeded


class ConfidenceBucket(BaseModel):
    label: str
    n: int
    predicted_confidence: float  # mean engine confidence in this bucket
    realized_success_rate: float  # fraction that actually succeeded


class CalibrationReport(BaseModel):
    """How well verdicts/confidence predict realized outcomes (DI-6/DI-8 learning loop)."""

    total_decisions: int = 0
    decisions_with_outcomes: int = 0
    outcome_coverage: float = 0.0  # decisions_with_outcomes / total
    scored_outcomes: int = 0  # outcomes carrying a definite success/failure
    brier_score: float | None = None  # mean (confidence - success)^2; lower is better
    by_verdict: list[VerdictOutcomeStat] = Field(default_factory=list)
    confidence_buckets: list[ConfidenceBucket] = Field(default_factory=list)
