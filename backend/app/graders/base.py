import math
import re
from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.models.course import PracticalFormat
from app.schemas.grading import CriterionResult, GradingReport, GradingRule

_NUMERIC_CONDITION_PATTERN = re.compile(
    r"^\s*(>=|<=|!=|==|>|<|=)?\s*([+-]?\d+(?:[.,]\d+)?)\s*$"
)
_PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


class BaseGrader(ABC):
    """Абстрактний базовий клас стратегії детермінованої автоперевірки практичних робіт."""

    format_type: PracticalFormat

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
