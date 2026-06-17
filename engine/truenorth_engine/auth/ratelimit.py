"""Per-principal API rate limiting (SC / PL-7).

A small in-process fixed-window limiter that protects the expensive judgment path from
runaway or abusive call volume. It is keyed by the authenticated principal (tenant +
subject), so one tenant cannot exhaust another's budget. This is intentionally simple
and single-process — a multi-replica deployment would move the counter to Redis behind
the same `check` seam.
"""

from __future__ import annotations

import threading
import time

from fastapi import Depends, HTTPException

from ..config import get_settings
from .deps import get_principal
from .rbac import Principal


class FixedWindowRateLimiter:
    """Counts hits per key within a rolling fixed window; thread-safe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: dict[str, tuple[int, float]] = {}  # key -> (count, window_start)

    def check(
        self, key: str, limit: int, window_s: float = 60.0, now: float | None = None
    ) -> float | None:
        """Record a hit. Return None if allowed, else seconds until the window resets."""
        if limit <= 0:  # disabled
            return None
        now = time.monotonic() if now is None else now
        with self._lock:
            count, start = self._hits.get(key, (0, now))
            if now - start >= window_s:  # window expired -> reset
                count, start = 0, now
            if count >= limit:
                return max(0.0, window_s - (now - start))
            self._hits[key] = (count + 1, start)
        return None

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_limiter = FixedWindowRateLimiter()


def enforce_rate_limit(principal: Principal = Depends(get_principal)) -> None:
    """FastAPI dependency: 429 (with Retry-After) when the principal exceeds its budget."""
    settings = get_settings()
    key = f"{principal.tenant_id}:{principal.subject}"
    retry_after = _limiter.check(key, settings.rate_limit_per_minute)
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded; slow down.",
            headers={"Retry-After": str(int(retry_after) + 1)},
        )
