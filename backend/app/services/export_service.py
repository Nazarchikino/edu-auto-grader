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
    GroupJournalRead,
    GroupJournalRow,
    GroupJournalStudentCell,
)

XLSX_MEDIA_TYPE: str = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
PDF_MEDIA_TYPE: str = "application/pdf"

_COURSE_SLUG_ORDER: dict[CourseSlug, int] = {
    CourseSlug.WORD: 0,
    CourseSlug.EXCEL: 1,
    CourseSlug.ACCESS: 2,
    CourseSlug.HTML: 3,
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

    best_submission_map: dict[tuple[uuid.UUID, uuid.UUID], Submission] = {}
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
        key = (submission.student_id, submission.practical_id)
        if key not in best_submission_map:
            best_submission_map[key] = submission

    rows: list[GroupJournalRow] = []
    for student in ordered_students:
        cells: list[GroupJournalStudentCell] = []
        total_score = 0.0

        for practical_info in practicals:
            matched = best_submission_map.get(
                (student.id, practical_info.practical_id)
            )
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

    error_stats = calculate_criterion_error_stats(list(best_submission_map.values()))
    return GroupJournalRead(
        group_id=group.id,
        group_code=group.code,
        specialty=group.specialty,
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
    resolved_practicals = list(practicals) if practicals is not None else []
    if not resolved_practicals and journal.rows:
        for idx, cell in enumerate(journal.rows[0].cells, start=1):
            resolved_practicals.append(
                PracticalColumnInfo(
                    practical_id=cell.practical_id,
                    practical_title=f"Практична робота №{idx}",
                    course_slug=CourseSlug.WORD,
                    course_title="Курс",
                    module_order_index=idx,
                    max_score=10.0,
                )
            )

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

    generated_at_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    sheet.cell(
        row=1,
        column=1,
        value=(
            f"Зведена відомість успішності групи {journal.group_code} "
            f"({journal.specialty})"
        ),
    ).font = title_font
    sheet.cell(
        row=2,
        column=1,
        value=f"Сформовано: {generated_at_str} | Студентів: {len(journal.rows)}",
    ).font = subtitle_font

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
        header_cell = sheet.cell(
            row=header_row_idx,
            column=col_idx,
            value=header_text,
        )
        header_cell.font = header_font
        header_cell.fill = header_fill
        header_cell.border = cell_border
        header_cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )

    cell_by_practical_for_row: dict[uuid.UUID, GroupJournalStudentCell]
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
        num_cell.alignment = Alignment(horizontal="center", vertical="center")

        name_cell = sheet.cell(
            row=excel_row,
            column=2,
            value=row_data.student_full_name,
        )
        name_cell.font = data_font
        name_cell.border = cell_border
        name_cell.alignment = Alignment(horizontal="left", vertical="center")

        cell_by_practical_for_row = {
            item.practical_id: item for item in row_data.cells
        }
        flagged_reasons: list[str] = []

        for p_idx, practical_info in enumerate(resolved_practicals, start=3):
            student_cell = cell_by_practical_for_row.get(
                practical_info.practical_id
            )
            score_cell = sheet.cell(row=excel_row, column=p_idx)
            score_cell.border = cell_border
            score_cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )

            if student_cell is None or student_cell.final_score is None:
                score_cell.value = "—"
                score_cell.font = data_font
            else:
                score_cell.value = round(student_cell.final_score, 2)
                score_cell.number_format = "0.00"
                if student_cell.is_plagiarism_flagged:
                    score_cell.fill = plagiarism_fill
                    score_cell.font = plagiarism_font
                    reason_text = (
                        student_cell.plagiarism_reason
                        or "Підозра на академічний плагіат"
                    )
                    flagged_reasons.append(
                        f"{practical_info.course_slug.value.upper()}: {reason_text}"
                    )
                else:
                    score_cell.font = data_font

        for extra_cell in row_data.cells:
            if (
                extra_cell.is_plagiarism_flagged
                and extra_cell.practical_id
                not in {p.practical_id for p in resolved_practicals}
            ):
                flagged_reasons.append(
                    extra_cell.plagiarism_reason
                    or "Підозра на академічний плагіат"
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
        total_cell.alignment = Alignment(horizontal="center", vertical="center")

        status_col_idx = total_col_idx + 1
        status_cell = sheet.cell(row=excel_row, column=status_col_idx)
        status_cell.border = cell_border
        if flagged_reasons:
            status_cell.value = f"ПЛАГІАТ: {'; '.join(flagged_reasons)}"
            status_cell.fill = plagiarism_fill
            status_cell.font = plagiarism_font
            status_cell.alignment = Alignment(
                horizontal="left",
                vertical="center",
                wrap_text=True,
            )
        else:
            status_cell.value = "ОК"
            status_cell.font = data_font
            status_cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
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
        h_cell = stats_sheet.cell(row=1, column=col_idx, value=header_text)
        h_cell.font = header_font
        h_cell.fill = header_fill
        h_cell.border = cell_border
        h_cell.alignment = Alignment(horizontal="center", vertical="center")

    for stat_idx, stat in enumerate(journal.error_stats, start=2):
        rule_cell = stats_sheet.cell(row=stat_idx, column=1, value=stat.rule_id)
        rule_cell.font = data_font
        rule_cell.border = cell_border

        desc_cell = stats_sheet.cell(
            row=stat_idx,
            column=2,
            value=stat.description,
        )
        desc_cell.font = data_font
        desc_cell.border = cell_border

        attempts_cell = stats_sheet.cell(
            row=stat_idx,
            column=3,
            value=stat.total_attempts,
        )
        attempts_cell.font = data_font
        attempts_cell.border = cell_border
        attempts_cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        failures_cell = stats_sheet.cell(
            row=stat_idx,
            column=4,
            value=stat.failure_count,
        )
        failures_cell.font = data_font
        failures_cell.border = cell_border
        failures_cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )

        rate_cell = stats_sheet.cell(
            row=stat_idx,
            column=5,
            value=round(stat.failure_rate_percent, 2),
        )
        rate_cell.font = data_font
        rate_cell.border = cell_border
        rate_cell.number_format = "0.00"
        rate_cell.alignment = Alignment(horizontal="center", vertical="center")

    _auto_adjust_worksheet_columns(stats_sheet)

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


def render_group_journal_pdf(
    journal: GroupJournalRead,
    practicals: Sequence[PracticalColumnInfo] | None = None,
) -> bytes:
    """Генерує зведену відомість успішності групи та аналітику помилок у форматі .pdf."""
    resolved_practicals = list(practicals) if practicals is not None else []
    if not resolved_practicals and journal.rows:
        for idx, cell in enumerate(journal.rows[0].cells, start=1):
            resolved_practicals.append(
                PracticalColumnInfo(
                    practical_id=cell.practical_id,
                    practical_title=f"Практична робота №{idx}",
                    course_slug=CourseSlug.WORD,
                    course_title="Курс",
                    module_order_index=idx,
                    max_score=10.0,
                )
            )

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    font_family, unicode_ok = _configure_pdf_font(pdf)
    pdf.add_page()

    pdf.set_font(font_family, style="B", size=14)
    title_text = _prepare_pdf_text(
        f"ЗВЕДЕНА ВІДОМІСТЬ УСПІШНОСТІ ГРУПИ {journal.group_code}",
        unicode_supported=unicode_ok,
    )
    pdf.cell(w=0, h=9, text=title_text, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(font_family, style="", size=10)
    generated_at_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    subtitle_text = _prepare_pdf_text(
        f"Спеціальність: {journal.specialty} | Студентів: {len(journal.rows)} | "
        f"Дата формування: {generated_at_str}",
        unicode_supported=unicode_ok,
    )
    pdf.cell(w=0, h=6, text=subtitle_text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    num_w = 14.0
    name_w = 72.0
    total_w = 24.0
    status_w = 38.0
    available_practicals_w = 277.0 - (num_w + name_w + total_w + status_w)
    practical_count = len(resolved_practicals)
    single_practical_w = (
        round(available_practicals_w / practical_count, 2)
        if practical_count > 0
        else 0.0
    )

    pdf.set_font(font_family, style="B", size=9)
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)

    pdf.cell(
        w=num_w,
        h=8,
        text=_prepare_pdf_text("№", unicode_supported=unicode_ok),
        border=1,
        align="C",
        fill=True,
    )
    pdf.cell(
        w=name_w,
        h=8,
        text=_prepare_pdf_text("ПІБ студента", unicode_supported=unicode_ok),
        border=1,
        align="L",
        fill=True,
    )
    for idx, p_info in enumerate(resolved_practicals, start=1):
        col_label = f"П{idx} ({p_info.course_slug.value.upper()})"
        pdf.cell(
            w=single_practical_w,
            h=8,
            text=_prepare_pdf_text(col_label, unicode_supported=unicode_ok),
            border=1,
            align="C",
            fill=True,
        )
    pdf.cell(
        w=total_w,
        h=8,
        text=_prepare_pdf_text("Сума", unicode_supported=unicode_ok),
        border=1,
        align="C",
        fill=True,
    )
    pdf.cell(
        w=status_w,
        h=8,
        text=_prepare_pdf_text("Антиплагіат", unicode_supported=unicode_ok),
        border=1,
        align="C",
        fill=True,
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_text_color(15, 23, 42)
    pdf.set_font(font_family, style="", size=9)

    for idx, row_data in enumerate(journal.rows, start=1):
        list_num = (
            row_data.list_number if row_data.list_number is not None else idx
        )
        cell_map = {item.practical_id: item for item in row_data.cells}
        has_plagiarism = any(item.is_plagiarism_flagged for item in row_data.cells)

        pdf.cell(
            w=num_w,
            h=7,
            text=str(list_num),
            border=1,
            align="C",
        )
        truncated_name = row_data.student_full_name[:38]
        pdf.cell(
            w=name_w,
            h=7,
            text=_prepare_pdf_text(truncated_name, unicode_supported=unicode_ok),
            border=1,
            align="L",
        )

        for p_info in resolved_practicals:
            st_cell = cell_map.get(p_info.practical_id)
            if st_cell is None or st_cell.final_score is None:
                val_text = "-"
            else:
                flag_suffix = " *" if st_cell.is_plagiarism_flagged else ""
                val_text = f"{st_cell.final_score:.2f}{flag_suffix}"
            pdf.cell(
                w=single_practical_w,
                h=7,
                text=_prepare_pdf_text(val_text, unicode_supported=unicode_ok),
                border=1,
                align="C",
            )

        pdf.set_font(font_family, style="B", size=9)
        pdf.cell(
            w=total_w,
            h=7,
            text=f"{row_data.total_score:.2f}",
            border=1,
            align="C",
        )
        status_label = "ПЛАГІАТ" if has_plagiarism else "ОК"
        pdf.set_font(
            font_family,
            style="B" if has_plagiarism else "",
            size=9,
        )
        pdf.cell(
            w=status_w,
            h=7,
            text=_prepare_pdf_text(status_label, unicode_supported=unicode_ok),
            border=1,
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.set_font(font_family, style="", size=9)

    if resolved_practicals:
        pdf.ln(4)
        pdf.set_font(font_family, style="B", size=9)
        pdf.cell(
            w=0,
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
                f"{p_info.practical_title} (макс. {p_info.max_score:.2f} б.)"
            )
            pdf.cell(
                w=0,
                h=5,
                text=_prepare_pdf_text(legend_line, unicode_supported=unicode_ok),
                new_x="LMARGIN",
                new_y="NEXT",
            )

    pdf.ln(4)
    pdf.set_font(font_family, style="B", size=10)
    pdf.cell(
        w=0,
        h=7,
        text=_prepare_pdf_text(
            "Статистика помилок за критеріями автоперевірки:",
            unicode_supported=unicode_ok,
        ),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    if not journal.error_stats:
        pdf.set_font(font_family, style="", size=9)
        pdf.cell(
            w=0,
            h=6,
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
            pdf.cell(
                w=0,
                h=5,
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
    "PDF_MEDIA_TYPE",
    "PracticalColumnInfo",
    "XLSX_MEDIA_TYPE",
    "build_content_disposition",
    "build_group_journal",
    "calculate_criterion_error_stats",
    "render_group_journal_pdf",
    "render_group_journal_xlsx",
]
