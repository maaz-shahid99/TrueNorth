"""Google SSO verification and TrueNorth session JWTs (SC-1).

`verify_engine_jwt` is the JWT half of the auth resolver seam beside `KeyStore.resolve`
(see deps.py): a bearer token is tried as a TrueNorth JWT first, then as an API key. Google
ID-token verification uses google-auth and is imported lazily so the rest of the engine
doesn't depend on it at import time.
"""

from __future__ import annotations

import time
from typing import Any

import jwt as pyjwt

from ..config import Settings
from .rbac import Principal, Role

_ALG = "HS256"


def mint_engine_jwt(
    *,
    subject: str,
    tenant: str,
    roles: list[Role],
    secret: str,
    ttl_seconds: int = 3600,
) -> str:
    now = int(time.time())
    payload = {
        "sub": subject,
        "tenant": tenant,
        "roles": [r.value for r in roles],
        "iat": now,
        "exp": now + ttl_seconds,
        "iss": "truenorth",
    }
    return pyjwt.encode(payload, secret, algorithm=_ALG)


def verify_engine_jwt(token: str, secret: str) -> Principal | None:
    if not secret or not token:
        return None
    try:
        payload = pyjwt.decode(
            token, secret, algorithms=[_ALG], options={"require": ["exp", "sub"]}
        )
    except pyjwt.PyJWTError:
        return None

    roles: list[Role] = []
    for r in payload.get("roles", []):
        try:
            roles.append(Role(r))
        except ValueError:
            continue
    return Principal(
        tenant_id=payload.get("tenant") or "default",
        subject=str(payload["sub"]),
        roles=roles,
    )


def verify_google_id_token(token: str, client_id: str) -> dict[str, Any] | None:
    """Verify a Google ID token's signature and audience; returns its claims or None."""
    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token

        return google_id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
    except Exception:
        return None


def principal_from_google(info: dict[str, Any], settings: Settings) -> Principal:
    """Map verified Google claims to a Principal: tenant = email domain, admins by allowlist."""
    email = str(info.get("email") or "")
    domain = email.split("@")[-1].lower() if "@" in email else "default"
    admins = {e.lower() for e in settings.sso_admin_emails}
    roles = [Role.ADMIN] if email.lower() in admins else [Role.REQUESTER]
    return Principal(tenant_id=domain or "default", subject=email, roles=roles)
