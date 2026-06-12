"""FastAPI auth dependencies (SC-1).

`get_principal` extracts the API key from `Authorization: Bearer <key>` or `X-API-Key`
and resolves it to a Principal (401 on missing/invalid). `require(*perms)` builds a
dependency that also enforces RBAC (403 on insufficient permissions).
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Header, HTTPException

from ..config import get_settings
from .keys import get_keystore
from .rbac import Permission, Principal


def _extract_token(authorization: str | None, x_api_key: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    if x_api_key:
        return x_api_key.strip()
    return None


def get_principal(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> Principal:
    token = _extract_token(authorization, x_api_key)
    if not token:
        raise HTTPException(status_code=401, detail="Missing API key.")
    principal = get_keystore(get_settings()).resolve(token)
    if principal is None:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key.")
    return principal


def require(*permissions: Permission) -> Callable[..., Principal]:
    def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if not all(principal.can(p) for p in permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        return principal

    return dependency
