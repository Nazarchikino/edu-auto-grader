import uuid
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, SmallInteger, String, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.progress import QuizAttempt, Submission
    from app.models.user import User


class CourseSlug(StrEnum):
    """Доступні дисципліни (ідентифікатори курсів)."""

    WORD = "word"
    EXCEL = "excel"
    ACCESS = "access"
    HTML = "html"


class PracticalFormat(StrEnum):
    """Формати практичних робіт для ядра автоперевірки."""

    DOCX = "docx"
    XLSX = "xlsx"
    ACCDB = "accdb"
    HTML = "html"


def _enum_values(enum_cls: type[StrEnum]) -> list[str]:
    """Повертає список рядкових значень Enum для збереження у PostgreSQL ENUM."""
    return [member.value for member in enum_cls]


class Course(Base):
    """Навчальний курс із дисципліни (таблиця `courses`)."""

    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[CourseSlug] = mapped_column(
        Enum(
            CourseSlug,
            name="course_slug",
            values_callable=_enum_values,
        ),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    teacher: Mapped["User"] = relationship("User")
    modules: Mapped[list["Module"]] = relationship(
        "Module",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Module.order_index",
    )


class Module(Base):
    """Навчальний модуль курсу з лекцією, тестом та практичною (таблиця `modules`)."""

    __tablename__ = "modules"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    lecture_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    course: Mapped[Course] = relationship(
        "Course",
        back_populates="modules",
    )
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(
        "QuizQuestion",
        back_populates="module",
        cascade="all, delete-orphan",
    )
    practical: Mapped["Practical | None"] = relationship(
        "Practical",
        back_populates="module",
        uselist=False,
        cascade="all, delete-orphan",
    )
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt",
        back_populates="module",
        cascade="all, delete-orphan",
    )


class QuizQuestion(Base):
    """Тестове питання для допуску до практичної роботи модуля (таблиця `quiz_questions`)."""

    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    options: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )
    correct_option_index: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    module: Mapped[Module] = relationship(
        "Module",
        back_populates="quiz_questions",
    )


class Practical(Base):
    """Практична робота модуля з варіантами та правилами автоперевірки (таблиця `practicals`)."""

    __tablename__ = "practicals"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    instructions: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    format_type: Mapped[PracticalFormat] = mapped_column(
        Enum(
            PracticalFormat,
            name="practical_format",
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("10.00"),
        server_default=text("10.00"),
        nullable=False,
    )
    variants: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    grading_rules: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    module: Mapped[Module] = relationship(
        "Module",
        back_populates="practical",
    )
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="practical",
        cascade="all, delete-orphan",
    )
