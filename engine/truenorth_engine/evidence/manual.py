"""Manual-facts evidence connector (DF-1 / DI-2).

A reusable connector that turns the structured facts a requester supplies (via
`request.inputs`) into cited evidence for one decision type. It generalises the pattern
the discount connector established: a field map naming each recognised input, a source
label, and a sufficiency threshold. This is the seam a real system-of-record connector
(HRIS, procurement, FP&A) replaces later — same `gather` signature, real source
citations instead of "manual:requester".
"""

from __future__ import annotations

from ..config import Settings
from ..schemas import DecisionRequest, EvidenceItem, EvidencePack


class ManualFactsConnector:
    def __init__(
        self,
        *,
        fields: dict[str, str],
        source: str = "manual:requester",
        note: str = "Manually supplied facts; a system-of-record connector would replace this source.",
        adequate_at: int = 4,
        empty_hint: str = "No facts supplied for this decision type.",
    ) -> None:
        self._fields = fields
        self._source = source
        self._note = note
        self._adequate_at = adequate_at
        self._empty_hint = empty_hint

    def gather(self, request: DecisionRequest, settings: Settings) -> EvidencePack:
        items = [
            EvidenceItem(claim=claim, value=request.inputs[key], source=self._source)
            for key, claim in self._fields.items()
            if request.inputs.get(key)
        ]
        if not items:
            return EvidencePack(sufficiency="unavailable", notes=self._empty_hint)
        sufficiency = "adequate" if len(items) >= self._adequate_at else "thin"
        return EvidencePack(items=items, sufficiency=sufficiency, notes=self._note)


# Recognised inputs per decision type -> the claim each becomes in the evidence pack.
HIRING_FIELDS: dict[str, str] = {
    "role": "Role / title",
    "level": "Level / seniority",
    "base_salary_usd": "Proposed base salary (USD)",
    "headcount_plan": "Approved in headcount plan?",
    "team": "Hiring team",
    "backfill_or_new": "Backfill or net-new headcount",
    "business_justification": "Business justification",
    "comp_band_fit": "Fit against the comp band",
}

VENDOR_FIELDS: dict[str, str] = {
    "vendor": "Vendor name",
    "annual_cost_usd": "Annual contract value (USD)",
    "contract_term_months": "Contract term (months)",
    "category": "Spend category",
    "data_access": "Data the vendor would access",
    "security_review": "Security review status",
    "alternatives_considered": "Alternatives considered",
    "lock_in_risk": "Switching / lock-in risk",
}

BUDGET_FIELDS: dict[str, str] = {
    "amount_usd": "Requested amount (USD)",
    "budget_line": "Budget line / cost center",
    "remaining_budget_usd": "Remaining budget on the line (USD)",
    "period": "Period (quarter / fiscal year)",
    "category": "Spend category (opex / capex)",
    "expected_return": "Expected return / outcome",
    "recurring": "One-time or recurring",
}


def hiring_connector() -> ManualFactsConnector:
    return ManualFactsConnector(
        fields=HIRING_FIELDS,
        empty_hint="No hiring facts supplied (e.g. --input role=Staff Engineer "
        "--input base_salary_usd=210000 --input headcount_plan=yes).",
    )


def vendor_connector() -> ManualFactsConnector:
    return ManualFactsConnector(
        fields=VENDOR_FIELDS,
        empty_hint="No procurement facts supplied (e.g. --input vendor=Acme "
        "--input annual_cost_usd=120000 --input data_access=PII).",
    )


def budget_connector() -> ManualFactsConnector:
    return ManualFactsConnector(
        fields=BUDGET_FIELDS,
        adequate_at=3,
        empty_hint="No budget facts supplied (e.g. --input amount_usd=50000 "
        "--input budget_line=Marketing-Q3 --input remaining_budget_usd=80000).",
    )
