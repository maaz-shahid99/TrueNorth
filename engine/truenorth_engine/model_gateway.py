"""Model gateway (PL-1).

A thin routing layer in front of the Anthropic Messages API. It picks the model by
stakes tier, applies prompt caching to the shared canon prefix so repeated lens calls
are cheap, and exposes one structured-output call helper used by every step of the
pipeline. Keeping this seam here is what preserves a vendor-exit path.
"""

from __future__ import annotations

from typing import TypeVar

import anthropic
from pydantic import BaseModel

from .config import Settings
from .schemas import StakesTier

T = TypeVar("T", bound=BaseModel)

# The immutable canon, cached across every lens/synthesis call within a decision.
CANON_SYSTEM = (
    "You are a judge inside TrueNorth, an enterprise decision-intelligence system. "
    "You evaluate a proposed decision and return a structured assessment. "
    "Rules you must obey:\n"
    "- The verdict scale is exactly: Endorse / Endorse-with-conditions / Caution / Oppose.\n"
    "- Ground every claim in the supplied evidence; never invent facts or numbers. If "
    "evidence is missing, say so and lower your confidence.\n"
    "- You advise; a human always decides. Never phrase output as an executed action.\n"
    "- Be specific and honest. A pro-forma or empty critical section is a failure."
)


class ModelGateway:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # The SDK reads ANTHROPIC_API_KEY from env; pass explicitly so config wins.
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key or None)

    def structured(
        self,
        *,
        tier: StakesTier,
        instruction: str,
        output_format: type[T],
        max_tokens: int = 4000,
        use_thinking: bool = False,
    ) -> T:
        """Run one structured-output call and return the parsed Pydantic object.

        Uses client.messages.parse so the model must return `output_format`'s shape.
        The canon goes in a cached system block; the per-call instruction is the user turn.
        """
        model = self._settings.model_for_tier(tier)
        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "system": [
                {
                    "type": "text",
                    "text": CANON_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            "messages": [{"role": "user", "content": instruction}],
            "output_format": output_format,
        }
        if use_thinking:
            # Adaptive thinking is the recommended mode on Opus 4.8 (high-stakes synthesis).
            kwargs["thinking"] = {"type": "adaptive"}

        response = self._client.messages.parse(**kwargs)
        parsed = response.parsed_output
        if parsed is None:  # refusal or unparseable
            raise RuntimeError(
                f"Model returned no parseable {output_format.__name__} "
                f"(stop_reason={response.stop_reason})."
            )
        return parsed

    @property
    def model_name(self) -> str:
        return self._settings.model_for_tier(StakesTier.S3)
