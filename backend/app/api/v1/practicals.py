import json
import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.api.deps import get_db, require_role
from app.core.config import settings
from app.core.exceptions import DomainError, InvalidFileFormatError
from app.core.upload_utils import read_upload_file_limited
from app.models.course import Practical, PracticalFormat
from app.models.user import User, UserRole
from app.schemas.course import PracticalTeacherRead
from app.schemas.grading import GradingRule, GradingRulesUpdateRequest
from app.schemas.submission import (
    MAX_HTML_CODE_LENGTH,
    DryRunGradingResponse,
    HtmlDryRunRequest,
    HtmlSubmissionRequest,
    SubmissionRead,
)
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


@dataclass(frozen=True, slots=True)
class ExtractedDryRunPayload:
    """Розібраний вміст HTTP-запиту на тестову (dry-run) перевірку правил практичної."""

    file_bytes: bytes | None = None
    filename: str | None = None
    raw_code: str | None = None
    variant_number: int = 1
    rules_override: list[GradingRule] | None = None
    payload_error: DomainError | None = None


def _parse_rules_json_field(raw_rules_json: str) -> list[GradingRule]:
    """Парсить і валідує JSON-рядок поля `rules_json` із multipart-форми dry-run."""
    try:
        parsed_raw: object = json.loads(raw_rules_json)
    except json.JSONDecodeError as exc:
        raise DomainError(
            "Некоректний JSON-формат поля 'rules_json'.",
            code="INVALID_RULES_JSON",
            status_code=422,
            context={"error": str(exc)},
        ) from exc

    if not isinstance(parsed_raw, list) or len(parsed_raw) == 0:
        raise DomainError(
            "Поле 'rules_json' повинно містити непорожній JSON-масив правил перевірки.",
            code="INVALID_RULES_JSON",
            status_code=422,
        )

    validated_rules: list[GradingRule] = []
    for index, item in enumerate(parsed_raw):
        try:
            validated_rules.append(GradingRule.model_validate(item))
        except ValidationError as exc:
            error_messages = [str(err.get("msg", "")) for err in exc.errors()]
            raise DomainError(
                f"Некоректне правило №{index + 1} у полі 'rules_json'.",
                code="INVALID_RULES_JSON",
                status_code=422,
                context={
                    "rule_index": index,
                    "validation_errors": error_messages,
                },
            ) from exc
    return validated_rules


async def _extract_dry_run_payload(
    request: Request,
    *,
    max_upload_bytes: int,
) -> ExtractedDryRunPayload:
    """Витягує дані для dry-run перевірки (multipart/form-data або application/json)."""
    content_type = request.headers.get("content-type", "").lower()

    if "application/json" in content_type:
        try:
            raw_json: object = await request.json()
        except Exception:
            return ExtractedDryRunPayload(
                payload_error=InvalidFileFormatError(
                    "Некоректний JSON-формат запиту на тестову перевірку правил.",
                )
            )

        try:
            parsed = HtmlDryRunRequest.model_validate(raw_json)
        except ValidationError as exc:
            errors = exc.errors()
            error_messages = [str(item.get("msg", "")) for item in errors]
            is_too_long = any(
                item.get("type") == "string_too_long"
                and "raw_code" in item.get("loc", ())
                for item in errors
            )
            if is_too_long:
                raise DomainError(
                    "Довжина вихідного HTML-коду перевищує максимально допустимі "
                    f"{MAX_HTML_CODE_LENGTH} символів.",
                    code="RAW_CODE_TOO_LONG",
                    status_code=422,
                    context={
                        "max_length": MAX_HTML_CODE_LENGTH,
                        "validation_errors": error_messages,
                    },
                ) from exc

            has_rules_or_variant_error = any(
                loc_head in {"rules_override", "variant_number"}
                for item in errors
                for loc_head in (item.get("loc", (None,))[0],)
            )
            if has_rules_or_variant_error:
                raise DomainError(
                    "Некоректні параметри запиту dry-run ('variant_number' або 'rules_override').",
                    code="INVALID_DRY_RUN_PAYLOAD",
                    status_code=422,
                    context={"validation_errors": error_messages},
                ) from exc

            return ExtractedDryRunPayload(
                payload_error=InvalidFileFormatError(
                    "Для dry-run перевірки HTML-роботи необхідно передати "
                    "непорожній рядок 'raw_code'.",
                    context={"validation_errors": error_messages},
                )
            )

        return ExtractedDryRunPayload(
            raw_code=parsed.raw_code,
            variant_number=parsed.variant_number,
            rules_override=parsed.rules_override,
        )

    if (
        "multipart/form-data" in content_type
        or "application/x-www-form-urlencoded" in content_type
    ):
        form = await request.form()
        try:
            uploaded_file = form.get("file")
            raw_code_field = form.get("raw_code")
            variant_field = form.get("variant_number")
            rules_json_field = form.get("rules_json")

            variant_number = 1
            if isinstance(variant_field, str) and variant_field.strip():
                try:
                    variant_number = int(variant_field.strip())
                except ValueError as exc:
                    raise DomainError(
                        "Поле 'variant_number' повинно бути цілим числом (>= 1).",
                        code="INVALID_VARIANT_NUMBER",
                        status_code=422,
                        context={"variant_number": variant_field},
                    ) from exc

            rules_override: list[GradingRule] | None = None
            if isinstance(rules_json_field, str) and rules_json_field.strip():
                rules_override = _parse_rules_json_field(rules_json_field.strip())

            file_bytes: bytes | None = None
            filename: str | None = None
            if isinstance(uploaded_file, StarletteUploadFile):
                filename = uploaded_file.filename or ""
                file_bytes = await read_upload_file_limited(
                    uploaded_file,
                    max_bytes=max_upload_bytes,
                )

            raw_code: str | None = (
                raw_code_field if isinstance(raw_code_field, str) else None
            )
            if raw_code is not None and len(raw_code) > MAX_HTML_CODE_LENGTH:
                raise DomainError(
                    "Довжина вихідного HTML-коду перевищує максимально допустимі "
                    f"{MAX_HTML_CODE_LENGTH} символів.",
                    code="RAW_CODE_TOO_LONG",
                    status_code=422,
                    context={"max_length": MAX_HTML_CODE_LENGTH},
                )

            return ExtractedDryRunPayload(
                file_bytes=file_bytes,
                filename=filename,
                raw_code=raw_code,
                variant_number=variant_number,
                rules_override=rules_override,
            )
        finally:
            await form.close()

    return ExtractedDryRunPayload(
        payload_error=InvalidFileFormatError(
            "Підтримуються лише запити multipart/form-data (файл) "
            "або application/json (raw_code).",
            context={"content_type": content_type},
        )
    )


async def _resolve_practical_upload_limit(
    db: AsyncSession,
    practical_id: uuid.UUID,
) -> int:
    """Обирає максимально допустимий розмір файлу залежно від формату практичної."""
    result = await db.execute(
        select(Practical.format_type).where(Practical.id == practical_id)
    )
    format_type = result.scalar_one_or_none()
    if format_type == PracticalFormat.ACCDB:
        return settings.MAX_ACCDB_UPLOAD_BYTES
    return settings.MAX_OFFICE_UPLOAD_BYTES


async def _extract_submission_payload(
    request: Request,
    *,
    max_upload_bytes: int,
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
            is_too_long = any(
                item.get("type") == "string_too_long" for item in exc.errors()
            )
            if is_too_long:
                raise DomainError(
                    "Довжина вихідного HTML-коду перевищує максимально допустимі "
                    f"{MAX_HTML_CODE_LENGTH} символів.",
                    code="RAW_CODE_TOO_LONG",
                    status_code=422,
                    context={
                        "max_length": MAX_HTML_CODE_LENGTH,
                        "validation_errors": error_messages,
                    },
                ) from exc
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
        try:
            uploaded_file = form.get("file")
            raw_code_field = form.get("raw_code")

            file_bytes: bytes | None = None
            filename: str | None = None
            if isinstance(uploaded_file, StarletteUploadFile):
                filename = uploaded_file.filename or ""
                file_bytes = await read_upload_file_limited(
                    uploaded_file,
                    max_bytes=max_upload_bytes,
                )

            raw_code: str | None = (
                raw_code_field if isinstance(raw_code_field, str) else None
            )
            if raw_code is not None and len(raw_code) > MAX_HTML_CODE_LENGTH:
                raise DomainError(
                    "Довжина вихідного HTML-коду перевищує максимально допустимі "
                    f"{MAX_HTML_CODE_LENGTH} символів.",
                    code="RAW_CODE_TOO_LONG",
                    status_code=422,
                    context={"max_length": MAX_HTML_CODE_LENGTH},
                )
            return ExtractedSubmissionPayload(
                file_bytes=file_bytes,
                filename=filename,
                raw_code=raw_code,
            )
        finally:
            await form.close()

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
                                "maxLength": MAX_HTML_CODE_LENGTH,
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
                                "maxLength": MAX_HTML_CODE_LENGTH,
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
    max_upload_bytes = await _resolve_practical_upload_limit(db, practical_id)
    extracted = await _extract_submission_payload(
        request,
        max_upload_bytes=max_upload_bytes,
    )
    service = SubmissionService(db)
    return await service.submit_practical(
        student=current_user,
        practical_id=practical_id,
        file_bytes=extracted.file_bytes,
        filename=extracted.filename,
        raw_code=extracted.raw_code,
        payload_error=extracted.payload_error,
    )


@router.post(
    "/practicals/{practical_id}/dry-run",
    response_model=DryRunGradingResponse,
    status_code=status.HTTP_200_OK,
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
                                "description": (
                                    "Тестовий файл практичної роботи (.docx, .xlsx, .accdb)"
                                ),
                            },
                            "variant_number": {
                                "type": "integer",
                                "minimum": 1,
                                "default": 1,
                                "description": "Номер індивідуального варіанта (1..N)",
                            },
                            "rules_json": {
                                "type": "string",
                                "description": "Опційний JSON-масив чернеткових правил перевірки",
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
                                "maxLength": MAX_HTML_CODE_LENGTH,
                                "description": "Тестовий HTML5-код",
                            },
                            "variant_number": {
                                "type": "integer",
                                "minimum": 1,
                                "default": 1,
                                "description": "Номер індивідуального варіанта (1..N)",
                            },
                            "rules_override": {
                                "type": "array",
                                "items": {"type": "object"},
                                "description": "Опційний масив чернеткових правил перевірки",
                            },
                        },
                    }
                },
            },
        }
    },
)
async def dry_run_practical_work(
    practical_id: uuid.UUID,
    request: Request,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DryRunGradingResponse:
    """Тестово перевіряє роботу за збереженими чи чернетковими правилами без запису в БД."""
    service = SubmissionService(db)
    practical = await service.get_practical_for_dry_run(
        practical_id=practical_id,
        requester=current_user,
    )
    max_upload_bytes = (
        settings.MAX_ACCDB_UPLOAD_BYTES
        if practical.format_type == PracticalFormat.ACCDB
        else settings.MAX_OFFICE_UPLOAD_BYTES
    )
    extracted = await _extract_dry_run_payload(
        request,
        max_upload_bytes=max_upload_bytes,
    )
    return await service.dry_run_practical(
        requester=current_user,
        practical_id=practical_id,
        file_bytes=extracted.file_bytes,
        filename=extracted.filename,
        raw_code=extracted.raw_code,
        variant_number=extracted.variant_number,
        rules_override=extracted.rules_override,
        payload_error=extracted.payload_error,
        loaded_practical=practical,
    )


@router.put(
    "/practicals/{practical_id}/rules",
    response_model=PracticalTeacherRead,
)
async def update_practical_grading_rules(
    practical_id: uuid.UUID,
    payload: GradingRulesUpdateRequest,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PracticalTeacherRead:
    """Оновлює JSONB-правила автоматизованої перевірки практичної роботи (для викладача)."""
    service = SubmissionService(db)
    return await service.update_grading_rules(
        practical_id=practical_id,
        payload=payload,
        requester=current_user,
    )
