import math
import shutil
import subprocess
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

import docx
import openpyxl  # type: ignore[import-untyped]
import pytest
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from app.core.config import settings
from app.core.exceptions import GradingError, InvalidFileFormatError
from app.graders.accdb_grader import (
    AccdbGrader,
    _parse_msys_objects_csv,
    _parse_msys_relationships_csv,
    build_accdb_bytes,
)
from app.graders.docx_grader import DocxGrader
from app.graders.factory import GraderFactory
from app.graders.html_grader import (
    EMPTY_HTML_BODY_ERROR_MESSAGE,
    HtmlGrader,
    has_meaningful_html_body,
)
from app.graders.metadata import (
    CORE_XML_ARCHIVE_PATH,
    compute_code_sha256,
    compute_file_sha256,
    evaluate_plagiarism,
    extract_core_xml_metadata,
    extract_document_metadata,
    parse_core_xml_bytes,
    validate_zip_archive_safety,
)
from app.graders.xlsx_grader import XlsxGrader, _canonicalize_formula
from app.models.course import CourseSlug, PracticalFormat
from app.schemas.grading import ExtractedMetadata, GradingRule, GradingRuleType
from app.seed import build_seed_bundle
from app.services.student_import_service import parse_docx_students
from tests.conftest import (
    _replace_zip_member,
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


def test_xlsx_grader_supports_dollar_reference_and_any_formula_expressions(
    tmp_path: Path,
) -> None:
    """Перевіряє підтримку 'contains:$', '$', 'any' та '=' у правилах формул XlsxGrader."""
    xlsx_path = tmp_path / "formula_modes.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.title = "Sheet1"
    sheet["A1"] = 10
    sheet["A2"] = 20
    sheet["B2"] = 50
    sheet["B10"] = 100
    sheet["C2"] = "=B2/$B$10"
    sheet["C3"] = "=B2/B$10"
    sheet["C4"] = "=B2/B10"
    sheet["D2"] = "=SUM(A1:A5)"
    sheet["D3"] = 42
    sheet["D4"] = "="
    workbook.save(str(xlsx_path))
    workbook.close()

    rules = [
        GradingRule(
            id="abs_contains_pass",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!C2",
            expected="contains:$",
            points=1.0,
            description="Абсолютне посилання (=B2/$B$10) проходить contains:$",
        ),
        GradingRule(
            id="abs_bare_dollar_pass",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!C2",
            expected="$",
            points=1.0,
            description="Абсолютне посилання (=B2/$B$10) проходить одиничний $",
        ),
        GradingRule(
            id="mixed_contains_pass",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!C3",
            expected="contains:$",
            points=1.0,
            description="Змішане посилання (=B2/B$10) проходить contains:$",
        ),
        GradingRule(
            id="rel_contains_fail",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!C4",
            expected="contains:$",
            points=1.0,
            description="Відносне посилання (=B2/B10) не проходить contains:$",
        ),
        GradingRule(
            id="rel_bare_dollar_fail",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!C4",
            expected="$",
            points=1.0,
            description="Відносне посилання (=B2/B10) не проходить одиничний $",
        ),
        GradingRule(
            id="any_formula_pass",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!D2",
            expected="any",
            points=1.0,
            description="Реальна формула (=SUM(A1:A5)) проходить any",
        ),
        GradingRule(
            id="eq_formula_pass",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!D2",
            expected="=",
            points=1.0,
            description="Реальна формула (=SUM(A1:A5)) проходить =",
        ),
        GradingRule(
            id="any_static_fail",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!D3",
            expected="any",
            points=1.0,
            description="Статичне число (42) не проходить any",
        ),
        GradingRule(
            id="eq_static_fail",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!D3",
            expected="=",
            points=1.0,
            description="Статичне число (42) не проходить =",
        ),
        GradingRule(
            id="eq_empty_body_fail",
            type=GradingRuleType.XLSX_FORMULA,
            target="Sheet1!D4",
            expected="=",
            points=1.0,
            description="Порожня формула ('=') не проходить =",
        ),
    ]

    report = XlsxGrader().evaluate(file_path=xlsx_path, rules=rules, variant_data={})
    results_by_id = {item.rule_id: item for item in report.results}

    assert results_by_id["abs_contains_pass"].passed is True
    assert results_by_id["abs_bare_dollar_pass"].passed is True
    assert results_by_id["mixed_contains_pass"].passed is True
    assert results_by_id["rel_contains_fail"].passed is False
    assert results_by_id["rel_bare_dollar_fail"].passed is False
    assert results_by_id["any_formula_pass"].passed is True
    assert results_by_id["eq_formula_pass"].passed is True
    assert results_by_id["any_static_fail"].passed is False
    assert results_by_id["eq_static_fail"].passed is False
    assert results_by_id["eq_empty_body_fail"].passed is False
    assert report.passed_count == 5
    assert report.failed_count == 5
    assert report.total_points == 5.0


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


def test_accdb_grader_accepts_hyperlink_type_as_memo(tmp_path: Path) -> None:
    """Перевіряє розпізнавання типу Hyperlink / Гіперпосилання для поля TYPE_MEMO."""
    accdb_path = build_sample_accdb(
        tmp_path / "friends.accdb",
        tables={
            "Друзі": [
                ("№ п/п", "AUTONUMBER"),
                ("Прізвище", "SHORT TEXT"),
                ("Ел. пошта", "HYPERLINK"),
                ("Дата народження", "DATE/TIME"),
            ],
        },
    )

    rules = [
        GradingRule(
            id="a_email_hyperlink",
            type=GradingRuleType.ACCDB_COLUMN_TYPE,
            target="Друзі.Ел. пошта",
            expected="Hyperlink",
            points=4.0,
            description="Поле 'Друзі.Ел. пошта' має тип Hyperlink (TYPE_MEMO)",
        ),
        GradingRule(
            id="a_email_hyperlink_uk",
            type=GradingRuleType.ACCDB_COLUMN_TYPE,
            target="Друзі.Ел. пошта",
            expected="Гіперпосилання",
            points=3.0,
            description="Поле 'Друзі.Ел. пошта' відповідає українському аліасу Гіперпосилання",
        ),
        GradingRule(
            id="a_surname_not_hyperlink",
            type=GradingRuleType.ACCDB_COLUMN_TYPE,
            target="Друзі.Прізвище",
            expected="Hyperlink",
            points=3.0,
            description="Текстове поле Short Text НЕ повинно проходити перевірку Hyperlink",
        ),
    ]

    grader = AccdbGrader()
    report = grader.evaluate(file_path=accdb_path, rules=rules, variant_data={})

    assert report.results[0].passed is True
    assert report.results[0].actual == "MEMO"
    assert report.results[1].passed is True
    assert report.results[2].passed is False
    assert report.total_points == 7.0
    assert report.passed_count == 2
    assert report.failed_count == 1


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


def test_html_grader_attribute_filter_selector_and_compound_colspan() -> None:
    """Перевіряє селектори з атрибутним фільтром (input[type='email'] -> required) та colspan."""
    grader = HtmlGrader()

    email_required_rule = GradingRule(
        id="h_email_req",
        type=GradingRuleType.HTML_ATTRIBUTE_EXISTS,
        target="input[type='email']",
        expected="required",
        points=2.0,
        description="Поле введення email має атрибут required",
    )
    link_rel_rule = GradingRule(
        id="h_link_rel",
        type=GradingRuleType.HTML_ATTRIBUTE_EXISTS,
        target="a[target='_blank']",
        expected="rel",
        points=2.0,
        description="Зовнішнє посилання з target='_blank' містить атрибут rel",
    )
    meta_charset_rule = GradingRule(
        id="h_meta_charset",
        type=GradingRuleType.HTML_ATTRIBUTE_EXISTS,
        target="head meta[charset]",
        expected="charset",
        points=2.0,
        description="Метатег у head містить атрибут charset",
    )
    colspan_rule = GradingRule(
        id="h_colspan",
        type=GradingRuleType.HTML_TAG_EXISTS,
        target="table td[colspan], table th[colspan]",
        expected="true",
        points=4.0,
        description="Таблиця використовує об'єднання стовпців colspan",
    )
    rules = [email_required_rule, link_rel_rule, meta_charset_rule, colspan_rule]

    # 1. Без required, без rel, без charset і без colspan — усі 4 правила мають провалитися
    failing_html = """<!DOCTYPE html>
    <html lang="uk">
      <head><meta name="description" content="demo"></head>
      <body>
        <a href="https://example.com" target="_blank">Зовнішнє посилання</a>
        <form><input type="email" name="user_email"></form>
        <table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>
      </body>
    </html>
    """
    fail_report = grader.evaluate(raw_code=failing_html, rules=rules, variant_data={})
    assert fail_report.passed_count == 0
    assert fail_report.failed_count == 4
    assert fail_report.total_points == 0.0

    # 2. З required, rel, charset і th[colspan] — усі 4 правила мають пройти
    passing_th_html = """<!DOCTYPE html>
    <html lang="uk">
      <head><meta charset="UTF-8"></head>
      <body>
        <a href="https://example.com" target="_blank" rel="noopener noreferrer">Посилання</a>
        <form><input type="email" name="user_email" required></form>
        <table><tr><th colspan="2">Заголовок</th></tr><tr><td>1</td><td>2</td></tr></table>
      </body>
    </html>
    """
    pass_report_th = grader.evaluate(raw_code=passing_th_html, rules=rules, variant_data={})
    assert pass_report_th.passed_count == 4
    assert pass_report_th.failed_count == 0
    assert pass_report_th.total_points == 10.0

    # 3. Складений селектор також спрацьовує, коли colspan задано на <td>
    passing_td_html = """<!DOCTYPE html>
    <html lang="uk">
      <body>
        <table><tr><td colspan="2">Підсумок</td></tr></table>
      </body>
    </html>
    """
    pass_report_td = grader.evaluate(
        raw_code=passing_td_html,
        rules=[colspan_rule],
        variant_data={},
    )
    assert pass_report_td.passed_count == 1
    assert pass_report_td.total_points == 4.0


def test_html_grader_empty_body_and_starter_template_score_zero() -> None:
    """Перевіряє, що порожнє <body> або мінімальний шаблон набирають 0.0 балів у HtmlGrader."""
    starter_html = """<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Практична робота</title>
</head>
<body>
  <!-- Виконайте завдання тут -->
</body>
</html>"""

    assert has_meaningful_html_body(starter_html) is False
    assert (
        has_meaningful_html_body(
            "<!DOCTYPE html><html><head><title>T</title></head>"
            "<body><!-- <h1>X</h1> --> \n </body></html>"
        )
        is False
    )
    assert (
        has_meaningful_html_body(
            "<!DOCTYPE html><html lang='uk'><head><meta charset='UTF-8'></head></html>"
        )
        is False
    )
    assert has_meaningful_html_body("<!DOCTYPE html><body>Текст</body>") is True
    assert has_meaningful_html_body("<!DOCTYPE html><body><h1>Заголовок</h1></body>") is True
    assert has_meaningful_html_body("<!DOCTYPE html><header><h1>Фрагмент</h1></header>") is True

    rules = [
        GradingRule(
            id="r_lang",
            type=GradingRuleType.HTML_ATTRIBUTE_EXISTS,
            target="html",
            expected="lang",
            points=3.0,
            description="Атрибут lang у html",
        ),
        GradingRule(
            id="r_charset",
            type=GradingRuleType.HTML_ATTRIBUTE_EXISTS,
            target="head meta[charset]",
            expected="charset",
            points=3.0,
            description="Метатег charset",
        ),
        GradingRule(
            id="r_title",
            type=GradingRuleType.HTML_TAG_EXISTS,
            target="head > title",
            expected="true",
            points=4.0,
            description="Тег title у head",
        ),
    ]

    report = HtmlGrader().evaluate(raw_code=starter_html, rules=rules, variant_data={})
    assert report.total_points == 0.0
    assert report.passed_count == 0
    assert report.failed_count == 3
    assert all(item.feedback == EMPTY_HTML_BODY_ERROR_MESSAGE for item in report.results)


def test_docx_grader_supports_uniform_single_number_margin(tmp_path: Path) -> None:
    """Перевіряє підтримку уніфікованого числового формату полів сторінки ('2.0' -> 20 мм)."""
    docx_path = build_sample_docx(
        tmp_path / "uniform_margins.docx",
        left_mm=20.0,
        right_mm=20.0,
        top_mm=20.0,
        bottom_mm=20.0,
    )
    rule = GradingRule(
        id="w_uniform_margin",
        type=GradingRuleType.DOCX_PAGE_MARGINS,
        target="document",
        expected="2.0",
        points=2.0,
        description="Усі поля сторінки 2.0 см (20 мм)",
    )
    report = DocxGrader().evaluate(file_path=docx_path, rules=[rule], variant_data={})
    assert report.passed_count == 1
    assert report.total_points == 2.0


def test_docx_grader_resolves_placeholders_in_target_and_expected(
    tmp_path: Path,
) -> None:
    """Перевіряє підстановку {placeholder} одночасно у rule.target та rule.expected DocxGrader."""
    docx_path = build_sample_docx(
        tmp_path / "variant_placeholders.docx",
        left_mm=20.0,
        right_mm=20.0,
        top_mm=15.0,
        bottom_mm=15.0,
        font_name="Calibri",
        font_size_pt=12.0,
        line_spacing=1.5,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
        include_table=True,
        table_rows=5,
        table_cols=3,
    )

    rules = [
        GradingRule(
            id="w_ph_margins",
            type=GradingRuleType.DOCX_PAGE_MARGINS,
            target="{section_target}",
            expected="{margins}",
            points=2.0,
            description="Поля цільової секції за параметром варіанта",
        ),
        GradingRule(
            id="w_ph_font",
            type=GradingRuleType.DOCX_FONT,
            target="{text_target}",
            expected="{body_font}:{body_size}",
            points=2.5,
            description="Шрифт і кегль цільових абзаців за варіантом",
        ),
        GradingRule(
            id="w_ph_spacing",
            type=GradingRuleType.DOCX_LINE_SPACING,
            target="{text_target}",
            expected="{line_spacing}",
            points=2.0,
            description="Міжрядковий інтервал за варіантом",
        ),
        GradingRule(
            id="w_ph_align",
            type=GradingRuleType.DOCX_ALIGNMENT,
            target="{text_target}",
            expected="{body_alignment}",
            points=1.5,
            description="Вирівнювання абзаців за варіантом",
        ),
        GradingRule(
            id="w_ph_table",
            type=GradingRuleType.DOCX_TABLE_EXISTS,
            target="{table_target}",
            expected=">={min_rows}",
            points=2.0,
            description="Кількість рядків цільової таблиці за варіантом",
        ),
    ]

    variant_data: dict[str, object] = {
        "variant_number": 2,
        "parameters": {
            "section_target": "section_0",
            "text_target": "body",
            "table_target": "table_0.rows",
            "margins": "left=2cm,right=2cm,top=1.5cm,bottom=1.5cm",
            "body_font": "Calibri",
            "body_size": "12",
            "line_spacing": "1.5",
            "body_alignment": "left",
            "min_rows": 5,
        },
    }

    grader = DocxGrader()
    report = grader.evaluate(file_path=docx_path, rules=rules, variant_data=variant_data)

    assert report.total_points == 10.0
    assert report.max_points == 10.0
    assert report.passed_count == 5
    assert report.failed_count == 0
    results_by_id = {item.rule_id: item for item in report.results}
    assert results_by_id["w_ph_margins"].target == "section_0"
    assert results_by_id["w_ph_margins"].expected == "left=2cm,right=2cm,top=1.5cm,bottom=1.5cm"
    assert results_by_id["w_ph_font"].target == "body"
    assert results_by_id["w_ph_font"].expected == "Calibri:12"
    assert results_by_id["w_ph_table"].target == "table_0.rows"
    assert results_by_id["w_ph_table"].expected == ">=5"

    # Перевірка реальних правил word.json для проблемних варіантів (М1 Вар. 2 та М3 Вар. 2)
    bundle = build_seed_bundle()
    word_course = next(course for course in bundle.courses if course.slug == CourseSlug.WORD)

    m1_practical = next(m for m in word_course.modules if m.order_index == 1).practical
    assert m1_practical is not None
    m1_rules = [GradingRule.model_validate(r) for r in m1_practical.grading_rules]
    m1_v2 = next(v for v in m1_practical.variants if v["variant_number"] == 2)
    m1_v2_docx = build_sample_docx(
        tmp_path / "word_m1_v2.docx",
        left_mm=20.0,
        right_mm=20.0,
        top_mm=20.0,
        bottom_mm=20.0,
        font_name="Calibri",
        font_size_pt=12.0,
        line_spacing=1.5,
        alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
    )
    m1_v2_report = grader.evaluate(
        file_path=m1_v2_docx,
        rules=m1_rules,
        variant_data=m1_v2,
    )
    assert m1_v2_report.total_points == 10.0
    assert m1_v2_report.failed_count == 0

    m3_practical = next(m for m in word_course.modules if m.order_index == 3).practical
    assert m3_practical is not None
    m3_rules = [GradingRule.model_validate(r) for r in m3_practical.grading_rules]
    m3_v2 = next(v for v in m3_practical.variants if v["variant_number"] == 2)
    m3_v2_docx = build_sample_docx(
        tmp_path / "word_m3_v2.docx",
        left_mm=20.0,
        right_mm=20.0,
        top_mm=15.0,
        bottom_mm=15.0,
        font_name="Times New Roman",
        font_size_pt=14.0,
        line_spacing=1.15,
        alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
    )
    m3_v2_report = grader.evaluate(
        file_path=m3_v2_docx,
        rules=m3_rules,
        variant_data=m3_v2,
    )
    assert m3_v2_report.total_points == 10.0
    assert m3_v2_report.failed_count == 0


def test_accdb_grader_evaluates_access_module_9_multiple_variants(
    tmp_path: Path,
) -> None:
    """Перевіряє, що різні варіанти Модуля 9 Access (включно з 2, 4, 5) набирають 10/10 балів."""
    bundle = build_seed_bundle()
    access_course = next(course for course in bundle.courses if course.slug == CourseSlug.ACCESS)
    m9_module = next(module for module in access_course.modules if module.order_index == 9)
    assert m9_module.practical is not None

    rules = [GradingRule.model_validate(raw) for raw in m9_module.practical.grading_rules]
    grader = AccdbGrader()
    built_paths: dict[int, Path] = {}

    for target_variant_number in (1, 2, 4, 5):
        variant = next(
            v
            for v in m9_module.practical.variants
            if v["variant_number"] == target_variant_number
        )
        raw_params = variant.get("parameters")
        assert isinstance(raw_params, dict)
        raw_tables = raw_params.get("tables")
        assert isinstance(raw_tables, list) and len(raw_tables) >= 3

        accdb_tables: dict[str, list[tuple[str, str]]] = {}
        for table_entry in raw_tables:
            assert isinstance(table_entry, dict)
            table_name = str(table_entry["name"])
            raw_fields = table_entry["fields"]
            raw_pks = set(table_entry.get("primary_keys", []))
            assert isinstance(raw_fields, list)
            accdb_tables[table_name] = [
                (str(field), "AUTONUMBER" if field in raw_pks else "SHORT TEXT")
                for field in raw_fields
            ]

        accdb_path = tmp_path / f"access_m09_v{target_variant_number}.accdb"
        accdb_path.write_bytes(build_accdb_bytes(accdb_tables))
        built_paths[target_variant_number] = accdb_path

        report = grader.evaluate(
            file_path=accdb_path,
            rules=rules,
            variant_data=variant,
        )
        assert report.total_points == 10.0, (
            f"Варіант {target_variant_number} Модуля 9 Access набрав {report.total_points}/10.0"
        )
        assert report.max_points == 10.0
        assert report.passed_count == 4
        assert report.failed_count == 0

    # База даних Варіанта 1 не повинна проходити перевірку для Варіанта 2
    variant_2 = next(v for v in m9_module.practical.variants if v["variant_number"] == 2)
    mismatch_report = grader.evaluate(
        file_path=built_paths[1],
        rules=rules,
        variant_data=variant_2,
    )
    assert mismatch_report.total_points == 0.0
    assert mismatch_report.passed_count == 0
    assert mismatch_report.failed_count == 4


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


def test_zip_bomb_protection_blocks_high_ratio_many_entries_and_oversized_uncompressed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє блокування Zip-бомб за коефіцієнтом стиснення, кількістю й розміром файлів."""
    # 1. ZIP із високим коефіцієнтом стиснення нулів (> 100x при file_size > 1 МБ)
    ratio_bomb_docx = tmp_path / "ratio_bomb.docx"
    with zipfile.ZipFile(ratio_bomb_docx, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("word/document.xml", b"\x00" * (2 * 1024 * 1024))

    ratio_bomb_xlsx = tmp_path / "ratio_bomb.xlsx"
    ratio_bomb_xlsx.write_bytes(ratio_bomb_docx.read_bytes())

    with pytest.raises(GradingError) as exc_direct:
        validate_zip_archive_safety(ratio_bomb_docx)
    assert exc_direct.value.status_code == 422
    assert exc_direct.value.code == "UNSAFE_ZIP_ARCHIVE"

    with pytest.raises(GradingError) as exc_meta:
        extract_core_xml_metadata(ratio_bomb_docx)
    assert exc_meta.value.code == "UNSAFE_ZIP_ARCHIVE"

    with pytest.raises(GradingError) as exc_docx:
        DocxGrader().evaluate(file_path=ratio_bomb_docx, rules=[], variant_data={})
    assert exc_docx.value.code == "UNSAFE_ZIP_ARCHIVE"

    with pytest.raises(GradingError) as exc_xlsx:
        XlsxGrader().evaluate(file_path=ratio_bomb_xlsx, rules=[], variant_data={})
    assert exc_xlsx.value.code == "UNSAFE_ZIP_ARCHIVE"

    with pytest.raises(GradingError) as exc_import:
        parse_docx_students(ratio_bomb_docx.read_bytes())
    assert exc_import.value.code == "UNSAFE_ZIP_ARCHIVE"

    # 2. ZIP із понад 500 записами (> MAX_ZIP_ENTRIES)
    many_entries_zip = tmp_path / "many_entries.docx"
    with zipfile.ZipFile(many_entries_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for idx in range(settings.MAX_ZIP_ENTRIES + 1):
            zf.writestr(f"entry_{idx:04d}.txt", b"ok")

    with pytest.raises(GradingError) as exc_entries:
        validate_zip_archive_safety(many_entries_zip)
    assert exc_entries.value.status_code == 422
    assert exc_entries.value.code == "UNSAFE_ZIP_ARCHIVE"

    # 3. Перевищення MAX_ZIP_SINGLE_ENTRY_BYTES та MAX_ZIP_UNCOMPRESSED_BYTES
    sized_zip = tmp_path / "sized_entries.docx"
    with zipfile.ZipFile(sized_zip, mode="w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("part1.bin", b"A" * 1024)
        zf.writestr("part2.bin", b"B" * 1024)

    monkeypatch.setattr(settings, "MAX_ZIP_SINGLE_ENTRY_BYTES", 512)
    with pytest.raises(GradingError) as exc_single:
        validate_zip_archive_safety(sized_zip)
    assert exc_single.value.code == "UNSAFE_ZIP_ARCHIVE"

    monkeypatch.setattr(settings, "MAX_ZIP_SINGLE_ENTRY_BYTES", 2048)
    monkeypatch.setattr(settings, "MAX_ZIP_UNCOMPRESSED_BYTES", 1500)
    with pytest.raises(GradingError) as exc_total:
        validate_zip_archive_safety(sized_zip)
    assert exc_total.value.code == "UNSAFE_ZIP_ARCHIVE"


def test_core_xml_parser_rejects_xml_entity_expansion_billion_laughs(
    tmp_path: Path,
) -> None:
    """Перевіряє безпечне відхилення XML Entity Expansion (<!DOCTYPE lolz ...>) через defusedxml."""
    billion_laughs_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b"<!DOCTYPE lolz [\n"
        b'  <!ENTITY lol "lol">\n'
        b'  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">\n'
        b'  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">\n'
        b'  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">\n'
        b"]>\n"
        b'<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"'
        b' xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        b"  <dc:creator>&lol4;</dc:creator>\n"
        b"</cp:coreProperties>\n"
    )

    with pytest.raises(GradingError) as exc_direct:
        parse_core_xml_bytes(billion_laughs_xml)
    assert exc_direct.value.status_code == 422
    assert exc_direct.value.code == "UNSAFE_XML_CONTENT"

    malicious_docx = build_sample_docx(tmp_path / "xxe_core.docx")
    _replace_zip_member(malicious_docx, CORE_XML_ARCHIVE_PATH, billion_laughs_xml)

    with pytest.raises(GradingError) as exc_archive:
        extract_core_xml_metadata(malicious_docx)
    assert exc_archive.value.status_code == 422
    assert exc_archive.value.code == "UNSAFE_XML_CONTENT"


def test_xlsx_grader_evaluates_uncached_complex_cross_sheet_and_localized_formulas(
    tmp_path: Path,
) -> None:
    """Перевіряє AST-обчислення формул без кешу (LibreOffice/Sheets), локалізації та цикли."""
    # Перевірка локалізації у _canonicalize_formula без пошкодження тексту в лапках
    assert (
        _canonicalize_formula(
            '=ЯКЩО(І(A1>0; B1<10); "ЯКЩО(СУММ(A1))"; "Ні")',
            strip_dollar=False,
        )
        == 'IF(AND(A1>0,B1<10),"ЯКЩО(СУММ(A1))","Ні")'
    )
    assert (
        _canonicalize_formula(
            "=СУММ($B$2:$B$5)+ВПР(C2;'Квартал 1'!$A$2:$B$5;2;FALSE)",
            strip_dollar=True,
        )
        == "SUM(B2:B5)+VLOOKUP(C2,'Квартал 1'!A2:B5,2,FALSE)"
    )

    xlsx_path = tmp_path / "uncached_complex.xlsx"
    wb = openpyxl.Workbook()
    ws_main = wb.active
    assert ws_main is not None
    ws_main.title = "Розрахунок"

    ws_ref = wb.create_sheet(title="Довідник")
    ws_ref["A1"] = "Код"
    ws_ref["B1"] = "Ціна"
    ws_ref["A2"] = "P1"
    ws_ref["B2"] = 120.0
    ws_ref["A3"] = "P2"
    ws_ref["B3"] = 250.0
    ws_ref["A4"] = "P3"
    ws_ref["B4"] = 400.0
    # Таблиця шкали для наближеного VLOOKUP (TRUE)
    ws_ref["D2"] = 0
    ws_ref["E2"] = "Незадовільно"
    ws_ref["D3"] = 60
    ws_ref["E3"] = "Задовільно"
    ws_ref["D4"] = 75
    ws_ref["E4"] = "Добре"
    ws_ref["D5"] = 90
    ws_ref["E5"] = "Відмінно"

    ws_quoted = wb.create_sheet(title="Квартал 1")
    ws_quoted["B2"] = 5.0

    # Вхідні дані на основному аркуші (без кешованих результатів формул!)
    ws_main["B2"] = 10.0
    ws_main["C2"] = 5.0
    ws_main["D2"] = 3.0
    ws_main["B3"] = 20.0
    ws_main["B4"] = 30.0
    ws_main["A5"] = "P2"
    ws_main["A6"] = 82.0
    ws_main["A7"] = 0.0
    ws_main["A8"] = "ІТ"
    ws_main["B8"] = 100.0
    ws_main["A9"] = "Економіка"
    ws_main["B9"] = 200.0
    ws_main["A10"] = "ІТ"
    ws_main["B10"] = 350.0

    # 1. Вкладені дужки та міжсторінкове посилання з лапками: (10+5)*3 + 5 = 50
    ws_main["E2"] = "=(B2+C2)*D2+'Квартал 1'!$B$2"
    # 2. IF + AND/OR/NOT (ліниве обчислення у E4 уникає ділення на нуль)
    ws_main["E3"] = '=IF(AND(B2>5, OR(C2=5, NOT(D2=3))), "Пройдено", "Провал")'
    ws_main["E4"] = "=IF(A7=0, 42, 100/A7)"
    # 3. VLOOKUP точний (FALSE) та наближений (TRUE) по міжсторінковому діапазону Довідник!
    ws_main["E5"] = "=VLOOKUP(A5, Довідник!$A$2:$B$4, 2, FALSE)"
    ws_main["E6"] = "=VLOOKUP(A6, Довідник!$D$2:$E$5, 2, TRUE)"
    # 4. Математичні функції: SQRT, EXP, COS, SIN, ABS, ROUND, POWER
    ws_main["E7"] = "=ROUND(SQRT(16) + EXP(0) + COS(0) + SIN(0) + ABS(-3.5) + POWER(2, 3), 1)"
    # 5. Локалізовані українські/російські назви функцій (СУММ, ЯКЩО, ВПР, КОРІНЬ, ОКРУГЛ)
    ws_main["E8"] = "=СУММ(B2:B4)"
    ws_main["E9"] = '=ЯКЩО(І(B2=10; C2=5); ВПР(A5; Довідник!$A$2:$B$4; 2; 0); 0)'
    ws_main["E10"] = "=ОКРУГЛ(КОРІНЬ(2) * 10; 2)"
    # 6. SUMIF, COUNTIF, COUNTA
    ws_main["E11"] = '=SUMIF(A8:A10, "ІТ", B8:B10)'
    ws_main["E12"] = '=COUNTIF(B8:B10, ">=200")'
    ws_main["E13"] = "=COUNTA(A8:A10)"
    # 7. Циклічні посилання та перевищення ліміту глибини рекурсії (> 30) не зависають
    ws_main["F1"] = "=F2+1"
    ws_main["F2"] = "=F1+1"
    ws_main["F3"] = "=F3*2"
    ws_main["F4"] = "=" + ("ABS(" * 35) + "1" + (")" * 35)

    wb.save(str(xlsx_path))
    wb.close()

    # Переконуємося, що data_only=True справді містить None для формульних комірок
    check_wb = openpyxl.load_workbook(str(xlsx_path), data_only=True)
    assert check_wb["Розрахунок"]["E2"].value is None
    assert check_wb["Розрахунок"]["E5"].value is None
    assert check_wb["Розрахунок"]["E9"].value is None
    check_wb.close()

    rules = [
        GradingRule(
            id="r_nested_cross",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E2",
            expected="50",
            points=1.0,
            description="Вкладені дужки та міжсторінкове посилання у лапках",
        ),
        GradingRule(
            id="r_if_and_or",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E3",
            expected="Пройдено",
            points=1.0,
            description="IF з AND/OR/NOT повертає рядок",
        ),
        GradingRule(
            id="r_if_lazy",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E4",
            expected="42",
            points=1.0,
            description="IF ліниво не обчислює гілку з діленням на нуль",
        ),
        GradingRule(
            id="r_vlookup_exact",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E5",
            expected="250",
            points=1.0,
            description="Точний VLOOKUP по міжсторінковому діапазону Довідник!",
        ),
        GradingRule(
            id="r_vlookup_approx",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E6",
            expected="Добре",
            points=1.0,
            description="Наближений VLOOKUP (TRUE) по відсортованій шкалі",
        ),
        GradingRule(
            id="r_math",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E7",
            expected="17.5",
            points=1.0,
            description="SQRT + EXP + COS + SIN + ABS + POWER + ROUND",
        ),
        GradingRule(
            id="r_loc_sum_formula",
            type=GradingRuleType.XLSX_FORMULA,
            target="Розрахунок!E8",
            expected="SUM(B2:B4)",
            points=1.0,
            description="Локалізована СУММ нормалізується до SUM",
        ),
        GradingRule(
            id="r_loc_sum_val",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E8",
            expected="60",
            points=1.0,
            description="Обчислене значення локалізованої СУММ",
        ),
        GradingRule(
            id="r_loc_if_vlookup_formula",
            type=GradingRuleType.XLSX_FORMULA,
            target="Розрахунок!E9",
            expected="func:VLOOKUP",
            points=1.0,
            description="Локалізована ВПР проходить перевірку func:VLOOKUP",
        ),
        GradingRule(
            id="r_loc_if_vlookup_val",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E9",
            expected="250",
            points=1.0,
            description="Обчислення ЯКЩО + І + ВПР без кешу",
        ),
        GradingRule(
            id="r_loc_round_sqrt",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E10",
            expected=str(round(math.sqrt(2.0) * 10.0, 2)),
            points=1.0,
            description="Обчислення ОКРУГЛ(КОРІНЬ(2)*10; 2)",
        ),
        GradingRule(
            id="r_sumif",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E11",
            expected="450",
            points=1.0,
            description="Обчислення SUMIF за текстовим критерієм",
        ),
        GradingRule(
            id="r_countif",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E12",
            expected="2",
            points=1.0,
            description="Обчислення COUNTIF за числовим оператором",
        ),
        GradingRule(
            id="r_counta",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!E13",
            expected="3",
            points=1.0,
            description="Обчислення COUNTA",
        ),
        GradingRule(
            id="r_cycle_mutual",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!F1",
            expected="not_null",
            points=1.0,
            description="Взаємне циклічне посилання не зависає і повертає None",
        ),
        GradingRule(
            id="r_cycle_self",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!F3",
            expected="not_null",
            points=1.0,
            description="Самопосилання не зависає і повертає None",
        ),
        GradingRule(
            id="r_depth_overflow",
            type=GradingRuleType.XLSX_VALUE,
            target="Розрахунок!F4",
            expected="not_null",
            points=1.0,
            description="Глибоке вкладення > 30 дужок безпечно повертає None",
        ),
    ]

    report = XlsxGrader().evaluate(file_path=xlsx_path, rules=rules, variant_data={})
    by_id = {item.rule_id: item for item in report.results}

    for ok_id in (
        "r_nested_cross",
        "r_if_and_or",
        "r_if_lazy",
        "r_vlookup_exact",
        "r_vlookup_approx",
        "r_math",
        "r_loc_sum_formula",
        "r_loc_sum_val",
        "r_loc_if_vlookup_formula",
        "r_loc_if_vlookup_val",
        "r_loc_round_sqrt",
        "r_sumif",
        "r_countif",
        "r_counta",
    ):
        assert by_id[ok_id].passed is True, f"Rule {ok_id} failed: {by_id[ok_id].feedback}"

    assert by_id["r_cycle_mutual"].passed is False
    assert by_id["r_cycle_mutual"].actual is None
    assert by_id["r_cycle_self"].passed is False
    assert by_id["r_cycle_self"].actual is None
    assert by_id["r_depth_overflow"].passed is False
    assert by_id["r_depth_overflow"].actual is None
    assert report.passed_count == 14
    assert report.failed_count == 3


def test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults(
    tmp_path: Path,
) -> None:
    """Перевіряє повне спадкування шрифтів через ланцюжок base_style та <w:docDefaults>."""
    grader = DocxGrader()

    # Сценарій 1: Ланцюжок base_style (GrandChild -> Child -> Parent), run.font == None
    chain_docx = tmp_path / "base_style_chain.docx"
    doc1 = docx.Document()
    parent_style = doc1.styles.add_style("CollegeBase", WD_STYLE_TYPE.PARAGRAPH)
    parent_style.font.name = "Times New Roman"
    child_style = doc1.styles.add_style("CollegeChild", WD_STYLE_TYPE.PARAGRAPH)
    child_style.base_style = parent_style
    child_style.font.size = Pt(14)
    grandchild_style = doc1.styles.add_style("CollegeLeaf", WD_STYLE_TYPE.PARAGRAPH)
    grandchild_style.base_style = child_style

    p1 = doc1.add_paragraph(style="CollegeLeaf")
    r1 = p1.add_run("Текст без явного шрифту на рівні Run.")
    assert r1.font.name is None
    assert r1.font.size is None
    doc1.save(str(chain_docx))

    rule_chain = GradingRule(
        id="w_chain",
        type=GradingRuleType.DOCX_FONT,
        target="body",
        expected="Times New Roman:14",
        points=5.0,
        description="Шрифт успадковується через ланцюжок base_style",
    )
    report_chain = grader.evaluate(file_path=chain_docx, rules=[rule_chain], variant_data={})
    assert report_chain.passed_count == 1
    assert report_chain.results[0].actual == "Times New Roman:14"

    reopened_doc1 = docx.Document(str(chain_docx))
    assert grader._resolve_paragraph_font_name(reopened_doc1, reopened_doc1.paragraphs[0]) == (
        "Times New Roman"
    )
    assert grader._resolve_paragraph_font_size(reopened_doc1, reopened_doc1.paragraphs[0]) == 14.0

    # Сценарій 2: Шрифт і кегль задані виключно у <w:docDefaults><w:rPrDefault><w:rPr>
    defaults_docx = tmp_path / "doc_defaults_only.docx"
    doc2 = docx.Document()
    styles_el = doc2.styles.element
    existing_defaults = styles_el.find(qn("w:docDefaults"))
    if existing_defaults is not None:
        styles_el.remove(existing_defaults)

    doc_defaults_el = OxmlElement("w:docDefaults")
    rpr_default_el = OxmlElement("w:rPrDefault")
    rpr_el = OxmlElement("w:rPr")
    rfonts_el = OxmlElement("w:rFonts")
    rfonts_el.set(qn("w:ascii"), "Georgia")
    rfonts_el.set(qn("w:hAnsi"), "Georgia")
    sz_el = OxmlElement("w:sz")
    sz_el.set(qn("w:val"), "28")  # 28 half-points == 14 pt
    rpr_el.append(rfonts_el)
    rpr_el.append(sz_el)
    rpr_default_el.append(rpr_el)
    doc_defaults_el.append(rpr_default_el)
    styles_el.insert(0, doc_defaults_el)

    p2 = doc2.add_paragraph("Абзац зі стилем Normal без явних властивостей шрифту.")
    assert p2.runs[0].font.name is None
    assert p2.runs[0].font.size is None
    doc2.save(str(defaults_docx))

    rule_defaults = GradingRule(
        id="w_defaults",
        type=GradingRuleType.DOCX_FONT,
        target="body",
        expected="Georgia:14",
        points=5.0,
        description="Шрифт і кегль зчитуються з w:docDefaults",
    )
    report_defaults = grader.evaluate(
        file_path=defaults_docx, rules=[rule_defaults], variant_data={}
    )
    assert report_defaults.passed_count == 1
    assert report_defaults.results[0].actual == "Georgia:14"

    reopened_doc2 = docx.Document(str(defaults_docx))
    assert grader._resolve_paragraph_font_name(reopened_doc2, reopened_doc2.paragraphs[0]) == (
        "Georgia"
    )
    assert grader._resolve_paragraph_font_size(reopened_doc2, reopened_doc2.paragraphs[0]) == 14.0


def test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє MSysObjects/MSysRelationships в AccdbGrader (access-parser + mdb-export CSV)."""
    # 1. Прямий витяг із бінарного .accdb через access-parser (з фільтрацією прихованих)
    full_accdb_path = tmp_path / "full_objects.accdb"
    full_accdb_path.write_bytes(
        build_accdb_bytes(
            tables={
                "Students": [("ID", "AUTONUMBER"), ("FullName", "TEXT(120)")],
                "Grades": [("ID", "AUTONUMBER"), ("StudentID", "LONG"), ("Score", "DOUBLE")],
            },
            queries=["Запит_Успішність", "Query_TopStudents"],
            forms=["Форма_Студенти"],
            reports=["Звіт_Відомість"],
            relationships=[
                ("Grades", "Students", "StudentID", "ID", "Rel_Students_Grades"),
            ],
            extra_msys_objects=[
                ("~sq_fHiddenTempQuery", 5, 0),
                ("HiddenFormByFlag", -32768, 8),
                ("MSysNavPaneForm", -32768, -2147483648),
                ("SystemReportFlag2", -32764, 2),
            ],
        )
    )

    rules = [
        GradingRule(
            id="q_by_name_ok",
            type=GradingRuleType.ACCDB_QUERY_EXISTS,
            target="Запит_Успішність",
            expected="true",
            points=1.0,
            description="Існує запит Запит_Успішність",
        ),
        GradingRule(
            id="q_by_count_ok",
            type=GradingRuleType.ACCDB_QUERY_EXISTS,
            target="*",
            expected="min>=2",
            points=1.0,
            description="У БД щонайменше 2 користувацькі запити (без ~sq_)",
        ),
        GradingRule(
            id="q_hidden_ignored",
            type=GradingRuleType.ACCDB_QUERY_EXISTS,
            target="~sq_fHiddenTempQuery",
            expected="true",
            points=1.0,
            description="Тимчасовий запит ~sq_ ігнорується",
        ),
        GradingRule(
            id="f_by_name_ok",
            type=GradingRuleType.ACCDB_FORM_EXISTS,
            target="Форма_Студенти",
            expected="true",
            points=1.0,
            description="Існує форма Форма_Студенти",
        ),
        GradingRule(
            id="f_hidden_ignored",
            type=GradingRuleType.ACCDB_FORM_EXISTS,
            target="*",
            expected="==1",
            points=1.0,
            description="Рівно 1 видима форма (приховані та MSys відфільтровані)",
        ),
        GradingRule(
            id="r_by_name_ok",
            type=GradingRuleType.ACCDB_REPORT_EXISTS,
            target="Звіт_Відомість",
            expected="true",
            points=1.0,
            description="Існує звіт Звіт_Відомість",
        ),
        GradingRule(
            id="r_missing_fail",
            type=GradingRuleType.ACCDB_REPORT_EXISTS,
            target="Неіснуючий_Звіт",
            expected="true",
            points=1.0,
            description="Відсутній звіт має провалити перевірку",
        ),
        GradingRule(
            id="rel_arrow_ok",
            type=GradingRuleType.ACCDB_RELATIONSHIP_EXISTS,
            target="Students->Grades",
            expected="true",
            points=1.0,
            description="Зв'язок Students->Grades розпізнано незалежно від напрямку",
        ),
        GradingRule(
            id="rel_comma_ok",
            type=GradingRuleType.ACCDB_RELATIONSHIP_EXISTS,
            target="Grades,Students",
            expected="true",
            points=1.0,
            description="Зв'язок Grades,Students розпізнано",
        ),
        GradingRule(
            id="rel_wildcard_ok",
            type=GradingRuleType.ACCDB_RELATIONSHIP_EXISTS,
            target="*",
            expected="min>=1",
            points=1.0,
            description="Кількість зв'язків >= 1",
        ),
        GradingRule(
            id="rel_missing_fail",
            type=GradingRuleType.ACCDB_RELATIONSHIP_EXISTS,
            target="Students->Courses",
            expected="true",
            points=1.0,
            description="Неіснуючий зв'язок провалює перевірку",
        ),
    ]

    grader = AccdbGrader()
    report = grader.evaluate(file_path=full_accdb_path, rules=rules, variant_data={})
    by_id = {item.rule_id: item for item in report.results}

    assert by_id["q_by_name_ok"].passed is True
    assert by_id["q_by_count_ok"].passed is True
    assert by_id["q_by_count_ok"].actual == "2"
    assert by_id["q_hidden_ignored"].passed is False
    assert by_id["f_by_name_ok"].passed is True
    assert by_id["f_hidden_ignored"].passed is True
    assert by_id["f_hidden_ignored"].actual == "1"
    assert by_id["r_by_name_ok"].passed is True
    assert by_id["r_missing_fail"].passed is False
    assert by_id["rel_arrow_ok"].passed is True
    assert by_id["rel_comma_ok"].passed is True
    assert by_id["rel_wildcard_ok"].passed is True
    assert by_id["rel_missing_fail"].passed is False
    assert report.passed_count == 8
    assert report.failed_count == 3

    # 2. Тест CSV-парсерів та fallback-інтеграції через mdb-export (Linux/Docker шлях)
    msys_objects_csv = (
        "Id,Name,Type,Flags\n"
        "101,Запит_Боржники,5,0\n"
        "102,~sq_Internal,5,3\n"
        "103,Форма_Картка,-32768,0\n"
        "104,ПрихованаФорма,-32768,8\n"
        "105,Звіт_Підсумок,-32764,0\n"
        "106,MSysHiddenReport,-32764,-2147483648\n"
    )
    msys_rels_csv = (
        "szObject,szReferencedObject,szColumn,szReferencedColumn,szRelationship\n"
        "Orders,Customers,CustomerID,ID,FK_Orders_Customers\n"
    )

    csv_q, csv_f, csv_r = _parse_msys_objects_csv(msys_objects_csv)
    assert csv_q == ("Запит_Боржники",)
    assert csv_f == ("Форма_Картка",)
    assert csv_r == ("Звіт_Підсумок",)

    csv_rels = _parse_msys_relationships_csv(msys_rels_csv)
    assert len(csv_rels) == 1
    assert csv_rels[0].source_table == "Orders"
    assert csv_rels[0].referenced_table == "Customers"

    # База без об'єктів у бінарному MSysObjects — mdb-export fallback має підхопити об'єкти з CSV
    bare_accdb_path = tmp_path / "bare_for_mdbtools.accdb"
    bare_accdb_path.write_bytes(
        build_accdb_bytes(
            tables={
                "Customers": [("ID", "AUTONUMBER"), ("Title", "TEXT")],
                "Orders": [("ID", "AUTONUMBER"), ("CustomerID", "LONG")],
            }
        )
    )

    def _fake_which(binary_name: str) -> str | None:
        if binary_name == "mdb-export":
            return "/usr/bin/mdb-export"
        return None

    def _fake_subprocess_run(
        cmd: list[str],
        *,
        capture_output: bool,
        text: bool,
        timeout: int,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        assert capture_output is True
        assert text is True
        assert timeout == 10
        assert check is False
        table_arg = cmd[-1]
        if table_arg == "MSysObjects":
            return subprocess.CompletedProcess(cmd, 0, stdout=msys_objects_csv, stderr="")
        if table_arg == "MSysRelationships":
            return subprocess.CompletedProcess(cmd, 0, stdout=msys_rels_csv, stderr="")
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="not found")

    monkeypatch.setattr(shutil, "which", _fake_which)
    monkeypatch.setattr(subprocess, "run", _fake_subprocess_run)

    mdb_rules = [
        GradingRule(
            id="mdb_q",
            type=GradingRuleType.ACCDB_QUERY_EXISTS,
            target="Запит_Боржники",
            expected="true",
            points=2.5,
            description="Запит знайдено через mdb-export",
        ),
        GradingRule(
            id="mdb_f",
            type=GradingRuleType.ACCDB_FORM_EXISTS,
            target="any",
            expected="min>=1",
            points=2.5,
            description="Форма знайдена через mdb-export",
        ),
        GradingRule(
            id="mdb_r",
            type=GradingRuleType.ACCDB_REPORT_EXISTS,
            target="Звіт_Підсумок",
            expected="true",
            points=2.5,
            description="Звіт знайдено через mdb-export",
        ),
        GradingRule(
            id="mdb_rel",
            type=GradingRuleType.ACCDB_RELATIONSHIP_EXISTS,
            target="Customers->Orders",
            expected="true",
            points=2.5,
            description="Зв'язок знайдено через mdb-export",
        ),
    ]
    mdb_report = grader.evaluate(file_path=bare_accdb_path, rules=mdb_rules, variant_data={})
    assert mdb_report.total_points == 10.0
    assert mdb_report.passed_count == 4
    assert mdb_report.failed_count == 0
