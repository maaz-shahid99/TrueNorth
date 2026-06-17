"""Meeting intelligence — decision & commitment extraction (MI-2).

Turns a meeting transcript into a list of candidate decisions a human can confirm and
route into the judgment pipeline. This is the capture half of the product thesis: most
decisions are made in meetings, then need judging. Extraction never auto-judges — it only
proposes; a person edits and submits each decision through the normal /v1/decisions path.
"""

from __future__ import annotations

from .model_gateway import ModelGateway
from .schemas import MeetingExtraction, StakesTier

_KNOWN_TYPES = (
    "release_go_no_go, discount_approval, hiring_approval, vendor_procurement, "
    "budget_spend, project_go_no_go, other"
)


def extract_decisions(
    gateway: ModelGateway, transcript: str, *, title: str = ""
) -> MeetingExtraction:
    """Extract candidate decisions from a transcript (MI-2). One structured model call."""
    header = f"Meeting: {title}\n\n" if title else ""
    return gateway.structured(
        tier=StakesTier.S3,
        instruction=(
            f"{header}Transcript:\n{transcript}\n\n"
            f"Extract the concrete decisions that were MADE or PROPOSED in this meeting — "
            f"not general discussion. For each decision provide:\n"
            f"- question: the decision phrased as a yes/no question ready to be judged;\n"
            f"- decision_type: the best fit from [{_KNOWN_TYPES}];\n"
            f"- owner: who owns it, if named;\n"
            f"- deadline: any stated date/timeframe;\n"
            f"- context: a one-line context from the discussion;\n"
            f"- dissent: any recorded disagreement or concern.\n"
            f"Also give a one- or two-sentence summary of the meeting. If no real decisions "
            f"were made, return an empty decisions list."
        ),
        output_format=MeetingExtraction,
        max_tokens=2000,
        step="meeting-extraction",
    )
