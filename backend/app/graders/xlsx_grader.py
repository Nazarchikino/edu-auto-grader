import math
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

import openpyxl  # type: ignore[import-untyped]
from defusedxml import DefusedXmlException
from openpyxl.cell.cell import Cell  # type: ignore[import-untyped]
from openpyxl.utils.cell import (  # type: ignore[import-untyped]
    column_index_from_string,
    get_column_letter,
)
from openpyxl.utils.exceptions import InvalidFileException  # type: ignore[import-untyped]
from openpyxl.workbook.workbook import Workbook  # type: ignore[import-untyped]
from openpyxl.worksheet.worksheet import Worksheet  # type: ignore[import-untyped]

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.graders.base import BaseGrader, format_student_criterion_description
from app.graders.metadata import validate_zip_archive_safety
from app.models.course import PracticalFormat
from app.schemas.grading import (
    CriterionResult,
    GradingReport,
    GradingRule,
    GradingRuleType,
)

MAX_FORMULA_RECURSION_DEPTH = 30
_MAX_RANGE_CELLS = 10_000

LOCALIZED_FUNCTION_ALIASES: dict[str, str] = {
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
    "ABS": "ABS",
    "EXP": "EXP",
    "COS": "COS",
    "SIN": "SIN",
    "TAN": "TAN",
    "LN": "LN",
    "LOG10": "LOG10",
}

_LOCALIZED_BOOL_LITERALS: dict[str, bool] = {
    "TRUE": True,
    "FALSE": False,
    "ІСТИНА": True,
    "ИСТИНА": True,
    "ХИБНІСТЬ": False,
    "ЛОЖЬ": False,
}

_CELL_COORD_PATTERN = re.compile(r"^\$?([A-Za-z]{1,3})\$?([1-9]\d*)$")
_SHEET_INDEX_PATTERN = re.compile(r"^(?:sheet_)?(\d+)$", re.IGNORECASE)
_CHART_TARGET_SUFFIX_PATTERN = re.compile(
    r"^(.*?)(?:\.(count|type))?$",
    re.IGNORECASE,
)
_NUMERIC_CONDITION_CHECK_PATTERN = re.compile(
    r"^\s*(>=|<=|!=|==|>|<|=)?\s*([+-]?\d+(?:[.,]\d+)?)\s*$"
)
_BARE_FUNCTION_NAME_PATTERN = re.compile(
    r"^[A-Za-zА-Яа-яЁёІіЇїЄєҐґ_][A-Za-zА-Яа-яЁёІіЇїЄєҐґ_.]*$"
)
_FUNC_CALL_NAME_PATTERN = re.compile(
    r"(?<![A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9_!.])"
    r"([A-Za-zА-Яа-яЁёІіЇїЄєҐґ_][A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9_.]*)(?=\()"
)
_DOLLAR_CELL_REF_PATTERN = re.compile(
    r"\$([A-Za-z]{1,3})\$([1-9]\d*)|\$([A-Za-z]{1,3})([1-9]\d*)|([A-Za-z]{1,3})\$([1-9]\d*)"
)
_NUMBER_TOKEN_PATTERN = re.compile(
    r"(?:\d+(?:\.\d+)?|\.\d+)(?:[Ee][+-]?\d+)?"
)
_UNQUOTED_SHEET_REF_PATTERN = re.compile(
    r"([A-Za-zА-Яа-яЁёІіЇїЄєҐґ_][A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9_.]*)!"
    r"(\$?[A-Za-z]{1,3}\$?[1-9]\d*)"
    r"(?::(?:[A-Za-zА-Яа-яЁёІіЇїЄєҐґ_][A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9_.]*!)?"
    r"(\$?[A-Za-z]{1,3}\$?[1-9]\d*))?"
)
_QUOTED_SHEET_CELL_SUFFIX_PATTERN = re.compile(
    r"(\$?[A-Za-z]{1,3}\$?[1-9]\d*)"
    r"(?::(?:'(?:[^']|'')*'!)?(\$?[A-Za-z]{1,3}\$?[1-9]\d*))?"
)
_LOCAL_RANGE_TOKEN_PATTERN = re.compile(
    r"(\$?[A-Za-z]{1,3}\$?[1-9]\d*):(\$?[A-Za-z]{1,3}\$?[1-9]\d*)"
)
_LOCAL_CELL_TOKEN_PATTERN = re.compile(
    r"(\$?[A-Za-z]{1,3}\$?[1-9]\d*)(?![A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9_!.])"
)
_IDENT_TOKEN_PATTERN = re.compile(
    r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ_][A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9_.]*"
)
_CRITERIA_OP_PATTERN = re.compile(r"^\s*(>=|<=|<>|!=|>|<|=)(.*)$")

_EXCEL_ERROR_TOKENS: frozenset[str] = frozenset(
    {
        "#NULL!",
        "#DIV/0!",
        "#VALUE!",
        "#REF!",
        "#NAME?",
        "#NUM!",
        "#N/A",
        "#GETTING_DATA",
        "#CALC!",
        "#SPILL!",
    }
)

_WORKBOOK_WIDE_TARGETS: frozenset[str] = frozenset(
    {"workbook", "document", "all", "any", "*"}
)

_KNOWN_CHART_TYPE_ALIASES: dict[str, tuple[str, ...]] = {
    "bar": ("barchart", "bar3dchart"),
    "column": ("barchart", "bar3dchart"),
    "col": ("barchart", "bar3dchart"),
    "line": ("linechart", "line3dchart"),
    "pie": ("piechart", "pie3dchart", "projectedpiechart"),
    "doughnut": ("doughnutchart",),
    "area": ("areachart", "area3dchart"),
    "scatter": ("scatterchart",),
    "radar": ("radarchart",),
    "bubble": ("bubblechart",),
    "stock": ("stockchart",),
    "surface": ("surfacechart", "surface3dchart"),
}


class XlsxGrader(BaseGrader):
    """Стратегія детермінованої автоперевірки електронних таблиць Microsoft Excel (.xlsx)."""

    format_type: PracticalFormat = PracticalFormat.XLSX
    supported_rule_types: frozenset[GradingRuleType] = frozenset(
        {
            GradingRuleType.XLSX_FORMULA,
            GradingRuleType.XLSX_VALUE,
            GradingRuleType.XLSX_CHART_EXISTS,
        }
    )

    def _prepare_cell_target_for_validation(self, target: str) -> str:
        """Підставляє тестові координати замість плейсхолдерів у цілі комірки Excel."""
        cleaned = target.strip()
        if self.is_whole_placeholder(cleaned):
            return "A1"
        if "!" in cleaned:
            raw_sheet, raw_coord = cleaned.rsplit("!", 1)
            sheet_sample = self.substitute_placeholders_for_validation(raw_sheet, "Sheet1")
            coord_sample = self.substitute_placeholders_for_validation(raw_coord, "A1")
            return f"{sheet_sample}!{coord_sample}"
        return self.substitute_placeholders_for_validation(cleaned, "A1")

    def validate_rule_definition(self, rule: GradingRule) -> None:
        """Перевіряє синтаксис правила Microsoft Excel (.xlsx) перед збереженням у БД."""
        super().validate_rule_definition(rule)

        if rule.type == GradingRuleType.XLSX_FORMULA:
            target_sample = self._prepare_cell_target_for_validation(rule.target)
            self._parse_cell_target(rule, target_sample)

            expected_clean = rule.expected.strip()
            if self.is_whole_placeholder(expected_clean):
                return
            expected_lower = expected_clean.lower()
            if expected_lower in {"any", "true", "exists", "not_null", "=", "$"}:
                return

            for prefix in ("contains:", "func:", "function:"):
                if expected_lower.startswith(prefix):
                    raw_token = expected_clean[len(prefix) :].strip()
                    sample_token = self.substitute_placeholders_for_validation(
                        raw_token,
                        "1",
                    ).strip()
                    if not sample_token or not _canonicalize_formula(
                        sample_token,
                        strip_dollar="$" not in sample_token,
                    ):
                        raise GradingError(
                            f"Порожній або некоректний вираз після '{prefix}' у правилі "
                            f"'{rule.id}' (expected='{rule.expected}').",
                            code="INVALID_RULE_DEFINITION",
                            status_code=422,
                            context={"rule_id": rule.id, "expected": rule.expected},
                        )
                    return

            expected_sample = self.substitute_placeholders_for_validation(
                expected_clean,
                "1",
            )
            if not _has_balanced_formula_delimiters(expected_sample):
                raise GradingError(
                    f"Незбалансовані дужки або лапки у формулі expected='{rule.expected}' "
                    f"правила '{rule.id}'.",
                    code="INVALID_RULE_DEFINITION",
                    status_code=422,
                    context={"rule_id": rule.id, "expected": rule.expected},
                )
            canonical = _canonicalize_formula(
                expected_sample,
                strip_dollar="$" not in expected_sample,
            )
            if not canonical:
                raise GradingError(
                    f"Некоректний вираз формули expected='{rule.expected}' у правилі '{rule.id}'.",
                    code="INVALID_RULE_DEFINITION",
                    status_code=422,
                    context={"rule_id": rule.id, "expected": rule.expected},
                )
            return

        if rule.type == GradingRuleType.XLSX_VALUE:
            target_sample = self._prepare_cell_target_for_validation(rule.target)
            self._parse_cell_target(rule, target_sample)
            return

        if rule.type == GradingRuleType.XLSX_CHART_EXISTS:
            target_sample = self.substitute_placeholders_for_validation(
                rule.target,
                "Sheet1",
            ).strip()
            _, prop_mode = self._parse_chart_target(target_sample)

            if self.is_whole_placeholder(rule.expected):
                return
            expected_sample = self.substitute_placeholders_for_validation(
                rule.expected,
                "1",
            ).strip()
            expected_lower = expected_sample.lower()

            if expected_lower.startswith("type:"):
                chart_type = expected_sample[5:].strip().lower()
                if not chart_type or re.fullmatch(r"[a-z0-9_]+", chart_type) is None:
                    raise GradingError(
                        f"Некоректний тип діаграми '{rule.expected}' у правилі '{rule.id}'. "
                        "Приклади: 'type:bar', 'type:line', 'type:pie'.",
                        code="INVALID_RULE_DEFINITION",
                        status_code=422,
                        context={"rule_id": rule.id, "expected": rule.expected},
                    )
                return

            if prop_mode == "type":
                if re.fullmatch(r"[a-z0-9_]+", expected_lower) is None:
                    raise GradingError(
                        f"Некоректний тип діаграми '{rule.expected}' у правилі '{rule.id}'.",
                        code="INVALID_RULE_DEFINITION",
                        status_code=422,
                        context={"rule_id": rule.id, "expected": rule.expected},
                    )
                return

            if expected_lower in _KNOWN_CHART_TYPE_ALIASES or expected_lower.endswith("chart"):
                return

            if prop_mode != "count" and expected_lower in {"true", "false", "yes", "no"}:
                return

            self.validate_numeric_condition(rule, expected_sample)
            return

    def evaluate(
        self,
        *,
        file_path: Path | None = None,
        raw_code: str | None = None,
        rules: list[GradingRule],
        variant_data: dict[str, object],
    ) -> GradingReport:
        """Виконує перевірку книги .xlsx у режимах data_only=False та data_only=True."""
        resolved_path = self.require_file_path(file_path, expected_suffix=".xlsx")
        validate_zip_archive_safety(resolved_path)
        formula_wb, value_wb = self._open_workbooks(resolved_path)

        try:
            results: list[CriterionResult] = []
            for rule in rules:
                resolved_expected = self.resolve_expected(rule.expected, variant_data)
                resolved_target = self.resolve_expected(rule.target, variant_data)
                resolved_rule = rule.model_copy(
                    update={
                        "description": format_student_criterion_description(
                            rule.description,
                            variant_data,
                        )
                    }
                )
                result = self._evaluate_rule(
                    formula_wb=formula_wb,
                    value_wb=value_wb,
                    rule=resolved_rule,
                    target=resolved_target,
                    expected=resolved_expected,
                )
                results.append(result)

            return self.build_report(results)
        finally:
            formula_wb.close()
            value_wb.close()

    def _open_workbooks(self, file_path: Path) -> tuple[Workbook, Workbook]:
        """Відкриває книгу .xlsx двічі: для інспекції формул/діаграм та кешованих значень."""
        formula_wb: Workbook | None = None
        try:
            formula_wb = openpyxl.load_workbook(filename=str(file_path), data_only=False)
            value_wb = openpyxl.load_workbook(filename=str(file_path), data_only=True)
            if not isinstance(formula_wb, Workbook) or not isinstance(value_wb, Workbook):
                raise InvalidFileFormatError(
                    f"Файл '{file_path.name}' не вдалося завантажити як книгу Excel.",
                    context={"file_name": file_path.name},
                )
            return formula_wb, value_wb
        except InvalidFileFormatError:
            if formula_wb is not None:
                formula_wb.close()
            raise
        except DefusedXmlException as exc:
            if formula_wb is not None:
                formula_wb.close()
            raise GradingError(
                f"Книга Excel '{file_path.name}' містить небезпечні XML-конструкції "
                "(DTD або сутності).",
                code="UNSAFE_XML_CONTENT",
                context={
                    "file_name": file_path.name,
                    "error_type": type(exc).__name__,
                },
            ) from exc
        except (
            InvalidFileException,
            zipfile.BadZipFile,
            ET.ParseError,
            KeyError,
            ValueError,
            TypeError,
            EOFError,
            OSError,
        ) as exc:
            if formula_wb is not None:
                formula_wb.close()
            raise InvalidFileFormatError(
                f"Не вдалося прочитати книгу Excel '{file_path.name}': "
                "файл пошкоджений або не є коректним пакетом OpenXML (.xlsx).",
                context={"file_name": file_path.name, "error": str(exc)},
            ) from exc

    def _evaluate_rule(
        self,
        *,
        formula_wb: Workbook,
        value_wb: Workbook,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Маршрутизує перевірку окремого правила Excel за його типом."""
        if rule.type == GradingRuleType.XLSX_FORMULA:
            return self._evaluate_formula(
                formula_wb=formula_wb,
                rule=rule,
                target=target,
                expected=expected,
            )
        if rule.type == GradingRuleType.XLSX_VALUE:
            return self._evaluate_value(
                value_wb=value_wb,
                formula_wb=formula_wb,
                rule=rule,
                target=target,
                expected=expected,
            )
        if rule.type == GradingRuleType.XLSX_CHART_EXISTS:
            return self._evaluate_chart_exists(
                formula_wb=formula_wb,
                rule=rule,
                target=target,
                expected=expected,
            )

        raise GradingError(
            f"XlsxGrader не підтримує правило типу '{rule.type.value}'.",
            context={"rule_id": rule.id, "rule_type": rule.type.value},
        )

    def _evaluate_formula(
        self,
        *,
        formula_wb: Workbook,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє наявність та структуру формули у цільовій комірці (data_only=False)."""
        sheet_name, cell_coord = self._parse_cell_target(rule, target)
        worksheet = self._resolve_worksheet(formula_wb, sheet_name)

        if worksheet is None:
            missing_sheet = sheet_name or "active"
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=(
                    f"Аркуш '{missing_sheet}' для перевірки комірки '{cell_coord}' "
                    "не знайдено у книзі Excel."
                ),
                resolved_expected=expected,
            )

        cell = self._get_cell(worksheet, cell_coord)
        formula_text = self._extract_formula_text(cell)

        if formula_text is None:
            raw_val = cell.value if cell is not None else None
            if raw_val is None or (isinstance(raw_val, str) and not raw_val.strip()):
                return self.build_criterion_result(
                    rule,
                    passed=False,
                    actual=None,
                    feedback=(
                        f"Комірка '{worksheet.title}!{cell_coord}' порожня — "
                        f"очікувалася формула '{expected}'."
                    ),
                    resolved_expected=expected,
                )

            formatted_static = _format_cell_value(raw_val)
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=formatted_static,
                feedback=(
                    f"У комірці '{worksheet.title}!{cell_coord}' міститься статичне значення "
                    f"'{formatted_static}' замість формули '{expected}'."
                ),
                resolved_expected=expected,
            )

        passed = self._matches_expected_formula(formula_text, expected)
        display_formula = (
            formula_text if formula_text.startswith("=") else f"={formula_text}"
        )

        if passed:
            feedback = (
                f"Формула у комірці '{worksheet.title}!{cell_coord}' ({display_formula}) "
                f"відповідає очікуваній умові '{expected}'."
            )
        else:
            feedback = (
                f"Формула у комірці '{worksheet.title}!{cell_coord}' ({display_formula}) "
                f"не відповідає очікуваному виразу '{expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=display_formula,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_value(
        self,
        *,
        value_wb: Workbook,
        formula_wb: Workbook,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє обчислене (кешоване) значення у цільовій комірці (data_only=True)."""
        sheet_name, cell_coord = self._parse_cell_target(rule, target)
        worksheet = self._resolve_worksheet(value_wb, sheet_name)

        if worksheet is None:
            missing_sheet = sheet_name or "active"
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=(
                    f"Аркуш '{missing_sheet}' для перевірки значення комірки '{cell_coord}' "
                    "не знайдено у книзі Excel."
                ),
                resolved_expected=expected,
            )

        formula_sheet = self._resolve_worksheet(formula_wb, sheet_name)
        raw_value = self._resolve_cell_evaluated_value(
            value_sheet=worksheet,
            formula_sheet=formula_sheet,
            coord=cell_coord,
            value_wb=value_wb,
            formula_wb=formula_wb,
        )
        actual_str = _format_cell_value(raw_value)
        expected_clean = expected.strip()
        expected_lower = expected_clean.lower()

        # Перевірка на помилки обчислення формул Excel (#DIV/0!, #VALUE!, #NAME? тощо)
        if isinstance(raw_value, str) and raw_value.strip().upper() in _EXCEL_ERROR_TOKENS:
            err_token = raw_value.strip().upper()
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=err_token,
                feedback=(
                    f"Комірка '{worksheet.title}!{cell_coord}' містить помилку обчислення Excel "
                    f"'{err_token}'."
                ),
                resolved_expected=expected,
            )

        # Режим 1: Перевірка на непорожнє обчислене значення ('not_null', 'not_empty', 'exists')
        if expected_lower in {"not_null", "not_empty", "exists", "any"}:
            has_value = raw_value is not None and (
                not isinstance(raw_value, str) or bool(raw_value.strip())
            )
            if has_value:
                feedback = (
                    f"У комірці '{worksheet.title}!{cell_coord}' присутнє обчислене значення "
                    f"'{actual_str}'."
                )
            else:
                formula_cell = (
                    self._get_cell(formula_sheet, cell_coord)
                    if formula_sheet is not None
                    else None
                )
                has_uncalculated_formula = (
                    self._extract_formula_text(formula_cell) is not None
                )
                if has_uncalculated_formula:
                    feedback = (
                        f"У комірці '{worksheet.title}!{cell_coord}' відсутнє кешоване обчислене "
                        "значення (файл збережено без перерахунку формул в Excel)."
                    )
                else:
                    feedback = (
                        f"Комірка '{worksheet.title}!{cell_coord}' порожня — "
                        "очікувалося непорожнє обчислене значення."
                    )
            return self.build_criterion_result(
                rule,
                passed=has_value,
                actual=actual_str,
                feedback=feedback,
                resolved_expected=expected,
            )

        # Режим 2: Перевірка на порожнє значення ('null', 'empty', 'none')
        if expected_lower in {"null", "empty", "none"}:
            is_empty = raw_value is None or (
                isinstance(raw_value, str) and not raw_value.strip()
            )
            feedback = (
                f"Комірка '{worksheet.title}!{cell_coord}' порожня, як і очікувалося."
                if is_empty
                else (
                    f"Комірка '{worksheet.title}!{cell_coord}' містить значення '{actual_str}', "
                    "хоча очікувалася порожня комірка."
                )
            )
            return self.build_criterion_result(
                rule,
                passed=is_empty,
                actual=actual_str,
                feedback=feedback,
                resolved_expected=expected,
            )

        # Режим 3: Перевірка на числовий тип ('number', 'numeric')
        if expected_lower in {"number", "numeric"}:
            numeric_val = _try_parse_numeric(raw_value)
            is_numeric = numeric_val is not None
            feedback = (
                f"Значення комірки '{worksheet.title}!{cell_coord}' ({actual_str}) є числовим."
                if is_numeric
                else (
                    f"У комірці '{worksheet.title}!{cell_coord}' очікувалося числове значення, "
                    f"фактично: '{actual_str or 'порожньо'}'."
                )
            )
            return self.build_criterion_result(
                rule,
                passed=is_numeric,
                actual=actual_str,
                feedback=feedback,
                resolved_expected=expected,
            )

        if raw_value is None:
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=(
                    f"Комірка '{worksheet.title}!{cell_coord}' не містить обчисленого значення "
                    f"(очікувалося '{expected}')."
                ),
                resolved_expected=expected,
            )

        # Режим 4: Числова умова ('18500', '>=100', '<=500', '==1850.5')
        if _NUMERIC_CONDITION_CHECK_PATTERN.match(expected_clean) is not None:
            numeric_val = _try_parse_numeric(raw_value)
            if numeric_val is None:
                return self.build_criterion_result(
                    rule,
                    passed=False,
                    actual=actual_str,
                    feedback=(
                        f"Значення комірки '{worksheet.title}!{cell_coord}' ('{actual_str}') "
                        f"не є числом для перевірки умови '{expected}'."
                    ),
                    resolved_expected=expected,
                )

            passed = self.compare_numeric_condition(
                numeric_val,
                expected_clean,
                tolerance=1e-2,
            )
            feedback = (
                f"Обчислене значення у комірці '{worksheet.title}!{cell_coord}' ({actual_str}) "
                f"відповідає умові '{expected}'."
                if passed
                else (
                    f"Обчислене значення у комірці '{worksheet.title}!{cell_coord}' ({actual_str}) "
                    f"не відповідає очікуваній умові '{expected}'."
                )
            )
            return self.build_criterion_result(
                rule,
                passed=passed,
                actual=actual_str,
                feedback=feedback,
                resolved_expected=expected,
            )

        # Режим 5: Булеве значення
        if isinstance(raw_value, bool) and expected_lower in {
            "true",
            "false",
            "1",
            "0",
            "yes",
            "no",
        }:
            expected_bool = self.parse_bool_expected(expected_clean)
            passed = raw_value == expected_bool
            bool_actual = "true" if raw_value else "false"
            feedback = (
                f"Булеве значення у комірці '{worksheet.title}!{cell_coord}' ({bool_actual}) "
                f"відповідає очікуваному '{expected}'."
                if passed
                else (
                    f"Булеве значення у комірці '{worksheet.title}!{cell_coord}' ({bool_actual}) "
                    f"не збігається з очікуваним '{expected}'."
                )
            )
            return self.build_criterion_result(
                rule,
                passed=passed,
                actual=bool_actual,
                feedback=feedback,
                resolved_expected=expected,
            )

        # Режим 6: Текстове порівняння (без урахування регістру та зайвих пробілів)
        actual_text = (actual_str or "").strip()
        passed = actual_text.casefold() == expected_clean.casefold()
        feedback = (
            f"Значення у комірці '{worksheet.title}!{cell_coord}' ('{actual_text}') "
            f"відповідає очікуваному '{expected}'."
            if passed
            else (
                f"Значення у комірці '{worksheet.title}!{cell_coord}' ('{actual_text}') "
                f"не збігається з очікуваним '{expected}'."
            )
        )
        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_chart_exists(
        self,
        *,
        formula_wb: Workbook,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє наявність, кількість або тип діаграм (_charts) на аркуші чи у книзі."""
        sheet_target, prop_mode = self._parse_chart_target(target)
        worksheets = self._select_worksheets_for_charts(formula_wb, sheet_target)

        if not worksheets:
            available = ", ".join(formula_wb.sheetnames)
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=(
                    f"Аркуш '{sheet_target}' не знайдено у книзі Excel "
                    f"(наявні аркуші: {available})."
                ),
                resolved_expected=expected,
            )

        charts = self._collect_charts(worksheets)
        chart_count = len(charts)
        target_label = (
            f"аркуші '{worksheets[0].title}'"
            if len(worksheets) == 1
            else "книзі Excel"
        )

        expected_clean = expected.strip()
        expected_lower = expected_clean.lower()

        # Перевірка конкретного типу діаграми (target="Sheet1.type" або expected="type:bar"/"bar")
        chart_type_filter = self._extract_chart_type_filter(prop_mode, expected_clean)
        if chart_type_filter is not None:
            detected_types = [self._get_chart_type_name(c) for c in charts]
            matched = any(
                self._chart_matches_type(c, chart_type_filter) for c in charts
            )
            actual_types = ", ".join(detected_types) if detected_types else "none"
            feedback = (
                f"На {target_label} знайдено діаграму очікуваного типу '{chart_type_filter}' "
                f"(наявні: {actual_types})."
                if matched
                else (
                    f"На {target_label} не знайдено діаграми типу '{chart_type_filter}' "
                    f"(знайдено: {actual_types})."
                )
            )
            return self.build_criterion_result(
                rule,
                passed=matched,
                actual=actual_types,
                feedback=feedback,
                resolved_expected=expected,
            )

        # Булевий режим ('true', 'false', 'yes', 'no')
        if prop_mode != "count" and expected_lower in {"true", "false", "yes", "no"}:
            expected_bool = self.parse_bool_expected(expected_clean)
            actual_bool = chart_count > 0
            passed = actual_bool == expected_bool
            actual_str = "true" if actual_bool else "false"
        else:
            # Числовий режим ('>=1', '1', '==2')
            passed = self.compare_numeric_condition(chart_count, expected_clean)
            actual_str = str(chart_count)

        if passed:
            feedback = (
                f"Перевірку діаграм на {target_label} пройдено "
                f"(знайдено діаграм: {chart_count})."
            )
        else:
            feedback = (
                f"Умову щодо діаграм на {target_label} не виконано: "
                f"знайдено {chart_count}, очікується '{expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _parse_cell_target(
        self,
        rule: GradingRule,
        target: str,
    ) -> tuple[str | None, str]:
        """Розбирає цільову адресу комірки ('D12', '$D$12', 'Sheet1!D12', \"'Sheet 1'!D12\")."""
        cleaned = target.strip()
        sheet_name: str | None = None
        coord_part = cleaned

        if "!" in cleaned:
            raw_sheet, coord_part = cleaned.rsplit("!", 1)
            raw_sheet = raw_sheet.strip()
            if (
                len(raw_sheet) >= 2
                and raw_sheet[0] in {"'", '"'}
                and raw_sheet[-1] == raw_sheet[0]
            ):
                raw_sheet = raw_sheet[1:-1]
            sheet_name = raw_sheet.strip() or None

        coord_clean = coord_part.strip()
        match = _CELL_COORD_PATTERN.match(coord_clean)
        if match is None:
            raise GradingError(
                f"Некоректна адреса цільової комірки Excel у правилі: '{target}'.",
                context={"rule_id": rule.id, "target": target},
            )

        col_letters = match.group(1).upper()
        row_digits = match.group(2)
        return sheet_name, f"{col_letters}{row_digits}"

    def _parse_chart_target(self, target: str) -> tuple[str, str | None]:
        """Розбирає target для діаграм ('Sheet1', 'Sheet1.count', 'Sheet1.type', 'workbook')."""
        cleaned = target.strip()
        match = _CHART_TARGET_SUFFIX_PATTERN.match(cleaned)
        if match is None:
            return cleaned, None

        base_sheet = (match.group(1) or "").strip()
        prop_group = match.group(2)
        prop_mode = prop_group.lower() if prop_group is not None else None
        if (
            len(base_sheet) >= 2
            and base_sheet[0] in {"'", '"'}
            and base_sheet[-1] == base_sheet[0]
        ):
            base_sheet = base_sheet[1:-1].strip()

        return base_sheet or "active", prop_mode

    def _resolve_worksheet(
        self,
        workbook: Workbook,
        sheet_name: str | None,
    ) -> Worksheet | None:
        """Знаходить робочий аркуш за назвою, індексом або повертає активний аркуш."""
        worksheets: list[Worksheet] = [
            ws for ws in workbook.worksheets if isinstance(ws, Worksheet)
        ]
        if not worksheets:
            return None

        if sheet_name is None or sheet_name.strip().lower() in {"", "active"}:
            active = workbook.active
            if isinstance(active, Worksheet):
                return active
            return worksheets[0]

        requested = sheet_name.strip()

        # 1. Точний збіг назви аркуша
        for ws in worksheets:
            if ws.title == requested:
                return ws

        # 2. Збіг без урахування регістру
        requested_cf = requested.casefold()
        for ws in worksheets:
            if ws.title.casefold() == requested_cf:
                return ws

        # 3. Вибір за індексом ('0', 'sheet_0', '1', 'sheet_1')
        idx_match = _SHEET_INDEX_PATTERN.match(requested)
        if idx_match is not None:
            idx = int(idx_match.group(1))
            if 0 <= idx < len(worksheets):
                return worksheets[idx]

        return None

    def _select_worksheets_for_charts(
        self,
        workbook: Workbook,
        sheet_target: str,
    ) -> list[Worksheet]:
        """Вибирає один або всі аркуші книги для перевірки наявності діаграм."""
        worksheets: list[Worksheet] = [
            ws for ws in workbook.worksheets if isinstance(ws, Worksheet)
        ]
        if not worksheets:
            return []

        normalized = sheet_target.strip().lower()
        if normalized in _WORKBOOK_WIDE_TARGETS:
            return worksheets

        resolved = self._resolve_worksheet(workbook, sheet_target)
        return [resolved] if resolved is not None else []

    def _get_cell(self, worksheet: Worksheet, coord: str) -> Cell | None:
        """Безпечно повертає об'єкт Cell за координатою комірки."""
        candidate: object = worksheet[coord]
        if isinstance(candidate, Cell):
            return candidate
        return None

    def _extract_formula_text(self, cell: Cell | None) -> str | None:
        """Витягує текст формули з комірки (включно з ArrayFormula), якщо це формула."""
        if cell is None:
            return None

        raw_value: object = cell.value
        if raw_value is None:
            return None

        if isinstance(raw_value, str):
            stripped = raw_value.strip()
            if stripped.startswith("="):
                return stripped
            if cell.data_type == "f" and stripped:
                return f"={stripped}"
            return None

        # Підтримка ArrayFormula / DataTableFormula з openpyxl.worksheet.formula
        formula_attr: object = getattr(raw_value, "text", None)
        if isinstance(formula_attr, str) and formula_attr.strip():
            stripped_attr = formula_attr.strip()
            return (
                stripped_attr
                if stripped_attr.startswith("=")
                else f"={stripped_attr}"
            )

        return None

    def _resolve_cell_evaluated_value(
        self,
        *,
        value_sheet: Worksheet,
        formula_sheet: Worksheet | None,
        coord: str,
        value_wb: Workbook | None = None,
        formula_wb: Workbook | None = None,
        depth: int = 0,
        visited_cells: frozenset[tuple[str, str]] = frozenset(),
        memo: dict[tuple[str, str], object] | None = None,
        strict_formula_errors: bool = False,
    ) -> object:
        """Повертає кешоване значення з data_only=True або обчислює формулу через AST-парсер."""
        normalized_coord = _normalize_cell_coord(coord)
        cell_key = (value_sheet.title.casefold(), normalized_coord)

        if memo is not None and cell_key in memo:
            return memo[cell_key]

        cell = self._get_cell(value_sheet, normalized_coord)
        raw_value: object = cell.value if cell is not None else None
        if raw_value is not None:
            if (
                strict_formula_errors
                and isinstance(raw_value, str)
                and raw_value.strip().upper() in _EXCEL_ERROR_TOKENS
            ):
                raise _FormulaEvalError(f"Excel error token: {raw_value}")
            if memo is not None:
                memo[cell_key] = raw_value
            return raw_value

        if formula_sheet is None:
            return None

        formula_cell = self._get_cell(formula_sheet, normalized_coord)
        formula_text = self._extract_formula_text(formula_cell)
        if formula_text is None:
            return None

        if depth > MAX_FORMULA_RECURSION_DEPTH or cell_key in visited_cells:
            if strict_formula_errors:
                raise _FormulaEvalError("Recursion limit exceeded or circular reference detected.")
            return None

        resolved_value_wb = value_wb if value_wb is not None else value_sheet.parent
        resolved_formula_wb = formula_wb if formula_wb is not None else formula_sheet.parent
        if not isinstance(resolved_value_wb, Workbook) or not isinstance(
            resolved_formula_wb, Workbook
        ):
            if strict_formula_errors:
                raise _FormulaEvalError("Workbook context unavailable for formula evaluation.")
            return None

        eval_memo = memo if memo is not None else {}
        next_visited = visited_cells | {cell_key}

        try:
            computed = self._evaluate_fallback_formula(
                formula_text=formula_text,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                value_wb=resolved_value_wb,
                formula_wb=resolved_formula_wb,
                depth=depth + 1,
                visited_cells=next_visited,
                memo=eval_memo,
                raise_on_error=strict_formula_errors,
            )
        except _FormulaEvalError:
            if strict_formula_errors:
                raise
            return None

        eval_memo[cell_key] = computed
        return computed

    def _evaluate_fallback_formula(
        self,
        *,
        formula_text: str,
        value_sheet: Worksheet,
        formula_sheet: Worksheet,
        value_wb: Workbook | None = None,
        formula_wb: Workbook | None = None,
        depth: int = 0,
        visited_cells: frozenset[tuple[str, str]] = frozenset(),
        memo: dict[tuple[str, str], object] | None = None,
        raise_on_error: bool = False,
    ) -> object:
        """Безпечно обчислює формулу Excel через рекурсивний AST-парсер без використання eval()."""
        if depth > MAX_FORMULA_RECURSION_DEPTH:
            if raise_on_error:
                raise _FormulaEvalError("Max formula recursion depth exceeded.")
            return None

        resolved_value_wb = value_wb if value_wb is not None else value_sheet.parent
        resolved_formula_wb = formula_wb if formula_wb is not None else formula_sheet.parent
        if not isinstance(resolved_value_wb, Workbook) or not isinstance(
            resolved_formula_wb, Workbook
        ):
            if raise_on_error:
                raise _FormulaEvalError("Workbook context unavailable.")
            return None

        canonical = _canonicalize_formula(formula_text, strip_dollar=False)
        if not canonical:
            if raise_on_error:
                raise _FormulaEvalError("Empty formula expression.")
            return None

        eval_memo = memo if memo is not None else {}

        try:
            tokens = _tokenize_formula(canonical)
            ast_node = _FormulaParser(tokens).parse()
            result = self._eval_ast_node(
                node=ast_node,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                value_wb=resolved_value_wb,
                formula_wb=resolved_formula_wb,
                depth=depth,
                visited_cells=visited_cells,
                memo=eval_memo,
            )
            if isinstance(result, _RangeValue):
                raise _FormulaEvalError("Unexpected bare range result in scalar context.")
            return result
        except _FormulaEvalError:
            if raise_on_error:
                raise
            return None

    def _eval_ast_node(
        self,
        *,
        node: "_ExprNode",
        value_sheet: Worksheet,
        formula_sheet: Worksheet,
        value_wb: Workbook,
        formula_wb: Workbook,
        depth: int,
        visited_cells: frozenset[tuple[str, str]],
        memo: dict[tuple[str, str], object],
    ) -> object:
        """Рекурсивно обчислює вузол AST формули Excel із контролем глибини."""
        if depth > MAX_FORMULA_RECURSION_DEPTH:
            raise _FormulaEvalError("Max AST evaluation depth exceeded.")

        if isinstance(node, _NumberNode):
            return node.value
        if isinstance(node, _StringNode):
            return node.value
        if isinstance(node, _BoolNode):
            return node.value
        if isinstance(node, _EmptyArgNode):
            return None

        if isinstance(node, _CellRefNode):
            target_val_ws, target_frm_ws = self._resolve_formula_target_sheets(
                sheet_name=node.sheet_name,
                current_value_sheet=value_sheet,
                current_formula_sheet=formula_sheet,
                value_wb=value_wb,
                formula_wb=formula_wb,
            )
            return self._resolve_cell_evaluated_value(
                value_sheet=target_val_ws,
                formula_sheet=target_frm_ws,
                coord=node.coord,
                value_wb=value_wb,
                formula_wb=formula_wb,
                depth=depth,
                visited_cells=visited_cells,
                memo=memo,
                strict_formula_errors=True,
            )

        if isinstance(node, _RangeRefNode):
            return self._resolve_range_values(
                node=node,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                value_wb=value_wb,
                formula_wb=formula_wb,
                depth=depth,
                visited_cells=visited_cells,
                memo=memo,
            )

        if isinstance(node, _UnaryOpNode):
            operand_val = self._eval_ast_node(
                node=node.operand,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                value_wb=value_wb,
                formula_wb=formula_wb,
                depth=depth + 1,
                visited_cells=visited_cells,
                memo=memo,
            )
            num = _coerce_formula_number(operand_val)
            if node.op == "+":
                return num
            if node.op == "-":
                return -num
            if node.op == "%":
                return num / 100.0
            raise _FormulaEvalError(f"Unsupported unary operator: {node.op}")

        if isinstance(node, _BinaryOpNode):
            left_val = self._eval_ast_node(
                node=node.left,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                value_wb=value_wb,
                formula_wb=formula_wb,
                depth=depth + 1,
                visited_cells=visited_cells,
                memo=memo,
            )
            right_val = self._eval_ast_node(
                node=node.right,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                value_wb=value_wb,
                formula_wb=formula_wb,
                depth=depth + 1,
                visited_cells=visited_cells,
                memo=memo,
            )
            return _apply_binary_operator(node.op, left_val, right_val)

        if isinstance(node, _FuncCallNode):
            return self._eval_function_call(
                node=node,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                value_wb=value_wb,
                formula_wb=formula_wb,
                depth=depth + 1,
                visited_cells=visited_cells,
                memo=memo,
            )

        raise _FormulaEvalError(f"Unsupported AST node: {type(node).__name__}")

    def _resolve_formula_target_sheets(
        self,
        *,
        sheet_name: str | None,
        current_value_sheet: Worksheet,
        current_formula_sheet: Worksheet,
        value_wb: Workbook,
        formula_wb: Workbook,
    ) -> tuple[Worksheet, Worksheet | None]:
        """Визначає аркуші значень та формул для локального або міжсторінкового посилання."""
        if sheet_name is None:
            return current_value_sheet, current_formula_sheet

        target_val_ws = self._resolve_worksheet(value_wb, sheet_name)
        target_frm_ws = self._resolve_worksheet(formula_wb, sheet_name)
        if target_val_ws is None:
            raise _FormulaEvalError(f"Referenced worksheet '{sheet_name}' not found.")
        return target_val_ws, target_frm_ws

    def _resolve_range_values(
        self,
        *,
        node: "_RangeRefNode",
        value_sheet: Worksheet,
        formula_sheet: Worksheet,
        value_wb: Workbook,
        formula_wb: Workbook,
        depth: int,
        visited_cells: frozenset[tuple[str, str]],
        memo: dict[tuple[str, str], object],
    ) -> "_RangeValue":
        """Матеріалізує двовимірний діапазон комірок (включно з міжсторінковими посиланнями)."""
        target_val_ws, target_frm_ws = self._resolve_formula_target_sheets(
            sheet_name=node.sheet_name,
            current_value_sheet=value_sheet,
            current_formula_sheet=formula_sheet,
            value_wb=value_wb,
            formula_wb=formula_wb,
        )

        start_col, start_row = _split_cell_coord(node.start_coord)
        end_col, end_row = _split_cell_coord(node.end_coord)
        col_lo, col_hi = min(start_col, end_col), max(start_col, end_col)
        row_lo, row_hi = min(start_row, end_row), max(start_row, end_row)

        total_cells = (row_hi - row_lo + 1) * (col_hi - col_lo + 1)
        if total_cells > _MAX_RANGE_CELLS:
            raise _FormulaEvalError(
                f"Formula range exceeds safety cell limit ({total_cells} > {_MAX_RANGE_CELLS})."
            )

        rows: list[tuple[object, ...]] = []
        for r_idx in range(row_lo, row_hi + 1):
            row_values: list[object] = []
            for c_idx in range(col_lo, col_hi + 1):
                col_letter = str(get_column_letter(c_idx))
                val = self._resolve_cell_evaluated_value(
                    value_sheet=target_val_ws,
                    formula_sheet=target_frm_ws,
                    coord=f"{col_letter}{r_idx}",
                    value_wb=value_wb,
                    formula_wb=formula_wb,
                    depth=depth,
                    visited_cells=visited_cells,
                    memo=memo,
                    strict_formula_errors=True,
                )
                row_values.append(val)
            rows.append(tuple(row_values))

        return _RangeValue(rows=tuple(rows))

    def _eval_function_call(
        self,
        *,
        node: "_FuncCallNode",
        value_sheet: Worksheet,
        formula_sheet: Worksheet,
        value_wb: Workbook,
        formula_wb: Workbook,
        depth: int,
        visited_cells: frozenset[tuple[str, str]],
        memo: dict[tuple[str, str], object],
    ) -> object:
        """Обчислює підтримувані функції Excel (з лінивим обчисленням гілок IF)."""
        if depth > MAX_FORMULA_RECURSION_DEPTH:
            raise _FormulaEvalError("Max function nesting depth exceeded.")

        raw_name = node.name.upper()
        func_name = LOCALIZED_FUNCTION_ALIASES.get(raw_name, raw_name)
        args = node.args

        def _eval(arg_node: _ExprNode) -> object:
            return self._eval_ast_node(
                node=arg_node,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                value_wb=value_wb,
                formula_wb=formula_wb,
                depth=depth,
                visited_cells=visited_cells,
                memo=memo,
            )

        # Ліниве обчислення IF(cond, true_branch, [false_branch=False])
        if func_name == "IF":
            if len(args) not in {2, 3}:
                raise _FormulaEvalError("IF expects 2 or 3 arguments.")
            cond_val = _eval(args[0])
            if _coerce_formula_bool(cond_val):
                return _eval(args[1])
            if len(args) == 3:
                return _eval(args[2])
            return False

        if func_name == "PI":
            if args:
                raise _FormulaEvalError("PI expects 0 arguments.")
            return math.pi

        evaluated_args = [_eval(arg) for arg in args]

        if func_name in {"SUM", "AVERAGE", "MIN", "MAX", "COUNT"}:
            if not evaluated_args:
                raise _FormulaEvalError(f"{func_name} requires at least 1 argument.")
            numbers = _collect_numeric_values(evaluated_args)
            if func_name == "SUM":
                return float(sum(numbers))
            if func_name == "COUNT":
                return float(len(numbers))
            if func_name == "AVERAGE":
                if not numbers:
                    raise _FormulaEvalError("AVERAGE division by zero (no numeric values).")
                return float(sum(numbers) / len(numbers))
            if func_name == "MIN":
                return float(min(numbers)) if numbers else 0.0
            return float(max(numbers)) if numbers else 0.0

        if func_name == "COUNTA":
            if not evaluated_args:
                raise _FormulaEvalError("COUNTA requires at least 1 argument.")
            return float(_count_non_empty_values(evaluated_args))

        if func_name in {"AND", "OR"}:
            if not evaluated_args:
                raise _FormulaEvalError(f"{func_name} requires at least 1 argument.")
            bools = _collect_logical_values(evaluated_args)
            if not bools:
                raise _FormulaEvalError(f"{func_name} received no logical values.")
            return all(bools) if func_name == "AND" else any(bools)

        if func_name == "NOT":
            if len(evaluated_args) != 1:
                raise _FormulaEvalError("NOT expects exactly 1 argument.")
            return not _coerce_formula_bool(evaluated_args[0])

        if func_name == "VLOOKUP":
            return _eval_vlookup(evaluated_args)

        if func_name == "SUMIF":
            return _eval_sumif(evaluated_args)

        if func_name == "COUNTIF":
            return _eval_countif(evaluated_args)

        if func_name == "SQRT":
            val = _require_single_number(func_name, evaluated_args)
            if val < 0.0:
                raise _FormulaEvalError("SQRT domain error.")
            return math.sqrt(val)

        if func_name == "EXP":
            val = _require_single_number(func_name, evaluated_args)
            try:
                res = math.exp(val)
            except OverflowError as exc:
                raise _FormulaEvalError("EXP overflow.") from exc
            if math.isnan(res) or math.isinf(res):
                raise _FormulaEvalError("EXP non-finite result.")
            return res

        if func_name == "COS":
            return math.cos(_require_single_number(func_name, evaluated_args))

        if func_name == "SIN":
            return math.sin(_require_single_number(func_name, evaluated_args))

        if func_name == "TAN":
            return math.tan(_require_single_number(func_name, evaluated_args))

        if func_name == "LN":
            val = _require_single_number(func_name, evaluated_args)
            if val <= 0.0:
                raise _FormulaEvalError("LN domain error.")
            return math.log(val)

        if func_name == "LOG10":
            val = _require_single_number(func_name, evaluated_args)
            if val <= 0.0:
                raise _FormulaEvalError("LOG10 domain error.")
            return math.log10(val)

        if func_name == "ABS":
            return abs(_require_single_number(func_name, evaluated_args))

        if func_name == "ROUND":
            if len(evaluated_args) != 2:
                raise _FormulaEvalError("ROUND expects exactly 2 arguments.")
            num_val = _coerce_formula_number(evaluated_args[0])
            digits = int(math.trunc(_coerce_formula_number(evaluated_args[1])))
            return _excel_round(num_val, digits)

        if func_name == "POWER":
            if len(evaluated_args) != 2:
                raise _FormulaEvalError("POWER expects exactly 2 arguments.")
            base_val = _coerce_formula_number(evaluated_args[0])
            exp_val = _coerce_formula_number(evaluated_args[1])
            return _safe_power(base_val, exp_val)

        raise _FormulaEvalError(f"Unsupported Excel function: {func_name}")

    def _matches_expected_formula(
        self,
        actual_formula: str,
        expected_expr: str,
    ) -> bool:
        """Детерміновано порівнює фактичну формулу комірки з очікуваним виразом правила."""
        expected_clean = expected_expr.strip()
        expected_lower = expected_clean.lower()

        canonical_actual = _canonicalize_formula(actual_formula, strip_dollar=False)
        if expected_lower in {"any", "true", "exists", "not_null", "="}:
            return bool(canonical_actual)

        # Одиничний '$' трактуємо як вимогу наявності абсолютного/змішаного посилання ('contains:$')
        if expected_clean == "$":
            expected_clean = "contains:$"
            expected_lower = "contains:$"

        canonical_actual_no_dollar = _canonicalize_formula(
            actual_formula, strip_dollar=True
        )

        # Режим 'contains:<вираз>' або 'func:<ІМ'Я_ФУНКЦІЇ>'
        for prefix in ("contains:", "func:", "function:"):
            if expected_lower.startswith(prefix):
                token = expected_clean[len(prefix) :].strip()
                if not token:
                    raise GradingError(
                        f"Порожній вираз після префікса '{prefix}' у правилі формули.",
                        context={"expected": expected_expr},
                    )
                preserve_dollar = "$" in token
                canonical_token = _canonicalize_formula(
                    token, strip_dollar=not preserve_dollar
                )
                target_formula = (
                    canonical_actual if preserve_dollar else canonical_actual_no_dollar
                )
                bare_func = _normalize_bare_function_name(canonical_token)
                if bare_func is not None:
                    return (
                        re.search(
                            rf"\b{re.escape(bare_func)}\(",
                            target_formula,
                        )
                        is not None
                    )
                return canonical_token in target_formula

        # Якщо очікуване значення — лише ім'я функції без дужок (напр. 'SUM', 'ВПР', 'LOG10')
        stripped_expected = expected_clean.lstrip("=").strip()
        bare_expected_func = _normalize_bare_function_name(stripped_expected)
        if bare_expected_func is not None:
            if canonical_actual == bare_expected_func:
                return True
            return (
                re.search(rf"\b{re.escape(bare_expected_func)}\(", canonical_actual)
                is not None
            )

        # Повне канонічне порівняння формули
        preserve_dollar = "$" in expected_clean
        canonical_expected = _canonicalize_formula(
            expected_clean,
            strip_dollar=not preserve_dollar,
        )
        target_actual = (
            canonical_actual if preserve_dollar else canonical_actual_no_dollar
        )
        return target_actual == canonical_expected

    def _collect_charts(self, worksheets: list[Worksheet]) -> list[object]:
        """Збирає всі об'єкти діаграм із приватного списку _charts обраних аркушів."""
        collected: list[object] = []
        for ws in worksheets:
            raw_charts: object = getattr(ws, "_charts", None)
            if isinstance(raw_charts, list):
                collected.extend(raw_charts)
        return collected

    def _extract_chart_type_filter(
        self,
        prop_mode: str | None,
        expected_clean: str,
    ) -> str | None:
        """Визначає, чи вимагає правило перевірки конкретного типу діаграми."""
        lower = expected_clean.lower()
        if lower.startswith("type:"):
            chart_type = expected_clean[5:].strip().lower()
            if not chart_type:
                raise GradingError(
                    "Порожній тип діаграми після префікса 'type:'.",
                    context={"expected": expected_clean},
                )
            return chart_type

        if prop_mode == "type":
            return lower

        if lower in _KNOWN_CHART_TYPE_ALIASES or lower.endswith("chart"):
            return lower

        return None

    def _get_chart_type_name(self, chart: object) -> str:
        """Повертає канонічну назву класу або XML-тегу діаграми openpyxl."""
        tag_name: object = getattr(chart, "tagname", None)
        if isinstance(tag_name, str) and tag_name.strip():
            return tag_name.strip()
        return type(chart).__name__

    def _chart_matches_type(self, chart: object, expected_type: str) -> bool:
        """Перевіряє, чи відповідає об'єкт діаграми очікуваному типу (bar, line, pie тощо)."""
        class_name = type(chart).__name__.lower()
        tag_name = str(getattr(chart, "tagname", "")).lower()
        normalized_expected = expected_type.strip().lower()

        allowed_tags = _KNOWN_CHART_TYPE_ALIASES.get(normalized_expected)
        if allowed_tags is not None:
            return class_name in allowed_tags or tag_name in allowed_tags

        candidates = {class_name, tag_name}
        return (
            normalized_expected in candidates
            or f"{normalized_expected}chart" in candidates
        )


def _has_balanced_formula_delimiters(expr: str) -> bool:
    """Перевіряє баланс круглих дужок та подвійних лапок у виразі формули Excel."""
    in_quotes = False
    depth = 0
    idx = 0
    length = len(expr)
    while idx < length:
        ch = expr[idx]
        if ch == '"':
            if in_quotes and idx + 1 < length and expr[idx + 1] == '"':
                idx += 2
                continue
            in_quotes = not in_quotes
        elif not in_quotes:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return False
        idx += 1
    return (not in_quotes) and depth == 0


class _FormulaEvalError(Exception):
    """Внутрішній виняток безпечного обчислювача формул Excel."""


@dataclass(frozen=True, slots=True)
class _RangeValue:
    """Двовимірна матриця обчислених значень діапазону комірок Excel."""

    rows: tuple[tuple[object, ...], ...]


@dataclass(frozen=True, slots=True)
class _NumberNode:
    value: float


@dataclass(frozen=True, slots=True)
class _StringNode:
    value: str


@dataclass(frozen=True, slots=True)
class _BoolNode:
    value: bool


@dataclass(frozen=True, slots=True)
class _EmptyArgNode:
    pass


@dataclass(frozen=True, slots=True)
class _CellRefNode:
    sheet_name: str | None
    coord: str


@dataclass(frozen=True, slots=True)
class _RangeRefNode:
    sheet_name: str | None
    start_coord: str
    end_coord: str


@dataclass(frozen=True, slots=True)
class _UnaryOpNode:
    op: str
    operand: "_ExprNode"


@dataclass(frozen=True, slots=True)
class _BinaryOpNode:
    op: str
    left: "_ExprNode"
    right: "_ExprNode"


@dataclass(frozen=True, slots=True)
class _FuncCallNode:
    name: str
    args: tuple["_ExprNode", ...]


_ExprNode = (
    _NumberNode
    | _StringNode
    | _BoolNode
    | _EmptyArgNode
    | _CellRefNode
    | _RangeRefNode
    | _UnaryOpNode
    | _BinaryOpNode
    | _FuncCallNode
)


@dataclass(frozen=True, slots=True)
class _Token:
    kind: str
    value: str
    sheet_name: str | None = None
    end_coord: str | None = None


def _tokenize_formula(expr: str) -> list[_Token]:
    """Розбиває канонізовану формулу Excel на детермінований потік токенів."""
    tokens: list[_Token] = []
    idx = 0
    length = len(expr)

    while idx < length:
        ch = expr[idx]

        if ch.isspace():
            idx += 1
            continue

        # Текстовий літерал у подвійних лапках ("..." із екрануванням "")
        if ch == '"':
            idx += 1
            chars: list[str] = []
            closed = False
            while idx < length:
                if expr[idx] == '"':
                    if idx + 1 < length and expr[idx + 1] == '"':
                        chars.append('"')
                        idx += 2
                        continue
                    closed = True
                    idx += 1
                    break
                chars.append(expr[idx])
                idx += 1
            if not closed:
                raise _FormulaEvalError("Unterminated string literal in formula.")
            tokens.append(_Token(kind="STRING", value="".join(chars)))
            continue

        # Посилання на аркуш в одинарних лапках: 'Квартал 1'!$B$2 або 'Квартал 1'!$B$2:$D$10
        if ch == "'":
            idx += 1
            sheet_chars: list[str] = []
            closed = False
            while idx < length:
                if expr[idx] == "'":
                    if idx + 1 < length and expr[idx + 1] == "'":
                        sheet_chars.append("'")
                        idx += 2
                        continue
                    closed = True
                    idx += 1
                    break
                sheet_chars.append(expr[idx])
                idx += 1
            if not closed or idx >= length or expr[idx] != "!":
                raise _FormulaEvalError("Malformed quoted sheet reference in formula.")
            idx += 1
            sheet_name = "".join(sheet_chars)
            suffix_match = _QUOTED_SHEET_CELL_SUFFIX_PATTERN.match(expr, idx)
            if suffix_match is None:
                raise _FormulaEvalError("Missing cell coordinate after quoted sheet name.")
            start_coord = _normalize_cell_coord(suffix_match.group(1))
            end_group = suffix_match.group(2)
            idx = suffix_match.end()
            if end_group is not None:
                tokens.append(
                    _Token(
                        kind="RANGE",
                        value=start_coord,
                        sheet_name=sheet_name,
                        end_coord=_normalize_cell_coord(end_group),
                    )
                )
            else:
                tokens.append(
                    _Token(kind="CELL", value=start_coord, sheet_name=sheet_name)
                )
            continue

        # Числовий літерал (цілі, десяткові, експоненційні)
        if ch.isdigit() or (ch == "." and idx + 1 < length and expr[idx + 1].isdigit()):
            num_match = _NUMBER_TOKEN_PATTERN.match(expr, idx)
            if num_match is None:
                raise _FormulaEvalError("Invalid numeric literal in formula.")
            tokens.append(_Token(kind="NUMBER", value=num_match.group(0)))
            idx = num_match.end()
            continue

        # Міжсторінкове посилання без лапок: Аркуш!B2 або Довідник!A1:B5
        sheet_ref_match = _UNQUOTED_SHEET_REF_PATTERN.match(expr, idx)
        if sheet_ref_match is not None:
            sheet_name = sheet_ref_match.group(1)
            start_coord = _normalize_cell_coord(sheet_ref_match.group(2))
            end_group = sheet_ref_match.group(3)
            idx = sheet_ref_match.end()
            if end_group is not None:
                tokens.append(
                    _Token(
                        kind="RANGE",
                        value=start_coord,
                        sheet_name=sheet_name,
                        end_coord=_normalize_cell_coord(end_group),
                    )
                )
            else:
                tokens.append(
                    _Token(kind="CELL", value=start_coord, sheet_name=sheet_name)
                )
            continue

        # Ім'я функції перед '(' перевіряємо ДО координат (щоб LOG10(...) не став клітинкою)
        ident_match = _IDENT_TOKEN_PATTERN.match(expr, idx)
        if (
            ident_match is not None
            and ident_match.end() < length
            and expr[ident_match.end()] == "("
        ):
            tokens.append(_Token(kind="FUNC", value=ident_match.group(0).upper()))
            idx = ident_match.end()
            continue

        # Локальний діапазон клітинок: A1:A10 або $B$2:$D$10
        local_range_match = _LOCAL_RANGE_TOKEN_PATTERN.match(expr, idx)
        if local_range_match is not None:
            tokens.append(
                _Token(
                    kind="RANGE",
                    value=_normalize_cell_coord(local_range_match.group(1)),
                    end_coord=_normalize_cell_coord(local_range_match.group(2)),
                )
            )
            idx = local_range_match.end()
            continue

        # Локальне посилання на клітинку: A1, $B$2
        local_cell_match = _LOCAL_CELL_TOKEN_PATTERN.match(expr, idx)
        if local_cell_match is not None:
            tokens.append(
                _Token(kind="CELL", value=_normalize_cell_coord(local_cell_match.group(1)))
            )
            idx = local_cell_match.end()
            continue

        # Булеві літерали (TRUE/FALSE/ІСТИНА/ХИБНІСТЬ/ИСТИНА/ЛОЖЬ)
        if ident_match is not None:
            ident_upper = ident_match.group(0).upper()
            if ident_upper in _LOCALIZED_BOOL_LITERALS:
                tokens.append(_Token(kind="BOOL", value=ident_upper))
                idx = ident_match.end()
                continue
            raise _FormulaEvalError(f"Unsupported identifier in formula: {ident_upper}")

        # Двосимвольні оператори порівняння
        if idx + 1 < length and expr[idx : idx + 2] in {"<=", ">=", "<>"}:
            tokens.append(_Token(kind="OP", value=expr[idx : idx + 2]))
            idx += 2
            continue

        if ch in {"=", "<", ">", "+", "-", "*", "/", "^", "&", "%"}:
            tokens.append(_Token(kind="OP", value=ch))
            idx += 1
            continue
        if ch == "(":
            tokens.append(_Token(kind="LPAREN", value=ch))
            idx += 1
            continue
        if ch == ")":
            tokens.append(_Token(kind="RPAREN", value=ch))
            idx += 1
            continue
        if ch == ",":
            tokens.append(_Token(kind="COMMA", value=ch))
            idx += 1
            continue

        raise _FormulaEvalError(f"Unexpected character in formula: {ch!r}")

    tokens.append(_Token(kind="EOF", value=""))
    return tokens


class _FormulaParser:
    """Рекурсивний низхідний парсер формул Excel у типізоване дерево AST."""

    def __init__(self, tokens: list[_Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    def parse(self) -> _ExprNode:
        node = self._parse_comparison(depth=0)
        if self._peek().kind != "EOF":
            raise _FormulaEvalError(f"Unexpected trailing token: {self._peek().value!r}")
        return node

    def _peek(self) -> _Token:
        return self._tokens[self._pos]

    def _consume(self, expected_kind: str | None = None) -> _Token:
        tok = self._tokens[self._pos]
        if expected_kind is not None and tok.kind != expected_kind:
            raise _FormulaEvalError(
                f"Expected token {expected_kind}, got {tok.kind} ({tok.value!r})."
            )
        self._pos += 1
        return tok

    def _check_depth(self, depth: int) -> None:
        if depth > MAX_FORMULA_RECURSION_DEPTH:
            raise _FormulaEvalError("Max formula expression nesting depth exceeded.")

    def _parse_comparison(self, depth: int) -> _ExprNode:
        self._check_depth(depth)
        left = self._parse_concat(depth)
        while self._peek().kind == "OP" and self._peek().value in {
            "=",
            "<>",
            "<",
            "<=",
            ">",
            ">=",
        }:
            op = self._consume("OP").value
            right = self._parse_concat(depth)
            left = _BinaryOpNode(op=op, left=left, right=right)
        return left

    def _parse_concat(self, depth: int) -> _ExprNode:
        left = self._parse_additive(depth)
        while self._peek().kind == "OP" and self._peek().value == "&":
            op = self._consume("OP").value
            right = self._parse_additive(depth)
            left = _BinaryOpNode(op=op, left=left, right=right)
        return left

    def _parse_additive(self, depth: int) -> _ExprNode:
        left = self._parse_multiplicative(depth)
        while self._peek().kind == "OP" and self._peek().value in {"+", "-"}:
            op = self._consume("OP").value
            right = self._parse_multiplicative(depth)
            left = _BinaryOpNode(op=op, left=left, right=right)
        return left

    def _parse_multiplicative(self, depth: int) -> _ExprNode:
        left = self._parse_unary(depth)
        while self._peek().kind == "OP" and self._peek().value in {"*", "/"}:
            op = self._consume("OP").value
            right = self._parse_unary(depth)
            left = _BinaryOpNode(op=op, left=left, right=right)
        return left

    def _parse_unary(self, depth: int) -> _ExprNode:
        self._check_depth(depth)
        if self._peek().kind == "OP" and self._peek().value in {"+", "-"}:
            op = self._consume("OP").value
            operand = self._parse_unary(depth + 1)
            return _UnaryOpNode(op=op, operand=operand)
        return self._parse_power(depth)

    def _parse_power(self, depth: int) -> _ExprNode:
        left = self._parse_postfix(depth)
        while self._peek().kind == "OP" and self._peek().value == "^":
            self._consume("OP")
            right = self._parse_unary(depth + 1)
            left = _BinaryOpNode(op="^", left=left, right=right)
        return left

    def _parse_postfix(self, depth: int) -> _ExprNode:
        node = self._parse_primary(depth)
        while self._peek().kind == "OP" and self._peek().value == "%":
            self._consume("OP")
            node = _UnaryOpNode(op="%", operand=node)
        return node

    def _parse_primary(self, depth: int) -> _ExprNode:
        self._check_depth(depth)
        tok = self._peek()

        if tok.kind == "NUMBER":
            self._consume("NUMBER")
            try:
                num = float(tok.value)
            except ValueError as exc:
                raise _FormulaEvalError(f"Invalid number: {tok.value}") from exc
            if math.isnan(num) or math.isinf(num):
                raise _FormulaEvalError(f"Non-finite number: {tok.value}")
            return _NumberNode(value=num)

        if tok.kind == "STRING":
            self._consume("STRING")
            return _StringNode(value=tok.value)

        if tok.kind == "BOOL":
            self._consume("BOOL")
            return _BoolNode(value=_LOCALIZED_BOOL_LITERALS[tok.value])

        if tok.kind == "CELL":
            self._consume("CELL")
            return _CellRefNode(sheet_name=tok.sheet_name, coord=tok.value)

        if tok.kind == "RANGE":
            self._consume("RANGE")
            if tok.end_coord is None:
                raise _FormulaEvalError("Incomplete range token.")
            return _RangeRefNode(
                sheet_name=tok.sheet_name,
                start_coord=tok.value,
                end_coord=tok.end_coord,
            )

        if tok.kind == "FUNC":
            func_name = self._consume("FUNC").value
            self._consume("LPAREN")
            args: list[_ExprNode] = []
            if self._peek().kind != "RPAREN":
                while True:
                    if self._peek().kind in {"COMMA", "RPAREN"}:
                        args.append(_EmptyArgNode())
                    else:
                        args.append(self._parse_comparison(depth + 1))
                    if self._peek().kind == "COMMA":
                        self._consume("COMMA")
                        continue
                    break
            self._consume("RPAREN")
            return _FuncCallNode(name=func_name, args=tuple(args))

        if tok.kind == "LPAREN":
            self._consume("LPAREN")
            inner = self._parse_comparison(depth + 1)
            self._consume("RPAREN")
            return inner

        raise _FormulaEvalError(f"Unexpected token in formula: {tok.kind} ({tok.value!r})")


def _normalize_cell_coord(raw_coord: str) -> str:
    """Нормалізує адресу комірки Excel, прибираючи '$' та приводячи букви до верхнього регістру."""
    match = _CELL_COORD_PATTERN.match(raw_coord.strip())
    if match is None:
        raise _FormulaEvalError(f"Invalid cell coordinate: {raw_coord}")
    return f"{match.group(1).upper()}{match.group(2)}"


def _split_cell_coord(coord: str) -> tuple[int, int]:
    """Розбиває нормалізовану адресу комірки ('B12') на (column_index, row_index)."""
    match = _CELL_COORD_PATTERN.match(coord)
    if match is None:
        raise _FormulaEvalError(f"Invalid cell coordinate: {coord}")
    return int(column_index_from_string(match.group(1).upper())), int(match.group(2))


def _coerce_formula_number(value: object) -> float:
    """Приводить скалярне значення формули Excel до числа float (порожнє -> 0.0, bool -> 0/1)."""
    if isinstance(value, _RangeValue):
        raise _FormulaEvalError("Cannot coerce range to scalar number.")
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    numeric = _try_parse_numeric(value)
    if numeric is not None:
        return numeric
    raise _FormulaEvalError(f"Expected numeric value in formula, got {value!r}.")


def _coerce_formula_bool(value: object) -> bool:
    """Приводить скалярне значення формули Excel до булевого типу."""
    if isinstance(value, _RangeValue):
        raise _FormulaEvalError("Cannot coerce range to scalar bool.")
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return not math.isclose(float(value), 0.0, abs_tol=1e-12)
    if isinstance(value, str):
        upper = value.strip().upper()
        if upper in _LOCALIZED_BOOL_LITERALS:
            return _LOCALIZED_BOOL_LITERALS[upper]
    raise _FormulaEvalError(f"Expected logical value in formula, got {value!r}.")


def _format_concat_operand(value: object) -> str:
    """Форматує операнд оператора конкатенації '&' у рядок Excel."""
    if isinstance(value, _RangeValue):
        raise _FormulaEvalError("Cannot concatenate range directly.")
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, float):
        rounded = round(value)
        if math.isclose(value, float(rounded), abs_tol=1e-9):
            return str(rounded)
        return str(value)
    return str(value)


def _safe_power(base: float, exponent: float) -> float:
    """Безпечно виконує піднесення до степеня із перевіркою області визначення та переповнення."""
    if base < 0.0 and not float(exponent).is_integer():
        raise _FormulaEvalError("Negative base raised to non-integer power.")
    if math.isclose(base, 0.0, abs_tol=1e-15) and exponent < 0.0:
        raise _FormulaEvalError("Zero raised to negative power.")
    try:
        result = math.pow(base, exponent)
    except (ValueError, OverflowError) as exc:
        raise _FormulaEvalError("Power computation failed.") from exc
    if math.isnan(result) or math.isinf(result):
        raise _FormulaEvalError("Power produced non-finite value.")
    return result


def _excel_round(value: float, digits: int) -> float:
    """Виконує округлення за правилом Excel (half away from zero), включно з від'ємним digits."""
    if abs(digits) > 15:
        raise _FormulaEvalError("ROUND digits out of supported range.")
    try:
        dec_val = Decimal(str(value))
        if digits >= 0:
            quantum = Decimal(1).scaleb(-digits)
            rounded = dec_val.quantize(quantum, rounding=ROUND_HALF_UP)
        else:
            scale = Decimal(10) ** (-digits)
            rounded = (dec_val / scale).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * scale
        return float(rounded)
    except (InvalidOperation, ValueError, OverflowError) as exc:
        raise _FormulaEvalError("ROUND computation failed.") from exc


def _excel_compare(left: object, right: object) -> int:
    """Порівнює два скалярні значення за семантикою Excel (-1, 0, +1)."""
    if isinstance(left, _RangeValue) or isinstance(right, _RangeValue):
        raise _FormulaEvalError("Cannot compare range values directly.")

    # Порожня клітинка при порівнянні адаптується до типу іншого операнда
    if left is None and right is None:
        return 0
    if left is None:
        if isinstance(right, bool):
            left = False
        elif isinstance(right, str):
            left = ""
        else:
            left = 0.0
    elif right is None:
        if isinstance(left, bool):
            right = False
        elif isinstance(left, str):
            right = ""
        else:
            right = 0.0

    left_num = _try_parse_numeric(left) if not isinstance(left, str) else None
    right_num = _try_parse_numeric(right) if not isinstance(right, str) else None
    if left_num is not None and right_num is not None:
        if math.isclose(left_num, right_num, rel_tol=1e-9, abs_tol=1e-12):
            return 0
        return -1 if left_num < right_num else 1

    if isinstance(left, str) and isinstance(right, str):
        l_cf = left.casefold()
        r_cf = right.casefold()
        if l_cf == r_cf:
            return 0
        return -1 if l_cf < r_cf else 1

    if isinstance(left, bool) and isinstance(right, bool):
        if left == right:
            return 0
        return -1 if not left and right else 1

    # Порядок різних типів у Excel: число < текст < булеве значення
    def _type_rank(val: object) -> int:
        if isinstance(val, bool):
            return 2
        if isinstance(val, str):
            return 1
        return 0

    l_rank = _type_rank(left)
    r_rank = _type_rank(right)
    if l_rank == r_rank:
        return 0
    return -1 if l_rank < r_rank else 1


def _apply_binary_operator(op: str, left: object, right: object) -> object:
    """Застосовує арифметичний, рядковий або логічний бінарний оператор Excel."""
    if op == "&":
        return _format_concat_operand(left) + _format_concat_operand(right)

    if op in {"=", "<>", "<", "<=", ">", ">="}:
        cmp_res = _excel_compare(left, right)
        if op == "=":
            return cmp_res == 0
        if op == "<>":
            return cmp_res != 0
        if op == "<":
            return cmp_res < 0
        if op == "<=":
            return cmp_res <= 0
        if op == ">":
            return cmp_res > 0
        return cmp_res >= 0

    left_num = _coerce_formula_number(left)
    right_num = _coerce_formula_number(right)
    if op == "+":
        return left_num + right_num
    if op == "-":
        return left_num - right_num
    if op == "*":
        return left_num * right_num
    if op == "/":
        if math.isclose(right_num, 0.0, abs_tol=1e-15):
            raise _FormulaEvalError("Division by zero.")
        return left_num / right_num
    if op == "^":
        return _safe_power(left_num, right_num)

    raise _FormulaEvalError(f"Unsupported binary operator: {op}")


def _collect_numeric_values(evaluated_args: list[object]) -> list[float]:
    """Збирає числові значення з аргументів функцій SUM/AVERAGE/MIN/MAX/COUNT."""
    numbers: list[float] = []
    for arg in evaluated_args:
        if isinstance(arg, _RangeValue):
            for row in arg.rows:
                for cell_val in row:
                    if isinstance(cell_val, bool) or cell_val is None:
                        continue
                    if isinstance(cell_val, (int, float)):
                        fval = float(cell_val)
                        if not (math.isnan(fval) or math.isinf(fval)):
                            numbers.append(fval)
        elif arg is None:
            continue
        elif isinstance(arg, bool):
            numbers.append(1.0 if arg else 0.0)
        else:
            num = _try_parse_numeric(arg)
            if num is not None:
                numbers.append(num)
    return numbers


def _count_non_empty_values(evaluated_args: list[object]) -> int:
    """Рахує кількість непорожніх значень у діапазонах і скалярах (COUNTA)."""
    count = 0
    for arg in evaluated_args:
        if isinstance(arg, _RangeValue):
            for row in arg.rows:
                for cell_val in row:
                    if cell_val is not None and cell_val != "":
                        count += 1
        elif arg is not None and arg != "":
            count += 1
    return count


def _collect_logical_values(evaluated_args: list[object]) -> list[bool]:
    """Збирає логічні значення для функцій AND / OR."""
    bools: list[bool] = []
    for arg in evaluated_args:
        if isinstance(arg, _RangeValue):
            for row in arg.rows:
                for cell_val in row:
                    if cell_val is None or isinstance(cell_val, str):
                        continue
                    bools.append(_coerce_formula_bool(cell_val))
        else:
            bools.append(_coerce_formula_bool(arg))
    return bools


def _require_single_number(func_name: str, evaluated_args: list[object]) -> float:
    """Перевіряє, що функція отримала рівно один числовий аргумент."""
    if len(evaluated_args) != 1:
        raise _FormulaEvalError(f"{func_name} expects exactly 1 argument.")
    return _coerce_formula_number(evaluated_args[0])


def _excel_wildcard_to_regex(pattern: str) -> re.Pattern[str]:
    """Компілює шаблон Excel із підстановками '*', '?' та екрануванням '~' у regex."""
    regex_parts: list[str] = ["^"]
    idx = 0
    length = len(pattern)
    while idx < length:
        ch = pattern[idx]
        if ch == "~" and idx + 1 < length:
            regex_parts.append(re.escape(pattern[idx + 1]))
            idx += 2
            continue
        if ch == "*":
            regex_parts.append(".*")
        elif ch == "?":
            regex_parts.append(".")
        else:
            regex_parts.append(re.escape(ch))
        idx += 1
    regex_parts.append("$")
    return re.compile("".join(regex_parts), re.IGNORECASE | re.DOTALL)


def _matches_exact_lookup(cell_value: object, lookup_value: object) -> bool:
    """Перевіряє точний збіг значення для VLOOKUP(..., FALSE/0) із підтримкою wildcard."""
    if isinstance(lookup_value, str) and isinstance(cell_value, str):
        if any(marker in lookup_value for marker in ("*", "?", "~")):
            return _excel_wildcard_to_regex(lookup_value).match(cell_value) is not None
        return cell_value.casefold() == lookup_value.casefold()
    return _excel_compare(cell_value, lookup_value) == 0


def _eval_vlookup(evaluated_args: list[object]) -> object:
    """Обчислює VLOOKUP(lookup_value, table_array, col_index_num, [range_lookup=TRUE])."""
    if len(evaluated_args) not in {3, 4}:
        raise _FormulaEvalError("VLOOKUP expects 3 or 4 arguments.")

    lookup_value = evaluated_args[0]
    table_arg = evaluated_args[1]
    if not isinstance(table_arg, _RangeValue) or not table_arg.rows or not table_arg.rows[0]:
        raise _FormulaEvalError("VLOOKUP requires a non-empty range as second argument.")

    col_index = int(math.trunc(_coerce_formula_number(evaluated_args[2])))
    num_cols = len(table_arg.rows[0])
    if col_index < 1 or col_index > num_cols:
        raise _FormulaEvalError("VLOOKUP column index out of bounds.")

    range_lookup = True
    if len(evaluated_args) == 4 and evaluated_args[3] is not None:
        range_lookup = _coerce_formula_bool(evaluated_args[3])

    if not range_lookup:
        for row in table_arg.rows:
            if _matches_exact_lookup(row[0], lookup_value):
                return row[col_index - 1]
        raise _FormulaEvalError("VLOOKUP exact match not found (#N/A).")

    # Наближений пошук (TRUE/1): найбільше значення <= lookup_value у відсортованій колонці
    lookup_num = _try_parse_numeric(lookup_value) if not isinstance(lookup_value, str) else None
    matched_row: tuple[object, ...] | None = None
    for row in table_arg.rows:
        candidate = row[0]
        if candidate is None:
            continue
        if lookup_num is not None:
            cand_num = _try_parse_numeric(candidate) if not isinstance(candidate, str) else None
            if cand_num is None:
                continue
            if cand_num < lookup_num or math.isclose(
                cand_num, lookup_num, rel_tol=1e-9, abs_tol=1e-12
            ):
                matched_row = row
            else:
                break
        elif isinstance(lookup_value, str) and isinstance(candidate, str):
            if candidate.casefold() <= lookup_value.casefold():
                matched_row = row
            else:
                break
        elif isinstance(lookup_value, bool) and isinstance(candidate, bool):
            if int(candidate) <= int(lookup_value):
                matched_row = row
            else:
                break

    if matched_row is None:
        raise _FormulaEvalError("VLOOKUP approximate match not found (#N/A).")
    return matched_row[col_index - 1]


def _matches_excel_criteria(cell_value: object, criteria: object) -> bool:
    """Перевіряє відповідність значення комірки критерію функцій SUMIF / COUNTIF."""
    if isinstance(criteria, bool):
        return isinstance(cell_value, bool) and cell_value == criteria

    if isinstance(criteria, (int, float)):
        cell_num = _try_parse_numeric(cell_value) if not isinstance(cell_value, str) else None
        return cell_num is not None and math.isclose(
            cell_num, float(criteria), rel_tol=1e-9, abs_tol=1e-12
        )

    if criteria is None:
        return cell_value is None or cell_value == ""

    if not isinstance(criteria, str):
        return False

    op_match = _CRITERIA_OP_PATTERN.match(criteria)
    if op_match is not None:
        op = op_match.group(1)
        rhs_raw = op_match.group(2).strip()
        rhs_num = _try_parse_numeric(rhs_raw)
        if op in {">", ">=", "<", "<="}:
            if rhs_num is None:
                if not isinstance(cell_value, str):
                    return False
                cmp_str = _excel_compare(cell_value, rhs_raw)
            else:
                cell_num = (
                    _try_parse_numeric(cell_value) if not isinstance(cell_value, str) else None
                )
                if cell_num is None:
                    return False
                cmp_str = _excel_compare(cell_num, rhs_num)
            if op == ">":
                return cmp_str > 0
            if op == ">=":
                return cmp_str >= 0
            if op == "<":
                return cmp_str < 0
            return cmp_str <= 0

        # '=' або '<>' / '!='
        if rhs_raw == "":
            is_equal = cell_value is None or cell_value == ""
        elif rhs_num is not None:
            cell_num = _try_parse_numeric(cell_value) if not isinstance(cell_value, str) else None
            is_equal = (
                cell_num is not None
                and math.isclose(cell_num, rhs_num, rel_tol=1e-9, abs_tol=1e-12)
            ) or (
                isinstance(cell_value, str)
                and cell_value.strip().casefold() == rhs_raw.casefold()
            )
        else:
            is_equal = _matches_exact_lookup(cell_value, rhs_raw)
        return is_equal if op == "=" else not is_equal

    crit_num = _try_parse_numeric(criteria)
    if crit_num is not None:
        cell_num = _try_parse_numeric(cell_value) if not isinstance(cell_value, str) else None
        if cell_num is not None and math.isclose(
            cell_num, crit_num, rel_tol=1e-9, abs_tol=1e-12
        ):
            return True

    return _matches_exact_lookup(cell_value, criteria)


def _eval_countif(evaluated_args: list[object]) -> float:
    """Обчислює COUNTIF(range, criteria)."""
    if len(evaluated_args) != 2:
        raise _FormulaEvalError("COUNTIF expects exactly 2 arguments.")
    criteria_range = evaluated_args[0]
    criteria = evaluated_args[1]
    if not isinstance(criteria_range, _RangeValue):
        raise _FormulaEvalError("COUNTIF requires a range as first argument.")
    matched = 0
    for row in criteria_range.rows:
        for cell_val in row:
            if _matches_excel_criteria(cell_val, criteria):
                matched += 1
    return float(matched)


def _eval_sumif(evaluated_args: list[object]) -> float:
    """Обчислює SUMIF(criteria_range, criteria, [sum_range])."""
    if len(evaluated_args) not in {2, 3}:
        raise _FormulaEvalError("SUMIF expects 2 or 3 arguments.")
    criteria_range = evaluated_args[0]
    criteria = evaluated_args[1]
    sum_range = evaluated_args[2] if len(evaluated_args) == 3 else criteria_range
    if not isinstance(criteria_range, _RangeValue) or not isinstance(sum_range, _RangeValue):
        raise _FormulaEvalError("SUMIF requires range arguments.")

    total = 0.0
    for r_idx, row in enumerate(criteria_range.rows):
        for c_idx, cell_val in enumerate(row):
            if not _matches_excel_criteria(cell_val, criteria):
                continue
            if r_idx < len(sum_range.rows) and c_idx < len(sum_range.rows[r_idx]):
                target_val = sum_range.rows[r_idx][c_idx]
                if isinstance(target_val, bool) or target_val is None:
                    continue
                if isinstance(target_val, (int, float)):
                    fval = float(target_val)
                    if not (math.isnan(fval) or math.isinf(fval)):
                        total += fval
    return float(total)


def _normalize_bare_function_name(token: str) -> str | None:
    """Нормалізує окреме ім'я функції (включно з локалізованими та LOG10) або повертає None."""
    cleaned = token.strip().upper()
    if not cleaned:
        return None
    if cleaned in LOCALIZED_FUNCTION_ALIASES:
        return LOCALIZED_FUNCTION_ALIASES[cleaned]
    if _BARE_FUNCTION_NAME_PATTERN.match(cleaned) is not None:
        return cleaned
    return None


def _replace_localized_functions_in_segment(segment: str) -> str:
    """Замінює локалізовані назви функцій лише перед '(' поза текстовими літералами."""
    return _FUNC_CALL_NAME_PATTERN.sub(
        lambda m: LOCALIZED_FUNCTION_ALIASES.get(m.group(1), m.group(1)),
        segment,
    )


def _canonicalize_formula(formula: str, *, strip_dollar: bool) -> str:
    """Нормалізує формулу Excel: прибирає '=', пробіли поза лапками, ';' -> ',', локалізації."""
    cleaned = formula.strip()
    if cleaned.startswith("="):
        cleaned = cleaned[1:].strip()

    # Прибираємо зовнішні дужки навколо всієї формули, якщо вони огортають весь вираз: =(A1+B1)
    while cleaned.startswith("(") and cleaned.endswith(")") and _is_wrapped_in_parens(cleaned):
        cleaned = cleaned[1:-1].strip()

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
        seg_text = _replace_localized_functions_in_segment(seg_text)
        if strip_dollar:
            seg_text = _DOLLAR_CELL_REF_PATTERN.sub(
                lambda m: (
                    f"{m.group(1) or m.group(3) or m.group(5)}"
                    f"{m.group(2) or m.group(4) or m.group(6)}"
                ),
                seg_text,
            )
        out_parts.append(seg_text)

    return "".join(out_parts)


def _is_wrapped_in_parens(expr: str) -> bool:
    """Перевіряє, чи зовнішні дужки '(' та ')' огортають увесь вираз цілком."""
    if not (expr.startswith("(") and expr.endswith(")")):
        return False

    depth = 0
    in_quotes = False
    quote_char = '"'
    idx = 0
    length = len(expr)

    while idx < length:
        ch = expr[idx]
        if in_quotes:
            if ch == quote_char:
                if idx + 1 < length and expr[idx + 1] == quote_char:
                    idx += 2
                    continue
                in_quotes = False
            idx += 1
            continue
        if ch in {'"', "'"}:
            in_quotes = True
            quote_char = ch
            idx += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and idx < length - 1:
                return False
        idx += 1

    return depth == 0


def _try_parse_numeric(value: object) -> float | None:
    """Намагається інтерпретувати значення комірки як число float (виключаючи bool та NaN)."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        float_val = float(value)
        return None if math.isnan(float_val) or math.isinf(float_val) else float_val
    if isinstance(value, str):
        cleaned = value.strip().replace(" ", "").replace(",", ".")
        if not cleaned:
            return None
        try:
            float_val = float(cleaned)
            return None if math.isnan(float_val) or math.isinf(float_val) else float_val
        except ValueError:
            return None
    return None


def _format_cell_value(value: object) -> str | None:
    """Форматує значення комірки у детермінований людиночитабельний рядок."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return str(value)
        rounded_int = round(value)
        if math.isclose(value, float(rounded_int), abs_tol=1e-9):
            return str(rounded_int)
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)
