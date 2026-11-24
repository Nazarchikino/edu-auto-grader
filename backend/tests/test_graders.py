import uuid
from dataclasses import dataclass
from pathlib import Path

import openpyxl  # type: ignore[import-untyped]
import pytest
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.graders.accdb_grader import AccdbGrader, build_accdb_bytes
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
from app.models.course import CourseSlug, PracticalFormat
from app.schemas.grading import ExtractedMetadata, GradingRule, GradingRuleType
from app.seed import build_seed_bundle
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
