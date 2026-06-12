"""Persistence layer: the immutable, verifiable decision ledger (GV-3).

One database per `DATABASE_URL`, shared across the audit store and the API-key store. The
engine is cached per URL so a process keeps a single connection pool (and a single live
in-memory SQLite DB during tests).
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker

from ..config import Settings
from .db import init_db, make_engine, make_session_factory
from .repository import DecisionStore

__all__ = ["DecisionStore", "get_store", "get_session_factory"]


@lru_cache(maxsize=8)
def _engine_for(database_url: str) -> Engine:
    engine = make_engine(database_url)
    init_db(engine)
    return engine


def get_session_factory(settings: Settings) -> sessionmaker:
    return make_session_factory(_engine_for(settings.database_url))


def get_store(settings: Settings) -> DecisionStore:
    return DecisionStore(get_session_factory(settings))
