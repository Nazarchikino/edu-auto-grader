import math
import re
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from decimal import Decimal
from pathlib import Path

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.models.course import PracticalFormat
from app.schemas.grading import (
    CriterionResult,
    GradingReport,
    GradingRule,
    GradingRuleType,
)

_NUMERIC_CONDITION_PATTERN = re.compile(
    r"^\s*(>=|<=|!=|==|>|<|=)?\s*([+-]?\d+(?:[.,]\d+)?)\s*$"
)
_PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
_WHOLE_PLACEHOLDER_PATTERN = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

_ALIGNMENT_UK_LABELS: dict[str, str] = {
    "justify": "по ширині",
    "both": "по ширині",
    "center": "по центру",
    "left": "по лівому краю",
    "right": "по правому краю",
    "distribute": "рівномірно за шириною",
}
_MARGIN_SIDE_ORDER: tuple[str, ...] = ("left", "right", "top", "bottom")
_MARGIN_SIDE_UK_LABELS: dict[str, str] = {
    "left": "ліве",
    "right": "праве",
    "top": "верхнє",
    "bottom": "нижнє",
}
_SINGLE_MARGIN_PATTERN = re.compile(
    r"^\s*(\d+(?:[.,]\d+)?)\s*(cm|mm|см|мм)?\s*$",
    re.IGNORECASE,
)
_COMPARISON_VALUE_PATTERN = re.compile(
    r"^\s*(>=|<=|>|<)\s*(\d+(?:[.,]\d+)?)\s*$"
)


def _format_uk_decimal(raw_number: str) -> str:
    """Форматує десяткове число з українською комою без зайвих кінцевих нулів."""
    normalized = raw_number.strip().replace(",", ".")
    if "." not in normalized:
        return normalized
    stripped = normalized.rstrip("0").rstrip(".")
    return stripped.replace(".", ",")


def _format_margin_measurement(raw_value: object) -> str:
    """Перетворює одиночний розмір поля ('1.5cm', '20mm', 2.0) у читабельний запис з одиницями."""
    if isinstance(raw_value, (int, float, Decimal)) and not isinstance(raw_value, bool):
        numeric = float(raw_value)
        unit = "см" if numeric <= 5.0 else "мм"
        return f"{_format_uk_decimal(str(raw_value))} {unit}"

    cleaned = str(raw_value).strip().strip("'\"")
    match = _SINGLE_MARGIN_PATTERN.fullmatch(cleaned)
    if match is None:
        return cleaned

    num_str = match.group(1)
    unit_raw = (match.group(2) or "").lower()
    if unit_raw in {"cm", "см"}:
        unit = "см"
    elif unit_raw in {"mm", "мм"}:
        unit = "мм"
    else:
        unit = "см" if float(num_str.replace(",", ".")) <= 5.0 else "мм"
    return f"{_format_uk_decimal(num_str)} {unit}"


def _format_margins_value(raw_value: object) -> str:
    """Форматує поля сторінки (рядок або словник) зрозумілою українською мовою."""
    if isinstance(raw_value, Mapping):
        parts: list[str] = []
        for side in _MARGIN_SIDE_ORDER:
            if side in raw_value:
                side_label = _MARGIN_SIDE_UK_LABELS[side]
                parts.append(f"{side_label} — {_format_margin_measurement(raw_value[side])}")
        if parts:
            return ", ".join(parts)

    cleaned = str(raw_value).strip().strip("'\"")
    if "=" in cleaned:
        side_values: dict[str, str] = {}
        for token in re.split(r"[,;]", cleaned):
            item = token.strip()
            if "=" not in item:
                continue
            k_raw, v_raw = item.split("=", maxsplit=1)
            side = k_raw.strip().lower()
            if side in _MARGIN_SIDE_UK_LABELS:
                side_values[side] = _format_margin_measurement(v_raw)
        if side_values:
            ordered = [
                f"{_MARGIN_SIDE_UK_LABELS[side]} — {side_values[side]}"
                for side in _MARGIN_SIDE_ORDER
                if side in side_values
            ]
            return ", ".join(ordered)

    if _SINGLE_MARGIN_PATTERN.fullmatch(cleaned) is not None:
        return f"по {_format_margin_measurement(cleaned)} з усіх боків"

    return cleaned


def _format_student_placeholder_value(token: str, raw_value: object) -> str:
    """Перетворює технічне значення параметра варіанта у зрозумілий український текст."""
    token_lower = token.lower()

    if isinstance(raw_value, bool):
        return "так" if raw_value else "ні"

    if isinstance(raw_value, Mapping):
        keys_lower = {str(k).lower() for k in raw_value}
        if keys_lower and keys_lower.issubset(set(_MARGIN_SIDE_ORDER)):
            return _format_margins_value(raw_value)
        formatted_pairs = [
            f"{k}: {_format_student_placeholder_value(str(k), v)}"
            for k, v in raw_value.items()
        ]
        return ", ".join(formatted_pairs)

    if isinstance(raw_value, (list, tuple)):
        return ", ".join(
            _format_student_placeholder_value(token, item) for item in raw_value
        )

    if isinstance(raw_value, (int, float, Decimal)):
        return _format_uk_decimal(str(raw_value))

    cleaned = str(raw_value).strip().strip("'\"")
    cleaned_lower = cleaned.lower()

    if cleaned_lower in _ALIGNMENT_UK_LABELS:
        return _ALIGNMENT_UK_LABELS[cleaned_lower]

    if cleaned_lower in {"true", "yes"}:
        return "так"
    if cleaned_lower in {"false", "no"}:
        return "ні"

    if (
        token_lower == "margins"
        or token_lower.endswith("_margins")
        or (
            "=" in cleaned
            and any(f"{side}=" in cleaned_lower for side in _MARGIN_SIDE_ORDER)
        )
    ):
        return _format_margins_value(cleaned)

    if token_lower == "line_spacing":
        num_norm = cleaned.replace(",", ".")
        if num_norm in {"1", "1.0"}:
            return "1,0 (одинарний)"
        if num_norm in {"2", "2.0"}:
            return "2,0 (подвійний)"
        return cleaned.replace(".", ",")

    if token_lower == "body_size" or token_lower.endswith("_size"):
        size_clean = re.sub(r"\s*(?:pt|пт)$", "", cleaned, flags=re.IGNORECASE)
        return _format_uk_decimal(size_clean)

    if token_lower == "min_tables":
        comp_match = _COMPARISON_VALUE_PATTERN.fullmatch(cleaned)
        if comp_match is not None:
            op, num_str = comp_match.group(1), comp_match.group(2)
            num_int = int(float(num_str.replace(",", ".")))
            if op == ">=" and num_int == 0:
                return "таблиця за цим варіантом не обов'язкова"
            if op == ">=" and num_int == 1:
                return "потрібна щонайменше 1 таблиця"
            if op == ">=":
                is_few = 2 <= (num_int % 10) <= 4 and not (12 <= (num_int % 100) <= 14)
                noun = "таблиці" if is_few else "таблиць"
                return f"потрібно щонайменше {num_int} {noun}"

    if token_lower == "pk_target" and "." in cleaned:
        table_name, col_name = cleaned.split(".", maxsplit=1)
        return f"«{col_name.strip()}» у таблиці «{table_name.strip()}»"

    comp_match = _COMPARISON_VALUE_PATTERN.fullmatch(cleaned)
    if comp_match is not None:
        op, num_str = comp_match.group(1), _format_uk_decimal(comp_match.group(2))
        op_labels = {
            ">=": "не менше",
            "<=": "не більше",
            ">": "більше",
            "<": "менше",
        }
        return f"{op_labels[op]} {num_str}"

    return cleaned


def format_student_criterion_description(
    description: str,
    variant_data: Mapping[str, object],
) -> str:
    """Підставляє параметри варіанта в опис критерію, форматуючи їх зрозумілою українською."""
    if "{" not in description:
        return description.strip()

    lookup: dict[str, object] = {}
    for key, value in variant_data.items():
        if key != "parameters":
            lookup[key] = value

    nested_params = variant_data.get("parameters")
    if isinstance(nested_params, Mapping):
        for key, value in nested_params.items():
            if isinstance(key, str):
                lookup[key] = value

    def _replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token not in lookup:
            return match.group(0)
        return _format_student_placeholder_value(token, lookup[token])

    return _PLACEHOLDER_PATTERN.sub(_replace, description).strip()


class BaseGrader(ABC):
    """Абстрактний базовий клас стратегії детермінованої автоперевірки практичних робіт."""

    format_type: PracticalFormat
    supported_rule_types: frozenset[GradingRuleType] = frozenset()

    def validate_rule_definition(self, rule: GradingRule) -> None:
        """Валідує тип правила та базовий синтаксис target/expected перед збереженням."""
        if self.supported_rule_types and rule.type not in self.supported_rule_types:
            raise GradingError(
                f"Правило '{rule.id}' типу '{rule.type.value}' не підтримується парсером "
                f"формату '{self.format_type.value}'.",
                code="INVALID_RULE_TYPE_FOR_FORMAT",
                status_code=422,
                context={
                    "rule_id": rule.id,
                    "rule_type": rule.type.value,
                    "format_type": self.format_type.value,
                },
            )
        if not rule.target.strip():
            raise GradingError(
                f"Порожнє поле target у правилі '{rule.id}'.",
                code="INVALID_RULE_DEFINITION",
                status_code=422,
                context={"rule_id": rule.id, "field": "target"},
            )
        if not rule.expected.strip():
            raise GradingError(
                f"Порожнє поле expected у правилі '{rule.id}'.",
                code="INVALID_RULE_DEFINITION",
                status_code=422,
                context={"rule_id": rule.id, "field": "expected"},
            )

    def is_whole_placeholder(self, value: str) -> bool:
        """Перевіряє, чи складається рядок виключно з одного плейсхолдера `{param}`."""
        return _WHOLE_PLACEHOLDER_PATTERN.fullmatch(value.strip()) is not None

    def substitute_placeholders_for_validation(
        self,
        value: str,
        sample: str = "1",
    ) -> str:
        """Підміняє плейсхолдери `{param}` тестовим значенням для синтаксичної валідації."""
        return _PLACEHOLDER_PATTERN.sub(sample, value)

    def is_valid_numeric_condition(self, expr: str) -> bool:
        """Повертає True, якщо рядок є коректною числовою умовою вигляду '>=4' або '1.5'."""
        return _NUMERIC_CONDITION_PATTERN.match(expr) is not None

    def validate_numeric_condition(
        self,
        rule: GradingRule,
        expr: str,
        *,
        sample_number: str = "1",
    ) -> None:
        """Перевіряє синтаксис числової умови з урахуванням плейсхолдерів `{param}`."""
        if self.is_whole_placeholder(expr):
            return
        substituted = self.substitute_placeholders_for_validation(expr, sample_number)
        if not self.is_valid_numeric_condition(substituted):
            raise GradingError(
                f"Некоректна числова умова expected='{rule.expected}' у правилі '{rule.id}'. "
                "Очікується число або оператор порівняння (напр. '1.5', '>=4', '==2').",
                code="INVALID_RULE_DEFINITION",
                status_code=422,
                context={
                    "rule_id": rule.id,
                    "rule_type": rule.type.value,
                    "expected": rule.expected,
                },
            )

    def validate_bool_or_numeric_condition(
        self,
        rule: GradingRule,
        expr: str,
        *,
        sample_number: str = "1",
    ) -> None:
        """Перевіряє, що умова є булевою ('true'/'false') або числовою ('>=1', '2')."""
        if self.is_whole_placeholder(expr):
            return
        substituted = self.substitute_placeholders_for_validation(expr, sample_number).strip()
        if substituted.lower() in {"true", "false", "yes", "no"}:
            return
        if self.is_valid_numeric_condition(substituted):
            return
        raise GradingError(
            f"Некоректний вираз expected='{rule.expected}' у правилі '{rule.id}'. "
            "Дозволені булеві значення ('true', 'false') або числові умови (напр. '>=1', '2').",
            code="INVALID_RULE_DEFINITION",
            status_code=422,
            context={
                "rule_id": rule.id,
                "rule_type": rule.type.value,
                "expected": rule.expected,
            },
        )

    @abstractmethod
    def evaluate(
        self,
        *,
        file_path: Path | None = None,
        raw_code: str | None = None,
        rules: list[GradingRule],
        variant_data: dict[str, object],
    ) -> GradingReport:
        """Виконує детерміновану перевірку роботи за списком правил."""
        raise NotImplementedError

    def require_file_path(
        self,
        file_path: Path | None,
        *,
        expected_suffix: str | None = None,
    ) -> Path:
        """Перевіряє наявність файлу на диску та відповідність очікуваному розширенню."""
        if file_path is None:
            raise InvalidFileFormatError(
                "Не передано шлях до файлу для перевірки практичної роботи.",
                context={"format_type": str(getattr(self, "format_type", "unknown"))},
            )

        resolved_path = Path(file_path)
        if not resolved_path.exists() or not resolved_path.is_file():
            raise InvalidFileFormatError(
                f"Файл для перевірки не знайдено: '{resolved_path.name}'.",
                context={"file_path": str(resolved_path)},
            )

        if expected_suffix is not None:
            normalized_expected = (
                expected_suffix.lower()
                if expected_suffix.startswith(".")
                else f".{expected_suffix.lower()}"
            )
            actual_suffix = resolved_path.suffix.lower()
            if actual_suffix != normalized_expected:
                raise InvalidFileFormatError(
                    f"Непідтримуване розширення файлу '{actual_suffix}'. "
                    f"Очікується '{normalized_expected}'.",
                    context={
                        "expected_suffix": normalized_expected,
                        "actual_suffix": actual_suffix,
                        "file_name": resolved_path.name,
                    },
                )

        return resolved_path

    def require_raw_code(self, raw_code: str | None) -> str:
        """Перевіряє наявність непорожнього вихідного коду для текстових/HTML-парсерів."""
        if raw_code is None or not raw_code.strip():
            raise InvalidFileFormatError(
                "Вихідний код роботи порожній або не переданий для перевірки.",
                context={"format_type": str(getattr(self, "format_type", "html"))},
            )
        return raw_code

    def resolve_expected(
        self,
        expected: str,
        variant_data: dict[str, object],
    ) -> str:
        """Підставляє параметри індивідуального варіанта `{param}` у рядок очікуваного значення."""
        if "{" not in expected:
            return expected

        lookup: dict[str, str] = {}
        for key, value in variant_data.items():
            if isinstance(value, (str, int, float, bool)):
                lookup[key] = str(value)

        nested_params = variant_data.get("parameters")
        if isinstance(nested_params, dict):
            for key, value in nested_params.items():
                if isinstance(key, str) and isinstance(value, (str, int, float, bool)):
                    lookup[key] = str(value)

        def _replace(match: re.Match[str]) -> str:
            token = match.group(1)
            return lookup.get(token, match.group(0))

        return _PLACEHOLDER_PATTERN.sub(_replace, expected)

    def parse_bool_expected(self, expected_expr: str) -> bool:
        """Перетворює текстове очікуване значення ('true', '1', 'yes', 'false', '0') на bool."""
        normalized = expected_expr.strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
        raise GradingError(
            f"Некоректний булевий вираз очікуваного значення у правилі: '{expected_expr}'.",
            context={"expected": expected_expr},
        )

    def compare_numeric_condition(
        self,
        actual_value: int | float,
        expected_expr: str,
        *,
        tolerance: float = 1e-4,
    ) -> bool:
        """Детерміновано перевіряє числову умову вигляду '>=4', '<=10', '==1.5', '18500'."""
        match = _NUMERIC_CONDITION_PATTERN.match(expected_expr)
        if match is None:
            raise GradingError(
                f"Некоректний числовий вираз очікуваного значення: '{expected_expr}'.",
                context={"expected": expected_expr},
            )

        operator_str = match.group(1) or "=="
        threshold = float(match.group(2).replace(",", "."))
        actual_float = float(actual_value)

        if operator_str in {"==", "="}:
            return math.isclose(actual_float, threshold, abs_tol=tolerance)
        if operator_str == "!=":
            return not math.isclose(actual_float, threshold, abs_tol=tolerance)
        if operator_str == ">=":
            return actual_float > threshold or math.isclose(
                actual_float, threshold, abs_tol=tolerance
            )
        if operator_str == "<=":
            return actual_float < threshold or math.isclose(
                actual_float, threshold, abs_tol=tolerance
            )
        if operator_str == ">":
            return actual_float > threshold and not math.isclose(
                actual_float, threshold, abs_tol=tolerance
            )
        if operator_str == "<":
            return actual_float < threshold and not math.isclose(
                actual_float, threshold, abs_tol=tolerance
            )
        return False

    def build_criterion_result(
        self,
        rule: GradingRule,
        *,
        passed: bool,
        actual: str | None,
        feedback: str,
        resolved_expected: str | None = None,
    ) -> CriterionResult:
        """Формує уніфікований результат перевірки одного критерію з нарахуванням балів."""
        max_points = round(float(rule.points), 2)
        points_awarded = max_points if passed else 0.0
        return CriterionResult(
            rule_id=rule.id,
            rule_type=rule.type,
            target=rule.target,
            expected=resolved_expected if resolved_expected is not None else rule.expected,
            actual=actual,
            passed=passed,
            points_awarded=points_awarded,
            max_points=max_points,
            description=rule.description,
            feedback=feedback,
        )

    def build_report(
        self,
        results: Sequence[CriterionResult],
    ) -> GradingReport:
        """Централізовано агрегує результати всіх критеріїв та підраховує підсумковий бал."""
        result_list = list(results)
        total_points = round(sum(item.points_awarded for item in result_list), 2)
        max_points = round(sum(item.max_points for item in result_list), 2)
        passed_count = sum(1 for item in result_list if item.passed)
        failed_count = len(result_list) - passed_count

        return GradingReport(
            format_type=self.format_type,
            total_points=total_points,
            max_points=max_points,
            passed_count=passed_count,
            failed_count=failed_count,
            results=result_list,
        )
