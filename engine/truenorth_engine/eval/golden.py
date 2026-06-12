"""Golden decision set (PL-4).

A small, curated set of decision scenarios with evidence injected directly (so runs are
deterministic and need no network) and expectations about what a sound judgment looks
like. These are not exact-answer assertions — judgment is not deterministic — but bands
the engine must stay within: an acceptable verdict set, lenses that must engage, and
confidence ceilings when evidence is thin. Regressions show up as cases falling out of
band.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ..schemas import (
    DecisionRequest,
    EvidenceItem,
    EvidencePack,
    LensName,
    StakesTier,
    Verdict,
)


class GoldenCase(BaseModel):
    id: str
    request: DecisionRequest
    evidence: EvidencePack | None = Field(
        default=None, description="Injected to bypass connectors; None lets the engine gather."
    )
    acceptable_verdicts: list[Verdict]
    must_engage_lenses: list[LensName] = Field(default_factory=list)
    expect_conditions: bool | None = Field(
        default=None, description="True: require conditions; False: forbid; None: don't care."
    )
    min_confidence: float | None = None
    max_confidence: float | None = None
    note: str = ""


GOLDEN_CASES: list[GoldenCase] = [
    GoldenCase(
        id="release-risky-many-bugs",
        request=DecisionRequest(
            decision_type="release_go_no_go",
            question="Ship release 2.4 tonight despite the open bug backlog?",
            stakes=StakesTier.S3,
            context="Marketing wants it out before a launch event tomorrow.",
        ),
        evidence=EvidencePack(
            items=[
                EvidenceItem(
                    claim="Open bug-labelled issues",
                    value="37",
                    source="github:acme/app/issues?label=bug",
                ),
                EvidenceItem(
                    claim="Recent CI pass rate (last completed runs)",
                    value="55% of 20",
                    source="github:acme/app/actions/runs",
                ),
                EvidenceItem(
                    claim="Open pull requests",
                    value="14",
                    source="github:acme/app/pulls",
                ),
            ],
            sufficiency="adequate",
        ),
        acceptable_verdicts=[Verdict.CAUTION, Verdict.OPPOSE, Verdict.ENDORSE_WITH_CONDITIONS],
        must_engage_lenses=[LensName.RISK],
        note="High open-bug count and weak CI must not yield an unconditional Endorse.",
    ),
    GoldenCase(
        id="release-clean",
        request=DecisionRequest(
            decision_type="release_go_no_go",
            question="Ship release 2.5 after a clean QA cycle?",
            stakes=StakesTier.S3,
            context="Standard monthly release; rollback path tested.",
        ),
        evidence=EvidencePack(
            items=[
                EvidenceItem(
                    claim="Open bug-labelled issues",
                    value="0",
                    source="github:acme/app/issues?label=bug",
                ),
                EvidenceItem(
                    claim="Recent CI pass rate (last completed runs)",
                    value="100% of 20",
                    source="github:acme/app/actions/runs",
                ),
                EvidenceItem(
                    claim="Open pull requests",
                    value="1",
                    source="github:acme/app/pulls",
                ),
            ],
            sufficiency="adequate",
        ),
        acceptable_verdicts=[Verdict.ENDORSE, Verdict.ENDORSE_WITH_CONDITIONS],
        must_engage_lenses=[LensName.RISK, LensName.CUSTOMER],
        note="Clean signals should support shipping, possibly with light conditions.",
    ),
    GoldenCase(
        id="release-thin-evidence",
        request=DecisionRequest(
            decision_type="release_go_no_go",
            question="Ship release 3.0 — the evidence connector returned nothing?",
            stakes=StakesTier.S3,
            context="The repo could not be reached; no signals were gathered.",
        ),
        evidence=EvidencePack(
            sufficiency="unavailable",
            notes="No repository supplied for the GitHub connector.",
        ),
        acceptable_verdicts=[
            Verdict.CAUTION,
            Verdict.OPPOSE,
            Verdict.ENDORSE_WITH_CONDITIONS,
        ],
        must_engage_lenses=[LensName.RISK],
        max_confidence=0.8,
        note="With no evidence, confidence must stay modest and the verdict must not be a clean Endorse.",
    ),
]
