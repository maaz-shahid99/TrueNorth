"""API-key persistence (SC-1).

Shares the same SQLAlchemy Base as the audit ledger so both tables live in one database.
Only the SHA-256 hash of a key is stored; the plaintext is shown once at mint time and is
not recoverable. Roles are stored as a JSON array of role names.
"""

from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..store.models import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True)
    subject: Mapped[str] = mapped_column(String(256))
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    roles: Mapped[str] = mapped_column(Text)  # JSON array of role names
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(String(40))
