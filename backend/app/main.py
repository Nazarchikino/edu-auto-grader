import asyncio
import contextlib
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api.deps import get_db
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import DomainError
from app.services.retention_service import run_periodic_retention_cleanup

MEDIA_SECURITY_CSP: str = (
    "default-src 'none'; img-src 'self'; media-src 'self'; object-src 'none'; sandbox"
)
MEDIA_PDF_SECURITY_CSP: str = (
    "default-src 'none'; object-src 'self'; frame-ancestors 'self'"
)


class MediaSecurityHeadersMiddleware:
    """ASGI-middleware для виставлення захисних заголовків відповідей у `/media/`."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        path: str = str(scope.get("path", ""))
        if not path.startswith("/media/"):
            await self._app(scope, receive, send)
            return

        is_pdf_path = path.lower().endswith(".pdf")

        async def _send_with_media_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                content_type = headers.get("content-type", "").lower()
                if is_pdf_path or content_type.startswith("application/pdf"):
                    headers["Content-Security-Policy"] = MEDIA_PDF_SECURITY_CSP
                else:
                    headers["Content-Security-Policy"] = MEDIA_SECURITY_CSP
            await send(message)

        await self._app(scope, receive, _send_with_media_headers)


def _check_uploads_dir_writable(upload_dir: Path) -> tuple[bool, str | None]:
    """Перевіряє існування та можливість запису у файлове сховище `UPLOADS_DIR`."""
    try:
        if not upload_dir.exists():
            return False, "Каталог UPLOADS_DIR не існує."
        if not upload_dir.is_dir():
            return False, "Шлях UPLOADS_DIR не є директорією."
        probe_path = upload_dir / f".healthcheck-{uuid.uuid4().hex}.tmp"
        try:
            probe_path.write_bytes(b"ok")
        finally:
            probe_path.unlink(missing_ok=True)
        return True, None
    except OSError as exc:
        return False, f"Каталог UPLOADS_DIR недоступний для запису: {exc}"


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    """Життєвий цикл застосунку: запускає та коректно зупиняє фонове очищення файлів робіт."""
    cleanup_task: asyncio.Task[None] | None = None
    if settings.ENABLE_RETENTION_CLEANUP_TASK:
        cleanup_task = asyncio.create_task(
            run_periodic_retention_cleanup(),
            name="submission-retention-cleanup",
        )
    try:
        yield
    finally:
        if cleanup_task is not None:
            cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await cleanup_task


def create_application() -> FastAPI:
    """Фабрика FastAPI-застосунку з налаштуванням CORS, security-заголовків та healthcheck."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition", "Retry-After"],
    )
    application.add_middleware(MediaSecurityHeadersMiddleware)

    @application.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "code": exc.code,
                "context": exc.context,
            },
            headers=exc.headers,
        )

    application.include_router(api_router, prefix=settings.API_V1_STR)
    application.mount(
        "/media/courses",
        StaticFiles(directory=settings.COURSE_MEDIA_DIR, check_dir=False),
        name="course-media",
    )

    @application.get("/health", tags=["system"])
    @application.get(f"{settings.API_V1_STR}/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        """Liveness-перевірка працездатності API-процесу."""
        return {"status": "ok", "version": settings.VERSION}

    @application.get(f"{settings.API_V1_STR}/health/ready", tags=["system"])
    async def readiness_check(
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> JSONResponse:
        """Readiness-перевірка доступності PostgreSQL (`SELECT 1`) і запису в `UPLOADS_DIR`."""
        details: dict[str, str] = {}

        db_ok = True
        try:
            await db.execute(text("SELECT 1"))
        except Exception as exc:
            db_ok = False
            details["database"] = f"Помилка підключення до БД: {exc}"

        uploads_ok, uploads_error = await run_in_threadpool(
            _check_uploads_dir_writable,
            settings.UPLOADS_DIR,
        )
        if not uploads_ok and uploads_error is not None:
            details["uploads"] = uploads_error

        if db_ok and uploads_ok:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "ready",
                    "database": "ok",
                    "uploads": "ok",
                },
            )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "ok" if db_ok else "error",
                "uploads": "ok" if uploads_ok else "error",
                "details": details,
            },
        )

    return application


app: FastAPI = create_application()
