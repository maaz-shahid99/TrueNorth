"""Canonical data model for the decision engine.

These Pydantic models ARE the L4 schema from the plan, enforced in code. The verdict
scale and stakes tiers match the immutable canon in docs/00-shared-specification.md.
The structured-output models (LensAssessment, Recommendation) are passed to
client.messages.parse() so Claude must return exactly this shape.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

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


# ----- Full decision record (the audit artifact, GV-3) ---------------------------

class DecisionRecord(BaseModel):
    request: DecisionRequest
    stakes: StakesTier
    model_used: str
    evidence: EvidencePack
    lenses: list[ScoredLens]
    devils_advocate: DevilsAdvocate
    recommendation: Recommendation
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "0.1.0"
