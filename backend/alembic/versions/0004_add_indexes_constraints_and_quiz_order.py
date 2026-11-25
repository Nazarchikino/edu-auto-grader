"""add_indexes_constraints_and_quiz_order

Revision ID: 0004_indexes_and_quiz_order
Revises: 0003_add_user_auth_security_fields
Create Date: 2026-11-25 03:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_indexes_and_quiz_order"
down_revision: str | None = "0003_add_user_auth_security_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Додає order_index для quiz_questions, складені B-Tree індекси та унікальні обмеження."""
    op.add_column(
        "quiz_questions",
        sa.Column(
            "order_index",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.execute(
        """
        UPDATE quiz_questions
        SET order_index = numbered.rn
        FROM (
            SELECT
                id,
                ROW_NUMBER() OVER (PARTITION BY module_id ORDER BY id) AS rn
            FROM quiz_questions
        ) AS numbered
        WHERE quiz_questions.id = numbered.id
        """
    )

    op.create_index(
        "ix_courses_teacher_id",
        "courses",
        ["teacher_id"],
        unique=False,
    )
    op.create_index(
        "ix_modules_course_order",
        "modules",
        ["course_id", "order_index"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_modules_course_order_index",
        "modules",
        ["course_id", "order_index"],
    )
    op.create_index(
        "ix_quiz_questions_module_order",
        "quiz_questions",
        ["module_id", "order_index"],
        unique=False,
    )
    op.create_index(
        "ix_quiz_attempts_student_module",
        "quiz_attempts",
        ["student_id", "module_id", "attempted_at"],
        unique=False,
    )
    op.create_index(
        "ix_submissions_student_practical",
        "submissions",
        ["student_id", "practical_id"],
        unique=False,
    )
    op.create_index(
        "ix_submissions_practical_submitted_at",
        "submissions",
        ["practical_id", "submitted_at"],
        unique=False,
    )
    op.create_index(
        "ix_users_group_id",
        "users",
        ["group_id"],
        unique=False,
    )
    op.create_index(
        "uq_users_group_list_number",
        "users",
        ["group_id", "list_number"],
        unique=True,
        postgresql_where=sa.text("group_id IS NOT NULL AND list_number IS NOT NULL"),
        sqlite_where=sa.text("group_id IS NOT NULL AND list_number IS NOT NULL"),
    )


def downgrade() -> None:
    """Симетрично видаляє створені індекси, унікальні обмеження та quiz_questions.order_index."""
    op.drop_index("uq_users_group_list_number", table_name="users")
    op.drop_index("ix_users_group_id", table_name="users")
    op.drop_index("ix_submissions_practical_submitted_at", table_name="submissions")
    op.drop_index("ix_submissions_student_practical", table_name="submissions")
    op.drop_index("ix_quiz_attempts_student_module", table_name="quiz_attempts")
    op.drop_index("ix_quiz_questions_module_order", table_name="quiz_questions")
    op.drop_constraint(
        "uq_modules_course_order_index",
        "modules",
        type_="unique",
    )
    op.drop_index("ix_modules_course_order", table_name="modules")
    op.drop_index("ix_courses_teacher_id", table_name="courses")
    op.drop_column("quiz_questions", "order_index")
