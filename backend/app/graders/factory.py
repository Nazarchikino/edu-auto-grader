import importlib
from typing import ClassVar

from app.core.exceptions import GradingError, InvalidFileFormatError
from app.graders.base import BaseGrader
from app.models.course import PracticalFormat

_DEFAULT_GRADER_MODULES: dict[PracticalFormat, tuple[str, str]] = {
    PracticalFormat.DOCX: ("app.graders.docx_grader", "DocxGrader"),
    PracticalFormat.XLSX: ("app.graders.xlsx_grader", "XlsxGrader"),
    PracticalFormat.ACCDB: ("app.graders.accdb_grader", "AccdbGrader"),
    PracticalFormat.HTML: ("app.graders.html_grader", "HtmlGrader"),
}


class GraderFactory:
    """Фабрика вибору стратегії автоперевірки залежно від формату практичної роботи."""

    _registry: ClassVar[dict[PracticalFormat, type[BaseGrader]]] = {}

    @classmethod
    def normalize_format(cls, format_type: PracticalFormat | str) -> PracticalFormat:
        """Нормалізує вхідний формат (Enum або рядок, включно з '.docx') до PracticalFormat."""
        if isinstance(format_type, PracticalFormat):
            return format_type

        cleaned = format_type.strip().lower().lstrip(".")
        try:
            return PracticalFormat(cleaned)
        except ValueError as exc:
            supported = [member.value for member in PracticalFormat]
            raise InvalidFileFormatError(
                f"Непідтримуваний формат практичної роботи: '{format_type}'. "
                f"Доступні формати: {', '.join(supported)}.",
                context={"format_type": format_type, "supported_formats": supported},
            ) from exc

    @classmethod
    def register(
        cls,
        format_type: PracticalFormat | str,
        grader_cls: type[BaseGrader],
    ) -> None:
        """Реєструє клас-стратегію парсера для вказаного формату."""
        resolved_format = cls.normalize_format(format_type)
        if not issubclass(grader_cls, BaseGrader):
            raise GradingError(
                f"Клас '{grader_cls.__name__}' повинен успадковувати BaseGrader.",
                context={"grader_class": grader_cls.__name__},
            )
        cls._registry[resolved_format] = grader_cls

    @classmethod
    def unregister(cls, format_type: PracticalFormat | str) -> None:
        """Видаляє зареєстрований парсер зі словника фабрики."""
        resolved_format = cls.normalize_format(format_type)
        cls._registry.pop(resolved_format, None)

    @classmethod
    def _load_default_grader_class(
        cls,
        format_type: PracticalFormat,
    ) -> type[BaseGrader]:
        """Ліниво імпортує стандартну стратегію парсера для формату PracticalFormat."""
        target = _DEFAULT_GRADER_MODULES.get(format_type)
        if target is None:
            raise InvalidFileFormatError(
                f"Для формату '{format_type.value}' не визначено стратегію перевірки.",
                context={"format_type": format_type.value},
            )

        module_path, class_name = target
        try:
            module = importlib.import_module(module_path)
            candidate: object = getattr(module, class_name)
        except (ModuleNotFoundError, AttributeError) as exc:
            raise GradingError(
                f"Парсер '{class_name}' для формату '{format_type.value}' ще не зареєстровано.",
                context={
                    "format_type": format_type.value,
                    "module_path": module_path,
                    "class_name": class_name,
                },
            ) from exc

        if not isinstance(candidate, type) or not issubclass(candidate, BaseGrader):
            raise GradingError(
                f"Об'єкт '{class_name}' у модулі '{module_path}' не є підкласом BaseGrader.",
                context={
                    "format_type": format_type.value,
                    "class_name": class_name,
                },
            )

        cls._registry[format_type] = candidate
        return candidate

    @classmethod
    def get_grader(cls, format_type: PracticalFormat | str) -> BaseGrader:
        """Повертає екземпляр відповідного парсера (BaseGrader) для заданого формату."""
        resolved_format = cls.normalize_format(format_type)
        grader_cls = cls._registry.get(resolved_format)
        if grader_cls is None:
            grader_cls = cls._load_default_grader_class(resolved_format)
        return grader_cls()
