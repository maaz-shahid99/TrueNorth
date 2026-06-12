"""Evidence connectors (DF-1 / DI-2).

Registry of one connector per decision type; `gather_evidence` dispatches on the
request's decision_type and degrades to "unavailable" when no connector is registered.
"""

from __future__ import annotations

from ..config import Settings
from ..schemas import DecisionRequest, EvidencePack
from .base import Connector
from .discount import ManualDiscountConnector
from .github import GitHubReleaseConnector

CONNECTORS: dict[str, Connector] = {
    "release_go_no_go": GitHubReleaseConnector(),
    "discount_approval": ManualDiscountConnector(),
}


def gather_evidence(request: DecisionRequest, settings: Settings) -> EvidencePack:
    connector = CONNECTORS.get(request.decision_type)
    if connector is None:
        return EvidencePack(
            sufficiency="unavailable",
            notes=f"No connector registered for decision type '{request.decision_type}'.",
        )
    return connector.gather(request, settings)
