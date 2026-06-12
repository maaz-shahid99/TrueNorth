"""initial schema: audit_entries + api_keys

Revision ID: 0001
Revises:
Create Date: 2026-06-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_entries",
        sa.Column("seq", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("entry_type", sa.String(length=32), nullable=False),
        sa.Column("decision_id", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("prev_hash", sa.String(length=64), nullable=False),
        sa.Column("entry_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
    )
    op.create_index("ix_audit_entries_tenant_id", "audit_entries", ["tenant_id"])
    op.create_index("ix_audit_entries_decision_id", "audit_entries", ["decision_id"])

    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("subject", sa.String(length=256), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("roles", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.String(length=40), nullable=False),
    )
    op.create_index("ix_api_keys_tenant_id", "api_keys", ["tenant_id"])
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)


def downgrade() -> None:
    op.drop_table("api_keys")
    op.drop_table("audit_entries")
