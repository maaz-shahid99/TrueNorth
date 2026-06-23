"""Policy engine tests (GV-1/GV-2, offline): matching, store CRUD, and the review gate."""

from __future__ import annotations

from truenorth_engine.config import Settings
from truenorth_engine.eval.fakes import ScriptedGateway
from truenorth_engine.pipeline import evaluate_decision
from truenorth_engine.policy import evaluate_policies, requires_review
from truenorth_engine.schemas import (
    DecisionRequest,
    EvidencePack,
    Policy,
    PolicyCondition,
    StakesTier,
    Verdict,
)


def _eval(policies, **kw):
    base = dict(
        decision_type="release_go_no_go",
        stakes=StakesTier.S3,
        verdict=Verdict.ENDORSE,
        has_alignment_conflict=False,
        cost_usd=0.0,
    )
    base.update(kw)
    return evaluate_policies(policies, **base)


def test_min_stakes_fires_at_or_above_threshold():
    p = Policy(name="exec sign-off", condition=PolicyCondition(min_stakes=StakesTier.S2))
    assert _eval([p], stakes=StakesTier.S1)  # S1 more severe than S2 -> fires
    assert _eval([p], stakes=StakesTier.S2)
    assert not _eval([p], stakes=StakesTier.S3)  # less severe -> no


def test_decision_type_and_verdict_filters():
    p = Policy(
        name="oppose releases",
        condition=PolicyCondition(decision_types=["release_go_no_go"], verdicts=[Verdict.OPPOSE]),
    )
    assert _eval([p], verdict=Verdict.OPPOSE)
    assert not _eval([p], verdict=Verdict.ENDORSE)
    assert not _eval([p], decision_type="discount_approval", verdict=Verdict.OPPOSE)


def test_alignment_conflict_and_cost_conditions():
    conflict = Policy(name="conflict", condition=PolicyCondition(on_alignment_conflict=True))
    assert _eval([conflict], has_alignment_conflict=True)
    assert not _eval([conflict], has_alignment_conflict=False)

    pricey = Policy(name="pricey", condition=PolicyCondition(min_cost_usd=1.0))
    assert _eval([pricey], cost_usd=2.5)
    assert not _eval([pricey], cost_usd=0.5)


def test_archived_policy_is_ignored_and_effect_drives_review():
    archived = Policy(name="old", status="archived", condition=PolicyCondition())
    assert _eval([archived]) == []

    flag_only = Policy(name="flag", effect="flag", condition=PolicyCondition())
    gate = Policy(name="gate", effect="require_review", condition=PolicyCondition())
    assert requires_review(_eval([flag_only])) is False
    assert requires_review(_eval([gate])) is True


def test_pipeline_policy_forces_review_for_low_stakes():
    policy = Policy(
        name="All releases need review",
        condition=PolicyCondition(decision_types=["release_go_no_go"]),
        effect="require_review",
    )
    record = evaluate_decision(
        DecisionRequest(decision_type="release_go_no_go", question="Ship?", stakes=StakesTier.S4),
        Settings(anthropic_api_key=""),
        gateway=ScriptedGateway(),
        evidence=EvidencePack(sufficiency="thin"),
        policies=[policy],
    )
    assert record.review_required is True  # S4 would not normally need review
    assert record.review_state == "pending"
    assert record.policy_flags[0].name == "All releases need review"


def test_pipeline_no_policies_keeps_low_stakes_unreviewed():
    record = evaluate_decision(
        DecisionRequest(decision_type="release_go_no_go", question="Ship?", stakes=StakesTier.S4),
        Settings(anthropic_api_key=""),
        gateway=ScriptedGateway(),
        evidence=EvidencePack(sufficiency="thin"),
    )
    assert record.review_required is False
    assert record.policy_flags == []


def test_policy_store_crud(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'pol.db').as_posix()}")
    from truenorth_engine import store
    from truenorth_engine.config import get_settings

    get_settings.cache_clear()
    store._engine_for.cache_clear()
    s = store.get_store(get_settings())

    p = s.add_policy(Policy(name="exec sign-off", condition=PolicyCondition(min_stakes="S2")), "default")
    assert [x.name for x in s.list_policies("default")] == ["exec sign-off"]
    assert s.archive_policy(p.id, "default") is True
    assert s.list_policies("default") == []
    assert s.archive_policy("nope", "default") is False

    get_settings.cache_clear()
    store._engine_for.cache_clear()
