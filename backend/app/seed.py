import argparse
import asyncio
import json
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.graders.factory import GraderFactory
from app.models.course import (
    ALLOWED_COURSE_SLUGS,
    MAX_COURSES_COUNT,
    Course,
    CourseSlug,
    Module,
    Practical,
    PracticalFormat,
    QuizQuestion,
)
from app.models.user import (
    MAX_COURSE_YEAR,
    MIN_COURSE_YEAR,
    AcademicGroup,
    User,
    UserRole,
)
from app.schemas.grading import GradingRule
from app.services.retention_service import delete_submission_files_for_paths_async

logger = logging.getLogger(__name__)

_QuizQuestionSignature = tuple[str, tuple[str, ...], int]


class _SeedQuizQuestionPayload(BaseModel):
    """Контракт тестового питання модуля у JSON-файлі навчального курсу."""

    model_config = ConfigDict(extra="forbid")

    question_text: str = Field(..., min_length=1)
    options: list[str] = Field(..., min_length=2)
    correct_option_index: int = Field(..., ge=0)

    @model_validator(mode="after")
    def _validate_correct_option_index(self) -> "_SeedQuizQuestionPayload":
        if self.correct_option_index >= len(self.options):
            raise ValueError(
                f"correct_option_index ({self.correct_option_index}) виходить за межі "
                f"списку варіантів довжини {len(self.options)}."
            )
        return self


class _SeedPracticalPayload(BaseModel):
    """Контракт практичної роботи модуля у JSON-файлі курсу (meta ігнорується)."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=255)
    instructions: str = Field(..., min_length=1)
    format_type: PracticalFormat
    max_score: Decimal = Field(default=Decimal("12.00"), gt=Decimal("0"))
    variants: list[dict[str, object]] = Field(default_factory=list)
    grading_rules: list[GradingRule] = Field(..., min_length=1)
    meta: dict[str, object] | None = Field(default=None, exclude=True)


class _SeedModulePayload(BaseModel):
    """Контракт навчального модуля у JSON-файлі курсу."""

    model_config = ConfigDict(extra="forbid")

    order_index: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=255)
    lecture_content: str = Field(..., min_length=1)
    quiz_questions: list[_SeedQuizQuestionPayload] = Field(default_factory=list)
    practical: _SeedPracticalPayload | None = None


class _SeedCoursePayload(BaseModel):
    """Контракт повного JSON-файлу одного навчального курсу."""

    model_config = ConfigDict(extra="forbid")

    slug: CourseSlug
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    modules: list[_SeedModulePayload] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _validate_unique_module_order_indices(self) -> "_SeedCoursePayload":
        seen_indices: set[int] = set()
        for module in self.modules:
            if module.order_index in seen_indices:
                raise ValueError(
                    f"Курс '{self.slug.value}' містить дубльований "
                    f"order_index={module.order_index}."
                )
            seen_indices.add(module.order_index)
        return self


@dataclass(frozen=True, slots=True)
class SeedSummary:
    """Підсумок виконання скрипта початкового наповнення бази даних."""

    group_code: str
    users_count: int
    courses_count: int
    modules_count: int
    questions_count: int
    practicals_count: int
    variants_count: int = 0


@dataclass(frozen=True, slots=True)
class SeedBundle:
    """Контейнер підготовлених ORM-об'єктів для ідемпотентного збереження в БД."""

    group: AcademicGroup
    admin: User
    teacher: User
    students: list[User]
    courses: list[Course]


def _extract_needs_rules_review(meta: dict[str, object] | None) -> bool:
    """Витягує прапорець needs_manual_rules_review із JSON-блоку practical.meta."""
    if not isinstance(meta, dict):
        return False
    return meta.get("needs_manual_rules_review") is True


def _load_course_from_json(
    course_path: Path,
    *,
    expected_slug: CourseSlug,
    teacher: User,
) -> Course:
    """Завантажує, валідує через Pydantic v2 та конвертує JSON-курс у ORM-граф."""
    if not course_path.is_file():
        raise FileNotFoundError(
            f"Не знайдено JSON-файл курсу '{expected_slug.value}': {course_path}"
        )

    raw_data: object = json.loads(course_path.read_text(encoding="utf-8"))
    payload = _SeedCoursePayload.model_validate(raw_data)

    if payload.slug != expected_slug:
        raise ValueError(
            f"Файл '{course_path.name}' має slug='{payload.slug.value}', "
            f"очікувалося '{expected_slug.value}'."
        )

    course = Course(
        title=payload.title,
        slug=payload.slug,
        description=payload.description,
        teacher=teacher,
    )

    sorted_modules = sorted(payload.modules, key=lambda item: item.order_index)
    for mod_payload in sorted_modules:
        module = Module(
            course=course,
            order_index=mod_payload.order_index,
            title=mod_payload.title,
            lecture_content=mod_payload.lecture_content,
        )
        module.quiz_questions = [
            QuizQuestion(
                order_index=idx,
                question_text=question.question_text,
                options=list(question.options),
                correct_option_index=question.correct_option_index,
            )
            for idx, question in enumerate(mod_payload.quiz_questions, start=1)
        ]
        if mod_payload.practical is not None:
            prac_payload = mod_payload.practical
            grader = GraderFactory.get_grader(prac_payload.format_type)
            validated_rules: list[dict[str, object]] = []
            for rule in prac_payload.grading_rules:
                parsed_rule = GradingRule.model_validate(rule)
                grader.validate_rule_definition(parsed_rule)
                validated_rules.append(parsed_rule.model_dump(mode="json"))
            module.practical = Practical(
                title=prac_payload.title,
                instructions=prac_payload.instructions,
                format_type=prac_payload.format_type,
                max_score=prac_payload.max_score.quantize(Decimal("0.01")),
                variants=list(prac_payload.variants),
                grading_rules=validated_rules,
                needs_rules_review=_extract_needs_rules_review(prac_payload.meta),
            )

    return course


def build_seed_bundle(content_dir: Path | None = None) -> SeedBundle:
    """Конструює повний граф даних із JSON-курсів: групу, викладача, студентів та 4 курси."""
    resolved_content_dir = (
        content_dir if content_dir is not None else settings.COURSE_CONTENT_DIR
    )

    group = AcademicGroup(
        code="КН-31",
        specialty="122 Комп'ютерні науки",
        course_year=3,
    )
    admin = User(
        email="admin@kpefk.lcloud.in.ua",
        password_hash=hash_password("Admin123!"),
        full_name="Адміністратор Системи",
        role=UserRole.ADMIN,
        group=None,
        list_number=None,
    )
    teacher = User(
        email="teacher@kpefk.lcloud.in.ua",
        password_hash=hash_password("Teacher123!"),
        full_name="Коваленко Олександр Петрович",
        role=UserRole.TEACHER,
        group=None,
        list_number=None,
    )
    students: list[User] = [
        User(
            email="student1@kpefk.lcloud.in.ua",
            password_hash=hash_password("Student123!"),
            full_name="Бондаренко Ірина Василівна",
            role=UserRole.STUDENT,
            group=group,
            list_number=1,
        ),
        User(
            email="student2@kpefk.lcloud.in.ua",
            password_hash=hash_password("Student123!"),
            full_name="Мельник Дмитро Сергійович",
            role=UserRole.STUDENT,
            group=group,
            list_number=2,
        ),
        User(
            email="student3@kpefk.lcloud.in.ua",
            password_hash=hash_password("Student123!"),
            full_name="Шевченко Максим Андрійович",
            role=UserRole.STUDENT,
            group=group,
            list_number=3,
        ),
    ]

    courses: list[Course] = [
        _load_course_from_json(
            resolved_content_dir / f"{slug.value}.json",
            expected_slug=slug,
            teacher=teacher,
        )
        for slug in ALLOWED_COURSE_SLUGS
    ]

    if not (MIN_COURSE_YEAR <= group.course_year <= MAX_COURSE_YEAR):
        raise ValueError(
            f"Курс академічної групи має бути в межах {MIN_COURSE_YEAR}..{MAX_COURSE_YEAR}."
        )

    course_slugs = tuple(course.slug for course in courses)
    if len(courses) != MAX_COURSES_COUNT or course_slugs != ALLOWED_COURSE_SLUGS:
        raise ValueError(
            "Набір початкових даних повинен містити виключно 4 дисципліни: "
            "word, excel, access, html."
        )

    return SeedBundle(
        group=group,
        admin=admin,
        teacher=teacher,
        students=students,
        courses=courses,
    )


def summarize_bundle(bundle: SeedBundle) -> SeedSummary:
    """Обчислює кількісні показники підготовленого набору початкових даних."""
    modules_count = sum(len(course.modules) for course in bundle.courses)
    questions_count = sum(
        len(module.quiz_questions)
        for course in bundle.courses
        for module in course.modules
    )
    practicals_count = sum(
        1
        for course in bundle.courses
        for module in course.modules
        if module.practical is not None
    )
    variants_count = sum(
        len(module.practical.variants)
        for course in bundle.courses
        for module in course.modules
        if module.practical is not None
    )
    return SeedSummary(
        group_code=bundle.group.code,
        users_count=2 + len(bundle.students),
        courses_count=len(bundle.courses),
        modules_count=modules_count,
        questions_count=questions_count,
        practicals_count=practicals_count,
        variants_count=variants_count,
    )


def _question_signature(question: QuizQuestion) -> _QuizQuestionSignature:
    """Повертає нормалізовану сигнатуру питання тесту для порівняння змін."""
    return (
        question.question_text,
        tuple(question.options),
        question.correct_option_index,
    )


def _sync_quiz_questions_in_place(
    existing_module: Module,
    incoming_questions: Sequence[QuizQuestion],
) -> None:
    """Оновлює питання тесту модуля без перестворення ідентичних записів і втрати QuizAttempt."""
    existing_questions = sorted(
        existing_module.quiz_questions,
        key=lambda item: (item.order_index, str(item.id)),
    )
    existing_by_sig: dict[_QuizQuestionSignature, list[QuizQuestion]] = {}
    for question in existing_questions:
        existing_by_sig.setdefault(_question_signature(question), []).append(question)

    matched_existing_obj_ids: set[int] = set()
    unmatched_incoming: list[tuple[int, QuizQuestion]] = []
    for idx, incoming in enumerate(incoming_questions, start=1):
        bucket = existing_by_sig.get(_question_signature(incoming))
        if bucket:
            kept = bucket.pop(0)
            matched_existing_obj_ids.add(id(kept))
            if kept.order_index != idx:
                kept.order_index = idx
        else:
            unmatched_incoming.append((idx, incoming))

    unmatched_existing = [
        question
        for question in existing_questions
        if id(question) not in matched_existing_obj_ids
    ]
    if not unmatched_incoming and not unmatched_existing:
        return

    for target, (target_order_index, source) in zip(
        unmatched_existing,
        unmatched_incoming,
        strict=False,
    ):
        target.order_index = target_order_index
        target.question_text = source.question_text
        target.options = list(source.options)
        target.correct_option_index = source.correct_option_index

    if len(unmatched_incoming) > len(unmatched_existing):
        for target_order_index, source in unmatched_incoming[
            len(unmatched_existing) :
        ]:
            existing_module.quiz_questions.append(
                QuizQuestion(
                    order_index=target_order_index,
                    question_text=source.question_text,
                    options=list(source.options),
                    correct_option_index=source.correct_option_index,
                )
            )
    elif len(unmatched_existing) > len(unmatched_incoming):
        for surplus in unmatched_existing[len(unmatched_incoming) :]:
            existing_module.quiz_questions.remove(surplus)


async def _sync_practical_in_place(
    session: AsyncSession,
    *,
    course_slug: CourseSlug,
    existing_module: Module,
    incoming_practical: Practical | None,
    allow_destructive_module_delete: bool,
    submission_file_paths_to_delete: list[str],
) -> None:
    """Неруйнівно синхронізує практичну роботу модуля зі збереженням Practical.id та Submission."""
    existing_practical = existing_module.practical

    if incoming_practical is not None:
        if existing_practical is None:
            existing_module.practical = Practical(
                title=incoming_practical.title,
                instructions=incoming_practical.instructions,
                format_type=incoming_practical.format_type,
                max_score=incoming_practical.max_score,
                variants=list(incoming_practical.variants),
                grading_rules=list(incoming_practical.grading_rules),
                needs_rules_review=incoming_practical.needs_rules_review,
            )
        else:
            existing_practical.title = incoming_practical.title
            existing_practical.instructions = incoming_practical.instructions
            existing_practical.format_type = incoming_practical.format_type
            existing_practical.max_score = incoming_practical.max_score
            existing_practical.variants = list(incoming_practical.variants)
            existing_practical.grading_rules = list(incoming_practical.grading_rules)
            existing_practical.needs_rules_review = incoming_practical.needs_rules_review
        return

    if existing_practical is None:
        return

    submissions = list(existing_practical.submissions)
    if submissions and not allow_destructive_module_delete:
        logger.warning(
            "Пропущено видалення практичної роботи '%s' (курс='%s', модуль=%d): "
            "знайдено %d здач студентів. Для примусового видалення передайте "
            "--allow-destructive-module-delete.",
            existing_practical.title,
            course_slug.value,
            existing_module.order_index,
            len(submissions),
        )
        return

    for submission in submissions:
        if submission.file_path is not None and submission.file_path.strip():
            submission_file_paths_to_delete.append(submission.file_path)

    existing_module.practical = None
    await session.delete(existing_practical)


async def _sync_course_in_place(
    session: AsyncSession,
    *,
    existing_course: Course,
    incoming_course: Course,
    allow_destructive_module_delete: bool,
    submission_file_paths_to_delete: list[str],
) -> None:
    """Неруйнівно оновлює курс, модулі, тести й практичні in-place за (course_id, order_index)."""
    existing_course.title = incoming_course.title
    existing_course.description = incoming_course.description

    existing_modules_by_order: dict[int, Module] = {}
    duplicate_existing_modules: list[Module] = []
    for existing_mod in sorted(
        existing_course.modules,
        key=lambda mod: (mod.order_index, str(mod.id)),
    ):
        if existing_mod.order_index not in existing_modules_by_order:
            existing_modules_by_order[existing_mod.order_index] = existing_mod
        else:
            duplicate_existing_modules.append(existing_mod)

    incoming_modules = sorted(
        incoming_course.modules,
        key=lambda mod: mod.order_index,
    )
    incoming_order_indices: set[int] = set()

    for incoming_mod in incoming_modules:
        incoming_order_indices.add(incoming_mod.order_index)
        matched_mod = existing_modules_by_order.get(incoming_mod.order_index)
        if matched_mod is None:
            new_module = Module(
                order_index=incoming_mod.order_index,
                title=incoming_mod.title,
                lecture_content=incoming_mod.lecture_content,
            )
            new_module.quiz_questions = [
                QuizQuestion(
                    order_index=question.order_index if question.order_index > 0 else idx,
                    question_text=question.question_text,
                    options=list(question.options),
                    correct_option_index=question.correct_option_index,
                )
                for idx, question in enumerate(incoming_mod.quiz_questions, start=1)
            ]
            if incoming_mod.practical is not None:
                new_module.practical = Practical(
                    title=incoming_mod.practical.title,
                    instructions=incoming_mod.practical.instructions,
                    format_type=incoming_mod.practical.format_type,
                    max_score=incoming_mod.practical.max_score,
                    variants=list(incoming_mod.practical.variants),
                    grading_rules=list(incoming_mod.practical.grading_rules),
                    needs_rules_review=incoming_mod.practical.needs_rules_review,
                )
            existing_course.modules.append(new_module)
            continue

        matched_mod.title = incoming_mod.title
        matched_mod.lecture_content = incoming_mod.lecture_content
        _sync_quiz_questions_in_place(matched_mod, incoming_mod.quiz_questions)
        await _sync_practical_in_place(
            session,
            course_slug=existing_course.slug,
            existing_module=matched_mod,
            incoming_practical=incoming_mod.practical,
            allow_destructive_module_delete=allow_destructive_module_delete,
            submission_file_paths_to_delete=submission_file_paths_to_delete,
        )

    extra_modules: list[Module] = [
        mod
        for order_idx, mod in existing_modules_by_order.items()
        if order_idx not in incoming_order_indices
    ]
    extra_modules.extend(duplicate_existing_modules)

    for extra_mod in extra_modules:
        quiz_attempts_count = len(extra_mod.quiz_attempts)
        submissions = (
            list(extra_mod.practical.submissions)
            if extra_mod.practical is not None
            else []
        )
        submissions_count = len(submissions)
        if (
            quiz_attempts_count > 0 or submissions_count > 0
        ) and not allow_destructive_module_delete:
            logger.warning(
                "Пропущено видалення зайвого модуля order_index=%d ('%s') курсу '%s': "
                "знайдено прогрес студентів (quiz_attempts=%d, submissions=%d). "
                "Для примусового видалення передайте --allow-destructive-module-delete.",
                extra_mod.order_index,
                extra_mod.title,
                existing_course.slug.value,
                quiz_attempts_count,
                submissions_count,
            )
            continue

        for submission in submissions:
            if submission.file_path is not None and submission.file_path.strip():
                submission_file_paths_to_delete.append(submission.file_path)

        if extra_mod in existing_course.modules:
            existing_course.modules.remove(extra_mod)
        await session.delete(extra_mod)


async def seed_database(
    session: AsyncSession,
    *,
    sync_courses: bool = False,
    allow_destructive_module_delete: bool = False,
    content_dir: Path | None = None,
    upload_dir: Path | None = None,
) -> SeedSummary:
    """Ідемпотентно наповнює БД групою, користувачами та 4 курсами (або неруйнівно синхронізує)."""
    bundle = build_seed_bundle(content_dir=content_dir)
    summary = summarize_bundle(bundle)

    existing_group_result = await session.execute(
        select(AcademicGroup).where(AcademicGroup.code == bundle.group.code)
    )
    group = existing_group_result.scalar_one_or_none()
    if group is None:
        group = bundle.group
        session.add(group)
        await session.flush()

    all_seed_users: list[User] = [bundle.admin, bundle.teacher, *bundle.students]
    persisted_teacher: User | None = None

    for candidate in all_seed_users:
        user_result = await session.execute(select(User).where(User.email == candidate.email))
        existing_user = user_result.scalar_one_or_none()
        if existing_user is None:
            if candidate.role == UserRole.STUDENT:
                candidate.group = group
            session.add(candidate)
            await session.flush()
            target_user = candidate
        else:
            target_user = existing_user

        if target_user.role == UserRole.TEACHER:
            persisted_teacher = target_user

    if persisted_teacher is None:
        raise RuntimeError("Не вдалося створити або знайти обліковий запис викладача.")

    submission_file_paths_to_delete: list[str] = []

    for course in bundle.courses:
        stmt = select(Course).where(Course.slug == course.slug)
        if sync_courses:
            stmt = stmt.execution_options(populate_existing=True).options(
                selectinload(Course.modules).selectinload(Module.quiz_questions),
                selectinload(Course.modules)
                .selectinload(Module.practical)
                .selectinload(Practical.submissions),
                selectinload(Course.modules).selectinload(Module.quiz_attempts),
            )
        course_result = await session.execute(stmt)
        existing_course = course_result.scalar_one_or_none()

        if existing_course is None:
            course.teacher = persisted_teacher
            session.add(course)
        elif sync_courses:
            await _sync_course_in_place(
                session,
                existing_course=existing_course,
                incoming_course=course,
                allow_destructive_module_delete=allow_destructive_module_delete,
                submission_file_paths_to_delete=submission_file_paths_to_delete,
            )

    await session.commit()

    if submission_file_paths_to_delete:
        effective_upload_dir = (
            upload_dir if upload_dir is not None else settings.UPLOADS_DIR
        )
        await delete_submission_files_for_paths_async(
            submission_file_paths_to_delete,
            upload_dir=effective_upload_dir,
        )

    return summary


async def run_seed(
    *,
    dry_run: bool = False,
    sync_courses: bool = False,
    allow_destructive_module_delete: bool = False,
) -> SeedSummary:
    """Запускає ініціалізацію даних у режимі запису/синхронізації БД або --dry-run."""
    if dry_run:
        bundle = build_seed_bundle()
        return summarize_bundle(bundle)

    async with AsyncSessionLocal() as session:
        return await seed_database(
            session,
            sync_courses=sync_courses,
            allow_destructive_module_delete=allow_destructive_module_delete,
        )


def main(argv: Sequence[str] | None = None) -> int:
    """CLI-точка входу для запуску наповнення бази даних (`python -m app.seed`)."""
    parser = argparse.ArgumentParser(
        description="Наповнення БД Edu Auto Grader курсами з JSON та початковими користувачами."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Перевірити побудову ORM-об'єктів без підключення до PostgreSQL.",
    )
    parser.add_argument(
        "--sync-courses",
        action="store_true",
        help=(
            "Неруйнівно синхронізувати існуючі курси в БД з актуального JSON "
            "(оновлює модулі, тести й практичні in-place зі збереженням користувачів, "
            "груп, спроб тестів та здач з оцінками студентів)."
        ),
    )
    parser.add_argument(
        "--allow-destructive-module-delete",
        action="store_true",
        help=(
            "Дозволити разом із --sync-courses видаляти зайві модулі або практичні, "
            "вилучені з JSON, навіть якщо за ними є спроби тестів чи здачі студентів "
            "(із безпечним очищенням пов'язаних файлів у uploads/)."
        ),
    )
    args = parser.parse_args(argv)

    summary = asyncio.run(
        run_seed(
            dry_run=bool(args.dry_run),
            sync_courses=bool(args.sync_courses),
            allow_destructive_module_delete=bool(args.allow_destructive_module_delete),
        )
    )
    if args.dry_run:
        mode_label = "DRY-RUN"
    elif args.sync_courses:
        mode_label = "SYNCED"
    else:
        mode_label = "APPLIED"
    print(
        f"[seed:{mode_label}] group={summary.group_code} "
        f"users={summary.users_count} courses={summary.courses_count} "
        f"modules={summary.modules_count} questions={summary.questions_count} "
        f"practicals={summary.practicals_count} variants={summary.variants_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
