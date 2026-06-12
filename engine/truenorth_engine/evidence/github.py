"""GitHub evidence connector for release go/no-go decisions (DF-1 + DI-2).

Gathers the concrete signals a team weighs before shipping: open bug count, recent CI
pass rate, and open pull requests. Every item carries a source citation (DF-5 lineage).
Degrades gracefully to 'unavailable' when no token or repo is supplied, rather than
inventing numbers.
"""

from __future__ import annotations

import httpx

from ..schemas import EvidenceItem, EvidencePack

_API = "https://api.github.com"


def gather_release_evidence(repo: str | None, token: str | None) -> EvidencePack:
    if not repo:
        return EvidencePack(
            sufficiency="unavailable", notes="No repository supplied for the GitHub connector."
        )

    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    items: list[EvidenceItem] = []
    try:
        with httpx.Client(base_url=_API, headers=headers, timeout=15.0) as client:
            # Open bugs: issues labelled "bug" that are open.
            bugs = client.get(
                "/search/issues",
                params={"q": f"repo:{repo} is:issue is:open label:bug"},
            )
            if bugs.status_code == 200:
                count = bugs.json().get("total_count", 0)
                items.append(
                    EvidenceItem(
                        claim="Open bug-labelled issues",
                        value=str(count),
                        source=f"github:{repo}/issues?label=bug",
                    )
                )

            # Open pull requests.
            prs = client.get(
                "/search/issues", params={"q": f"repo:{repo} is:pr is:open"}
            )
            if prs.status_code == 200:
                items.append(
                    EvidenceItem(
                        claim="Open pull requests",
                        value=str(prs.json().get("total_count", 0)),
                        source=f"github:{repo}/pulls",
                    )
                )

            # Recent CI: pass rate of the last 20 workflow runs.
            runs = client.get(
                f"/repos/{repo}/actions/runs", params={"per_page": 20}
            )
            if runs.status_code == 200:
                data = runs.json().get("workflow_runs", [])
                completed = [r for r in data if r.get("status") == "completed"]
                if completed:
                    passed = sum(1 for r in completed if r.get("conclusion") == "success")
                    rate = round(100 * passed / len(completed))
                    items.append(
                        EvidenceItem(
                            claim="Recent CI pass rate (last completed runs)",
                            value=f"{rate}% of {len(completed)}",
                            source=f"github:{repo}/actions/runs",
                        )
                    )
    except httpx.HTTPError as exc:
        return EvidencePack(
            sufficiency="unavailable", notes=f"GitHub request failed: {exc}"
        )

    if not items:
        return EvidencePack(
            sufficiency="unavailable",
            notes="GitHub returned no usable signals (check token scope / repo name).",
        )

    sufficiency = "adequate" if len(items) >= 3 else "thin"
    return EvidencePack(items=items, sufficiency=sufficiency)
