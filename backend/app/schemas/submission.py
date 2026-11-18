import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.models.course import CourseSlug
from app.schemas.grading import ExtractedMetadata, GradingReport


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
        description="Вихідний HTML5-код, написаний студентом у редакторі",
    )


class ManualGradeUpdateRequest(BaseModel):
    """Запит викладача на ручне коригування оцінки та додавання коментаря до здачі."""

    model_config = ConfigDict(extra="forbid")

    final_score: float = Field(
        ...,
        ge=0.0,
        description="Скоригований викладачем підсумковий бал",
    )
    teacher_comment: str | None = Field(
        default=None,
        max_length=2000,
        description="Коментар викладача щодо роботи або виявленого плагіату",
    )


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
    max_score: float = Field(default=10.0, gt=0.0)
    grading_report: GradingReport
    teacher_comment: str | None = None
    submitted_at: datetime


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


class GroupJournalRead(BaseModel):
    """Зведена відомість успішності академічної групи з аналітикою типових помилок."""

    model_config = ConfigDict(extra="forbid")

    group_id: uuid.UUID
    group_code: str
    specialty: str
    rows: list[GroupJournalRow] = Field(default_factory=list)
    error_stats: list[CriterionErrorStat] = Field(default_factory=list)
