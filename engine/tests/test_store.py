"""Audit-store tests (offline, in-memory SQLite).

Verify append + read-back, and that the hash chain detects tampering — the core GV-3
guarantee. No API key or network needed.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

from truenorth_engine.schemas import (
    DecisionRecord,
    DecisionRequest,
    DevilsAdvocate,
    EvidencePack,
    LensAssessment,
    LensName,
    Outcome,
    Recommendation,
    ScoredLens,
    StakesTier,
    Verdict,
)
from truenorth_engine.store.db import init_db, make_engine, make_session_factory
from truenorth_engine.store.models import AuditEntry
from truenorth_engine.store.repository import DecisionStore


def _record(question: str = "Ship 2.4 tonight?") -> DecisionRecord:
    return DecisionRecord(
        request=DecisionRequest(decision_type="release_go_no_go", question=question),
        stakes=StakesTier.S3,
        model_used="claude-sonnet-4-6",
        evidence=EvidencePack(sufficiency="thin"),
        lenses=[
            ScoredLens(
                lens=LensName.RISK,
                assessment=LensAssessment(
                    leaning=Verdict.CAUTION, rationale="open bugs", confidence=0.5
                ),
            )
        ],
        devils_advocate=DevilsAdvocate(counter_case="ship could regress checkout"),
        recommendation=Recommendation(
            verdict=Verdict.CAUTION,
            reasoning="thin evidence",
            confidence=0.5,
            minority_report="the fix is urgent enough to justify shipping",
        ),
    )


@pytest.fixture
def store():
    engine = make_engine("sqlite://")
    init_db(engine)
    factory = make_session_factory(engine)
    return DecisionStore(factory), factory


def test_record_and_get_roundtrip(store):
    s, _ = store
    rec = _record()
    s.record_decision(rec)
    fetched = s.get_decision(rec.id)
    assert fetched is not None
    assert fetched.id == rec.id
    assert fetched.recommendation.verdict == Verdict.CAUTION


def test_chain_verifies_across_entries(store):
    s, _ = store
    for q in ("a", "b", "c"):
        s.record_decision(_record(q))
    result = s.verify_chain()
    assert result.ok is True
    assert result.entries_checked == 3


def test_tampering_is_detected(store):
    s, factory = store
    s.record_decision(_record("first"))
    s.record_decision(_record("second"))
    assert s.verify_chain().ok is True

    # Forge an earlier entry directly in the DB, simulating a malicious edit.
    with factory.begin() as session:
        first = session.execute(
            select(AuditEntry).order_by(AuditEntry.seq.asc()).limit(1)
        ).scalar_one()
        first.payload = '{"tampered":true}'

    result = s.verify_chain()
    assert result.ok is False
    assert result.broken_at_seq == 1


def test_outcome_links_to_decision(store):
    s, _ = store
    rec = _record()
    s.record_decision(rec)
    s.record_outcome(
        Outcome(decision_id=rec.id, realized="shipped; one hotfix needed", success=True)
    )
    outcomes = s.get_outcomes(rec.id)
    assert len(outcomes) == 1
    assert outcomes[0].success is True
    assert s.verify_chain().ok is True  # outcomes extend the same chain


def test_list_decisions_newest_first(store):
    s, _ = store
    s.record_decision(_record("older"))
    s.record_decision(_record("newer"))
    listed = s.list_decisions()
    assert listed[0].request.question == "newer"
    assert listed[1].request.question == "older"
