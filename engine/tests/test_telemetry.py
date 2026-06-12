"""Telemetry/cost tests (PL-6): pricing, aggregation, and the gateway recording path."""

from __future__ import annotations

from types import SimpleNamespace

from truenorth_engine.config import Settings
from truenorth_engine.model_gateway import ModelGateway
from truenorth_engine.schemas import CallUsage, Recommendation, StakesTier, Verdict
from truenorth_engine.telemetry import Telemetry, estimate_cost


def test_estimate_cost_known_model():
    # Haiku: $0.80/Mtok in, $4.00/Mtok out -> 1000 in + 500 out = 0.0008 + 0.002.
    assert estimate_cost("claude-haiku-4-5", 1000, 500) == 0.0028


def test_estimate_cost_unknown_model_is_zero():
    assert estimate_cost("some-future-model", 1000, 500) == 0.0


def test_summary_aggregates_calls():
    t = Telemetry()
    t.record_call(CallUsage(step="a", model="m", input_tokens=100, output_tokens=10, cost_usd=0.001))
    t.record_call(CallUsage(step="b", model="m", input_tokens=200, output_tokens=20, cost_usd=0.002))
    summary = t.summary()
    assert summary.total_input_tokens == 300
    assert summary.total_output_tokens == 30
    assert summary.total_cost_usd == 0.003
    assert len(summary.calls) == 2


def test_gateway_records_usage_with_fake_client():
    telemetry = Telemetry()
    gateway = ModelGateway(Settings(anthropic_api_key=""), telemetry=telemetry)

    rec = Recommendation(
        verdict=Verdict.CAUTION, reasoning="r", confidence=0.5, minority_report="m"
    )
    fake_usage = SimpleNamespace(
        input_tokens=1000,
        output_tokens=500,
        cache_read_input_tokens=0,
        cache_creation_input_tokens=0,
    )
    fake_response = SimpleNamespace(parsed_output=rec, usage=fake_usage, stop_reason="end_turn")
    gateway._client = SimpleNamespace(
        messages=SimpleNamespace(parse=lambda **kwargs: fake_response)
    )

    out = gateway.structured(
        tier=StakesTier.S4, instruction="x", output_format=Recommendation, step="synthesis"
    )
    assert out is rec
    summary = telemetry.summary()
    assert len(summary.calls) == 1
    assert summary.calls[0].step == "synthesis"
    assert summary.total_input_tokens == 1000
    assert summary.total_cost_usd > 0
