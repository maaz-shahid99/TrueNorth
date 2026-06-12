"""Connector abstraction (DF-1 / DI-2).

A connector turns a decision request into an evidence pack for one decision type. The
registry dispatches by decision_type; adding a new decision type means adding a connector
and registering it — the pipeline does not change.
"""

from __future__ import annotations

from typing import Protocol

from ..config import Settings
from ..schemas import DecisionRequest, EvidencePack


class Connector(Protocol):
    def gather(self, request: DecisionRequest, settings: Settings) -> EvidencePack: ...
