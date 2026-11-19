import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    SmallInteger,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

MIN_COURSE_YEAR: int = 1
MAX_COURSE_YEAR: int = 4


class UserRole(StrEnum):
    """Ролі користувачів у системі."""

    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


def _enum_values(enum_cls: type[UserRole]) -> list[str]:
    """Повертає список рядкових значень Enum для збереження у PostgreSQL ENUM."""
    return [member.value for member in enum_cls]


class AcademicGroup(Base):
    """Академічна група коледжу (таблиця `academic_groups`)."""

    __tablename__ = "academic_groups"
    __table_args__ = (
        CheckConstraint(
            f"course_year >= {MIN_COURSE_YEAR} AND course_year <= {MAX_COURSE_YEAR}",
            name="ck_academic_groups_course_year_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
    )
    specialty: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    course_year: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="group",
    )


class User(Base):
    """Користувач системи: студент, викладач або адміністратор (таблиця `users`)."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    group_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("academic_groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    list_number: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    group: Mapped[AcademicGroup | None] = relationship(
        "AcademicGroup",
        back_populates="users",
    )
