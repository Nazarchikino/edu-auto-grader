import math
import uuid
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import DomainError, QuizNotPassedError
from app.models.course import Module, Practical, QuizQuestion
from app.models.progress import QuizAttempt
from app.models.user import User
from app.schemas.course import (
    PracticalStudentRead,
    PracticalVariant,
    QuizSubmitRequest,
    QuizSubmitResponse,
)


def get_quiz_pass_threshold_percent() -> Decimal:
    """Повертає поточний поріг успішного складання тесту-допуску з налаштувань."""
    return Decimal(str(settings.QUIZ_PASS_THRESHOLD_PERCENT)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def _ensure_utc(dt: datetime) -> datetime:
    """Нормалізує часову мітку до UTC (зокрема для naive datetime у SQLite)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def format_cooldown_remaining(seconds: int) -> str:
    """Форматує залишок часу cooldown у вигляді «X хв Y сек»."""
    safe_seconds = max(0, seconds)
    minutes, rem_seconds = divmod(safe_seconds, 60)
    return f"{minutes} хв {rem_seconds} сек"


def calculate_variant_index(list_number: int | None, total_variants: int) -> int:
    """Обчислює 0-орієнтований індекс варіанта студента за формулою специфікації."""
    if total_variants <= 0:
        return 0
    effective_list_number = list_number if list_number is not None and list_number > 0 else 1
    return (effective_list_number - 1) % total_variants


def resolve_student_variant(
    practical: Practical,
    list_number: int | None,
) -> tuple[int, int, PracticalVariant]:
    """Визначає індекс, номер та об'єкт індивідуального варіанта практичної для студента."""
    raw_variants = practical.variants
    total_variants = len(raw_variants)
    variant_index = calculate_variant_index(list_number, total_variants)
    variant_number = variant_index + 1

    if total_variants == 0:
        fallback_variant = PracticalVariant(
            variant_number=1,
            title=practical.title,
            task_description=practical.instructions,
            parameters={},
        )
        return 0, 1, fallback_variant

    selected_raw = raw_variants[variant_index]
    raw_parameters = selected_raw.get("parameters")
    parameters: dict[str, object] = (
        dict(raw_parameters) if isinstance(raw_parameters, dict) else {}
    )
    title_raw = selected_raw.get("title")
    description_raw = selected_raw.get("task_description")

    variant = PracticalVariant(
        variant_number=variant_number,
        title=(
            str(title_raw)
            if isinstance(title_raw, str) and title_raw.strip()
            else f"Варіант {variant_number}"
        ),
        task_description=(
            str(description_raw)
            if isinstance(description_raw, str) and description_raw.strip()
            else practical.instructions
        ),
        parameters=parameters,
    )
    return variant_index, variant_number, variant


class QuizService:
    """Сервіс перевірки тестів-допусків та контролю доступу до практичних робіт."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_module_quiz_status(
        self,
        *,
        student_id: uuid.UUID,
        module_id: uuid.UUID,
        has_questions: bool = True,
    ) -> tuple[bool, float | None]:
        """Повертає прапорець успішного складання тесту та найкращий результат студента."""
        stmt = select(
            func.max(case((QuizAttempt.passed.is_(True), 1), else_=0)),
            func.max(QuizAttempt.score_percent),
        ).where(
            QuizAttempt.student_id == student_id,
            QuizAttempt.module_id == module_id,
        )
        result = await self._db.execute(stmt)
        row = result.one()
        passed_flag: int | None = row[0]
        max_score: Decimal | None = row[1]

        quiz_passed = True if not has_questions else bool(passed_flag)
        best_score = float(max_score) if max_score is not None else None
        return quiz_passed, best_score

    async def get_quiz_cooldown_remaining_seconds(
        self,
        *,
        student_id: uuid.UUID,
        module_id: uuid.UUID,
        quiz_passed: bool | None = None,
        now: datetime | None = None,
    ) -> int:
        """Обчислює залишок часу очікування (у секундах) після невдалої спроби тесту."""
        cooldown_seconds = int(settings.QUIZ_RETRY_COOLDOWN_SECONDS)
        if cooldown_seconds <= 0:
            return 0

        if quiz_passed is None:
            already_passed, _ = await self.get_module_quiz_status(
                student_id=student_id,
                module_id=module_id,
                has_questions=True,
            )
        else:
            already_passed = quiz_passed

        if already_passed:
            return 0

        latest_stmt = (
            select(QuizAttempt)
            .where(
                QuizAttempt.student_id == student_id,
                QuizAttempt.module_id == module_id,
            )
            .order_by(QuizAttempt.attempted_at.desc(), QuizAttempt.id.desc())
            .limit(1)
        )
        latest_result = await self._db.execute(latest_stmt)
        latest_attempt = latest_result.scalar_one_or_none()
        if latest_attempt is None or latest_attempt.passed:
            return 0

        reference_now = _ensure_utc(now) if now is not None else datetime.now(UTC)
        attempt_time = _ensure_utc(latest_attempt.attempted_at)
        elapsed_seconds = max(0.0, (reference_now - attempt_time).total_seconds())
        remaining_float = float(cooldown_seconds) - elapsed_seconds
        if remaining_float <= 0.0:
            return 0

        return min(cooldown_seconds, max(1, math.ceil(remaining_float)))

    async def has_passed_quiz(
        self,
        *,
        student_id: uuid.UUID,
        module_id: uuid.UUID,
    ) -> bool:
        """Перевіряє, чи склав студент тест-допуск для вказаного модуля."""
        module_stmt = select(Module.id).where(Module.id == module_id)
        module_result = await self._db.execute(module_stmt)
        module_exists = module_result.scalar_one_or_none() is not None
        if not module_exists:
            has_questions = True
        else:
            questions_count_stmt = select(func.count(QuizQuestion.id)).where(
                QuizQuestion.module_id == module_id
            )
            questions_count_result = await self._db.execute(questions_count_stmt)
            has_questions = int(questions_count_result.scalar_one()) > 0

        quiz_passed, _ = await self.get_module_quiz_status(
            student_id=student_id,
            module_id=module_id,
            has_questions=has_questions,
        )
        return quiz_passed

    async def ensure_quiz_passed(
        self,
        *,
        student_id: uuid.UUID,
        module_id: uuid.UUID,
    ) -> None:
        """Генерує QuizNotPassedError, якщо студент ще не склав тест-допуск модуля."""
        passed = await self.has_passed_quiz(
            student_id=student_id,
            module_id=module_id,
        )
        if not passed:
            threshold = get_quiz_pass_threshold_percent()
            raise QuizNotPassedError(
                detail=(
                    f"Необхідно успішно скласти тест-допуск (>= {float(threshold):g}%) "
                    "перед здачею практичної роботи."
                ),
                context={
                    "module_id": str(module_id),
                    "student_id": str(student_id),
                    "pass_threshold_percent": float(threshold),
                },
            )

    async def submit_quiz(
        self,
        *,
        student: User,
        module_id: uuid.UUID,
        payload: QuizSubmitRequest,
    ) -> QuizSubmitResponse:
        """Оцінює відповіді студента на тест-допуск із перевіркою повноти та cooldown."""
        stmt = select(Module).where(Module.id == module_id)
        result = await self._db.execute(stmt)
        module = result.scalar_one_or_none()
        if module is None:
            raise DomainError(
                "Навчальний модуль не знайдено.",
                code="MODULE_NOT_FOUND",
                status_code=404,
                context={"module_id": str(module_id)},
            )

        questions_stmt = (
            select(QuizQuestion)
            .where(QuizQuestion.module_id == module.id)
            .order_by(QuizQuestion.order_index.asc(), QuizQuestion.id.asc())
        )
        questions_result = await self._db.execute(questions_stmt)
        questions = list(questions_result.scalars().all())
        total_questions = len(questions)
        if total_questions == 0:
            raise DomainError(
                "У цьому модулі ще не налаштовано тестових питань.",
                code="QUIZ_EMPTY",
                status_code=422,
                context={"module_id": str(module_id)},
            )

        questions_by_id = {question.id: question for question in questions}
        submitted_answers: dict[uuid.UUID, int] = {}

        for item in payload.answers:
            question = questions_by_id.get(item.question_id)
            if question is None:
                raise DomainError(
                    "Тестове питання не належить до вказаного модуля.",
                    code="INVALID_QUIZ_QUESTION",
                    status_code=422,
                    context={
                        "module_id": str(module_id),
                        "question_id": str(item.question_id),
                    },
                )
            if item.question_id in submitted_answers:
                raise DomainError(
                    "Запит містить дублікати відповідей на одне й те саме питання.",
                    code="DUPLICATE_QUIZ_ANSWER",
                    status_code=422,
                    context={"question_id": str(item.question_id)},
                )
            if item.selected_option_index >= len(question.options):
                raise DomainError(
                    "Індекс обраної відповіді виходить за межі доступних варіантів.",
                    code="INVALID_QUIZ_OPTION_INDEX",
                    status_code=422,
                    context={
                        "question_id": str(item.question_id),
                        "selected_option_index": item.selected_option_index,
                        "options_count": len(question.options),
                    },
                )
            submitted_answers[item.question_id] = item.selected_option_index

        if set(submitted_answers.keys()) != set(questions_by_id.keys()):
            missing_count = total_questions - len(submitted_answers)
            raise DomainError(
                f"Необхідно відповісти на всі питання тесту "
                f"({len(submitted_answers)} із {total_questions}, пропущено: {missing_count}).",
                code="INCOMPLETE_QUIZ_SUBMISSION",
                status_code=422,
                context={
                    "module_id": str(module_id),
                    "answered_count": len(submitted_answers),
                    "total_questions": total_questions,
                    "missing_count": missing_count,
                },
            )

        previously_passed, _ = await self.get_module_quiz_status(
            student_id=student.id,
            module_id=module.id,
            has_questions=True,
        )

        cooldown_remaining = await self.get_quiz_cooldown_remaining_seconds(
            student_id=student.id,
            module_id=module.id,
            quiz_passed=previously_passed,
        )
        if cooldown_remaining > 0:
            formatted_wait = format_cooldown_remaining(cooldown_remaining)
            raise DomainError(
                f"Повторна спроба буде доступна через {formatted_wait}. "
                "Перечитайте конспект лекції.",
                code="QUIZ_RETRY_COOLDOWN",
                status_code=429,
                context={
                    "module_id": str(module_id),
                    "retry_after_seconds": cooldown_remaining,
                },
                headers={"Retry-After": str(cooldown_remaining)},
            )

        correct_count = sum(
            1
            for question in questions
            if submitted_answers.get(question.id) == question.correct_option_index
        )

        raw_percent = (Decimal(correct_count) * Decimal("100")) / Decimal(total_questions)
        score_percent = raw_percent.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        threshold_percent = get_quiz_pass_threshold_percent()
        passed = score_percent >= threshold_percent

        attempt = QuizAttempt(
            student_id=student.id,
            module_id=module.id,
            score_percent=score_percent,
            passed=passed,
        )
        self._db.add(attempt)
        await self._db.commit()
        await self._db.refresh(attempt)

        practical_unlocked = passed or previously_passed
        retry_after_seconds = (
            max(0, int(settings.QUIZ_RETRY_COOLDOWN_SECONDS))
            if not passed and not previously_passed
            else 0
        )

        return QuizSubmitResponse(
            id=attempt.id,
            module_id=module.id,
            score_percent=float(attempt.score_percent),
            passed=attempt.passed,
            correct_count=correct_count,
            total_questions=total_questions,
            practical_unlocked=practical_unlocked,
            attempted_at=attempt.attempted_at,
            retry_after_seconds=retry_after_seconds,
        )

    async def get_student_practical(
        self,
        *,
        student: User,
        practical_id: uuid.UUID,
    ) -> PracticalStudentRead:
        """Повертає умову практичної роботи та індивідуальний варіант студента."""
        stmt = select(Practical).where(Practical.id == practical_id)
        result = await self._db.execute(stmt)
        practical = result.scalar_one_or_none()
        if practical is None:
            raise DomainError(
                "Практичну роботу не знайдено.",
                code="PRACTICAL_NOT_FOUND",
                status_code=404,
                context={"practical_id": str(practical_id)},
            )

        await self.ensure_quiz_passed(
            student_id=student.id,
            module_id=practical.module_id,
        )

        variant_index, variant_number, variant = resolve_student_variant(
            practical=practical,
            list_number=student.list_number,
        )

        return PracticalStudentRead(
            id=practical.id,
            module_id=practical.module_id,
            title=practical.title,
            instructions=practical.instructions,
            format_type=practical.format_type,
            max_score=float(practical.max_score),
            variant_index=variant_index,
            variant_number=variant_number,
            variant=variant,
        )


__all__ = [
    "QuizService",
    "calculate_variant_index",
    "format_cooldown_remaining",
    "get_quiz_pass_threshold_percent",
    "resolve_student_variant",
]
