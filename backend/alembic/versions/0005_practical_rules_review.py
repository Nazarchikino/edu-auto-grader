"""add_practical_needs_rules_review

Revision ID: 0005_practical_rules_review
Revises: 0004_indexes_and_quiz_order
Create Date: 2026-11-25 18:40:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_practical_rules_review"
down_revision: str | None = "0004_indexes_and_quiz_order"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Додає булеве поле needs_rules_review до таблиці practicals."""
    op.add_column(
        "practicals",
        sa.Column(
            "needs_rules_review",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    """Видаляє поле needs_rules_review із таблиці practicals."""
    op.drop_column("practicals", "needs_rules_review")
