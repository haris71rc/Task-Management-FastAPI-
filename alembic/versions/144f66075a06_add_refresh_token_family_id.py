"""add refresh token family id

Revision ID: 144f66075a06
Revises: e061f93b69ae
Create Date: 2026-10-10 14:11:54.806447

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "144f66075a06"
down_revision: Union[str, Sequence[str], None] = "e061f93b69ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add the column temporarily as nullable.
    op.add_column(
        "refresh_tokens",
        sa.Column("family_id", sa.Uuid(), nullable=True),
    )

    # 2. Give every existing token its own family.
    op.execute("""
        UPDATE refresh_tokens
        SET family_id = gen_random_uuid()
        WHERE family_id IS NULL
        """)

    # 3. Enforce the final constraint and create an index.
    op.alter_column(
        "refresh_tokens",
        "family_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    op.create_index(
        "ix_refresh_tokens_family_id",
        "refresh_tokens",
        ["family_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_refresh_tokens_family_id",
        table_name="refresh_tokens",
    )
    op.drop_column("refresh_tokens", "family_id")
