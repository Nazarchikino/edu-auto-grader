class DomainError(Exception):
    """Базовий доменний виняток системи з уніфікованим контрактом відповіді."""

    def __init__(
        self,
        detail: str,
        *,
        code: str = "DOMAIN_ERROR",
        status_code: int = 400,
        context: dict[str, object] | None = None,
    ) -> None:
        super().__init__(detail)
        self.detail: str = detail
        self.code: str = code
        self.status_code: int = status_code
        self.context: dict[str, object] = context if context is not None else {}


class GradingError(DomainError):
    """Помилка під час автоматизованої перевірки практичної роботи."""

    def __init__(
        self,
        detail: str,
        *,
        code: str = "GRADING_ERROR",
        status_code: int = 422,
        context: dict[str, object] | None = None,
    ) -> None:
        super().__init__(detail, code=code, status_code=status_code, context=context)


class InvalidFileFormatError(GradingError):
    """Завантажений файл має некоректний або пошкоджений формат."""

    def __init__(
        self,
        detail: str,
        *,
        context: dict[str, object] | None = None,
    ) -> None:
        super().__init__(
            detail,
            code="INVALID_FILE_FORMAT",
            status_code=415,
            context=context,
        )


class PlagiarismDetectedError(DomainError):
    """Виявлено порушення академічної доброчесності (збіг хешу або метаданих)."""

    def __init__(
        self,
        detail: str,
        *,
        context: dict[str, object] | None = None,
    ) -> None:
        super().__init__(
            detail,
            code="PLAGIARISM_DETECTED",
            status_code=409,
            context=context,
        )


class QuizNotPassedError(DomainError):
    """Спроба доступу або здачі практичної роботи без успішного тесту-допуску."""

    def __init__(
        self,
        detail: str = (
            "Необхідно успішно скласти тест-допуск (>= 70%) "
            "перед здачею практичної роботи."
        ),
        *,
        context: dict[str, object] | None = None,
    ) -> None:
        super().__init__(
            detail,
            code="QUIZ_NOT_PASSED",
            status_code=403,
            context=context,
        )
