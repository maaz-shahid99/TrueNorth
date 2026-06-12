"""Database engine and session wiring.

Defaults to a local SQLite file so the engine runs with zero infrastructure; point
DATABASE_URL at Postgres for a real deployment (the ORM is portable across both).
"""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base


def make_engine(database_url: str) -> Engine:
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        if ":memory:" in database_url or database_url == "sqlite://":
            # Keep one in-memory DB alive across sessions/threads (tests, ephemeral runs).
            return create_engine(
                database_url,
                future=True,
                connect_args=connect_args,
                poolclass=StaticPool,
            )
        return create_engine(database_url, future=True, connect_args=connect_args)
    return create_engine(database_url, future=True, pool_pre_ping=True)


def make_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(engine, expire_on_commit=False, future=True)


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)
