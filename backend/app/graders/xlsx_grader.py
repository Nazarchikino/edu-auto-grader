import math
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import openpyxl  # type: ignore[import-untyped]
from openpyxl.cell.cell import Cell  # type: ignore[import-untyped]
from openpyxl.utils.cell import (  # type: ignore[import-untyped]
    column_index_from_string,
    get_column_letter,
)
from openpyxl.utils.exceptions import InvalidFileException  # type: ignore[import-untyped]
from openpyxl.workbook.workbook import Workbook  # type: ignore[import-untyped]
from openpyxl.worksheet.worksheet import Worksheet  # type: ignore[import-untyped]

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.graders.base import BaseGrader
from app.models.course import PracticalFormat
from app.schemas.grading import (
    CriterionResult,
    GradingReport,
    GradingRule,
    GradingRuleType,
)

_CELL_COORD_PATTERN = re.compile(r"^\$?([A-Za-z]{1,3})\$?([1-9]\d*)$")
_CELL_RANGE_PATTERN = re.compile(
    r"^\$?([A-Za-z]{1,3})\$?([1-9]\d*):\$?([A-Za-z]{1,3})\$?([1-9]\d*)$"
)
_RANGE_FUNC_PATTERN = re.compile(
    r"^(SUM|AVERAGE|MIN|MAX|COUNT)\(([^()]+)\)$",
    re.IGNORECASE,
)
_BINARY_ARITH_PATTERN = re.compile(
    r"^(\$?[A-Za-z]{1,3}\$?[1-9]\d*|[+-]?\d+(?:\.\d+)?)\s*([+\-*/])\s*"
    r"(\$?[A-Za-z]{1,3}\$?[1-9]\d*|[+-]?\d+(?:\.\d+)?)$"
)
_SHEET_INDEX_PATTERN = re.compile(r"^(?:sheet_)?(\d+)$", re.IGNORECASE)
_CHART_TARGET_SUFFIX_PATTERN = re.compile(
    r"^(.*?)(?:\.(count|type))?$",
    re.IGNORECASE,
)
_NUMERIC_CONDITION_CHECK_PATTERN = re.compile(
    r"^\s*(>=|<=|!=|==|>|<|=)?\s*([+-]?\d+(?:[.,]\d+)?)\s*$"
)
_BARE_FUNCTION_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z_.]*$")
_DOLLAR_CELL_REF_PATTERN = re.compile(
    r"\$([A-Za-z]{1,3})\$([1-9]\d*)|\$([A-Za-z]{1,3})([1-9]\d*)|([A-Za-z]{1,3})\$([1-9]\d*)"
)

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
        formula_wb, value_wb = self._open_workbooks(resolved_path)

        try:
            results: list[CriterionResult] = []
            for rule in rules:
                resolved_expected = self.resolve_expected(rule.expected, variant_data)
                resolved_target = self.resolve_expected(rule.target, variant_data)
                result = self._evaluate_rule(
                    formula_wb=formula_wb,
                    value_wb=value_wb,
                    rule=rule,
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
        depth: int = 0,
    ) -> object:
        """Повертає кешоване значення з data_only=True або детерміновано обчислює базову формулу."""
        cell = self._get_cell(value_sheet, coord)
        raw_value: object = cell.value if cell is not None else None
        if raw_value is not None or formula_sheet is None or depth > 3:
            return raw_value

        formula_cell = self._get_cell(formula_sheet, coord)
        formula_text = self._extract_formula_text(formula_cell)
        if formula_text is None:
            return None

        return self._evaluate_fallback_formula(
            formula_text=formula_text,
            value_sheet=value_sheet,
            formula_sheet=formula_sheet,
            depth=depth + 1,
        )

    def _evaluate_fallback_formula(
        self,
        *,
        formula_text: str,
        value_sheet: Worksheet,
        formula_sheet: Worksheet,
        depth: int,
    ) -> float | None:
        """Обчислює базові статистичні функції (SUM/AVERAGE/MIN/MAX/COUNT) та арифметику комірок."""
        canonical = _canonicalize_formula(formula_text, strip_dollar=True)

        func_match = _RANGE_FUNC_PATTERN.match(canonical)
        if func_match is not None:
            func_name = func_match.group(1).upper()
            args_str = func_match.group(2)
            values = self._collect_formula_argument_numbers(
                args_str=args_str,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                depth=depth,
            )
            if not values:
                return None
            if func_name == "SUM":
                return float(sum(values))
            if func_name == "AVERAGE":
                return float(sum(values) / len(values))
            if func_name == "MIN":
                return float(min(values))
            if func_name == "MAX":
                return float(max(values))
            if func_name == "COUNT":
                return float(len(values))

        arith_match = _BINARY_ARITH_PATTERN.match(canonical)
        if arith_match is not None:
            left_num = self._resolve_operand_number(
                token=arith_match.group(1),
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                depth=depth,
            )
            op = arith_match.group(2)
            right_num = self._resolve_operand_number(
                token=arith_match.group(3),
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                depth=depth,
            )
            if left_num is None or right_num is None:
                return None
            if op == "+":
                return left_num + right_num
            if op == "-":
                return left_num - right_num
            if op == "*":
                return left_num * right_num
            if op == "/":
                return None if math.isclose(right_num, 0.0) else left_num / right_num

        return None

    def _collect_formula_argument_numbers(
        self,
        *,
        args_str: str,
        value_sheet: Worksheet,
        formula_sheet: Worksheet,
        depth: int,
    ) -> list[float]:
        """Збирає числові значення з переліку аргументів функції (діапазонів або комірок)."""
        numbers: list[float] = []
        for raw_arg in args_str.split(","):
            arg = raw_arg.strip()
            if not arg:
                continue

            range_match = _CELL_RANGE_PATTERN.match(arg)
            if range_match is not None:
                start_col = int(column_index_from_string(range_match.group(1).upper()))
                start_row = int(range_match.group(2))
                end_col = int(column_index_from_string(range_match.group(3).upper()))
                end_row = int(range_match.group(4))

                col_lo, col_hi = min(start_col, end_col), max(start_col, end_col)
                row_lo, row_hi = min(start_row, end_row), max(start_row, end_row)

                for r_idx in range(row_lo, row_hi + 1):
                    for c_idx in range(col_lo, col_hi + 1):
                        col_letter = str(get_column_letter(c_idx))
                        cell_val = self._resolve_cell_evaluated_value(
                            value_sheet=value_sheet,
                            formula_sheet=formula_sheet,
                            coord=f"{col_letter}{r_idx}",
                            depth=depth,
                        )
                        num = _try_parse_numeric(cell_val)
                        if num is not None:
                            numbers.append(num)
                continue

            operand_num = self._resolve_operand_number(
                token=arg,
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                depth=depth,
            )
            if operand_num is not None:
                numbers.append(operand_num)

        return numbers

    def _resolve_operand_number(
        self,
        *,
        token: str,
        value_sheet: Worksheet,
        formula_sheet: Worksheet,
        depth: int,
    ) -> float | None:
        """Обчислює числовий операнд (літерал або посилання на комірку)."""
        coord_match = _CELL_COORD_PATTERN.match(token)
        if coord_match is not None:
            coord = f"{coord_match.group(1).upper()}{coord_match.group(2)}"
            val = self._resolve_cell_evaluated_value(
                value_sheet=value_sheet,
                formula_sheet=formula_sheet,
                coord=coord,
                depth=depth,
            )
            return _try_parse_numeric(val)
        return _try_parse_numeric(token)

    def _matches_expected_formula(
        self,
        actual_formula: str,
        expected_expr: str,
    ) -> bool:
        """Детерміновано порівнює фактичну формулу комірки з очікуваним виразом правила."""
        expected_clean = expected_expr.strip()
        expected_lower = expected_clean.lower()

        if expected_lower in {"any", "true", "exists", "not_null"}:
            return True

        canonical_actual = _canonicalize_formula(actual_formula, strip_dollar=False)
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
                if _BARE_FUNCTION_NAME_PATTERN.match(canonical_token) is not None:
                    return (
                        re.search(
                            rf"\b{re.escape(canonical_token)}\(",
                            target_formula,
                        )
                        is not None
                    )
                return canonical_token in target_formula

        # Якщо очікуване значення — лише ім'я функції без дужок та цифр (напр. 'SUM', 'AVERAGE')
        stripped_expected = expected_clean.lstrip("=").strip()
        if _BARE_FUNCTION_NAME_PATTERN.match(stripped_expected) is not None:
            func_name = stripped_expected.upper()
            if canonical_actual == func_name:
                return True
            return (
                re.search(rf"\b{re.escape(func_name)}\(", canonical_actual) is not None
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


def _canonicalize_formula(formula: str, *, strip_dollar: bool) -> str:
    """Нормалізує формулу Excel: прибирає '=', пробіли поза лапками, ';' -> ',' та регістр."""
    cleaned = formula.strip()
    if cleaned.startswith("="):
        cleaned = cleaned[1:].strip()

    # Прибираємо зовнішні дужки навколо всієї формули, якщо вони огортають весь вираз: =(A1+B1)
    while cleaned.startswith("(") and cleaned.endswith(")") and _is_wrapped_in_parens(cleaned):
        cleaned = cleaned[1:-1].strip()

    out_chars: list[str] = []
    in_quotes = False
    quote_char = '"'

    for ch in cleaned:
        if in_quotes:
            out_chars.append(ch)
            if ch == quote_char:
                in_quotes = False
            continue

        if ch in {'"', "'"}:
            in_quotes = True
            quote_char = ch
            out_chars.append(ch)
            continue

        if ch.isspace():
            continue

        if ch == ";":
            out_chars.append(",")
            continue

        out_chars.append(ch.upper())

    canonical = "".join(out_chars)
    if strip_dollar:
        canonical = _DOLLAR_CELL_REF_PATTERN.sub(
            lambda m: (
                f"{m.group(1) or m.group(3) or m.group(5)}"
                f"{m.group(2) or m.group(4) or m.group(6)}"
            ),
            canonical,
        )
    return canonical


def _is_wrapped_in_parens(expr: str) -> bool:
    """Перевіряє, чи зовнішні дужки '(' та ')' огортають увесь вираз цілком."""
    if not (expr.startswith("(") and expr.endswith(")")):
        return False

    depth = 0
    in_quotes = False
    quote_char = '"'

    for idx, ch in enumerate(expr):
        if in_quotes:
            if ch == quote_char:
                in_quotes = False
            continue
        if ch in {'"', "'"}:
            in_quotes = True
            quote_char = ch
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and idx < len(expr) - 1:
                return False

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
