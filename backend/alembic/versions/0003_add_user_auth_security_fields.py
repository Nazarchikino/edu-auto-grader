"""add_user_auth_security_fields

Revision ID: 0003_user_auth_security
Revises: 0002_restrict_course_year_to_4
Create Date: 2026-11-25 02:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_user_auth_security"
down_revision: str | None = "0002_restrict_course_year_to_4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Додає поля token_version та must_change_password до таблиці users."""
    op.add_column(
        "users",
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "must_change_password",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    """Видаляє поля token_version та must_change_password із таблиці users."""
    op.drop_column("users", "must_change_password")
    op.drop_column("users", "token_version")
