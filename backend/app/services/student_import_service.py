import io
import re
import secrets
import uuid
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

import docx
from docx.opc.exceptions import PackageNotFoundError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.exceptions import DomainError, InvalidFileFormatError
from app.core.security import hash_password_async
from app.core.upload_utils import format_size_limit_mb
from app.graders.metadata import validate_zip_archive_safety
from app.models.course import Practical
from app.models.user import AcademicGroup, User, UserRole
from app.schemas.auth import (
    ImportedStudentItem,
    ImportSkippedItem,
    StudentImportResponse,
)
from app.services.quiz_service import calculate_variant_index

DEFAULT_COLLEGE_EMAIL_DOMAIN: Final[str] = "kpefk.com.ua"
DEFAULT_TOTAL_VARIANTS: Final[int] = 3
TEMP_PASSWORD_LENGTH: Final[int] = 8
MAX_GROUP_LIST_NUMBER: Final[int] = 100
VARIANT_FORMULA_NOTE: Final[str] = (
    "Індивідуальний варіант кожної практичної роботи обчислюється "
    "автоматично за номером у списку: ((№ - 1) mod K) + 1"
)

UKRAINIAN_ALPHABET: Final[str] = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
_UKRAINIAN_CHAR_RANK: Final[dict[str, int]] = {
    ch: idx for idx, ch in enumerate(UKRAINIAN_ALPHABET)
}

_UKRAINIAN_TRANSLIT_LOWER: Final[dict[str, str]] = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "h",
    "ґ": "g",
    "д": "d",
    "е": "e",
    "є": "ye",
    "ж": "zh",
    "з": "z",
    "и": "y",
    "і": "i",
    "ї": "yi",
    "й": "y",
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
    "ю": "yu",
    "я": "ya",
    "ё": "yo",
    "ы": "y",
    "э": "e",
    "ъ": "",
}

_APOSTROPHE_TRANSLATION: Final[dict[int, str]] = str.maketrans(
    {
        "`": "'",
        "’": "'",
        "‘": "'",
        "ʼ": "'",
        "´": "'",
        "ʹ": "'",
    }
)

_EMPTY_PLACEHOLDERS: Final[frozenset[str]] = frozenset(
    {"", "-", "—", "–", "н/д", "n/a", "none"}
)

_PW_UPPER: Final[str] = "ABCDEFGHJKLMNPQRSTUVWXYZ"
_PW_LOWER: Final[str] = "abcdefghijkmnopqrstuvwxyz"
_PW_DIGITS: Final[str] = "23456789"
_PW_ALL: Final[str] = _PW_UPPER + _PW_LOWER + _PW_DIGITS

_HEADER_FULL_NAME_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "піб",
        "п і б",
        "прізвище",
        "прізвище ім'я по батькові",
        "прізвище, ім'я, по батькові",
        "студент",
        "full name",
        "fullname",
        "full_name",
    }
)
_HEADER_LOGIN_TOKENS: Final[frozenset[str]] = frozenset(
    {"логін", "логин", "login", "username", "обліковий запис"}
)
_HEADER_EMAIL_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "e-mail",
        "email",
        "e mail",
        "пошта",
        "електронна пошта",
        "ел пошта",
        "ел. пошта",
        "mail",
    }
)
_HEADER_PASSWORD_TOKENS: Final[frozenset[str]] = frozenset(
    {"пароль", "password", "тимчасовий пароль", "початковий пароль"}
)
_HEADER_EXTRA_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "дод інформація",
        "дод. інформація",
        "додаткова інформація",
        "примітка",
        "примітки",
        "інформація",
        "extra",
        "notes",
    }
)
_HEADER_INDEX_TOKENS: Final[frozenset[str]] = frozenset(
    {"№", "№ з/п", "№ п/п", "no", "n", "#"}
)

UkrainianWordKey = tuple[tuple[int, int], ...]
UkrainianSortKey = tuple[tuple[UkrainianWordKey, ...], str, str]


@dataclass(frozen=True, slots=True)
class ParsedStudentCandidate:
    """Проміжний валідний запис студента, зчитаний із файлу перед сортуванням."""

    row_number: int
    full_name: str
    explicit_email: str | None
    explicit_password: str | None


@dataclass(frozen=True, slots=True)
class _DocxColumnMap:
    """Індекси колонок таблиці видачі коледжу у документі .docx."""

    full_name_idx: int
    login_idx: int | None = None
    email_idx: int | None = None
    password_idx: int | None = None


def _clean_whitespace(value: str) -> str:
    """Видаляє невидимі символи, нерозривні пробіли та стискає послідовні пробіли."""
    cleaned = value.replace("\u00a0", " ").replace("\u200b", "").replace("\ufeff", "")
    return re.sub(r"\s+", " ", cleaned).strip()


def normalize_full_name(raw_name: str) -> str:
    """Нормалізує ПІБ студента: замінює варіанти апострофа на `'` та очищує пробіли."""
    cleaned = _clean_whitespace(raw_name)
    return cleaned.translate(_APOSTROPHE_TRANSLATION)


def _strip_placeholder(value: str) -> str:
    """Повертає порожній рядок для маркерів на кшталт `-`, `—`, `н/д`."""
    cleaned = _clean_whitespace(value)
    if cleaned.casefold() in _EMPTY_PLACEHOLDERS:
        return ""
    return cleaned


def _encode_ukrainian_word(word: str) -> UkrainianWordKey:
    """Кодує слово у послідовність вагових пар згідно з українською абеткою."""
    encoded: list[tuple[int, int]] = []
    for ch in word.casefold():
        if ch == "'":
            continue
        rank = _UKRAINIAN_CHAR_RANK.get(ch)
        if rank is not None:
            encoded.append((0, rank))
        elif "a" <= ch <= "z":
            encoded.append((1, ord(ch)))
        elif ch.isdigit():
            encoded.append((2, ord(ch)))
        else:
            encoded.append((3, ord(ch)))
    return tuple(encoded)


def ukrainian_sort_key(full_name: str) -> UkrainianSortKey:
    """Повертає ключ сортування ПІБ за правильним порядком української абетки.

    Порядок літер:
    А Б В Г Ґ Д Е Є Ж З И І Ї Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ь Ю Я.
    """
    normalized = normalize_full_name(full_name)
    word_keys = tuple(_encode_ukrainian_word(word) for word in normalized.split())
    return (word_keys, normalized.casefold(), normalized)


def transliterate_ukrainian_slug(text: str) -> str:
    """Транслітерує український рядок у безпечний ASCII-слаг нижнього регістру."""
    normalized = normalize_full_name(text).casefold()
    chars: list[str] = []
    for ch in normalized:
        if ch == "'":
            continue
        mapped = _UKRAINIAN_TRANSLIT_LOWER.get(ch)
        if mapped is not None:
            chars.append(mapped)
        elif ("a" <= ch <= "z") or ch.isdigit() or ch == "-":
            chars.append(ch)
    slug = re.sub(r"-{2,}", "-", "".join(chars)).strip("-")
    return slug


def validate_and_normalize_email(raw_email: str) -> str | None:
    """Нормалізує та перевіряє формат електронної пошти; повертає None при помилці."""
    email = _clean_whitespace(raw_email).lower()
    if (
        not email
        or len(email) > 255
        or " " in email
        or email.count("@") != 1
        or email.startswith("@")
        or email.endswith("@")
    ):
        return None
    local_part, domain_part = email.split("@", maxsplit=1)
    if (
        not local_part
        or local_part.startswith(".")
        or local_part.endswith(".")
        or ".." in local_part
        or "." not in domain_part
        or domain_part.startswith(".")
        or domain_part.endswith(".")
        or ".." in domain_part
    ):
        return None
    return email


def build_generated_email(
    full_name: str,
    reserved_emails: set[str],
    *,
    domain: str = DEFAULT_COLLEGE_EMAIL_DOMAIN,
) -> str:
    """Генерує унікальний транслітерований email формату `{surname}.{initial}@kpefk.com.ua`."""
    words = normalize_full_name(full_name).split()
    surname_slug = transliterate_ukrainian_slug(words[0]) if words else ""
    initial_slug = ""
    if len(words) >= 2:
        given_slug = transliterate_ukrainian_slug(words[1])
        for ch in given_slug:
            if ch.isalnum():
                initial_slug = ch
                break

    if surname_slug and initial_slug:
        base_local = f"{surname_slug}.{initial_slug}"
    elif surname_slug:
        base_local = surname_slug
    else:
        base_local = "student"

    base_local = base_local.strip(".-")[:60] or "student"

    candidate = f"{base_local}@{domain}"
    suffix = 2
    while candidate in reserved_emails:
        candidate = f"{base_local}{suffix}@{domain}"
        suffix += 1

    reserved_emails.add(candidate)
    return candidate


def generate_temp_password(length: int = TEMP_PASSWORD_LENGTH) -> str:
    """Генерує криптографічно стійкий тимчасовий пароль заданої довжини (типово 8 символів)."""
    effective_length = max(length, 6)
    chars: list[str] = [
        secrets.choice(_PW_UPPER),
        secrets.choice(_PW_LOWER),
        secrets.choice(_PW_DIGITS),
    ]
    chars.extend(secrets.choice(_PW_ALL) for _ in range(effective_length - 3))
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def _normalize_header_token(cell_text: str) -> str:
    """Нормалізує текст заголовка колонки для надійного зіставлення."""
    cleaned = _clean_whitespace(cell_text).translate(_APOSTROPHE_TRANSLATION).casefold()
    cleaned = re.sub(r"[.:]+", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _classify_header_cell(cell_text: str) -> str | None:
    """Визначає семантичну роль заголовка колонки таблиці .docx."""
    token = _normalize_header_token(cell_text)
    if not token or len(token) > 48 or "@" in token or any(ch.isdigit() for ch in token):
        return None
    words = set(token.split())
    if token in _HEADER_INDEX_TOKENS:
        return "index"
    if (
        token in _HEADER_FULL_NAME_TOKENS
        or "піб" in words
        or token.startswith("прізвище")
    ):
        return "full_name"
    if (
        token in _HEADER_EMAIL_TOKENS
        or "e-mail" in words
        or "email" in words
        or "пошта" in words
    ):
        return "email"
    if token in _HEADER_LOGIN_TOKENS or "логін" in words or "login" in words:
        return "login"
    if token in _HEADER_PASSWORD_TOKENS or "пароль" in words or "password" in words:
        return "password"
    if (
        token in _HEADER_EXTRA_TOKENS
        or "дод інформац" in token
        or "додаткова інформац" in token
    ):
        return "extra"
    return None


def _detect_docx_header_columns(cells: list[str]) -> _DocxColumnMap | None:
    """Розпізнає рядок заголовків таблиці .docx та повертає карту індексів колонок."""
    roles: dict[str, int] = {}
    matched_count = 0
    for idx, cell_text in enumerate(cells):
        role = _classify_header_cell(cell_text)
        if role is not None:
            matched_count += 1
            if role not in roles:
                roles[role] = idx

    if "full_name" not in roles:
        return None

    # Для багатоколонкової таблиці очікуємо щонайменше 2 заголовки
    # (наприклад, ПІБ + Логін/E-mail/Пароль).
    non_empty_cells = sum(1 for cell in cells if cell)
    if non_empty_cells > 1 and matched_count < 2:
        return None

    return _DocxColumnMap(
        full_name_idx=roles["full_name"],
        login_idx=roles.get("login"),
        email_idx=roles.get("email"),
        password_idx=roles.get("password"),
    )


def _infer_default_docx_columns(cells: list[str]) -> _DocxColumnMap:
    """Визначає позиційну карту колонок таблиці .docx, якщо рядок заголовків відсутній."""
    col_count = len(cells)
    if col_count >= 5 and cells[0].isdigit():
        return _DocxColumnMap(full_name_idx=1, login_idx=2, email_idx=3, password_idx=4)
    if col_count >= 4:
        return _DocxColumnMap(full_name_idx=0, login_idx=1, email_idx=2, password_idx=3)
    if col_count == 3:
        if "@" in cells[1]:
            return _DocxColumnMap(full_name_idx=0, email_idx=1, password_idx=2)
        return _DocxColumnMap(full_name_idx=0, login_idx=1, password_idx=2)
    if col_count == 2:
        if "@" in cells[1]:
            return _DocxColumnMap(full_name_idx=0, email_idx=1)
        return _DocxColumnMap(full_name_idx=0, login_idx=1)
    return _DocxColumnMap(full_name_idx=0)


def _get_cell_value(cells: list[str], idx: int | None) -> str:
    """Безпечно повертає текст комірки за індексом або порожній рядок."""
    if idx is None or idx < 0 or idx >= len(cells):
        return ""
    return cells[idx]


def parse_docx_students(
    file_bytes: bytes,
) -> tuple[list[ParsedStudentCandidate], list[ImportSkippedItem]]:
    """Зчитує список студентів із таблиць офіційної відомості коледжу формату .docx."""
    validate_zip_archive_safety(file_bytes)
    try:
        document = docx.Document(io.BytesIO(file_bytes))
    except (zipfile.BadZipFile, PackageNotFoundError, ValueError, OSError) as exc:
        raise InvalidFileFormatError(
            "Не вдалося прочитати документ .docx — файл пошкоджений або має некоректний формат.",
            context={"error": str(exc)},
        ) from exc

    candidates: list[ParsedStudentCandidate] = []
    skipped: list[ImportSkippedItem] = []
    global_row_number = 0

    for table in document.tables:
        col_map: _DocxColumnMap | None = None

        for row in table.rows:
            cells = [_clean_whitespace(cell.text) for cell in row.cells]
            if not any(cells):
                continue

            # Пропуск об'єднаних рядків-заголовків на всю ширину таблиці (напр., назва групи).
            if len(cells) >= 2 and len(set(cells)) == 1:
                continue

            detected_header = _detect_docx_header_columns(cells)
            if detected_header is not None:
                col_map = detected_header
                continue

            global_row_number += 1
            active_map = col_map if col_map is not None else _infer_default_docx_columns(cells)

            full_name = normalize_full_name(_get_cell_value(cells, active_map.full_name_idx))
            raw_email = _strip_placeholder(_get_cell_value(cells, active_map.email_idx))
            raw_login = _strip_placeholder(_get_cell_value(cells, active_map.login_idx))
            raw_password = _strip_placeholder(_get_cell_value(cells, active_map.password_idx))

            if not full_name:
                skipped.append(
                    ImportSkippedItem(
                        row_number=global_row_number,
                        full_name=None,
                        email=raw_email or raw_login or None,
                        reason="Відсутнє ПІБ студента в рядку таблиці.",
                    )
                )
                continue

            if len(full_name) > 255:
                skipped.append(
                    ImportSkippedItem(
                        row_number=global_row_number,
                        full_name=full_name[:255],
                        email=raw_email or raw_login or None,
                        reason="Довжина ПІБ перевищує допустимі 255 символів.",
                    )
                )
                continue

            explicit_email: str | None = None
            if raw_email:
                normalized_email = validate_and_normalize_email(raw_email)
                if normalized_email is None:
                    skipped.append(
                        ImportSkippedItem(
                            row_number=global_row_number,
                            full_name=full_name,
                            email=raw_email,
                            reason="Некоректний формат електронної пошти.",
                        )
                    )
                    continue
                explicit_email = normalized_email
            elif raw_login:
                email_from_login = (
                    raw_login.lower()
                    if "@" in raw_login
                    else f"{raw_login.lower()}@{DEFAULT_COLLEGE_EMAIL_DOMAIN}"
                )
                normalized_email = validate_and_normalize_email(email_from_login)
                if normalized_email is None:
                    skipped.append(
                        ImportSkippedItem(
                            row_number=global_row_number,
                            full_name=full_name,
                            email=raw_login,
                            reason="Некоректний логін для формування електронної пошти.",
                        )
                    )
                    continue
                explicit_email = normalized_email

            if raw_password and len(raw_password) > 128:
                skipped.append(
                    ImportSkippedItem(
                        row_number=global_row_number,
                        full_name=full_name,
                        email=explicit_email,
                        reason="Довжина пароля перевищує допустимі 128 символів.",
                    )
                )
                continue

            candidates.append(
                ParsedStudentCandidate(
                    row_number=global_row_number,
                    full_name=full_name,
                    explicit_email=explicit_email,
                    explicit_password=raw_password if raw_password else None,
                )
            )

    return candidates, skipped


def _is_txt_header_line(parts: list[str]) -> bool:
    """Перевіряє, чи є рядок текстового файлу рядком заголовків (`ПІБ; email; пароль`)."""
    if not parts:
        return False
    first_role = _classify_header_cell(parts[0])
    if first_role != "full_name":
        return False
    if len(parts) == 1:
        return _normalize_header_token(parts[0]) in _HEADER_FULL_NAME_TOKENS
    second_role = _classify_header_cell(parts[1])
    return second_role in {"email", "login", "password"}


def parse_txt_students(
    file_bytes: bytes,
) -> tuple[list[ParsedStudentCandidate], list[ImportSkippedItem]]:
    """Зчитує список студентів із текстового файлу UTF-8 (.txt).

    Підтримує формати рядків:
    - `ПІБ; email; пароль`
    - `ПІБ; email`
    - `ПІБ`
    Порожні рядки ігноруються.
    """
    try:
        decoded_text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InvalidFileFormatError(
            "Текстовий файл .txt має бути збережений у кодуванні UTF-8.",
            context={"error": str(exc)},
        ) from exc

    candidates: list[ParsedStudentCandidate] = []
    skipped: list[ImportSkippedItem] = []

    for line_number, raw_line in enumerate(decoded_text.splitlines(), start=1):
        stripped_line = raw_line.strip()
        if not stripped_line:
            continue

        parts = [_clean_whitespace(part) for part in stripped_line.split(";")]
        if _is_txt_header_line(parts):
            continue

        full_name = normalize_full_name(parts[0]) if parts else ""
        raw_email = _strip_placeholder(parts[1]) if len(parts) >= 2 else ""
        raw_password = _strip_placeholder(parts[2]) if len(parts) >= 3 else ""

        if not full_name:
            skipped.append(
                ImportSkippedItem(
                    row_number=line_number,
                    full_name=None,
                    email=raw_email or None,
                    reason="Відсутнє ПІБ студента в рядку.",
                )
            )
            continue

        if len(full_name) > 255:
            skipped.append(
                ImportSkippedItem(
                    row_number=line_number,
                    full_name=full_name[:255],
                    email=raw_email or None,
                    reason="Довжина ПІБ перевищує допустимі 255 символів.",
                )
            )
            continue

        explicit_email: str | None = None
        if raw_email:
            normalized_email = validate_and_normalize_email(raw_email)
            if normalized_email is None:
                skipped.append(
                    ImportSkippedItem(
                        row_number=line_number,
                        full_name=full_name,
                        email=raw_email,
                        reason="Некоректний формат електронної пошти.",
                    )
                )
                continue
            explicit_email = normalized_email

        if raw_password and len(raw_password) > 128:
            skipped.append(
                ImportSkippedItem(
                    row_number=line_number,
                    full_name=full_name,
                    email=explicit_email,
                    reason="Довжина пароля перевищує допустимі 128 символів.",
                )
            )
            continue

        candidates.append(
            ParsedStudentCandidate(
                row_number=line_number,
                full_name=full_name,
                explicit_email=explicit_email,
                explicit_password=raw_password if raw_password else None,
            )
        )

    return candidates, skipped


def build_credentials_report(
    report: StudentImportResponse,
    *,
    generated_at: datetime | None = None,
) -> str:
    """Формує текстову відомість облікових даних імпортованих студентів (.txt).

    Замість фіксованого номера варіанта (який залежить від кількості варіантів K
    конкретної практичної роботи) виводить стовпець «№ у списку» та примітку формули.
    """
    timestamp = (
        generated_at.astimezone(UTC)
        if generated_at is not None and generated_at.tzinfo is not None
        else (generated_at.replace(tzinfo=UTC) if generated_at is not None else datetime.now(UTC))
    )
    generated_at_str = timestamp.strftime("%d.%m.%Y %H:%M UTC")

    lines: list[str] = [
        "ЗВІТ ОБЛІКОВИХ ДАНИХ СТУДЕНТІВ (Edu Auto Grader)",
        f"Академічна група: {report.group_code}",
        f"Дата імпорту: {generated_at_str}",
        f"Створено студентів: {report.created_count}",
        f"Пропущено записів: {report.skipped_count}",
        f"Примітка: {VARIANT_FORMULA_NOTE}",
        "=" * 88,
        "№ у списку | ПІБ | E-mail | Пароль",
        "-" * 88,
    ]

    if not report.created:
        lines.append("Нових студентів не створено.")
    else:
        for item in report.created:
            lines.append(
                f"{item.list_number} | {item.full_name} | {item.email} | {item.temp_password}"
            )

    if report.skipped:
        lines.extend(
            [
                "",
                "ПРОПУЩЕНІ ЗАПИСИ ТА ПОМИЛКИ:",
                "-" * 88,
            ]
        )
        for skipped in report.skipped:
            identity_parts: list[str] = [skipped.full_name or "без ПІБ"]
            if skipped.email is not None:
                identity_parts.append(f"<{skipped.email}>")
            lines.append(
                f"Рядок #{skipped.row_number} | {' '.join(identity_parts)} | {skipped.reason}"
            )

    return "\r\n".join(lines) + "\r\n"


class StudentImportService:
    """Сервіс масового імпорту студентів академічної групи з .docx або .txt."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _get_group_or_404(self, group_id: uuid.UUID) -> AcademicGroup:
        """Повертає академічну групу за ID або піднімає DomainError 404."""
        result = await self._db.execute(
            select(AcademicGroup).where(AcademicGroup.id == group_id)
        )
        group = result.scalar_one_or_none()
        if group is None:
            raise DomainError(
                "Академічну групу не знайдено.",
                code="GROUP_NOT_FOUND",
                status_code=404,
                context={"group_id": str(group_id)},
            )
        return group

    async def _resolve_total_variants(self) -> int:
        """Визначає кількість варіантів практичних робіт для розрахунку variant_number."""
        result = await self._db.execute(select(Practical.variants))
        counts = [
            len(raw_variants)
            for raw_variants in result.scalars().all()
            if isinstance(raw_variants, list) and len(raw_variants) > 0
        ]
        if not counts:
            return DEFAULT_TOTAL_VARIANTS
        multi_variant_counts = [count for count in counts if count > 1]
        effective_counts = multi_variant_counts if multi_variant_counts else counts
        frequency = Counter(effective_counts)
        best_count, _best_freq = max(
            frequency.items(),
            key=lambda item: (item[1], item[0]),
        )
        return best_count

    async def import_students(
        self,
        *,
        group_id: uuid.UUID,
        filename: str,
        file_bytes: bytes,
    ) -> StudentImportResponse:
        """Виконує парсинг, українське алфавітне сортування, нумерацію та імпорт студентів."""
        group = await self._get_group_or_404(group_id)

        cleaned_filename = filename.strip()
        lower_filename = cleaned_filename.lower()
        if not (lower_filename.endswith(".docx") or lower_filename.endswith(".txt")):
            raise InvalidFileFormatError(
                "Підтримуються лише файли відомостей у форматах .docx або .txt.",
                context={"filename": cleaned_filename},
            )

        if not file_bytes:
            raise DomainError(
                "Завантажений файл порожній.",
                code="EMPTY_IMPORT_FILE",
                status_code=422,
                context={"filename": cleaned_filename},
            )

        max_import_bytes = settings.MAX_IMPORT_UPLOAD_BYTES
        if len(file_bytes) > max_import_bytes:
            raise DomainError(
                "Розмір файлу перевищує максимально допустимий ліміт "
                f"({format_size_limit_mb(max_import_bytes)}).",
                code="FILE_TOO_LARGE",
                status_code=413,
                context={
                    "size_bytes": len(file_bytes),
                    "max_bytes": max_import_bytes,
                },
            )

        if lower_filename.endswith(".docx"):
            candidates, skipped_items = await run_in_threadpool(
                parse_docx_students,
                file_bytes,
            )
        else:
            candidates, skipped_items = await run_in_threadpool(
                parse_txt_students,
                file_bytes,
            )

        if not candidates and not skipped_items:
            raise DomainError(
                "Файл не містить жодного запису студентів для імпорту.",
                code="EMPTY_IMPORT_FILE",
                status_code=422,
                context={"filename": cleaned_filename},
            )

        # КРИТИЧНО: спочатку сортуємо всіх валідних кандидатів за українською абеткою,
        # і лише після цього присвоюємо list_number та розраховуємо variant_number.
        sorted_candidates = sorted(
            candidates,
            key=lambda item: (ukrainian_sort_key(item.full_name), item.row_number),
        )

        existing_emails_result = await self._db.execute(select(User.email))
        existing_emails: set[str] = {
            email.strip().lower() for email in existing_emails_result.scalars().all()
        }

        max_list_number_result = await self._db.execute(
            select(func.max(User.list_number)).where(
                User.group_id == group.id,
                User.role == UserRole.STUDENT,
            )
        )
        max_existing_list_number = max_list_number_result.scalar_one_or_none()
        next_list_number = (
            int(max_existing_list_number) + 1
            if max_existing_list_number is not None and max_existing_list_number > 0
            else 1
        )

        total_variants = await self._resolve_total_variants()

        # Резервуємо наявні у БД та явні email з файлу, щоб автогенерація не створювала колізій.
        reserved_for_generation: set[str] = set(existing_emails)
        for candidate in sorted_candidates:
            if candidate.explicit_email is not None:
                reserved_for_generation.add(candidate.explicit_email)

        created_emails_in_batch: set[str] = set()
        users_to_create: list[User] = []
        created_items: list[ImportedStudentItem] = []

        for candidate in sorted_candidates:
            if candidate.explicit_email is not None:
                resolved_email = candidate.explicit_email
                if resolved_email in existing_emails:
                    skipped_items.append(
                        ImportSkippedItem(
                            row_number=candidate.row_number,
                            full_name=candidate.full_name,
                            email=resolved_email,
                            reason=(
                                f"Користувач із поштою «{resolved_email}» "
                                "вже зареєстрований у системі."
                            ),
                        )
                    )
                    continue
                if resolved_email in created_emails_in_batch:
                    skipped_items.append(
                        ImportSkippedItem(
                            row_number=candidate.row_number,
                            full_name=candidate.full_name,
                            email=resolved_email,
                            reason=(
                                f"Дублікат електронної пошти «{resolved_email}» "
                                "у завантаженому файлі."
                            ),
                        )
                    )
                    continue
            else:
                resolved_email = build_generated_email(
                    candidate.full_name,
                    reserved_for_generation,
                )

            if next_list_number > MAX_GROUP_LIST_NUMBER:
                skipped_items.append(
                    ImportSkippedItem(
                        row_number=candidate.row_number,
                        full_name=candidate.full_name,
                        email=resolved_email,
                        reason=(
                            "Перевищено максимальний порядковий номер студента в групі "
                            f"({MAX_GROUP_LIST_NUMBER})."
                        ),
                    )
                )
                continue

            temp_password = (
                candidate.explicit_password
                if candidate.explicit_password is not None
                else generate_temp_password()
            )
            assigned_list_number = next_list_number
            next_list_number += 1

            variant_index = calculate_variant_index(assigned_list_number, total_variants)
            variant_number = variant_index + 1

            password_hash = await hash_password_async(temp_password)
            user_id = uuid.uuid4()
            user = User(
                id=user_id,
                email=resolved_email,
                password_hash=password_hash,
                full_name=candidate.full_name,
                role=UserRole.STUDENT,
                group_id=group.id,
                list_number=assigned_list_number,
                must_change_password=True,
            )
            users_to_create.append(user)
            created_emails_in_batch.add(resolved_email)

            created_items.append(
                ImportedStudentItem(
                    user_id=user_id,
                    list_number=assigned_list_number,
                    variant_number=variant_number,
                    full_name=candidate.full_name,
                    email=resolved_email,
                    temp_password=temp_password,
                )
            )

        if users_to_create:
            self._db.add_all(users_to_create)
            await self._db.commit()

        return StudentImportResponse(
            group_id=group.id,
            group_code=group.code,
            total_variants=total_variants,
            created_count=len(created_items),
            skipped_count=len(skipped_items),
            created=created_items,
            skipped=skipped_items,
        )
