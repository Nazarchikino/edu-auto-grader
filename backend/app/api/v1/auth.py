import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.exceptions import DomainError
from app.core.security import create_token_pair, decode_token, verify_password
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


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
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Автентифікує користувача за email та паролем і повертає пару JWT-токенів."""
    normalized_email = payload.email.strip().lower()
    stmt = select(User).where(func.lower(User.email) == normalized_email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise DomainError(
            "Невірна електронна пошта або пароль.",
            code="INVALID_CREDENTIALS",
            status_code=401,
        )

    return create_token_pair(subject=user.id, role=user.role)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    payload: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Оновлює пару JWT access та refresh токенів за дійсним refresh-токеном."""
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

    return create_token_pair(subject=user.id, role=user.role)


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Повертає профіль поточного автентифікованого користувача."""
    return serialize_user(current_user)
