"""initial_schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-18 21:55:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

user_role_enum = postgresql.ENUM(
    "student",
    "teacher",
    "admin",
    name="user_role",
    create_type=False,
)
course_slug_enum = postgresql.ENUM(
    "word",
    "excel",
    "access",
    "html",
    name="course_slug",
    create_type=False,
)
practical_format_enum = postgresql.ENUM(
    "docx",
    "xlsx",
    "accdb",
    "html",
    name="practical_format",
    create_type=False,
)


def upgrade() -> None:
    """Створення початкової схеми БД для всіх 8 таблиць та ENUM-типів."""
    bind = op.get_bind()
    user_role_enum.create(bind, checkfirst=True)
    course_slug_enum.create(bind, checkfirst=True)
    practical_format_enum.create(bind, checkfirst=True)

    op.create_table(
        "academic_groups",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("specialty", sa.String(length=128), nullable=False),
        sa.Column("course_year", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_academic_groups_code"),
        "academic_groups",
        ["code"],
        unique=True,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("group_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("list_number", sa.SmallInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["academic_groups.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )

    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", course_slug_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("teacher_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_courses_slug"),
        "courses",
        ["slug"],
        unique=True,
    )

    op.create_table(
        "modules",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("course_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("order_index", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("lecture_content", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("module_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("correct_option_index", sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["module_id"],
            ["modules.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("student_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("module_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("score_percent", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column(
            "attempted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["module_id"],
            ["modules.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "practicals",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("module_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("format_type", practical_format_enum, nullable=False),
        sa.Column(
            "max_score",
            sa.Numeric(precision=5, scale=2),
            server_default=sa.text("10.00"),
            nullable=False,
        ),
        sa.Column("variants", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("grading_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["module_id"],
            ["modules.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("module_id"),
    )

    op.create_table(
        "submissions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("practical_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("student_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("variant_index", sa.SmallInteger(), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column("raw_code", sa.Text(), nullable=True),
        sa.Column("file_hash", sa.String(length=64), nullable=True),
        sa.Column(
            "extracted_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "is_plagiarism_flagged",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("plagiarism_reason", sa.Text(), nullable=True),
        sa.Column("auto_score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("final_score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("grading_report", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("teacher_comment", sa.Text(), nullable=True),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["practical_id"],
            ["practicals.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_submissions_file_hash"),
        "submissions",
        ["file_hash"],
        unique=False,
    )


def downgrade() -> None:
    """Відкат початкової схеми БД у зворотному порядку залежностей."""
    op.drop_index(op.f("ix_submissions_file_hash"), table_name="submissions")
    op.drop_table("submissions")
    op.drop_table("practicals")
    op.drop_table("quiz_attempts")
    op.drop_table("quiz_questions")
    op.drop_table("modules")
    op.drop_index(op.f("ix_courses_slug"), table_name="courses")
    op.drop_table("courses")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_academic_groups_code"), table_name="academic_groups")
    op.drop_table("academic_groups")

    bind = op.get_bind()
    practical_format_enum.drop(bind, checkfirst=True)
    course_slug_enum.drop(bind, checkfirst=True)
    user_role_enum.drop(bind, checkfirst=True)
