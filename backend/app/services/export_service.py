import io
import re
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import quote

import openpyxl  # type: ignore[import-untyped]
from fpdf import FPDF
from openpyxl.styles import (  # type: ignore[import-untyped]
    Alignment,
    Border,
    Font,
    PatternFill,
    Side,
)
from openpyxl.utils.cell import get_column_letter  # type: ignore[import-untyped]
from openpyxl.worksheet.worksheet import Worksheet  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.concurrency import run_in_threadpool

from app.core.exceptions import DomainError
from app.models.course import Course, CourseSlug, Module, Practical
from app.models.progress import Submission
from app.models.user import AcademicGroup, User, UserRole
from app.schemas.auth import AcademicGroupRead
from app.schemas.grading import GradingReport
from app.schemas.submission import (
    CriterionErrorStat,
    ExportFormat,
    GroupJournalPracticalRead,
    GroupJournalRead,
    GroupJournalRow,
    GroupJournalStudentCell,
)

XLSX_MEDIA_TYPE: str = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
PDF_MEDIA_TYPE: str = "application/pdf"
MAX_PRACTICALS_PER_PDF_PAGE: int = 10

_FORMULA_INJECTION_PREFIXES: tuple[str, ...] = ("=", "+", "-", "@", "\t", "\r")

_COURSE_SLUG_ORDER: dict[CourseSlug, int] = {
    CourseSlug.WORD: 0,
    CourseSlug.EXCEL: 1,
    CourseSlug.ACCESS: 2,
    CourseSlug.HTML: 3,
}

_COURSE_SHORT_LABELS: dict[CourseSlug, str] = {
    CourseSlug.WORD: "W",
    CourseSlug.EXCEL: "E",
    CourseSlug.ACCESS: "A",
    CourseSlug.HTML: "H",
}

_FONT_CANDIDATE_PAIRS: tuple[tuple[str, str], ...] = (
    (
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ),
    (
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
    ),
    (
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/tahomabd.ttf",
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ),
    (
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ),
    (
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ),
    (
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ),
    (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ),
)

_UKRAINIAN_TRANSLIT_MAP: dict[str, str] = {
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
    "’": "'",
    "ʼ": "'",
    "«": '"',
    "»": '"',
    "—": "-",
    "–": "-",
    "№": "No.",
}


@dataclass(frozen=True, slots=True)
class PracticalColumnInfo:
    """Метадані стовпця практичної роботи для побудови зведеної відомості групи."""

    practical_id: uuid.UUID
    practical_title: str
    course_slug: CourseSlug
    course_title: str
    module_order_index: int
    max_score: float
    needs_rules_review: bool = False


@dataclass(frozen=True, slots=True)
class GroupJournalBundle:
    """Зібраний пакет даних відомості групи разом із метаданими практичних робіт."""

    group: AcademicGroupRead
    practicals: list[PracticalColumnInfo]
    journal: GroupJournalRead


@dataclass(frozen=True, slots=True)
class ExportedDocument:
    """Згенерований бінарний файл відомості успішності (.xlsx або .pdf)."""

    content: bytes
    media_type: str
    filename: str
    content_disposition: str
    export_format: ExportFormat


@dataclass(slots=True)
class _RuleStatAccumulator:
    """Внутрішній акумулятор статистики помилок за окремим правилом автоперевірки."""

    rule_id: str
    description: str
    total_attempts: int = 0
    failure_count: int = 0


def _transliterate_to_ascii(text: str) -> str:
    """Транслітерує український текст у безпечний Latin-1/ASCII для fallback-шрифтів PDF."""
    characters: list[str] = []
    for char in text:
        if char in _UKRAINIAN_TRANSLIT_MAP:
            characters.append(_UKRAINIAN_TRANSLIT_MAP[char])
        elif ord(char) < 128:
            characters.append(char)
        else:
            characters.append("?")
    return "".join(characters)


def _sanitize_filename_token(raw_value: str) -> str:
    """Перетворює шифр групи на безпечний ASCII-токен для HTTP Content-Disposition."""
    transliterated = _transliterate_to_ascii(raw_value.strip())
    sanitized = re.sub(r"[^A-Za-z0-9_-]+", "_", transliterated).strip("_")
    return sanitized or "group"


def build_content_disposition(filename_ascii: str, filename_utf8: str) -> str:
    """Формує заголовок Content-Disposition за стандартом RFC 5987 для завантаження файлу."""
    encoded_utf8 = quote(filename_utf8, safe="")
    return f'attachment; filename="{filename_ascii}"; filename*=UTF-8\'\'{encoded_utf8}'


def _normalize_utc_timestamp(value: datetime) -> datetime:
    """Нормалізує мітку часу до UTC для безпечного порівняння naive/aware значень."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def calculate_criterion_error_stats(
    submissions: Sequence[Submission],
) -> list[CriterionErrorStat]:
    """Розраховує аналітичну статистику помилок студентів групи по критеріях перевірки."""
    accumulators: dict[str, _RuleStatAccumulator] = {}

    ordered_submissions = sorted(
        submissions,
        key=lambda item: (_normalize_utc_timestamp(item.submitted_at), str(item.id)),
    )
    for submission in ordered_submissions:
        raw_report = submission.grading_report
        if not isinstance(raw_report, dict) or not raw_report:
            continue
        try:
            report = GradingReport.model_validate(raw_report)
        except Exception:
            continue

        for result in report.results:
            acc = accumulators.get(result.rule_id)
            if acc is None:
                acc = _RuleStatAccumulator(
                    rule_id=result.rule_id,
                    description=result.description,
                )
                accumulators[result.rule_id] = acc
            acc.total_attempts += 1
            if not result.passed:
                acc.failure_count += 1

    stats: list[CriterionErrorStat] = []
    for acc in accumulators.values():
        failure_rate = (
            round((acc.failure_count / acc.total_attempts) * 100.0, 2)
            if acc.total_attempts > 0
            else 0.0
        )
        stats.append(
            CriterionErrorStat(
                rule_id=acc.rule_id,
                description=acc.description,
                total_attempts=acc.total_attempts,
                failure_count=acc.failure_count,
                failure_rate_percent=failure_rate,
            )
        )

    stats.sort(
        key=lambda item: (
            -item.failure_rate_percent,
            -item.failure_count,
            item.rule_id,
        )
    )
    return stats


def sanitize_spreadsheet_text(value: str) -> str:
    """Нейтралізує провідні символи формул для захисту від Spreadsheet Formula Injection."""
    if not value:
        return value
    if value.startswith(_FORMULA_INJECTION_PREFIXES) or value.lstrip().startswith(
        _FORMULA_INJECTION_PREFIXES
    ):
        return f"'{value}"
    return value


def _set_xlsx_text_cell(
    worksheet: Worksheet,
    *,
    row: int,
    column: int,
    text: str,
    font: Font | None = None,
    fill: PatternFill | None = None,
    border: Border | None = None,
    alignment: Alignment | None = None,
) -> None:
    """Записує екранований текст у клітинку XLSX із явним строковим типом даних 's'."""
    cell = worksheet.cell(row=row, column=column)
    cell.value = sanitize_spreadsheet_text(text)
    cell.data_type = "s"
    if font is not None:
        cell.font = font
    if fill is not None:
        cell.fill = fill
    if border is not None:
        cell.border = border
    if alignment is not None:
        cell.alignment = alignment


def _resolve_practical_columns(
    journal: GroupJournalRead,
    practicals: Sequence[PracticalColumnInfo] | None,
) -> list[PracticalColumnInfo]:
    """Визначає впорядкований перелік колонок практичних робіт для експорту відомості."""
    if practicals is not None and len(practicals) > 0:
        return list(practicals)
    if practicals is None and journal.practicals:
        return [
            PracticalColumnInfo(
                practical_id=item.practical_id,
                practical_title=item.title,
                course_slug=item.course_slug,
                course_title=item.course_slug.value.upper(),
                module_order_index=item.module_order_index,
                max_score=item.max_score,
                needs_rules_review=item.needs_rules_review,
            )
            for item in journal.practicals
        ]
    if practicals is not None:
        return []
    if journal.rows:
        return [
            PracticalColumnInfo(
                practical_id=cell.practical_id,
                practical_title=f"Практична робота №{idx}",
                course_slug=CourseSlug.WORD,
                course_title="Курс",
                module_order_index=idx,
                max_score=10.0,
            )
            for idx, cell in enumerate(journal.rows[0].cells, start=1)
        ]
    return []


def build_group_journal(
    *,
    group: AcademicGroup,
    students: Sequence[User],
    practicals: Sequence[PracticalColumnInfo],
    submissions: Sequence[Submission],
) -> GroupJournalRead:
    """Формує зведену відомість успішності групи з рядками студентів та статистикою помилок."""
    ordered_students = sorted(
        students,
        key=lambda user: (
            user.list_number is None,
            user.list_number if user.list_number is not None else 0,
            user.full_name.lower(),
            str(user.id),
        ),
    )

    allowed_student_ids = {student.id for student in ordered_students}
    allowed_practical_ids = {info.practical_id for info in practicals}
    best_by_pair: dict[tuple[uuid.UUID, uuid.UUID], Submission] = {}
    ordered_submissions_best = sorted(
        submissions,
        key=lambda item: (
            Decimal(str(item.final_score)),
            _normalize_utc_timestamp(item.submitted_at),
            str(item.id),
        ),
        reverse=True,
    )
    for submission in ordered_submissions_best:
        if (
            submission.student_id not in allowed_student_ids
            or submission.practical_id not in allowed_practical_ids
        ):
            continue
        key = (submission.student_id, submission.practical_id)
        if key not in best_by_pair:
            best_by_pair[key] = submission

    rows: list[GroupJournalRow] = []
    for student in ordered_students:
        cells: list[GroupJournalStudentCell] = []
        total_score = 0.0

        for practical_info in practicals:
            matched = best_by_pair.get((student.id, practical_info.practical_id))
            if matched is None:
                cells.append(
                    GroupJournalStudentCell(
                        practical_id=practical_info.practical_id,
                        submission_id=None,
                        auto_score=None,
                        final_score=None,
                        is_plagiarism_flagged=False,
                        plagiarism_reason=None,
                        submitted_at=None,
                    )
                )
            else:
                final_score_float = round(float(matched.final_score), 2)
                auto_score_float = round(float(matched.auto_score), 2)
                total_score += final_score_float
                cells.append(
                    GroupJournalStudentCell(
                        practical_id=practical_info.practical_id,
                        submission_id=matched.id,
                        auto_score=auto_score_float,
                        final_score=final_score_float,
                        is_plagiarism_flagged=matched.is_plagiarism_flagged,
                        plagiarism_reason=matched.plagiarism_reason,
                        submitted_at=matched.submitted_at,
                    )
                )

        rows.append(
            GroupJournalRow(
                student_id=student.id,
                student_full_name=student.full_name,
                list_number=student.list_number,
                cells=cells,
                total_score=round(total_score, 2),
            )
        )

    # Передаємо виключно дедупліковані актуальні здачі (1 найкраща здача на пару студент–практична).
    error_stats = calculate_criterion_error_stats(list(best_by_pair.values()))
    practical_headers = [
        GroupJournalPracticalRead(
            practical_id=info.practical_id,
            title=info.practical_title,
            course_slug=info.course_slug,
            module_order_index=info.module_order_index,
            max_score=info.max_score,
            needs_rules_review=info.needs_rules_review,
        )
        for info in practicals
    ]
    return GroupJournalRead(
        group_id=group.id,
        group_code=group.code,
        specialty=group.specialty,
        practicals=practical_headers,
        rows=rows,
        error_stats=error_stats,
    )


def _auto_adjust_worksheet_columns(worksheet: Worksheet) -> None:
    """Автоматично підбирає ширину стовпців аркуша Excel за довжиною вмісту комірок."""
    for col_idx in range(1, worksheet.max_column + 1):
        col_letter = get_column_letter(col_idx)
        max_len = 10
        for row_idx in range(1, worksheet.max_row + 1):
            cell_val = worksheet.cell(row=row_idx, column=col_idx).value
            if cell_val is not None:
                text_len = len(str(cell_val))
                if row_idx > 2 and text_len > max_len:
                    max_len = text_len
        worksheet.column_dimensions[col_letter].width = min(max_len + 4, 48)


def render_group_journal_xlsx(
    journal: GroupJournalRead,
    practicals: Sequence[PracticalColumnInfo] | None = None,
) -> bytes:
    """Генерує зведену відомість успішності групи та статистику помилок у форматі .xlsx."""
    resolved_practicals = _resolve_practical_columns(journal, practicals)

    workbook = openpyxl.Workbook()
    sheet: Worksheet = workbook.active
    sheet.title = "Відомість успішності"

    thin_side = Side(border_style="thin", color="CBD5E1")
    cell_border = Border(
        left=thin_side,
        right=thin_side,
        top=thin_side,
        bottom=thin_side,
    )
    title_font = Font(name="Calibri", size=14, bold=True, color="0F172A")
    subtitle_font = Font(name="Calibri", size=10, italic=True, color="475569")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(
        fill_type="solid",
        start_color="1E3A8A",
        end_color="1E3A8A",
    )
    data_font = Font(name="Calibri", size=11, color="0F172A")
    total_font = Font(name="Calibri", size=11, bold=True, color="0F172A")
    plagiarism_fill = PatternFill(
        fill_type="solid",
        start_color="FEE2E2",
        end_color="FEE2E2",
    )
    plagiarism_font = Font(name="Calibri", size=11, bold=True, color="991B1B")

    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    left_wrap_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    generated_at_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    _set_xlsx_text_cell(
        sheet,
        row=1,
        column=1,
        text=(
            f"Зведена відомість успішності групи {journal.group_code} "
            f"({journal.specialty})"
        ),
        font=title_font,
    )
    _set_xlsx_text_cell(
        sheet,
        row=2,
        column=1,
        text=f"Сформовано: {generated_at_str} | Студентів: {len(journal.rows)}",
        font=subtitle_font,
    )

    practical_headers = [
        (
            f"{info.course_slug.value.upper()}: {info.practical_title} "
            f"(макс. {info.max_score:.2f})"
        )
        for info in resolved_practicals
    ]
    headers = [
        "№ з/п",
        "ПІБ студента",
        *practical_headers,
        "Сумарний бал",
        "Антиплагіат",
    ]

    header_row_idx = 4
    for col_idx, header_text in enumerate(headers, start=1):
        _set_xlsx_text_cell(
            sheet,
            row=header_row_idx,
            column=col_idx,
            text=header_text,
            font=header_font,
            fill=header_fill,
            border=cell_border,
            alignment=header_align,
        )

    plagiarism_incidents: list[tuple[int, str, str, str, float | None, str]] = []
    cell_by_practical_for_row: dict[uuid.UUID, GroupJournalStudentCell]
    resolved_practical_ids = {p.practical_id for p in resolved_practicals}

    for student_idx, row_data in enumerate(journal.rows, start=1):
        excel_row = header_row_idx + student_idx
        list_num = (
            row_data.list_number
            if row_data.list_number is not None
            else student_idx
        )

        num_cell = sheet.cell(row=excel_row, column=1, value=list_num)
        num_cell.font = data_font
        num_cell.border = cell_border
        num_cell.alignment = center_align

        _set_xlsx_text_cell(
            sheet,
            row=excel_row,
            column=2,
            text=row_data.student_full_name,
            font=data_font,
            border=cell_border,
            alignment=left_align,
        )

        cell_by_practical_for_row = {
            item.practical_id: item for item in row_data.cells
        }
        flagged_reasons: list[str] = []

        for p_idx, practical_info in enumerate(resolved_practicals, start=3):
            student_cell = cell_by_practical_for_row.get(
                practical_info.practical_id
            )

            if student_cell is None or student_cell.final_score is None:
                _set_xlsx_text_cell(
                    sheet,
                    row=excel_row,
                    column=p_idx,
                    text="—",
                    font=data_font,
                    border=cell_border,
                    alignment=center_align,
                )
            else:
                score_cell = sheet.cell(
                    row=excel_row,
                    column=p_idx,
                    value=round(student_cell.final_score, 2),
                )
                score_cell.border = cell_border
                score_cell.alignment = center_align
                score_cell.number_format = "0.00"
                if student_cell.is_plagiarism_flagged:
                    score_cell.fill = plagiarism_fill
                    score_cell.font = plagiarism_font
                    raw_reason = (
                        student_cell.plagiarism_reason
                        or "Підозра на академічний плагіат"
                    )
                    safe_reason = sanitize_spreadsheet_text(raw_reason)
                    flagged_reasons.append(
                        f"{practical_info.course_slug.value.upper()}: {safe_reason}"
                    )
                    plagiarism_incidents.append(
                        (
                            list_num,
                            row_data.student_full_name,
                            practical_info.course_slug.value.upper(),
                            practical_info.practical_title,
                            round(student_cell.final_score, 2),
                            raw_reason,
                        )
                    )
                else:
                    score_cell.font = data_font

        for extra_cell in row_data.cells:
            if (
                extra_cell.is_plagiarism_flagged
                and extra_cell.practical_id not in resolved_practical_ids
            ):
                raw_extra_reason = (
                    extra_cell.plagiarism_reason
                    or "Підозра на академічний плагіат"
                )
                flagged_reasons.append(sanitize_spreadsheet_text(raw_extra_reason))
                plagiarism_incidents.append(
                    (
                        list_num,
                        row_data.student_full_name,
                        "—",
                        str(extra_cell.practical_id),
                        (
                            round(extra_cell.final_score, 2)
                            if extra_cell.final_score is not None
                            else None
                        ),
                        raw_extra_reason,
                    )
                )

        total_col_idx = 3 + len(resolved_practicals)
        total_cell = sheet.cell(
            row=excel_row,
            column=total_col_idx,
            value=round(row_data.total_score, 2),
        )
        total_cell.font = total_font
        total_cell.border = cell_border
        total_cell.number_format = "0.00"
        total_cell.alignment = center_align

        status_col_idx = total_col_idx + 1
        if flagged_reasons:
            _set_xlsx_text_cell(
                sheet,
                row=excel_row,
                column=status_col_idx,
                text=f"ПЛАГІАТ: {'; '.join(flagged_reasons)}",
                font=plagiarism_font,
                fill=plagiarism_fill,
                border=cell_border,
                alignment=left_wrap_align,
            )
        else:
            _set_xlsx_text_cell(
                sheet,
                row=excel_row,
                column=status_col_idx,
                text="ОК",
                font=data_font,
                border=cell_border,
                alignment=center_align,
            )

    _auto_adjust_worksheet_columns(sheet)

    stats_sheet: Worksheet = workbook.create_sheet(title="Статистика помилок")
    stats_headers = [
        "ID правила",
        "Опис критерію",
        "Усього спроб",
        "Кількість помилок",
        "Частка помилок (%)",
    ]
    for col_idx, header_text in enumerate(stats_headers, start=1):
        _set_xlsx_text_cell(
            stats_sheet,
            row=1,
            column=col_idx,
            text=header_text,
            font=header_font,
            fill=header_fill,
            border=cell_border,
            alignment=center_align,
        )

    for stat_idx, stat in enumerate(journal.error_stats, start=2):
        _set_xlsx_text_cell(
            stats_sheet,
            row=stat_idx,
            column=1,
            text=stat.rule_id,
            font=data_font,
            border=cell_border,
            alignment=left_align,
        )
        _set_xlsx_text_cell(
            stats_sheet,
            row=stat_idx,
            column=2,
            text=stat.description,
            font=data_font,
            border=cell_border,
            alignment=left_wrap_align,
        )

        attempts_cell = stats_sheet.cell(
            row=stat_idx,
            column=3,
            value=stat.total_attempts,
        )
        attempts_cell.font = data_font
        attempts_cell.border = cell_border
        attempts_cell.alignment = center_align

        failures_cell = stats_sheet.cell(
            row=stat_idx,
            column=4,
            value=stat.failure_count,
        )
        failures_cell.font = data_font
        failures_cell.border = cell_border
        failures_cell.alignment = center_align

        rate_cell = stats_sheet.cell(
            row=stat_idx,
            column=5,
            value=round(stat.failure_rate_percent, 2),
        )
        rate_cell.font = data_font
        rate_cell.border = cell_border
        rate_cell.number_format = "0.00"
        rate_cell.alignment = center_align

    _auto_adjust_worksheet_columns(stats_sheet)

    plagiarism_sheet: Worksheet = workbook.create_sheet(title="Антиплагіат")
    plagiarism_headers = [
        "№ з/п",
        "ПІБ студента",
        "Курс",
        "Практична робота",
        "Бал",
        "Причина підозри",
    ]
    for col_idx, header_text in enumerate(plagiarism_headers, start=1):
        _set_xlsx_text_cell(
            plagiarism_sheet,
            row=1,
            column=col_idx,
            text=header_text,
            font=header_font,
            fill=header_fill,
            border=cell_border,
            alignment=center_align,
        )

    for incident_idx, incident in enumerate(plagiarism_incidents, start=2):
        inc_list_num, inc_name, inc_course, inc_title, inc_score, inc_reason = incident

        inc_num_cell = plagiarism_sheet.cell(
            row=incident_idx,
            column=1,
            value=inc_list_num,
        )
        inc_num_cell.font = data_font
        inc_num_cell.border = cell_border
        inc_num_cell.alignment = center_align

        _set_xlsx_text_cell(
            plagiarism_sheet,
            row=incident_idx,
            column=2,
            text=inc_name,
            font=data_font,
            border=cell_border,
            alignment=left_align,
        )
        _set_xlsx_text_cell(
            plagiarism_sheet,
            row=incident_idx,
            column=3,
            text=inc_course,
            font=data_font,
            border=cell_border,
            alignment=center_align,
        )
        _set_xlsx_text_cell(
            plagiarism_sheet,
            row=incident_idx,
            column=4,
            text=inc_title,
            font=data_font,
            border=cell_border,
            alignment=left_wrap_align,
        )
        if inc_score is None:
            _set_xlsx_text_cell(
                plagiarism_sheet,
                row=incident_idx,
                column=5,
                text="—",
                font=data_font,
                border=cell_border,
                alignment=center_align,
            )
        else:
            inc_score_cell = plagiarism_sheet.cell(
                row=incident_idx,
                column=5,
                value=inc_score,
            )
            inc_score_cell.font = plagiarism_font
            inc_score_cell.fill = plagiarism_fill
            inc_score_cell.border = cell_border
            inc_score_cell.number_format = "0.00"
            inc_score_cell.alignment = center_align

        _set_xlsx_text_cell(
            plagiarism_sheet,
            row=incident_idx,
            column=6,
            text=inc_reason,
            font=plagiarism_font,
            fill=plagiarism_fill,
            border=cell_border,
            alignment=left_wrap_align,
        )

    _auto_adjust_worksheet_columns(plagiarism_sheet)

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _configure_pdf_font(pdf: FPDF) -> tuple[str, bool]:
    """Реєструє системний Unicode TTF-шрифт із підтримкою кирилиці або повертає fallback."""
    for regular_path_str, bold_path_str in _FONT_CANDIDATE_PAIRS:
        regular_path = Path(regular_path_str)
        if not regular_path.is_file():
            continue
        bold_path = Path(bold_path_str)
        resolved_bold = bold_path if bold_path.is_file() else regular_path
        pdf.add_font("ReportSans", style="", fname=str(regular_path))
        pdf.add_font("ReportSans", style="B", fname=str(resolved_bold))
        return "ReportSans", True

    return "Helvetica", False


def _prepare_pdf_text(text: str, *, unicode_supported: bool) -> str:
    """Готує рядок до виводу у PDF (залишає Unicode або транслітерує для Latin-1)."""
    if unicode_supported:
        return text
    return _transliterate_to_ascii(text)


def _format_pdf_score(score: float, *, flagged: bool = False) -> str:
    """Форматує бал компактно для PDF-клітинок (наприклад: 10, 8.5, 8.5*)."""
    rounded = round(score, 2)
    if rounded == 0:
        rounded = 0.0
    formatted = f"{rounded:.2f}"
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")
    return f"{formatted}*" if flagged else formatted


def _fit_pdf_text(pdf: FPDF, text: str, max_width_mm: float) -> str:
    """Обрізає текст із трикрапкою так, щоб він гарантовано вміщався у ширину клітинки PDF."""
    normalized = re.sub(r"[\r\n\t]+", " ", text).strip()
    available_width = max_width_mm - (2.0 * float(pdf.c_margin)) - 0.2
    if not normalized or available_width <= 0.0:
        return ""
    if float(pdf.get_string_width(normalized)) <= available_width:
        return normalized

    ellipsis = "..."
    if float(pdf.get_string_width(ellipsis)) > available_width:
        low, high = 0, len(normalized)
        while low < high:
            mid = (low + high + 1) // 2
            if float(pdf.get_string_width(normalized[:mid])) <= available_width:
                low = mid
            else:
                high = mid - 1
        return normalized[:low]

    low, high = 0, len(normalized)
    while low < high:
        mid = (low + high + 1) // 2
        candidate = f"{normalized[:mid].rstrip()}{ellipsis}"
        if float(pdf.get_string_width(candidate)) <= available_width:
            low = mid
        else:
            high = mid - 1
    if low == 0:
        return ellipsis
    return f"{normalized[:low].rstrip()}{ellipsis}"


def render_group_journal_pdf(
    journal: GroupJournalRead,
    practicals: Sequence[PracticalColumnInfo] | None = None,
) -> bytes:
    """Генерує зведену відомість успішності групи та аналітику помилок у форматі .pdf."""
    resolved_practicals = _resolve_practical_columns(journal, practicals)
    indexed_practicals: list[tuple[int, PracticalColumnInfo]] = list(
        enumerate(resolved_practicals, start=1)
    )
    if indexed_practicals:
        practical_chunks: list[list[tuple[int, PracticalColumnInfo]]] = [
            indexed_practicals[start : start + MAX_PRACTICALS_PER_PDF_PAGE]
            for start in range(0, len(indexed_practicals), MAX_PRACTICALS_PER_PDF_PAGE)
        ]
    else:
        practical_chunks = [[]]

    total_chunks = len(practical_chunks)
    generated_at_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    font_family, unicode_ok = _configure_pdf_font(pdf)

    usable_w = float(pdf.epw)
    num_w = 11.0
    base_name_w = 60.0
    total_w = 18.0
    avg_w = 18.0
    notes_w = 28.0
    header_h = 8.0
    row_h = 7.0

    def _draw_page_header(
        *,
        chunk_index: int,
        chunk_items: list[tuple[int, PracticalColumnInfo]],
    ) -> None:
        pdf.set_text_color(15, 23, 42)
        pdf.set_font(font_family, style="B", size=13)
        title_raw = f"ЗВЕДЕНА ВІДОМІСТЬ УСПІШНОСТІ ГРУПИ {journal.group_code}"
        title_text = _fit_pdf_text(
            pdf,
            _prepare_pdf_text(title_raw, unicode_supported=unicode_ok),
            usable_w,
        )
        pdf.cell(w=usable_w, h=8, text=title_text, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(font_family, style="", size=9.5)
        subtitle_raw = (
            f"Спеціальність: {journal.specialty} | Студентів: {len(journal.rows)} | "
            f"Дата формування: {generated_at_str}"
        )
        subtitle_text = _fit_pdf_text(
            pdf,
            _prepare_pdf_text(subtitle_raw, unicode_supported=unicode_ok),
            usable_w,
        )
        pdf.cell(w=usable_w, h=5.5, text=subtitle_text, new_x="LMARGIN", new_y="NEXT")

        if total_chunks > 1 and chunk_items:
            first_num = chunk_items[0][0]
            last_num = chunk_items[-1][0]
            pdf.set_font(font_family, style="B", size=9.5)
            part_raw = (
                f"Частина {chunk_index + 1} з {total_chunks} "
                f"(роботи {first_num}–{last_num})"
            )
            part_text = _fit_pdf_text(
                pdf,
                _prepare_pdf_text(part_raw, unicode_supported=unicode_ok),
                usable_w,
            )
            pdf.cell(w=usable_w, h=5.5, text=part_text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2.5)

    def _draw_table_header(
        *,
        chunk_items: list[tuple[int, PracticalColumnInfo]],
        name_w: float,
        single_practical_w: float,
        include_summary: bool,
    ) -> None:
        pdf.set_font(font_family, style="B", size=8.5)
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)

        pdf.cell(
            w=num_w,
            h=header_h,
            text=_fit_pdf_text(
                pdf,
                _prepare_pdf_text("№", unicode_supported=unicode_ok),
                num_w,
            ),
            border=1,
            align="C",
            fill=True,
        )
        pdf.cell(
            w=name_w,
            h=header_h,
            text=_fit_pdf_text(
                pdf,
                _prepare_pdf_text("ПІБ студента", unicode_supported=unicode_ok),
                name_w,
            ),
            border=1,
            align="L",
            fill=True,
        )

        inner_practical_w = single_practical_w - (2.0 * float(pdf.c_margin)) - 0.2
        for item_idx, (p_num, p_info) in enumerate(chunk_items):
            is_rightmost = not include_summary and item_idx == len(chunk_items) - 1
            full_label = _prepare_pdf_text(
                f"П{p_num} ({p_info.course_slug.value.upper()})",
                unicode_supported=unicode_ok,
            )
            short_code = _COURSE_SHORT_LABELS.get(
                p_info.course_slug,
                p_info.course_slug.value[:1].upper(),
            )
            compact_label = _prepare_pdf_text(
                f"П{p_num} ({short_code})",
                unicode_supported=unicode_ok,
            )
            chosen_label = (
                full_label
                if float(pdf.get_string_width(full_label)) <= inner_practical_w
                else compact_label
            )
            fitted_label = _fit_pdf_text(pdf, chosen_label, single_practical_w)
            pdf.cell(
                w=single_practical_w,
                h=header_h,
                text=fitted_label,
                border=1,
                align="C",
                fill=True,
                new_x="LMARGIN" if is_rightmost else "RIGHT",
                new_y="NEXT" if is_rightmost else "TOP",
            )

        if include_summary:
            pdf.cell(
                w=total_w,
                h=header_h,
                text=_fit_pdf_text(
                    pdf,
                    _prepare_pdf_text("Сума", unicode_supported=unicode_ok),
                    total_w,
                ),
                border=1,
                align="C",
                fill=True,
            )
            pdf.cell(
                w=avg_w,
                h=header_h,
                text=_fit_pdf_text(
                    pdf,
                    _prepare_pdf_text("Середній", unicode_supported=unicode_ok),
                    avg_w,
                ),
                border=1,
                align="C",
                fill=True,
            )
            pdf.cell(
                w=notes_w,
                h=header_h,
                text=_fit_pdf_text(
                    pdf,
                    _prepare_pdf_text("Примітки", unicode_supported=unicode_ok),
                    notes_w,
                ),
                border=1,
                align="C",
                fill=True,
                new_x="LMARGIN",
                new_y="NEXT",
            )

    for chunk_idx, chunk_items in enumerate(practical_chunks):
        pdf.add_page()
        include_summary = chunk_idx == total_chunks - 1
        summary_w = (total_w + avg_w + notes_w) if include_summary else 0.0
        chunk_count = len(chunk_items)
        if chunk_count > 0:
            name_w = base_name_w
            available_practicals_w = usable_w - (num_w + name_w + summary_w)
            single_practical_w = available_practicals_w / chunk_count
        else:
            name_w = usable_w - (num_w + summary_w)
            single_practical_w = 0.0

        _draw_page_header(chunk_index=chunk_idx, chunk_items=chunk_items)
        _draw_table_header(
            chunk_items=chunk_items,
            name_w=name_w,
            single_practical_w=single_practical_w,
            include_summary=include_summary,
        )

        pdf.set_text_color(15, 23, 42)
        pdf.set_font(font_family, style="", size=8.5)

        for row_idx, row_data in enumerate(journal.rows, start=1):
            if float(pdf.get_y()) + row_h > float(pdf.page_break_trigger):
                pdf.add_page()
                _draw_page_header(chunk_index=chunk_idx, chunk_items=chunk_items)
                _draw_table_header(
                    chunk_items=chunk_items,
                    name_w=name_w,
                    single_practical_w=single_practical_w,
                    include_summary=include_summary,
                )
                pdf.set_text_color(15, 23, 42)
                pdf.set_font(font_family, style="", size=8.5)

            list_num = (
                row_data.list_number
                if row_data.list_number is not None
                else row_idx
            )
            cell_map = {item.practical_id: item for item in row_data.cells}

            pdf.cell(
                w=num_w,
                h=row_h,
                text=_fit_pdf_text(pdf, str(list_num), num_w),
                border=1,
                align="C",
            )
            prepared_name = _prepare_pdf_text(
                row_data.student_full_name,
                unicode_supported=unicode_ok,
            )
            pdf.cell(
                w=name_w,
                h=row_h,
                text=_fit_pdf_text(pdf, prepared_name, name_w),
                border=1,
                align="L",
            )

            for item_idx, (_p_num, p_info) in enumerate(chunk_items):
                is_rightmost = (
                    not include_summary and item_idx == len(chunk_items) - 1
                )
                st_cell = cell_map.get(p_info.practical_id)
                if st_cell is None or st_cell.final_score is None:
                    val_text = "-"
                else:
                    val_text = _format_pdf_score(
                        st_cell.final_score,
                        flagged=st_cell.is_plagiarism_flagged,
                    )
                pdf.cell(
                    w=single_practical_w,
                    h=row_h,
                    text=_fit_pdf_text(
                        pdf,
                        _prepare_pdf_text(val_text, unicode_supported=unicode_ok),
                        single_practical_w,
                    ),
                    border=1,
                    align="C",
                    new_x="LMARGIN" if is_rightmost else "RIGHT",
                    new_y="NEXT" if is_rightmost else "TOP",
                )

            if include_summary:
                scored_values = [
                    st_cell.final_score
                    for p_info in resolved_practicals
                    if (st_cell := cell_map.get(p_info.practical_id)) is not None
                    and st_cell.final_score is not None
                ]
                avg_text = (
                    _format_pdf_score(sum(scored_values) / len(scored_values))
                    if scored_values
                    else "-"
                )
                flagged_count = sum(
                    1 for item in row_data.cells if item.is_plagiarism_flagged
                )
                has_plagiarism = flagged_count > 0

                pdf.set_font(font_family, style="B", size=8.5)
                pdf.cell(
                    w=total_w,
                    h=row_h,
                    text=_fit_pdf_text(
                        pdf,
                        _format_pdf_score(row_data.total_score),
                        total_w,
                    ),
                    border=1,
                    align="C",
                )
                pdf.set_font(font_family, style="", size=8.5)
                pdf.cell(
                    w=avg_w,
                    h=row_h,
                    text=_fit_pdf_text(pdf, avg_text, avg_w),
                    border=1,
                    align="C",
                )

                if flagged_count > 1:
                    notes_label = f"ПЛАГІАТ ({flagged_count})"
                elif has_plagiarism:
                    notes_label = "ПЛАГІАТ"
                else:
                    notes_label = "ОК"

                pdf.set_font(
                    font_family,
                    style="B" if has_plagiarism else "",
                    size=8.5,
                )
                pdf.cell(
                    w=notes_w,
                    h=row_h,
                    text=_fit_pdf_text(
                        pdf,
                        _prepare_pdf_text(notes_label, unicode_supported=unicode_ok),
                        notes_w,
                    ),
                    border=1,
                    align="C",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
                pdf.set_font(font_family, style="", size=8.5)

    pdf.ln(3)
    pdf.set_font(font_family, style="", size=8)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(
        w=usable_w,
        h=5,
        text=_fit_pdf_text(
            pdf,
            _prepare_pdf_text(
                "Примітка: позначка * біля бала вказує на підозру щодо академічного плагіату.",
                unicode_supported=unicode_ok,
            ),
            usable_w,
        ),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_text_color(15, 23, 42)

    if resolved_practicals:
        pdf.ln(2)
        pdf.set_font(font_family, style="B", size=9)
        pdf.cell(
            w=usable_w,
            h=6,
            text=_prepare_pdf_text(
                "Перелік практичних робіт:",
                unicode_supported=unicode_ok,
            ),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.set_font(font_family, style="", size=8)
        for idx, p_info in enumerate(resolved_practicals, start=1):
            legend_line = (
                f"П{idx} ({p_info.course_slug.value.upper()}) — "
                f"{p_info.practical_title} "
                f"(макс. {_format_pdf_score(p_info.max_score)} б.)"
            )
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(
                w=usable_w,
                h=4.8,
                text=_prepare_pdf_text(legend_line, unicode_supported=unicode_ok),
                new_x="LMARGIN",
                new_y="NEXT",
            )

    pdf.ln(3)
    pdf.set_font(font_family, style="B", size=9.5)
    pdf.cell(
        w=usable_w,
        h=6.5,
        text=_prepare_pdf_text(
            "Статистика помилок за критеріями автоперевірки:",
            unicode_supported=unicode_ok,
        ),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    if not journal.error_stats:
        pdf.set_font(font_family, style="", size=8.5)
        pdf.cell(
            w=usable_w,
            h=5.5,
            text=_prepare_pdf_text(
                "Дані про типові помилки відсутні.",
                unicode_supported=unicode_ok,
            ),
            new_x="LMARGIN",
            new_y="NEXT",
        )
    else:
        pdf.set_font(font_family, style="", size=8)
        for stat in journal.error_stats:
            stat_line = (
                f"[{stat.rule_id}] {stat.description} — помилок: "
                f"{stat.failure_count}/{stat.total_attempts} "
                f"({stat.failure_rate_percent:.2f}%)"
            )
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(
                w=usable_w,
                h=4.8,
                text=_prepare_pdf_text(stat_line, unicode_supported=unicode_ok),
                new_x="LMARGIN",
                new_y="NEXT",
            )

    return bytes(pdf.output())


class ExportService:
    """Сервіс аналітики успішності академічних груп та експорту відомостей у .xlsx і .pdf."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_groups(self) -> list[AcademicGroupRead]:
        """Повертає перелік усіх академічних груп коледжу, відсортованих за курсом і шифром."""
        stmt = select(AcademicGroup).order_by(
            AcademicGroup.course_year.asc(),
            AcademicGroup.code.asc(),
        )
        result = await self._db.execute(stmt)
        groups = result.scalars().all()
        return [AcademicGroupRead.model_validate(group) for group in groups]

    async def _load_group_or_404(self, group_id: uuid.UUID) -> AcademicGroup:
        """Завантажує академічну групу за ID або генерує доменну помилку 404."""
        stmt = select(AcademicGroup).where(AcademicGroup.id == group_id)
        result = await self._db.execute(stmt)
        group = result.scalar_one_or_none()
        if group is None:
            raise DomainError(
                "Академічну групу не знайдено.",
                code="GROUP_NOT_FOUND",
                status_code=404,
                context={"group_id": str(group_id)},
            )
        return group

    async def _ensure_course_exists(self, course_id: uuid.UUID) -> None:
        """Перевіряє існування навчального курсу за ID при фільтрації відомості."""
        stmt = select(Course.id).where(Course.id == course_id)
        result = await self._db.execute(stmt)
        if result.scalar_one_or_none() is None:
            raise DomainError(
                "Навчальний курс не знайдено.",
                code="COURSE_NOT_FOUND",
                status_code=404,
                context={"course_id": str(course_id)},
            )

    async def _load_practicals(
        self,
        *,
        course_id: uuid.UUID | None = None,
    ) -> list[PracticalColumnInfo]:
        """Завантажує перелік практичних робіт, впорядкованих за курсом та індексом модуля."""
        if course_id is not None:
            await self._ensure_course_exists(course_id)

        stmt = (
            select(Practical)
            .join(Module, Practical.module_id == Module.id)
            .join(Course, Module.course_id == Course.id)
            .options(selectinload(Practical.module).selectinload(Module.course))
        )
        if course_id is not None:
            stmt = stmt.where(Module.course_id == course_id)

        result = await self._db.execute(stmt)
        practicals = list(result.scalars().all())
        practicals.sort(
            key=lambda item: (
                _COURSE_SLUG_ORDER.get(item.module.course.slug, 99),
                item.module.order_index,
                item.title.lower(),
                str(item.id),
            )
        )

        return [
            PracticalColumnInfo(
                practical_id=practical.id,
                practical_title=practical.title,
                course_slug=practical.module.course.slug,
                course_title=practical.module.course.title,
                module_order_index=practical.module.order_index,
                max_score=float(practical.max_score),
                needs_rules_review=practical.needs_rules_review,
            )
            for practical in practicals
        ]

    async def _load_group_students(self, group_id: uuid.UUID) -> list[User]:
        """Завантажує список студентів академічної групи."""
        stmt = select(User).where(
            User.group_id == group_id,
            User.role == UserRole.STUDENT,
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def _load_group_submissions(
        self,
        *,
        student_ids: Sequence[uuid.UUID],
        practical_ids: Sequence[uuid.UUID],
    ) -> list[Submission]:
        """Завантажує всі здачі практичних робіт студентів вказаної групи."""
        if not student_ids or not practical_ids:
            return []

        stmt = (
            select(Submission)
            .where(
                Submission.student_id.in_(list(student_ids)),
                Submission.practical_id.in_(list(practical_ids)),
            )
            .order_by(Submission.submitted_at.desc(), Submission.id.desc())
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def build_journal_bundle(
        self,
        *,
        group_id: uuid.UUID,
        course_id: uuid.UUID | None = None,
    ) -> GroupJournalBundle:
        """Збирає повний пакет даних електронного журналу групи та статистики помилок."""
        group = await self._load_group_or_404(group_id)
        practicals = await self._load_practicals(course_id=course_id)
        students = await self._load_group_students(group.id)
        submissions = await self._load_group_submissions(
            student_ids=[student.id for student in students],
            practical_ids=[item.practical_id for item in practicals],
        )
        journal = build_group_journal(
            group=group,
            students=students,
            practicals=practicals,
            submissions=submissions,
        )
        return GroupJournalBundle(
            group=AcademicGroupRead.model_validate(group),
            practicals=practicals,
            journal=journal,
        )

    async def get_group_journal(
        self,
        *,
        group_id: uuid.UUID,
        course_id: uuid.UUID | None = None,
    ) -> GroupJournalRead:
        """Повертає зведену відомість успішності академічної групи (JSON-контракт)."""
        bundle = await self.build_journal_bundle(
            group_id=group_id,
            course_id=course_id,
        )
        return bundle.journal

    async def export_group_journal(
        self,
        *,
        group_id: uuid.UUID,
        export_format: ExportFormat = ExportFormat.XLSX,
        course_id: uuid.UUID | None = None,
    ) -> ExportedDocument:
        """Генерує бінарний файл відомості успішності групи у форматі .xlsx або .pdf."""
        bundle = await self.build_journal_bundle(
            group_id=group_id,
            course_id=course_id,
        )
        safe_token = _sanitize_filename_token(bundle.group.code)
        extension = export_format.value
        filename_ascii = f"group_journal_{safe_token}.{extension}"
        filename_utf8 = f"Відомість_{bundle.group.code}.{extension}"
        content_disposition = build_content_disposition(
            filename_ascii=filename_ascii,
            filename_utf8=filename_utf8,
        )

        if export_format == ExportFormat.XLSX:
            content = await run_in_threadpool(
                render_group_journal_xlsx,
                journal=bundle.journal,
                practicals=bundle.practicals,
            )
            media_type = XLSX_MEDIA_TYPE
        else:
            content = await run_in_threadpool(
                render_group_journal_pdf,
                journal=bundle.journal,
                practicals=bundle.practicals,
            )
            media_type = PDF_MEDIA_TYPE

        return ExportedDocument(
            content=content,
            media_type=media_type,
            filename=filename_ascii,
            content_disposition=content_disposition,
            export_format=export_format,
        )


__all__ = [
    "ExportService",
    "ExportedDocument",
    "GroupJournalBundle",
    "MAX_PRACTICALS_PER_PDF_PAGE",
    "PDF_MEDIA_TYPE",
    "PracticalColumnInfo",
    "XLSX_MEDIA_TYPE",
    "build_content_disposition",
    "build_group_journal",
    "calculate_criterion_error_stats",
    "render_group_journal_pdf",
    "render_group_journal_xlsx",
    "sanitize_spreadsheet_text",
]
