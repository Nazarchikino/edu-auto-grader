import re
import uuid
from collections.abc import Iterable, Sequence
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.concurrency import run_in_threadpool

from app.api.deps import ensure_course_owner_or_admin
from app.core.config import settings
from app.core.exceptions import (
    DomainError,
    GradingError,
    InvalidFileFormatError,
    PlagiarismDetectedError,
)
from app.graders.factory import GraderFactory
from app.graders.html_grader import (
    EMPTY_HTML_BODY_ERROR_MESSAGE,
    has_meaningful_html_body,
)
from app.graders.metadata import (
    check_submission_plagiarism,
    compute_submission_hash,
    extract_document_metadata,
)
from app.models.course import CourseSlug, Module, Practical, PracticalFormat
from app.models.progress import Submission
from app.models.user import AcademicGroup, User, UserRole
from app.schemas.course import (
    PracticalTeacherRead,
    PracticalVariant,
    calculate_practical_score_breakdown,
)
from app.schemas.grading import (
    ExtractedMetadata,
    GradingReport,
    GradingRule,
    GradingRulesUpdateRequest,
    PlagiarismCheckResult,
)
from app.schemas.submission import (
    MAX_HTML_CODE_LENGTH,
    ManualGradeUpdateRequest,
    SubmissionRead,
)
from app.services.export_service import XLSX_MEDIA_TYPE, build_content_disposition
from app.services.quiz_service import QuizService, resolve_student_variant
from app.services.retention_service import resolve_submission_file_path

_HTML_EXTENSIONS: frozenset[str] = frozenset({".html", ".htm"})

DOCX_MEDIA_TYPE: str = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
ACCDB_MEDIA_TYPE: str = "application/vnd.ms-access"
HTML_MEDIA_TYPE: str = "text/html; charset=utf-8"

_PRACTICAL_MEDIA_TYPES: dict[PracticalFormat, str] = {
    PracticalFormat.DOCX: DOCX_MEDIA_TYPE,
    PracticalFormat.XLSX: XLSX_MEDIA_TYPE,
    PracticalFormat.ACCDB: ACCDB_MEDIA_TYPE,
    PracticalFormat.HTML: HTML_MEDIA_TYPE,
}

_APOSTROPHE_CHARS: tuple[str, ...] = ("'", "’", "‘", "ʼ", "`", "´")

_UKRAINIAN_FILENAME_TRANSLIT: dict[str, str] = {
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


@dataclass(frozen=True, slots=True)
class SubmissionDownloadPayload:
    """Підготовлений файл або HTML-вміст практичної роботи студента для завантаження."""

    media_type: str
    filename_ascii: str
    filename_utf8: str
    content_disposition: str
    file_path: Path | None = None
    content: bytes | None = None


def _strip_apostrophes(value: str) -> str:
    """Прибирає символи апострофа для формування безпечної назви файлу."""
    cleaned = value
    for char in _APOSTROPHE_CHARS:
        cleaned = cleaned.replace(char, "")
    return cleaned


def _sanitize_utf8_token(raw_value: str, *, fallback: str) -> str:
    """Очищує токен назви файлу, зберігаючи кирилицю/латиницю, цифри та дефіс."""
    cleaned = _strip_apostrophes(raw_value.strip())
    sanitized = re.sub(r"[^\w\-]+", "_", cleaned, flags=re.UNICODE).strip("_")
    return sanitized or fallback


def _sanitize_ascii_token(raw_value: str, *, fallback: str) -> str:
    """Транслітерує та очищує токен назви файлу до безпечного ASCII-рядка."""
    cleaned = _strip_apostrophes(raw_value.strip())
    transliterated = "".join(
        _UKRAINIAN_FILENAME_TRANSLIT.get(ch, ch if ord(ch) < 128 else "_")
        for ch in cleaned
    )
    sanitized = re.sub(r"[^A-Za-z0-9_-]+", "_", transliterated).strip("_")
    return sanitized or fallback


def _build_submission_download_names(submission: Submission) -> tuple[str, str, str]:
    """Формує ASCII/UTF-8 імена та заголовок Content-Disposition для файлу роботи студента."""
    student: User | None = submission.__dict__.get("student")
    group: AcademicGroup | None = (
        student.__dict__.get("group")
        if student is not None and student.group_id is not None
        else None
    )
    practical: Practical | None = submission.__dict__.get("practical")
    module: Module | None = (
        practical.__dict__.get("module") if practical is not None else None
    )
    course = module.__dict__.get("course") if module is not None else None

    if group is not None and group.code.strip():
        group_utf8 = _sanitize_utf8_token(group.code, fallback="без_групи")
        group_ascii = _sanitize_ascii_token(group.code, fallback="no_group")
    else:
        group_utf8 = "без_групи"
        group_ascii = "no_group"

    raw_surname = ""
    if student is not None and student.full_name.strip():
        raw_surname = student.full_name.strip().split()[0]
    surname_utf8 = _sanitize_utf8_token(raw_surname, fallback="студент")
    surname_ascii = _sanitize_ascii_token(raw_surname, fallback="student")

    ext = practical.format_type.value if practical is not None else "bin"
    raw_slug = course.slug.value if course is not None else ext
    slug_token = _sanitize_ascii_token(raw_slug, fallback=ext).lower()
    variant_number = submission.variant_index + 1

    filename_utf8 = f"{group_utf8}_{surname_utf8}_{slug_token}_v{variant_number}.{ext}"
    filename_ascii = f"{group_ascii}_{surname_ascii}_{slug_token}_v{variant_number}.{ext}"
    content_disposition = build_content_disposition(
        filename_ascii=filename_ascii,
        filename_utf8=filename_utf8,
    )
    return filename_ascii, filename_utf8, content_disposition


def _check_files_exist_batch(
    paths: Iterable[str],
    uploads_dir: Path,
) -> set[str]:
    """Пакетно перевіряє фізичну наявність файлів у межах `uploads_dir` (для threadpool).

    Повертає множину вхідних шляхів, що безпечно резолвляться всередину
    `uploads_dir` та існують на диску як звичайні файли.
    """
    existing: set[str] = set()
    seen: set[str] = set()
    for raw_path in paths:
        if not raw_path or not raw_path.strip() or raw_path in seen:
            continue
        seen.add(raw_path)
        resolved = resolve_submission_file_path(raw_path, uploads_dir)
        if resolved is not None and resolved.is_file():
            existing.add(raw_path)
    return existing


def _resolve_existing_submission_file(
    raw_file_path: str | None,
    uploads_dir: Path,
) -> Path | None:
    """Резолвить шлях до файлу здачі в межах `uploads_dir` та перевіряє наявність на диску."""
    resolved = resolve_submission_file_path(raw_file_path, uploads_dir)
    if resolved is None or not resolved.is_file():
        return None
    return resolved


def _save_uploaded_file(
    *,
    uploads_dir: Path,
    practical_id: uuid.UUID,
    student_id: uuid.UUID,
    submission_id: uuid.UUID,
    expected_suffix: str,
    file_bytes: bytes,
) -> tuple[Path, str]:
    """Зберігає завантажений файл практичної на диск та обчислює його SHA-256 хеш."""
    target_dir = uploads_dir / str(practical_id) / str(student_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    saved_path = target_dir / f"{submission_id}{expected_suffix}"
    saved_path.write_bytes(file_bytes)
    try:
        file_hash = compute_submission_hash(file_path=saved_path)
    except Exception:
        saved_path.unlink(missing_ok=True)
        raise
    return saved_path, file_hash


def _unlink_file_quietly(path: Path) -> None:
    """Видаляє файл із диска без помилки, якщо він уже відсутній."""
    path.unlink(missing_ok=True)


def _is_submission_file_available(
    submission: Submission,
    *,
    format_type: PracticalFormat | None,
    uploads_dir: Path,
    existing_file_paths: AbstractSet[str] | None = None,
) -> bool:
    """Перевіряє фізичну наявність файлу здачі в UPLOADS_DIR або непорожнього raw_code."""
    if format_type == PracticalFormat.HTML:
        return bool(submission.raw_code and submission.raw_code.strip())
    if format_type is not None:
        if submission.file_path is None:
            return False
        if existing_file_paths is not None:
            return submission.file_path in existing_file_paths
        resolved = resolve_submission_file_path(submission.file_path, uploads_dir)
        return resolved is not None and resolved.is_file()
    if submission.file_path is not None:
        if existing_file_paths is not None:
            return submission.file_path in existing_file_paths
        resolved = resolve_submission_file_path(submission.file_path, uploads_dir)
        return resolved is not None and resolved.is_file()
    return bool(submission.raw_code and submission.raw_code.strip())


def serialize_practical_teacher(practical: Practical) -> PracticalTeacherRead:
    """Перетворює ORM-модель Practical у повну схему PracticalTeacherRead для викладача."""
    variants = [PracticalVariant.model_validate(item) for item in practical.variants]
    grading_rules = [GradingRule.model_validate(item) for item in practical.grading_rules]
    return PracticalTeacherRead(
        id=practical.id,
        module_id=practical.module_id,
        title=practical.title,
        instructions=practical.instructions,
        format_type=practical.format_type,
        max_score=float(practical.max_score),
        needs_rules_review=practical.needs_rules_review,
        variants=variants,
        grading_rules=grading_rules,
    )


def serialize_submission(
    submission: Submission,
    *,
    uploads_dir: Path | None = None,
    retention_days: int | None = None,
    existing_file_paths: AbstractSet[str] | None = None,
) -> SubmissionRead:
    """Перетворює ORM-модель Submission зі зв'язаними сутностями у контракт SubmissionRead."""
    practical: Practical | None = submission.__dict__.get("practical")
    student: User | None = submission.__dict__.get("student")

    practical_title: str | None = None
    course_slug: CourseSlug | None = None
    format_type: PracticalFormat | None = None
    max_score: float = 12.0

    if practical is not None:
        practical_title = practical.title
        format_type = practical.format_type
        max_score = float(practical.max_score)
        module: Module | None = practical.__dict__.get("module")
        if module is not None:
            course = module.__dict__.get("course")
            if course is not None:
                course_slug = course.slug

    student_full_name: str | None = student.full_name if student is not None else None
    extracted_metadata = ExtractedMetadata.model_validate(submission.extracted_metadata)
    grading_report = GradingReport.model_validate(submission.grading_report)

    if grading_report.results:
        rule_points_source: list[Decimal | float] = [
            criterion.max_points for criterion in grading_report.results
        ]
    elif practical is not None and practical.grading_rules:
        rule_points_source = [
            GradingRule.model_validate(item).points for item in practical.grading_rules
        ]
    else:
        rule_points_source = [grading_report.max_points]

    auto_max_dec, manual_bonus_dec = calculate_practical_score_breakdown(
        max_score,
        rule_points_source,
    )

    effective_uploads_dir = (
        uploads_dir if uploads_dir is not None else settings.UPLOADS_DIR
    )
    effective_retention_days = (
        retention_days
        if retention_days is not None
        else settings.SUBMISSION_FILE_RETENTION_DAYS
    )
    is_file_available = _is_submission_file_available(
        submission,
        format_type=format_type,
        uploads_dir=effective_uploads_dir,
        existing_file_paths=existing_file_paths,
    )
    file_expires_at: datetime | None = (
        submission.submitted_at + timedelta(days=effective_retention_days)
        if is_file_available
        else None
    )

    return SubmissionRead(
        id=submission.id,
        practical_id=submission.practical_id,
        practical_title=practical_title,
        course_slug=course_slug,
        student_id=submission.student_id,
        student_full_name=student_full_name,
        variant_index=submission.variant_index,
        variant_number=submission.variant_index + 1,
        file_path=submission.file_path,
        raw_code=submission.raw_code,
        file_hash=submission.file_hash,
        extracted_metadata=extracted_metadata,
        is_plagiarism_flagged=submission.is_plagiarism_flagged,
        plagiarism_reason=submission.plagiarism_reason,
        auto_score=float(submission.auto_score),
        final_score=float(submission.final_score),
        max_score=max_score,
        auto_max_score=round(float(auto_max_dec), 2),
        manual_bonus_max=round(float(manual_bonus_dec), 2),
        grading_report=grading_report,
        teacher_comment=submission.teacher_comment,
        submitted_at=submission.submitted_at,
        is_file_available=is_file_available,
        file_expires_at=file_expires_at,
    )


class SubmissionService:
    """Сервіс оркестрації здачі практичних робіт, автоперевірки, антиплагіату та оцінювання."""

    def __init__(
        self,
        db: AsyncSession,
        *,
        uploads_dir: Path | None = None,
    ) -> None:
        self._db = db
        self._quiz_service = QuizService(db)
        self._uploads_dir = uploads_dir if uploads_dir is not None else settings.UPLOADS_DIR

    async def _load_practical_or_404(self, practical_id: uuid.UUID) -> Practical:
        """Завантажує практичну роботу разом із модулем та курсом або генерує 404."""
        stmt = (
            select(Practical)
            .options(
                selectinload(Practical.module).selectinload(Module.course),
            )
            .where(Practical.id == practical_id)
        )
        result = await self._db.execute(stmt)
        practical = result.scalar_one_or_none()
        if practical is None:
            raise DomainError(
                "Практичну роботу не знайдено.",
                code="PRACTICAL_NOT_FOUND",
                status_code=404,
                context={"practical_id": str(practical_id)},
            )
        return practical

    async def _load_submission_or_404(self, submission_id: uuid.UUID) -> Submission:
        """Завантажує здачу практичної роботи зі зв'язаними практичною, курсом і студентом."""
        stmt = (
            select(Submission)
            .options(
                selectinload(Submission.practical)
                .selectinload(Practical.module)
                .selectinload(Module.course),
                selectinload(Submission.student).selectinload(User.group),
            )
            .where(Submission.id == submission_id)
            .execution_options(populate_existing=True)
        )
        result = await self._db.execute(stmt)
        submission = result.scalar_one_or_none()
        if submission is None:
            raise DomainError(
                "Здачу практичної роботи не знайдено.",
                code="SUBMISSION_NOT_FOUND",
                status_code=404,
                context={"submission_id": str(submission_id)},
            )
        return submission

    async def _check_submission_files_batch(
        self,
        submissions: Sequence[Submission],
    ) -> set[str]:
        """Пакетно перевіряє фізичну наявність файлів для списку здач у threadpool."""
        unique_paths = {
            item.file_path
            for item in submissions
            if item.file_path is not None and item.file_path.strip()
        }
        if not unique_paths:
            return set()
        return await run_in_threadpool(
            _check_files_exist_batch,
            unique_paths,
            self._uploads_dir,
        )

    async def _evaluate_html_submission(
        self,
        *,
        format_type: PracticalFormat,
        rules: list[GradingRule],
        variant_data: dict[str, object],
        raw_code: str | None,
        file_bytes: bytes | None,
        filename: str | None,
    ) -> tuple[str, str, ExtractedMetadata, GradingReport]:
        """Виконує перевірку HTML-коду та обчислює його нормалізований SHA-256 хеш у threadpool."""
        resolved_code = raw_code

        if resolved_code is None and file_bytes is not None:
            safe_filename = (filename or "").strip()
            actual_suffix = Path(safe_filename).suffix.lower()
            if actual_suffix not in _HTML_EXTENSIONS:
                raise InvalidFileFormatError(
                    f"Непідтримуване розширення файлу '{actual_suffix or 'невідоме'}' "
                    "для HTML-практичної роботи. Очікується '.html' або JSON із 'raw_code'.",
                    context={
                        "expected_format": format_type.value,
                        "actual_suffix": actual_suffix,
                        "file_name": safe_filename,
                    },
                )
            try:
                resolved_code = file_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise InvalidFileFormatError(
                    "Завантажений HTML-файл має некоректне кодування (очікується UTF-8).",
                    context={"file_name": safe_filename},
                ) from exc

        if resolved_code is None or not resolved_code.strip():
            raise InvalidFileFormatError(
                "Для здачі HTML-практичної роботи необхідно передати непорожній вихідний код.",
                context={"format_type": format_type.value},
            )

        if len(resolved_code) > MAX_HTML_CODE_LENGTH:
            raise DomainError(
                "Довжина вихідного HTML-коду перевищує максимально допустимі "
                f"{MAX_HTML_CODE_LENGTH} символів.",
                code="RAW_CODE_TOO_LONG",
                status_code=422,
                context={"max_length": MAX_HTML_CODE_LENGTH},
            )

        if not await run_in_threadpool(has_meaningful_html_body, resolved_code):
            raise GradingError(
                EMPTY_HTML_BODY_ERROR_MESSAGE,
                code="EMPTY_HTML_BODY",
                status_code=422,
                context={"format_type": format_type.value},
            )

        file_hash = await run_in_threadpool(
            compute_submission_hash,
            raw_code=resolved_code,
        )
        extracted_metadata = await run_in_threadpool(
            extract_document_metadata,
            raw_code=resolved_code,
        )
        grader = GraderFactory.get_grader(format_type)
        report = await run_in_threadpool(
            grader.evaluate,
            raw_code=resolved_code,
            rules=rules,
            variant_data=variant_data,
        )
        return resolved_code, file_hash, extracted_metadata, report

    async def _evaluate_file_submission(
        self,
        *,
        submission_id: uuid.UUID,
        student_id: uuid.UUID,
        practical_id: uuid.UUID,
        format_type: PracticalFormat,
        rules: list[GradingRule],
        variant_data: dict[str, object],
        file_bytes: bytes | None,
        filename: str | None,
    ) -> tuple[Path, str, ExtractedMetadata, GradingReport]:
        """Зберігає файл (.docx/.xlsx/.accdb), витягує метадані та запускає парсер у threadpool."""
        if file_bytes is None:
            raise InvalidFileFormatError(
                f"Для практичної роботи формату '.{format_type.value}' "
                "необхідно завантажити файл.",
                context={"expected_format": format_type.value},
            )

        safe_filename = (filename or "").strip()
        expected_suffix = f".{format_type.value}"
        actual_suffix = Path(safe_filename).suffix.lower()
        if actual_suffix != expected_suffix:
            raise InvalidFileFormatError(
                f"Непідтримуване розширення файлу '{actual_suffix or 'невідоме'}'. "
                f"Очікується '{expected_suffix}'.",
                context={
                    "expected_suffix": expected_suffix,
                    "actual_suffix": actual_suffix,
                    "file_name": safe_filename,
                },
            )

        if len(file_bytes) == 0:
            raise InvalidFileFormatError(
                f"Завантажений файл '{safe_filename}' порожній.",
                context={
                    "expected_suffix": expected_suffix,
                    "file_name": safe_filename,
                },
            )

        saved_path, file_hash = await run_in_threadpool(
            _save_uploaded_file,
            uploads_dir=self._uploads_dir,
            practical_id=practical_id,
            student_id=student_id,
            submission_id=submission_id,
            expected_suffix=expected_suffix,
            file_bytes=file_bytes,
        )

        try:
            extracted_metadata = await run_in_threadpool(
                extract_document_metadata,
                saved_path,
            )
            grader = GraderFactory.get_grader(format_type)
            report = await run_in_threadpool(
                grader.evaluate,
                file_path=saved_path,
                rules=rules,
                variant_data=variant_data,
            )
        except Exception:
            await run_in_threadpool(_unlink_file_quietly, saved_path)
            raise

        return saved_path, file_hash, extracted_metadata, report

    async def _check_plagiarism(
        self,
        *,
        practical: Practical,
        student_id: uuid.UUID,
        file_hash: str | None,
        extracted_metadata: ExtractedMetadata,
    ) -> PlagiarismCheckResult:
        """Перевіряє здачу на академічну доброчесність з урахуванням відбитків та варіантів."""
        return await check_submission_plagiarism(
            self._db,
            practical_id=practical.id,
            student_id=student_id,
            file_hash=file_hash,
            metadata=extracted_metadata,
            variants_count=len(practical.variants),
            format_type=practical.format_type,
        )

    async def submit_practical(
        self,
        *,
        student: User,
        practical_id: uuid.UUID,
        file_bytes: bytes | None = None,
        filename: str | None = None,
        raw_code: str | None = None,
        payload_error: DomainError | None = None,
        reject_on_plagiarism: bool = False,
    ) -> SubmissionRead:
        """Оркеструє перевірку допуску, оцінювання роботи, антиплагіат та збереження здачі."""
        practical = await self._load_practical_or_404(practical_id)

        await self._quiz_service.ensure_quiz_passed(
            student_id=student.id,
            module_id=practical.module_id,
        )

        if payload_error is not None:
            raise payload_error

        variant_index, _variant_number, variant = resolve_student_variant(
            practical=practical,
            list_number=student.list_number,
        )
        variant_data: dict[str, object] = {
            **variant.model_dump(mode="python"),
            **variant.parameters,
        }
        rules = [GradingRule.model_validate(item) for item in practical.grading_rules]

        submission_id = uuid.uuid4()
        saved_path: Path | None = None
        stored_file_path: str | None = None
        stored_raw_code: str | None = None

        if practical.format_type == PracticalFormat.HTML:
            (
                stored_raw_code,
                file_hash,
                extracted_metadata,
                report,
            ) = await self._evaluate_html_submission(
                format_type=practical.format_type,
                rules=rules,
                variant_data=variant_data,
                raw_code=raw_code,
                file_bytes=file_bytes,
                filename=filename,
            )
        else:
            (
                saved_path,
                file_hash,
                extracted_metadata,
                report,
            ) = await self._evaluate_file_submission(
                submission_id=submission_id,
                student_id=student.id,
                practical_id=practical.id,
                format_type=practical.format_type,
                rules=rules,
                variant_data=variant_data,
                file_bytes=file_bytes,
                filename=filename,
            )
            stored_file_path = saved_path.as_posix()

        plagiarism_result = await self._check_plagiarism(
            practical=practical,
            student_id=student.id,
            file_hash=file_hash,
            extracted_metadata=extracted_metadata,
        )

        if reject_on_plagiarism and plagiarism_result.is_flagged:
            if saved_path is not None:
                await run_in_threadpool(_unlink_file_quietly, saved_path)
            raise PlagiarismDetectedError(
                plagiarism_result.reason
                or "Виявлено збіг вмісту, хешу або метаданих роботи з іншим студентом.",
                context={
                    "practical_id": str(practical.id),
                    "matched_submission_id": (
                        str(plagiarism_result.matched_submission_id)
                        if plagiarism_result.matched_submission_id is not None
                        else None
                    ),
                    "matched_student_id": (
                        str(plagiarism_result.matched_student_id)
                        if plagiarism_result.matched_student_id is not None
                        else None
                    ),
                },
            )

        raw_auto_score = Decimal(str(report.total_points)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        auto_score = min(raw_auto_score, practical.max_score)
        final_score = auto_score

        submission = Submission(
            id=submission_id,
            practical_id=practical.id,
            student_id=student.id,
            variant_index=variant_index,
            file_path=stored_file_path,
            raw_code=stored_raw_code,
            file_hash=file_hash,
            extracted_metadata=extracted_metadata.model_dump(
                mode="json",
                exclude_none=True,
            ),
            is_plagiarism_flagged=plagiarism_result.is_flagged,
            plagiarism_reason=plagiarism_result.reason,
            auto_score=auto_score,
            final_score=final_score,
            grading_report=report.model_dump(mode="json"),
            teacher_comment=None,
        )
        self._db.add(submission)
        await self._db.commit()

        loaded_submission = await self._load_submission_or_404(submission.id)
        existing_file_paths = await self._check_submission_files_batch(
            [loaded_submission]
        )
        return serialize_submission(
            loaded_submission,
            uploads_dir=self._uploads_dir,
            existing_file_paths=existing_file_paths,
        )

    async def update_grading_rules(
        self,
        *,
        practical_id: uuid.UUID,
        payload: GradingRulesUpdateRequest,
        requester: User,
    ) -> PracticalTeacherRead:
        """Оновлює JSONB-правила автоперевірки практичної роботи з валідацією сумісності."""
        practical = await self._load_practical_or_404(practical_id)
        ensure_course_owner_or_admin(
            practical.module.course,
            requester,
            context={"practical_id": str(practical_id)},
        )
        expected_prefix = f"{practical.format_type.value}_"
        grader = GraderFactory.get_grader(practical.format_type)

        seen_rule_ids: set[str] = set()
        for rule in payload.grading_rules:
            if rule.id in seen_rule_ids:
                raise DomainError(
                    f"Дублікат ідентифікатора правила автоперевірки: '{rule.id}'.",
                    code="DUPLICATE_RULE_ID",
                    status_code=422,
                    context={"rule_id": rule.id, "practical_id": str(practical.id)},
                )
            seen_rule_ids.add(rule.id)

            if not rule.type.value.startswith(expected_prefix):
                raise DomainError(
                    f"Правило '{rule.id}' типу '{rule.type.value}' не сумісне з форматом "
                    f"практичної роботи '{practical.format_type.value}'.",
                    code="INVALID_RULE_TYPE_FOR_FORMAT",
                    status_code=422,
                    context={
                        "rule_id": rule.id,
                        "rule_type": rule.type.value,
                        "format_type": practical.format_type.value,
                    },
                )

            try:
                grader.validate_rule_definition(rule)
            except GradingError as exc:
                context = dict(exc.context)
                context.setdefault("rule_id", rule.id)
                context["practical_id"] = str(practical.id)
                detail = (
                    exc.detail
                    if rule.id in exc.detail
                    else f"Некоректне правило '{rule.id}': {exc.detail}"
                )
                raise GradingError(
                    detail,
                    code=exc.code if exc.code != "GRADING_ERROR" else "INVALID_RULE_DEFINITION",
                    status_code=422,
                    context=context,
                ) from exc

        total_points = sum(rule.points for rule in payload.grading_rules)
        practical.grading_rules = [
            rule.model_dump(mode="json") for rule in payload.grading_rules
        ]
        if payload.sync_max_score:
            practical.max_score = Decimal(str(round(total_points, 2))).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        practical.needs_rules_review = (
            payload.needs_rules_review
            if payload.needs_rules_review is not None
            else False
        )

        await self._db.commit()
        await self._db.refresh(practical)
        return serialize_practical_teacher(practical)

    async def update_manual_grade(
        self,
        *,
        submission_id: uuid.UUID,
        payload: ManualGradeUpdateRequest,
        requester: User,
    ) -> SubmissionRead:
        """Виконує ручне коригування оцінки та коментаря викладача для здачі студента."""
        submission = await self._load_submission_or_404(submission_id)
        ensure_course_owner_or_admin(
            submission.practical.module.course,
            requester,
            code="FORBIDDEN_SUBMISSION_GRADING",
            context={"submission_id": str(submission_id)},
        )
        max_score = submission.practical.max_score

        if payload.teacher_score_adjustment is not None:
            adjustment_decimal = Decimal(str(payload.teacher_score_adjustment)).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
            final_score_decimal = (submission.auto_score + adjustment_decimal).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        else:
            if payload.final_score is None:
                raise DomainError(
                    "Необхідно передати 'final_score' або 'teacher_score_adjustment'.",
                    code="INVALID_GRADE_UPDATE",
                    status_code=422,
                    context={"submission_id": str(submission_id)},
                )
            final_score_decimal = Decimal(str(payload.final_score)).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

        if final_score_decimal < Decimal("0.00"):
            raise DomainError(
                f"Підсумковий бал ({final_score_decimal}) не може бути меншим за 0.00.",
                code="SCORE_BELOW_ZERO",
                status_code=422,
                context={
                    "final_score": float(final_score_decimal),
                    "min_score": 0.0,
                    "submission_id": str(submission_id),
                },
            )

        if final_score_decimal > max_score:
            raise DomainError(
                f"Підсумковий бал ({final_score_decimal}) не може перевищувати "
                f"максимальний бал практичної роботи ({max_score}).",
                code="SCORE_EXCEEDS_MAX",
                status_code=422,
                context={
                    "final_score": float(final_score_decimal),
                    "max_score": float(max_score),
                    "submission_id": str(submission_id),
                },
            )

        submission.final_score = final_score_decimal
        submission.teacher_comment = payload.teacher_comment

        await self._db.commit()
        refreshed = await self._load_submission_or_404(submission.id)
        existing_file_paths = await self._check_submission_files_batch([refreshed])
        return serialize_submission(
            refreshed,
            uploads_dir=self._uploads_dir,
            existing_file_paths=existing_file_paths,
        )

    async def prepare_submission_download(
        self,
        *,
        submission_id: uuid.UUID,
        requester: User,
    ) -> SubmissionDownloadPayload:
        """Перевіряє права доступу та готує файл або HTML-код здачі для завантаження викладачем."""
        if requester.role not in (UserRole.ADMIN, UserRole.TEACHER):
            raise DomainError(
                "Завантаження робіт студентів дозволено лише викладачам та адміністраторам.",
                code="FORBIDDEN_SUBMISSION_DOWNLOAD",
                status_code=403,
                context={"submission_id": str(submission_id)},
            )

        submission = await self._load_submission_or_404(submission_id)
        practical = submission.practical
        ensure_course_owner_or_admin(
            practical.module.course,
            requester,
            code="FORBIDDEN_SUBMISSION_DOWNLOAD",
            context={"submission_id": str(submission_id)},
        )

        filename_ascii, filename_utf8, content_disposition = (
            _build_submission_download_names(submission)
        )
        media_type = _PRACTICAL_MEDIA_TYPES[practical.format_type]

        if practical.format_type == PracticalFormat.HTML:
            if submission.raw_code is None or not submission.raw_code.strip():
                raise DomainError(
                    "Файл роботи видалено за терміном зберігання або відсутній на сервері.",
                    code="SUBMISSION_FILE_NOT_FOUND",
                    status_code=404,
                    context={"submission_id": str(submission_id)},
                )
            return SubmissionDownloadPayload(
                media_type=media_type,
                filename_ascii=filename_ascii,
                filename_utf8=filename_utf8,
                content_disposition=content_disposition,
                content=submission.raw_code.encode("utf-8"),
            )

        resolved_path = await run_in_threadpool(
            _resolve_existing_submission_file,
            submission.file_path,
            self._uploads_dir,
        )
        if resolved_path is None:
            raise DomainError(
                "Файл роботи видалено за терміном зберігання або відсутній на сервері.",
                code="SUBMISSION_FILE_NOT_FOUND",
                status_code=404,
                context={"submission_id": str(submission_id)},
            )

        return SubmissionDownloadPayload(
            media_type=media_type,
            filename_ascii=filename_ascii,
            filename_utf8=filename_utf8,
            content_disposition=content_disposition,
            file_path=resolved_path,
        )

    async def get_submission(
        self,
        *,
        submission_id: uuid.UUID,
        requester: User,
    ) -> SubmissionRead:
        """Повертає деталі здачі з перевіркою власника здачі (студент) або курсу (викладач)."""
        submission = await self._load_submission_or_404(submission_id)
        if requester.role == UserRole.STUDENT:
            if submission.student_id != requester.id:
                raise DomainError(
                    "Доступ до чужої здачі практичної роботи заборонено.",
                    code="FORBIDDEN_SUBMISSION_ACCESS",
                    status_code=403,
                    context={"submission_id": str(submission_id)},
                )
        else:
            ensure_course_owner_or_admin(
                submission.practical.module.course,
                requester,
                code="FORBIDDEN_SUBMISSION_ACCESS",
                context={"submission_id": str(submission_id)},
            )
        existing_file_paths = await self._check_submission_files_batch([submission])
        return serialize_submission(
            submission,
            uploads_dir=self._uploads_dir,
            existing_file_paths=existing_file_paths,
        )

    async def list_submissions(
        self,
        *,
        requester: User,
        practical_id: uuid.UUID | None = None,
        student_id: uuid.UUID | None = None,
        group_id: uuid.UUID | None = None,
        plagiarism_only: bool = False,
    ) -> list[SubmissionRead]:
        """Повертає список здач практичних робіт із фільтрацією за роллю та параметрами."""
        stmt = (
            select(Submission)
            .options(
                selectinload(Submission.practical)
                .selectinload(Practical.module)
                .selectinload(Module.course),
                selectinload(Submission.student),
            )
            .order_by(Submission.submitted_at.desc())
        )

        if requester.role == UserRole.STUDENT:
            stmt = stmt.where(Submission.student_id == requester.id)
        else:
            if student_id is not None:
                stmt = stmt.where(Submission.student_id == student_id)
            if group_id is not None:
                stmt = stmt.join(User, Submission.student_id == User.id).where(
                    User.group_id == group_id
                )

        if practical_id is not None:
            stmt = stmt.where(Submission.practical_id == practical_id)
        if plagiarism_only:
            stmt = stmt.where(Submission.is_plagiarism_flagged.is_(True))

        result = await self._db.execute(stmt)
        submissions = list(result.scalars().all())
        existing_file_paths = await self._check_submission_files_batch(submissions)
        return [
            serialize_submission(
                item,
                uploads_dir=self._uploads_dir,
                existing_file_paths=existing_file_paths,
            )
            for item in submissions
        ]


__all__ = [
    "ACCDB_MEDIA_TYPE",
    "DOCX_MEDIA_TYPE",
    "HTML_MEDIA_TYPE",
    "SubmissionDownloadPayload",
    "SubmissionService",
    "serialize_practical_teacher",
    "serialize_submission",
]
