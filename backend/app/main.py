import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import DomainError
from app.services.retention_service import run_periodic_retention_cleanup


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
    """Фабрика FastAPI-застосунку з налаштуванням CORS та глобальних обробників помилок."""
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
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "version": settings.VERSION}

    return application


app: FastAPI = create_application()
