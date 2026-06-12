"""FastAPI surface (SX-5), authenticated and multi-tenant (SC-1).

Every endpoint (except /healthz) requires an API key with the right permission, and all
storage is scoped to the caller's tenant. High-stakes decisions land in a PENDING review
state and need a reviewer's sign-off (DI-7 / GV-2).

    POST /v1/decisions                 decision:create   judge + persist (tenant-scoped)
    GET  /v1/decisions                 decision:list     list this tenant's decisions
    GET  /v1/decisions/{id}            decision:read     fetch one decision
    POST /v1/decisions/{id}/outcomes   outcome:write     record what happened (DI-8)
    GET  /v1/decisions/{id}/outcomes   decision:read     list recorded outcomes
    POST /v1/decisions/{id}/review     review:act        approve / reject (DI-7 / GV-2)
    GET  /v1/decisions/{id}/review     decision:read     review state + history
    GET  /v1/audit/verify              audit:verify      verify the tenant's hash chain
    GET  /healthz                      (public)          liveness

Mint keys with `truenorth-admin mint --subject ... --role ...`.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException

from .auth.deps import require
from .auth.rbac import Permission, Principal
from .config import get_settings
from .pipeline import evaluate_decision
from .review import compute_state
from .schemas import (
    ChainVerification,
    DecisionRecord,
    DecisionRequest,
    Outcome,
    OutcomeRequest,
    ReviewAction,
    ReviewActionInput,
    ReviewStatus,
)
from .store import get_store

app = FastAPI(title="TrueNorth Decision Engine", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/decisions", response_model=DecisionRecord)
def create_decision(
    request: DecisionRequest,
    principal: Principal = Depends(require(Permission.DECISION_CREATE)),
) -> DecisionRecord:
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
    get_store(settings).record_decision(record, principal.tenant_id)
    return record


@app.get("/v1/decisions", response_model=list[DecisionRecord])
def list_decisions(
    limit: int = 50,
    offset: int = 0,
    principal: Principal = Depends(require(Permission.DECISION_LIST)),
) -> list[DecisionRecord]:
    return get_store(get_settings()).list_decisions(
        tenant_id=principal.tenant_id, limit=limit, offset=offset
    )


@app.get("/v1/decisions/{decision_id}", response_model=DecisionRecord)
def get_decision(
    decision_id: str,
    principal: Principal = Depends(require(Permission.DECISION_READ)),
) -> DecisionRecord:
    record = get_store(get_settings()).get_decision(decision_id, principal.tenant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No decision with that id.")
    return record


@app.post("/v1/decisions/{decision_id}/outcomes", response_model=Outcome)
def add_outcome(
    decision_id: str,
    body: OutcomeRequest,
    principal: Principal = Depends(require(Permission.OUTCOME_WRITE)),
) -> Outcome:
    store = get_store(get_settings())
    if store.get_decision(decision_id, principal.tenant_id) is None:
        raise HTTPException(status_code=404, detail="No decision with that id.")
    outcome = Outcome(decision_id=decision_id, **body.model_dump())
    store.record_outcome(outcome, principal.tenant_id)
    return outcome


@app.get("/v1/decisions/{decision_id}/outcomes", response_model=list[Outcome])
def list_outcomes(
    decision_id: str,
    principal: Principal = Depends(require(Permission.DECISION_READ)),
) -> list[Outcome]:
    return get_store(get_settings()).get_outcomes(decision_id, principal.tenant_id)


@app.post("/v1/decisions/{decision_id}/review", response_model=ReviewStatus)
def submit_review(
    decision_id: str,
    body: ReviewActionInput,
    principal: Principal = Depends(require(Permission.REVIEW_ACT)),
) -> ReviewStatus:
    store = get_store(get_settings())
    record = store.get_decision(decision_id, principal.tenant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No decision with that id.")
    action = ReviewAction(decision_id=decision_id, actor=principal.subject, **body.model_dump())
    store.record_review(action, principal.tenant_id)
    history = store.get_reviews(decision_id, principal.tenant_id)
    return ReviewStatus(
        decision_id=decision_id,
        required=record.review_required,
        state=compute_state(record.review_required, history),
        history=history,
    )


@app.get("/v1/decisions/{decision_id}/review", response_model=ReviewStatus)
def get_review(
    decision_id: str,
    principal: Principal = Depends(require(Permission.DECISION_READ)),
) -> ReviewStatus:
    store = get_store(get_settings())
    record = store.get_decision(decision_id, principal.tenant_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No decision with that id.")
    history = store.get_reviews(decision_id, principal.tenant_id)
    return ReviewStatus(
        decision_id=decision_id,
        required=record.review_required,
        state=compute_state(record.review_required, history),
        history=history,
    )


@app.get("/v1/audit/verify", response_model=ChainVerification)
def verify_audit(
    principal: Principal = Depends(require(Permission.AUDIT_VERIFY)),
) -> ChainVerification:
    return get_store(get_settings()).verify_chain(principal.tenant_id)
