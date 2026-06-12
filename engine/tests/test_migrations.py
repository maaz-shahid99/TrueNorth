"""Migration test (PL-7): `alembic upgrade head` builds the expected schema.

Runs against a temp SQLite DB so it stays offline and fast, while proving the migration
applies cleanly and creates the audit + auth tables.
"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

_ENGINE_DIR = Path(__file__).resolve().parents[1]


def test_alembic_upgrade_creates_tables(tmp_path, monkeypatch):
    db = tmp_path / "migrated.db"
    url = f"sqlite:///{db.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)

    cfg = Config(str(_ENGINE_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(_ENGINE_DIR / "migrations"))
    command.upgrade(cfg, "head")

    tables = set(inspect(create_engine(url)).get_table_names())
    assert {"audit_entries", "api_keys"} <= tables
