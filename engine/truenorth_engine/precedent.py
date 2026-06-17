"""Precedent retrieval (KG / institutional memory, deepens DI-2).

Given a new decision request and the tenant's past decisions, surface the most similar
prior decisions and how they turned out. Similarity is lexical (token-overlap on the
question + context) with a same-decision-type bonus — deliberately dependency-free and
deterministic, so it needs no embedding provider and is fully testable offline. The
embedding-based variant can replace `_similarity` later behind the same interface.
"""

from __future__ import annotations

import re

from .schemas import DecisionRecord, DecisionRequest, Outcome, Precedent

# Common words that carry no decision-specific signal.
_STOP = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "her", "was", "one",
    "our", "out", "his", "has", "had", "him", "she", "they", "this", "that", "with",
    "from", "have", "will", "should", "would", "could", "into", "than", "then", "them",
    "what", "when", "which", "while", "your", "about", "ship", "approve", "decision",
}


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in _STOP}


def _similarity(a: set[str], b: set[str]) -> float:
    """Jaccard overlap of two token sets, in [0, 1]."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def summarize_outcomes(outcomes: list[Outcome]) -> str:
    """A short, human-readable summary of the latest recorded outcome (empty if none)."""
    if not outcomes:
        return ""
    latest = outcomes[-1]
    flag = "success" if latest.success else "miss" if latest.success is False else "recorded"
    return f"{flag}: {latest.realized}".strip()[:200]


def rank_precedents(
    request: DecisionRequest,
    candidates: list[DecisionRecord],
    *,
    limit: int = 3,
    min_score: float = 0.05,
    same_type_bonus: float = 0.15,
) -> list[Precedent]:
    """Rank candidate past decisions by similarity to `request`; return the top `limit`.

    Outcome summaries are left empty here; the caller fills them for the chosen few so the
    ranking stays a pure function over the decision records.
    """
    req_tokens = _tokens(f"{request.question} {request.context or ''}")
    scored: list[tuple[float, DecisionRecord]] = []
    for rec in candidates:
        if rec.request.question == request.question and rec.request.context == request.context:
            continue  # don't surface an identical prior submission as its own precedent
        sim = _similarity(req_tokens, _tokens(f"{rec.request.question} {rec.request.context or ''}"))
        if rec.request.decision_type == request.decision_type:
            sim = min(1.0, sim + same_type_bonus)
        if sim >= min_score:
            scored.append((sim, rec))

    scored.sort(key=lambda pair: (pair[0], pair[1].created_at), reverse=True)
    return [
        Precedent(
            decision_id=rec.id,
            question=rec.request.question,
            decision_type=rec.request.decision_type,
            verdict=rec.recommendation.verdict,
            stakes=rec.stakes,
            created_at=rec.created_at,
            similarity=round(sim, 3),
        )
        for sim, rec in scored[:limit]
    ]
