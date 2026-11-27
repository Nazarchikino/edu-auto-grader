import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, Response, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.api.deps import ensure_course_owner_or_admin, get_db, require_role
from app.core.config import settings
from app.core.exceptions import DomainError, InvalidFileFormatError
from app.core.upload_utils import read_upload_file_limited
from app.graders.metadata import compute_bytes_sha256, validate_zip_archive_safety
from app.models.course import Module, Practical, PracticalFormat
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
from app.services.export_service import XLSX_MEDIA_TYPE, build_content_disposition
from app.services.retention_service import (
    delete_submission_file_safely_async,
    resolve_submission_file_path,
)
from app.services.submission_service import (
    ACCDB_MEDIA_TYPE,
    DOCX_MEDIA_TYPE,
    SubmissionService,
    serialize_practical_teacher,
)

router = APIRouter(tags=["practicals"])

AllAuthUser = Annotated[
    User,
    Depends(require_role(UserRole.STUDENT, UserRole.TEACHER, UserRole.ADMIN)),
]
StudentUser = Annotated[
    User,
    Depends(require_role(UserRole.STUDENT)),
]
TeacherOrAdminUser = Annotated[
    User,
    Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
]

ALLOWED_TEMPLATE_EXTENSIONS: frozenset[str] = frozenset(
    {".docx", ".xlsx", ".accdb", ".zip", ".txt", ".csv"}
)
ZIP_TEMPLATE_EXTENSIONS: frozenset[str] = frozenset({".docx", ".xlsx", ".zip"})

_TEMPLATE_MEDIA_TYPES: dict[str, str] = {
    ".docx": DOCX_MEDIA_TYPE,
    ".xlsx": XLSX_MEDIA_TYPE,
    ".accdb": ACCDB_MEDIA_TYPE,
    ".zip": "application/zip",
    ".txt": "text/plain; charset=utf-8",
    ".csv": "text/csv; charset=utf-8",
}

_TEMPLATE_ASCII_TRANSLIT: dict[str, str] = {
    "А": "A",
    "Б": "B",
    "В": "V",
    "Г": "H",
    "Ґ": "G",
    "Д": "D",
    "Е": "E",
    "Є": "Ye",
    "Ж": "Zh",
    "З": "Z",
    "И": "Y",
    "І": "I",
    "Ї": "Yi",
    "Й": "Y",
    "К": "K",
    "Л": "L",
    "М": "M",
    "Н": "N",
    "О": "O",
    "П": "P",
    "Р": "R",
    "С": "S",
    "Т": "T",
    "У": "U",
    "Ф": "F",
    "Х": "Kh",
    "Ц": "Ts",
    "Ч": "Ch",
    "Ш": "Sh",
    "Щ": "Shch",
    "Ь": "",
    "Ю": "Yu",
    "Я": "Ya",
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "h",
    "ґ": "g",
    "д": "d",
    "е": "e",
    "є": "ie",
    "ж": "zh",
    "з": "z",
    "и": "y",
    "і": "i",
    "ї": "i",
    "й": "i",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ь": "",
    "ю": "iu",
    "я": "ia",
}


def _sanitize_template_display_name(raw_filename: str, expected_suffix: str) -> str:
    """Очищує оригінальну назву файлу-заготовки від шляхів та керуючих символів."""
    base_name = Path(raw_filename.replace("\\", "/")).name
    cleaned = "".join(
        ch for ch in base_name if ord(ch) >= 32 and ord(ch) != 127
    ).strip()
    if not cleaned or cleaned.lower() == expected_suffix:
        return f"template{expected_suffix}"
    if len(cleaned) > 255:
        stem = Path(cleaned).stem
        max_stem_len = max(1, 255 - len(expected_suffix))
        cleaned = f"{stem[:max_stem_len]}{expected_suffix}"
    return cleaned


def _build_template_content_disposition(
    template_file_name: str | None,
    fallback_suffix: str,
) -> str:
    """Формує RFC 5987 Content-Disposition на основі назви файлу-заготовки."""
    raw_name = (template_file_name or "").strip()
    suffix = Path(raw_name).suffix.lower() or fallback_suffix
    raw_stem = Path(raw_name).stem if raw_name else "template"

    utf8_stem = re.sub(r"[^\w.\-]+", "_", raw_stem, flags=re.UNICODE).strip("._")
    utf8_stem = utf8_stem or "template"
    filename_utf8 = f"{utf8_stem}{suffix}"

    transliterated = "".join(
        _TEMPLATE_ASCII_TRANSLIT.get(ch, ch if ord(ch) < 128 else "_")
        for ch in raw_stem
    )
    ascii_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", transliterated).strip("._")
    ascii_stem = ascii_stem or "template"
    filename_ascii = f"{ascii_stem}{suffix}"

    return build_content_disposition(
        filename_ascii=filename_ascii,
        filename_utf8=filename_utf8,
    )


def _save_template_file(
    *,
    uploads_dir: Path,
    ext_no_dot: str,
    file_bytes: bytes,
) -> tuple[Path, str]:
    """Зберігає файл-заготовку у `UPLOADS_DIR/templates/` і обчислює SHA-256 (для threadpool)."""
    uploads_root = uploads_dir.resolve()
    templates_dir = (uploads_root / "templates").resolve()
    if templates_dir == uploads_root or not templates_dir.is_relative_to(uploads_root):
        raise DomainError(
            "Небезпечний шлях каталогу файлів-заготовок.",
            code="UNSAFE_TEMPLATE_PATH",
            status_code=422,
        )

    stored_filename = f"{uuid.uuid4().hex}.{ext_no_dot}"
    saved_path = (templates_dir / stored_filename).resolve()
    if saved_path.parent != templates_dir or not saved_path.is_relative_to(uploads_root):
        raise DomainError(
            "Небезпечний шлях файлу-заготовки.",
            code="UNSAFE_TEMPLATE_PATH",
            status_code=422,
        )

    templates_dir.mkdir(parents=True, exist_ok=True)
    saved_path.write_bytes(file_bytes)
    try:
        file_hash = compute_bytes_sha256(file_bytes)
    except Exception:
        saved_path.unlink(missing_ok=True)
        raise
    return saved_path, file_hash


def _resolve_existing_template_file(
    raw_file_path: str | None,
    uploads_dir: Path,
) -> Path | None:
    """Резолвить файл-заготовку в межах `UPLOADS_DIR` і перевіряє його наявність на диску."""
    resolved = resolve_submission_file_path(raw_file_path, uploads_dir)
    if resolved is None or not resolved.is_file():
        return None
    return resolved


def _unlink_template_quietly(path: Path) -> None:
    """Видаляє файл-заготовку з диска без помилки при відсутності файлу."""
    path.unlink(missing_ok=True)


async def _load_practical_with_course_or_404(
    db: AsyncSession,
    practical_id: uuid.UUID,
) -> Practical:
    """Завантажує практичну роботу разом із модулем та курсом або повертає 404."""
    stmt = (
        select(Practical)
        .options(selectinload(Practical.module).selectinload(Module.course))
        .where(Practical.id == practical_id)
    )
    result = await db.execute(stmt)
    practical = result.scalar_one_or_none()
    if practical is None:
        raise DomainError(
            "Практичну роботу не знайдено.",
            code="PRACTICAL_NOT_FOUND",
            status_code=404,
            context={"practical_id": str(practical_id)},
        )
    return practical


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


@router.post(
    "/practicals/{practical_id}/template",
    response_model=PracticalTeacherRead,
    status_code=status.HTTP_200_OK,
)
async def upload_practical_template(
    practical_id: uuid.UUID,
    file: Annotated[UploadFile, File(...)],
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PracticalTeacherRead:
    """Прикріплює або замінює файл-заготовку (шаблон) практичної роботи викладачем."""
    practical = await _load_practical_with_course_or_404(db, practical_id)
    ensure_course_owner_or_admin(
        practical.module.course,
        current_user,
        context={"practical_id": str(practical_id)},
    )

    safe_filename = (file.filename or "").strip()
    actual_suffix = Path(safe_filename).suffix.lower()
    if actual_suffix not in ALLOWED_TEMPLATE_EXTENSIONS:
        raise DomainError(
            f"Непідтримуваний формат файлу-заготовки '{actual_suffix or 'невідомий'}'. "
            "Дозволені формати: .docx, .xlsx, .accdb, .zip, .txt, .csv.",
            code="UNSUPPORTED_TEMPLATE_FORMAT",
            status_code=422,
            context={
                "practical_id": str(practical_id),
                "file_name": safe_filename,
                "actual_suffix": actual_suffix,
            },
        )

    max_bytes = (
        settings.MAX_ACCDB_UPLOAD_BYTES
        if actual_suffix == ".accdb"
        else settings.MAX_OFFICE_UPLOAD_BYTES
    )
    file_bytes = await read_upload_file_limited(file, max_bytes=max_bytes)
    if len(file_bytes) == 0:
        raise DomainError(
            f"Завантажений файл-заготовка '{safe_filename}' порожній.",
            code="EMPTY_TEMPLATE_FILE",
            status_code=422,
            context={"practical_id": str(practical_id), "file_name": safe_filename},
        )

    if actual_suffix in ZIP_TEMPLATE_EXTENSIONS:
        try:
            await run_in_threadpool(validate_zip_archive_safety, file_bytes)
        except InvalidFileFormatError as exc:
            raise DomainError(
                exc.detail,
                code="INVALID_TEMPLATE_ARCHIVE",
                status_code=422,
                context={
                    "practical_id": str(practical_id),
                    "file_name": safe_filename,
                },
            ) from exc

    ext_no_dot = actual_suffix.lstrip(".")
    saved_path, file_hash = await run_in_threadpool(
        _save_template_file,
        uploads_dir=settings.UPLOADS_DIR,
        ext_no_dot=ext_no_dot,
        file_bytes=file_bytes,
    )
    display_name = _sanitize_template_display_name(safe_filename, actual_suffix)
    old_template_path = practical.template_file_path

    practical.template_file_path = saved_path.as_posix()
    practical.template_file_name = display_name
    practical.template_file_hash = file_hash

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        await run_in_threadpool(_unlink_template_quietly, saved_path)
        raise

    await db.refresh(practical)

    if (
        old_template_path is not None
        and old_template_path.strip()
        and old_template_path != practical.template_file_path
    ):
        await delete_submission_file_safely_async(
            old_template_path,
            upload_dir=settings.UPLOADS_DIR,
        )

    return serialize_practical_teacher(practical)


@router.delete(
    "/practicals/{practical_id}/template",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_practical_template(
    practical_id: uuid.UUID,
    current_user: TeacherOrAdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Видаляє прикріплений файл-заготовку практичної роботи з БД і диска."""
    practical = await _load_practical_with_course_or_404(db, practical_id)
    ensure_course_owner_or_admin(
        practical.module.course,
        current_user,
        context={"practical_id": str(practical_id)},
    )

    old_template_path = practical.template_file_path
    practical.template_file_path = None
    practical.template_file_name = None
    practical.template_file_hash = None
    await db.commit()

    if old_template_path is not None and old_template_path.strip():
        await delete_submission_file_safely_async(
            old_template_path,
            upload_dir=settings.UPLOADS_DIR,
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/practicals/{practical_id}/template",
    response_class=Response,
)
async def download_practical_template(
    practical_id: uuid.UUID,
    _current_user: AllAuthUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Віддає авторизованому користувачу файл-заготовку (шаблон) практичної роботи."""
    result = await db.execute(select(Practical).where(Practical.id == practical_id))
    practical = result.scalar_one_or_none()
    if practical is None:
        raise DomainError(
            "Практичну роботу не знайдено.",
            code="PRACTICAL_NOT_FOUND",
            status_code=404,
            context={"practical_id": str(practical_id)},
        )

    if practical.template_file_path is None or not practical.template_file_path.strip():
        raise DomainError(
            "Для цієї практичної роботи файл-заготовку не прикріплено.",
            code="TEMPLATE_FILE_NOT_FOUND",
            status_code=404,
            context={"practical_id": str(practical_id)},
        )

    resolved_path = await run_in_threadpool(
        _resolve_existing_template_file,
        practical.template_file_path,
        settings.UPLOADS_DIR,
    )
    if resolved_path is None:
        raise DomainError(
            "Файл-заготовка відсутній на сервері.",
            code="TEMPLATE_FILE_NOT_FOUND",
            status_code=404,
            context={"practical_id": str(practical_id)},
        )

    suffix = resolved_path.suffix.lower()
    media_type = _TEMPLATE_MEDIA_TYPES.get(suffix, "application/octet-stream")
    content_disposition = _build_template_content_disposition(
        practical.template_file_name,
        fallback_suffix=suffix or ".bin",
    )
    return FileResponse(
        path=resolved_path,
        media_type=media_type,
        headers={"Content-Disposition": content_disposition},
    )
