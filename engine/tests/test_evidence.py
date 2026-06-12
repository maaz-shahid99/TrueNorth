"""Connector tests (DF-1, offline): registry dispatch, discount inputs, lens routing."""

from __future__ import annotations

from truenorth_engine.config import Settings
from truenorth_engine.evidence import gather_evidence
from truenorth_engine.evidence.discount import ManualDiscountConnector
from truenorth_engine.evidence.github import GitHubReleaseConnector
from truenorth_engine.lenses import lenses_for
from truenorth_engine.schemas import DecisionRequest, LensName


def _settings() -> Settings:
    return Settings(anthropic_api_key="", github_token="")


def test_github_connector_without_repo_is_unavailable():
    request = DecisionRequest(decision_type="release_go_no_go", question="Ship?")
    pack = GitHubReleaseConnector().gather(request, _settings())
    assert pack.sufficiency == "unavailable"


def test_discount_connector_builds_evidence_from_inputs():
    request = DecisionRequest(
        decision_type="discount_approval",
        question="Approve 30% off?",
        inputs={
            "discount_pct": "30",
            "gross_margin_pct": "20",
            "customer_tier": "strategic",
            "deal_value": "500000",
        },
    )
    pack = ManualDiscountConnector().gather(request, _settings())
    assert pack.sufficiency == "adequate"
    assert len(pack.items) == 4
    assert all(item.source == "manual:requester" for item in pack.items)


def test_discount_connector_without_inputs_is_unavailable():
    request = DecisionRequest(decision_type="discount_approval", question="Approve?")
    assert ManualDiscountConnector().gather(request, _settings()).sufficiency == "unavailable"


def test_gather_evidence_dispatches_by_type():
    discount = DecisionRequest(
        decision_type="discount_approval",
        question="Approve?",
        inputs={"discount_pct": "10", "gross_margin_pct": "40"},
    )
    assert gather_evidence(discount, _settings()).items  # routed to discount connector

    unknown = DecisionRequest(decision_type="board_vote", question="Approve?")
    assert gather_evidence(unknown, _settings()).sufficiency == "unavailable"


def test_discount_lenses_include_financial():
    assert LensName.FINANCIAL in lenses_for("discount_approval")
