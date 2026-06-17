"""Goals & alignment tests (GA, offline): store CRUD, connector degradation, pipeline."""

from __future__ import annotations

from truenorth_engine.config import Settings
from truenorth_engine.eval.fakes import ScriptedGateway
from truenorth_engine.goals import gather_goals
from truenorth_engine.goals.jira_goals import gather_jira_goals
from truenorth_engine.pipeline import evaluate_decision
from truenorth_engine.schemas import (
    DecisionRequest,
    DevilsAdvocate,
    EvidencePack,
    Goal,
    GoalAlignment,
    GoalLink,
    LensAssessment,
    Recommendation,
    StakesTier,
    Verdict,
)


class _AlignFakeGateway:
    """Covers every structured-output step including the alignment step."""

    def structured(self, *, output_format, **kwargs):
        if output_format is LensAssessment:
            return LensAssessment(leaning=Verdict.CAUTION, rationale="r", confidence=0.5)
        if output_format is DevilsAdvocate:
            return DevilsAdvocate(counter_case="c")
        if output_format is GoalAlignment:
            return GoalAlignment(
                score=0.3,
                rationale="weak strategic fit",
                conflicts=[GoalLink(goal_id="g1", title="Grow ARR 30%", relation="conflicts")],
            )
        if output_format is Recommendation:
            return Recommendation(
                verdict=Verdict.CAUTION, reasoning="z", confidence=0.5, minority_report="m"
            )
        raise RuntimeError(f"no canned output for {output_format.__name__}")


def _store(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'g.db').as_posix()}")
    from truenorth_engine import store
    from truenorth_engine.config import get_settings

    get_settings.cache_clear()
    store._engine_for.cache_clear()
    return store, get_settings, store.get_store(get_settings())


def test_goal_store_crud(tmp_path, monkeypatch):
    store, get_settings, s = _store(tmp_path, monkeypatch)
    goal = s.add_goal(Goal(title="Grow ARR 30%", level="board"), "default")
    assert [g.title for g in s.list_goals("default")] == ["Grow ARR 30%"]

    assert s.archive_goal(goal.id, "default") is True
    assert s.list_goals("default") == []  # archived goals are hidden by default
    assert any(g.id == goal.id for g in s.list_goals("default", include_archived=True))
    assert s.archive_goal("does-not-exist", "default") is False

    get_settings.cache_clear()
    store._engine_for.cache_clear()


def test_gather_goals_includes_stored_goals(tmp_path, monkeypatch):
    store, get_settings, s = _store(tmp_path, monkeypatch)
    s.add_goal(Goal(title="Cut infra cost 20%"), "default")
    goals = gather_goals(s, get_settings(), "default")  # Jira unconfigured -> stored only
    assert [g.title for g in goals] == ["Cut infra cost 20%"]

    get_settings.cache_clear()
    store._engine_for.cache_clear()


def test_jira_goals_empty_without_config():
    assert gather_jira_goals(None, None, None, None) == []
    assert gather_jira_goals("https://x.atlassian.net", "e", "t", None) == []  # no JQL


def test_pipeline_attaches_alignment_when_goals_present():
    request = DecisionRequest(
        decision_type="release_go_no_go", question="Ship the risky release?", stakes=StakesTier.S3
    )
    record = evaluate_decision(
        request,
        Settings(anthropic_api_key=""),
        gateway=_AlignFakeGateway(),
        evidence=EvidencePack(sufficiency="thin"),
        goals=[Goal(id="g1", title="Grow ARR 30%")],
    )
    assert record.alignment is not None
    assert record.alignment.score == 0.3
    assert record.alignment.conflicts[0].title == "Grow ARR 30%"


def test_pipeline_alignment_none_without_goals():
    request = DecisionRequest(
        decision_type="release_go_no_go", question="Ship it?", stakes=StakesTier.S3
    )
    record = evaluate_decision(
        request,
        Settings(anthropic_api_key=""),
        gateway=ScriptedGateway(),  # never asked for GoalAlignment when there are no goals
        evidence=EvidencePack(sufficiency="thin"),
    )
    assert record.alignment is None
