"""Goal sources (GA-1).

The tenant's active goals come from two places, merged: goals entered/stored directly
(the manual source, always available and offline-friendly) and goals pulled live from a
connector (Jira today). `gather_goals` is the single seam the pipeline and API use, so
adding an Asana/spreadsheet connector later means registering it here — nothing else
changes. Connectors degrade gracefully to an empty list when unconfigured.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..config import Settings
from ..schemas import Goal
from .jira_goals import JiraGoalConnector

if TYPE_CHECKING:
    from ..store.repository import DecisionStore


def gather_goals(store: DecisionStore, settings: Settings, tenant_id: str = "default") -> list[Goal]:
    """Merge stored (manual) goals with any live connector goals for the tenant."""
    goals: list[Goal] = list(store.list_goals(tenant_id))
    goals.extend(JiraGoalConnector().list_goals(settings))  # empty unless Jira is configured
    return goals
