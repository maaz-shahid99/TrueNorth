"""Model gateway (PL-1).

A thin routing layer in front of the Anthropic Messages API. It picks the model by
stakes tier, applies prompt caching to the shared canon prefix so repeated lens calls
are cheap, and exposes one structured-output call helper used by every step of the
pipeline. Keeping this seam here is what preserves a vendor-exit path.

The live call path is hardened: transient failures (rate limits, timeouts, connection
errors, 5xx/overloaded) are retried with exponential backoff + jitter, and the two
failure modes a caller cares about are distinct typed exceptions — `ModelRefusalError`
(the model returned nothing parseable) and `ModelUnavailableError` (the service was
unreachable after exhausting retries).
"""

from __future__ import annotations

import logging
import random
import time
from typing import TypeVar

import anthropic
from pydantic import BaseModel

from .config import Settings
from .schemas import CallUsage, StakesTier
from .telemetry import Telemetry, estimate_cost

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger("truenorth.model_gateway")

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


class ModelError(RuntimeError):
    """Base class for model-gateway failures."""


class ModelRefusalError(ModelError):
    """The model returned no parseable output (a refusal or a truncated response)."""


class ModelUnavailableError(ModelError):
    """The model call failed after exhausting retries (rate limit / transient error)."""


def _is_retryable(exc: Exception) -> bool:
    """Transient failures worth retrying: rate limits, timeouts, connection drops, 5xx."""
    if isinstance(
        exc,
        (
            anthropic.RateLimitError,
            anthropic.APITimeoutError,
            anthropic.APIConnectionError,
            anthropic.InternalServerError,
        ),
    ):
        return True
    # 429 and any 5xx surfaced as a generic status error (e.g. 529 "overloaded").
    status = getattr(exc, "status_code", None)
    return isinstance(exc, anthropic.APIStatusError) and (status == 429 or (status or 0) >= 500)


def _retry_after_seconds(exc: Exception) -> float | None:
    """Honor a server-supplied Retry-After header when present."""
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if not headers:
        return None
    raw = headers.get("retry-after")
    if raw is None:
        return None
    try:
        return max(0.0, float(raw))
    except (TypeError, ValueError):
        return None


class ModelGateway:
    def __init__(self, settings: Settings, telemetry: Telemetry | None = None) -> None:
        self._settings = settings
        self._telemetry = telemetry
        # The SDK reads ANTHROPIC_API_KEY from env; pass explicitly so config wins.
        # We own the retry loop, so disable the SDK's own retries (max_retries=0) to
        # avoid compounding backoff, and bound every call with a timeout.
        self._client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key or None,
            timeout=settings.model_timeout_seconds,
            max_retries=0,
        )

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

        Raises ``ModelRefusalError`` if the model returns nothing parseable, and
        ``ModelUnavailableError`` if the service is unreachable after retries.
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
        response = self._call_with_retries(kwargs, step=step, model=model)
        latency_ms = int((time.perf_counter() - start) * 1000)

        parsed = response.parsed_output
        if parsed is None:  # refusal or truncated/unparseable output
            raise ModelRefusalError(
                f"Model returned no parseable {output_format.__name__} "
                f"(step={step or '?'}, stop_reason={getattr(response, 'stop_reason', '?')})."
            )

        if self._telemetry is not None:
            self._telemetry.record_call(_usage_from(response, model, step, latency_ms))
        return parsed

    def _call_with_retries(self, kwargs: dict, *, step: str, model: str) -> object:
        """Invoke messages.parse with exponential backoff on transient failures."""
        max_retries = self._settings.model_max_retries
        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                return self._client.messages.parse(**kwargs)
            except Exception as exc:  # noqa: BLE001 - re-raised below if not retryable
                if not _is_retryable(exc):
                    raise
                last_exc = exc
                if attempt >= max_retries:
                    break
                delay = self._backoff_delay(attempt, exc)
                logger.warning(
                    "model call transient failure step=%s model=%s attempt=%d/%d err=%s "
                    "retrying_in=%.2fs",
                    step or "?",
                    model,
                    attempt + 1,
                    max_retries,
                    type(exc).__name__,
                    delay,
                )
                time.sleep(delay)
        raise ModelUnavailableError(
            f"Model call failed after {max_retries} retries "
            f"(step={step or '?'}, model={model}): {type(last_exc).__name__}: {last_exc}"
        ) from last_exc

    def _backoff_delay(self, attempt: int, exc: Exception) -> float:
        """Server Retry-After wins; otherwise exponential backoff with full jitter."""
        retry_after = _retry_after_seconds(exc)
        if retry_after is not None:
            return retry_after
        base = self._settings.model_retry_base_delay
        return random.uniform(0, base * (2**attempt))

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
