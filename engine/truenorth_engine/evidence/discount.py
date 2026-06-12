"""Discount-approval evidence connector (DF-1 / DI-2).

No CRM is wired yet, so this connector turns deal facts the requester supplies (via
`request.inputs`) into cited evidence. It is fully functional today and is the exact seam
a Salesforce/HubSpot connector replaces later — same `gather` signature, real source
citations instead of "manual:requester".
"""

from __future__ import annotations

from ..config import Settings
from ..schemas import DecisionRequest, EvidenceItem, EvidencePack

# Recognised deal inputs -> the claim each becomes in the evidence pack.
_FIELDS: dict[str, str] = {
    "deal_value": "Total deal value (USD)",
    "discount_pct": "Requested discount (%)",
    "gross_margin_pct": "Resulting gross margin (%)",
    "customer_tier": "Customer tier / strategic importance",
    "competitor": "Competitive pressure",
    "contract_term_months": "Contract term (months)",
    "approver_limit_pct": "Discount the requester can self-approve (%)",
}


class ManualDiscountConnector:
    def gather(self, request: DecisionRequest, settings: Settings) -> EvidencePack:
        items = [
            EvidenceItem(claim=claim, value=request.inputs[key], source="manual:requester")
            for key, claim in _FIELDS.items()
            if request.inputs.get(key)
        ]
        if not items:
            return EvidencePack(
                sufficiency="unavailable",
                notes="No deal inputs supplied (e.g. --input discount_pct=35 --input gross_margin_pct=12).",
            )
        sufficiency = "adequate" if len(items) >= 4 else "thin"
        return EvidencePack(
            items=items,
            sufficiency=sufficiency,
            notes="Manually supplied deal facts; a CRM connector would replace this source.",
        )
