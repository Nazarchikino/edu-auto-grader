import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

import bcrypt
import jwt
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import DomainError
from app.models.user import UserRole
from app.schemas.auth import TokenPayload, TokenResponse


def hash_password(plain_password: str) -> str:
    """Генерує безпечний bcrypt-хеш для відкритого пароля."""
    salt: bytes = bcrypt.gensalt(rounds=12)
    hashed: bytes = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Перевіряє відповідність відкритого пароля збереженому bcrypt-хешу."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def _encode_jwt_token(
    *,
    subject: str,
    role: UserRole,
    token_type: Literal["access", "refresh"],
    expires_delta: timedelta,
) -> str:
    """Формує та підписує JWT-токен із базовими claims (sub, role, token_type, exp)."""
    now = datetime.now(UTC)
    expire = now + expires_delta
    payload: dict[str, object] = {
        "sub": subject,
        "role": role.value,
        "token_type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(
    subject: str | uuid.UUID,
    role: UserRole,
    expires_delta: timedelta | None = None,
) -> str:
    """Створює підписаний JWT access-токен із заданим терміном дії."""
    delta = (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return _encode_jwt_token(
        subject=str(subject),
        role=role,
        token_type="access",
        expires_delta=delta,
    )


def create_refresh_token(
    subject: str | uuid.UUID,
    role: UserRole,
    expires_delta: timedelta | None = None,
) -> str:
    """Створює підписаний JWT refresh-токен із заданим терміном дії."""
    delta = (
        expires_delta
        if expires_delta is not None
        else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return _encode_jwt_token(
        subject=str(subject),
        role=role,
        token_type="refresh",
        expires_delta=delta,
    )


def create_token_pair(
    subject: str | uuid.UUID,
    role: UserRole,
) -> TokenResponse:
    """Генерує пару JWT access та refresh токенів для користувача."""
    return TokenResponse(
        access_token=create_access_token(subject=subject, role=role),
        refresh_token=create_refresh_token(subject=subject, role=role),
        token_type="bearer",
    )


def decode_token(
    token: str,
    *,
    expected_type: Literal["access", "refresh"] | None = None,
) -> TokenPayload:
    """Декодує та валідує JWT-токен, повертаючи типізований TokenPayload."""
    try:
        raw_payload: dict[str, object] = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        payload = TokenPayload.model_validate(raw_payload)
    except jwt.ExpiredSignatureError as exc:
        raise DomainError(
            "Термін дії токена автентифікації минув.",
            code="TOKEN_EXPIRED",
            status_code=401,
        ) from exc
    except (jwt.InvalidTokenError, ValidationError) as exc:
        raise DomainError(
            "Недійсний токен автентифікації.",
            code="INVALID_TOKEN",
            status_code=401,
        ) from exc

    if expected_type is not None and payload.token_type != expected_type:
        raise DomainError(
            f"Очікувався токен типу '{expected_type}', отримано '{payload.token_type}'.",
            code="INVALID_TOKEN_TYPE",
            status_code=401,
            context={
                "expected_type": expected_type,
                "actual_type": payload.token_type,
            },
        )

    return payload
