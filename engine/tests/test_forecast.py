"""Scenario forecast tests (SF-1/SF-2, offline): runs for high stakes, skipped for low."""

from __future__ import annotations

from truenorth_engine.config import Settings
from truenorth_engine.eval.fakes import ScriptedGateway
from truenorth_engine.pipeline import evaluate_decision
from truenorth_engine.schemas import (
    DecisionRequest,
    DevilsAdvocate,
    EvidencePack,
    LensAssessment,
    Recommendation,
    Scenario,
    ScenarioForecast,
    StakesTier,
    Verdict,
)


class _ForecastFakeGateway:
    def structured(self, *, output_format, **kwargs):
        if output_format is LensAssessment:
            return LensAssessment(leaning=Verdict.CAUTION, rationale="r", confidence=0.5)
        if output_format is DevilsAdvocate:
            return DevilsAdvocate(counter_case="c")
        if output_format is ScenarioForecast:
            return ScenarioForecast(
                summary="Wide range of outcomes.",
                scenarios=[
                    Scenario(name="Expected", probability=0.6, projection="Steady", drivers=["x"]),
                    Scenario(name="Worst case", probability=0.2, projection="Outage", drivers=["y"]),
                ],
            )
        if output_format is Recommendation:
            return Recommendation(
                verdict=Verdict.CAUTION, reasoning="z", confidence=0.5, minority_report="m"
            )
        raise RuntimeError(f"no canned output for {output_format.__name__}")


def test_forecast_attached_for_high_stakes():
    request = DecisionRequest(
        decision_type="project_go_no_go", question="Bet the company on X?", stakes=StakesTier.S1
    )
    record = evaluate_decision(
        request,
        Settings(anthropic_api_key=""),
        gateway=_ForecastFakeGateway(),
        evidence=EvidencePack(sufficiency="thin"),
    )
    assert record.forecast is not None
    assert [s.name for s in record.forecast.scenarios] == ["Expected", "Worst case"]


def test_no_forecast_for_low_stakes():
    request = DecisionRequest(
        decision_type="release_go_no_go", question="Routine ship?", stakes=StakesTier.S4
    )
    record = evaluate_decision(
        request,
        Settings(anthropic_api_key=""),
        gateway=ScriptedGateway(),  # never asked for a ScenarioForecast at low stakes
        evidence=EvidencePack(sufficiency="thin"),
    )
    assert record.forecast is None
