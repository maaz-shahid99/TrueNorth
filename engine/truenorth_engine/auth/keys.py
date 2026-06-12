"""API-key store (SC-1): mint, resolve, list, revoke.

`resolve` is the seam an OIDC/JWT verifier would replace: credential string in, Principal
out. Keys are high-entropy random tokens, so a fast SHA-256 lookup hash is sufficient
(these are not user-chosen passwords).
"""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ..config import Settings
from ..store import get_session_factory
from .models import ApiKey
from .rbac import Principal, Role

_KEY_PREFIX = "tn_"


class ApiKeyInfo(BaseModel):
    id: str
    tenant_id: str
    subject: str
    roles: list[Role]
    active: bool
    created_at: str


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _generate_key() -> str:
    return _KEY_PREFIX + secrets.token_urlsafe(32)


class KeyStore:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def mint(self, tenant_id: str, subject: str, roles: list[Role]) -> tuple[str, ApiKeyInfo]:
        key = _generate_key()
        info = ApiKeyInfo(
            id=uuid4().hex,
            tenant_id=tenant_id,
            subject=subject,
            roles=roles,
            active=True,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._sf.begin() as session:
            session.add(
                ApiKey(
                    id=info.id,
                    tenant_id=tenant_id,
                    subject=subject,
                    key_hash=_hash(key),
                    roles=json.dumps([r.value for r in roles]),
                    active=True,
                    created_at=info.created_at,
                )
            )
        return key, info

    def resolve(self, key: str) -> Principal | None:
        with self._sf() as session:
            row = session.execute(
                select(ApiKey).where(ApiKey.key_hash == _hash(key), ApiKey.active.is_(True))
            ).scalar_one_or_none()
            if row is None:
                return None
            roles = [Role(r) for r in json.loads(row.roles)]
            return Principal(tenant_id=row.tenant_id, subject=row.subject, roles=roles)

    def list(self, tenant_id: str) -> list[ApiKeyInfo]:
        with self._sf() as session:
            rows = (
                session.execute(select(ApiKey).where(ApiKey.tenant_id == tenant_id))
                .scalars()
                .all()
            )
            return [
                ApiKeyInfo(
                    id=r.id,
                    tenant_id=r.tenant_id,
                    subject=r.subject,
                    roles=[Role(x) for x in json.loads(r.roles)],
                    active=r.active,
                    created_at=r.created_at,
                )
                for r in rows
            ]

    def revoke(self, key_id: str, tenant_id: str = "default") -> bool:
        with self._sf.begin() as session:
            row = session.execute(
                select(ApiKey).where(ApiKey.id == key_id, ApiKey.tenant_id == tenant_id)
            ).scalar_one_or_none()
            if row is None:
                return False
            row.active = False
            return True


def get_keystore(settings: Settings) -> KeyStore:
    return KeyStore(get_session_factory(settings))
