import io
import re
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import openpyxl  # type: ignore[import-untyped]
from fpdf import FPDF
from openpyxl.worksheet.worksheet import Worksheet  # type: ignore[import-untyped]

from app.models.course import CourseSlug, PracticalFormat
from app.models.progress import Submission
from app.models.user import AcademicGroup, User, UserRole
from app.schemas.auth import ImportedStudentItem, ImportSkippedItem, StudentImportResponse
from app.schemas.grading import CriterionResult, GradingReport, GradingRuleType
from app.schemas.submission import (
    CriterionErrorStat,
    GroupJournalPracticalRead,
    GroupJournalRead,
    GroupJournalRow,
    GroupJournalStudentCell,
)
from app.services.export_service import (
    MAX_PRACTICALS_PER_PDF_PAGE,
    PracticalColumnInfo,
    _configure_pdf_font,
    _fit_pdf_text,
    _format_pdf_score,
    build_group_journal,
    render_group_journal_pdf,
    render_group_journal_xlsx,
    sanitize_spreadsheet_text,
)
from app.services.student_import_service import (
    VARIANT_FORMULA_NOTE,
    build_credentials_report,
)


def _count_pdf_pages(pdf_bytes: bytes) -> int:
    """Підраховує кількість сторінок у згенерованому PDF-документі за словниками /Type /Page."""
    return len(re.findall(rb"/Type\s*/Page(?!s)\b", pdf_bytes))


def _make_grading_report_dict(
    *,
    rule_id: str,
    passed: bool,
    max_score: float = 10.0,
) -> dict[str, object]:
    """Формує валідний словник GradingReport для модульних тестів статистики помилок."""
    earned = max_score if passed else 0.0
    report = GradingReport(
        format_type=PracticalFormat.XLSX,
        total_points=earned,
        max_points=max_score,
        passed_count=1 if passed else 0,
        failed_count=0 if passed else 1,
        results=[
            CriterionResult(
                rule_id=rule_id,
                rule_type=GradingRuleType.XLSX_FORMULA,
                target="B10",
                expected="SUM",
                actual="=SUM(B2:B9)" if passed else None,
                passed=passed,
                points_awarded=earned,
                max_points=max_score,
                description="Перевірка обов'язкової формули SUM",
                feedback="Успішно" if passed else "Формула відсутня",
            )
        ],
    )
    return report.model_dump(mode="json")


def _make_submission(
    *,
    student_id: uuid.UUID,
    practical_id: uuid.UUID,
    score: float,
    passed: bool,
    submitted_at: datetime,
    rule_id: str = "rule_sum_1",
) -> Submission:
    """Створює in-memory ORM-екземпляр Submission для перевірки build_group_journal."""
    return Submission(
        id=uuid.uuid4(),
        practical_id=practical_id,
        student_id=student_id,
        variant_index=0,
        auto_score=Decimal(f"{score:.2f}"),
        final_score=Decimal(f"{score:.2f}"),
        grading_report=_make_grading_report_dict(rule_id=rule_id, passed=passed),
        extracted_metadata={},
        is_plagiarism_flagged=False,
        plagiarism_reason=None,
        submitted_at=submitted_at,
    )


def _build_wide_journal(
    *,
    practical_specs: list[tuple[CourseSlug, str]],
    student_count: int = 3,
) -> tuple[GroupJournalRead, list[PracticalColumnInfo]]:
    """Генерує тестовий журнал групи з довільною кількістю практичних робіт."""
    group_id = uuid.uuid4()
    practicals: list[PracticalColumnInfo] = []
    practical_headers: list[GroupJournalPracticalRead] = []

    for idx, (slug, title) in enumerate(practical_specs, start=1):
        p_id = uuid.uuid4()
        practicals.append(
            PracticalColumnInfo(
                practical_id=p_id,
                practical_title=title,
                course_slug=slug,
                course_title=slug.value.upper(),
                module_order_index=idx,
                max_score=10.0,
            )
        )
        practical_headers.append(
            GroupJournalPracticalRead(
                practical_id=p_id,
                title=title,
                course_slug=slug,
                module_order_index=idx,
                max_score=10.0,
            )
        )

    rows: list[GroupJournalRow] = []
    for student_idx in range(1, student_count + 1):
        cells: list[GroupJournalStudentCell] = []
        total_score = 0.0
        for p_idx, info in enumerate(practicals, start=1):
            if p_idx % 4 == 0:
                cells.append(
                    GroupJournalStudentCell(
                        practical_id=info.practical_id,
                        submission_id=None,
                        auto_score=None,
                        final_score=None,
                        is_plagiarism_flagged=False,
                        plagiarism_reason=None,
                        submitted_at=None,
                    )
                )
            else:
                score = 8.5 if p_idx % 2 == 0 else 10.0
                flagged = student_idx == 1 and p_idx == 2
                total_score += score
                cells.append(
                    GroupJournalStudentCell(
                        practical_id=info.practical_id,
                        submission_id=uuid.uuid4(),
                        auto_score=score,
                        final_score=score,
                        is_plagiarism_flagged=flagged,
                        plagiarism_reason="Збіг вмісту" if flagged else None,
                        submitted_at=datetime(2026, 11, 25, 12, 0, tzinfo=UTC),
                    )
                )

        long_name = (
            "Олександренко-Костянтинівський Володимир Олександрович (дуже довге ПІБ)"
            if student_idx == 1
            else f"Студент Тестовий №{student_idx}"
        )
        rows.append(
            GroupJournalRow(
                student_id=uuid.uuid4(),
                student_full_name=long_name,
                list_number=student_idx,
                cells=cells,
                total_score=round(total_score, 2),
            )
        )

    journal = GroupJournalRead(
        group_id=group_id,
        group_code="КН-31",
        specialty="122 Комп'ютерні науки",
        practicals=practical_headers,
        rows=rows,
        error_stats=[
            CriterionErrorStat(
                rule_id="r_formula_1",
                description="Перевірка коректності формули підсумку на аркуші Excel",
                total_attempts=student_count,
                failure_count=1,
                failure_rate_percent=round(100.0 / student_count, 2),
            )
        ],
    )
    return journal, practicals


def test_sanitize_spreadsheet_text_escapes_all_formula_prefixes() -> None:
    """Перевіряє екранування всіх небезпечних префіксів формул Excel/Calc."""
    dangerous_inputs = [
        "=CMD|'/C calc'!A0",
        '=HYPERLINK("http://evil", "click")',
        "+1+1",
        "-2+3",
        "@SUM(A1:A2)",
        "\t=1+1",
        "\r=1+1",
        "   =1+1",
        "\n+CMD()",
    ]
    for payload in dangerous_inputs:
        sanitized = sanitize_spreadsheet_text(payload)
        assert sanitized == f"'{payload}"

    safe_inputs = ["", "   ", "Бондаренко Ірина Василівна", "—", "ОК", "КН-31"]
    for safe_value in safe_inputs:
        assert sanitize_spreadsheet_text(safe_value) == safe_value


def test_render_group_journal_xlsx_sanitizes_formula_injection_and_keeps_numbers() -> None:
    """Перевіряє, що небезпечні рядки в .xlsx записані як безпечний текст 's' із префіксом \"'\"."""
    practical_id = uuid.uuid4()
    practicals = [
        PracticalColumnInfo(
            practical_id=practical_id,
            practical_title="=SUM(1,2) Робота",
            course_slug=CourseSlug.EXCEL,
            course_title="Excel",
            module_order_index=1,
            max_score=10.0,
        )
    ]
    evil_name = "=CMD|'/C calc'!A0"
    evil_plagiarism = '=HYPERLINK("http://evil", "click")'
    plus_name = "+1+1 Студент"

    journal = GroupJournalRead(
        group_id=uuid.uuid4(),
        group_code="=GROUP_1",
        specialty="@Specialty",
        practicals=[
            GroupJournalPracticalRead(
                practical_id=practical_id,
                title="=SUM(1,2) Робота",
                course_slug=CourseSlug.EXCEL,
                module_order_index=1,
                max_score=10.0,
            )
        ],
        rows=[
            GroupJournalRow(
                student_id=uuid.uuid4(),
                student_full_name=evil_name,
                list_number=1,
                cells=[
                    GroupJournalStudentCell(
                        practical_id=practical_id,
                        submission_id=uuid.uuid4(),
                        auto_score=8.5,
                        final_score=8.5,
                        is_plagiarism_flagged=True,
                        plagiarism_reason=evil_plagiarism,
                        submitted_at=datetime(2026, 11, 25, 10, 0, tzinfo=UTC),
                    )
                ],
                total_score=8.5,
            ),
            GroupJournalRow(
                student_id=uuid.uuid4(),
                student_full_name=plus_name,
                list_number=2,
                cells=[
                    GroupJournalStudentCell(
                        practical_id=practical_id,
                        submission_id=None,
                        auto_score=None,
                        final_score=None,
                        is_plagiarism_flagged=False,
                        plagiarism_reason=None,
                        submitted_at=None,
                    )
                ],
                total_score=0.0,
            ),
        ],
        error_stats=[
            CriterionErrorStat(
                rule_id="-rule_1",
                description="@SUM(1,2) небезпечний опис",
                total_attempts=2,
                failure_count=1,
                failure_rate_percent=50.0,
            )
        ],
    )

    xlsx_bytes = render_group_journal_xlsx(journal, practicals)
    workbook = openpyxl.load_workbook(io.BytesIO(xlsx_bytes), data_only=False)
    try:
        # 1. Основний аркуш журналу
        main_sheet = workbook["Відомість успішності"]
        assert isinstance(main_sheet, Worksheet)

        evil_name_cell = main_sheet.cell(row=5, column=2)
        assert evil_name_cell.data_type == "s"
        assert evil_name_cell.value == f"'{evil_name}"

        plus_name_cell = main_sheet.cell(row=6, column=2)
        assert plus_name_cell.data_type == "s"
        assert plus_name_cell.value == f"'{plus_name}"

        # Числові клітинки залишаються числовими
        score_cell = main_sheet.cell(row=5, column=3)
        assert score_cell.data_type == "n"
        assert score_cell.value == 8.5

        total_cell = main_sheet.cell(row=5, column=4)
        assert total_cell.data_type == "n"
        assert total_cell.value == 8.5

        status_cell = main_sheet.cell(row=5, column=5)
        assert status_cell.data_type == "s"
        assert isinstance(status_cell.value, str)
        assert f"'{evil_plagiarism}" in status_cell.value

        # 2. Аркуш статистики помилок
        stats_sheet = workbook["Статистика помилок"]
        assert isinstance(stats_sheet, Worksheet)
        rule_id_cell = stats_sheet.cell(row=2, column=1)
        desc_cell = stats_sheet.cell(row=2, column=2)
        assert rule_id_cell.data_type == "s"
        assert rule_id_cell.value == "'-rule_1"
        assert desc_cell.data_type == "s"
        assert desc_cell.value == "'@SUM(1,2) небезпечний опис"
        assert stats_sheet.cell(row=2, column=3).data_type == "n"
        assert stats_sheet.cell(row=2, column=4).data_type == "n"
        assert stats_sheet.cell(row=2, column=5).data_type == "n"

        # 3. Аркуш інцидентів антиплагіату — прямі клітинки ПІБ і plagiarism_reason
        plagiarism_sheet = workbook["Антиплагіат"]
        assert isinstance(plagiarism_sheet, Worksheet)
        plag_name_cell = plagiarism_sheet.cell(row=2, column=2)
        plag_title_cell = plagiarism_sheet.cell(row=2, column=4)
        plag_reason_cell = plagiarism_sheet.cell(row=2, column=6)
        assert plag_name_cell.data_type == "s"
        assert plag_name_cell.value == f"'{evil_name}"
        assert plag_title_cell.data_type == "s"
        assert plag_title_cell.value == "'=SUM(1,2) Робота"
        assert plag_reason_cell.data_type == "s"
        assert plag_reason_cell.value == f"'{evil_plagiarism}"

        # 4. У жодному аркуші книги немає активної формули (data_type == "f")
        for sheet_name in workbook.sheetnames:
            ws = workbook[sheet_name]
            for row in ws.iter_rows():
                for cell in row:
                    assert cell.data_type != "f", (
                        f"Знайдено активну формулу в {sheet_name}!{cell.coordinate}: {cell.value!r}"
                    )
    finally:
        workbook.close()


def test_render_group_journal_pdf_paginates_15_excel_and_37_all_course_practicals() -> None:
    """Перевіряє горизонтальну пагінацію широких PDF-відомостей (15 та 37 робіт)."""
    assert MAX_PRACTICALS_PER_PDF_PAGE == 10

    # 1. 15 практичних робіт курсу Excel -> щонайменше 2 сторінки (10 + 5 колонок)
    excel_specs = [
        (CourseSlug.EXCEL, f"Практична робота з MS Excel №{idx} (розширена назва теми)")
        for idx in range(1, 16)
    ]
    excel_journal, excel_practicals = _build_wide_journal(practical_specs=excel_specs)

    pdf_15_explicit = render_group_journal_pdf(excel_journal, excel_practicals)
    assert pdf_15_explicit.startswith(b"%PDF-")
    assert _count_pdf_pages(pdf_15_explicit) >= 2

    # Також перевіряємо побудову колонок із journal.practicals без передачі аргументу practicals
    pdf_15_from_journal = render_group_journal_pdf(excel_journal)
    assert pdf_15_from_journal.startswith(b"%PDF-")
    assert _count_pdf_pages(pdf_15_from_journal) >= 2

    # 2. 37 практичних робіт усіх 4 курсів -> щонайменше 4 сторінки (10 + 10 + 10 + 7)
    all_course_specs: list[tuple[CourseSlug, str]] = (
        [(CourseSlug.WORD, f"MS Word: Практична №{i}") for i in range(1, 11)]
        + [(CourseSlug.EXCEL, f"MS Excel: Практична №{i}") for i in range(1, 16)]
        + [(CourseSlug.ACCESS, f"MS Access: Практична №{i}") for i in range(1, 7)]
        + [(CourseSlug.HTML, f"HTML5/CSS3: Практична №{i}") for i in range(1, 7)]
    )
    assert len(all_course_specs) == 37
    wide_journal, wide_practicals = _build_wide_journal(practical_specs=all_course_specs)

    pdf_37 = render_group_journal_pdf(wide_journal, wide_practicals)
    assert pdf_37.startswith(b"%PDF-")
    assert _count_pdf_pages(pdf_37) >= 4


def test_pdf_compact_score_formatting_and_text_fitting() -> None:
    """Перевіряє компактне форматування балів та безпечне обрізання тексту під ширину клітинки."""
    assert _format_pdf_score(10.0) == "10"
    assert _format_pdf_score(8.5) == "8.5"
    assert _format_pdf_score(8.5, flagged=True) == "8.5*"
    assert _format_pdf_score(8.25, flagged=True) == "8.25*"
    assert _format_pdf_score(100.0) == "100"
    assert _format_pdf_score(0.0) == "0"

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    font_family, _unicode_ok = _configure_pdf_font(pdf)
    pdf.set_font(font_family, style="", size=8.5)

    long_text = "Дуже Довге Прізвище Ім'я По Батькові Студента Для Перевірки Меж Клітинки"
    max_cell_w = 35.0
    fitted = _fit_pdf_text(pdf, long_text, max_cell_w)
    assert fitted.endswith("...")
    assert float(pdf.get_string_width(fitted)) <= max_cell_w - (2.0 * float(pdf.c_margin))
    assert _fit_pdf_text(pdf, "Короткий", max_cell_w) == "Короткий"
    assert _fit_pdf_text(pdf, "Будь-який", 1.0) == ""


def test_build_group_journal_deduplicates_error_stats_to_one_active_submission_per_pair() -> None:
    """Перевіряє, що повторні спроби студента не спотворюють відсоток помилок error_stats."""
    group = AcademicGroup(
        id=uuid.uuid4(),
        code="КН-31",
        specialty="122 Комп'ютерні науки",
        course_year=3,
    )
    student1 = User(
        id=uuid.uuid4(),
        email="s1@kpefk.com.ua",
        password_hash="hash",
        full_name="Андрієнко Андрій",
        role=UserRole.STUDENT,
        group_id=group.id,
        list_number=1,
    )
    student2 = User(
        id=uuid.uuid4(),
        email="s2@kpefk.com.ua",
        password_hash="hash",
        full_name="Бойко Богдан",
        role=UserRole.STUDENT,
        group_id=group.id,
        list_number=2,
    )
    outsider_student_id = uuid.uuid4()

    practical_id = uuid.uuid4()
    other_practical_id = uuid.uuid4()
    practicals = [
        PracticalColumnInfo(
            practical_id=practical_id,
            practical_title="Практична №1",
            course_slug=CourseSlug.EXCEL,
            course_title="MS Excel",
            module_order_index=1,
            max_score=10.0,
        )
    ]

    base_time = datetime(2026, 11, 25, 9, 0, tzinfo=UTC)

    # Сценарій 1: студент 1 робить 10 невдалих спроб, студент 2 здає без помилок
    # + додаємо зайві здачі стороннього студента та іншої практичної (мають ігноруватися)
    failed_attempts_s1 = [
        _make_submission(
            student_id=student1.id,
            practical_id=practical_id,
            score=0.0,
            passed=False,
            submitted_at=base_time + timedelta(minutes=attempt_idx),
            rule_id="excel_sum",
        )
        for attempt_idx in range(10)
    ]
    passed_attempt_s2 = _make_submission(
        student_id=student2.id,
        practical_id=practical_id,
        score=10.0,
        passed=True,
        submitted_at=base_time + timedelta(minutes=15),
        rule_id="excel_sum",
    )
    unrelated_submissions = [
        _make_submission(
            student_id=outsider_student_id,
            practical_id=practical_id,
            score=0.0,
            passed=False,
            submitted_at=base_time + timedelta(minutes=16),
            rule_id="excel_sum",
        ),
        _make_submission(
            student_id=student1.id,
            practical_id=other_practical_id,
            score=0.0,
            passed=False,
            submitted_at=base_time + timedelta(minutes=17),
            rule_id="excel_sum",
        ),
    ]

    journal_with_one_failing = build_group_journal(
        group=group,
        students=[student1, student2],
        practicals=practicals,
        submissions=[*failed_attempts_s1, passed_attempt_s2, *unrelated_submissions],
    )
    assert len(journal_with_one_failing.error_stats) == 1
    stat_one_failing = journal_with_one_failing.error_stats[0]
    assert stat_one_failing.rule_id == "excel_sum"
    assert stat_one_failing.total_attempts == 2
    assert stat_one_failing.failure_count == 1
    assert stat_one_failing.failure_rate_percent == 50.0

    # Сценарій 2: після 10 невдалих спроб студент 1 успішно здає роботу без помилок
    passed_attempt_s1 = _make_submission(
        student_id=student1.id,
        practical_id=practical_id,
        score=10.0,
        passed=True,
        submitted_at=base_time + timedelta(minutes=30),
        rule_id="excel_sum",
    )
    journal_all_passed = build_group_journal(
        group=group,
        students=[student1, student2],
        practicals=practicals,
        submissions=[*failed_attempts_s1, passed_attempt_s1, passed_attempt_s2],
    )
    assert len(journal_all_passed.error_stats) == 1
    stat_all_passed = journal_all_passed.error_stats[0]
    assert stat_all_passed.total_attempts == 2
    assert stat_all_passed.failure_count == 0
    assert stat_all_passed.failure_rate_percent == 0.0


def test_build_credentials_report_uses_list_number_and_dynamic_variant_note() -> None:
    """Перевіряє формулювання стовпця «№ у списку» та примітки формули у звіті імпорту."""
    response = StudentImportResponse(
        group_id=uuid.uuid4(),
        group_code="ПЗ-21",
        total_variants=15,
        created_count=2,
        skipped_count=1,
        created=[
            ImportedStudentItem(
                user_id=uuid.uuid4(),
                list_number=1,
                variant_number=1,
                full_name="Авраменко Іван Петрович",
                email="avramenko.i@kpefk.com.ua",
                temp_password="PassWord1",
            ),
            ImportedStudentItem(
                user_id=uuid.uuid4(),
                list_number=12,
                variant_number=12,
                full_name="Бондаренко Олена Сергіївна",
                email="bondarenko.o@kpefk.com.ua",
                temp_password="PassWord2",
            ),
        ],
        skipped=[
            ImportSkippedItem(
                row_number=4,
                full_name="Дубль Студент",
                email="dup@kpefk.com.ua",
                reason="Дублікат електронної пошти.",
            )
        ],
    )

    report_text = build_credentials_report(
        response,
        generated_at=datetime(2026, 11, 25, 14, 30, tzinfo=UTC),
    )

    assert VARIANT_FORMULA_NOTE in report_text
    assert "№ у списку | ПІБ | E-mail | Пароль" in report_text
    assert "| Варіант |" not in report_text
    assert "| Варіант " not in report_text
    assert "1 | Авраменко Іван Петрович | avramenko.i@kpefk.com.ua | PassWord1" in report_text
    assert "12 | Бондаренко Олена Сергіївна | bondarenko.o@kpefk.com.ua | PassWord2" in report_text
    assert (
        "Рядок #4 | Дубль Студент <dup@kpefk.com.ua> | Дублікат електронної пошти."
        in report_text
    )


def test_export_group_journal_xlsx_and_pdf_support_12_point_scale() -> None:
    """Перевіряє коректність build_group_journal, .xlsx та .pdf експорту для 12-бальної шкали."""
    assert _format_pdf_score(12.0) == "12"
    assert _format_pdf_score(11.5) == "11.5"

    group = AcademicGroup(
        id=uuid.uuid4(),
        code="КН-32",
        specialty="122 Комп'ютерні науки",
        course_year=3,
    )
    student = User(
        id=uuid.uuid4(),
        email="creative.student@kpefk.lcloud.in.ua",
        password_hash="hash",
        full_name="Гончаренко Олена Вікторівна",
        role=UserRole.STUDENT,
        group_id=group.id,
        list_number=1,
    )

    p1_id = uuid.uuid4()
    p2_id = uuid.uuid4()
    practicals = [
        PracticalColumnInfo(
            practical_id=p1_id,
            practical_title="Форматування текстового документа",
            course_slug=CourseSlug.WORD,
            course_title="Microsoft Word",
            module_order_index=1,
            max_score=12.0,
        ),
        PracticalColumnInfo(
            practical_id=p2_id,
            practical_title="Формули та діаграми",
            course_slug=CourseSlug.EXCEL,
            course_title="Microsoft Excel",
            module_order_index=2,
            max_score=12.0,
        ),
    ]

    now_utc = datetime(2026, 11, 25, 15, 0, tzinfo=UTC)
    sub1 = Submission(
        id=uuid.uuid4(),
        practical_id=p1_id,
        student_id=student.id,
        variant_index=0,
        auto_score=Decimal("10.00"),
        final_score=Decimal("12.00"),
        grading_report=_make_grading_report_dict(rule_id="r_word_1", passed=True),
        extracted_metadata={},
        is_plagiarism_flagged=False,
        plagiarism_reason=None,
        submitted_at=now_utc,
    )
    sub2 = Submission(
        id=uuid.uuid4(),
        practical_id=p2_id,
        student_id=student.id,
        variant_index=0,
        auto_score=Decimal("9.50"),
        final_score=Decimal("11.50"),
        grading_report=_make_grading_report_dict(rule_id="r_excel_1", passed=True),
        extracted_metadata={},
        is_plagiarism_flagged=False,
        plagiarism_reason=None,
        submitted_at=now_utc + timedelta(minutes=5),
    )

    journal = build_group_journal(
        group=group,
        students=[student],
        practicals=practicals,
        submissions=[sub1, sub2],
    )
    assert [item.max_score for item in journal.practicals] == [12.0, 12.0]
    assert len(journal.rows) == 1
    assert journal.rows[0].total_score == 23.5
    assert journal.rows[0].cells[0].auto_score == 10.0
    assert journal.rows[0].cells[0].final_score == 12.0
    assert journal.rows[0].cells[1].auto_score == 9.5
    assert journal.rows[0].cells[1].final_score == 11.5

    # Перевірка .xlsx експорту
    xlsx_bytes = render_group_journal_xlsx(journal, practicals)
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes), data_only=False)
    try:
        sheet = wb["Відомість успішності"]
        assert isinstance(sheet, Worksheet)
        subtitle_val = str(sheet.cell(row=2, column=1).value)
        assert "Макс. сума: 24.00 б." in subtitle_val
        assert "(макс. 12.00)" in str(sheet.cell(row=4, column=3).value)
        assert "(макс. 12.00)" in str(sheet.cell(row=4, column=4).value)
        assert sheet.cell(row=5, column=3).value == 12.0
        assert sheet.cell(row=5, column=4).value == 11.5
        assert sheet.cell(row=5, column=5).value == 23.5
    finally:
        wb.close()

    # Перевірка .pdf експорту
    pdf_bytes = render_group_journal_pdf(journal, practicals)
    assert pdf_bytes.startswith(b"%PDF-")
    assert _count_pdf_pages(pdf_bytes) >= 1
