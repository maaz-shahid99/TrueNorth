"""Alembic environment.

Reads DATABASE_URL from the environment (so the same migrations run against SQLite in
dev and Postgres in production) and targets the shared SQLAlchemy metadata. Importing the
auth models registers the api_keys table alongside the audit ledger.
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import truenorth_engine.auth.models  # noqa: F401  (registers api_keys on Base.metadata)
from truenorth_engine.store.models import Base

config = context.config

_db_url = os.environ.get("DATABASE_URL", "sqlite:///./truenorth.db")
config.set_main_option("sqlalchemy.url", _db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
