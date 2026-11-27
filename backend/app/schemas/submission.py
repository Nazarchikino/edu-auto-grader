import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from app.models.course import CourseSlug, PracticalFormat
from app.schemas.grading import ExtractedMetadata, GradingReport, GradingRule

MAX_HTML_CODE_LENGTH: int = 250_000


class ExportFormat(StrEnum):
    """Доступні формати експорту відомості успішності академічної групи."""

    XLSX = "xlsx"
    PDF = "pdf"


class HtmlSubmissionRequest(BaseModel):
    """Запит студента на здачу та автоперевірку HTML-коду із вбудованої пісочниці."""

    model_config = ConfigDict(extra="forbid")

    raw_code: str = Field(
        ...,
        min_length=1,
        max_length=MAX_HTML_CODE_LENGTH,
        description="Вихідний HTML5-код, написаний студентом у редакторі",
    )


class HtmlDryRunRequest(BaseModel):
    """Запит викладача на тестову (dry-run) перевірку HTML-коду без запису в БД."""

    model_config = ConfigDict(extra="forbid")

    raw_code: str = Field(
        ...,
        min_length=1,
        max_length=MAX_HTML_CODE_LENGTH,
        description="Вихідний HTML5-код для тестової перевірки правил",
    )
    variant_number: int = Field(
        default=1,
        ge=1,
        description="Номер індивідуального варіанта (1..N) для підстановки параметрів",
    )
    rules_override: list[GradingRule] | None = Field(
        default=None,
        min_length=1,
        description=(
            "Опційний список чернеткових правил перевірки, "
            "які застосовуються замість збережених без зміни БД"
        ),
    )


class DryRunGradingResponse(BaseModel):
    """Результат безпечної тестової (dry-run) перевірки практичної роботи без побічних ефектів."""

    model_config = ConfigDict(extra="forbid")

    practical_id: uuid.UUID
    format_type: PracticalFormat
    variant_number: int = Field(..., ge=1)
    auto_score: Decimal = Field(..., ge=Decimal("0"))
    auto_max_score: Decimal = Field(..., ge=Decimal("0"))
    max_score: Decimal = Field(..., gt=Decimal("0"))
    manual_bonus_max: Decimal = Field(..., ge=Decimal("0"))
    grading_report: GradingReport
    extracted_metadata: ExtractedMetadata = Field(default_factory=ExtractedMetadata)

    @field_serializer(
        "auto_score",
        "auto_max_score",
        "max_score",
        "manual_bonus_max",
        when_used="json",
    )
    def _serialize_scores(self, value: Decimal) -> float:
        """Серіалізує бали як JSON-числа для узгодженості з іншими API-контрактами."""
        return round(float(value), 2)


class ManualGradeUpdateRequest(BaseModel):
    """Запит викладача на ручне коригування оцінки та додавання коментаря до здачі."""

    model_config = ConfigDict(extra="forbid")

    final_score: float | None = Field(
        default=None,
        ge=0.0,
        allow_inf_nan=False,
        description="Скоригований викладачем підсумковий бал",
    )
    teacher_score_adjustment: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description=(
            "Відносне коригування бала понад auto_score "
            "(наприклад, +1.0 або +2.0 за творче завдання)"
        ),
    )
    teacher_comment: str | None = Field(
        default=None,
        max_length=2000,
        description="Коментар викладача щодо роботи або виявленого плагіату",
    )

    @model_validator(mode="after")
    def _validate_score_input(self) -> "ManualGradeUpdateRequest":
        if self.final_score is None and self.teacher_score_adjustment is None:
            raise ValueError(
                "Необхідно передати 'final_score' або 'teacher_score_adjustment'."
            )
        if self.final_score is not None and self.teacher_score_adjustment is not None:
            raise ValueError(
                "Передайте або 'final_score', або 'teacher_score_adjustment', "
                "але не обидва поля одночасно."
            )
        return self


class SubmissionRead(BaseModel):
    """Повна інформація про здачу практичної роботи, антиплагіат та звіт автоперевірки."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    practical_id: uuid.UUID
    practical_title: str | None = None
    course_slug: CourseSlug | None = None
    student_id: uuid.UUID
    student_full_name: str | None = None
    variant_index: int = Field(..., ge=0)
    variant_number: int = Field(default=1, ge=1)
    file_path: str | None = None
    raw_code: str | None = None
    file_hash: str | None = None
    extracted_metadata: ExtractedMetadata = Field(default_factory=ExtractedMetadata)
    is_plagiarism_flagged: bool = False
    plagiarism_reason: str | None = None
    auto_score: float = Field(..., ge=0.0)
    final_score: float = Field(..., ge=0.0)
    max_score: float = Field(default=12.0, gt=0.0)
    auto_max_score: float = Field(default=10.0, ge=0.0)
    manual_bonus_max: float = Field(default=2.0, ge=0.0)
    grading_report: GradingReport
    teacher_comment: str | None = None
    submitted_at: datetime
    is_file_available: bool = False
    file_expires_at: datetime | None = None


class CriterionErrorStat(BaseModel):
    """Аналітична статистика помилок студентів групи за окремим критерієм перевірки."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str
    description: str
    total_attempts: int = Field(..., ge=0)
    failure_count: int = Field(..., ge=0)
    failure_rate_percent: float = Field(..., ge=0.0, le=100.0)


class GroupJournalStudentCell(BaseModel):
    """Комірка електронного журналу групи з результатом студента за одну практичну роботу."""

    model_config = ConfigDict(extra="forbid")

    practical_id: uuid.UUID
    submission_id: uuid.UUID | None = None
    auto_score: float | None = None
    final_score: float | None = None
    is_plagiarism_flagged: bool = False
    plagiarism_reason: str | None = None
    submitted_at: datetime | None = None


class GroupJournalRow(BaseModel):
    """Рядок студента у зведеній відомості успішності академічної групи."""

    model_config = ConfigDict(extra="forbid")

    student_id: uuid.UUID
    student_full_name: str
    list_number: int | None = None
    cells: list[GroupJournalStudentCell] = Field(default_factory=list)
    total_score: float = Field(default=0.0, ge=0.0)


class GroupJournalPracticalRead(BaseModel):
    """Метадані стовпця практичної роботи у зведеній відомості успішності групи."""

    model_config = ConfigDict(extra="forbid")

    practical_id: uuid.UUID
    title: str
    course_slug: CourseSlug
    module_order_index: int = Field(..., ge=1)
    max_score: float = Field(..., gt=0.0)
    needs_rules_review: bool = False


class GroupJournalRead(BaseModel):
    """Зведена відомість успішності академічної групи з аналітикою типових помилок."""

    model_config = ConfigDict(extra="forbid")

    group_id: uuid.UUID
    group_code: str
    specialty: str
    practicals: list[GroupJournalPracticalRead] = Field(default_factory=list)
    rows: list[GroupJournalRow] = Field(default_factory=list)
    error_stats: list[CriterionErrorStat] = Field(default_factory=list)
