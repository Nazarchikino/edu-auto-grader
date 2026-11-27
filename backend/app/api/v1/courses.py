import uuid
from collections.abc import Sequence
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.concurrency import run_in_threadpool

from app.api.deps import (
    ensure_course_owner_or_admin,
    get_current_user,
    get_db,
    require_role,
)
from app.core.config import settings
from app.core.exceptions import DomainError
from app.core.upload_utils import read_upload_file_limited
from app.models.course import (
    ALLOWED_COURSE_SLUGS,
    MAX_COURSES_COUNT,
    Course,
    Module,
    Practical,
    QuizQuestion,
)
from app.models.progress import QuizAttempt, Submission
from app.models.user import User, UserRole
from app.schemas.course import (
    CourseCreate,
    CourseMediaUploadRead,
    CourseRead,
    CourseUpdate,
    ModuleCreate,
    ModuleDetailRead,
    ModuleReorderRequest,
    ModuleSummaryRead,
    ModuleUpdate,
    PracticalCreate,
    PracticalStudentRead,
    PracticalSummaryRead,
    PracticalTeacherRead,
    PracticalUpdate,
    PracticalVariant,
    QuizQuestionCreate,
    QuizQuestionRead,
    QuizQuestionTeacherRead,
    QuizQuestionUpdate,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from app.schemas.grading import GradingRule
from app.services.quiz_service import (
    QuizService,
    build_student_grading_criteria,
    resolve_student_variant,
)
from app.services.retention_service import delete_submission_files_for_paths_async

router = APIRouter(tags=["courses"])

TeacherOrAdminUser = Annotated[
    User,
    Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
]
StudentUser = Annotated[
    User,
    Depends(require_role(UserRole.STUDENT)),
]

ALLOWED_COURSE_MEDIA_EXTENSIONS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".webp", ".gif"}
)


def _matches_raster_image_magic_bytes(suffix: str, file_bytes: bytes) -> bool:
    """Перевіряє реальну сигнатуру (magic bytes) растрового зображення."""
    if suffix == ".png":
        return file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in {".jpg", ".jpeg"}:
        return file_bytes.startswith(b"\xff\xd8\xff")
    if suffix == ".gif":
        return file_bytes.startswith((b"GIF87a", b"GIF89a"))
    if suffix == ".webp":
        return (
            len(file_bytes) >= 12
            and file_bytes[:4] == b"RIFF"
            and file_bytes[8:12] == b"WEBP"
        )
    return False


def _save_course_media_file(
    *,
    media_dir: Path,
    course_slug: str,
    ext_no_dot: str,
    file_bytes: bytes,
) -> tuple[str, Path]:
    """Безпечно записує ілюстрацію у `COURSE_MEDIA_DIR/<slug>/uploads/` (для threadpool)."""
    media_root = media_dir.resolve()
    target_dir = (media_root / course_slug / "uploads").resolve()
    if target_dir == media_root or not target_dir.is_relative_to(media_root):
        raise DomainError(
            "Небезпечний шлях каталогу медіафайлів курсу.",
            code="UNSAFE_MEDIA_PATH",
            status_code=422,
        )

    filename = f"{uuid.uuid4().hex}.{ext_no_dot}"
    saved_path = (target_dir / filename).resolve()
    if saved_path.parent != target_dir or not saved_path.is_relative_to(media_root):
        raise DomainError(
            "Небезпечний шлях файлу ілюстрації.",
            code="UNSAFE_MEDIA_PATH",
            status_code=422,
        )

    target_dir.mkdir(parents=True, exist_ok=True)
    saved_path.write_bytes(file_bytes)
    return filename, saved_path


async def _fetch_user_progress_maps(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> tuple[dict[uuid.UUID, bool], dict[uuid.UUID, float], dict[uuid.UUID, float]]:
    """Завантажує агреговані результати тестів та практичних робіт користувача."""
    quiz_stmt = (
        select(
            QuizAttempt.module_id,
            func.max(case((QuizAttempt.passed.is_(True), 1), else_=0)),
            func.max(QuizAttempt.score_percent),
        )
        .where(QuizAttempt.student_id == user_id)
        .group_by(QuizAttempt.module_id)
    )
    quiz_result = await db.execute(quiz_stmt)

    passed_by_module: dict[uuid.UUID, bool] = {}
    best_quiz_by_module: dict[uuid.UUID, float] = {}
    for row in quiz_result.all():
        module_id: uuid.UUID = row[0]
        passed_flag: int | None = row[1]
        max_quiz_score: Decimal | None = row[2]
        passed_by_module[module_id] = bool(passed_flag)
        if max_quiz_score is not None:
            best_quiz_by_module[module_id] = float(max_quiz_score)

    sub_stmt = (
        select(
            Submission.practical_id,
            func.max(Submission.final_score),
        )
        .where(Submission.student_id == user_id)
        .group_by(Submission.practical_id)
    )
    sub_result = await db.execute(sub_stmt)

    best_practical_by_id: dict[uuid.UUID, float] = {}
    for row in sub_result.all():
        practical_id: uuid.UUID = row[0]
        max_sub_score: Decimal | None = row[1]
        if max_sub_score is not None:
            best_practical_by_id[practical_id] = round(float(max_sub_score), 2)

    return passed_by_module, best_quiz_by_module, best_practical_by_id


def _serialize_course(
    course: Course,
    *,
    passed_by_module: dict[uuid.UUID, bool],
    best_quiz_by_module: dict[uuid.UUID, float],
    best_practical_by_id: dict[uuid.UUID, float],
) -> CourseRead:
    """Формує CourseRead із розрахунком прогресу по модулях курсу."""
    ordered_modules = sorted(course.modules, key=lambda item: item.order_index)
    module_summaries: list[ModuleSummaryRead] = []
    completed_modules = 0

    for module in ordered_modules:
        has_questions = len(module.quiz_questions) > 0
        quiz_passed = (
            passed_by_module.get(module.id, False) if has_questions else True
        )
        best_quiz_score = best_quiz_by_module.get(module.id)

        practical = module.practical
        practical_id = practical.id if practical is not None else None
        practical_format = practical.format_type if practical is not None else None
        practical_score = (
            best_practical_by_id.get(practical.id) if practical is not None else None
        )
        practical_max_score = (
            float(practical.max_score) if practical is not None else None
        )
        practical_needs_rules_review = (
            practical.needs_rules_review if practical is not None else False
        )

        if quiz_passed and (practical_id is None or practical_score is not None):
            completed_modules += 1

        module_summaries.append(
            ModuleSummaryRead(
                id=module.id,
                course_id=course.id,
                order_index=module.order_index,
                title=module.title,
                quiz_passed=quiz_passed,
                best_quiz_score=best_quiz_score,
                practical_id=practical_id,
                practical_format=practical_format,
                practical_score=practical_score,
                practical_max_score=practical_max_score,
                practical_needs_rules_review=practical_needs_rules_review,
            )
        )

    total_modules = len(module_summaries)
    progress_percent = (
        round((completed_modules / total_modules) * 100.0, 2)
        if total_modules > 0
        else 0.0
    )

    return CourseRead(
        id=course.id,
        title=course.title,
        slug=course.slug,
        description=course.description,
        teacher_id=course.teacher_id,
        total_modules=total_modules,
        completed_modules=completed_modules,
        progress_percent=progress_percent,
        modules=module_summaries,
    )


async def _load_course_or_404(
    db: AsyncSession,
    course_id: uuid.UUID,
) -> Course:
    """Завантажує курс разом із модулями, тестами та практичними або кидає 404."""
    stmt = (
        select(Course)
        .options(
            selectinload(Course.modules).selectinload(Module.quiz_questions),
            selectinload(Course.modules).selectinload(Module.practical),
        )
        .where(Course.id == course_id)
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if course is None:
        raise DomainError(
            "Навчальний курс не знайдено.",
            code="COURSE_NOT_FOUND",
            status_code=404,
            context={"course_id": str(course_id)},
        )
    return course


async def _load_module_or_404(
    db: AsyncSession,
    module_id: uuid.UUID,
) -> Module:
    """Завантажує модуль разом із курсом, питаннями тесту та практичною або кидає 404."""
    stmt = (
        select(Module)
        .options(
            selectinload(Module.course),
            selectinload(Module.quiz_questions),
            selectinload(Module.practical),
        )
        .where(Module.id == module_id)
    )
    result = await db.execute(stmt)
    module = result.scalar_one_or_none()
    if module is None:
        raise DomainError(
            "Навчальний модуль не знайдено.",
            code="MODULE_NOT_FOUND",
            status_code=404,
            context={"module_id": str(module_id)},
        )
    return module


async def _ensure_module_order_index_unique(
    db: AsyncSession,
    course_id: uuid.UUID,
    order_index: int,
    *,
    exclude_module_id: uuid.UUID | None = None,
) -> None:
    """Перевіряє унікальність порядкового номера модуля в межах навчального курсу."""
    stmt = select(Module.id).where(
        Module.course_id == course_id,
        Module.order_index == order_index,
    )
    if exclude_module_id is not None:
        stmt = stmt.where(Module.id != exclude_module_id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise DomainError(
            f"У цьому курсі модуль із порядковим номером {order_index} уже існує.",
            code="MODULE_ORDER_INDEX_EXISTS",
            status_code=409,
            context={
                "course_id": str(course_id),
                "order_index": order_index,
            },
        )


async def _build_module_detail_read(
    db: AsyncSession,
    module: Module,
    current_user: User,
    *,
    preview_variant: int | None = None,
) -> ModuleDetailRead:
    """Формує детальне представлення модуля з лекцією, тестом та статусом практичної."""
    questions_stmt = (
        select(QuizQuestion)
        .where(QuizQuestion.module_id == module.id)
        .order_by(QuizQuestion.order_index.asc(), QuizQuestion.id.asc())
    )
    questions_result = await db.execute(questions_stmt)
    ordered_questions = list(questions_result.scalars().all())

    is_teacher_preview = current_user.role in (UserRole.TEACHER, UserRole.ADMIN)
    has_questions = len(ordered_questions) > 0

    if is_teacher_preview:
        quiz_passed = True
        best_quiz_score: float | None = None
        quiz_cooldown_remaining_seconds = 0
        practical_unlocked = True
    else:
        quiz_service = QuizService(db)
        quiz_passed, best_quiz_score = await quiz_service.get_module_quiz_status(
            student_id=current_user.id,
            module_id=module.id,
            has_questions=has_questions,
        )
        quiz_cooldown_remaining_seconds = 0
        if has_questions and not quiz_passed:
            quiz_cooldown_remaining_seconds = (
                await quiz_service.get_quiz_cooldown_remaining_seconds(
                    student_id=current_user.id,
                    module_id=module.id,
                    quiz_passed=quiz_passed,
                )
            )
        practical_unlocked = quiz_passed

    practical_summary: PracticalSummaryRead | None = None
    if module.practical is not None:
        max_sub_score: Decimal | None = None
        if not is_teacher_preview:
            best_sub_stmt = select(func.max(Submission.final_score)).where(
                Submission.student_id == current_user.id,
                Submission.practical_id == module.practical.id,
            )
            best_sub_result = await db.execute(best_sub_stmt)
            max_sub_score = best_sub_result.scalar_one_or_none()

        total_variants = max(1, len(module.practical.variants))
        if is_teacher_preview:
            clamped_variant = max(1, min(preview_variant or 1, total_variants))
            _, assigned_variant_number, resolved_variant = resolve_student_variant(
                practical=module.practical,
                list_number=clamped_variant,
            )
        else:
            _, assigned_variant_number, resolved_variant = resolve_student_variant(
                practical=module.practical,
                list_number=current_user.list_number,
            )

        practical_summary = PracticalSummaryRead(
            id=module.practical.id,
            module_id=module.id,
            title=module.practical.title,
            instructions=(
                module.practical.instructions if practical_unlocked else None
            ),
            format_type=module.practical.format_type,
            max_score=float(module.practical.max_score),
            is_unlocked=practical_unlocked,
            best_score=(
                round(float(max_sub_score), 2) if max_sub_score is not None else None
            ),
            needs_rules_review=module.practical.needs_rules_review,
            has_template_file=bool(module.practical.template_file_path),
            template_file_name=(
                module.practical.template_file_name
                if module.practical.template_file_path
                else None
            ),
            assigned_variant_number=assigned_variant_number,
            total_variants=total_variants,
            variant=resolved_variant if practical_unlocked else None,
            grading_criteria=build_student_grading_criteria(
                module.practical,
                resolved_variant,
            ),
        )

    quiz_questions_read = [
        QuizQuestionRead(
            id=question.id,
            module_id=question.module_id,
            question_text=question.question_text,
            options=list(question.options),
        )
        for question in ordered_questions
    ]

    return ModuleDetailRead(
        id=module.id,
        course_id=module.course_id,
        order_index=module.order_index,
        title=module.title,
        lecture_content=module.lecture_content,
        quiz_questions=quiz_questions_read,
        quiz_passed=quiz_passed,
        best_quiz_score=best_quiz_score,
        quiz_cooldown_remaining_seconds=quiz_cooldown_remaining_seconds,
        practical_unlocked=practical_unlocked,
        practical=practical_summary,
    )


async def _collect_practical_submission_file_paths(
    db: AsyncSession,
    practical_id: uuid.UUID,
) -> list[str]:
    """Збирає всі непорожні шляхи фізичних файлів здач практичної роботи."""
    paths_result = await db.execute(
        select(Submission.file_path).where(
            Submission.practical_id == practical_id,
            Submission.file_path.is_not(None),
        )
    )
    return [
        file_path
        for file_path in paths_result.scalars().all()
        if file_path is not None and file_path.strip()
    ]


def _serialize_practical_teacher(practical: Practical) -> PracticalTeacherRead:
    """Перетворює ORM-модель Practical у повну схему PracticalTeacherRead для викладача."""
    variants = [
        PracticalVariant.model_validate(item) for item in practical.variants
    ]
    grading_rules = [
        GradingRule.model_validate(item) for item in practical.grading_rules
    ]
    return PracticalTeacherRead(
        id=practical.id,
        module_id=practical.module_id,
        title=practical.title,
        instructions=practical.instructions,
        format_type=practical.format_type,
        max_score=float(practical.max_score),
        needs_rules_review=practical.needs_rules_review,
        has_template_file=bool(practical.template_file_path),
        template_file_name=(
            practical.template_file_name if practical.template_file_path else None
        ),
        variants=variants,
        grading_rules=grading_rules,
    )


@router.get("/courses", response_model=list[CourseRead])
async def list_courses(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CourseRead]:
    """Повертає перелік 4 навчальних курсів із прогресом поточного користувача."""
    stmt = (
        select(Course)
        .where(Course.slug.in_(ALLOWED_COURSE_SLUGS))
        .options(
            selectinload(Course.modules).selectinload(Module.quiz_questions),
            selectinload(Course.modules).selectinload(Module.practical),
        )
        .order_by(Course.slug)
    )
    result = await db.execute(stmt)
    courses: Sequence[Course] = result.scalars().all()

    passed_by_module, best_quiz_by_module, best_practical_by_id = (
        await _fetch_user_progress_maps(db, current_user.id)
    )

    return [
        _serialize_course(
            course,
            passed_by_module=passed_by_module,
            best_quiz_by_module=best_quiz_by_module,
            best_practical_by_id=best_practical_by_id,
        )
        for course in courses
    ]


@router.get("/courses/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CourseRead:
    """Повертає детальну інформацію про курс та список його модулів із прогресом."""
    course = await _load_course_or_404(db, course_id)
    passed_by_module, best_quiz_by_module, best_practical_by_id = (
        await _fetch_user_progress_maps(db, current_user.id)
    )
    return _serialize_course(
        course,
        passed_by_module=passed_by_module,
        best_quiz_by_module=best_quiz_by_module,
        best_practical_by_id=best_practical_by_id,
    )


@router.post(
    "/courses",
    response_model=CourseRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_course(
    payload: CourseCreate,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CourseRead:
    """Створює новий навчальний курс у межах 4 фіксованих дисциплін."""
    existing_stmt = select(Course).where(Course.slug == payload.slug)
    existing_result = await db.execute(existing_stmt)
    if existing_result.scalar_one_or_none() is not None:
        raise DomainError(
            "Курс із таким ідентифікатором дисципліни вже існує.",
            code="COURSE_SLUG_EXISTS",
            status_code=409,
            context={"slug": payload.slug.value},
        )

    total_courses_result = await db.execute(select(func.count(Course.id)))
    total_courses_count = int(total_courses_result.scalar_one())
    if total_courses_count >= MAX_COURSES_COUNT:
        raise DomainError(
            f"У системі дозволено не більше {MAX_COURSES_COUNT} навчальних курсів.",
            code="MAX_COURSES_LIMIT_REACHED",
            status_code=409,
            context={"max_courses": MAX_COURSES_COUNT},
        )

    course = Course(
        title=payload.title,
        slug=payload.slug,
        description=payload.description,
        teacher_id=current_user.id,
    )
    db.add(course)
    await db.commit()

    loaded_course = await _load_course_or_404(db, course.id)
    return _serialize_course(
        loaded_course,
        passed_by_module={},
        best_quiz_by_module={},
        best_practical_by_id={},
    )


@router.patch("/courses/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdate,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CourseRead:
    """Оновлює назву, опис або (лише для адміністратора) викладача навчального курсу."""
    course = await _load_course_or_404(db, course_id)
    ensure_course_owner_or_admin(course, current_user)

    if payload.teacher_id is not None and payload.teacher_id != course.teacher_id:
        if current_user.role != UserRole.ADMIN:
            raise DomainError(
                "Змінювати викладача курсу має право лише адміністратор.",
                code="FORBIDDEN_COURSE_TEACHER_CHANGE",
                status_code=403,
                context={
                    "course_id": str(course.id),
                    "requested_teacher_id": str(payload.teacher_id),
                },
            )
        teacher_result = await db.execute(
            select(User).where(User.id == payload.teacher_id)
        )
        new_teacher = teacher_result.scalar_one_or_none()
        if new_teacher is None:
            raise DomainError(
                "Обраного викладача не знайдено.",
                code="USER_NOT_FOUND",
                status_code=404,
                context={"teacher_id": str(payload.teacher_id)},
            )
        if new_teacher.role not in (UserRole.TEACHER, UserRole.ADMIN):
            raise DomainError(
                "Закріпити курс можна лише за викладачем або адміністратором.",
                code="INVALID_COURSE_TEACHER",
                status_code=422,
                context={
                    "teacher_id": str(payload.teacher_id),
                    "role": new_teacher.role.value,
                },
            )
        course.teacher_id = new_teacher.id

    if payload.title is not None:
        course.title = payload.title
    if payload.description is not None:
        course.description = payload.description

    await db.commit()
    refreshed_course = await _load_course_or_404(db, course.id)
    passed_by_module, best_quiz_by_module, best_practical_by_id = (
        await _fetch_user_progress_maps(db, current_user.id)
    )
    return _serialize_course(
        refreshed_course,
        passed_by_module=passed_by_module,
        best_quiz_by_module=best_quiz_by_module,
        best_practical_by_id=best_practical_by_id,
    )


@router.get("/modules/{module_id}", response_model=ModuleDetailRead)
async def get_module(
    module_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    preview_variant: Annotated[int | None, Query(ge=1)] = None,
) -> ModuleDetailRead:
    """Повертає текст лекції, питання тесту-допуску та статус доступу до практичної."""
    module = await _load_module_or_404(db, module_id)
    if current_user.role in (UserRole.TEACHER, UserRole.ADMIN):
        ensure_course_owner_or_admin(
            module.course,
            current_user,
            context={"module_id": str(module_id)},
        )
    effective_preview_variant = (
        preview_variant
        if current_user.role in (UserRole.TEACHER, UserRole.ADMIN)
        else None
    )
    return await _build_module_detail_read(
        db,
        module,
        current_user,
        preview_variant=effective_preview_variant,
    )


@router.post(
    "/courses/{course_id}/modules",
    response_model=ModuleDetailRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_module(
    course_id: uuid.UUID,
    payload: ModuleCreate,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ModuleDetailRead:
    """Створює новий навчальний модуль з лекцією в межах курсу."""
    course = await _load_course_or_404(db, course_id)
    ensure_course_owner_or_admin(course, current_user)
    await _ensure_module_order_index_unique(db, course_id, payload.order_index)

    module = Module(
        course_id=course_id,
        order_index=payload.order_index,
        title=payload.title,
        lecture_content=payload.lecture_content,
    )
    db.add(module)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DomainError(
            f"У цьому курсі модуль із порядковим номером {payload.order_index} уже існує.",
            code="MODULE_ORDER_INDEX_EXISTS",
            status_code=409,
            context={
                "course_id": str(course_id),
                "order_index": payload.order_index,
            },
        ) from exc

    loaded_module = await _load_module_or_404(db, module.id)
    return await _build_module_detail_read(db, loaded_module, current_user)


@router.put(
    "/courses/{course_id}/modules/reorder",
    response_model=list[ModuleSummaryRead],
)
async def reorder_course_modules(
    course_id: uuid.UUID,
    payload: ModuleReorderRequest,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ModuleSummaryRead]:
    """Змінює порядок модулів курсу у 2 кроки в одній транзакції без конфлікту унікальності."""
    course = await _load_course_or_404(db, course_id)
    ensure_course_owner_or_admin(course, current_user)

    modules_by_id: dict[uuid.UUID, Module] = {
        module.id: module for module in course.modules
    }
    if len(payload.module_ids) != len(set(payload.module_ids)):
        raise DomainError(
            "Список module_ids містить дублікати ідентифікаторів модулів.",
            code="DUPLICATE_MODULE_IDS",
            status_code=422,
            context={"course_id": str(course_id)},
        )

    if set(payload.module_ids) != set(modules_by_id.keys()):
        raise DomainError(
            "Список module_ids має містити рівно всі модулі цього курсу "
            "без пропусків і сторонніх ідентифікаторів.",
            code="INVALID_MODULE_REORDER_SET",
            status_code=422,
            context={
                "course_id": str(course_id),
                "expected_count": len(modules_by_id),
                "received_count": len(payload.module_ids),
            },
        )

    if payload.module_ids:
        for idx, mod_id in enumerate(payload.module_ids):
            modules_by_id[mod_id].order_index = -(idx + 1)
        await db.flush()

        for idx, mod_id in enumerate(payload.module_ids, start=1):
            modules_by_id[mod_id].order_index = idx
        await db.flush()

        await db.commit()

    refreshed_course = await _load_course_or_404(db, course_id)
    passed_by_module, best_quiz_by_module, best_practical_by_id = (
        await _fetch_user_progress_maps(db, current_user.id)
    )
    serialized = _serialize_course(
        refreshed_course,
        passed_by_module=passed_by_module,
        best_quiz_by_module=best_quiz_by_module,
        best_practical_by_id=best_practical_by_id,
    )
    return serialized.modules


@router.post(
    "/courses/{course_id}/media",
    response_model=CourseMediaUploadRead,
    status_code=status.HTTP_200_OK,
)
async def upload_course_media(
    course_id: uuid.UUID,
    file: Annotated[UploadFile, File(...)],
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CourseMediaUploadRead:
    """Безпечно завантажує растрову ілюстрацію лекції (PNG/JPEG/WebP/GIF, до 5 МБ)."""
    course = await _load_course_or_404(db, course_id)
    ensure_course_owner_or_admin(course, current_user)

    safe_filename = (file.filename or "").strip()
    actual_suffix = Path(safe_filename).suffix.lower()
    if actual_suffix not in ALLOWED_COURSE_MEDIA_EXTENSIONS:
        raise DomainError(
            f"Непідтримуваний формат зображення '{actual_suffix or 'невідомий'}'. "
            "Дозволено лише растрові формати: .png, .jpg, .jpeg, .webp, .gif "
            "(SVG/HTML/XML/JS заборонено з міркувань безпеки).",
            code="UNSUPPORTED_MEDIA_FORMAT",
            status_code=422,
            context={
                "course_id": str(course_id),
                "file_name": safe_filename,
                "actual_suffix": actual_suffix,
            },
        )

    file_bytes = await read_upload_file_limited(
        file,
        max_bytes=settings.MAX_COURSE_MEDIA_UPLOAD_BYTES,
    )
    if len(file_bytes) == 0:
        raise DomainError(
            "Завантажений файл зображення порожній.",
            code="EMPTY_MEDIA_FILE",
            status_code=422,
            context={"course_id": str(course_id), "file_name": safe_filename},
        )

    if not _matches_raster_image_magic_bytes(actual_suffix, file_bytes):
        raise DomainError(
            f"Вміст файлу '{safe_filename}' не відповідає формату '{actual_suffix}' "
            "(невалідна сигнатура зображення).",
            code="INVALID_IMAGE_MAGIC_BYTES",
            status_code=422,
            context={
                "course_id": str(course_id),
                "file_name": safe_filename,
                "actual_suffix": actual_suffix,
            },
        )

    ext_no_dot = actual_suffix.lstrip(".")
    stored_filename, _saved_path = await run_in_threadpool(
        _save_course_media_file,
        media_dir=settings.COURSE_MEDIA_DIR,
        course_slug=course.slug.value,
        ext_no_dot=ext_no_dot,
        file_bytes=file_bytes,
    )
    media_url = f"/media/courses/{course.slug.value}/uploads/{stored_filename}"
    return CourseMediaUploadRead(
        url=media_url,
        markdown=f"![Ілюстрація]({media_url})",
        filename=stored_filename,
        size_bytes=len(file_bytes),
    )


@router.patch("/modules/{module_id}", response_model=ModuleDetailRead)
async def update_module(
    module_id: uuid.UUID,
    payload: ModuleUpdate,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ModuleDetailRead:
    """Оновлює порядковий номер, заголовок або текст лекції модуля."""
    module = await _load_module_or_404(db, module_id)
    ensure_course_owner_or_admin(
        module.course,
        current_user,
        context={"module_id": str(module_id)},
    )
    if payload.order_index is not None and payload.order_index != module.order_index:
        await _ensure_module_order_index_unique(
            db,
            module.course_id,
            payload.order_index,
            exclude_module_id=module.id,
        )
        module.order_index = payload.order_index
    if payload.title is not None:
        module.title = payload.title
    if payload.lecture_content is not None:
        module.lecture_content = payload.lecture_content

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DomainError(
            f"У цьому курсі модуль із порядковим номером {module.order_index} уже існує.",
            code="MODULE_ORDER_INDEX_EXISTS",
            status_code=409,
            context={
                "course_id": str(module.course_id),
                "order_index": module.order_index,
            },
        ) from exc
    refreshed_module = await _load_module_or_404(db, module.id)
    return await _build_module_detail_read(db, refreshed_module, current_user)


@router.delete(
    "/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_module(
    module_id: uuid.UUID,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Видаляє модуль курсу, перенумеровує решту тем 1..N та видаляє файли здач із диска."""
    stmt = (
        select(Module)
        .execution_options(populate_existing=True)
        .options(
            selectinload(Module.course),
            selectinload(Module.quiz_questions),
            selectinload(Module.quiz_attempts),
            selectinload(Module.practical).selectinload(Practical.submissions),
        )
        .where(Module.id == module_id)
    )
    result = await db.execute(stmt)
    module = result.scalar_one_or_none()
    if module is None:
        raise DomainError(
            "Навчальний модуль не знайдено.",
            code="MODULE_NOT_FOUND",
            status_code=404,
            context={"module_id": str(module_id)},
        )

    ensure_course_owner_or_admin(
        module.course,
        current_user,
        code="FORBIDDEN_COURSE_MODIFICATION",
        context={"module_id": str(module_id)},
    )

    submission_file_paths: list[str] = []
    if module.practical is not None:
        submission_file_paths = await _collect_practical_submission_file_paths(
            db,
            module.practical.id,
        )
        if (
            module.practical.template_file_path is not None
            and module.practical.template_file_path.strip()
        ):
            submission_file_paths.append(module.practical.template_file_path)

    course_id = module.course_id
    if "modules" in module.course.__dict__ and module in module.course.modules:
        module.course.modules.remove(module)
    await db.delete(module)
    await db.flush()

    remaining_stmt = (
        select(Module)
        .where(Module.course_id == course_id, Module.id != module_id)
        .order_by(Module.order_index.asc(), Module.id.asc())
    )
    remaining_result = await db.execute(remaining_stmt)
    for new_order_index, remaining_module in enumerate(
        remaining_result.scalars().all(),
        start=1,
    ):
        if remaining_module.order_index != new_order_index:
            remaining_module.order_index = new_order_index
            await db.flush()

    await db.commit()

    if submission_file_paths:
        await delete_submission_files_for_paths_async(
            submission_file_paths,
            upload_dir=settings.UPLOADS_DIR,
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/modules/{module_id}/quiz/questions",
    response_model=list[QuizQuestionTeacherRead],
)
async def list_module_quiz_questions_teacher(
    module_id: uuid.UUID,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[QuizQuestionTeacherRead]:
    """Повертає перелік питань тесту-допуску модуля разом із правильними відповідями."""
    module = await _load_module_or_404(db, module_id)
    ensure_course_owner_or_admin(
        module.course,
        current_user,
        context={"module_id": str(module_id)},
    )
    questions_stmt = (
        select(QuizQuestion)
        .where(QuizQuestion.module_id == module.id)
        .order_by(QuizQuestion.order_index.asc(), QuizQuestion.id.asc())
    )
    questions_result = await db.execute(questions_stmt)
    ordered_questions = questions_result.scalars().all()
    return [
        QuizQuestionTeacherRead(
            id=question.id,
            module_id=question.module_id,
            question_text=question.question_text,
            options=list(question.options),
            correct_option_index=question.correct_option_index,
        )
        for question in ordered_questions
    ]


@router.post(
    "/modules/{module_id}/quiz/questions",
    response_model=QuizQuestionTeacherRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_quiz_question(
    module_id: uuid.UUID,
    payload: QuizQuestionCreate,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuizQuestionTeacherRead:
    """Додає нове тестове питання до модуля."""
    module = await _load_module_or_404(db, module_id)
    ensure_course_owner_or_admin(
        module.course,
        current_user,
        context={"module_id": str(module_id)},
    )
    if payload.correct_option_index >= len(payload.options):
        raise DomainError(
            "Індекс правильної відповіді виходить за межі списку варіантів.",
            code="INVALID_CORRECT_OPTION_INDEX",
            status_code=422,
            context={
                "correct_option_index": payload.correct_option_index,
                "options_count": len(payload.options),
            },
        )

    max_order_result = await db.execute(
        select(func.max(QuizQuestion.order_index)).where(
            QuizQuestion.module_id == module_id
        )
    )
    max_order_index = max_order_result.scalar_one_or_none()
    next_order_index = int(max_order_index) + 1 if max_order_index is not None else 1

    question = QuizQuestion(
        module_id=module_id,
        order_index=next_order_index,
        question_text=payload.question_text,
        options=list(payload.options),
        correct_option_index=payload.correct_option_index,
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)

    return QuizQuestionTeacherRead(
        id=question.id,
        module_id=question.module_id,
        question_text=question.question_text,
        options=list(question.options),
        correct_option_index=question.correct_option_index,
    )


@router.patch(
    "/quiz/questions/{question_id}",
    response_model=QuizQuestionTeacherRead,
)
async def update_quiz_question(
    question_id: uuid.UUID,
    payload: QuizQuestionUpdate,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuizQuestionTeacherRead:
    """Оновлює текст, варіанти або правильну відповідь питання зі збереженням id та порядку."""
    stmt = (
        select(QuizQuestion)
        .options(
            selectinload(QuizQuestion.module).selectinload(Module.course),
        )
        .where(QuizQuestion.id == question_id)
    )
    result = await db.execute(stmt)
    question = result.scalar_one_or_none()
    if question is None:
        raise DomainError(
            "Тестове питання не знайдено.",
            code="QUIZ_QUESTION_NOT_FOUND",
            status_code=404,
            context={"question_id": str(question_id)},
        )

    ensure_course_owner_or_admin(
        question.module.course,
        current_user,
        context={"question_id": str(question_id)},
    )

    effective_options = (
        list(payload.options)
        if payload.options is not None
        else [opt.strip() for opt in question.options]
    )
    if len(effective_options) < 2 or any(not opt for opt in effective_options):
        raise DomainError(
            "Необхідно вказати щонайменше 2 непорожні варіанти відповіді.",
            code="INVALID_QUIZ_OPTIONS",
            status_code=422,
            context={"question_id": str(question_id)},
        )

    effective_correct_index = (
        payload.correct_option_index
        if payload.correct_option_index is not None
        else question.correct_option_index
    )
    if effective_correct_index < 0 or effective_correct_index >= len(effective_options):
        raise DomainError(
            "Індекс правильної відповіді виходить за межі списку варіантів.",
            code="INVALID_CORRECT_OPTION_INDEX",
            status_code=422,
            context={
                "question_id": str(question_id),
                "correct_option_index": effective_correct_index,
                "options_count": len(effective_options),
            },
        )

    if payload.question_text is not None:
        question.question_text = payload.question_text
    if payload.options is not None:
        question.options = effective_options
    if payload.correct_option_index is not None:
        question.correct_option_index = effective_correct_index

    await db.commit()
    await db.refresh(question)

    return QuizQuestionTeacherRead(
        id=question.id,
        module_id=question.module_id,
        question_text=question.question_text,
        options=list(question.options),
        correct_option_index=question.correct_option_index,
    )


@router.delete(
    "/quiz/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_quiz_question(
    question_id: uuid.UUID,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Видаляє тестове питання за його ідентифікатором."""
    stmt = (
        select(QuizQuestion)
        .options(
            selectinload(QuizQuestion.module).selectinload(Module.course),
        )
        .where(QuizQuestion.id == question_id)
    )
    result = await db.execute(stmt)
    question = result.scalar_one_or_none()
    if question is None:
        raise DomainError(
            "Тестове питання не знайдено.",
            code="QUIZ_QUESTION_NOT_FOUND",
            status_code=404,
            context={"question_id": str(question_id)},
        )

    ensure_course_owner_or_admin(
        question.module.course,
        current_user,
        context={"question_id": str(question_id)},
    )

    await db.delete(question)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/modules/{module_id}/quiz/submit", response_model=QuizSubmitResponse)
async def submit_module_quiz(
    module_id: uuid.UUID,
    payload: QuizSubmitRequest,
    current_user: StudentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuizSubmitResponse:
    """Перевіряє відповіді тесту-допуску студента та розблоковує практичну роботу."""
    quiz_service = QuizService(db)
    return await quiz_service.submit_quiz(
        student=current_user,
        module_id=module_id,
        payload=payload,
    )


@router.get("/practicals/{practical_id}", response_model=PracticalStudentRead)
async def get_practical_for_student(
    practical_id: uuid.UUID,
    current_user: StudentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PracticalStudentRead:
    """Повертає методичні вказівки та персональний варіант практичної роботи студента."""
    quiz_service = QuizService(db)
    return await quiz_service.get_student_practical(
        student=current_user,
        practical_id=practical_id,
    )


@router.get("/practicals/{practical_id}/teacher", response_model=PracticalTeacherRead)
async def get_practical_for_teacher(
    practical_id: uuid.UUID,
    _current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PracticalTeacherRead:
    """Повертає повні налаштування практичної роботи з усіма варіантами та правилами."""
    stmt = select(Practical).where(Practical.id == practical_id)
    result = await db.execute(stmt)
    practical = result.scalar_one_or_none()
    if practical is None:
        raise DomainError(
            "Практичну роботу не знайдено.",
            code="PRACTICAL_NOT_FOUND",
            status_code=404,
            context={"practical_id": str(practical_id)},
        )
    return _serialize_practical_teacher(practical)


@router.post(
    "/modules/{module_id}/practical",
    response_model=PracticalTeacherRead,
    status_code=status.HTTP_201_CREATED,
)
async def upsert_module_practical(
    module_id: uuid.UUID,
    payload: PracticalCreate,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PracticalTeacherRead:
    """Створює або повністю оновлює практичну роботу модуля."""
    module = await _load_module_or_404(db, module_id)
    ensure_course_owner_or_admin(
        module.course,
        current_user,
        context={"module_id": str(module_id)},
    )
    serialized_variants: list[dict[str, object]] = [
        variant.model_dump(mode="json") for variant in payload.variants
    ]
    serialized_rules: list[dict[str, object]] = [
        rule.model_dump(mode="json") for rule in payload.grading_rules
    ]
    max_score_decimal = payload.max_score.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    if module.practical is None:
        practical = Practical(
            module_id=module.id,
            title=payload.title,
            instructions=payload.instructions,
            format_type=payload.format_type,
            max_score=max_score_decimal,
            variants=serialized_variants,
            grading_rules=serialized_rules,
        )
        db.add(practical)
    else:
        practical = module.practical
        practical.title = payload.title
        practical.instructions = payload.instructions
        practical.format_type = payload.format_type
        practical.max_score = max_score_decimal
        practical.variants = serialized_variants
        practical.grading_rules = serialized_rules

    await db.commit()
    await db.refresh(practical)
    return _serialize_practical_teacher(practical)


@router.patch("/practicals/{practical_id}", response_model=PracticalTeacherRead)
async def update_practical(
    practical_id: uuid.UUID,
    payload: PracticalUpdate,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PracticalTeacherRead:
    """Частково оновлює параметри, варіанти або правила практичної роботи."""
    stmt = (
        select(Practical)
        .options(
            selectinload(Practical.module).selectinload(Module.course),
        )
        .where(Practical.id == practical_id)
    )
    result = await db.execute(stmt)
    practical = result.scalar_one_or_none()
    if practical is None:
        raise DomainError(
            "Практичну роботу не знайдено.",
            code="PRACTICAL_NOT_FOUND",
            status_code=404,
            context={"practical_id": str(practical_id)},
        )

    ensure_course_owner_or_admin(
        practical.module.course,
        current_user,
        context={"practical_id": str(practical_id)},
    )

    if payload.title is not None:
        practical.title = payload.title
    if payload.instructions is not None:
        practical.instructions = payload.instructions
    if payload.format_type is not None:
        practical.format_type = payload.format_type
    if payload.max_score is not None:
        practical.max_score = payload.max_score.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    if payload.variants is not None:
        practical.variants = [
            variant.model_dump(mode="json") for variant in payload.variants
        ]
    if payload.grading_rules is not None:
        practical.grading_rules = [
            rule.model_dump(mode="json") for rule in payload.grading_rules
        ]
    if payload.needs_rules_review is not None:
        practical.needs_rules_review = payload.needs_rules_review

    await db.commit()
    await db.refresh(practical)
    return _serialize_practical_teacher(practical)


@router.delete(
    "/practicals/{practical_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_practical(
    practical_id: uuid.UUID,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Видаляє практичну роботу й її здачі, залишаючи модуль, лекцію та тест недоторканими."""
    stmt = (
        select(Practical)
        .execution_options(populate_existing=True)
        .options(
            selectinload(Practical.module).selectinload(Module.course),
            selectinload(Practical.submissions),
        )
        .where(Practical.id == practical_id)
    )
    result = await db.execute(stmt)
    practical = result.scalar_one_or_none()
    if practical is None:
        raise DomainError(
            "Практичну роботу не знайдено.",
            code="PRACTICAL_NOT_FOUND",
            status_code=404,
            context={"practical_id": str(practical_id)},
        )

    ensure_course_owner_or_admin(
        practical.module.course,
        current_user,
        code="FORBIDDEN_COURSE_MODIFICATION",
        context={"practical_id": str(practical_id)},
    )

    submission_file_paths = await _collect_practical_submission_file_paths(
        db,
        practical.id,
    )
    if (
        practical.template_file_path is not None
        and practical.template_file_path.strip()
    ):
        submission_file_paths.append(practical.template_file_path)

    if "practical" in practical.module.__dict__:
        practical.module.practical = None
    await db.delete(practical)
    await db.commit()

    if submission_file_paths:
        await delete_submission_files_for_paths_async(
            submission_file_paths,
            upload_dir=settings.UPLOADS_DIR,
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
