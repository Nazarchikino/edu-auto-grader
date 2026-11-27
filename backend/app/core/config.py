from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT: Path = Path(__file__).resolve().parents[2]
_PROJECT_ROOT: Path = _BACKEND_ROOT.parent

DEFAULT_JWT_SECRET_KEY: str = "change-me-in-production-super-secret-jwt-key-32b"
MIN_PRODUCTION_JWT_SECRET_LENGTH: int = 32


def _resolve_backend_path(raw_path: Path) -> Path:
    """Безпечно резолвить відносний шлях (uploads/content/media) відносно кореня `backend/`."""
    if raw_path.is_absolute():
        return raw_path

    if raw_path.parts and raw_path.parts[0] == _BACKEND_ROOT.name:
        stripped = Path(*raw_path.parts[1:]) if len(raw_path.parts) > 1 else Path()
        candidate_from_backend = (_BACKEND_ROOT / stripped).resolve()
        if candidate_from_backend.exists():
            return candidate_from_backend
        return (_PROJECT_ROOT / raw_path).resolve()

    return (_BACKEND_ROOT / raw_path).resolve()


class Settings(BaseSettings):
    """Глобальні налаштування середовища застосунку (Pydantic v2 BaseSettings)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Edu Auto Grader"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    APP_ENV: Literal["development", "test", "production"] = "development"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "edu_auto_grader"
    DATABASE_URL: str | None = None

    JWT_SECRET_KEY: str = DEFAULT_JWT_SECRET_KEY
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ENABLE_LOGIN_RATE_LIMIT: bool = True
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS: int = Field(default=10, ge=1)
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60, ge=1)

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )

    UPLOADS_DIR: Path = _BACKEND_ROOT / "uploads"
    SUBMISSION_FILE_RETENTION_DAYS: int = Field(default=90, ge=1)
    SUBMISSION_SUPERSEDED_GRACE_HOURS: int = Field(default=24, ge=0)
    ENABLE_RETENTION_CLEANUP_TASK: bool = True
    COURSE_CONTENT_DIR: Path = _BACKEND_ROOT / "content" / "courses"
    COURSE_MEDIA_DIR: Path = _BACKEND_ROOT / "content" / "media"
    QUIZ_PASS_THRESHOLD_PERCENT: float = Field(default=70.0, ge=0.0, le=100.0)
    QUIZ_RETRY_COOLDOWN_SECONDS: int = Field(default=300, ge=0)

    MAX_OFFICE_UPLOAD_BYTES: int = Field(default=15 * 1024 * 1024, ge=1)
    MAX_ACCDB_UPLOAD_BYTES: int = Field(default=30 * 1024 * 1024, ge=1)
    MAX_IMPORT_UPLOAD_BYTES: int = Field(default=5 * 1024 * 1024, ge=1)
    MAX_COURSE_MEDIA_UPLOAD_BYTES: int = Field(default=5 * 1024 * 1024, ge=1)

    MAX_ZIP_ENTRIES: int = Field(default=500, ge=1)
    MAX_ZIP_UNCOMPRESSED_BYTES: int = Field(default=50 * 1024 * 1024, ge=1)
    MAX_ZIP_SINGLE_ENTRY_BYTES: int = Field(default=20 * 1024 * 1024, ge=1)
    MAX_ZIP_COMPRESSION_RATIO: float = Field(default=100.0, gt=0.0)

    @field_validator("UPLOADS_DIR", "COURSE_CONTENT_DIR", "COURSE_MEDIA_DIR", mode="after")
    @classmethod
    def _validate_backend_paths(cls, value: Path) -> Path:
        return _resolve_backend_path(value)

    @model_validator(mode="after")
    def _validate_production_security(self) -> "Settings":
        """Блокує запуск у production із дефолтним або закоротким JWT_SECRET_KEY."""
        if self.APP_ENV == "production":
            stripped_secret = self.JWT_SECRET_KEY.strip()
            if (
                self.JWT_SECRET_KEY == DEFAULT_JWT_SECRET_KEY
                or stripped_secret == DEFAULT_JWT_SECRET_KEY
                or len(stripped_secret) < MIN_PRODUCTION_JWT_SECRET_LENGTH
            ):
                raise ValueError(
                    "У режимі production необхідно задати надійний JWT_SECRET_KEY "
                    f"довжиною щонайменше {MIN_PRODUCTION_JWT_SECRET_LENGTH} символів, "
                    "відмінний від значення за замовчуванням."
                )
        return self

    @property
    def async_database_url(self) -> str:
        """Формує асинхронний DSN для SQLAlchemy 2.0 (asyncpg)."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Повертає кешований екземпляр налаштувань застосунку."""
    return Settings()


settings: Settings = get_settings()
