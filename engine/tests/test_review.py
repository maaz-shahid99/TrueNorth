"""Review-gate tests (DI-7 / GV-2): which tiers require sign-off, and state derivation."""

from __future__ import annotations

from truenorth_engine.config import Settings
from truenorth_engine.review import compute_state, review_required
from truenorth_engine.schemas import ReviewAction, ReviewState, StakesTier


def test_default_required_tiers():
    settings = Settings()
    assert review_required(StakesTier.S1, settings) is True
    assert review_required(StakesTier.S2, settings) is True
    assert review_required(StakesTier.S3, settings) is False
    assert review_required(StakesTier.S4, settings) is False


def test_pending_when_required_and_no_actions():
    assert compute_state(True, []) == ReviewState.PENDING


def test_not_required_when_below_threshold():
    assert compute_state(False, []) == ReviewState.NOT_REQUIRED


def test_approve_sets_approved():
    action = ReviewAction(decision_id="d1", actor="rev", action="approve")
    assert compute_state(True, [action]) == ReviewState.APPROVED


def test_reject_overrides_approve():
    approve = ReviewAction(decision_id="d1", actor="r1", action="approve")
    reject = ReviewAction(decision_id="d1", actor="r2", action="reject")
    assert compute_state(True, [approve, reject]) == ReviewState.REJECTED
