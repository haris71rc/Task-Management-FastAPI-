"""Rename task creator to owner while preserving existing task ownership.

Revision ID: c9d7e42a6b11
Revises: bfae808cd04c
"""
from alembic import op

revision = "c9d7e42a6b11"
down_revision = "bfae808cd04c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("tasks", "created_by", new_column_name="owner_id")


def downgrade() -> None:
    op.alter_column("tasks", "owner_id", new_column_name="created_by")
