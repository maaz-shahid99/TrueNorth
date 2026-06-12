"""API tests via FastAPI TestClient (offline).

The model call is stubbed, so these exercise auth (401), RBAC (403), tenant isolation,
and the review endpoint end to end without touching Anthropic.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from truenorth_engine.schemas import (
    DecisionRecord,
    DecisionRequest,
    DevilsAdvocate,
    EvidencePack,
    LensAssessment,
    LensName,
    Recommendation,
    ReviewState,
    ScoredLens,
    StakesTier,
    Verdict,
)


def _fake_record(request: DecisionRequest) -> DecisionRecord:
    return DecisionRecord(
        request=request,
        stakes=StakesTier.S2,
        model_used="claude-opus-4-8",
        evidence=EvidencePack(sufficiency="thin"),
        lenses=[
            ScoredLens(
                lens=LensName.RISK,
                assessment=LensAssessment(
                    leaning=Verdict.CAUTION, rationale="x", confidence=0.5
                ),
            )
        ],
        devils_advocate=DevilsAdvocate(counter_case="y"),
        recommendation=Recommendation(
            verdict=Verdict.CAUTION, reasoning="z", confidence=0.5, minority_report="m"
        ),
        review_required=True,
        review_state=ReviewState.PENDING,
    )


@pytest.fixture
def client(monkeypatch, tmp_path):
    db = tmp_path / "api.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db.as_posix()}")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    from truenorth_engine import store
    from truenorth_engine.config import get_settings

    get_settings.cache_clear()
    store._engine_for.cache_clear()

    import truenorth_engine.api as api

    monkeypatch.setattr(api, "evaluate_decision", lambda request, settings: _fake_record(request))

    from truenorth_engine.auth.keys import get_keystore
    from truenorth_engine.auth.rbac import Role

    keystore = get_keystore(get_settings())
    req_key, _ = keystore.mint("default", "alice", [Role.REQUESTER])
    rev_key, _ = keystore.mint("default", "bob", [Role.REVIEWER])
    other_key, _ = keystore.mint("other", "carol", [Role.REQUESTER])

    yield TestClient(api.app), {"requester": req_key, "reviewer": rev_key, "other": other_key}

    get_settings.cache_clear()
    store._engine_for.cache_clear()


def _h(key: str) -> dict[str, str]:
    return {"X-API-Key": key}


def _create(tc: TestClient, key: str):
    return tc.post(
        "/v1/decisions",
        json={"decision_type": "release_go_no_go", "question": "Ship 2.4?"},
        headers=_h(key),
    )


def test_unauthenticated_is_rejected(client):
    tc, _ = client
    assert tc.get("/v1/decisions").status_code == 401


def test_create_then_list(client):
    tc, keys = client
    created = _create(tc, keys["requester"])
    assert created.status_code == 200
    body = created.json()
    assert body["review_required"] is True
    assert body["review_state"] == "pending"

    listed = tc.get("/v1/decisions", headers=_h(keys["requester"]))
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_review_requires_reviewer_role(client):
    tc, keys = client
    decision_id = _create(tc, keys["requester"]).json()["id"]

    forbidden = tc.post(
        f"/v1/decisions/{decision_id}/review",
        json={"action": "approve"},
        headers=_h(keys["requester"]),
    )
    assert forbidden.status_code == 403

    approved = tc.post(
        f"/v1/decisions/{decision_id}/review",
        json={"action": "approve", "note": "lgtm"},
        headers=_h(keys["reviewer"]),
    )
    assert approved.status_code == 200
    assert approved.json()["state"] == "approved"


def test_tenant_isolation(client):
    tc, keys = client
    _create(tc, keys["requester"])  # under tenant "default"
    other = tc.get("/v1/decisions", headers=_h(keys["other"]))
    assert other.status_code == 200
    assert other.json() == []
