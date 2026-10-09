"""add user role and updated at

Revision ID: 74968ed43995
Revises: 62f4720ad3ee
Create Date: 2026-10-09 15:34:13.842853

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "74968ed43995"
down_revision: Union[str, Sequence[str], None] = "62f4720ad3ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the PostgreSQL enum type first.
    user_role_enum = sa.Enum(
        "ADMIN",
        "USER",
        name="userrole",
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add role, assigning USER to existing rows.
    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            server_default="USER",
            nullable=False,
        ),
    )

    # 3. Add updated_at.
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # 4. Remove the temporary role default.
    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("users", "updated_at")
    op.drop_column("users", "role")

    # Remove the enum type after its column is dropped.
    user_role_enum = sa.Enum(
        "ADMIN",
        "USER",
        name="userrole",
    )
    user_role_enum.drop(op.get_bind(), checkfirst=True)
