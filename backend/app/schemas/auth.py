import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import MAX_COURSE_YEAR, MIN_COURSE_YEAR, UserRole


class ErrorResponse(BaseModel):
    """Уніфікований формат JSON-відповіді при виникненні доменних винятків."""

    model_config = ConfigDict(extra="forbid")

    detail: str
    code: str
    context: dict[str, object] = Field(default_factory=dict)


class LoginRequest(BaseModel):
    """Запит на автентифікацію користувача за електронною поштою та паролем."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class RefreshTokenRequest(BaseModel):
    """Запит на оновлення пари токенів за допомогою refresh-токена."""

    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Відповідь сервера з JWT access та refresh токенами."""

    model_config = ConfigDict(extra="forbid")

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class TokenPayload(BaseModel):
    """Декодований корисний вміст (claims) JWT-токена."""

    model_config = ConfigDict(extra="ignore")

    sub: str
    role: UserRole
    token_type: Literal["access", "refresh"]
    exp: int


class AcademicGroupBase(BaseModel):
    """Базові поля академічної групи коледжу."""

    code: str = Field(..., min_length=1, max_length=32)
    specialty: str = Field(..., min_length=1, max_length=128)
    course_year: int = Field(..., ge=MIN_COURSE_YEAR, le=MAX_COURSE_YEAR)


class AcademicGroupCreate(AcademicGroupBase):
    """Схема створення нової академічної групи адміністратором."""

    model_config = ConfigDict(extra="forbid")


class AcademicGroupUpdate(BaseModel):
    """Схема часткового оновлення академічної групи адміністратором."""

    model_config = ConfigDict(extra="forbid")

    code: str | None = Field(default=None, min_length=1, max_length=32)
    specialty: str | None = Field(default=None, min_length=1, max_length=128)
    course_year: int | None = Field(
        default=None,
        ge=MIN_COURSE_YEAR,
        le=MAX_COURSE_YEAR,
    )


class AcademicGroupRead(AcademicGroupBase):
    """Схема читання даних академічної групи."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class UserBase(BaseModel):
    """Базові поля облікового запису користувача."""

    email: str = Field(..., min_length=3, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole
    group_id: uuid.UUID | None = None
    list_number: int | None = Field(default=None, ge=1, le=100)


class UserCreate(UserBase):
    """Схема створення користувача адміністратором."""

    model_config = ConfigDict(extra="forbid")

    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    """Схема часткового оновлення даних користувача адміністратором."""

    model_config = ConfigDict(extra="forbid")

    email: str | None = Field(default=None, min_length=3, max_length=255)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = None
    group_id: uuid.UUID | None = None
    list_number: int | None = Field(default=None, ge=1, le=100)
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserRead(UserBase):
    """Публічне представлення профілю користувача без хешу пароля."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    group_code: str | None = None
    created_at: datetime
