"""restrict_course_year_to_4

Revision ID: 0002_restrict_course_year_to_4
Revises: 0001_initial_schema
Create Date: 2026-11-19 17:30:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_restrict_course_year_to_4"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Обмежує діапазон курсу навчання академічних груп значеннями 1..4."""
    op.execute("UPDATE academic_groups SET course_year = 4 WHERE course_year > 4")
    op.execute("UPDATE academic_groups SET course_year = 1 WHERE course_year < 1")
    op.create_check_constraint(
        "ck_academic_groups_course_year_range",
        "academic_groups",
        "course_year >= 1 AND course_year <= 4",
    )


def downgrade() -> None:
    """Видаляє CHECK-обмеження діапазону course_year для таблиці academic_groups."""
    op.drop_constraint(
        "ck_academic_groups_course_year_range",
        "academic_groups",
        type_="check",
    )
