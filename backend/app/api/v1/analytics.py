import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.core.exceptions import DomainError
from app.models.user import User, UserRole
from app.schemas.auth import AcademicGroupRead
from app.schemas.submission import ExportFormat, GroupJournalRead
from app.services.export_service import (
    PDF_MEDIA_TYPE,
    XLSX_MEDIA_TYPE,
    ExportService,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

TeacherOrAdminUser = Annotated[
    User,
    Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
]


def _parse_export_format(raw_format: ExportFormat | str) -> ExportFormat:
    """Валідує та нормалізує запитаний формат експорту відомості (.xlsx або .pdf)."""
    if isinstance(raw_format, ExportFormat):
        return raw_format
    normalized = raw_format.strip().lower()
    try:
        return ExportFormat(normalized)
    except ValueError as exc:
        raise DomainError(
            f"Непідтримуваний формат експорту '{raw_format}'. Доступні формати: xlsx, pdf.",
            code="UNSUPPORTED_EXPORT_FORMAT",
            status_code=422,
            context={
                "format": raw_format,
                "allowed_formats": [item.value for item in ExportFormat],
            },
        ) from exc


@router.get("/groups", response_model=list[AcademicGroupRead])
async def list_academic_groups(
    _current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AcademicGroupRead]:
    """Повертає перелік академічних груп коледжу для перегляду журналу та експорту."""
    service = ExportService(db)
    return await service.list_groups()


@router.get("/groups/{group_id}/journal", response_model=GroupJournalRead)
async def get_group_journal(
    group_id: uuid.UUID,
    _current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    course_id: Annotated[uuid.UUID | None, Query()] = None,
) -> GroupJournalRead:
    """Повертає зведену відомість успішності академічної групи та статистику помилок."""
    service = ExportService(db)
    return await service.get_group_journal(
        group_id=group_id,
        course_id=course_id,
    )


@router.get(
    "/groups/{group_id}/export",
    response_class=Response,
    responses={
        200: {
            "description": "Згенерований файл відомості успішності групи (.xlsx або .pdf)",
            "content": {
                XLSX_MEDIA_TYPE: {
                    "schema": {"type": "string", "format": "binary"},
                },
                PDF_MEDIA_TYPE: {
                    "schema": {"type": "string", "format": "binary"},
                },
            },
        }
    },
)
async def export_group_journal(
    group_id: uuid.UUID,
    _current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    format: Annotated[
         str,
        Query(description="Формат експорту відомості успішності: 'xlsx' або 'pdf'"),
    ] = ExportFormat.XLSX.value,
    course_id: Annotated[uuid.UUID | None, Query()] = None,
) -> Response:
    """Генерує та віддає файл зведеної відомості успішності групи у форматі .xlsx або .pdf."""
    resolved_format = _parse_export_format(format)
    service = ExportService(db)
    document = await service.export_group_journal(
        group_id=group_id,
        export_format=resolved_format,
        course_id=course_id,
    )
    return Response(
        content=document.content,
        media_type=document.media_type,
        headers={
            "Content-Disposition": document.content_disposition,
        },
    )
