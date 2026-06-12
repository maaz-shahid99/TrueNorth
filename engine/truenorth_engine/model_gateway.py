"""Model gateway (PL-1).

A thin routing layer in front of the Anthropic Messages API. It picks the model by
stakes tier, applies prompt caching to the shared canon prefix so repeated lens calls
are cheap, and exposes one structured-output call helper used by every step of the
pipeline. Keeping this seam here is what preserves a vendor-exit path.
"""

from __future__ import annotations

import time
from typing import TypeVar

import anthropic
from pydantic import BaseModel

from .config import Settings
from .schemas import CallUsage, StakesTier
from .telemetry import Telemetry, estimate_cost

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
    def __init__(self, settings: Settings, telemetry: Telemetry | None = None) -> None:
        self._settings = settings
        self._telemetry = telemetry
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
        step: str = "",
    ) -> T:
        """Run one structured-output call and return the parsed Pydantic object.

        Uses client.messages.parse so the model must return `output_format`'s shape.
        The canon goes in a cached system block; the per-call instruction is the user turn.
        Token usage, latency, and estimated cost are recorded to the telemetry collector.
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

        start = time.perf_counter()
        response = self._client.messages.parse(**kwargs)
        latency_ms = int((time.perf_counter() - start) * 1000)

        parsed = response.parsed_output
        if parsed is None:  # refusal or unparseable
            raise RuntimeError(
                f"Model returned no parseable {output_format.__name__} "
                f"(stop_reason={response.stop_reason})."
            )

        if self._telemetry is not None:
            self._telemetry.record_call(_usage_from(response, model, step, latency_ms))
        return parsed

    @property
    def model_name(self) -> str:
        return self._settings.model_for_tier(StakesTier.S3)


def _usage_from(response: object, model: str, step: str, latency_ms: int) -> CallUsage:
    """Extract token usage from a Messages response and price it (PL-6)."""
    usage = getattr(response, "usage", None)
    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
    cache_read = int(getattr(usage, "cache_read_input_tokens", 0) or 0)
    cache_write = int(getattr(usage, "cache_creation_input_tokens", 0) or 0)
    return CallUsage(
        step=step,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read,
        cache_write_tokens=cache_write,
        latency_ms=latency_ms,
        cost_usd=estimate_cost(model, input_tokens, output_tokens),
    )
