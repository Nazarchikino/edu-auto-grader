import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User, UserRole
from app.schemas.submission import ManualGradeUpdateRequest, SubmissionRead
from app.services.export_service import XLSX_MEDIA_TYPE
from app.services.submission_service import (
    ACCDB_MEDIA_TYPE,
    DOCX_MEDIA_TYPE,
    HTML_MEDIA_TYPE,
    SubmissionService,
)

router = APIRouter(tags=["submissions"])

AuthenticatedUser = Annotated[User, Depends(get_current_user)]
TeacherOrAdminUser = Annotated[
    User,
    Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
]


@router.get("/submissions/me", response_model=list[SubmissionRead])
async def list_my_submissions(
    current_user: AuthenticatedUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    practical_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[SubmissionRead]:
    """Повертає історію здач практичних робіт поточного користувача (залікова книжка)."""
    service = SubmissionService(db)
    return await service.list_submissions(
        requester=current_user,
        practical_id=practical_id,
        student_id=current_user.id,
    )


@router.get("/submissions", response_model=list[SubmissionRead])
async def list_submissions(
    current_user: AuthenticatedUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    practical_id: Annotated[uuid.UUID | None, Query()] = None,
    student_id: Annotated[uuid.UUID | None, Query()] = None,
    group_id: Annotated[uuid.UUID | None, Query()] = None,
    plagiarism_only: Annotated[bool, Query()] = False,
) -> list[SubmissionRead]:
    """Повертає перелік здач практичних робіт із фільтрацією (для викладача або студента)."""
    service = SubmissionService(db)
    return await service.list_submissions(
        requester=current_user,
        practical_id=practical_id,
        student_id=student_id,
        group_id=group_id,
        plagiarism_only=plagiarism_only,
    )


@router.get("/submissions/{submission_id}", response_model=SubmissionRead)
async def get_submission_detail(
    submission_id: uuid.UUID,
    current_user: AuthenticatedUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubmissionRead:
    """Повертає деталізований звіт автоперевірки та статус антиплагіату конкретної здачі."""
    service = SubmissionService(db)
    return await service.get_submission(
        submission_id=submission_id,
        requester=current_user,
    )


@router.get(
    "/submissions/{submission_id}/download",
    response_class=Response,
    responses={
        200: {
            "description": "Файл практичної роботи студента (.docx/.xlsx/.accdb/.html)",
            "content": {
                DOCX_MEDIA_TYPE: {"schema": {"type": "string", "format": "binary"}},
                XLSX_MEDIA_TYPE: {"schema": {"type": "string", "format": "binary"}},
                ACCDB_MEDIA_TYPE: {"schema": {"type": "string", "format": "binary"}},
                HTML_MEDIA_TYPE: {"schema": {"type": "string", "format": "binary"}},
            },
        },
        403: {"description": "Доступ до завантаження роботи заборонено"},
        404: {"description": "Здачу або файл роботи не знайдено"},
    },
)
async def download_submission_file(
    submission_id: uuid.UUID,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Віддає викладачу курсу або адміну файл (.docx/.xlsx/.accdb) чи HTML-код роботи."""
    service = SubmissionService(db)
    payload = await service.prepare_submission_download(
        submission_id=submission_id,
        requester=current_user,
    )
    headers = {"Content-Disposition": payload.content_disposition}
    if payload.file_path is not None:
        return FileResponse(
            path=payload.file_path,
            media_type=payload.media_type,
            headers=headers,
        )
    return Response(
        content=payload.content or b"",
        media_type=payload.media_type,
        headers=headers,
    )


@router.patch("/submissions/{submission_id}/grade", response_model=SubmissionRead)
async def update_submission_grade(
    submission_id: uuid.UUID,
    payload: ManualGradeUpdateRequest,
    _current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubmissionRead:
    """Ручне коригування підсумкового бала та додавання коментаря викладача."""
    service = SubmissionService(db)
    return await service.update_manual_grade(
        submission_id=submission_id,
        payload=payload,
    )
