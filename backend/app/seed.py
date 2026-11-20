import argparse
import asyncio
import json
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import bcrypt
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import AsyncSessionLocal
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
    max_score: Decimal = Field(default=Decimal("10.00"), gt=Decimal("0"))
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


def hash_password(plain_password: str) -> str:
    """Генерує bcrypt-хеш пароля користувача."""
    salt = bcrypt.gensalt(rounds=12)
    hashed: bytes = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


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
                question_text=question.question_text,
                options=list(question.options),
                correct_option_index=question.correct_option_index,
            )
            for question in mod_payload.quiz_questions
        ]
        if mod_payload.practical is not None:
            prac_payload = mod_payload.practical
            validated_rules: list[dict[str, object]] = [
                GradingRule.model_validate(rule).model_dump(mode="json")
                for rule in prac_payload.grading_rules
            ]
            module.practical = Practical(
                title=prac_payload.title,
                instructions=prac_payload.instructions,
                format_type=prac_payload.format_type,
                max_score=prac_payload.max_score.quantize(Decimal("0.01")),
                variants=list(prac_payload.variants),
                grading_rules=validated_rules,
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


async def seed_database(
    session: AsyncSession,
    *,
    sync_courses: bool = False,
    content_dir: Path | None = None,
) -> SeedSummary:
    """Ідемпотентно наповнює БД групою, користувачами та 4 курсами (або синхронізує курси)."""
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

    for course in bundle.courses:
        stmt = select(Course).where(Course.slug == course.slug)
        if sync_courses:
            stmt = stmt.options(
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
            existing_course.title = course.title
            existing_course.description = course.description
            existing_course.modules.clear()
            await session.flush()

            fresh_modules = list(course.modules)
            course.modules.clear()
            for module in fresh_modules:
                module.course = existing_course
                existing_course.modules.append(module)

    await session.commit()
    return summary


async def run_seed(
    *,
    dry_run: bool = False,
    sync_courses: bool = False,
) -> SeedSummary:
    """Запускає ініціалізацію даних у режимі запису/синхронізації БД або --dry-run."""
    if dry_run:
        bundle = build_seed_bundle()
        return summarize_bundle(bundle)

    async with AsyncSessionLocal() as session:
        return await seed_database(session, sync_courses=sync_courses)


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
            "Оновити існуючі курси в БД з актуального JSON (перезаписує модулі, "
            "тести й практичні, зберігаючи користувачів та академічні групи)."
        ),
    )
    args = parser.parse_args(argv)

    summary = asyncio.run(
        run_seed(
            dry_run=bool(args.dry_run),
            sync_courses=bool(args.sync_courses),
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
