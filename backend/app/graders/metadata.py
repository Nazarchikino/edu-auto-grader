import contextlib
import csv
import hashlib
import io
import json
import math
import re
import shutil
import subprocess
import uuid
import zipfile
from collections.abc import Mapping, Sequence
from datetime import date, datetime, time
from pathlib import Path
from typing import Protocol
from xml.etree.ElementTree import Element as XmlElement

import openpyxl  # type: ignore[import-untyped]
from access_parser.access_parser import AccessParser  # type: ignore[import-untyped]
from bs4 import BeautifulSoup, FeatureNotFound
from bs4.element import (
    Comment,
    Declaration,
    Doctype,
    NavigableString,
    ProcessingInstruction,
    Tag,
)
from defusedxml import DefusedXmlException
from defusedxml import ElementTree as DefusedET
from openpyxl.utils.cell import get_column_letter  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import GradingError, InvalidFileFormatError
from app.models.course import PracticalFormat
from app.models.progress import Submission
from app.schemas.grading import ExtractedMetadata, PlagiarismCheckResult

CORE_XML_ARCHIVE_PATH = "docProps/core.xml"
OPENXML_EXTENSIONS: frozenset[str] = frozenset({".docx", ".xlsx"})
HTML_EXTENSIONS: frozenset[str] = frozenset({".html", ".htm"})
ACCDB_EXTENSIONS: frozenset[str] = frozenset({".accdb", ".mdb"})

GENERIC_CREATOR_NAMES: frozenset[str] = frozenset(
    {
        "user",
        "admin",
        "administrator",
        "student",
        "windows user",
        "microsoft office user",
        "microsoft",
        "pc",
        "owner",
        "guest",
        "acer",
        "asus",
        "hp",
        "lenovo",
        "dell",
        "kpefk",
        "college",
        "користувач",
        "адміністратор",
        "студент",
    }
)

SHINGLE_NGRAM_SIZE = 3
SHINGLE_MIN_WORDS = 15
SHINGLE_SKETCH_SIZE = 64
MIN_SHINGLES_FOR_SIMILARITY = 12
SHINGLE_PLAGIARISM_THRESHOLD = 0.85
SHINGLE_CREATED_CORROBORATION_THRESHOLD = 0.70
SHINGLE_HTML_SKELETON_MIN_OVERLAP = 0.35

DOCX_MIN_NORMALIZED_CHARS = 40
XLSX_MIN_FORMULAS_FOR_FINGERPRINT = 3
XLSX_MIN_NON_EMPTY_CELLS_FOR_FINGERPRINT = 10
HTML_MIN_BODY_TAGS_FOR_FINGERPRINT = 5

_HASH_CHUNK_SIZE = 65536
_MIN_ENTRY_BYTES_FOR_RATIO_CHECK = 1_048_576
_MAX_XLSX_CELLS_FOR_FINGERPRINT = 50_000
_MAX_ACCDB_ROWS_FOR_FINGERPRINT = 5_000
_ACCESS_HEADER_MAGIC = b"\x00\x01\x00\x00"
_ACCESS_SYSTEM_TABLE_PREFIXES: tuple[str, ...] = ("msys", "usys", "~")

_HTML_SHELL_TAGS: frozenset[str] = frozenset(
    {"html", "head", "meta", "title", "link", "style", "base"}
)
_HTML_NON_TEXT_TAGS: frozenset[str] = frozenset({"script", "style", "noscript"})
_HTML_NON_CONTENT_STRING_TYPES = (
    Comment,
    Declaration,
    Doctype,
    ProcessingInstruction,
)

_APOSTROPHE_PATTERN = re.compile(r"['’‘ʼ`´]+")
_WORD_TOKEN_PATTERN = re.compile(r"[^\W_]+", flags=re.UNICODE)
_CSS_COMMENT_PATTERN = re.compile(r"/\*.*?\*/", flags=re.DOTALL)
_CSS_BLOCK_PATTERN = re.compile(r"\{([^{}]*)\}")
_XLSX_FUNC_CALL_PATTERN = re.compile(
    r"(?<![A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9_!.])"
    r"([A-Za-zА-Яа-яЁёІіЇїЄєҐґ_][A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9_.]*)(?=\()"
)
_XLSX_LOCALIZED_FUNCTION_ALIASES: dict[str, str] = {
    "СУМ": "SUM",
    "СУММ": "SUM",
    "СЕРЕДНЄ": "AVERAGE",
    "СРЗНАЧ": "AVERAGE",
    "МІН": "MIN",
    "МИН": "MIN",
    "МАКС": "MAX",
    "КІЛЬКІСТЬ": "COUNT",
    "СЧЕТ": "COUNT",
    "СЧЁТ": "COUNT",
    "КІЛЬКІСТЬЗ": "COUNTA",
    "СЧЕТЗ": "COUNTA",
    "СЧЁТЗ": "COUNTA",
    "ЯКЩО": "IF",
    "ЕСЛИ": "IF",
    "І": "AND",
    "И": "AND",
    "АБО": "OR",
    "ИЛИ": "OR",
    "НЕ": "NOT",
    "ВПР": "VLOOKUP",
    "КОРІНЬ": "SQRT",
    "КОРЕНЬ": "SQRT",
    "ОКРУГЛ": "ROUND",
    "СТЕПІНЬ": "POWER",
    "СТЕПЕНЬ": "POWER",
    "СУМЯКЩО": "SUMIF",
    "СУММЕСЛИ": "SUMIF",
    "КІЛЬКІСТЬЯКЩО": "COUNTIF",
    "СЧЕТЕСЛИ": "COUNTIF",
    "СЧЁТЕСЛИ": "COUNTIF",
}

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


def _tokenize_normalized_words(raw_text: str) -> list[str]:
    """Нормалізує текст (нижній регістр, без пунктуації/апострофів) у список слів."""
    cleaned = _APOSTROPHE_PATTERN.sub("", raw_text.casefold())
    return _WORD_TOKEN_PATTERN.findall(cleaned)


def compute_text_shingles(words: Sequence[str]) -> list[str]:
    """Будує детермінований MinHash-скетч (до 64 найменших хешів 3-грам слів)."""
    if len(words) < SHINGLE_MIN_WORDS:
        return []

    hashes: set[str] = set()
    limit = len(words) - SHINGLE_NGRAM_SIZE + 1
    for idx in range(limit):
        shingle = " ".join(words[idx : idx + SHINGLE_NGRAM_SIZE])
        digest = hashlib.blake2b(shingle.encode("utf-8"), digest_size=8).hexdigest()
        hashes.add(digest)

    return sorted(hashes)[:SHINGLE_SKETCH_SIZE]


def compute_shingle_jaccard(
    shingles_a: Sequence[str],
    shingles_b: Sequence[str],
) -> float | None:
    """Оцінює схожість Jaccard двох MinHash-скетчів шинглів (KMV-оцінювач, при len >= 12)."""
    set_a = {item.strip() for item in shingles_a if item and item.strip()}
    set_b = {item.strip() for item in shingles_b if item and item.strip()}
    if len(set_a) < MIN_SHINGLES_FOR_SIMILARITY or len(set_b) < MIN_SHINGLES_FOR_SIMILARITY:
        return None

    union_set = set_a | set_b
    if not union_set:
        return 0.0

    # Якщо жоден скетч не обрізаний до SHINGLE_SKETCH_SIZE — точний індекс Jaccard.
    if len(set_a) < SHINGLE_SKETCH_SIZE and len(set_b) < SHINGLE_SKETCH_SIZE:
        return len(set_a & set_b) / len(union_set)

    # Для обрізаних bottom-k (KMV) скетчів беремо k найменших хешів об'єднання:
    # на цьому інтервалі обидва скетчі гарантовано повні, тому оцінка незміщена.
    top_k_union = set(sorted(union_set)[:SHINGLE_SKETCH_SIZE])
    if not top_k_union:
        return 0.0
    return len(top_k_union & set_a & set_b) / len(top_k_union)


_DOCX_DOCUMENT_XML_PATH = "word/document.xml"
_DOCX_WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_DOCX_TAG_BODY = f"{{{_DOCX_WORD_NS}}}body"
_DOCX_TAG_P = f"{{{_DOCX_WORD_NS}}}p"
_DOCX_TAG_TBL = f"{{{_DOCX_WORD_NS}}}tbl"
_DOCX_TAG_TR = f"{{{_DOCX_WORD_NS}}}tr"
_DOCX_TAG_TC = f"{{{_DOCX_WORD_NS}}}tc"
_DOCX_TAG_SDT = f"{{{_DOCX_WORD_NS}}}sdt"
_DOCX_TAG_SDT_CONTENT = f"{{{_DOCX_WORD_NS}}}sdtContent"
_DOCX_TAG_T = f"{{{_DOCX_WORD_NS}}}t"
_DOCX_BREAK_TAGS: frozenset[str] = frozenset(
    {
        f"{{{_DOCX_WORD_NS}}}tab",
        f"{{{_DOCX_WORD_NS}}}br",
        f"{{{_DOCX_WORD_NS}}}cr",
    }
)


def _extract_docx_paragraph_xml_text(paragraph_el: XmlElement) -> str:
    """Витягує текст з XML-вузла <w:p>, зберігаючи пробіли на табуляціях і переносах."""
    parts: list[str] = []
    for node in paragraph_el.iter():
        if node.tag == _DOCX_TAG_T and node.text:
            parts.append(node.text)
        elif node.tag in _DOCX_BREAK_TAGS:
            parts.append(" ")
    return "".join(parts).strip()


def _collect_docx_xml_table_texts(table_el: XmlElement, out: list[str]) -> None:
    """Рекурсивно збирає текст клітинок <w:tc> із таблиці <w:tbl> (включно з вкладеними)."""
    for row_el in table_el:
        if row_el.tag != _DOCX_TAG_TR:
            continue
        for cell_el in row_el:
            if cell_el.tag != _DOCX_TAG_TC:
                continue
            for child in cell_el:
                if child.tag == _DOCX_TAG_P:
                    text = _extract_docx_paragraph_xml_text(child)
                    if text:
                        out.append(text)
                elif child.tag == _DOCX_TAG_TBL:
                    _collect_docx_xml_table_texts(child, out)


def _collect_docx_body_fragments(
    container: XmlElement,
    paragraph_out: list[str],
    table_out: list[str],
) -> None:
    """Збирає текст абзаців та таблиць із <w:body> (включно з content controls <w:sdt>)."""
    for child in container:
        if child.tag == _DOCX_TAG_P:
            text = _extract_docx_paragraph_xml_text(child)
            if text:
                paragraph_out.append(text)
        elif child.tag == _DOCX_TAG_TBL:
            _collect_docx_xml_table_texts(child, table_out)
        elif child.tag == _DOCX_TAG_SDT:
            sdt_content = child.find(_DOCX_TAG_SDT_CONTENT)
            if sdt_content is not None:
                _collect_docx_body_fragments(sdt_content, paragraph_out, table_out)


def _extract_docx_fingerprint(
    file_path: Path,
) -> tuple[str | None, list[str], bool | None]:
    """Генерує структурний відбиток і MinHash-шингли для документа Word (.docx)."""
    try:
        with zipfile.ZipFile(file_path, mode="r") as archive:
            if _DOCX_DOCUMENT_XML_PATH not in archive.namelist():
                return None, [], None
            doc_xml_bytes = archive.read(_DOCX_DOCUMENT_XML_PATH)

        root_raw: object = DefusedET.fromstring(doc_xml_bytes)
        if not isinstance(root_raw, XmlElement):
            return None, [], None

        body_el = root_raw.find(_DOCX_TAG_BODY)
        target_container = body_el if body_el is not None else root_raw
        paragraph_fragments: list[str] = []
        table_fragments: list[str] = []
        _collect_docx_body_fragments(target_container, paragraph_fragments, table_fragments)
        fragments = paragraph_fragments + table_fragments
    except Exception:
        return None, [], None

    words = _tokenize_normalized_words(" ".join(fragments))
    normalized_text = " ".join(words)
    shingles = compute_text_shingles(words)
    if len(normalized_text) < DOCX_MIN_NORMALIZED_CHARS:
        return None, shingles, None

    fingerprint = compute_bytes_sha256(f"docx:v1:{normalized_text}".encode())
    return fingerprint, shingles, True


def _canonicalize_xlsx_formula(formula: str) -> str:
    """Канонізує формулу Excel: прибирає '=', пробіли поза лапками, ';' -> ',', локалізації."""
    cleaned = formula.strip()
    if cleaned.startswith("="):
        cleaned = cleaned[1:].strip()
    if not cleaned:
        return ""

    segments: list[tuple[bool, str]] = []
    buf: list[str] = []
    idx = 0
    length = len(cleaned)
    in_quotes = False
    quote_char = '"'

    while idx < length:
        ch = cleaned[idx]
        if in_quotes:
            buf.append(ch)
            if ch == quote_char:
                if idx + 1 < length and cleaned[idx + 1] == quote_char:
                    buf.append(cleaned[idx + 1])
                    idx += 2
                    continue
                segments.append((True, "".join(buf)))
                buf = []
                in_quotes = False
            idx += 1
            continue

        if ch in {'"', "'"}:
            if buf:
                segments.append((False, "".join(buf)))
                buf = []
            in_quotes = True
            quote_char = ch
            buf.append(ch)
            idx += 1
            continue

        buf.append(ch)
        idx += 1

    if buf:
        segments.append((in_quotes, "".join(buf)))

    out_parts: list[str] = []
    for is_quoted, raw_seg in segments:
        if is_quoted:
            out_parts.append(raw_seg)
            continue

        normalized_chars: list[str] = []
        for ch in raw_seg:
            if ch.isspace():
                continue
            if ch == ";":
                normalized_chars.append(",")
                continue
            normalized_chars.append(ch.upper())

        seg_text = "".join(normalized_chars)
        seg_text = _XLSX_FUNC_CALL_PATTERN.sub(
            lambda m: _XLSX_LOCALIZED_FUNCTION_ALIASES.get(m.group(1), m.group(1)),
            seg_text,
        )
        out_parts.append(seg_text)

    return "".join(out_parts)


def _extract_xlsx_formula_text(raw_value: object) -> str | None:
    """Витягує текст формули з клітинки Excel (рядок '=...' або об'єкт ArrayFormula)."""
    if isinstance(raw_value, str):
        stripped = raw_value.strip()
        return stripped if stripped.startswith("=") else None

    formula_attr: object = getattr(raw_value, "text", None)
    if isinstance(formula_attr, str):
        stripped = formula_attr.strip()
        return stripped if stripped.startswith("=") else None
    return None


def _normalize_xlsx_value(raw_value: object) -> str | None:
    """Нормалізує значення непорожньої клітинки Excel незалежно від форматування."""
    if raw_value is None:
        return None
    if isinstance(raw_value, bool):
        return "B:1" if raw_value else "B:0"
    if isinstance(raw_value, int):
        return f"N:{raw_value}"
    if isinstance(raw_value, float):
        if math.isnan(raw_value) or math.isinf(raw_value):
            return f"N:{raw_value}"
        rounded = round(raw_value)
        if math.isclose(raw_value, float(rounded), abs_tol=1e-9):
            return f"N:{rounded}"
        return f"N:{raw_value:.6f}".rstrip("0").rstrip(".")
    if isinstance(raw_value, (datetime, date, time)):
        return f"D:{raw_value.isoformat()}"
    if isinstance(raw_value, str):
        cleaned = " ".join(raw_value.strip().casefold().split())
        return f"S:{cleaned}" if cleaned else None
    cleaned = " ".join(str(raw_value).strip().casefold().split())
    return f"O:{cleaned}" if cleaned else None


def _extract_xlsx_fingerprint(file_path: Path) -> tuple[str | None, bool | None]:
    """Генерує структурний відбиток книги Excel (.xlsx) за формулами та клітинками."""
    workbook = None
    try:
        workbook = openpyxl.load_workbook(
            filename=str(file_path),
            data_only=False,
            read_only=True,
        )
        formulas: list[tuple[int, str, str]] = []
        values: list[tuple[int, str, str]] = []
        non_empty_cells = 0

        for sheet_idx, sheet_name in enumerate(workbook.sheetnames):
            worksheet = workbook[sheet_name]
            for row_idx, row in enumerate(worksheet.iter_rows(values_only=True), start=1):
                for col_idx, raw_val in enumerate(row, start=1):
                    if raw_val is None:
                        continue
                    formula_text = _extract_xlsx_formula_text(raw_val)
                    if formula_text is not None:
                        canonical = _canonicalize_xlsx_formula(formula_text)
                        if canonical:
                            coord = f"{get_column_letter(col_idx)}{row_idx}"
                            formulas.append((sheet_idx, coord, canonical))
                            non_empty_cells += 1
                    else:
                        norm_val = _normalize_xlsx_value(raw_val)
                        if norm_val is not None:
                            coord = f"{get_column_letter(col_idx)}{row_idx}"
                            values.append((sheet_idx, coord, norm_val))
                            non_empty_cells += 1

                    if non_empty_cells >= _MAX_XLSX_CELLS_FOR_FINGERPRINT:
                        break
                if non_empty_cells >= _MAX_XLSX_CELLS_FOR_FINGERPRINT:
                    break
            if non_empty_cells >= _MAX_XLSX_CELLS_FOR_FINGERPRINT:
                break
    except Exception:
        return None, None
    finally:
        if workbook is not None:
            with contextlib.suppress(Exception):
                workbook.close()

    if (
        len(formulas) < XLSX_MIN_FORMULAS_FOR_FINGERPRINT
        and non_empty_cells < XLSX_MIN_NON_EMPTY_CELLS_FOR_FINGERPRINT
    ):
        return None, None

    payload = json.dumps(
        {"formulas": formulas, "values": values},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    fingerprint = compute_bytes_sha256(f"xlsx:v1:{payload}".encode())
    has_unique = len(formulas) >= XLSX_MIN_FORMULAS_FOR_FINGERPRINT
    return fingerprint, has_unique


def _normalize_css_declarations(raw_declarations: str) -> str:
    """Нормалізує та сортує CSS-властивості 'prop:val' без коментарів і зайвих пробілів."""
    cleaned = _CSS_COMMENT_PATTERN.sub("", raw_declarations)
    pairs: list[str] = []
    for raw_part in cleaned.split(";"):
        if ":" not in raw_part:
            continue
        prop, val = raw_part.split(":", 1)
        norm_prop = " ".join(prop.strip().casefold().split())
        norm_val = " ".join(val.strip().casefold().split())
        if norm_prop and norm_val:
            pairs.append(f"{norm_prop}:{norm_val}")
    if not pairs:
        return ""
    pairs.sort()
    return ";".join(pairs)


def _extract_css_property_blocks(soup: BeautifulSoup) -> list[str]:
    """Витягує відсортовані CSS-блоки зі <style> без селекторів (class/id) і коментарів."""
    blocks: list[str] = []
    for style_tag in soup.find_all("style"):
        css_text = style_tag.get_text() if isinstance(style_tag, Tag) else ""
        if not css_text:
            continue
        without_comments = _CSS_COMMENT_PATTERN.sub("", css_text)
        for match in _CSS_BLOCK_PATTERN.finditer(without_comments):
            normalized = _normalize_css_declarations(match.group(1))
            if normalized:
                blocks.append(normalized)
    blocks.sort()
    return blocks


def _serialize_html_dom_structure(root: Tag) -> tuple[list[str], int]:
    """Нормалізує DOM-дерево в послідовність тегів і відсортованих inline CSS-властивостей."""
    tokens: list[str] = []
    tag_count = 0

    def _walk(node: Tag) -> None:
        nonlocal tag_count
        for child in node.children:
            if not isinstance(child, Tag):
                continue
            tag_name = child.name.casefold()
            if tag_name in _HTML_SHELL_TAGS:
                continue
            tag_count += 1
            raw_style = child.attrs.get("style")
            inline_css = (
                _normalize_css_declarations(raw_style)
                if isinstance(raw_style, str)
                else ""
            )
            tokens.append(f"<{tag_name}|{inline_css}>" if inline_css else f"<{tag_name}>")
            _walk(child)
            tokens.append(f"</{tag_name}>")

    _walk(root)
    return tokens, tag_count


def _extract_html_visible_text(root: Tag) -> str:
    """Витягує видимий текст із DOM-вузла без коментарів, <script> та <style>."""
    parts: list[str] = []

    def _walk(node: Tag) -> None:
        for child in node.children:
            if isinstance(child, _HTML_NON_CONTENT_STRING_TYPES):
                continue
            if isinstance(child, Tag):
                tag_name = child.name.casefold()
                if tag_name in _HTML_NON_TEXT_TAGS or tag_name in _HTML_SHELL_TAGS:
                    continue
                _walk(child)
                continue
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    parts.append(text)

    _walk(root)
    return " ".join(parts)


def _extract_html_fingerprint(
    html_source: str,
) -> tuple[str | None, list[str], bool | None]:
    """Генерує DOM+CSS структурний відбиток і текстові шингли для HTML-документа."""
    try:
        try:
            soup = BeautifulSoup(html_source, "lxml")
        except FeatureNotFound:
            soup = BeautifulSoup(html_source, "html.parser")

        for non_content in list(
            soup.find_all(
                string=lambda node: isinstance(node, _HTML_NON_CONTENT_STRING_TYPES)
            )
        ):
            non_content.extract()

        css_blocks = _extract_css_property_blocks(soup)
        body = soup.find("body")
        root: Tag = body if isinstance(body, Tag) else soup

        dom_tokens, body_tag_count = _serialize_html_dom_structure(root)
        visible_text = _extract_html_visible_text(root)
    except Exception:
        return None, [], None

    words = _tokenize_normalized_words(visible_text)
    shingles = compute_text_shingles(words)

    if body_tag_count < HTML_MIN_BODY_TAGS_FOR_FINGERPRINT:
        return None, shingles, None

    payload = json.dumps(
        {"dom": dom_tokens, "css": css_blocks},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    fingerprint = compute_bytes_sha256(f"html:v1:{payload}".encode())
    has_css = bool(css_blocks) or any("|" in token for token in dom_tokens)
    has_unique = has_css or len(shingles) >= MIN_SHINGLES_FOR_SIMILARITY
    return fingerprint, shingles, has_unique


def _is_accdb_system_table(table_name: str) -> bool:
    """Перевіряє, чи є таблиця Access системною (MSys*, USys*, ~*)."""
    return table_name.strip().casefold().startswith(_ACCESS_SYSTEM_TABLE_PREFIXES)


def _normalize_accdb_value(value: object) -> str:
    """Нормалізує значення комірки таблиці Access у детермінований рядок."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return str(value)
        rounded = round(value)
        if math.isclose(value, float(rounded), abs_tol=1e-9):
            return str(rounded)
        return f"{value:.6f}".rstrip("0").rstrip(".")
    if isinstance(value, (bytes, bytearray)):
        return hashlib.sha256(bytes(value)).hexdigest()[:16]
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    return " ".join(str(value).strip().casefold().split())


def _extract_accdb_table_via_mdb_export(
    mdb_export_bin: str,
    file_path: Path,
    table_name: str,
) -> tuple[list[str], list[list[str]]] | None:
    """Експортує колонки та нормалізовані рядки таблиці Access через mdb-export (timeout=10)."""
    try:
        proc = subprocess.run(
            [mdb_export_bin, str(file_path), table_name],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        return None

    reader = csv.reader(io.StringIO(proc.stdout))
    header = next(reader, None)
    if not header:
        return None

    indexed_cols = sorted(
        (col.strip().casefold(), idx)
        for idx, col in enumerate(header)
        if col.strip()
    )
    norm_cols = [col_name for col_name, _ in indexed_cols]
    rows: list[list[str]] = []
    for raw_row in reader:
        if len(rows) >= _MAX_ACCDB_ROWS_FOR_FINGERPRINT:
            break
        if not any(cell.strip() for cell in raw_row):
            continue
        rows.append(
            [
                _normalize_accdb_value(raw_row[idx] if idx < len(raw_row) else "")
                for _, idx in indexed_cols
            ]
        )
    rows.sort()
    return norm_cols, rows


def _extract_accdb_tables_via_mdbtools(
    file_path: Path,
) -> list[dict[str, object]]:
    """Fallback-екстракція таблиць, колонок і рядків Access через mdb-tables / mdb-export."""
    mdb_tables_bin = shutil.which("mdb-tables")
    if mdb_tables_bin is None:
        return []

    try:
        proc = subprocess.run(
            [mdb_tables_bin, "-1", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    if proc.returncode != 0:
        return []

    user_tables = sorted(
        {
            line.strip()
            for line in proc.stdout.splitlines()
            if line.strip() and not _is_accdb_system_table(line.strip())
        },
        key=lambda name: (name.casefold(), name),
    )
    if not user_tables:
        return []

    mdb_export_bin = shutil.which("mdb-export")
    tables_payload: list[dict[str, object]] = []
    for table_name in user_tables:
        norm_cols: list[str] = []
        rows: list[list[str]] = []
        if mdb_export_bin is not None:
            exported = _extract_accdb_table_via_mdb_export(
                mdb_export_bin,
                file_path,
                table_name,
            )
            if exported is not None:
                norm_cols, rows = exported
        tables_payload.append(
            {
                "table": table_name.casefold(),
                "columns": norm_cols,
                "rows": rows,
            }
        )
    return tables_payload


def _extract_accdb_fingerprint(file_path: Path) -> tuple[str | None, bool | None]:
    """Генерує структурний відбиток бази даних Access (.accdb) за таблицями, полями і даними."""
    try:
        header = file_path.read_bytes()[:32]
    except OSError:
        return None, None

    if len(header) < 32 or not header.startswith(_ACCESS_HEADER_MAGIC):
        return None, None

    tables_payload: list[dict[str, object]] = []
    mdb_export_bin = shutil.which("mdb-export")

    try:
        parser = AccessParser(str(file_path))
        catalog_obj: object = getattr(parser, "catalog", None)
        if isinstance(catalog_obj, Mapping):
            user_tables = sorted(
                (
                    raw_name.strip()
                    for raw_name in catalog_obj
                    if isinstance(raw_name, str)
                    and raw_name.strip()
                    and not _is_accdb_system_table(raw_name.strip())
                ),
                key=lambda name: (name.casefold(), name),
            )
            for table_name in user_tables:
                norm_cols: list[str] = []
                rows: list[list[str]] = []
                parse_failed = False

                try:
                    parsed_raw: object = parser.parse_table(table_name)
                except Exception:
                    parsed_raw = None
                    parse_failed = True

                if isinstance(parsed_raw, Mapping) and parsed_raw:
                    col_entries = sorted(
                        (str(col_key).strip().casefold(), col_key)
                        for col_key in parsed_raw
                        if str(col_key).strip()
                    )
                    norm_cols = [norm_name for norm_name, _ in col_entries]
                    list_lengths = [
                        len(parsed_raw[orig_key])
                        for _, orig_key in col_entries
                        if isinstance(parsed_raw[orig_key], (list, tuple))
                    ]
                    row_count = min(
                        max(list_lengths, default=0),
                        _MAX_ACCDB_ROWS_FOR_FINGERPRINT,
                    )
                    for row_idx in range(row_count):
                        row_values: list[str] = []
                        for _, orig_key in col_entries:
                            col_series = parsed_raw[orig_key]
                            if isinstance(col_series, (list, tuple)) and row_idx < len(col_series):
                                row_values.append(_normalize_accdb_value(col_series[row_idx]))
                            else:
                                row_values.append("")
                        rows.append(row_values)
                    rows.sort()
                else:
                    if parse_failed and mdb_export_bin is not None:
                        exported = _extract_accdb_table_via_mdb_export(
                            mdb_export_bin,
                            file_path,
                            table_name,
                        )
                        if exported is not None:
                            norm_cols, rows = exported

                    if not norm_cols:
                        with contextlib.suppress(Exception):
                            table_obj: object = parser.get_table(table_name)
                            raw_cols: object = getattr(table_obj, "columns", None)
                            if isinstance(raw_cols, Mapping):
                                norm_cols = sorted(
                                    str(col_key).strip().casefold()
                                    for col_key in raw_cols
                                    if str(col_key).strip()
                                )

                tables_payload.append(
                    {
                        "table": table_name.casefold(),
                        "columns": norm_cols,
                        "rows": rows,
                    }
                )
    except Exception:
        tables_payload = []

    if not tables_payload:
        tables_payload = _extract_accdb_tables_via_mdbtools(file_path)

    if not tables_payload:
        return None, None

    has_row_data = any(
        isinstance(entry.get("rows"), list) and bool(entry["rows"])
        for entry in tables_payload
    )
    serialized = json.dumps(tables_payload, ensure_ascii=False, separators=(",", ":"))
    fingerprint = compute_bytes_sha256(f"accdb:v1:{serialized}".encode())
    return fingerprint, has_row_data


def extract_document_metadata(
    file_path: Path | None = None,
    *,
    raw_code: str | None = None,
) -> ExtractedMetadata:
    """Універсальний екстрактор метаданих і структурних відбитків (.docx/.xlsx/.accdb/.html)."""
    if raw_code is not None:
        fp, shingles, has_unique = _extract_html_fingerprint(raw_code)
        return ExtractedMetadata(
            content_fingerprint=fp,
            text_shingles=shingles,
            has_unique_content=has_unique,
        )

    if file_path is None:
        return ExtractedMetadata()

    resolved = Path(file_path)
    if not resolved.exists() or not resolved.is_file():
        raise InvalidFileFormatError(
            f"Файл для аналізу метаданих не знайдено: '{resolved.name}'.",
            context={"file_path": str(resolved)},
        )

    suffix = resolved.suffix.lower()

    if suffix in HTML_EXTENSIONS:
        try:
            html_text = resolved.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ExtractedMetadata()
        fp, shingles, has_unique = _extract_html_fingerprint(html_text)
        return ExtractedMetadata(
            content_fingerprint=fp,
            text_shingles=shingles,
            has_unique_content=has_unique,
        )

    if suffix in ACCDB_EXTENSIONS:
        fp, has_row_data = _extract_accdb_fingerprint(resolved)
        return ExtractedMetadata(
            content_fingerprint=fp,
            has_unique_content=has_row_data,
        )

    if suffix in OPENXML_EXTENSIONS or zipfile.is_zipfile(resolved):
        metadata = extract_core_xml_metadata(resolved)
        if suffix == ".docx":
            fp, shingles, has_unique = _extract_docx_fingerprint(resolved)
            return metadata.model_copy(
                update={
                    "content_fingerprint": fp,
                    "text_shingles": shingles,
                    "has_unique_content": has_unique,
                }
            )
        if suffix == ".xlsx":
            fp, has_unique = _extract_xlsx_fingerprint(resolved)
            return metadata.model_copy(
                update={
                    "content_fingerprint": fp,
                    "has_unique_content": has_unique,
                }
            )
        return metadata

    return ExtractedMetadata()


def _coerce_metadata(raw_metadata: ExtractedMetadata | dict[str, object]) -> ExtractedMetadata:
    """Перетворює словник або об'єкт метаданих на валідований екземпляр ExtractedMetadata."""
    if isinstance(raw_metadata, ExtractedMetadata):
        return raw_metadata
    return ExtractedMetadata.model_validate(raw_metadata)


def _clean_optional_str(value: str | None) -> str | None:
    """Обрізає пробіли у рядку та перетворює порожній рядок на None."""
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def _is_generic_creator(creator: str | None) -> bool:
    """Перевіряє, чи є ім'я автора системним/типовим для комп'ютерного класу."""
    cleaned = _clean_optional_str(creator)
    if cleaned is None:
        return True
    normalized = " ".join(cleaned.casefold().split())
    return normalized in GENERIC_CREATOR_NAMES


def _is_content_fingerprint_match_actionable(
    *,
    candidate_meta: ExtractedMetadata,
    existing_meta: ExtractedMetadata,
    shingle_similarity: float | None,
    same_created: bool,
    same_modified: bool,
    same_non_generic_creator: bool,
    variants_count: int | None,
    format_type: PracticalFormat | None,
) -> bool:
    """Перевіряє, чи збіг content_fingerprint є надійним доказом плагіату без false positives."""
    if (
        shingle_similarity is not None
        and shingle_similarity < SHINGLE_HTML_SKELETON_MIN_OVERLAP
    ):
        return False

    if variants_count is None or variants_count > 1:
        return True

    if same_created or same_modified or same_non_generic_creator:
        return True

    if (
        shingle_similarity is not None
        and shingle_similarity >= SHINGLE_CREATED_CORROBORATION_THRESHOLD
    ):
        return True

    if format_type == PracticalFormat.ACCDB:
        return (
            candidate_meta.has_unique_content is True
            and existing_meta.has_unique_content is True
        )

    if format_type == PracticalFormat.XLSX:
        candidate_stripped = (
            _clean_optional_str(candidate_meta.created) is None
            and _clean_optional_str(candidate_meta.creator) is None
        )
        existing_stripped = (
            _clean_optional_str(existing_meta.created) is None
            and _clean_optional_str(existing_meta.creator) is None
        )
        if candidate_stripped != existing_stripped:
            return True
        if candidate_stripped and existing_stripped:
            return candidate_meta.has_unique_content is True
        return False

    return candidate_meta.has_unique_content is True


def evaluate_plagiarism(
    *,
    student_id: uuid.UUID,
    file_hash: str | None,
    metadata: ExtractedMetadata | dict[str, object],
    existing_submissions: Sequence[SubmissionRecordProtocol],
    variants_count: int | None = None,
    format_type: PracticalFormat | None = None,
) -> PlagiarismCheckResult:
    """Детерміновано перевіряє здачу на плагіат за SHA-256, відбитком, шинглами та core.xml."""
    candidate_meta = _coerce_metadata(metadata)
    normalized_hash = file_hash.strip().lower() if file_hash else None
    candidate_fp = _clean_optional_str(candidate_meta.content_fingerprint)
    candidate_created = _clean_optional_str(candidate_meta.created)
    candidate_creator = _clean_optional_str(candidate_meta.creator)
    candidate_modified = _clean_optional_str(candidate_meta.modified)

    for existing in existing_submissions:
        if existing.student_id == student_id:
            continue

        # 1. Точний збіг бінарного / нормалізованого SHA-256 хешу файлу або коду
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
        existing_fp = _clean_optional_str(existing_meta.content_fingerprint)
        existing_created = _clean_optional_str(existing_meta.created)
        existing_creator = _clean_optional_str(existing_meta.creator)
        existing_modified = _clean_optional_str(existing_meta.modified)

        shingle_similarity = compute_shingle_jaccard(
            candidate_meta.text_shingles,
            existing_meta.text_shingles,
        )
        same_created = bool(
            candidate_created and existing_created and candidate_created == existing_created
        )
        same_modified = bool(
            candidate_modified and existing_modified and candidate_modified == existing_modified
        )
        same_non_generic_creator = bool(
            candidate_creator
            and existing_creator
            and " ".join(candidate_creator.casefold().split())
            == " ".join(existing_creator.casefold().split())
            and not _is_generic_creator(candidate_creator)
        )
        same_fingerprint = bool(candidate_fp and existing_fp and candidate_fp == existing_fp)

        # 2. Точний збіг структурного відбитка вмісту (content_fingerprint)
        if same_fingerprint and _is_content_fingerprint_match_actionable(
            candidate_meta=candidate_meta,
            existing_meta=existing_meta,
            shingle_similarity=shingle_similarity,
            same_created=same_created,
            same_modified=same_modified,
            same_non_generic_creator=same_non_generic_creator,
            variants_count=variants_count,
            format_type=format_type,
        ):
            return PlagiarismCheckResult(
                is_flagged=True,
                reason=(
                    "Збіг структурного вмісту роботи з роботою іншого студента "
                    f"(ID здачі: {existing.id})."
                ),
                matched_submission_id=existing.id,
                matched_student_id=existing.student_id,
            )

        # 3. Висока схожість MinHash-шинглів тексту (Jaccard >= 0.85 при len >= 12)
        if (
            shingle_similarity is not None
            and shingle_similarity >= SHINGLE_PLAGIARISM_THRESHOLD
        ):
            similarity_percent = round(shingle_similarity * 100)
            return PlagiarismCheckResult(
                is_flagged=True,
                reason=(
                    f"Висока текстова схожість ({similarity_percent}%) з роботою іншого "
                    f"студента (ID здачі: {existing.id})."
                ),
                matched_submission_id=existing.id,
                matched_student_id=existing.student_id,
            )

        # 4. Метадані docProps/core.xml без хибних спрацювань на шаблони та системні імена
        if same_created:
            corroborators: list[str] = []
            if same_non_generic_creator and candidate_creator is not None:
                corroborators.append(f"creator='{candidate_creator}'")
            if same_modified and candidate_modified is not None:
                corroborators.append(f"modified='{candidate_modified}'")
            if (
                shingle_similarity is not None
                and shingle_similarity >= SHINGLE_CREATED_CORROBORATION_THRESHOLD
            ):
                corroborators.append(f"текстова схожість {round(shingle_similarity * 100)}%")
            if same_fingerprint:
                corroborators.append("збіг структурного вмісту")

            if corroborators:
                details = ", ".join(corroborators)
                return PlagiarismCheckResult(
                    is_flagged=True,
                    reason=(
                        "Виявлено збіг метаданих docProps/core.xml "
                        f"(created='{candidate_created}', {details}) "
                        f"зі здачею іншого студента (ID здачі: {existing.id})."
                    ),
                    matched_submission_id=existing.id,
                    matched_student_id=existing.student_id,
                )

        if same_non_generic_creator and same_modified:
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
    variants_count: int | None = None,
    format_type: PracticalFormat | None = None,
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
        variants_count=variants_count,
        format_type=format_type,
    )
