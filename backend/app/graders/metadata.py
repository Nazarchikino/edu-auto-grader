import hashlib
import io
import uuid
import zipfile
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol
from xml.etree.ElementTree import Element as XmlElement

from defusedxml import DefusedXmlException
from defusedxml import ElementTree as DefusedET
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import GradingError, InvalidFileFormatError
from app.models.progress import Submission
from app.schemas.grading import ExtractedMetadata, PlagiarismCheckResult

CORE_XML_ARCHIVE_PATH = "docProps/core.xml"
OPENXML_EXTENSIONS: frozenset[str] = frozenset({".docx", ".xlsx"})
_HASH_CHUNK_SIZE = 65536
_MIN_ENTRY_BYTES_FOR_RATIO_CHECK = 1_048_576

_CORE_XML_NAMESPACES: dict[str, str] = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
}


class SubmissionRecordProtocol(Protocol):
    """Структурний контракт попередньої здачі для перевірки на академічну доброчесність."""

    @property
    def id(self) -> uuid.UUID: ...

    @property
    def student_id(self) -> uuid.UUID: ...

    @property
    def file_hash(self) -> str | None: ...

    @property
    def extracted_metadata(self) -> dict[str, object] | ExtractedMetadata: ...


def compute_bytes_sha256(data: bytes) -> str:
    """Обчислює SHA-256 хеш (64 hex-символи у нижньому регістрі) для масиву байтів."""
    return hashlib.sha256(data).hexdigest()


def compute_file_sha256(file_path: Path) -> str:
    """Обчислює SHA-256 хеш бінарного файлу практичної роботи поблочно."""
    resolved = Path(file_path)
    if not resolved.exists() or not resolved.is_file():
        raise InvalidFileFormatError(
            f"Файл для обчислення SHA-256 не знайдено: '{resolved.name}'.",
            context={"file_path": str(resolved)},
        )

    hasher = hashlib.sha256()
    try:
        with resolved.open("rb") as file_obj:
            while chunk := file_obj.read(_HASH_CHUNK_SIZE):
                hasher.update(chunk)
    except OSError as exc:
        raise InvalidFileFormatError(
            f"Не вдалося прочитати файл '{resolved.name}' для обчислення SHA-256.",
            context={"file_path": str(resolved)},
        ) from exc

    return hasher.hexdigest()


def normalize_code_for_hashing(raw_code: str) -> str:
    """Нормалізує вихідний HTML-код (уніфікація пробільних символів) перед хешуванням."""
    return " ".join(raw_code.strip().split())


def compute_code_sha256(raw_code: str) -> str:
    """Обчислює SHA-256 хеш нормалізованого вихідного коду практичної роботи."""
    normalized = normalize_code_for_hashing(raw_code)
    if not normalized:
        raise InvalidFileFormatError(
            "Вихідний код для обчислення SHA-256 порожній.",
            context={"raw_code_length": len(raw_code)},
        )
    return compute_bytes_sha256(normalized.encode("utf-8"))


def compute_submission_hash(
    *,
    file_path: Path | None = None,
    raw_code: str | None = None,
) -> str:
    """Обчислює SHA-256 хеш здачі студента (для завантаженого файлу або HTML-коду)."""
    if file_path is not None:
        return compute_file_sha256(file_path)
    if raw_code is not None:
        return compute_code_sha256(raw_code)
    raise InvalidFileFormatError(
        "Для обчислення SHA-256 необхідно передати шлях до файлу або вихідний код."
    )


def validate_zip_archive_safety(source: bytes | Path) -> None:
    """Перевіряє OpenXML ZIP-архів на ознаки Zip-бомби до будь-якого розпакування."""
    source_label = source.name if isinstance(source, Path) else "<uploaded-bytes>"
    zip_input: io.BytesIO | Path = io.BytesIO(source) if isinstance(source, bytes) else source

    try:
        with zipfile.ZipFile(zip_input, mode="r") as archive:
            infos = archive.infolist()
    except (zipfile.BadZipFile, OSError) as exc:
        raise InvalidFileFormatError(
            f"Файл '{source_label}' не є коректним OpenXML ZIP-архівом.",
            context={"file_name": source_label},
        ) from exc

    max_entries = settings.MAX_ZIP_ENTRIES
    if len(infos) > max_entries:
        raise GradingError(
            "Архів OpenXML містить забагато внутрішніх файлів "
            f"({len(infos)} > {max_entries}).",
            code="UNSAFE_ZIP_ARCHIVE",
            context={
                "file_name": source_label,
                "entries_count": len(infos),
                "max_entries": max_entries,
            },
        )

    max_single_bytes = settings.MAX_ZIP_SINGLE_ENTRY_BYTES
    max_total_bytes = settings.MAX_ZIP_UNCOMPRESSED_BYTES
    max_ratio = settings.MAX_ZIP_COMPRESSION_RATIO
    total_uncompressed_bytes = 0

    for zinfo in infos:
        if zinfo.file_size > max_single_bytes:
            raise GradingError(
                "Один із файлів усередині OpenXML-архіву перевищує максимально "
                "допустимий нестиснений розмір.",
                code="UNSAFE_ZIP_ARCHIVE",
                context={
                    "file_name": source_label,
                    "entry_name": zinfo.filename,
                    "entry_size_bytes": zinfo.file_size,
                    "max_single_entry_bytes": max_single_bytes,
                },
            )

        total_uncompressed_bytes += zinfo.file_size
        if total_uncompressed_bytes > max_total_bytes:
            raise GradingError(
                "Сумарний нестиснений розмір файлів OpenXML-архіву перевищує "
                "максимально допустимий ліміт.",
                code="UNSAFE_ZIP_ARCHIVE",
                context={
                    "file_name": source_label,
                    "uncompressed_bytes": total_uncompressed_bytes,
                    "max_uncompressed_bytes": max_total_bytes,
                },
            )

        if (
            zinfo.compress_size > 0
            and zinfo.file_size > _MIN_ENTRY_BYTES_FOR_RATIO_CHECK
        ):
            ratio = zinfo.file_size / zinfo.compress_size
            if ratio > max_ratio:
                raise GradingError(
                    "OpenXML-архів відхилено через підозріло високий коефіцієнт "
                    f"стиснення ({ratio:.1f}x > {max_ratio:.1f}x).",
                    code="UNSAFE_ZIP_ARCHIVE",
                    context={
                        "file_name": source_label,
                        "entry_name": zinfo.filename,
                        "file_size": zinfo.file_size,
                        "compress_size": zinfo.compress_size,
                        "compression_ratio": round(ratio, 2),
                        "max_compression_ratio": max_ratio,
                    },
                )


def _find_xml_text(
    root: XmlElement,
    namespaced_xpath: str,
    local_name: str,
) -> str | None:
    """Шукає текстове значення XML-вузла за простором імен або локальним ім'ям тегу."""
    element = root.find(namespaced_xpath, _CORE_XML_NAMESPACES)
    if element is not None and element.text is not None:
        cleaned = element.text.strip()
        return cleaned if cleaned else None

    suffix = f"}}{local_name}"
    for candidate in root.iter():
        if (
            candidate.tag == local_name or candidate.tag.endswith(suffix)
        ) and candidate.text is not None:
            cleaned = candidate.text.strip()
            return cleaned if cleaned else None
    return None


def parse_core_xml_bytes(xml_bytes: bytes) -> ExtractedMetadata:
    """Парсить вміст XML-файлу `docProps/core.xml` у контракт ExtractedMetadata через defusedxml."""
    try:
        root_raw: object = DefusedET.fromstring(xml_bytes)
    except DefusedXmlException as exc:
        raise GradingError(
            "Виявлено небезпечні XML-конструкції (DTD/сутності) у docProps/core.xml.",
            code="UNSAFE_XML_CONTENT",
            context={
                "archive_member": CORE_XML_ARCHIVE_PATH,
                "error_type": type(exc).__name__,
            },
        ) from exc
    except DefusedET.ParseError as exc:
        raise InvalidFileFormatError(
            "Пошкоджений XML-файл метаданих docProps/core.xml.",
            context={"archive_member": CORE_XML_ARCHIVE_PATH},
        ) from exc

    if not isinstance(root_raw, XmlElement):
        raise InvalidFileFormatError(
            "Пошкоджений XML-файл метаданих docProps/core.xml.",
            context={"archive_member": CORE_XML_ARCHIVE_PATH},
        )

    return ExtractedMetadata(
        creator=_find_xml_text(root_raw, "dc:creator", "creator"),
        last_modified_by=_find_xml_text(root_raw, "cp:lastModifiedBy", "lastModifiedBy"),
        created=_find_xml_text(root_raw, "dcterms:created", "created"),
        modified=_find_xml_text(root_raw, "dcterms:modified", "modified"),
        revision=_find_xml_text(root_raw, "cp:revision", "revision"),
    )


def extract_core_xml_metadata(file_path: Path) -> ExtractedMetadata:
    """Витягує метадані авторства з `docProps/core.xml` OpenXML-архіву (.docx, .xlsx)."""
    resolved = Path(file_path)
    if not resolved.exists() or not resolved.is_file():
        raise InvalidFileFormatError(
            f"Файл для екстракції метаданих не знайдено: '{resolved.name}'.",
            context={"file_path": str(resolved)},
        )

    validate_zip_archive_safety(resolved)

    try:
        with zipfile.ZipFile(resolved, mode="r") as archive:
            if CORE_XML_ARCHIVE_PATH not in archive.namelist():
                return ExtractedMetadata()
            xml_bytes = archive.read(CORE_XML_ARCHIVE_PATH)
    except (zipfile.BadZipFile, OSError) as exc:
        raise InvalidFileFormatError(
            f"Файл '{resolved.name}' не є коректним OpenXML ZIP-архівом.",
            context={"file_name": resolved.name},
        ) from exc

    return parse_core_xml_bytes(xml_bytes)


def extract_document_metadata(file_path: Path | None = None) -> ExtractedMetadata:
    """Універсальний екстрактор метаданих файлу здачі (.docx/.xlsx -> core.xml)."""
    if file_path is None:
        return ExtractedMetadata()

    resolved = Path(file_path)
    if not resolved.exists() or not resolved.is_file():
        raise InvalidFileFormatError(
            f"Файл для аналізу метаданих не знайдено: '{resolved.name}'.",
            context={"file_path": str(resolved)},
        )

    suffix = resolved.suffix.lower()
    if suffix in OPENXML_EXTENSIONS:
        return extract_core_xml_metadata(resolved)

    if zipfile.is_zipfile(resolved):
        return extract_core_xml_metadata(resolved)

    return ExtractedMetadata()


def _coerce_metadata(raw_metadata: ExtractedMetadata | dict[str, object]) -> ExtractedMetadata:
    """Перетворює словник або об'єкт метаданих на валідований екземпляр ExtractedMetadata."""
    if isinstance(raw_metadata, ExtractedMetadata):
        return raw_metadata
    return ExtractedMetadata.model_validate(raw_metadata)


def evaluate_plagiarism(
    *,
    student_id: uuid.UUID,
    file_hash: str | None,
    metadata: ExtractedMetadata | dict[str, object],
    existing_submissions: Sequence[SubmissionRecordProtocol],
) -> PlagiarismCheckResult:
    """Детерміновано перевіряє здачу на збіг SHA-256 або метаданих core.xml з іншими студентами."""
    candidate_meta = _coerce_metadata(metadata)
    normalized_hash = file_hash.strip().lower() if file_hash else None
    candidate_created = candidate_meta.created.strip() if candidate_meta.created else None
    candidate_creator = candidate_meta.creator.strip() if candidate_meta.creator else None
    candidate_modified = candidate_meta.modified.strip() if candidate_meta.modified else None

    for existing in existing_submissions:
        if existing.student_id == student_id:
            continue

        existing_hash = existing.file_hash.strip().lower() if existing.file_hash else None
        if normalized_hash and existing_hash and normalized_hash == existing_hash:
            return PlagiarismCheckResult(
                is_flagged=True,
                reason=(
                    "Виявлено повний збіг SHA-256 хешу роботи зі здачею іншого студента "
                    f"(ID здачі: {existing.id})."
                ),
                matched_submission_id=existing.id,
                matched_student_id=existing.student_id,
            )

        existing_meta = _coerce_metadata(existing.extracted_metadata)
        existing_created = existing_meta.created.strip() if existing_meta.created else None
        existing_creator = existing_meta.creator.strip() if existing_meta.creator else None
        existing_modified = existing_meta.modified.strip() if existing_meta.modified else None

        if candidate_created and existing_created and candidate_created == existing_created:
            creator_note = (
                f", creator='{candidate_creator}'"
                if candidate_creator and candidate_creator == existing_creator
                else ""
            )
            return PlagiarismCheckResult(
                is_flagged=True,
                reason=(
                    "Виявлено збіг метаданих docProps/core.xml "
                    f"(created='{candidate_created}'{creator_note}) "
                    f"зі здачею іншого студента (ID здачі: {existing.id})."
                ),
                matched_submission_id=existing.id,
                matched_student_id=existing.student_id,
            )

        if (
            candidate_creator
            and existing_creator
            and candidate_creator == existing_creator
            and candidate_modified
            and existing_modified
            and candidate_modified == existing_modified
        ):
            return PlagiarismCheckResult(
                is_flagged=True,
                reason=(
                    "Виявлено збіг метаданих автора та часу модифікації docProps/core.xml "
                    f"(creator='{candidate_creator}', modified='{candidate_modified}') "
                    f"зі здачею іншого студента (ID здачі: {existing.id})."
                ),
                matched_submission_id=existing.id,
                matched_student_id=existing.student_id,
            )

    return PlagiarismCheckResult(
        is_flagged=False,
        reason=None,
        matched_submission_id=None,
        matched_student_id=None,
    )


async def check_submission_plagiarism(
    db: AsyncSession,
    *,
    practical_id: uuid.UUID,
    student_id: uuid.UUID,
    file_hash: str | None,
    metadata: ExtractedMetadata | dict[str, object],
) -> PlagiarismCheckResult:
    """Виконує запит до БД та перевіряє роботу студента на плагіат серед здач за цією практичною."""
    stmt = (
        select(Submission)
        .where(
            Submission.practical_id == practical_id,
            Submission.student_id != student_id,
        )
        .order_by(Submission.submitted_at.asc())
    )
    result = await db.execute(stmt)
    existing_submissions = list(result.scalars().all())

    return evaluate_plagiarism(
        student_id=student_id,
        file_hash=file_hash,
        metadata=metadata,
        existing_submissions=existing_submissions,
    )
