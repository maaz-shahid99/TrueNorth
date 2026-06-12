"""SQLAlchemy ORM for the immutable audit ledger (GV-3).

A single append-only table holds every governed event — each decision record and each
recorded outcome — linked into a per-tenant SHA-256 hash chain so any later tampering
with a stored row is detectable. There are deliberately no update or delete paths.
"""

from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuditEntry(Base):
    """One link in the tamper-evident chain. Written once, never modified."""

    __tablename__ = "audit_entries"

    seq: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(128), index=True)
    entry_type: Mapped[str] = mapped_column(String(32))  # "decision" | "outcome"
    decision_id: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[str] = mapped_column(Text)  # canonical JSON of the record/outcome
    prev_hash: Mapped[str] = mapped_column(String(64))
    entry_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[str] = mapped_column(String(40))  # ISO-8601 UTC, hashed verbatim
