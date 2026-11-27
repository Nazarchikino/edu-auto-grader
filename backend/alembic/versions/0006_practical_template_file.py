"""add_practical_template_file_fields

Revision ID: 0006_practical_template_file
Revises: 0005_practical_rules_review
Create Date: 2026-11-27 17:45:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_practical_template_file"
down_revision: str | None = "0005_practical_rules_review"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Додає опційні поля файлу-заготовки (template_file_*) до таблиці practicals."""
    op.add_column(
        "practicals",
        sa.Column(
            "template_file_path",
            sa.String(length=500),
            nullable=True,
        ),
    )
    op.add_column(
        "practicals",
        sa.Column(
            "template_file_name",
            sa.String(length=255),
            nullable=True,
        ),
    )
    op.add_column(
        "practicals",
        sa.Column(
            "template_file_hash",
            sa.String(length=64),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Видаляє поля файлу-заготовки із таблиці practicals."""
    op.drop_column("practicals", "template_file_hash")
    op.drop_column("practicals", "template_file_name")
    op.drop_column("practicals", "template_file_path")
