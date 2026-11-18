import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.api.deps import get_db, require_role
from app.core.exceptions import DomainError, InvalidFileFormatError
from app.models.user import User, UserRole
from app.schemas.course import PracticalTeacherRead
from app.schemas.grading import GradingRulesUpdateRequest
from app.schemas.submission import HtmlSubmissionRequest, SubmissionRead
from app.services.submission_service import SubmissionService

router = APIRouter(tags=["practicals"])

StudentUser = Annotated[
    User,
    Depends(require_role(UserRole.STUDENT)),
]
TeacherOrAdminUser = Annotated[
    User,
    Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
]


@dataclass(frozen=True, slots=True)
class ExtractedSubmissionPayload:
    """Розібраний вміст HTTP-запиту на здачу практичної роботи (файл або HTML-код)."""

    file_bytes: bytes | None = None
    filename: str | None = None
    raw_code: str | None = None
    payload_error: DomainError | None = None


async def _extract_submission_payload(
    request: Request,
) -> ExtractedSubmissionPayload:
    """Витягує завантажений файл (multipart/form-data) або HTML-код (application/json)."""
    content_type = request.headers.get("content-type", "").lower()

    if "application/json" in content_type:
        try:
            raw_json: object = await request.json()
        except Exception:
            return ExtractedSubmissionPayload(
                payload_error=InvalidFileFormatError(
                    "Некоректний JSON-формат запиту на здачу практичної роботи.",
                )
            )

        try:
            parsed = HtmlSubmissionRequest.model_validate(raw_json)
        except ValidationError as exc:
            error_messages = [str(item.get("msg", "")) for item in exc.errors()]
            return ExtractedSubmissionPayload(
                payload_error=InvalidFileFormatError(
                    "Для здачі HTML-роботи необхідно передати непорожній рядок 'raw_code'.",
                    context={"validation_errors": error_messages},
                )
            )
        return ExtractedSubmissionPayload(raw_code=parsed.raw_code)

    if (
        "multipart/form-data" in content_type
        or "application/x-www-form-urlencoded" in content_type
    ):
        form = await request.form()
        uploaded_file = form.get("file")
        raw_code_field = form.get("raw_code")

        file_bytes: bytes | None = None
        filename: str | None = None
        if isinstance(uploaded_file, StarletteUploadFile):
            file_bytes = await uploaded_file.read()
            filename = uploaded_file.filename or ""
            await uploaded_file.close()

        raw_code: str | None = (
            raw_code_field if isinstance(raw_code_field, str) else None
        )
        return ExtractedSubmissionPayload(
            file_bytes=file_bytes,
            filename=filename,
            raw_code=raw_code,
        )

    return ExtractedSubmissionPayload(
        payload_error=InvalidFileFormatError(
            "Підтримуються лише запити multipart/form-data (файл) "
            "або application/json (raw_code).",
            context={"content_type": content_type},
        )
    )


@router.post(
    "/practicals/{practical_id}/submit",
    response_model=SubmissionRead,
    status_code=status.HTTP_201_CREATED,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "file": {
                                "type": "string",
                                "format": "binary",
                                "description": "Файл практичної роботи (.docx, .xlsx, .accdb)",
                            },
                            "raw_code": {
                                "type": "string",
                                "description": "Вихідний HTML5-код (опційно через форму)",
                            },
                        },
                    }
                },
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["raw_code"],
                        "properties": {
                            "raw_code": {
                                "type": "string",
                                "minLength": 1,
                                "description": "Вихідний HTML5-код із пісочниці",
                            }
                        },
                    }
                },
            },
        }
    },
)
async def submit_practical_work(
    practical_id: uuid.UUID,
    request: Request,
    current_user: StudentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubmissionRead:
    """Приймає файл або HTML-код студента, виконує миттєву автоперевірку та антиплагіат."""
    extracted = await _extract_submission_payload(request)
    service = SubmissionService(db)
    return await service.submit_practical(
        student=current_user,
        practical_id=practical_id,
        file_bytes=extracted.file_bytes,
        filename=extracted.filename,
        raw_code=extracted.raw_code,
        payload_error=extracted.payload_error,
    )


@router.put(
    "/practicals/{practical_id}/rules",
    response_model=PracticalTeacherRead,
)
async def update_practical_grading_rules(
    practical_id: uuid.UUID,
    payload: GradingRulesUpdateRequest,
    _current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PracticalTeacherRead:
    """Оновлює JSONB-правила автоматизованої перевірки практичної роботи (для викладача)."""
    service = SubmissionService(db)
    return await service.update_grading_rules(
        practical_id=practical_id,
        payload=payload,
    )
