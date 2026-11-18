import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import DomainError
from app.core.security import decode_token
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Визначає поточного автентифікованого користувача за JWT Bearer-токеном."""
    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
        or not credentials.credentials
    ):
        raise DomainError(
            "Не надано токен автентифікації.",
            code="NOT_AUTHENTICATED",
            status_code=401,
        )

    payload = decode_token(credentials.credentials, expected_type="access")
    try:
        user_id = uuid.UUID(payload.sub)
    except ValueError as exc:
        raise DomainError(
            "Некоректний ідентифікатор користувача в токені.",
            code="INVALID_TOKEN",
            status_code=401,
        ) from exc

    stmt = (
        select(User)
        .options(selectinload(User.group))
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise DomainError(
            "Користувача не знайдено.",
            code="USER_NOT_FOUND",
            status_code=401,
        )

    return user


def require_role(
    *allowed_roles: UserRole,
) -> Callable[[User], Awaitable[User]]:
    """Фабрика RBAC-залежностей для обмеження доступу за ролями користувача."""
    if not allowed_roles:
        raise ValueError("Необхідно вказати щонайменше одну дозволену роль.")

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise DomainError(
                "Недостатньо прав доступу для виконання цієї операції.",
                code="FORBIDDEN",
                status_code=403,
                context={
                    "required_roles": [role.value for role in allowed_roles],
                    "actual_role": current_user.role.value,
                },
            )
        return current_user

    return role_checker


__all__ = [
    "bearer_scheme",
    "get_current_user",
    "get_db",
    "require_role",
]
