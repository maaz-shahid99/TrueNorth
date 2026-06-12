"""Hash-chain primitives for the audit ledger (GV-3).

Each entry's hash binds the previous hash, the tenant, the entry type, the logical
decision id, the canonical payload, and the timestamp. Recomputing the chain from the
genesis hash detects any insertion, deletion, reordering, or in-place edit of a row.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENESIS = "0" * 64
_SEP = b"\x1e"  # ASCII record separator: prevents field-boundary ambiguity in the hash


def canonical_json(payload: dict[str, Any]) -> str:
    """Deterministic JSON so the same record always hashes to the same digest."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash(
    *,
    prev_hash: str,
    tenant_id: str,
    entry_type: str,
    decision_id: str,
    payload_json: str,
    created_at: str,
) -> str:
    h = hashlib.sha256()
    for part in (prev_hash, tenant_id, entry_type, decision_id, payload_json, created_at):
        h.update(part.encode("utf-8"))
        h.update(_SEP)
    return h.hexdigest()
