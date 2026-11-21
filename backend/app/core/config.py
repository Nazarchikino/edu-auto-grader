from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT: Path = Path(__file__).resolve().parents[2]
_PROJECT_ROOT: Path = _BACKEND_ROOT.parent


def _resolve_backend_path(raw_path: Path) -> Path:
    """Безпечно резолвить відносний шлях контенту/медіа відносно кореня `backend/`."""
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

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "edu_auto_grader"
    DATABASE_URL: str | None = None

    JWT_SECRET_KEY: str = "change-me-in-production-super-secret-jwt-key-32b"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )

    UPLOADS_DIR: Path = Path("uploads")
    SUBMISSION_FILE_RETENTION_DAYS: int = Field(default=90, ge=1)
    ENABLE_RETENTION_CLEANUP_TASK: bool = True
    COURSE_CONTENT_DIR: Path = _BACKEND_ROOT / "content" / "courses"
    COURSE_MEDIA_DIR: Path = _BACKEND_ROOT / "content" / "media"
    QUIZ_PASS_THRESHOLD_PERCENT: float = 70.0

    @field_validator("COURSE_CONTENT_DIR", "COURSE_MEDIA_DIR", mode="after")
    @classmethod
    def _validate_content_paths(cls, value: Path) -> Path:
        return _resolve_backend_path(value)

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
