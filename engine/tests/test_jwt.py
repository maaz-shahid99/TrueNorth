"""JWT tests (SC-1): mint/verify roundtrip and the resolver guarantees behind Google SSO."""

from __future__ import annotations

from truenorth_engine.auth.jwt import mint_engine_jwt, verify_engine_jwt
from truenorth_engine.auth.rbac import Permission, Role


def test_mint_and_verify_roundtrip():
    token = mint_engine_jwt(
        subject="alice@acme.com", tenant="acme.com", roles=[Role.REQUESTER], secret="s3cret"
    )
    principal = verify_engine_jwt(token, "s3cret")
    assert principal is not None
    assert principal.subject == "alice@acme.com"
    assert principal.tenant_id == "acme.com"
    assert principal.can(Permission.DECISION_CREATE)
    assert not principal.can(Permission.ADMIN)


def test_verify_rejects_wrong_secret():
    token = mint_engine_jwt(subject="a", tenant="t", roles=[Role.ADMIN], secret="right")
    assert verify_engine_jwt(token, "wrong") is None


def test_verify_empty_secret_or_token_returns_none():
    assert verify_engine_jwt("anything", "") is None
    assert verify_engine_jwt("", "secret") is None


def test_admin_jwt_grants_all_permissions():
    token = mint_engine_jwt(subject="root@acme.com", tenant="acme.com", roles=[Role.ADMIN], secret="k")
    principal = verify_engine_jwt(token, "k")
    assert principal is not None
    assert all(principal.can(p) for p in Permission)
