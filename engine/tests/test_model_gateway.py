"""Hardened model-gateway path (PL-1): typed errors and retry/backoff behavior.

These tests never touch the network — the SDK client is replaced with a fake whose
``messages.parse`` raises chosen Anthropic exceptions or returns canned responses.
``model_retry_base_delay=0`` keeps the backoff sleeps effectively instant.
"""

from __future__ import annotations

from types import SimpleNamespace

import anthropic
import httpx
import pytest

from truenorth_engine.config import Settings
from truenorth_engine.model_gateway import (
    ModelGateway,
    ModelRefusalError,
    ModelUnavailableError,
    _is_retryable,
    _retry_after_seconds,
)
from truenorth_engine.schemas import Recommendation, StakesTier, Verdict


def _settings(**overrides) -> Settings:
    base = dict(anthropic_api_key="", model_retry_base_delay=0.0, model_max_retries=2)
    base.update(overrides)
    return Settings(**base)


def _good_response():
    rec = Recommendation(
        verdict=Verdict.CAUTION, reasoning="r", confidence=0.5, minority_report="m"
    )
    usage = SimpleNamespace(
        input_tokens=10,
        output_tokens=5,
        cache_read_input_tokens=0,
        cache_creation_input_tokens=0,
    )
    return SimpleNamespace(parsed_output=rec, usage=usage, stop_reason="end_turn")


def _fake_client(parse):
    return SimpleNamespace(messages=SimpleNamespace(parse=parse))


def _status_error(cls, status_code: int, headers: dict | None = None):
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    resp = httpx.Response(status_code, headers=headers or {}, request=req)
    return cls("boom", response=resp, body=None)


def _call(gateway: ModelGateway):
    return gateway.structured(
        tier=StakesTier.S4, instruction="x", output_format=Recommendation, step="synthesis"
    )


def test_refusal_raises_model_refusal_error():
    gateway = ModelGateway(_settings())
    refused = SimpleNamespace(parsed_output=None, usage=None, stop_reason="refusal")
    gateway._client = _fake_client(lambda **kw: refused)
    with pytest.raises(ModelRefusalError):
        _call(gateway)


def test_retries_then_succeeds():
    calls = {"n": 0}

    def flaky(**kw):
        calls["n"] += 1
        if calls["n"] < 3:
            raise _status_error(anthropic.RateLimitError, 429)
        return _good_response()

    gateway = ModelGateway(_settings(model_max_retries=3))
    gateway._client = _fake_client(flaky)
    out = _call(gateway)
    assert out.verdict == Verdict.CAUTION
    assert calls["n"] == 3  # two failures + one success


def test_exhausting_retries_raises_unavailable():
    def always_500(**kw):
        raise _status_error(anthropic.InternalServerError, 500)

    gateway = ModelGateway(_settings(model_max_retries=2))
    gateway._client = _fake_client(always_500)
    with pytest.raises(ModelUnavailableError):
        _call(gateway)


def test_non_retryable_error_propagates_unwrapped():
    def bad_request(**kw):
        raise _status_error(anthropic.BadRequestError, 400)

    gateway = ModelGateway(_settings())
    gateway._client = _fake_client(bad_request)
    with pytest.raises(anthropic.BadRequestError):
        _call(gateway)


def test_is_retryable_classification():
    assert _is_retryable(_status_error(anthropic.RateLimitError, 429))
    assert _is_retryable(_status_error(anthropic.InternalServerError, 503))
    assert _is_retryable(_status_error(anthropic.APIStatusError, 529))  # overloaded
    assert not _is_retryable(_status_error(anthropic.BadRequestError, 400))
    assert not _is_retryable(ValueError("nope"))


def test_retry_after_header_is_honored():
    exc = _status_error(anthropic.RateLimitError, 429, headers={"retry-after": "1.5"})
    assert _retry_after_seconds(exc) == 1.5
    assert _retry_after_seconds(_status_error(anthropic.RateLimitError, 429)) is None
