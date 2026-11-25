import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.course import CourseSlug, PracticalFormat
from app.schemas.grading import GradingRule


class QuizQuestionCreate(BaseModel):
    """Схема створення тестового питання для допуску до практичної роботи."""

    model_config = ConfigDict(extra="forbid")

    question_text: str = Field(..., min_length=1)
    options: list[str] = Field(..., min_length=2)
    correct_option_index: int = Field(..., ge=0)


class QuizQuestionRead(BaseModel):
    """Публічне представлення питання тесту-допуску для студента (без правильної відповіді)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    module_id: uuid.UUID
    question_text: str
    options: list[str]


class QuizQuestionTeacherRead(QuizQuestionRead):
    """Повне представлення тестового питання для викладача з індексом правильної відповіді."""

    correct_option_index: int = Field(..., ge=0)


class QuizAnswerItem(BaseModel):
    """Вибрана студентом відповідь на одне питання тесту-допуску."""

    model_config = ConfigDict(extra="forbid")

    question_id: uuid.UUID
    selected_option_index: int = Field(..., ge=0)


class QuizSubmitRequest(BaseModel):
    """Запит студента на перевірку відповідей тесту-допуску модуля."""

    model_config = ConfigDict(extra="forbid")

    answers: list[QuizAnswerItem] = Field(..., min_length=1)


class QuizSubmitResponse(BaseModel):
    """Результат проходження студентом тесту-допуску та статус розблокування практичної."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    module_id: uuid.UUID
    score_percent: float = Field(..., ge=0.0, le=100.0)
    passed: bool
    correct_count: int = Field(..., ge=0)
    total_questions: int = Field(..., ge=0)
    practical_unlocked: bool
    attempted_at: datetime
    retry_after_seconds: int = Field(default=0, ge=0)


class PracticalVariant(BaseModel):
    """Опис індивідуального варіанта завдання практичної роботи."""

    model_config = ConfigDict(extra="forbid")

    variant_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=1)
    task_description: str = Field(..., min_length=1)
    parameters: dict[str, object] = Field(default_factory=dict)


class PracticalCreate(BaseModel):
    """Схема створення або повного оновлення практичної роботи модуля викладачем."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=255)
    instructions: str = Field(..., min_length=1)
    format_type: PracticalFormat
    max_score: float = Field(default=10.0, gt=0.0)
    variants: list[PracticalVariant] = Field(default_factory=list)
    grading_rules: list[GradingRule] = Field(default_factory=list)


class PracticalUpdate(BaseModel):
    """Схема часткового оновлення методичних вказівок та параметрів практичної роботи."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=255)
    instructions: str | None = Field(default=None, min_length=1)
    format_type: PracticalFormat | None = None
    max_score: float | None = Field(default=None, gt=0.0)
    variants: list[PracticalVariant] | None = None
    grading_rules: list[GradingRule] | None = None


class PracticalSummaryRead(BaseModel):
    """Стисла інформація про практичну роботу в контексті навчального модуля."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    format_type: PracticalFormat
    max_score: float = Field(..., gt=0.0)
    is_unlocked: bool = False
    best_score: float | None = None


class PracticalStudentRead(BaseModel):
    """Повні умови практичної роботи з розрахованим індивідуальним варіантом студента."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    instructions: str
    format_type: PracticalFormat
    max_score: float = Field(..., gt=0.0)
    variant_index: int = Field(..., ge=0)
    variant_number: int = Field(..., ge=1)
    variant: PracticalVariant


class PracticalTeacherRead(BaseModel):
    """Повне представлення практичної роботи для викладача з усіма варіантами та правилами."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    instructions: str
    format_type: PracticalFormat
    max_score: float = Field(..., gt=0.0)
    variants: list[PracticalVariant] = Field(default_factory=list)
    grading_rules: list[GradingRule] = Field(default_factory=list)


class ModuleCreate(BaseModel):
    """Схема створення навчального модуля (теми) в межах курсу."""

    model_config = ConfigDict(extra="forbid")

    order_index: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=255)
    lecture_content: str = Field(..., min_length=1)


class ModuleUpdate(BaseModel):
    """Схема оновлення навчального модуля викладачем."""

    model_config = ConfigDict(extra="forbid")

    order_index: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    lecture_content: str | None = Field(default=None, min_length=1)


class ModuleSummaryRead(BaseModel):
    """Елемент списку модулів курсу зі статусом проходження для поточного студента."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    order_index: int
    title: str
    quiz_passed: bool = False
    best_quiz_score: float | None = None
    practical_id: uuid.UUID | None = None
    practical_format: PracticalFormat | None = None
    practical_score: float | None = None


class ModuleDetailRead(BaseModel):
    """Детальне представлення модуля: текст лекції, питання тесту-допуску та практична."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    order_index: int
    title: str
    lecture_content: str
    quiz_questions: list[QuizQuestionRead] = Field(default_factory=list)
    quiz_passed: bool = False
    best_quiz_score: float | None = None
    quiz_cooldown_remaining_seconds: int = Field(default=0, ge=0)
    practical_unlocked: bool = False
    practical: PracticalSummaryRead | None = None


class CourseCreate(BaseModel):
    """Схема створення нового курсу викладачем."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=255)
    slug: CourseSlug
    description: str = Field(..., min_length=1)


class CourseUpdate(BaseModel):
    """Схема редагування курсу викладачем або адміністратором."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    teacher_id: uuid.UUID | None = None


class CourseRead(BaseModel):
    """Представлення курсу з переліком модулів та відсотком прогресу студента."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: CourseSlug
    description: str
    teacher_id: uuid.UUID
    total_modules: int = Field(default=0, ge=0)
    completed_modules: int = Field(default=0, ge=0)
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    modules: list[ModuleSummaryRead] = Field(default_factory=list)
