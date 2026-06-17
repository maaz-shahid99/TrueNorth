"""Precedent retrieval tests (KG / DI-2, offline): ranking logic + store integration."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from truenorth_engine.precedent import rank_precedents, summarize_outcomes
from truenorth_engine.schemas import (
    DecisionRecord,
    DecisionRequest,
    DevilsAdvocate,
    EvidencePack,
    Outcome,
    Recommendation,
    ReviewState,
    StakesTier,
    Verdict,
)


def _record(question: str, decision_type: str, verdict: Verdict, ago_days: int = 1) -> DecisionRecord:
    return DecisionRecord(
        request=DecisionRequest(decision_type=decision_type, question=question),
        stakes=StakesTier.S3,
        model_used="claude-haiku-4-5",
        evidence=EvidencePack(sufficiency="thin"),
        lenses=[],
        devils_advocate=DevilsAdvocate(counter_case="c"),
        recommendation=Recommendation(
            verdict=verdict, reasoning="r", confidence=0.5, minority_report="m"
        ),
        review_required=False,
        review_state=ReviewState.NOT_REQUIRED,
        created_at=datetime.now(timezone.utc) - timedelta(days=ago_days),
    )


def test_ranks_more_similar_decision_first():
    request = DecisionRequest(
        decision_type="release_go_no_go",
        question="Should we ship the mobile checkout release tonight?",
    )
    candidates = [
        _record("Approve a discount for the Globex renewal?", "discount_approval", Verdict.CAUTION),
        _record("Should we ship the mobile checkout release this week?", "release_go_no_go", Verdict.OPPOSE),
        _record("Hire a new platform engineer?", "hiring_approval", Verdict.ENDORSE),
    ]
    result = rank_precedents(request, candidates, limit=3)
    assert result, "expected at least one precedent"
    assert "checkout release" in result[0].question  # the closest match ranks first
    assert result[0].verdict == Verdict.OPPOSE


def test_excludes_identical_submission_and_low_similarity():
    request = DecisionRequest(
        decision_type="release_go_no_go", question="Ship the nightly build now?"
    )
    candidates = [
        _record("Ship the nightly build now?", "release_go_no_go", Verdict.ENDORSE),  # identical
        _record("Relocate the Berlin office next year?", "project_go_no_go", Verdict.CAUTION),
    ]
    result = rank_precedents(request, candidates, limit=5)
    assert all(p.question != "Ship the nightly build now?" for p in result)


def test_limit_is_respected():
    request = DecisionRequest(decision_type="release_go_no_go", question="Ship release alpha beta?")
    candidates = [
        _record(f"Ship release alpha beta gamma {i}?", "release_go_no_go", Verdict.CAUTION)
        for i in range(5)
    ]
    assert len(rank_precedents(request, candidates, limit=2)) == 2


def test_summarize_outcomes():
    assert summarize_outcomes([]) == ""
    success = Outcome(decision_id="d1", realized="shipped cleanly", success=True)
    assert summarize_outcomes([success]).startswith("success:")
    miss = Outcome(decision_id="d1", realized="rolled back", success=False)
    assert summarize_outcomes([miss]).startswith("miss:")


def test_store_find_precedents_fills_outcomes(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'p.db').as_posix()}")
    from truenorth_engine import store
    from truenorth_engine.config import get_settings

    get_settings.cache_clear()
    store._engine_for.cache_clear()
    s = store.get_store(get_settings())

    past = _record("Ship the payments service release tonight?", "release_go_no_go", Verdict.OPPOSE)
    s.record_decision(past, "default")
    s.record_outcome(
        Outcome(decision_id=past.id, realized="caused a Sev1 outage", success=False), "default"
    )

    new_request = DecisionRequest(
        decision_type="release_go_no_go", question="Should we ship the payments service release?"
    )
    precedents = s.find_precedents(new_request, "default")
    assert precedents
    assert precedents[0].decision_id == past.id
    assert precedents[0].outcome_summary.startswith("miss:")

    get_settings.cache_clear()
    store._engine_for.cache_clear()
