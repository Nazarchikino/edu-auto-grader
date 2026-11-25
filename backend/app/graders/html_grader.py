import re
from pathlib import Path

from bs4 import BeautifulSoup, FeatureNotFound
from bs4.element import (
    Comment,
    Declaration,
    Doctype,
    NavigableString,
    ProcessingInstruction,
    Tag,
)

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.graders.base import BaseGrader
from app.models.course import PracticalFormat
from app.schemas.grading import (
    CriterionResult,
    GradingReport,
    GradingRule,
    GradingRuleType,
)

EMPTY_HTML_BODY_ERROR_MESSAGE: str = (
    "Тіло HTML-документа (<body>) порожнє. Додайте власну розмітку перед здачею."
)

_NON_CONTENT_STRING_TYPES = (
    Comment,
    Declaration,
    Doctype,
    ProcessingInstruction,
)
_DOCUMENT_SHELL_TAGS: frozenset[str] = frozenset(
    {"html", "head", "meta", "title", "link", "style", "base"}
)

_NUMERIC_CONDITION_CHECK_PATTERN = re.compile(
    r"^\s*(>=|<=|!=|==|>|<|=)?\s*([+-]?\d+(?:[.,]\d+)?)\s*$"
)
_BARE_TAG_CLOSURE_PATTERN = re.compile(r"^<\s*([a-zA-Z][a-zA-Z0-9:-]*)\s*/?\s*>$")
_ATTR_BRACKET_END_PATTERN = re.compile(
    r"^(.*?)\[\s*([a-zA-Z_:][a-zA-Z0-9_.:-]*)\s*(?:([~|^$*]?=)\s*(['\"]?)(.*?)\4\s*)?\]\s*$"
)
_TABLE_DIRECT_TR_PATTERN = re.compile(r"\btable\s*>\s*tr\b", re.IGNORECASE)

_KNOWN_HTML_ATTRIBUTES: frozenset[str] = frozenset(
    {
        "action",
        "alt",
        "aria-label",
        "autocomplete",
        "autofocus",
        "charset",
        "checked",
        "class",
        "cols",
        "colspan",
        "content",
        "controls",
        "data",
        "datetime",
        "dir",
        "disabled",
        "download",
        "enctype",
        "for",
        "form",
        "headers",
        "height",
        "hidden",
        "href",
        "http-equiv",
        "id",
        "lang",
        "list",
        "loop",
        "max",
        "maxlength",
        "method",
        "min",
        "minlength",
        "multiple",
        "muted",
        "name",
        "novalidate",
        "pattern",
        "placeholder",
        "poster",
        "preload",
        "readonly",
        "rel",
        "required",
        "role",
        "rows",
        "rowspan",
        "scope",
        "selected",
        "size",
        "src",
        "step",
        "style",
        "tabindex",
        "target",
        "title",
        "type",
        "value",
        "width",
    }
)


def parse_html_document(html_source: str) -> BeautifulSoup:
    """Парсить HTML-рядок у DOM-дерево BeautifulSoup через lxml (або html.parser)."""
    try:
        return BeautifulSoup(html_source, "lxml")
    except FeatureNotFound:
        return BeautifulSoup(html_source, "html.parser")
    except Exception as exc:
        raise InvalidFileFormatError(
            "Не вдалося побудувати DOM-дерево з переданого HTML-коду.",
            context={"error": str(exc)},
        ) from exc


def _node_has_visible_content(node: object) -> bool:
    """Перевіряє, чи є вузол DOM HTML-елементом або непорожнім текстом поза коментарями."""
    if isinstance(node, Tag):
        return True
    if isinstance(node, _NON_CONTENT_STRING_TYPES):
        return False
    if isinstance(node, NavigableString):
        return bool(str(node).strip())
    return False


def has_meaningful_html_body(html_or_soup: str | BeautifulSoup) -> bool:
    """Перевіряє, чи містить <body> хоча б один елемент або непорожній текст поза коментарями."""
    soup = (
        html_or_soup
        if isinstance(html_or_soup, BeautifulSoup)
        else parse_html_document(html_or_soup)
    )
    body = soup.find("body")
    if isinstance(body, Tag):
        return any(_node_has_visible_content(child) for child in body.contents)

    html_tag = soup.find("html")
    root: Tag = html_tag if isinstance(html_tag, Tag) else soup
    for child in root.contents:
        if isinstance(child, Tag):
            if child.name.lower() in _DOCUMENT_SHELL_TAGS:
                continue
            return True
        if _node_has_visible_content(child):
            return True
    return False


class HtmlGrader(BaseGrader):
    """Стратегія детермінованої автоперевірки HTML5-документів на базі BeautifulSoup4."""

    format_type: PracticalFormat = PracticalFormat.HTML

    def evaluate(
        self,
        *,
        file_path: Path | None = None,
        raw_code: str | None = None,
        rules: list[GradingRule],
        variant_data: dict[str, object],
    ) -> GradingReport:
        """Виконує валідацію DOM-дерева HTML5 за списком правил."""
        html_source = self._resolve_html_source(file_path=file_path, raw_code=raw_code)
        soup = self._parse_html(html_source)

        if not has_meaningful_html_body(soup):
            empty_results = [
                self.build_criterion_result(
                    rule,
                    passed=False,
                    actual=None,
                    feedback=EMPTY_HTML_BODY_ERROR_MESSAGE,
                    resolved_expected=self.resolve_expected(rule.expected, variant_data),
                )
                for rule in rules
            ]
            return self.build_report(empty_results)

        results: list[CriterionResult] = []
        for rule in rules:
            resolved_expected = self.resolve_expected(rule.expected, variant_data)
            resolved_target = self.resolve_expected(rule.target, variant_data)
            result = self._evaluate_rule(
                soup=soup,
                rule=rule,
                target=resolved_target,
                expected=resolved_expected,
            )
            results.append(result)

        return self.build_report(results)

    def _resolve_html_source(
        self,
        *,
        file_path: Path | None,
        raw_code: str | None,
    ) -> str:
        """Отримує вихідний HTML-код із параметра raw_code або з файлу .html."""
        if raw_code is not None:
            return self.require_raw_code(raw_code)

        if file_path is not None:
            resolved_path = self.require_file_path(file_path)
            suffix = resolved_path.suffix.lower()
            if suffix not in {".html", ".htm"}:
                raise InvalidFileFormatError(
                    f"Непідтримуване розширення файлу '{suffix}'. Очікується '.html'.",
                    context={
                        "expected_suffix": ".html",
                        "actual_suffix": suffix,
                        "file_name": resolved_path.name,
                    },
                )
            try:
                content = resolved_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError) as exc:
                raise InvalidFileFormatError(
                    f"Не вдалося прочитати HTML-файл '{resolved_path.name}' у кодуванні UTF-8.",
                    context={"file_name": resolved_path.name, "error": str(exc)},
                ) from exc
            return self.require_raw_code(content)

        return self.require_raw_code(raw_code)

    def _parse_html(self, html_source: str) -> BeautifulSoup:
        """Парсить HTML-рядок у DOM-дерево BeautifulSoup через lxml (або html.parser)."""
        return parse_html_document(html_source)

    def _evaluate_rule(
        self,
        *,
        soup: BeautifulSoup,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Маршрутизує перевірку окремого HTML-правила за його типом."""
        if rule.type == GradingRuleType.HTML_TAG_EXISTS:
            return self._evaluate_tag_exists(
                soup=soup,
                rule=rule,
                target=target,
                expected=expected,
            )
        if rule.type == GradingRuleType.HTML_TAG_COUNT:
            return self._evaluate_tag_count(
                soup=soup,
                rule=rule,
                target=target,
                expected=expected,
            )
        if rule.type == GradingRuleType.HTML_ATTRIBUTE_EXISTS:
            return self._evaluate_attribute_exists(
                soup=soup,
                rule=rule,
                target=target,
                expected=expected,
            )

        raise GradingError(
            f"HtmlGrader не підтримує правило типу '{rule.type.value}'.",
            context={"rule_id": rule.id, "rule_type": rule.type.value},
        )

    def _evaluate_tag_exists(
        self,
        *,
        soup: BeautifulSoup,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє наявність HTML-елемента (або відповідність тексту) за CSS-селектором."""
        target_clean = target.strip()
        expected_clean = expected.strip()
        expected_lower = expected_clean.lower()

        if _is_doctype_target(target_clean):
            return self._evaluate_doctype_exists(
                soup=soup,
                rule=rule,
                expected=expected_clean,
            )

        elements = self._select_elements(soup, rule, target_clean)
        count = len(elements)

        # Режим 1: Булева умова ('true', 'false', 'yes', 'no')
        if expected_lower in {"true", "false", "yes", "no"}:
            expected_bool = self.parse_bool_expected(expected_clean)
            actual_bool = count > 0
            passed = actual_bool == expected_bool
            actual_str = "true" if actual_bool else "false"
            if passed:
                feedback = (
                    f"Елемент за селектором '{target_clean}' знайдено в DOM-дереві "
                    f"(знайдено: {count})."
                    if actual_bool
                    else f"Елемент за селектором '{target_clean}' відсутній, як і очікувалося."
                )
            else:
                feedback = (
                    f"У HTML-документі не знайдено елементів за селектором '{target_clean}'."
                    if not actual_bool
                    else (
                        f"Елемент за селектором '{target_clean}' присутній у документі "
                        f"(знайдено: {count}), хоча очікувалося '{expected}'."
                    )
                )
            return self.build_criterion_result(
                rule,
                passed=passed,
                actual=actual_str,
                feedback=feedback,
                resolved_expected=expected,
            )

        # Режим 2: Числова умова ('>=1', '1', '==2')
        if _NUMERIC_CONDITION_CHECK_PATTERN.match(expected_clean) is not None:
            passed = self.compare_numeric_condition(count, expected_clean)
            feedback = (
                f"Кількість елементів '{target_clean}' ({count}) відповідає умові '{expected}'."
                if passed
                else (
                    f"Кількість елементів '{target_clean}' ({count}) "
                    f"не відповідає очікуваній умові '{expected}'."
                )
            )
            return self.build_criterion_result(
                rule,
                passed=passed,
                actual=str(count),
                feedback=feedback,
                resolved_expected=expected,
            )

        # Режим 3: Перевірка текстового вмісту знайденого елемента
        if not elements:
            return self.build_criterion_result(
                rule,
                passed=False,
                actual=None,
                feedback=(
                    f"Елемент за селектором '{target_clean}' не знайдено "
                    f"(очікувався вміст '{expected_clean}')."
                ),
                resolved_expected=expected,
            )

        mode, needle = _parse_text_match_expected(expected_clean)
        needle_norm = _normalize_text(needle).casefold()
        extracted_texts = [
            _normalize_text(el.get_text(" ", strip=True))
            for el in elements
        ]
        non_empty_texts = [t for t in extracted_texts if t]

        if mode == "not_empty":
            passed = len(non_empty_texts) > 0
        elif mode == "contains":
            passed = any(needle_norm in t.casefold() for t in extracted_texts)
        else:
            passed = any(
                t.casefold() == needle_norm or needle_norm in t.casefold()
                for t in extracted_texts
            )

        actual_text = "; ".join(non_empty_texts) if non_empty_texts else ""
        if passed:
            feedback = (
                f"Елемент '{target_clean}' знайдено, його текстовий вміст ('{actual_text}') "
                f"відповідає вимозі '{expected}'."
            )
        else:
            feedback = (
                f"Текстовий вміст елемента '{target_clean}' ('{actual_text}') "
                f"не відповідає очікуваному '{expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_text or None,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_doctype_exists(
        self,
        *,
        soup: BeautifulSoup,
        rule: GradingRule,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє наявність декларації <!DOCTYPE html> на початку документа."""
        doctypes = [
            str(node).strip()
            for node in soup.contents
            if isinstance(node, Doctype)
        ]
        has_doctype = any(dt.lower() == "html" or "html" in dt.lower() for dt in doctypes)
        expected_lower = expected.strip().lower()

        if expected_lower in {"true", "false", "yes", "no"}:
            expected_bool = self.parse_bool_expected(expected)
        else:
            expected_bool = True

        passed = has_doctype == expected_bool
        actual_str = "true" if has_doctype else "false"
        feedback = (
            "Декларація <!DOCTYPE html> присутня у документі."
            if passed and has_doctype
            else (
                "У документі відсутня обов'язкова декларація <!DOCTYPE html>."
                if not has_doctype
                else f"Статус <!DOCTYPE html> ({actual_str}) відповідає умові '{expected}'."
            )
        )
        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_tag_count(
        self,
        *,
        soup: BeautifulSoup,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Підраховує кількість DOM-елементів за CSS-селектором та звіряє з числовою умовою."""
        target_clean = target.strip()
        expected_clean = expected.strip()
        expected_lower = expected_clean.lower()

        elements = self._select_elements(soup, rule, target_clean)
        count = len(elements)

        if expected_lower in {"true", "false", "yes", "no"}:
            expected_bool = self.parse_bool_expected(expected_clean)
            actual_bool = count > 0
            passed = actual_bool == expected_bool
            actual_str = "true" if actual_bool else "false"
        else:
            passed = self.compare_numeric_condition(count, expected_clean)
            actual_str = str(count)

        if passed:
            feedback = (
                f"Кількість елементів за селектором '{target_clean}' ({count}) "
                f"відповідає умові '{expected}'."
            )
        else:
            feedback = (
                f"Кількість елементів за селектором '{target_clean}' становить {count}, "
                f"очікується '{expected}'."
            )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _evaluate_attribute_exists(
        self,
        *,
        soup: BeautifulSoup,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> CriterionResult:
        """Перевіряє наявність та/або значення атрибутів у цільових HTML-елементах."""
        selector, attr_names, inline_expected_val = self._parse_attribute_rule_spec(
            soup=soup,
            rule=rule,
            target=target,
            expected=expected,
        )
        elements = self._select_elements(soup, rule, selector)
        expected_clean = expected.strip()
        expected_lower = expected_clean.lower()

        if not elements:
            is_negative_check = (
                inline_expected_val is None
                and expected_lower in {"false", "0", "no"}
            )
            missing_actual = (
                "false"
                if expected_lower in {"true", "false", "1", "0", "yes", "no"}
                else None
            )
            return self.build_criterion_result(
                rule,
                passed=is_negative_check,
                actual=missing_actual,
                feedback=(
                    f"Елемент за селектором '{selector}' для перевірки атрибута "
                    f"'{', '.join(attr_names)}' не знайдено у HTML-документі."
                ),
                resolved_expected=expected,
            )

        # Випадок 1: Перевірка конкретного значення атрибута (напр., lang="uk" або type="submit")
        if inline_expected_val is not None:
            attr_name = attr_names[0]
            collected_values: list[str] = []
            matched = False
            for el in elements:
                val = _get_tag_attribute_str(el, attr_name)
                if val is not None:
                    collected_values.append(val)
                    if _attribute_value_matches(val, inline_expected_val):
                        matched = True

            actual_val = ", ".join(dict.fromkeys(collected_values)) if collected_values else None
            if matched:
                feedback = (
                    f"Атрибут '{attr_name}' елемента '{selector}' має очікуване значення "
                    f"'{actual_val}'."
                )
            elif collected_values:
                feedback = (
                    f"Атрибут '{attr_name}' елемента '{selector}' має значення '{actual_val}', "
                    f"очікувалося '{inline_expected_val}'."
                )
            else:
                feedback = (
                    f"Атрибут '{attr_name}' відсутній в елементі '{selector}' "
                    f"(очікувалося значення '{inline_expected_val}')."
                )
            return self.build_criterion_result(
                rule,
                passed=matched,
                actual=actual_val,
                feedback=feedback,
                resolved_expected=expected,
            )

        # Випадок 2: Перевірка наявності одного або кількох атрибутів
        matching_elements_count = sum(
            1
            for el in elements
            if all(_tag_has_attribute(el, attr) for attr in attr_names)
        )
        has_attr = matching_elements_count > 0

        if expected_lower in {"true", "false", "yes", "no"}:
            expected_bool = self.parse_bool_expected(expected_clean)
            passed = has_attr == expected_bool
            actual_str = "true" if has_attr else "false"
        elif _NUMERIC_CONDITION_CHECK_PATTERN.match(expected_clean) is not None:
            passed = self.compare_numeric_condition(matching_elements_count, expected_clean)
            actual_str = str(matching_elements_count)
        else:
            # Коли expected містив назву атрибута (напр. target="img", expected="alt")
            passed = has_attr
            found_attrs = [
                attr
                for attr in attr_names
                if any(_tag_has_attribute(el, attr) for el in elements)
            ]
            actual_str = ", ".join(found_attrs) if found_attrs else "none"

        attr_label = ", ".join(attr_names)
        if passed:
            feedback = (
                f"Атрибут '{attr_label}' присутній в елементі '{selector}'."
                if has_attr
                else f"Атрибут '{attr_label}' відсутній в елементі '{selector}', як і очікувалося."
            )
        else:
            feedback = (
                f"В елементі '{selector}' відсутній обов'язковий атрибут '{attr_label}'."
                if not has_attr
                else (
                    f"Атрибут '{attr_label}' присутній в елементі '{selector}', "
                    f"хоча очікувалося '{expected}'."
                )
            )

        return self.build_criterion_result(
            rule,
            passed=passed,
            actual=actual_str,
            feedback=feedback,
            resolved_expected=expected,
        )

    def _select_elements(
        self,
        soup: BeautifulSoup,
        rule: GradingRule,
        raw_selector: str,
    ) -> list[Tag]:
        """Виконує пошук DOM-елементів за CSS-селектором із нормалізацією табличних рядків."""
        selector = _normalize_selector(raw_selector)
        if not selector:
            raise GradingError(
                f"Порожній CSS-селектор у правилі '{rule.id}'.",
                context={"rule_id": rule.id, "target": raw_selector},
            )

        try:
            selected = [el for el in soup.select(selector) if isinstance(el, Tag)]
        except Exception as exc:
            raise GradingError(
                f"Некоректний CSS-селектор '{raw_selector}' у правилі '{rule.id}': {exc}",
                context={"rule_id": rule.id, "target": raw_selector, "error": str(exc)},
            ) from exc

        # У HTML5 рядки таблиці <tr> часто вкладені у <thead>/<tbody>/<tfoot>.
        # Якщо правило шукає 'table > tr', а прямих дочірніх <tr> немає, перевіряємо секції таблиці.
        if not selected and _TABLE_DIRECT_TR_PATTERN.search(selector) is not None:
            expanded_selector = ", ".join(
                _TABLE_DIRECT_TR_PATTERN.sub(replacement, selector)
                for replacement in (
                    "table > tr",
                    "table > thead > tr",
                    "table > tbody > tr",
                    "table > tfoot > tr",
                )
            )
            try:
                selected = [
                    el for el in soup.select(expanded_selector) if isinstance(el, Tag)
                ]
            except Exception:
                selected = []

        return selected

    def _parse_attribute_rule_spec(
        self,
        *,
        soup: BeautifulSoup,
        rule: GradingRule,
        target: str,
        expected: str,
    ) -> tuple[str, list[str], str | None]:
        """Розбирає target та expected правила html_attribute_exists на (selector, attrs, value)."""
        target_clean = target.strip()
        expected_clean = expected.strip()
        expected_lower = expected_clean.lower()
        is_bool_or_num_expected = (
            expected_lower in {"true", "false", "1", "0", "yes", "no"}
            or _NUMERIC_CONDITION_CHECK_PATTERN.match(expected_clean) is not None
        )

        # Формат 1: selector@attr (напр., 'img@alt', 'html@lang', 'input@type')
        if "@" in target_clean:
            sel_part, attr_part = target_clean.rsplit("@", 1)
            selector = _normalize_selector(sel_part) or "*"
            attr_part_clean = attr_part.strip()
            if not attr_part_clean:
                raise GradingError(
                    f"Не вказано назву атрибута після '@' у цілі '{target}'.",
                    context={"rule_id": rule.id, "target": target},
                )
            if "=" in attr_part_clean:
                a_name, a_val = attr_part_clean.split("=", 1)
                return selector, [a_name.strip().lower()], _strip_quotes(a_val)

            attrs = [a.strip().lower() for a in attr_part_clean.split(",") if a.strip()]
            value_check = None if is_bool_or_num_expected else _strip_quotes(expected_clean)
            return selector, attrs, value_check

        # Формат 2: CSS селектор з атрибутом у квадратних дужках ('img[alt]', 'html[lang="uk"]')
        bracket_match = _ATTR_BRACKET_END_PATTERN.match(target_clean)
        if bracket_match is not None:
            base_sel = _normalize_selector(bracket_match.group(1)) or "*"
            attr_name = bracket_match.group(2).strip().lower()
            inline_op = bracket_match.group(3)
            inline_val = bracket_match.group(5)
            if inline_op is not None and inline_val is not None:
                if not is_bool_or_num_expected:
                    if "=" in expected_clean:
                        attr_key, attr_val = expected_clean.split("=", 1)
                        key_clean = attr_key.strip().lower()
                        if key_clean and re.match(
                            r"^[a-zA-Z_:][a-zA-Z0-9_.:-]*$",
                            key_clean,
                        ):
                            return (
                                _normalize_selector(target_clean),
                                [key_clean],
                                _strip_quotes(attr_val),
                            )
                    expected_attrs = [
                        _strip_quotes(token).lower()
                        for token in re.split(r"[,;]", expected_clean)
                        if _strip_quotes(token)
                    ]
                    if (
                        expected_attrs
                        and all(
                            re.match(r"^[a-zA-Z_:][a-zA-Z0-9_.:-]*$", attr) is not None
                            for attr in expected_attrs
                        )
                        and not (
                            len(expected_attrs) == 1
                            and expected_attrs[0] == inline_val.strip().lower()
                            and expected_attrs[0] not in _KNOWN_HTML_ATTRIBUTES
                        )
                    ):
                        return _normalize_selector(target_clean), expected_attrs, None
                return base_sel, [attr_name], inline_val.strip()
            expected_unquoted = _strip_quotes(expected_clean)
            value_check = (
                None
                if is_bool_or_num_expected or expected_unquoted.lower() == attr_name
                else expected_unquoted
            )
            return base_sel, [attr_name], value_check

        # Формат 3: target='img', expected='alt=Logo' або expected='lang=uk'
        if "=" in expected_clean and not is_bool_or_num_expected:
            attr_key, attr_val = expected_clean.split("=", 1)
            key_clean = attr_key.strip().lower()
            if key_clean and re.match(r"^[a-zA-Z_:][a-zA-Z0-9_.:-]*$", key_clean):
                return _normalize_selector(target_clean), [key_clean], _strip_quotes(attr_val)

        # Формат 4: target='img.alt' або 'a.href', коли після крапки стоїть відомий HTML-атрибут
        if "." in target_clean:
            base_part, dot_suffix = target_clean.rsplit(".", 1)
            candidate_attr = dot_suffix.strip().lower()
            if base_part.strip() and candidate_attr in _KNOWN_HTML_ATTRIBUTES:
                try:
                    has_literal_match = len(soup.select(target_clean)) > 0
                except Exception:
                    has_literal_match = False
                if not has_literal_match:
                    value_check = (
                        None if is_bool_or_num_expected else _strip_quotes(expected_clean)
                    )
                    return _normalize_selector(base_part), [candidate_attr], value_check

        # Формат 5: target='img', expected='alt' або expected='alt,src'
        if not is_bool_or_num_expected:
            attrs = [
                _strip_quotes(token).lower()
                for token in re.split(r"[,;]", expected_clean)
                if _strip_quotes(token)
            ]
            if attrs and all(
                re.match(r"^[a-zA-Z_:][a-zA-Z0-9_.:-]*$", a) is not None for a in attrs
            ):
                return _normalize_selector(target_clean), attrs, None

        raise GradingError(
            f"Не вдалося визначити цільовий HTML-атрибут у правилі '{rule.id}' "
            f"(target='{target}', expected='{expected}'). "
            "Використовуйте формат 'tag@attr', 'tag[attr]' або вкажіть назву атрибута в expected.",
            context={"rule_id": rule.id, "target": target, "expected": expected},
        )


def _is_doctype_target(target: str) -> bool:
    """Перевіряє, чи стосується селектор декларації <!DOCTYPE html>."""
    lowered = target.strip().lower()
    return lowered in {"doctype", "!doctype", "<!doctype>", "<!doctype html>"}


def _normalize_selector(raw_selector: str) -> str:
    """Нормалізує запис тегу ('<h1>' -> 'h1') або повертає очищений CSS-селектор."""
    cleaned = raw_selector.strip()
    tag_match = _BARE_TAG_CLOSURE_PATTERN.match(cleaned)
    if tag_match is not None:
        return tag_match.group(1)
    return cleaned


def _normalize_text(text: str) -> str:
    """Нормалізує пробільні символи всередині тексту елемента."""
    return " ".join(text.split())


def _strip_quotes(value: str) -> str:
    """Видаляє обрамлюючі одинарні або подвійні лапки з рядка."""
    cleaned = value.strip()
    if (
        len(cleaned) >= 2
        and cleaned[0] in {"'", '"'}
        and cleaned[-1] == cleaned[0]
    ):
        return cleaned[1:-1].strip()
    return cleaned


def _parse_text_match_expected(expected: str) -> tuple[str, str]:
    """Визначає режим перевірки тексту елемента ('not_empty', 'contains', 'match')."""
    cleaned = expected.strip()
    lowered = cleaned.lower()
    if lowered in {"not_empty", "not_null", "non_empty", "exists", "any"}:
        return "not_empty", ""
    if lowered.startswith("contains:"):
        return "contains", _strip_quotes(cleaned[9:])
    if lowered.startswith("text:"):
        return "match", _strip_quotes(cleaned[5:])
    return "match", _strip_quotes(cleaned)


def _tag_has_attribute(tag: Tag, attr_name: str) -> bool:
    """Перевіряє, чи має HTML-елемент указаний атрибут із непорожнім значенням."""
    attr_key = _find_tag_attr_key(tag, attr_name)
    if attr_key is None:
        return False

    raw_val: object = tag.attrs.get(attr_key)
    if raw_val is None:
        return False
    if isinstance(raw_val, str):
        # Булеві HTML5-атрибути (required, disabled, checked, readonly, multiple, controls, hidden)
        # у BeautifulSoup можуть мати порожній рядок "" як валідне значення присутності
        if attr_key.lower() in {
            "autofocus",
            "checked",
            "controls",
            "disabled",
            "hidden",
            "loop",
            "multiple",
            "muted",
            "novalidate",
            "readonly",
            "required",
            "selected",
        }:
            return True
        return bool(raw_val.strip())
    if isinstance(raw_val, list):
        return any(str(item).strip() for item in raw_val)
    return True


def _get_tag_attribute_str(tag: Tag, attr_name: str) -> str | None:
    """Повертає текстове представлення значення атрибута HTML-тегу або None."""
    attr_key = _find_tag_attr_key(tag, attr_name)
    if attr_key is None:
        return None

    raw_val: object = tag.attrs.get(attr_key)
    if raw_val is None:
        return None
    if isinstance(raw_val, list):
        return " ".join(str(item).strip() for item in raw_val if str(item).strip())
    return str(raw_val).strip()


def _find_tag_attr_key(tag: Tag, attr_name: str) -> str | None:
    """Знаходить ключ атрибута в словнику tag.attrs без урахування регістру."""
    target_lower = attr_name.strip().lower()
    if target_lower in tag.attrs:
        return target_lower
    for key in tag.attrs:
        if isinstance(key, str) and key.lower() == target_lower:
            return key
    return None


def _attribute_value_matches(actual_val: str, expected_val: str) -> bool:
    """Порівнює фактичне значення HTML-атрибута з очікуваним (включно з токенами класів)."""
    actual_clean = actual_val.strip()
    expected_clean = expected_val.strip()
    if actual_clean.casefold() == expected_clean.casefold():
        return True
    actual_tokens = {tok.casefold() for tok in actual_clean.split() if tok}
    return expected_clean.casefold() in actual_tokens
