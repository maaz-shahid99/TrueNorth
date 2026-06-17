"""Goal-connector abstraction (GA-1 / DF-1).

A goal connector turns an external system of record into the tenant's strategic goals.
The registry-style `gather_goals` (in this package's __init__) dispatches and merges
sources; a connector implements just this one method and degrades to [] when unconfigured.
"""

from __future__ import annotations

from typing import Protocol

from ..config import Settings
from ..schemas import Goal


class GoalSource(Protocol):
    def list_goals(self, settings: Settings) -> list[Goal]: ...
