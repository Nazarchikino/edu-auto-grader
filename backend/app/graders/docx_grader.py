import math
import re
import zipfile
from pathlib import Path

import docx
from docx.document import Document as DocxDocument
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.exceptions import PackageNotFoundError
from docx.section import Section
from docx.styles.style import BaseStyle
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.graders.base import BaseGrader
from app.models.course import PracticalFormat
from app.schemas.grading import (
    CriterionResult,
    GradingReport,
    GradingRule,
    GradingRuleType,
)

_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_W_TAG_PPR = f"{{{_W_NS}}}pPr"
_W_TAG_RPR = f"{{{_W_NS}}}rPr"
_W_TAG_NUMPR = f"{{{_W_NS}}}numPr"
_W_TAG_NUMID = f"{{{_W_NS}}}numId"
_W_TAG_RFONTS = f"{{{_W_NS}}}rFonts"
_W_TAG_SZ = f"{{{_W_NS}}}sz"
_W_TAG_SPACING = f"{{{_W_NS}}}spacing"
_W_TAG_JC = f"{{{_W_NS}}}jc"
_W_TAG_DOC_DEFAULTS = f"{{{_W_NS}}}docDefaults"
_W_TAG_RPR_DEFAULT = f"{{{_W_NS}}}rPrDefault"
_W_TAG_PPR_DEFAULT = f"{{{_W_NS}}}pPrDefault"
_W_ATTR_VAL = f"{{{_W_NS}}}val"
_W_ATTR_ASCII = f"{{{_W_NS}}}ascii"
_W_ATTR_HANSI = f"{{{_W_NS}}}hAnsi"
_W_ATTR_CS = f"{{{_W_NS}}}cs"
_W_ATTR_LINE = f"{{{_W_NS}}}line"
_W_ATTR_LINE_RULE = f"{{{_W_NS}}}lineRule"

_MARGIN_KEYS: tuple[str, ...] = ("left", "right", "top", "bottom")
_MARGIN_TOLERANCE_MM = 0.5
_FONT_SIZE_TOLERANCE_PT = 0.25
_LINE_SPACING_TOLERANCE = 0.05
_BULLET_PREFIXES: tuple[str, ...] = ("•", "●", "○", "▪", "◦")

_SECTION_INDEX_PATTERN = re.compile(r"^(?:section_)?(\d+)$", re.IGNORECASE)
_PARAGRAPH_INDEX_PATTERN = re.compile(r"^(?:paragraph_|p_)(\d+)$", re.IGNORECASE)
_TABLE_TARGET_PATTERN = re.compile(
    r"^(?:table_(\d+)|document|table)(?:\.(rows|cols|columns))?$",
    re.IGNORECASE,
)

_ALIGNMENT_ENUM_TO_NAME: dict[WD_ALIGN_PARAGRAPH, str] = {
    WD_ALIGN_PARAGRAPH.LEFT: "LEFT",
    WD_ALIGN_PARAGRAPH.CENTER: "CENTER",
    WD_ALIGN_PARAGRAPH.RIGHT: "RIGHT",
    WD_ALIGN_PARAGRAPH.JUSTIFY: "JUSTIFY",
    WD_ALIGN_PARAGRAPH.DISTRIBUTE: "DISTRIBUTE",
}

_ALIGNMENT_ALIASES: dict[str, str] = {
    "LEFT": "LEFT",
    "CENTER": "CENTER",
    "RIGHT": "RIGHT",
    "JUSTIFY": "JUSTIFY",
    "BOTH": "JUSTIFY",
    "DISTRIBUTE": "DISTRIBUTE",
}


class DocxGrader(BaseGrader):
    """Стратегія детермінованої автоперевірки документів Microsoft Word (.docx)."""

    format_type: PracticalFormat = PracticalFormat.DOCX

    def evaluate(
        self,
        *,
        file_path: Path | None = None,
        raw_code: str | None = None,
        rules: list[GradingRule],
        variant_data: dict[str, object],
    ) -> GradingReport:
        """Виконує перевірку документа .docx за переліком правил."""
        resolved_path = self.require_file_path(file_path, expected_suffix=".docx")
        document = self._open_document(resolved_path)

        results: list[CriterionResult] = []
        for rule in rules:
            resolved_expected = self.resolve_expected(rule.expected, variant_data)
            result = self._evaluate_rule(document, rule, resolved_expected)
            results.append(result)

        return self.build_report(results)

    def _open_document(self, file_path: Path) -> DocxDocument:
        """Відкриває документ .docx та перетворює помилки формату на InvalidFileFormatError."""
        try:
            return docx.Document(str(file_path))
        except (
            PackageNotFoundError,
            zipfile.BadZipFile,
            KeyError,
            ValueError,
            OSError,
        ) as exc:
            raise InvalidFileFormatError(
                f"Не вдалося прочитати документ Word '{file_path.name}': "
                "файл пошкоджений або не є коректним пакетом OpenXML (.docx).",
                context={"file_name": file_path.name, "error": str(exc)},
            ) from exc

    def _evaluate_rule(
        self,
        document: DocxDocument,
        rule: GradingRule,
        expected: str,
    ) -> CriterionResult:
        """Маршрутизує перевірку окремого правила за його типом."""
        if rule.type == GradingRuleType.DOCX_PAGE_MARGINS:
            return self._evaluate_page_margins(document, rule, expected)
        if rule.type == GradingRuleType.DOCX_FONT:
            return self._evaluate_font(document, rule, expected)
        if rule.type == GradingRuleType.DOCX_LINE_SPACING:
            return self._evaluate_line_spacing(document, rule, expected)
        if rule.type == GradingRuleType.DOCX_ALIGNMENT:
            return self._evaluate_alignment(document, rule, expected)
        if rule.type == GradingRuleType.DOCX_TABLE_EXISTS:
            return self._evaluate_table_exists(document, rule, expected)
        if rule.type == GradingRuleType.DOCX_LIST_EXISTS:
            return self._evaluate_list_exists(document, rule, expected)

        raise GradingError(
            f"DocxGrader не підтримує правило типу '{rule.type.value}'.",
            context={"rule_id": rule.id, "rule_type": rule.type.value},
        )

    def _evaluate_page_margins(
        self,
        document: DocxDocument,
        rule: GradingRule,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє розміри полів сторінки (left, right, top, bottom) у міліметрах."""
        expected_margins = self._parse_expected_margins(expected)
        sections = self._select_sections(document, rule.target)

        if not sections:
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=f"Секцію сторінки '{rule.target}' не знайдено в документі.",
                resolved_expected=expected,
            )

        all_passed = True
        section_actuals: list[str] = []
        mismatches: list[str] = []

        for section in sections:
            actual_map = self._extract_section_margins_mm(section)
            formatted_parts: list[str] = []
            for side in expected_margins:
                actual_val = actual_map.get(side)
                expected_val = expected_margins[side]
                if actual_val is None:
                    all_passed = False
                    formatted_parts.append(f"{side}=None")
                    mismatches.append(
                        f"{side}: не задано (очікується {_format_number(expected_val)} мм)"
                    )
                else:
                    formatted_parts.append(f"{side}={_format_number(actual_val)}")
                    if abs(actual_val - expected_val) > _MARGIN_TOLERANCE_MM:
                        all_passed = False
                        mismatches.append(
                            f"{side}={_format_number(actual_val)} мм "
                            f"(очікується {_format_number(expected_val)} мм)"
                        )
            section_actuals.append(",".join(formatted_parts))

        actual_str = "; ".join(dict.fromkeys(section_actuals))
        if all_passed:
            feedback = f"Поля сторінки відповідають вимогам ({actual_str} мм)."
        else:
            feedback = "Невідповідність полів сторінки: " + ", ".join(mismatches) + "."

        return self.build_criterion_result(
            rule,
            passed=all_passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_font(
        self,
        document: DocxDocument,
        rule: GradingRule,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє гарнітуру (font name) та кегль (font size у пт) цільових абзаців."""
        expected_name, expected_size = self._parse_expected_font(expected)
        paragraphs = self._select_paragraphs(document, rule.target)

        if not paragraphs:
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=f"У документі не знайдено текстових абзаців для цілі '{rule.target}'.",
                resolved_expected=expected,
            )

        detected_pairs: list[str] = []
        all_passed = True

        for paragraph in paragraphs:
            p_fonts = self._resolve_paragraph_fonts(document, paragraph)
            for font_name, font_size in p_fonts:
                pair_label = self._format_font_pair(
                    font_name,
                    font_size,
                    include_name=expected_name is not None or expected_size is None,
                    include_size=expected_size is not None or expected_name is None,
                )
                if pair_label not in detected_pairs:
                    detected_pairs.append(pair_label)

                name_ok = True
                if expected_name is not None:
                    name_ok = (
                        font_name is not None
                        and font_name.strip().lower() == expected_name.strip().lower()
                    )

                size_ok = True
                if expected_size is not None:
                    size_ok = (
                        font_size is not None
                        and math.isclose(
                            font_size,
                            expected_size,
                            abs_tol=_FONT_SIZE_TOLERANCE_PT,
                        )
                    )

                if not (name_ok and size_ok):
                    all_passed = False

        actual_str = ", ".join(detected_pairs) if detected_pairs else None
        if all_passed:
            feedback = f"Шрифт відповідає вимогам ({actual_str})."
        else:
            feedback = (
                f"Виявлено невідповідність шрифту: фактично '{actual_str}', "
                f"очікується '{expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=all_passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_line_spacing(
        self,
        document: DocxDocument,
        rule: GradingRule,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє міжрядковий інтервал цільових абзаців документа."""
        paragraphs = self._select_paragraphs(document, rule.target)

        if not paragraphs:
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=f"У документі не знайдено текстових абзаців для цілі '{rule.target}'.",
                resolved_expected=expected,
            )

        detected_spacings: list[str] = []
        all_passed = True

        for paragraph in paragraphs:
            spacing = self._resolve_paragraph_line_spacing(document, paragraph)
            if spacing is None:
                all_passed = False
                if "None" not in detected_spacings:
                    detected_spacings.append("None")
                continue

            formatted = _format_number(spacing, precision=2)
            if formatted not in detected_spacings:
                detected_spacings.append(formatted)

            if not self.compare_numeric_condition(
                spacing,
                expected,
                tolerance=_LINE_SPACING_TOLERANCE,
            ):
                all_passed = False

        actual_str = ", ".join(detected_spacings) if detected_spacings else None
        if all_passed:
            feedback = f"Міжрядковий інтервал відповідає вимогам ({actual_str})."
        else:
            feedback = (
                f"Міжрядковий інтервал не відповідає вимогам: фактично '{actual_str}', "
                f"очікується '{expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=all_passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_alignment(
        self,
        document: DocxDocument,
        rule: GradingRule,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє вирівнювання цільових абзаців (LEFT, CENTER, RIGHT, JUSTIFY)."""
        expected_key = expected.strip().upper()
        normalized_expected = _ALIGNMENT_ALIASES.get(expected_key)
        if normalized_expected is None:
            raise GradingError(
                f"Невідомий тип вирівнювання абзацу у правилі: '{expected}'.",
                context={"rule_id": rule.id, "expected": expected},
            )

        paragraphs = self._select_paragraphs(document, rule.target)
        if not paragraphs:
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=f"У документі не знайдено текстових абзаців для цілі '{rule.target}'.",
                resolved_expected=expected,
            )

        detected_alignments: list[str] = []
        all_passed = True

        for paragraph in paragraphs:
            alignment_name = self._resolve_paragraph_alignment(document, paragraph)
            label = alignment_name if alignment_name is not None else "None"
            if label not in detected_alignments:
                detected_alignments.append(label)

            if alignment_name != normalized_expected:
                all_passed = False

        actual_str = ", ".join(detected_alignments) if detected_alignments else None
        if all_passed:
            feedback = f"Вирівнювання абзаців відповідає вимогам ({actual_str})."
        else:
            feedback = (
                f"Вирівнювання абзаців не відповідає вимогам: фактично '{actual_str}', "
                f"очікується '{normalized_expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=all_passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_table_exists(
        self,
        document: DocxDocument,
        rule: GradingRule,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє наявність, кількість або розмірність таблиць у документі."""
        tables = document.tables
        table_count = len(tables)
        target_clean = rule.target.strip()
        target_match = _TABLE_TARGET_PATTERN.match(target_clean)

        if target_match is not None and target_match.group(2) is not None:
            idx_group = target_match.group(1)
            table_idx = int(idx_group) if idx_group is not None else 0
            dimension = target_match.group(2).lower()

            if table_idx >= table_count:
                return self.build_criterion_result(
                    rule,
                    passed=False,
                    actual="0",
                    feedback=f"Таблицю з індексом {table_idx} не знайдено в документі.",
                    resolved_expected=expected,
                )

            target_table = tables[table_idx]
            dim_value = (
                len(target_table.rows)
                if dimension == "rows"
                else len(target_table.columns)
            )
            passed = self.compare_numeric_condition(dim_value, expected)
            dim_label = "рядків" if dimension == "rows" else "стовпців"
            feedback = (
                f"Кількість {dim_label} у таблиці ({dim_value}) відповідає умові '{expected}'."
                if passed
                else (
                    f"Кількість {dim_label} у таблиці ({dim_value}) "
                    f"не відповідає умові '{expected}'."
                )
            )
            return self.build_criterion_result(
                rule,
                passed=passed,
                actual=str(dim_value),
                feedback=feedback,
                resolved_expected=expected,
            )

        normalized_expected = expected.strip().lower()
        if normalized_expected in {"true", "false", "yes", "no"}:
            expected_bool = self.parse_bool_expected(expected)
            actual_bool = table_count > 0
            passed = actual_bool == expected_bool
            actual_str = "true" if actual_bool else "false"
        else:
            passed = self.compare_numeric_condition(table_count, expected)
            actual_str = str(table_count)

        if passed:
            feedback = f"Перевірку таблиць пройдено (знайдено таблиць: {table_count})."
        else:
            feedback = (
                f"Умову щодо таблиць не виконано: знайдено {table_count}, "
                f"очікується '{expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_list_exists(
        self,
        document: DocxDocument,
        rule: GradingRule,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє наявність маркованих або нумерованих списків у документі."""
        list_paragraphs = [
            p for p in document.paragraphs if p.text.strip() and self._is_list_paragraph(p)
        ]
        list_count = len(list_paragraphs)

        normalized_expected = expected.strip().lower()
        if normalized_expected in {"true", "false", "yes", "no"}:
            expected_bool = self.parse_bool_expected(expected)
            actual_bool = list_count > 0
            passed = actual_bool == expected_bool
            actual_str = "true" if actual_bool else "false"
        else:
            passed = self.compare_numeric_condition(list_count, expected)
            actual_str = str(list_count)

        if passed:
            feedback = (
                f"Перевірку списків пройдено (елементів списку в документі: {list_count})."
            )
        else:
            feedback = (
                f"Умову щодо наявності списку не виконано: знайдено елементів {list_count}, "
                f"очікується '{expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _select_sections(
        self,
        document: DocxDocument,
        target: str,
    ) -> list[Section]:
        """Вибирає секції документа відповідно до target ('section_0', '0', 'all', 'document')."""
        sections = list(document.sections)
        if not sections:
            return []

        cleaned = target.strip()
        match = _SECTION_INDEX_PATTERN.match(cleaned)
        if match is not None:
            index = int(match.group(1))
            if 0 <= index < len(sections):
                return [sections[index]]
            return []

        return sections

    def _select_paragraphs(
        self,
        document: DocxDocument,
        target: str,
    ) -> list[Paragraph]:
        """Вибирає непорожні абзаци документа за цільовим селектором ('body', 'document', 'p_0')."""
        all_paragraphs = list(document.paragraphs)
        non_empty = [p for p in all_paragraphs if p.text.strip()]
        cleaned = target.strip()
        cleaned_lower = cleaned.lower()

        idx_match = _PARAGRAPH_INDEX_PATTERN.match(cleaned)
        if idx_match is not None:
            index = int(idx_match.group(1))
            if 0 <= index < len(non_empty):
                return [non_empty[index]]
            if 0 <= index < len(all_paragraphs) and all_paragraphs[index].text.strip():
                return [all_paragraphs[index]]
            return []

        if cleaned_lower.startswith("style:"):
            style_target = cleaned[6:].strip().lower()
            return [
                p
                for p in non_empty
                if p.style is not None
                and p.style.name is not None
                and p.style.name.lower() == style_target
            ]

        if cleaned_lower in {"heading", "headings"}:
            return [p for p in non_empty if self._is_heading_paragraph(p)]

        if cleaned_lower.startswith("heading"):
            suffix = cleaned_lower.removeprefix("heading").lstrip("_ ").strip()
            selected: list[Paragraph] = []
            for p in non_empty:
                style_name = (p.style.name if p.style and p.style.name else "").lower()
                if not suffix:
                    if style_name.startswith(("heading", "заголовок")):
                        selected.append(p)
                elif style_name in {f"heading {suffix}", f"заголовок {suffix}"}:
                    selected.append(p)
            return selected

        if cleaned_lower == "body":
            body_paragraphs = [
                p
                for p in non_empty
                if not self._is_heading_paragraph(p)
            ]
            return body_paragraphs if body_paragraphs else non_empty

        return non_empty

    def _is_heading_paragraph(self, paragraph: Paragraph) -> bool:
        """Визначає, чи належить абзац до заголовків документа."""
        style_name = (
            paragraph.style.name.lower()
            if paragraph.style is not None and paragraph.style.name is not None
            else ""
        )
        return style_name.startswith(("heading", "заголовок", "title", "subtitle"))

    def _parse_expected_margins(self, expected: str) -> dict[str, float]:
        """Розбирає рядок очікуваних полів вигляду 'left=30,right=15,top=20,bottom=20' у мм."""
        raw_tokens = [token.strip() for token in re.split(r"[,;]", expected) if token.strip()]
        if not raw_tokens:
            raise GradingError(
                "Порожній вираз очікуваних полів сторінки у правилі.",
                context={"expected": expected},
            )

        parsed: dict[str, float] = {}
        if all("=" not in token for token in raw_tokens) and len(raw_tokens) == 4:
            for side, token in zip(_MARGIN_KEYS, raw_tokens, strict=True):
                parsed[side] = self._parse_margin_value_mm(token, expected)
            return parsed

        if len(raw_tokens) == 1 and "=" not in raw_tokens[0]:
            single_token = raw_tokens[0]
            cleaned_single = single_token.strip().lower()
            has_explicit_unit = cleaned_single.endswith(("mm", "cm"))
            margin_mm = self._parse_margin_value_mm(single_token, expected)
            if not has_explicit_unit and margin_mm <= 5.0:
                margin_mm *= 10.0
            return {side: margin_mm for side in _MARGIN_KEYS}

        for token in raw_tokens:
            if "=" not in token:
                raise GradingError(
                    f"Некоректний формат поля сторінки '{token}' у виразі '{expected}'.",
                    context={"expected": expected, "token": token},
                )
            key_raw, val_raw = token.split("=", maxsplit=1)
            side = key_raw.strip().lower()
            if side not in _MARGIN_KEYS:
                raise GradingError(
                    f"Невідома назва поля сторінки '{side}'. Дозволені: left, right, top, bottom.",
                    context={"expected": expected, "side": side},
                )
            parsed[side] = self._parse_margin_value_mm(val_raw, expected)

        return parsed

    def _parse_margin_value_mm(self, raw_value: str, full_expected: str) -> float:
        """Перетворює текстове значення поля ('30', '30mm', '3cm') на число в міліметрах."""
        cleaned = raw_value.strip().lower()
        multiplier = 1.0
        if cleaned.endswith("mm"):
            cleaned = cleaned[:-2].strip()
        elif cleaned.endswith("cm"):
            cleaned = cleaned[:-2].strip()
            multiplier = 10.0

        try:
            value = float(cleaned.replace(",", ".")) * multiplier
        except ValueError as exc:
            raise GradingError(
                f"Некоректне числове значення поля сторінки '{raw_value}' у '{full_expected}'.",
                context={"expected": full_expected, "value": raw_value},
            ) from exc

        return value

    def _extract_section_margins_mm(self, section: Section) -> dict[str, float | None]:
        """Зчитує поля секції сторінки в міліметрах."""
        return {
            "left": float(section.left_margin.mm) if section.left_margin is not None else None,
            "right": float(section.right_margin.mm) if section.right_margin is not None else None,
            "top": float(section.top_margin.mm) if section.top_margin is not None else None,
            "bottom": (
                float(section.bottom_margin.mm) if section.bottom_margin is not None else None
            ),
        }

    def _parse_expected_font(self, expected: str) -> tuple[str | None, float | None]:
        """Розбирає очікуваний шрифт вигляду 'Times New Roman:14' або 'name=Arial,size=12'."""
        cleaned = expected.strip()
        if not cleaned:
            raise GradingError(
                "Порожній вираз очікуваного шрифту у правилі.",
                context={"expected": expected},
            )

        if "=" in cleaned:
            font_name: str | None = None
            font_size: float | None = None
            for part in re.split(r"[,;]", cleaned):
                if "=" not in part:
                    continue
                k, v = part.split("=", maxsplit=1)
                key = k.strip().lower()
                val = v.strip()
                if key in {"name", "font", "family"} and val:
                    font_name = val
                elif key in {"size", "pt"} and val:
                    font_size = self._parse_font_size_pt(val, expected)
            if font_name is None and font_size is None:
                raise GradingError(
                    f"Не вдалося розпізнати параметри шрифту у виразі '{expected}'.",
                    context={"expected": expected},
                )
            return font_name, font_size

        if ":" in cleaned:
            name_part, size_part = cleaned.rsplit(":", maxsplit=1)
            resolved_name = name_part.strip() or None
            resolved_size = (
                self._parse_font_size_pt(size_part, expected) if size_part.strip() else None
            )
            if resolved_name is None and resolved_size is None:
                raise GradingError(
                    f"Некоректний вираз очікуваного шрифту: '{expected}'.",
                    context={"expected": expected},
                )
            return resolved_name, resolved_size

        return cleaned, None

    def _parse_font_size_pt(self, raw_size: str, full_expected: str) -> float:
        """Перетворює рядок розміру шрифту ('14', '14pt', '14.0') на float у пунктах."""
        cleaned = raw_size.strip().lower()
        if cleaned.endswith(("pt", "пт")):
            cleaned = cleaned[:-2].strip()
        try:
            return float(cleaned.replace(",", "."))
        except ValueError as exc:
            raise GradingError(
                f"Некоректний розмір шрифту '{raw_size}' у правилі '{full_expected}'.",
                context={"expected": full_expected, "size": raw_size},
            ) from exc

    def _resolve_paragraph_fonts(
        self,
        document: DocxDocument,
        paragraph: Paragraph,
    ) -> list[tuple[str | None, float | None]]:
        """Визначає ефективні (name, size_pt) для всіх непорожніх текстових фрагментів абзацу."""
        non_empty_runs = [run for run in paragraph.runs if run.text.strip()]
        fallback_name, fallback_size = self._resolve_paragraph_level_font(document, paragraph)

        if not non_empty_runs:
            return [(fallback_name, fallback_size)]

        results: list[tuple[str | None, float | None]] = []
        for run in non_empty_runs:
            run_name, run_size = self._resolve_run_font(run)
            effective_name = run_name if run_name is not None else fallback_name
            effective_size = run_size if run_size is not None else fallback_size
            pair = (effective_name, effective_size)
            if pair not in results:
                results.append(pair)

        return results

    def _resolve_run_font(self, run: Run) -> tuple[str | None, float | None]:
        """Витягує ім'я та розмір шрифту безпосередньо з Run та його стилю."""
        name: str | None = run.font.name
        size_pt: float | None = float(run.font.size.pt) if run.font.size is not None else None

        if name is None or size_pt is None:
            xml_name, xml_size = self._extract_rpr_font(run._element.find(_W_TAG_RPR))
            if name is None:
                name = xml_name
            if size_pt is None:
                size_pt = xml_size

        if (name is None or size_pt is None) and run.style is not None:
            style_name, style_size = self._resolve_style_chain_font(run.style)
            if name is None:
                name = style_name
            if size_pt is None:
                size_pt = style_size

        return name, size_pt

    def _resolve_paragraph_level_font(
        self,
        document: DocxDocument,
        paragraph: Paragraph,
    ) -> tuple[str | None, float | None]:
        """Визначає шрифт на рівні абзацу, ланцюжка його стилів, Normal та docDefaults."""
        name: str | None = None
        size_pt: float | None = None

        ppr = paragraph._element.find(_W_TAG_PPR)
        if ppr is not None:
            name, size_pt = self._extract_rpr_font(ppr.find(_W_TAG_RPR))

        if (name is None or size_pt is None) and paragraph.style is not None:
            style_name, style_size = self._resolve_style_chain_font(paragraph.style)
            if name is None:
                name = style_name
            if size_pt is None:
                size_pt = style_size

        if name is None or size_pt is None:
            try:
                normal_style = document.styles["Normal"]
            except KeyError:
                normal_style = None
            if normal_style is not None:
                norm_name, norm_size = self._resolve_style_chain_font(normal_style)
                if name is None:
                    name = norm_name
                if size_pt is None:
                    size_pt = norm_size

        if name is None or size_pt is None:
            def_name, def_size = self._extract_doc_defaults_font(document)
            if name is None:
                name = def_name
            if size_pt is None:
                size_pt = def_size

        return name, size_pt

    def _resolve_style_chain_font(
        self,
        style: BaseStyle,
    ) -> tuple[str | None, float | None]:
        """Проходить ланцюжок base_style для пошуку успадкованої гарнітури та кегля."""
        name: str | None = None
        size_pt: float | None = None
        current: BaseStyle | None = style
        visited: set[str] = set()

        while current is not None:
            style_id = str(getattr(current, "style_id", id(current)))
            if style_id in visited:
                break
            visited.add(style_id)

            font = getattr(current, "font", None)
            if font is not None:
                if name is None and font.name is not None:
                    name = str(font.name)
                if size_pt is None and font.size is not None:
                    size_pt = float(font.size.pt)

            element = getattr(current, "_element", None)
            if element is not None and (name is None or size_pt is None):
                xml_name, xml_size = self._extract_rpr_font(element.find(_W_TAG_RPR))
                if name is None:
                    name = xml_name
                if size_pt is None:
                    size_pt = xml_size

            if name is not None and size_pt is not None:
                break

            base = getattr(current, "base_style", None)
            current = base if isinstance(base, BaseStyle) else None

        return name, size_pt

    def _extract_doc_defaults_font(
        self,
        document: DocxDocument,
    ) -> tuple[str | None, float | None]:
        """Зчитує глобальний шрифт за замовчуванням із секції w:docDefaults у styles.xml."""
        styles_element = document.styles.element
        doc_defaults = styles_element.find(_W_TAG_DOC_DEFAULTS)
        if doc_defaults is None:
            return None, None
        rpr_default = doc_defaults.find(_W_TAG_RPR_DEFAULT)
        if rpr_default is None:
            return None, None
        return self._extract_rpr_font(rpr_default.find(_W_TAG_RPR))

    def _extract_rpr_font(
        self,
        rpr_element: object,
    ) -> tuple[str | None, float | None]:
        """Витягує назву шрифту (w:rFonts) та розмір у пунктах (w:sz / 2) з XML-вузла w:rPr."""
        if rpr_element is None or not hasattr(rpr_element, "find"):
            return None, None

        name: str | None = None
        size_pt: float | None = None

        rfonts = rpr_element.find(_W_TAG_RFONTS)
        if rfonts is not None and hasattr(rfonts, "get"):
            for attr in (_W_ATTR_ASCII, _W_ATTR_HANSI, _W_ATTR_CS):
                candidate = rfonts.get(attr)
                if isinstance(candidate, str) and candidate.strip():
                    name = candidate.strip()
                    break

        sz = rpr_element.find(_W_TAG_SZ)
        if sz is not None and hasattr(sz, "get"):
            raw_half_points = sz.get(_W_ATTR_VAL)
            if isinstance(raw_half_points, str):
                try:
                    size_pt = float(raw_half_points) / 2.0
                except ValueError:
                    size_pt = None

        return name, size_pt

    def _format_font_pair(
        self,
        font_name: str | None,
        font_size: float | None,
        *,
        include_name: bool,
        include_size: bool,
    ) -> str:
        """Форматує знайдену пару гарнітури та кегля для звіту ('Times New Roman:14')."""
        name_str = font_name if font_name is not None else "None"
        size_str = _format_number(font_size) if font_size is not None else "None"
        if include_name and include_size:
            return f"{name_str}:{size_str}"
        if include_name:
            return name_str
        return size_str

    def _resolve_paragraph_line_spacing(
        self,
        document: DocxDocument,
        paragraph: Paragraph,
    ) -> float | None:
        """Визначає міжрядковий інтервал абзацу (множник рядків, напр. 1.5)."""
        direct = self._extract_line_spacing_value(
            paragraph.paragraph_format.line_spacing,
            paragraph._element.find(_W_TAG_PPR),
        )
        if direct is not None:
            return direct

        current: BaseStyle | None = paragraph.style
        visited: set[str] = set()
        while current is not None:
            style_id = str(getattr(current, "style_id", id(current)))
            if style_id in visited:
                break
            visited.add(style_id)

            pf = getattr(current, "paragraph_format", None)
            el = getattr(current, "_element", None)
            ppr = el.find(_W_TAG_PPR) if el is not None and hasattr(el, "find") else None
            spacing = self._extract_line_spacing_value(
                getattr(pf, "line_spacing", None) if pf is not None else None,
                ppr,
            )
            if spacing is not None:
                return spacing

            base = getattr(current, "base_style", None)
            current = base if isinstance(base, BaseStyle) else None

        try:
            normal_style = document.styles["Normal"]
        except KeyError:
            normal_style = None
        if normal_style is not None:
            pf = getattr(normal_style, "paragraph_format", None)
            el = getattr(normal_style, "_element", None)
            ppr = el.find(_W_TAG_PPR) if el is not None and hasattr(el, "find") else None
            spacing = self._extract_line_spacing_value(
                getattr(pf, "line_spacing", None) if pf is not None else None,
                ppr,
            )
            if spacing is not None:
                return spacing

        styles_element = document.styles.element
        doc_defaults = styles_element.find(_W_TAG_DOC_DEFAULTS)
        if doc_defaults is not None:
            ppr_default = doc_defaults.find(_W_TAG_PPR_DEFAULT)
            if ppr_default is not None:
                return self._extract_line_spacing_value(None, ppr_default.find(_W_TAG_PPR))

        return None

    def _extract_line_spacing_value(
        self,
        pf_line_spacing: float | int | None,
        ppr_element: object,
    ) -> float | None:
        """Конвертує значення line_spacing із ParagraphFormat або w:spacing у множник."""
        if isinstance(pf_line_spacing, float):
            return pf_line_spacing
        if (
            isinstance(pf_line_spacing, int)
            and not isinstance(pf_line_spacing, bool)
            and pf_line_spacing <= 10
        ):
            return float(pf_line_spacing)

        if ppr_element is not None and hasattr(ppr_element, "find"):
            spacing_el = ppr_element.find(_W_TAG_SPACING)
            if spacing_el is not None and hasattr(spacing_el, "get"):
                raw_line = spacing_el.get(_W_ATTR_LINE)
                line_rule = spacing_el.get(_W_ATTR_LINE_RULE)
                if isinstance(raw_line, str) and (line_rule is None or line_rule == "auto"):
                    try:
                        return float(raw_line) / 240.0
                    except ValueError:
                        return None

        return None

    def _resolve_paragraph_alignment(
        self,
        document: DocxDocument,
        paragraph: Paragraph,
    ) -> str | None:
        """Визначає канонічну назву вирівнювання абзацу ('LEFT', 'CENTER', 'RIGHT', 'JUSTIFY')."""
        direct = self._extract_alignment_name(
            paragraph.alignment or paragraph.paragraph_format.alignment,
            paragraph._element.find(_W_TAG_PPR),
        )
        if direct is not None:
            return direct

        current: BaseStyle | None = paragraph.style
        visited: set[str] = set()
        while current is not None:
            style_id = str(getattr(current, "style_id", id(current)))
            if style_id in visited:
                break
            visited.add(style_id)

            pf = getattr(current, "paragraph_format", None)
            el = getattr(current, "_element", None)
            ppr = el.find(_W_TAG_PPR) if el is not None and hasattr(el, "find") else None
            aligned = self._extract_alignment_name(
                getattr(pf, "alignment", None) if pf is not None else None,
                ppr,
            )
            if aligned is not None:
                return aligned

            base = getattr(current, "base_style", None)
            current = base if isinstance(base, BaseStyle) else None

        try:
            normal_style = document.styles["Normal"]
        except KeyError:
            normal_style = None
        if normal_style is not None:
            pf = getattr(normal_style, "paragraph_format", None)
            el = getattr(normal_style, "_element", None)
            ppr = el.find(_W_TAG_PPR) if el is not None and hasattr(el, "find") else None
            aligned = self._extract_alignment_name(
                getattr(pf, "alignment", None) if pf is not None else None,
                ppr,
            )
            if aligned is not None:
                return aligned

        return None

    def _extract_alignment_name(
        self,
        alignment_enum: WD_ALIGN_PARAGRAPH | None,
        ppr_element: object,
    ) -> str | None:
        """Перетворює WD_ALIGN_PARAGRAPH або XML-тег w:jc на канонічний рядок."""
        if alignment_enum is not None and alignment_enum in _ALIGNMENT_ENUM_TO_NAME:
            return _ALIGNMENT_ENUM_TO_NAME[alignment_enum]

        if ppr_element is not None and hasattr(ppr_element, "find"):
            jc_el = ppr_element.find(_W_TAG_JC)
            if jc_el is not None and hasattr(jc_el, "get"):
                raw_val = jc_el.get(_W_ATTR_VAL)
                if isinstance(raw_val, str):
                    return _ALIGNMENT_ALIASES.get(raw_val.strip().upper())

        return None

    def _is_list_paragraph(self, paragraph: Paragraph) -> bool:
        """Перевіряє, чи є абзац елементом списку (w:numPr, стиль списку або маркер)."""
        if self._has_xml_numbering(paragraph._element.find(_W_TAG_PPR)):
            return True

        current: BaseStyle | None = paragraph.style
        visited: set[str] = set()
        while current is not None:
            style_id = str(getattr(current, "style_id", id(current)))
            if style_id in visited:
                break
            visited.add(style_id)

            style_name = (current.name or "").lower()
            if "list" in style_name or "список" in style_name:
                return True

            el = getattr(current, "_element", None)
            ppr = el.find(_W_TAG_PPR) if el is not None and hasattr(el, "find") else None
            if self._has_xml_numbering(ppr):
                return True

            base = getattr(current, "base_style", None)
            current = base if isinstance(base, BaseStyle) else None

        stripped = paragraph.text.lstrip()
        return stripped.startswith(_BULLET_PREFIXES)

    def _has_xml_numbering(self, ppr_element: object) -> bool:
        """Перевіряє наявність активного вузла w:numPr (numId != '0') у властивостях абзацу."""
        if ppr_element is None or not hasattr(ppr_element, "find"):
            return False

        num_pr = ppr_element.find(_W_TAG_NUMPR)
        if num_pr is None:
            return False

        if hasattr(num_pr, "find"):
            num_id_el = num_pr.find(_W_TAG_NUMID)
            if num_id_el is not None and hasattr(num_id_el, "get"):
                val = num_id_el.get(_W_ATTR_VAL)
                if isinstance(val, str):
                    return val.strip() != "0"

        return True


def _format_number(value: float, *, precision: int = 1) -> str:
    """Форматує число з плаваючою комою без зайвого '.0' для цілих значень."""
    rounded_int = round(value)
    if math.isclose(value, float(rounded_int), abs_tol=0.05):
        return str(rounded_int)
    formatted = f"{value:.{precision}f}".rstrip("0").rstrip(".")
    return formatted
