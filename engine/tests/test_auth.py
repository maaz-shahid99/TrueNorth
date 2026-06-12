"""Auth/RBAC tests (offline, in-memory SQLite). Mint, resolve, revoke, and role gates."""

from __future__ import annotations

import pytest

from truenorth_engine.auth.keys import KeyStore
from truenorth_engine.auth.rbac import Permission, Role
from truenorth_engine.store.db import init_db, make_engine, make_session_factory


@pytest.fixture
def keystore():
    engine = make_engine("sqlite://")
    init_db(engine)
    return KeyStore(make_session_factory(engine))


def test_mint_and_resolve(keystore):
    key, info = keystore.mint("acme", "alice", [Role.REQUESTER])
    principal = keystore.resolve(key)
    assert principal is not None
    assert principal.tenant_id == "acme"
    assert principal.subject == "alice"
    assert principal.can(Permission.DECISION_CREATE)
    assert not principal.can(Permission.REVIEW_ACT)
    assert not principal.can(Permission.ADMIN)
    assert info.tenant_id == "acme"


def test_resolve_unknown_key_returns_none(keystore):
    assert keystore.resolve("tn_not_a_real_key") is None


def test_revoke_disables_key(keystore):
    key, info = keystore.mint("acme", "svc", [Role.VIEWER])
    assert keystore.resolve(key) is not None
    assert keystore.revoke(info.id, "acme") is True
    assert keystore.resolve(key) is None


def test_admin_has_all_permissions(keystore):
    key, _ = keystore.mint("acme", "root", [Role.ADMIN])
    principal = keystore.resolve(key)
    assert all(principal.can(perm) for perm in Permission)


def test_reviewer_can_act_but_not_create(keystore):
    key, _ = keystore.mint("acme", "rev", [Role.REVIEWER])
    principal = keystore.resolve(key)
    assert principal.can(Permission.REVIEW_ACT)
    assert not principal.can(Permission.DECISION_CREATE)


def test_list_is_scoped_to_tenant(keystore):
    keystore.mint("acme", "a", [Role.VIEWER])
    keystore.mint("other", "b", [Role.VIEWER])
    assert len(keystore.list("acme")) == 1
    assert len(keystore.list("other")) == 1
