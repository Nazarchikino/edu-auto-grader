import uuid
from dataclasses import dataclass
from pathlib import Path

import pytest
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.graders.accdb_grader import AccdbGrader
from app.graders.docx_grader import DocxGrader
from app.graders.factory import GraderFactory
from app.graders.html_grader import HtmlGrader
from app.graders.metadata import (
    compute_code_sha256,
    compute_file_sha256,
    evaluate_plagiarism,
    extract_document_metadata,
)
from app.graders.xlsx_grader import XlsxGrader
from app.models.course import PracticalFormat
from app.schemas.grading import ExtractedMetadata, GradingRule, GradingRuleType
from tests.conftest import (
    build_sample_accdb,
    build_sample_docx,
    build_sample_xlsx,
)


@dataclass(frozen=True, slots=True)
class DummySubmissionRecord:
    """Тестовий запис попередньої здачі для перевірки алгоритму антиплагіату."""

    id: uuid.UUID
    student_id: uuid.UUID
    file_hash: str | None
    extracted_metadata: dict[str, object] | ExtractedMetadata


def test_grader_factory_resolves_all_four_formats() -> None:
    """Перевіряє створення парсерів усіх 4 форматів через GraderFactory."""
    assert isinstance(GraderFactory.get_grader(PracticalFormat.DOCX), DocxGrader)
    assert isinstance(GraderFactory.get_grader(".docx"), DocxGrader)
    assert isinstance(GraderFactory.get_grader("XLSX"), XlsxGrader)
    assert isinstance(GraderFactory.get_grader("accdb"), AccdbGrader)
    assert isinstance(GraderFactory.get_grader(PracticalFormat.HTML), HtmlGrader)

    with pytest.raises(InvalidFileFormatError) as exc_info:
        GraderFactory.get_grader("pptx")
    assert exc_info.value.code == "INVALID_FILE_FORMAT"


def test_docx_grader_evaluates_valid_document(tmp_path: Path) -> None:
    """Перевіряє успішне оцінювання коректно оформленого документа Word (.docx)."""
    docx_path = build_sample_docx(
        tmp_path / "valid_report.docx",
        left_mm=30.0,
        right_mm=15.0,
        top_mm=20.0,
        bottom_mm=20.0,
        font_name="Times New Roman",
        font_size_pt=14.0,
        line_spacing=1.5,
        alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
        include_table=True,
        table_rows=4,
        table_cols=3,
        include_list=True,
    )

    rules = [
        GradingRule(
            id="w1",
            type=GradingRuleType.DOCX_PAGE_MARGINS,
            target="section_0",
            expected="left=30,right=15,top=20,bottom=20",
            points=2.0,
            description="Поля сторінки 30/15/20/20 мм",
        ),
        GradingRule(
            id="w2",
            type=GradingRuleType.DOCX_FONT,
            target="body",
            expected="{font_name}:14",
            points=2.5,
            description="Шрифт Times New Roman 14 пт",
        ),
        GradingRule(
            id="w3",
            type=GradingRuleType.DOCX_LINE_SPACING,
            target="body",
            expected="1.5",
            points=1.5,
            description="Міжрядковий інтервал 1.5",
        ),
        GradingRule(
            id="w4",
            type=GradingRuleType.DOCX_ALIGNMENT,
            target="body",
            expected="JUSTIFY",
            points=1.5,
            description="Вирівнювання абзаців за шириною",
        ),
        GradingRule(
            id="w5",
            type=GradingRuleType.DOCX_TABLE_EXISTS,
            target="table_0.rows",
            expected=">={min_rows}",
            points=1.5,
            description="Таблиця містить щонайменше 4 рядки",
        ),
        GradingRule(
            id="w6",
            type=GradingRuleType.DOCX_LIST_EXISTS,
            target="document",
            expected="true",
            points=1.0,
            description="Наявний маркований або нумерований список",
        ),
    ]

    grader = DocxGrader()
    report = grader.evaluate(
        file_path=docx_path,
        rules=rules,
        variant_data={"font_name": "Times New Roman", "min_rows": 4},
    )

    assert report.format_type == PracticalFormat.DOCX
    assert report.total_points == 10.0
    assert report.max_points == 10.0
    assert report.passed_count == 6
    assert report.failed_count == 0
    assert all(item.passed for item in report.results)


def test_docx_grader_detects_formatting_violations_and_corrupt_files(
    tmp_path: Path,
) -> None:
    """Перевіряє виявлення помилок форматування та пошкоджених файлів у DocxGrader."""
    bad_docx_path = build_sample_docx(
        tmp_path / "wrong_report.docx",
        left_mm=15.0,
        right_mm=15.0,
        top_mm=15.0,
        bottom_mm=15.0,
        font_name="Arial",
        font_size_pt=11.0,
        line_spacing=1.0,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
        include_table=False,
        include_list=False,
    )

    rules = [
        GradingRule(
            id="w1",
            type=GradingRuleType.DOCX_PAGE_MARGINS,
            target="section_0",
            expected="left=30,right=15,top=20,bottom=20",
            points=2.0,
            description="Поля сторінки",
        ),
        GradingRule(
            id="w2",
            type=GradingRuleType.DOCX_FONT,
            target="body",
            expected="Times New Roman:14",
            points=2.0,
            description="Шрифт",
        ),
        GradingRule(
            id="w3",
            type=GradingRuleType.DOCX_LINE_SPACING,
            target="body",
            expected="1.5",
            points=2.0,
            description="Інтервал",
        ),
        GradingRule(
            id="w4",
            type=GradingRuleType.DOCX_ALIGNMENT,
            target="body",
            expected="JUSTIFY",
            points=2.0,
            description="Вирівнювання",
        ),
        GradingRule(
            id="w5",
            type=GradingRuleType.DOCX_TABLE_EXISTS,
            target="document",
            expected=">=1",
            points=1.0,
            description="Таблиця",
        ),
        GradingRule(
            id="w6",
            type=GradingRuleType.DOCX_LIST_EXISTS,
            target="document",
            expected="true",
            points=1.0,
            description="Список",
        ),
    ]

    grader = DocxGrader()
    report = grader.evaluate(file_path=bad_docx_path, rules=rules, variant_data={})

    assert report.total_points == 0.0
    assert report.passed_count == 0
    assert report.failed_count == 6

    corrupt_docx = tmp_path / "corrupt.docx"
    corrupt_docx.write_bytes(b"not-a-valid-zip-archive")
    with pytest.raises(InvalidFileFormatError):
        grader.evaluate(file_path=corrupt_docx, rules=rules, variant_data={})


def test_xlsx_grader_evaluates_formulas_values_and_charts(tmp_path: Path) -> None:
    """Перевіряє роботу XlsxGrader для формул, обчислених значень та діаграм."""
    xlsx_path = build_sample_xlsx(
        tmp_path / "valid_calc.xlsx",
        sheet_title="Sheet1",
        values=[1850.0] * 10,
        sum_formula="=SUM(D2:D11)",
        avg_formula="=AVERAGE(D2:D11)",
        include_chart=True,
    )

    rules = [
        GradingRule(
            id="x1",
            type=GradingRuleType.XLSX_FORMULA,
            target="D12",
            expected="SUM(D2:D11)",
            points=3.0,
            description="Формула SUM у D12",
        ),
        GradingRule(
            id="x2",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!D13",
            expected="AVERAGE(D2:D11)",
            points=2.5,
            description="Формула AVERAGE у D13",
        ),
        GradingRule(
            id="x3",
            type=GradingRuleType.XLSX_VALUE,
            target="D12",
            expected="{expected_sum}",
            points=2.5,
            description="Обчислене значення суми в D12 дорівнює 18500",
        ),
        GradingRule(
            id="x4",
            type=GradingRuleType.XLSX_CHART_EXISTS,
            target="Sheet1",
            expected="true",
            points=2.0,
            description="На аркуші Sheet1 побудовано діаграму",
        ),
    ]

    grader = XlsxGrader()
    report = grader.evaluate(
        file_path=xlsx_path,
        rules=rules,
        variant_data={"expected_sum": 18500},
    )

    assert report.format_type == PracticalFormat.XLSX
    assert report.total_points == 10.0
    assert report.passed_count == 4
    assert report.failed_count == 0


def test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart(
    tmp_path: Path,
) -> None:
    """Перевіряє провал критеріїв XlsxGrader за статичного числа замість формули та без діаграми."""
    xlsx_path = build_sample_xlsx(
        tmp_path / "static_calc.xlsx",
        values=[100.0] * 10,
        sum_formula=None,
        avg_formula=None,
        include_chart=False,
    )

    rules = [
        GradingRule(
            id="x1",
            type=GradingRuleType.XLSX_FORMULA,
            target="D12",
            expected="SUM(D2:D11)",
            points=4.0,
            description="Формула SUM у D12",
        ),
        GradingRule(
            id="x2",
            type=GradingRuleType.XLSX_VALUE,
            target="D12",
            expected="1000",
            points=3.0,
            description="Значення у D12 дорівнює 1000",
        ),
        GradingRule(
            id="x3",
            type=GradingRuleType.XLSX_CHART_EXISTS,
            target="Sheet1",
            expected="true",
            points=3.0,
            description="Наявність діаграми",
        ),
    ]

    grader = XlsxGrader()
    report = grader.evaluate(file_path=xlsx_path, rules=rules, variant_data={})

    assert report.results[0].passed is False
    assert "статичне значення" in report.results[0].feedback
    assert report.results[1].passed is True
    assert report.results[2].passed is False
    assert report.total_points == 3.0
    assert report.passed_count == 1
    assert report.failed_count == 2

    corrupt_xlsx = tmp_path / "broken.xlsx"
    corrupt_xlsx.write_bytes(b"corrupted-excel-payload")
    with pytest.raises(InvalidFileFormatError):
        grader.evaluate(file_path=corrupt_xlsx, rules=rules, variant_data={})


def test_accdb_grader_evaluates_tables_columns_and_types(tmp_path: Path) -> None:
    """Перевіряє інспекцію таблиць, стовпців та їхніх типів даних у AccdbGrader."""
    accdb_path = build_sample_accdb(tmp_path / "college.accdb")

    rules = [
        GradingRule(
            id="a1",
            type=GradingRuleType.ACCDB_TABLE_EXISTS,
            target="{primary_table}",
            expected="true",
            points=2.0,
            description="Таблиця Students існує",
        ),
        GradingRule(
            id="a2",
            type=GradingRuleType.ACCDB_TABLE_EXISTS,
            target="Grades",
            expected="true",
            points=2.0,
            description="Таблиця Grades існує",
        ),
        GradingRule(
            id="a3",
            type=GradingRuleType.ACCDB_COLUMN_EXISTS,
            target="Students.FullName",
            expected="true",
            points=2.0,
            description="Поле Students.FullName існує",
        ),
        GradingRule(
            id="a4",
            type=GradingRuleType.ACCDB_COLUMN_TYPE,
            target="Students.ID",
            expected="AutoNumber",
            points=2.0,
            description="Поле Students.ID має тип AutoNumber",
        ),
        GradingRule(
            id="a5",
            type=GradingRuleType.ACCDB_COLUMN_TYPE,
            target="Grades.Score",
            expected="DOUBLE",
            points=2.0,
            description="Поле Grades.Score має числовий тип DOUBLE",
        ),
    ]

    grader = AccdbGrader()
    report = grader.evaluate(
        file_path=accdb_path,
        rules=rules,
        variant_data={"primary_table": "Students"},
    )

    assert report.format_type == PracticalFormat.ACCDB
    assert report.total_points == 10.0
    assert report.passed_count == 5
    assert report.failed_count == 0


def test_accdb_grader_detects_missing_schema_elements_and_invalid_header(
    tmp_path: Path,
) -> None:
    """Перевіряє виявлення відсутніх таблиць/стовпців/типів та невалідного заголовка .accdb."""
    accdb_path = build_sample_accdb(
        tmp_path / "partial.accdb",
        tables={
            "Students": [
                ("ID", "AUTONUMBER"),
                ("FullName", "TEXT(100)"),
            ],
        },
    )

    rules = [
        GradingRule(
            id="a1",
            type=GradingRuleType.ACCDB_TABLE_EXISTS,
            target="Grades",
            expected="true",
            points=3.0,
            description="Таблиця Grades існує",
        ),
        GradingRule(
            id="a2",
            type=GradingRuleType.ACCDB_COLUMN_EXISTS,
            target="Students.GroupCode",
            expected="true",
            points=3.0,
            description="Стовпець GroupCode існує",
        ),
        GradingRule(
            id="a3",
            type=GradingRuleType.ACCDB_COLUMN_TYPE,
            target="Students.FullName",
            expected="DATETIME",
            points=4.0,
            description="Поле FullName має тип DATETIME",
        ),
    ]

    grader = AccdbGrader()
    report = grader.evaluate(file_path=accdb_path, rules=rules, variant_data={})

    assert report.total_points == 0.0
    assert report.passed_count == 0
    assert report.failed_count == 3

    invalid_accdb = tmp_path / "invalid.accdb"
    invalid_accdb.write_bytes(b"NOT_AN_ACCESS_DATABASE_FILE_HEADER_1234567890")
    with pytest.raises(InvalidFileFormatError):
        grader.evaluate(file_path=invalid_accdb, rules=rules, variant_data={})


def test_html_grader_evaluates_semantic_dom_structure_and_attributes() -> None:
    """Перевіряє валідацію DOM-дерева HTML5 через BeautifulSoup4 у HtmlGrader."""
    html_code = """<!DOCTYPE html>
    <html lang="uk">
      <head>
        <meta charset="utf-8">
        <title>Розклад занять КН-31</title>
      </head>
      <body>
        <header>
          <h1>Розклад занять КН-31</h1>
        </header>
        <main>
          <img src="logo.png" alt="Логотип коледжу">
          <table>
            <tr><th>День</th><th>Дисципліна</th></tr>
            <tr><td>Понеділок</td><td>Інформатика</td></tr>
            <tr><td>Вівторок</td><td>Бази даних</td></tr>
            <tr><td>Середа</td><td>Вебтехнології</td></tr>
          </table>
          <form action="/consult" method="post">
            <input type="email" name="email" required>
            <button type="submit">Записатися</button>
          </form>
        </main>
      </body>
    </html>
    """

    rules = [
        GradingRule(
            id="h0",
            type=GradingRuleType.HTML_TAG_EXISTS,
            target="<!DOCTYPE html>",
            expected="true",
            points=1.0,
            description="Наявна декларація <!DOCTYPE html>",
        ),
        GradingRule(
            id="h1",
            type=GradingRuleType.HTML_TAG_EXISTS,
            target="header > h1",
            expected="{required_heading}",
            points=2.0,
            description="Заголовок містить назву розкладу варіанта",
        ),
        GradingRule(
            id="h2",
            type=GradingRuleType.HTML_TAG_EXISTS,
            target="main",
            expected="true",
            points=2.0,
            description="Наявний семантичний тег <main>",
        ),
        GradingRule(
            id="h3",
            type=GradingRuleType.HTML_TAG_COUNT,
            target="table > tr",
            expected=">={min_rows}",
            points=3.0,
            description="Таблиця містить щонайменше 4 рядки",
        ),
        GradingRule(
            id="h4",
            type=GradingRuleType.HTML_ATTRIBUTE_EXISTS,
            target="img.alt",
            expected="true",
            points=1.0,
            description="Зображення має обов'язковий атрибут alt",
        ),
        GradingRule(
            id="h5",
            type=GradingRuleType.HTML_ATTRIBUTE_EXISTS,
            target="form[method]",
            expected="post",
            points=1.0,
            description="Форма використовує метод POST",
        ),
    ]

    grader = HtmlGrader()
    report = grader.evaluate(
        raw_code=html_code,
        rules=rules,
        variant_data={"required_heading": "Розклад занять КН-31", "min_rows": 4},
    )

    assert report.format_type == PracticalFormat.HTML
    assert report.total_points == 10.0
    assert report.passed_count == 6
    assert report.failed_count == 0


def test_html_grader_detects_missing_tags_and_rejects_empty_code() -> None:
    """Перевіряє виявлення помилок верстки та відхилення порожнього HTML-коду."""
    incomplete_html = "<div><table><tr><td>1</td></tr></table><img src='a.png'></div>"

    rules = [
        GradingRule(
            id="h1",
            type=GradingRuleType.HTML_TAG_EXISTS,
            target="header > h1",
            expected="true",
            points=3.0,
            description="Наявний header > h1",
        ),
        GradingRule(
            id="h2",
            type=GradingRuleType.HTML_TAG_COUNT,
            target="table tr",
            expected=">=4",
            points=4.0,
            description="Щонайменше 4 рядки таблиці",
        ),
        GradingRule(
            id="h3",
            type=GradingRuleType.HTML_ATTRIBUTE_EXISTS,
            target="img.alt",
            expected="true",
            points=3.0,
            description="Наявний атрибут alt у img",
        ),
    ]

    grader = HtmlGrader()
    report = grader.evaluate(raw_code=incomplete_html, rules=rules, variant_data={})

    assert report.total_points == 0.0
    assert report.passed_count == 0
    assert report.failed_count == 3

    with pytest.raises(InvalidFileFormatError):
        grader.evaluate(raw_code="   \n\t  ", rules=rules, variant_data={})

    incompatible_rule = [
        GradingRule(
            id="bad",
            type=GradingRuleType.XLSX_FORMULA,
            target="D12",
            expected="SUM(D2:D11)",
            points=2.0,
            description="Несумісне правило",
        )
    ]
    with pytest.raises(GradingError):
        grader.evaluate(raw_code=incomplete_html, rules=incompatible_rule, variant_data={})


def test_metadata_extraction_and_plagiarism_detection(tmp_path: Path) -> None:
    """Перевіряє екстракцію docProps/core.xml, SHA-256 хешування та детермінований антиплагіат."""
    student_a = uuid.uuid4()
    student_b = uuid.uuid4()
    submission_a_id = uuid.uuid4()

    docx_a = build_sample_docx(
        tmp_path / "student_a.docx",
        creator="Бондаренко Ірина",
        created_iso="2026-11-18T08:15:00Z",
        modified_iso="2026-11-18T09:00:00Z",
    )
    meta_a = extract_document_metadata(docx_a)
    hash_a = compute_file_sha256(docx_a)

    assert meta_a.creator == "Бондаренко Ірина"
    assert meta_a.created == "2026-11-18T08:15:00Z"
    assert meta_a.modified == "2026-11-18T09:00:00Z"
    assert len(hash_a) == 64

    existing_records = [
        DummySubmissionRecord(
            id=submission_a_id,
            student_id=student_a,
            file_hash=hash_a,
            extracted_metadata=meta_a,
        )
    ]

    # 1. Повторна здача тим самим студентом НЕ маркується як плагіат
    self_check = evaluate_plagiarism(
        student_id=student_a,
        file_hash=hash_a,
        metadata=meta_a,
        existing_submissions=existing_records,
    )
    assert self_check.is_flagged is False

    # 2. Збіг SHA-256 хешу між різними студентами
    hash_match_check = evaluate_plagiarism(
        student_id=student_b,
        file_hash=hash_a,
        metadata=ExtractedMetadata(
            creator="Інший Автор",
            created="2026-11-19T12:00:00Z",
        ),
        existing_submissions=existing_records,
    )
    assert hash_match_check.is_flagged is True
    assert hash_match_check.matched_submission_id == submission_a_id
    assert hash_match_check.matched_student_id == student_a
    assert hash_match_check.reason is not None
    assert "SHA-256" in hash_match_check.reason

    # 3. Різний хеш файлу, але збіг часу створення (created) у docProps/core.xml
    created_match_check = evaluate_plagiarism(
        student_id=student_b,
        file_hash="f" * 64,
        metadata=ExtractedMetadata(
            creator="Бондаренко Ірина",
            created="2026-11-18T08:15:00Z",
            modified="2026-11-18T19:45:00Z",
        ),
        existing_submissions=existing_records,
    )
    assert created_match_check.is_flagged is True
    assert created_match_check.matched_submission_id == submission_a_id
    assert created_match_check.reason is not None
    assert "docProps/core.xml" in created_match_check.reason

    # 4. Унікальна робота іншого студента
    clean_check = evaluate_plagiarism(
        student_id=student_b,
        file_hash="a" * 64,
        metadata=ExtractedMetadata(
            creator="Мельник Дмитро",
            created="2026-11-18T14:22:10Z",
            modified="2026-11-18T15:10:00Z",
        ),
        existing_submissions=existing_records,
    )
    assert clean_check.is_flagged is False
    assert clean_check.reason is None

    # 5. Нормалізація пробільних символів при хешуванні HTML-коду
    code_1 = "<header>\n  <h1>Розклад</h1>\n</header>"
    code_2 = "  <header>   <h1>Розклад</h1> </header>  "
    assert compute_code_sha256(code_1) == compute_code_sha256(code_2)
