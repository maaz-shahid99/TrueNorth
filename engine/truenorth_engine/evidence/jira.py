"""Jira evidence connector for project go/no-go decisions (DF-1 + DI-2).

Gathers the signals a team weighs before greenlighting or continuing a project: open
issue count, work in progress, and unresolved blockers, via the Jira Cloud REST API.
Every item carries a source citation (DF-5 lineage). When Jira is not configured (no
base URL / token) or no project key is supplied, it degrades gracefully and falls back
to the project facts the requester provides in `request.inputs`, rather than inventing
numbers — the same pattern as the GitHub connector.

Configure with JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN (an API token); pass the project
key as `inputs.jira_project` on the request.
"""

from __future__ import annotations

import httpx

from ..config import Settings
from ..schemas import DecisionRequest, EvidenceItem, EvidencePack
from .manual import ManualFactsConnector

# Project-brief facts a requester can supply directly (used with or without Jira).
PROJECT_FIELDS: dict[str, str] = {
    "objective": "Project objective",
    "budget_usd": "Budget (USD)",
    "timeline_months": "Timeline (months)",
    "team_size": "Team size (FTEs)",
    "dependencies": "Key dependencies",
    "success_metric": "Primary success metric",
    "risk_summary": "Known risks",
}


def _jql_total(client: httpx.Client, jql: str) -> int | None:
    """Return the issue count for a JQL query, or None if the request did not succeed."""
    resp = client.get("/rest/api/3/search", params={"jql": jql, "maxResults": 0})
    if resp.status_code != 200:
        return None
    return resp.json().get("total")


def gather_jira_evidence(
    base_url: str | None, email: str | None, token: str | None, project: str | None
) -> EvidencePack:
    if not (base_url and token and project):
        return EvidencePack(
            sufficiency="unavailable",
            notes="Jira not configured (set JIRA_BASE_URL + JIRA_TOKEN and inputs.jira_project).",
        )

    auth = (email or "", token)
    headers = {"Accept": "application/json"}
    safe = project.replace('"', "")
    queries = {
        "Open issues": f'project = "{safe}" AND statusCategory != Done',
        "Work in progress": f'project = "{safe}" AND statusCategory = "In Progress"',
        "Unresolved blockers": f'project = "{safe}" AND priority = Highest AND statusCategory != Done',
    }

    items: list[EvidenceItem] = []
    try:
        with httpx.Client(
            base_url=base_url.rstrip("/"), headers=headers, auth=auth, timeout=15.0
        ) as client:
            for claim, jql in queries.items():
                total = _jql_total(client, jql)
                if total is not None:
                    items.append(
                        EvidenceItem(
                            claim=claim, value=str(total), source=f"jira:{safe}"
                        )
                    )
    except httpx.HTTPError as exc:
        return EvidencePack(sufficiency="unavailable", notes=f"Jira request failed: {exc}")

    if not items:
        return EvidencePack(
            sufficiency="unavailable",
            notes="Jira returned no usable signals (check credentials / project key).",
        )
    sufficiency = "adequate" if len(items) >= 3 else "thin"
    return EvidencePack(items=items, sufficiency=sufficiency, notes=f"Live Jira signals for {safe}.")


class JiraProjectConnector:
    """Connector for project go/no-go: live Jira signals plus any requester-supplied facts."""

    def __init__(self) -> None:
        self._manual = ManualFactsConnector(
            fields=PROJECT_FIELDS,
            adequate_at=3,
            empty_hint="No project facts supplied (e.g. --input objective=... "
            "--input budget_usd=250000 --input timeline_months=6).",
        )

    def gather(self, request: DecisionRequest, settings: Settings) -> EvidencePack:
        jira = gather_jira_evidence(
            settings.jira_base_url or None,
            settings.jira_email or None,
            settings.jira_token or None,
            request.inputs.get("jira_project"),
        )
        manual = self._manual.gather(request, settings)
        items = jira.items + manual.items
        if not items:
            return EvidencePack(
                sufficiency="unavailable",
                notes="No Jira project configured and no project facts supplied.",
            )
        notes = " ".join(
            n for n in (jira.notes if jira.items else "", manual.notes if manual.items else "") if n
        )
        sufficiency = "adequate" if len(items) >= 3 else "thin"
        return EvidencePack(items=items, sufficiency=sufficiency, notes=notes)
