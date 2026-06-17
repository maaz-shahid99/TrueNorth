"""Rate-limit tests (offline): the window logic in isolation and the 429 path via the API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from truenorth_engine.auth.ratelimit import FixedWindowRateLimiter


def test_allows_up_to_limit_then_blocks():
    rl = FixedWindowRateLimiter()
    # Pin the clock so the test is deterministic (no sleeps).
    assert rl.check("k", limit=2, now=100.0) is None
    assert rl.check("k", limit=2, now=100.5) is None
    blocked = rl.check("k", limit=2, now=101.0)
    assert blocked is not None and blocked > 0  # seconds until reset


def test_window_resets_after_expiry():
    rl = FixedWindowRateLimiter()
    assert rl.check("k", limit=1, window_s=60.0, now=0.0) is None
    assert rl.check("k", limit=1, window_s=60.0, now=30.0) is not None  # still in window
    assert rl.check("k", limit=1, window_s=60.0, now=61.0) is None  # window rolled over


def test_keys_are_independent():
    rl = FixedWindowRateLimiter()
    assert rl.check("tenant-a:alice", limit=1, now=0.0) is None
    assert rl.check("tenant-b:bob", limit=1, now=0.0) is None  # different key, fresh budget
    assert rl.check("tenant-a:alice", limit=1, now=0.0) is not None


def test_limit_zero_disables():
    rl = FixedWindowRateLimiter()
    for _ in range(5):
        assert rl.check("k", limit=0, now=0.0) is None


@pytest.fixture
def rate_limited_client(monkeypatch, tmp_path):
    db = tmp_path / "rl.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db.as_posix()}")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")

    from truenorth_engine import store
    from truenorth_engine.config import get_settings

    get_settings.cache_clear()
    store._engine_for.cache_clear()

    import truenorth_engine.api as api
    from truenorth_engine.auth.keys import get_keystore
    from truenorth_engine.auth.ratelimit import _limiter
    from truenorth_engine.auth.rbac import Role
    from truenorth_engine.schemas import (
        DecisionRecord,
        DecisionRequest,
        DevilsAdvocate,
        EvidencePack,
        Recommendation,
        ReviewState,
        StakesTier,
        Verdict,
    )

    def _fake_record(request: DecisionRequest) -> DecisionRecord:
        return DecisionRecord(
            request=request,
            stakes=StakesTier.S4,
            model_used="claude-haiku-4-5",
            evidence=EvidencePack(sufficiency="thin"),
            lenses=[],
            devils_advocate=DevilsAdvocate(counter_case="y"),
            recommendation=Recommendation(
                verdict=Verdict.CAUTION, reasoning="z", confidence=0.5, minority_report="m"
            ),
            review_required=False,
            review_state=ReviewState.NOT_REQUIRED,
        )

    _limiter.reset()
    monkeypatch.setattr(
        api, "evaluate_decision", lambda request, settings, **kwargs: _fake_record(request)
    )

    key, _ = get_keystore(get_settings()).mint("default", "alice", [Role.REQUESTER])
    yield TestClient(api.app), key

    _limiter.reset()
    get_settings.cache_clear()
    store._engine_for.cache_clear()


def test_api_returns_429_when_limit_exceeded(rate_limited_client):
    tc, key = rate_limited_client
    body = {"decision_type": "release_go_no_go", "question": "Ship?"}
    headers = {"X-API-Key": key}

    assert tc.post("/v1/decisions", json=body, headers=headers).status_code == 200
    assert tc.post("/v1/decisions", json=body, headers=headers).status_code == 200
    third = tc.post("/v1/decisions", json=body, headers=headers)
    assert third.status_code == 429
    assert "Retry-After" in third.headers
