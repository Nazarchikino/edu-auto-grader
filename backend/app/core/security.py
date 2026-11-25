import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

import bcrypt
import jwt
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.exceptions import DomainError
from app.models.user import UserRole
from app.schemas.auth import TokenPayload, TokenResponse

PASSWORD_HASH_PREFIX: str = "sha256$"
BCRYPT_MAX_PASSWORD_BYTES: int = 72


def _sha256_password_bytes(plain_password: str) -> bytes:
    """Попередньо хешує пароль через SHA-256 у 64 ASCII-байти для безпечного bcrypt."""
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest().encode("ascii")


def hash_password(plain_password: str) -> str:
    """Генерує безпечний `sha256$<bcrypt>` хеш без обмеження 72 байтів UTF-8."""
    salt: bytes = bcrypt.gensalt(rounds=12)
    hashed: bytes = bcrypt.hashpw(_sha256_password_bytes(plain_password), salt)
    return f"{PASSWORD_HASH_PREFIX}{hashed.decode('utf-8')}"


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Перевіряє пароль проти `sha256$<bcrypt>` або legacy-хешу bcrypt без ValueError."""
    if not password_hash:
        return False

    try:
        if password_hash.startswith(PASSWORD_HASH_PREFIX):
            raw_bcrypt_hash = password_hash[len(PASSWORD_HASH_PREFIX) :]
            if not raw_bcrypt_hash:
                return False
            return bcrypt.checkpw(
                _sha256_password_bytes(plain_password),
                raw_bcrypt_hash.encode("utf-8"),
            )

        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
            return False
        return bcrypt.checkpw(
            password_bytes,
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


async def hash_password_async(plain_password: str) -> str:
    """Асинхронно хешує пароль через bcrypt у threadpool без блокування Event Loop."""
    return await run_in_threadpool(hash_password, plain_password)


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """Асинхронно перевіряє пароль через bcrypt у threadpool без блокування Event Loop."""
    return await run_in_threadpool(verify_password, plain_password, hashed_password)


def _encode_jwt_token(
    *,
    subject: str,
    role: UserRole,
    token_type: Literal["access", "refresh"],
    expires_delta: timedelta,
    token_version: int = 0,
) -> str:
    """Формує та підписує JWT-токен із claims (sub, role, token_type, tv, iat, exp)."""
    now = datetime.now(UTC)
    expire = now + expires_delta
    payload: dict[str, object] = {
        "sub": subject,
        "role": role.value,
        "token_type": token_type,
        "tv": token_version,
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
    *,
    token_version: int = 0,
) -> str:
    """Створює підписаний JWT access-токен із заданим терміном дії та token_version."""
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
        token_version=token_version,
    )


def create_refresh_token(
    subject: str | uuid.UUID,
    role: UserRole,
    expires_delta: timedelta | None = None,
    *,
    token_version: int = 0,
) -> str:
    """Створює підписаний JWT refresh-токен із заданим терміном дії та token_version."""
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
        token_version=token_version,
    )


def create_token_pair(
    subject: str | uuid.UUID,
    role: UserRole,
    *,
    token_version: int = 0,
) -> TokenResponse:
    """Генерує пару JWT access та refresh токенів для користувача з прив'язкою до tv."""
    return TokenResponse(
        access_token=create_access_token(
            subject=subject,
            role=role,
            token_version=token_version,
        ),
        refresh_token=create_refresh_token(
            subject=subject,
            role=role,
            token_version=token_version,
        ),
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
