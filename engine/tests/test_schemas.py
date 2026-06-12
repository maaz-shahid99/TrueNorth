"""Schema and routing tests that run without an API key (the increment-1 test step).

These verify the canon is encoded correctly and the gateway routes by stakes. The
live end-to-end run (real Claude calls) is exercised via the CLI once a key is set.
"""

from __future__ import annotations

import pytest

from truenorth_engine.config import Settings
from truenorth_engine.lenses import lenses_for
from truenorth_engine.schemas import (
    DecisionRequest,
    LensAssessment,
    Recommendation,
    StakesTier,
    Verdict,
)


def test_verdict_scale_is_canonical():
    assert [v.value for v in Verdict] == [
        "Endorse",
        "Endorse-with-conditions",
        "Caution",
        "Oppose",
    ]


def test_stakes_routing_distinct_models():
    s = Settings(
        truenorth_model_s1="claude-opus-4-8",
        truenorth_model_s3="claude-sonnet-4-6",
        truenorth_model_s4="claude-haiku-4-5",
    )
    assert s.model_for_tier(StakesTier.S1) == "claude-opus-4-8"
    assert s.model_for_tier(StakesTier.S3) == "claude-sonnet-4-6"
    assert s.model_for_tier(StakesTier.S4) == "claude-haiku-4-5"


def test_release_lenses_include_risk():
    lenses = lenses_for("release_go_no_go")
    assert any(lens.value == "risk" for lens in lenses)


def test_recommendation_requires_minority_report():
    with pytest.raises(Exception):
        Recommendation(verdict=Verdict.ENDORSE, reasoning="ok", confidence=0.9)  # missing field


def test_confidence_bounds_enforced():
    with pytest.raises(Exception):
        LensAssessment(leaning=Verdict.ENDORSE, rationale="x", confidence=1.5)


def test_decision_request_defaults():
    req = DecisionRequest(decision_type="release_go_no_go", question="Ship 2.4?")
    assert req.options == []
    assert req.stakes is None
