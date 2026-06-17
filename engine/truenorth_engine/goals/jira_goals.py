"""Jira goal connector (GA-1 / DF-1).

Pulls the issues that represent strategic goals/OKRs (selected by a configured JQL, e.g.
`issuetype = Epic AND labels = okr`) and maps them to Goal objects for alignment scoring.
Degrades gracefully to an empty list when Jira is not configured or a request fails —
the manual goal source still applies, so alignment keeps working offline.
"""

from __future__ import annotations

import httpx

from ..config import Settings
from ..schemas import Goal, GoalLevel


def gather_jira_goals(
    base_url: str | None, email: str | None, token: str | None, jql: str | None
) -> list[Goal]:
    if not (base_url and token and jql):
        return []
    auth = (email or "", token)
    headers = {"Accept": "application/json"}
    try:
        with httpx.Client(
            base_url=base_url.rstrip("/"), headers=headers, auth=auth, timeout=15.0
        ) as client:
            resp = client.get(
                "/rest/api/3/search",
                params={"jql": jql, "fields": "summary", "maxResults": 50},
            )
            if resp.status_code != 200:
                return []
            issues = resp.json().get("issues", [])
    except httpx.HTTPError:
        return []

    goals: list[Goal] = []
    for issue in issues:
        key = issue.get("key", "")
        summary = (issue.get("fields") or {}).get("summary", "")
        if summary:
            goals.append(
                Goal(title=summary, level=GoalLevel.DEPARTMENT, source=f"jira:{key}")
            )
    return goals


class JiraGoalConnector:
    """Goal source backed by Jira issues selected via JIRA_GOAL_JQL."""

    def list_goals(self, settings: Settings) -> list[Goal]:
        return gather_jira_goals(
            settings.jira_base_url or None,
            settings.jira_email or None,
            settings.jira_token or None,
            settings.jira_goal_jql or None,
        )
