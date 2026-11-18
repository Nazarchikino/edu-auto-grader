from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import DomainError


def create_application() -> FastAPI:
    """Фабрика FastAPI-застосунку з налаштуванням CORS та глобальних обробників помилок."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
        )

    application.include_router(api_router, prefix=settings.API_V1_STR)
    application.include_router(auth_router, include_in_schema=False)

    @application.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "version": settings.VERSION}

    return application


app: FastAPI = create_application()
