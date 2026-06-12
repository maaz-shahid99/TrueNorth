"""FastAPI surface (SX-5).

POST /v1/decisions  -> evaluate a decision, return the full DecisionRecord.
GET  /healthz       -> liveness.

This is the API a workbench or the future web UI calls. Auth, rate limiting, and the
immutable audit store (GV-3) are deliberately deferred to a later increment.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .config import get_settings
from .pipeline import evaluate_decision
from .schemas import DecisionRecord, DecisionRequest

app = FastAPI(title="TrueNorth Decision Engine", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/decisions", response_model=DecisionRecord)
def create_decision(request: DecisionRequest) -> DecisionRecord:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY is not configured; the engine cannot judge decisions.",
        )
    try:
        return evaluate_decision(request, settings)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
