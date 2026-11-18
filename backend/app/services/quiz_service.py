import uuid
from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DomainError, QuizNotPassedError
from app.models.course import Module, Practical
from app.models.progress import QuizAttempt
from app.models.user import User
from app.schemas.course import (
    PracticalStudentRead,
    PracticalVariant,
    QuizSubmitRequest,
    QuizSubmitResponse,
)

QUIZ_PASS_THRESHOLD_PERCENT: Final[Decimal] = Decimal("70.00")


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

    async def has_passed_quiz(
        self,
        *,
        student_id: uuid.UUID,
        module_id: uuid.UUID,
    ) -> bool:
        """Перевіряє, чи склав студент тест-допуск для вказаного модуля (>= 70%)."""
        module_stmt = (
            select(Module)
            .options(selectinload(Module.quiz_questions))
            .where(Module.id == module_id)
        )
        module_result = await self._db.execute(module_stmt)
        module = module_result.scalar_one_or_none()
        has_questions = True if module is None else len(module.quiz_questions) > 0

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
            raise QuizNotPassedError(
                context={
                    "module_id": str(module_id),
                    "student_id": str(student_id),
                },
            )

    async def submit_quiz(
        self,
        *,
        student: User,
        module_id: uuid.UUID,
        payload: QuizSubmitRequest,
    ) -> QuizSubmitResponse:
        """Оцінює відповіді студента на тест-допуск, зберігає спробу та відкриває практичну."""
        stmt = (
            select(Module)
            .options(selectinload(Module.quiz_questions))
            .where(Module.id == module_id)
        )
        result = await self._db.execute(stmt)
        module = result.scalar_one_or_none()
        if module is None:
            raise DomainError(
                "Навчальний модуль не знайдено.",
                code="MODULE_NOT_FOUND",
                status_code=404,
                context={"module_id": str(module_id)},
            )

        questions = module.quiz_questions
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
            if item.question_id not in questions_by_id:
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
            submitted_answers[item.question_id] = item.selected_option_index

        correct_count = sum(
            1
            for question in questions
            if submitted_answers.get(question.id) == question.correct_option_index
        )

        raw_percent = (Decimal(correct_count) * Decimal("100")) / Decimal(total_questions)
        score_percent = raw_percent.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        passed = score_percent >= QUIZ_PASS_THRESHOLD_PERCENT

        attempt = QuizAttempt(
            student_id=student.id,
            module_id=module.id,
            score_percent=score_percent,
            passed=passed,
        )
        self._db.add(attempt)
        await self._db.commit()
        await self._db.refresh(attempt)

        previously_passed, _ = await self.get_module_quiz_status(
            student_id=student.id,
            module_id=module.id,
            has_questions=True,
        )
        practical_unlocked = passed or previously_passed

        return QuizSubmitResponse(
            id=attempt.id,
            module_id=module.id,
            score_percent=float(attempt.score_percent),
            passed=attempt.passed,
            correct_count=correct_count,
            total_questions=total_questions,
            practical_unlocked=practical_unlocked,
            attempted_at=attempt.attempted_at,
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
    "QUIZ_PASS_THRESHOLD_PERCENT",
    "QuizService",
    "calculate_variant_index",
    "resolve_student_variant",
]
