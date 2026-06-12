"""Per-call observability and cost capture (PL-6).

A Telemetry collector accumulates one CallUsage per model call (tokens, latency, and an
estimated USD cost) and emits a structured log line. The pipeline rolls the collector up
into a UsageSummary on the DecisionRecord, so spend is part of the audit trail. An OTel
exporter would plug into `record_call` without changing callers.
"""

from __future__ import annotations

import logging

from .schemas import CallUsage, UsageSummary

logger = logging.getLogger("truenorth.telemetry")

# Approximate list price in USD per million tokens (input, output). Override per
# deployment as contracts dictate; unknown models price at zero rather than guess.
PRICING_PER_MTOK: dict[str, tuple[float, float]] = {
    "claude-opus-4-8": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (0.80, 4.0),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    in_rate, out_rate = PRICING_PER_MTOK.get(model, (0.0, 0.0))
    return round((input_tokens / 1_000_000) * in_rate + (output_tokens / 1_000_000) * out_rate, 6)


class Telemetry:
    def __init__(self) -> None:
        self.calls: list[CallUsage] = []

    def record_call(self, usage: CallUsage) -> None:
        self.calls.append(usage)
        logger.info(
            "model_call step=%s model=%s in=%d out=%d cache_read=%d cost=$%.4f latency=%dms",
            usage.step,
            usage.model,
            usage.input_tokens,
            usage.output_tokens,
            usage.cache_read_tokens,
            usage.cost_usd,
            usage.latency_ms,
        )

    def summary(self) -> UsageSummary:
        return UsageSummary(
            calls=list(self.calls),
            total_input_tokens=sum(c.input_tokens for c in self.calls),
            total_output_tokens=sum(c.output_tokens for c in self.calls),
            total_cost_usd=round(sum(c.cost_usd for c in self.calls), 6),
            total_latency_ms=sum(c.latency_ms for c in self.calls),
        )
