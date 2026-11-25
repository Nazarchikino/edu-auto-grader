import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.exceptions import DomainError
from app.core.rate_limit import build_login_rate_limit_key, login_rate_limiter
from app.core.security import (
    create_token_pair,
    decode_token,
    hash_password_async,
    verify_password_async,
)
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _extract_client_ip(request: Request) -> str:
    """Повертає IP-адресу клієнта із запиту для ключа rate limiter."""
    if request.client is not None and request.client.host:
        return request.client.host
    return "unknown"


def serialize_user(user: User) -> UserRead:
    """Перетворює ORM-модель User у публічну Pydantic-схему UserRead."""
    group_code = user.group.code if user.group is not None else None
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        group_id=user.group_id,
        group_code=group_code,
        list_number=user.list_number,
        must_change_password=user.must_change_password,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Автентифікує користувача за email та паролем із rate limiting невдалих спроб."""
    normalized_email = payload.email.strip().lower()
    rate_limit_key = build_login_rate_limit_key(
        _extract_client_ip(request),
        normalized_email,
    )

    if settings.ENABLE_LOGIN_RATE_LIMIT:
        retry_after = login_rate_limiter.check_limit(
            rate_limit_key,
            max_attempts=settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS,
            window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
        )
        if retry_after is not None:
            raise DomainError(
                f"Забагато невдалих спроб входу. Повторіть спробу через {retry_after} с.",
                code="TOO_MANY_LOGIN_ATTEMPTS",
                status_code=429,
                context={"retry_after": retry_after},
                headers={"Retry-After": str(retry_after)},
            )

    stmt = select(User).where(func.lower(User.email) == normalized_email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not await verify_password_async(
        payload.password,
        user.password_hash,
    ):
        if settings.ENABLE_LOGIN_RATE_LIMIT:
            login_rate_limiter.record_failure(
                rate_limit_key,
                window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
            )
        raise DomainError(
            "Невірна електронна пошта або пароль.",
            code="INVALID_CREDENTIALS",
            status_code=401,
        )

    if settings.ENABLE_LOGIN_RATE_LIMIT:
        login_rate_limiter.reset_key(rate_limit_key)

    return create_token_pair(
        subject=user.id,
        role=user.role,
        token_version=user.token_version,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    payload: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Оновлює пару JWT access та refresh токенів із перевіркою token_version."""
    token_payload = decode_token(payload.refresh_token, expected_type="refresh")
    try:
        user_id = uuid.UUID(token_payload.sub)
    except ValueError as exc:
        raise DomainError(
            "Некоректний ідентифікатор користувача в токені.",
            code="INVALID_TOKEN",
            status_code=401,
        ) from exc

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise DomainError(
            "Користувача не знайдено.",
            code="USER_NOT_FOUND",
            status_code=401,
        )

    if token_payload.tv != user.token_version:
        raise DomainError(
            "Сесію завершено через зміну або скидання пароля. Увійдіть повторно.",
            code="TOKEN_REVOKED",
            status_code=401,
        )

    return create_token_pair(
        subject=user.id,
        role=user.role,
        token_version=user.token_version,
    )


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChangePasswordResponse:
    """Змінює пароль поточного користувача, відкликає старі сесії та повертає нові токени."""
    if not await verify_password_async(
        payload.current_password,
        current_user.password_hash,
    ):
        raise DomainError(
            "Поточний пароль вказано невірно.",
            code="INVALID_CURRENT_PASSWORD",
            status_code=400,
        )

    current_user.password_hash = await hash_password_async(payload.new_password)
    current_user.must_change_password = False
    current_user.token_version += 1
    await db.commit()

    refreshed_result = await db.execute(
        select(User)
        .options(selectinload(User.group))
        .where(User.id == current_user.id)
        .execution_options(populate_existing=True)
    )
    updated_user = refreshed_result.scalar_one()

    tokens = create_token_pair(
        subject=updated_user.id,
        role=updated_user.role,
        token_version=updated_user.token_version,
    )
    return ChangePasswordResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        user=serialize_user(updated_user),
    )


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Повертає профіль поточного автентифікованого користувача."""
    return serialize_user(current_user)
