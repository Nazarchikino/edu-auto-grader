import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_role
from app.api.v1.auth import serialize_user
from app.core.config import settings
from app.core.exceptions import DomainError
from app.core.security import hash_password_async
from app.core.upload_utils import read_upload_file_limited
from app.models.course import Course
from app.models.progress import Submission
from app.models.user import AcademicGroup, User, UserRole
from app.schemas.auth import (
    AcademicGroupCreate,
    AcademicGroupRead,
    AcademicGroupUpdate,
    AdminResetPasswordRequest,
    AdminResetPasswordResponse,
    StudentImportResponse,
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.services.retention_service import delete_submission_files_for_paths_async
from app.services.student_import_service import StudentImportService, generate_temp_password

router = APIRouter(prefix="/admin", tags=["admin"])

AdminUser = Annotated[
    User,
    Depends(require_role(UserRole.ADMIN)),
]


def _normalize_non_empty(value: str, *, field_label: str, code: str) -> str:
    """Обрізає пробіли та перевіряє, що текстове поле не є порожнім."""
    cleaned = value.strip()
    if not cleaned:
        raise DomainError(
            f"Поле «{field_label}» не може бути порожнім.",
            code=code,
            status_code=422,
        )
    return cleaned


def _normalize_email(raw_email: str) -> str:
    """Нормалізує та виконує базову валідацію формату електронної пошти."""
    email = raw_email.strip().lower()
    if (
        not email
        or " " in email
        or email.count("@") != 1
        or email.startswith("@")
        or email.endswith("@")
    ):
        raise DomainError(
            "Некоректний формат електронної пошти.",
            code="INVALID_EMAIL",
            status_code=422,
            context={"email": raw_email},
        )
    local_part, domain_part = email.split("@", maxsplit=1)
    if (
        not local_part
        or "." not in domain_part
        or domain_part.startswith(".")
        or domain_part.endswith(".")
    ):
        raise DomainError(
            "Некоректний формат електронної пошти.",
            code="INVALID_EMAIL",
            status_code=422,
            context={"email": raw_email},
        )
    return email


async def _get_group_or_404(
    db: AsyncSession,
    group_id: uuid.UUID,
) -> AcademicGroup:
    """Повертає академічну групу за ID або піднімає DomainError 404."""
    result = await db.execute(
        select(AcademicGroup).where(AcademicGroup.id == group_id)
    )
    group = result.scalar_one_or_none()
    if group is None:
        raise DomainError(
            "Академічну групу не знайдено.",
            code="GROUP_NOT_FOUND",
            status_code=404,
            context={"group_id": str(group_id)},
        )
    return group


async def _get_user_with_group_or_404(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> User:
    """Повертає користувача із завантаженою групою або піднімає DomainError 404."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.group))
        .where(User.id == user_id)
        .execution_options(populate_existing=True)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise DomainError(
            "Користувача не знайдено.",
            code="USER_NOT_FOUND",
            status_code=404,
            context={"user_id": str(user_id)},
        )
    return user


async def _ensure_group_code_unique(
    db: AsyncSession,
    code: str,
    *,
    exclude_group_id: uuid.UUID | None = None,
) -> None:
    """Перевіряє унікальність шифру академічної групи (Unicode case-insensitive)."""
    stmt = select(AcademicGroup.id, AcademicGroup.code)
    if exclude_group_id is not None:
        stmt = stmt.where(AcademicGroup.id != exclude_group_id)
    result = await db.execute(stmt)
    target_key = code.casefold()
    for _existing_id, existing_code in result.all():
        if existing_code.casefold() == target_key:
            raise DomainError(
                f"Академічна група з шифром «{code}» вже існує.",
                code="GROUP_CODE_EXISTS",
                status_code=409,
                context={"code": code},
            )


async def _ensure_email_unique(
    db: AsyncSession,
    email: str,
    *,
    exclude_user_id: uuid.UUID | None = None,
) -> None:
    """Перевіряє унікальність електронної пошти користувача."""
    stmt = select(User.id).where(func.lower(User.email) == email.lower())
    if exclude_user_id is not None:
        stmt = stmt.where(User.id != exclude_user_id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise DomainError(
            f"Користувач із поштою «{email}» вже зареєстрований.",
            code="USER_EMAIL_EXISTS",
            status_code=409,
            context={"email": email},
        )


@router.get("/groups", response_model=list[AcademicGroupRead])
async def list_admin_groups(
    _current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AcademicGroupRead]:
    """Повертає перелік усіх академічних груп коледжу для панелі адміністратора."""
    stmt = select(AcademicGroup).order_by(
        AcademicGroup.course_year.asc(),
        AcademicGroup.code.asc(),
    )
    result = await db.execute(stmt)
    groups = result.scalars().all()
    return [AcademicGroupRead.model_validate(group) for group in groups]


@router.post(
    "/groups",
    response_model=AcademicGroupRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_admin_group(
    payload: AcademicGroupCreate,
    _current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AcademicGroupRead:
    """Створює нову академічну групу у довіднику коледжу."""
    code = _normalize_non_empty(
        payload.code,
        field_label="Шифр групи",
        code="INVALID_GROUP_CODE",
    )
    specialty = _normalize_non_empty(
        payload.specialty,
        field_label="Спеціальність",
        code="INVALID_SPECIALTY",
    )
    await _ensure_group_code_unique(db, code)

    group = AcademicGroup(
        code=code,
        specialty=specialty,
        course_year=payload.course_year,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return AcademicGroupRead.model_validate(group)


@router.patch("/groups/{group_id}", response_model=AcademicGroupRead)
async def update_admin_group(
    group_id: uuid.UUID,
    payload: AcademicGroupUpdate,
    _current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AcademicGroupRead:
    """Оновлює шифр, спеціальність або курс академічної групи."""
    group = await _get_group_or_404(db, group_id)
    fields_set = payload.model_fields_set

    if "code" in fields_set and payload.code is not None:
        normalized_code = _normalize_non_empty(
            payload.code,
            field_label="Шифр групи",
            code="INVALID_GROUP_CODE",
        )
        await _ensure_group_code_unique(
            db,
            normalized_code,
            exclude_group_id=group.id,
        )
        group.code = normalized_code

    if "specialty" in fields_set and payload.specialty is not None:
        group.specialty = _normalize_non_empty(
            payload.specialty,
            field_label="Спеціальність",
            code="INVALID_SPECIALTY",
        )

    if "course_year" in fields_set and payload.course_year is not None:
        group.course_year = payload.course_year

    await db.commit()
    await db.refresh(group)
    return AcademicGroupRead.model_validate(group)


@router.delete(
    "/groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_admin_group(
    group_id: uuid.UUID,
    _current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Видаляє академічну групу та відв'язує студентів, які до неї належали."""
    group = await _get_group_or_404(db, group_id)

    await db.execute(
        update(User)
        .where(User.group_id == group.id)
        .values(group_id=None)
    )
    await db.delete(group)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/users", response_model=list[UserRead])
async def list_admin_users(
    _current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    role: Annotated[UserRole | None, Query()] = None,
    group_id: Annotated[uuid.UUID | None, Query()] = None,
    search: Annotated[str | None, Query(max_length=128)] = None,
) -> list[UserRead]:
    """Повертає перелік облікових записів користувачів із підтримкою фільтрації."""
    stmt = (
        select(User)
        .options(selectinload(User.group))
        .order_by(User.full_name.asc(), User.email.asc())
    )

    if role is not None:
        stmt = stmt.where(User.role == role)

    if group_id is not None:
        stmt = stmt.where(User.group_id == group_id)

    result = await db.execute(stmt)
    users = list(result.scalars().all())

    if search is not None and search.strip():
        needle = search.strip().casefold()
        users = [
            user
            for user in users
            if needle in user.full_name.casefold()
            or needle in user.email.casefold()
            or (user.group is not None and needle in user.group.code.casefold())
        ]

    return [serialize_user(user) for user in users]


@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_admin_user(
    payload: UserCreate,
    _current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Створює новий обліковий запис студента, викладача або адміністратора."""
    email = _normalize_email(payload.email)
    full_name = _normalize_non_empty(
        payload.full_name,
        field_label="ПІБ користувача",
        code="INVALID_FULL_NAME",
    )
    await _ensure_email_unique(db, email)

    resolved_group_id: uuid.UUID | None = None
    resolved_list_number: int | None = None
    if payload.role == UserRole.STUDENT:
        if payload.group_id is not None:
            await _get_group_or_404(db, payload.group_id)
            resolved_group_id = payload.group_id
        resolved_list_number = payload.list_number

    password_hash = await hash_password_async(payload.password)
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role=payload.role,
        group_id=resolved_group_id,
        list_number=resolved_list_number,
    )
    db.add(user)
    await db.commit()

    created_user = await _get_user_with_group_or_404(db, user.id)
    return serialize_user(created_user)


@router.post(
    "/users/import",
    response_model=StudentImportResponse,
    status_code=status.HTTP_200_OK,
)
async def import_admin_students(
    _current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    group_id: Annotated[uuid.UUID, Form()],
    file: Annotated[UploadFile, File()],
) -> StudentImportResponse:
    """Масово імпортує студентів академічної групи з файлу відомості .docx або .txt."""
    filename = file.filename or ""
    try:
        file_bytes = await read_upload_file_limited(
            file,
            max_bytes=settings.MAX_IMPORT_UPLOAD_BYTES,
        )
    finally:
        await file.close()

    service = StudentImportService(db)
    return await service.import_students(
        group_id=group_id,
        filename=filename,
        file_bytes=file_bytes,
    )


@router.patch("/users/{user_id}", response_model=UserRead)
async def update_admin_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Оновлює облікові дані, роль, академічну групу або номер у списку користувача."""
    user = await _get_user_with_group_or_404(db, user_id)
    fields_set = payload.model_fields_set

    if "email" in fields_set and payload.email is not None:
        normalized_email = _normalize_email(payload.email)
        await _ensure_email_unique(
            db,
            normalized_email,
            exclude_user_id=user.id,
        )
        user.email = normalized_email

    if "full_name" in fields_set and payload.full_name is not None:
        user.full_name = _normalize_non_empty(
            payload.full_name,
            field_label="ПІБ користувача",
            code="INVALID_FULL_NAME",
        )

    target_role = user.role
    if "role" in fields_set and payload.role is not None:
        if user.id == current_admin.id and payload.role != UserRole.ADMIN:
            raise DomainError(
                "Неможливо зняти роль адміністратора з власного облікового запису.",
                code="CANNOT_DEMOTE_SELF",
                status_code=409,
                context={"user_id": str(user.id)},
            )
        target_role = payload.role
        user.role = target_role

    if target_role == UserRole.STUDENT:
        if "group_id" in fields_set:
            if payload.group_id is not None:
                await _get_group_or_404(db, payload.group_id)
            user.group_id = payload.group_id
        if "list_number" in fields_set:
            user.list_number = payload.list_number
    else:
        user.group_id = None
        user.list_number = None

    if "password" in fields_set and payload.password is not None:
        user.password_hash = await hash_password_async(payload.password)
        user.token_version += 1
        if user.id != current_admin.id:
            user.must_change_password = True

    await db.commit()
    updated_user = await _get_user_with_group_or_404(db, user.id)
    return serialize_user(updated_user)


@router.post(
    "/users/{user_id}/reset-password",
    response_model=AdminResetPasswordResponse,
    status_code=status.HTTP_200_OK,
)
async def reset_admin_user_password(
    user_id: uuid.UUID,
    _current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    payload: AdminResetPasswordRequest | None = None,
) -> AdminResetPasswordResponse:
    """Скидає пароль користувача, інкрементує token_version і вимагає зміну пароля."""
    user = await _get_user_with_group_or_404(db, user_id)
    resolved_password = (
        payload.new_password
        if payload is not None and payload.new_password is not None
        else generate_temp_password()
    )

    user.password_hash = await hash_password_async(resolved_password)
    user.token_version += 1
    user.must_change_password = True

    await db.commit()
    updated_user = await _get_user_with_group_or_404(db, user.id)
    return AdminResetPasswordResponse(
        user=serialize_user(updated_user),
        temp_password=resolved_password,
    )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_admin_user(
    user_id: uuid.UUID,
    current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Видаляє обліковий запис користувача, якщо він не є поточним адміном і не веде курсів."""
    user = await _get_user_with_group_or_404(db, user_id)

    if user.id == current_admin.id:
        raise DomainError(
            "Неможливо видалити власний обліковий запис адміністратора.",
            code="CANNOT_DELETE_SELF",
            status_code=409,
            context={"user_id": str(user.id)},
        )

    owned_courses_result = await db.execute(
        select(func.count(Course.id)).where(Course.teacher_id == user.id)
    )
    owned_courses_count = int(owned_courses_result.scalar_one())
    if owned_courses_count > 0:
        raise DomainError(
            "Неможливо видалити користувача, оскільки за ним закріплені навчальні курси.",
            code="USER_HAS_COURSES",
            status_code=409,
            context={
                "user_id": str(user.id),
                "courses_count": owned_courses_count,
            },
        )

    submission_paths_result = await db.execute(
        select(Submission.file_path).where(
            Submission.student_id == user.id,
            Submission.file_path.is_not(None),
        )
    )
    submission_file_paths = [
        file_path
        for file_path in submission_paths_result.scalars().all()
        if file_path is not None
    ]

    await db.delete(user)
    await db.commit()

    if submission_file_paths:
        await delete_submission_files_for_paths_async(
            submission_file_paths,
            upload_dir=settings.UPLOADS_DIR,
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
