"""Stakes-tiered human review gates (DI-7 / GV-2).

The engine advises; a human decides. High-stakes decisions require explicit sign-off
before they count as approved; routine ones do not. Review actions are appended to the
same immutable ledger as decisions, so the approval trail is itself tamper-evident.
"""

from __future__ import annotations

from .config import Settings
from .schemas import ReviewAction, ReviewState, StakesTier


def review_required(stakes: StakesTier, settings: Settings) -> bool:
    return stakes in settings.review_required_tiers


def compute_state(required: bool, actions: list[ReviewAction]) -> ReviewState:
    """Derive the current review state from the recorded action history.

    A rejection is decisive and overrides any prior approval; otherwise an approval
    settles it. With no actions, the state is PENDING when review is required and
    NOT_REQUIRED otherwise.
    """
    if any(a.action == "reject" for a in actions):
        return ReviewState.REJECTED
    if any(a.action == "approve" for a in actions):
        return ReviewState.APPROVED
    return ReviewState.PENDING if required else ReviewState.NOT_REQUIRED
