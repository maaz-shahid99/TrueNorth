"""FastAPI surface (SX-5).

    POST /v1/decisions                 evaluate a decision; persists it to the ledger
    GET  /v1/decisions                 list recorded decisions (newest first)
    GET  /v1/decisions/{id}            fetch one recorded decision
    POST /v1/decisions/{id}/outcomes   record what actually happened (DI-8)
    GET  /v1/decisions/{id}/outcomes   list recorded outcomes
    GET  /v1/audit/verify              verify the audit hash chain (GV-3)
    GET  /healthz                      liveness

Every evaluated decision is written to the append-only, hash-chained audit store. Auth,
rate limiting, and multi-tenant scoping arrive in a later increment; for now everything
is recorded under the "default" tenant.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .config import get_settings
from .pipeline import evaluate_decision
from .schemas import (
    ChainVerification,
    DecisionRecord,
    DecisionRequest,
    Outcome,
    OutcomeRequest,
)
from .store import get_store

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
        record = evaluate_decision(request, settings)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    get_store(settings).record_decision(record)
    return record


@app.get("/v1/decisions", response_model=list[DecisionRecord])
def list_decisions(limit: int = 50, offset: int = 0) -> list[DecisionRecord]:
    return get_store(get_settings()).list_decisions(limit=limit, offset=offset)


@app.get("/v1/decisions/{decision_id}", response_model=DecisionRecord)
def get_decision(decision_id: str) -> DecisionRecord:
    record = get_store(get_settings()).get_decision(decision_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No decision with that id.")
    return record


@app.post("/v1/decisions/{decision_id}/outcomes", response_model=Outcome)
def add_outcome(decision_id: str, body: OutcomeRequest) -> Outcome:
    store = get_store(get_settings())
    if store.get_decision(decision_id) is None:
        raise HTTPException(status_code=404, detail="No decision with that id.")
    outcome = Outcome(decision_id=decision_id, **body.model_dump())
    store.record_outcome(outcome)
    return outcome


@app.get("/v1/decisions/{decision_id}/outcomes", response_model=list[Outcome])
def list_outcomes(decision_id: str) -> list[Outcome]:
    return get_store(get_settings()).get_outcomes(decision_id)


@app.get("/v1/audit/verify", response_model=ChainVerification)
def verify_audit() -> ChainVerification:
    return get_store(get_settings()).verify_chain()
