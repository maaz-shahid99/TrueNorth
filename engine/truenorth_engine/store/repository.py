"""Append-only decision store with a verifiable hash chain (GV-3 + DI-8).

Exposes exactly the operations a tamper-evident ledger should: append a decision,
append an outcome, read them back, and verify the whole chain. There is deliberately no
update or delete method — the only way to "change" history is to append a correction.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ..schemas import ChainVerification, DecisionRecord, Outcome, ReviewAction
from .audit import GENESIS, canonical_json, compute_hash
from .models import AuditEntry


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DecisionStore:
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    # ----- writes (append-only) --------------------------------------------------

    def _append(
        self, *, entry_type: str, decision_id: str, payload_obj: BaseModel, tenant_id: str
    ) -> str:
        payload_json = canonical_json(payload_obj.model_dump(mode="json"))
        created_at = _now_iso()
        with self._sf.begin() as session:
            last = session.execute(
                select(AuditEntry)
                .where(AuditEntry.tenant_id == tenant_id)
                .order_by(AuditEntry.seq.desc())
                .limit(1)
            ).scalar_one_or_none()
            prev_hash = last.entry_hash if last else GENESIS
            entry_hash = compute_hash(
                prev_hash=prev_hash,
                tenant_id=tenant_id,
                entry_type=entry_type,
                decision_id=decision_id,
                payload_json=payload_json,
                created_at=created_at,
            )
            session.add(
                AuditEntry(
                    tenant_id=tenant_id,
                    entry_type=entry_type,
                    decision_id=decision_id,
                    payload=payload_json,
                    prev_hash=prev_hash,
                    entry_hash=entry_hash,
                    created_at=created_at,
                )
            )
        return entry_hash

    def record_decision(self, record: DecisionRecord, tenant_id: str = "default") -> str:
        """Append a decision record; returns its chain hash (the audit receipt)."""
        return self._append(
            entry_type="decision",
            decision_id=record.id,
            payload_obj=record,
            tenant_id=tenant_id,
        )

    def record_outcome(self, outcome: Outcome, tenant_id: str = "default") -> str:
        """Append what actually happened for an earlier decision (DI-8 learning loop)."""
        return self._append(
            entry_type="outcome",
            decision_id=outcome.decision_id,
            payload_obj=outcome,
            tenant_id=tenant_id,
        )

    def record_review(self, action: ReviewAction, tenant_id: str = "default") -> str:
        """Append a human sign-off action to the same tamper-evident chain (DI-7 / GV-2)."""
        return self._append(
            entry_type="review",
            decision_id=action.decision_id,
            payload_obj=action,
            tenant_id=tenant_id,
        )

    # ----- reads ------------------------------------------------------------------

    def get_decision(self, decision_id: str, tenant_id: str = "default") -> DecisionRecord | None:
        with self._sf() as session:
            row = session.execute(
                select(AuditEntry)
                .where(
                    AuditEntry.tenant_id == tenant_id,
                    AuditEntry.entry_type == "decision",
                    AuditEntry.decision_id == decision_id,
                )
                .order_by(AuditEntry.seq.desc())
                .limit(1)
            ).scalar_one_or_none()
            return DecisionRecord.model_validate_json(row.payload) if row else None

    def list_decisions(
        self, tenant_id: str = "default", limit: int = 50, offset: int = 0
    ) -> list[DecisionRecord]:
        with self._sf() as session:
            rows = (
                session.execute(
                    select(AuditEntry)
                    .where(
                        AuditEntry.tenant_id == tenant_id,
                        AuditEntry.entry_type == "decision",
                    )
                    .order_by(AuditEntry.seq.desc())
                    .limit(limit)
                    .offset(offset)
                )
                .scalars()
                .all()
            )
            return [DecisionRecord.model_validate_json(r.payload) for r in rows]

    def get_outcomes(self, decision_id: str, tenant_id: str = "default") -> list[Outcome]:
        with self._sf() as session:
            rows = (
                session.execute(
                    select(AuditEntry)
                    .where(
                        AuditEntry.tenant_id == tenant_id,
                        AuditEntry.entry_type == "outcome",
                        AuditEntry.decision_id == decision_id,
                    )
                    .order_by(AuditEntry.seq.asc())
                )
                .scalars()
                .all()
            )
            return [Outcome.model_validate_json(r.payload) for r in rows]

    def get_reviews(self, decision_id: str, tenant_id: str = "default") -> list[ReviewAction]:
        with self._sf() as session:
            rows = (
                session.execute(
                    select(AuditEntry)
                    .where(
                        AuditEntry.tenant_id == tenant_id,
                        AuditEntry.entry_type == "review",
                        AuditEntry.decision_id == decision_id,
                    )
                    .order_by(AuditEntry.seq.asc())
                )
                .scalars()
                .all()
            )
            return [ReviewAction.model_validate_json(r.payload) for r in rows]

    # ----- integrity --------------------------------------------------------------

    def verify_chain(self, tenant_id: str = "default") -> ChainVerification:
        with self._sf() as session:
            rows = (
                session.execute(
                    select(AuditEntry)
                    .where(AuditEntry.tenant_id == tenant_id)
                    .order_by(AuditEntry.seq.asc())
                )
                .scalars()
                .all()
            )
        prev = GENESIS
        for i, row in enumerate(rows):
            expected = compute_hash(
                prev_hash=prev,
                tenant_id=row.tenant_id,
                entry_type=row.entry_type,
                decision_id=row.decision_id,
                payload_json=row.payload,
                created_at=row.created_at,
            )
            if row.prev_hash != prev or row.entry_hash != expected:
                return ChainVerification(
                    ok=False,
                    entries_checked=i,
                    broken_at_seq=row.seq,
                    detail="hash mismatch — an entry was altered, inserted, or reordered.",
                )
            prev = row.entry_hash
        return ChainVerification(ok=True, entries_checked=len(rows), detail="chain intact")
