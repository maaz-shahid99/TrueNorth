"""Scripted gateway for offline harness runs and tests.

Returns canned structured outputs without calling any model, so the eval harness can be
exercised end to end with no API key (CI dry-run) and so the grader can be tested
against known-good and known-bad judgments.

All golden cases pin their stakes tier, so the pipeline never asks this gateway to
classify stakes — only lens, devil's-advocate, and recommendation outputs are needed.
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from ..schemas import (
    Condition,
    DevilsAdvocate,
    LensAssessment,
    Recommendation,
    StakesTier,
    Verdict,
)

T = TypeVar("T", bound=BaseModel)


class ScriptedGateway:
    def __init__(
        self,
        *,
        verdict: Verdict = Verdict.ENDORSE_WITH_CONDITIONS,
        lens_leaning: Verdict = Verdict.CAUTION,
        confidence: float = 0.6,
        with_conditions: bool = True,
    ) -> None:
        self.verdict = verdict
        self.lens_leaning = lens_leaning
        self.confidence = confidence
        self.with_conditions = with_conditions

    def structured(
        self,
        *,
        tier: StakesTier,
        instruction: str,
        output_format: type[T],
        max_tokens: int = 4000,
        use_thinking: bool = False,
    ) -> T:
        if output_format is LensAssessment:
            return LensAssessment(  # type: ignore[return-value]
                leaning=self.lens_leaning,
                rationale="scripted lens rationale",
                confidence=self.confidence,
                applicable=True,
            )
        if output_format is DevilsAdvocate:
            return DevilsAdvocate(  # type: ignore[return-value]
                counter_case="scripted counter-case",
                failure_conditions=["scripted failure condition"],
                bias_flags=[],
            )
        if output_format is Recommendation:
            conditions = [Condition(text="scripted condition")] if self.with_conditions else []
            return Recommendation(  # type: ignore[return-value]
                verdict=self.verdict,
                reasoning="scripted reasoning",
                confidence=self.confidence,
                conditions=conditions,
                minority_report="scripted minority report",
            )
        raise RuntimeError(
            f"ScriptedGateway has no canned output for {output_format.__name__}"
        )
