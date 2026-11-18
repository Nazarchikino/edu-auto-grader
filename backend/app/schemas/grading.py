import uuid
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.models.course import PracticalFormat


class GradingRuleType(StrEnum):
    """Підтримувані типи детермінованих правил автоперевірки для всіх парсерів."""

    # Microsoft Word (.docx)
    DOCX_PAGE_MARGINS = "docx_page_margins"
    DOCX_FONT = "docx_font"
    DOCX_LINE_SPACING = "docx_line_spacing"
    DOCX_ALIGNMENT = "docx_alignment"
    DOCX_TABLE_EXISTS = "docx_table_exists"
    DOCX_LIST_EXISTS = "docx_list_exists"

    # Microsoft Excel (.xlsx)
    XLSX_FORMULA = "xlsx_formula"
    XLSX_VALUE = "xlsx_value"
    XLSX_CHART_EXISTS = "xlsx_chart_exists"

    # Microsoft Access (.accdb)
    ACCDB_TABLE_EXISTS = "accdb_table_exists"
    ACCDB_COLUMN_EXISTS = "accdb_column_exists"
    ACCDB_COLUMN_TYPE = "accdb_column_type"

    # HTML5 (BeautifulSoup4 DOM)
    HTML_TAG_EXISTS = "html_tag_exists"
    HTML_TAG_COUNT = "html_tag_count"
    HTML_ATTRIBUTE_EXISTS = "html_attribute_exists"


class GradingRule(BaseModel):
    """Декларативне правило оцінювання одного критерію практичної роботи."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Унікальний ідентифікатор правила в межах практичної роботи",
    )
    type: GradingRuleType = Field(
        ...,
        description="Тип перевірки для відповідного парсера",
    )
    target: str = Field(
        ...,
        min_length=1,
        description="Цільовий елемент перевірки (комірка, селектор, таблиця.поле, секція)",
    )
    expected: str = Field(
        ...,
        min_length=1,
        description="Очікуване значення або вираз умови",
    )
    points: float = Field(
        ...,
        gt=0.0,
        description="Максимальна кількість балів за виконання критерію",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Людиночитабельний опис критерію для звіту",
    )


class CriterionResult(BaseModel):
    """Результат перевірки окремого критерію (правила) ядром автоперевірки."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(..., min_length=1)
    rule_type: GradingRuleType
    target: str = Field(..., min_length=1)
    expected: str = Field(..., min_length=1)
    actual: str | None = Field(
        default=None,
        description="Фактичне знайдене значення у файлі або коді студента",
    )
    passed: bool = Field(
        ...,
        description="Чи виконано умову критерію",
    )
    points_awarded: float = Field(
        ...,
        ge=0.0,
        description="Нараховані бали за критерій",
    )
    max_points: float = Field(
        ...,
        gt=0.0,
        description="Максимально можливі бали за критерій",
    )
    description: str = Field(..., min_length=1)
    feedback: str = Field(
        ...,
        min_length=1,
        description="Детальне пояснення результату перевірки критерію",
    )


class GradingReport(BaseModel):
    """Підсумковий деталізований звіт автоматизованої перевірки практичної роботи."""

    model_config = ConfigDict(extra="forbid")

    format_type: PracticalFormat
    total_points: float = Field(
        ...,
        ge=0.0,
        description="Сума нарахованих балів за всіма критеріями",
    )
    max_points: float = Field(
        ...,
        ge=0.0,
        description="Максимально можлива сума балів за правилами",
    )
    passed_count: int = Field(
        ...,
        ge=0,
        description="Кількість успішно виконаних критеріїв",
    )
    failed_count: int = Field(
        ...,
        ge=0,
        description="Кількість провалених критеріїв",
    )
    results: list[CriterionResult] = Field(
        default_factory=list,
        description="Перелік результатів по кожному окремому правилу",
    )


class ExtractedMetadata(BaseModel):
    """Метадані документа (docProps/core.xml або властивості файлу) для контролю авторства."""

    model_config = ConfigDict(extra="allow")

    creator: str | None = None
    last_modified_by: str | None = None
    created: str | None = None
    modified: str | None = None
    revision: str | None = None


class PlagiarismCheckResult(BaseModel):
    """Результат перевірки здачі на академічну доброчесність (SHA-256 та core.xml)."""

    model_config = ConfigDict(extra="forbid")

    is_flagged: bool = False
    reason: str | None = None
    matched_submission_id: uuid.UUID | None = None
    matched_student_id: uuid.UUID | None = None


class GradingRulesUpdateRequest(BaseModel):
    """Запит викладача на оновлення списку правил автоперевірки практичної роботи."""

    model_config = ConfigDict(extra="forbid")

    grading_rules: list[GradingRule] = Field(
        ...,
        min_length=1,
        description="Новий перелік декларативних правил оцінювання",
    )
