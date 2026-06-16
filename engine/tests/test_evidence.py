"""Connector tests (DF-1, offline): registry dispatch, discount inputs, lens routing."""

from __future__ import annotations

from truenorth_engine.config import Settings
from truenorth_engine.evidence import CONNECTORS, gather_evidence
from truenorth_engine.evidence.discount import ManualDiscountConnector
from truenorth_engine.evidence.github import GitHubReleaseConnector
from truenorth_engine.evidence.jira import JiraProjectConnector, gather_jira_evidence
from truenorth_engine.evidence.manual import hiring_connector, vendor_connector
from truenorth_engine.lenses import lenses_for
from truenorth_engine.schemas import DecisionRequest, LensName


def _settings(**kw) -> Settings:
    base = dict(anthropic_api_key="", github_token="")
    base.update(kw)
    return Settings(**base)


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


# ----- Phase 9: new decision types + connectors -----------------------------------


def test_all_new_decision_types_are_registered():
    for dtype in ("hiring_approval", "vendor_procurement", "budget_spend", "project_go_no_go"):
        assert dtype in CONNECTORS


def test_manual_facts_connector_builds_evidence():
    request = DecisionRequest(
        decision_type="hiring_approval",
        question="Approve a Staff Engineer hire?",
        inputs={
            "role": "Staff Engineer",
            "level": "L6",
            "base_salary_usd": "210000",
            "headcount_plan": "yes",
        },
    )
    pack = hiring_connector().gather(request, _settings())
    assert pack.sufficiency == "adequate"
    assert len(pack.items) == 4


def test_manual_facts_connector_without_inputs_is_unavailable():
    request = DecisionRequest(decision_type="vendor_procurement", question="Approve vendor?")
    assert vendor_connector().gather(request, _settings()).sufficiency == "unavailable"


def test_lens_routing_for_new_types():
    assert LensName.PEOPLE in lenses_for("hiring_approval")
    assert LensName.LEGAL in lenses_for("vendor_procurement")
    assert LensName.FINANCIAL in lenses_for("budget_spend")
    assert LensName.STRATEGIC in lenses_for("project_go_no_go")


def test_jira_evidence_unavailable_without_config():
    pack = gather_jira_evidence(base_url=None, email=None, token=None, project=None)
    assert pack.sufficiency == "unavailable"


def test_project_connector_falls_back_to_manual_facts_without_jira():
    request = DecisionRequest(
        decision_type="project_go_no_go",
        question="Greenlight the migration project?",
        inputs={
            "objective": "Migrate billing to the new platform",
            "budget_usd": "250000",
            "timeline_months": "6",
        },
    )
    pack = JiraProjectConnector().gather(request, _settings())
    assert pack.sufficiency == "adequate"
    assert len(pack.items) == 3
    assert all(item.source == "manual:requester" for item in pack.items)


def test_project_connector_unavailable_with_nothing():
    request = DecisionRequest(decision_type="project_go_no_go", question="Greenlight?")
    assert JiraProjectConnector().gather(request, _settings()).sufficiency == "unavailable"
