"""Persistence layer: the immutable, verifiable decision ledger (GV-3)."""

from __future__ import annotations

from functools import lru_cache

from ..config import Settings
from .db import init_db, make_engine, make_session_factory
from .repository import DecisionStore

__all__ = ["DecisionStore", "get_store"]


@lru_cache(maxsize=8)
def _store_for(database_url: str) -> DecisionStore:
    engine = make_engine(database_url)
    init_db(engine)
    return DecisionStore(make_session_factory(engine))


def get_store(settings: Settings) -> DecisionStore:
    return _store_for(settings.database_url)
