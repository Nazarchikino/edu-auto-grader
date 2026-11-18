import uuid
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import (
    DomainError,
    InvalidFileFormatError,
    PlagiarismDetectedError,
)
from app.graders.factory import GraderFactory
from app.graders.metadata import (
    check_submission_plagiarism,
    compute_submission_hash,
    extract_document_metadata,
)
from app.models.course import CourseSlug, Module, Practical, PracticalFormat
from app.models.progress import Submission
from app.models.user import User, UserRole
from app.schemas.course import PracticalTeacherRead, PracticalVariant
from app.schemas.grading import (
    ExtractedMetadata,
    GradingReport,
    GradingRule,
    GradingRulesUpdateRequest,
)
from app.schemas.submission import ManualGradeUpdateRequest, SubmissionRead
from app.services.quiz_service import QuizService, resolve_student_variant

_HTML_EXTENSIONS: frozenset[str] = frozenset({".html", ".htm"})


def serialize_practical_teacher(practical: Practical) -> PracticalTeacherRead:
    """Перетворює ORM-модель Practical у повну схему PracticalTeacherRead для викладача."""
    variants = [PracticalVariant.model_validate(item) for item in practical.variants]
    grading_rules = [GradingRule.model_validate(item) for item in practical.grading_rules]
    return PracticalTeacherRead(
        id=practical.id,
        module_id=practical.module_id,
        title=practical.title,
        instructions=practical.instructions,
        format_type=practical.format_type,
        max_score=float(practical.max_score),
        variants=variants,
        grading_rules=grading_rules,
    )


def serialize_submission(submission: Submission) -> SubmissionRead:
    """Перетворює ORM-модель Submission зі зв'язаними сутностями у контракт SubmissionRead."""
    practical: Practical | None = submission.__dict__.get("practical")
    student: User | None = submission.__dict__.get("student")

    practical_title: str | None = None
    course_slug: CourseSlug | None = None
    max_score: float = 10.0

    if practical is not None:
        practical_title = practical.title
        max_score = float(practical.max_score)
        module: Module | None = practical.__dict__.get("module")
        if module is not None:
            course = module.__dict__.get("course")
            if course is not None:
                course_slug = course.slug

    student_full_name: str | None = student.full_name if student is not None else None
    extracted_metadata = ExtractedMetadata.model_validate(submission.extracted_metadata)
    grading_report = GradingReport.model_validate(submission.grading_report)

    return SubmissionRead(
        id=submission.id,
        practical_id=submission.practical_id,
        practical_title=practical_title,
        course_slug=course_slug,
        student_id=submission.student_id,
        student_full_name=student_full_name,
        variant_index=submission.variant_index,
        variant_number=submission.variant_index + 1,
        file_path=submission.file_path,
        raw_code=submission.raw_code,
        file_hash=submission.file_hash,
        extracted_metadata=extracted_metadata,
        is_plagiarism_flagged=submission.is_plagiarism_flagged,
        plagiarism_reason=submission.plagiarism_reason,
        auto_score=float(submission.auto_score),
        final_score=float(submission.final_score),
        max_score=max_score,
        grading_report=grading_report,
        teacher_comment=submission.teacher_comment,
        submitted_at=submission.submitted_at,
    )


class SubmissionService:
    """Сервіс оркестрації здачі практичних робіт, автоперевірки, антиплагіату та оцінювання."""

    def __init__(
        self,
        db: AsyncSession,
        *,
        uploads_dir: Path | None = None,
    ) -> None:
        self._db = db
        self._quiz_service = QuizService(db)
        self._uploads_dir = uploads_dir if uploads_dir is not None else settings.UPLOADS_DIR

    async def _load_practical_or_404(self, practical_id: uuid.UUID) -> Practical:
        """Завантажує практичну роботу разом із модулем та курсом або генерує 404."""
        stmt = (
            select(Practical)
            .options(
                selectinload(Practical.module).selectinload(Module.course),
            )
            .where(Practical.id == practical_id)
        )
        result = await self._db.execute(stmt)
        practical = result.scalar_one_or_none()
        if practical is None:
            raise DomainError(
                "Практичну роботу не знайдено.",
                code="PRACTICAL_NOT_FOUND",
                status_code=404,
                context={"practical_id": str(practical_id)},
            )
        return practical

    async def _load_submission_or_404(self, submission_id: uuid.UUID) -> Submission:
        """Завантажує здачу практичної роботи зі зв'язаними практичною, курсом і студентом."""
        stmt = (
            select(Submission)
            .options(
                selectinload(Submission.practical)
                .selectinload(Practical.module)
                .selectinload(Module.course),
                selectinload(Submission.student),
            )
            .where(Submission.id == submission_id)
        )
        result = await self._db.execute(stmt)
        submission = result.scalar_one_or_none()
        if submission is None:
            raise DomainError(
                "Здачу практичної роботи не знайдено.",
                code="SUBMISSION_NOT_FOUND",
                status_code=404,
                context={"submission_id": str(submission_id)},
            )
        return submission

    def _evaluate_html_submission(
        self,
        *,
        practical: Practical,
        rules: list[GradingRule],
        variant_data: dict[str, object],
        raw_code: str | None,
        file_bytes: bytes | None,
        filename: str | None,
    ) -> tuple[str, str, ExtractedMetadata, GradingReport]:
        """Виконує перевірку HTML-коду та обчислює його нормалізований SHA-256 хеш."""
        resolved_code = raw_code

        if resolved_code is None and file_bytes is not None:
            safe_filename = (filename or "").strip()
            actual_suffix = Path(safe_filename).suffix.lower()
            if actual_suffix not in _HTML_EXTENSIONS:
                raise InvalidFileFormatError(
                    f"Непідтримуване розширення файлу '{actual_suffix or 'невідоме'}' "
                    "для HTML-практичної роботи. Очікується '.html' або JSON із 'raw_code'.",
                    context={
                        "expected_format": practical.format_type.value,
                        "actual_suffix": actual_suffix,
                        "file_name": safe_filename,
                    },
                )
            try:
                resolved_code = file_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise InvalidFileFormatError(
                    "Завантажений HTML-файл має некоректне кодування (очікується UTF-8).",
                    context={"file_name": safe_filename},
                ) from exc

        if resolved_code is None or not resolved_code.strip():
            raise InvalidFileFormatError(
                "Для здачі HTML-практичної роботи необхідно передати непорожній вихідний код.",
                context={"format_type": practical.format_type.value},
            )

        file_hash = compute_submission_hash(raw_code=resolved_code)
        extracted_metadata = ExtractedMetadata()
        grader = GraderFactory.get_grader(practical.format_type)
        report = grader.evaluate(
            raw_code=resolved_code,
            rules=rules,
            variant_data=variant_data,
        )
        return resolved_code, file_hash, extracted_metadata, report

    def _evaluate_file_submission(
        self,
        *,
        submission_id: uuid.UUID,
        student_id: uuid.UUID,
        practical: Practical,
        rules: list[GradingRule],
        variant_data: dict[str, object],
        file_bytes: bytes | None,
        filename: str | None,
    ) -> tuple[Path, str, ExtractedMetadata, GradingReport]:
        """Зберігає файл (.docx/.xlsx/.accdb), витягує метадані та запускає парсер."""
        if file_bytes is None:
            raise InvalidFileFormatError(
                f"Для практичної роботи формату '.{practical.format_type.value}' "
                "необхідно завантажити файл.",
                context={"expected_format": practical.format_type.value},
            )

        safe_filename = (filename or "").strip()
        expected_suffix = f".{practical.format_type.value}"
        actual_suffix = Path(safe_filename).suffix.lower()
        if actual_suffix != expected_suffix:
            raise InvalidFileFormatError(
                f"Непідтримуване розширення файлу '{actual_suffix or 'невідоме'}'. "
                f"Очікується '{expected_suffix}'.",
                context={
                    "expected_suffix": expected_suffix,
                    "actual_suffix": actual_suffix,
                    "file_name": safe_filename,
                },
            )

        if len(file_bytes) == 0:
            raise InvalidFileFormatError(
                f"Завантажений файл '{safe_filename}' порожній.",
                context={
                    "expected_suffix": expected_suffix,
                    "file_name": safe_filename,
                },
            )

        target_dir = self._uploads_dir / str(practical.id) / str(student_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        saved_path = target_dir / f"{submission_id}{expected_suffix}"
        saved_path.write_bytes(file_bytes)

        try:
            file_hash = compute_submission_hash(file_path=saved_path)
            extracted_metadata = extract_document_metadata(saved_path)
            grader = GraderFactory.get_grader(practical.format_type)
            report = grader.evaluate(
                file_path=saved_path,
                rules=rules,
                variant_data=variant_data,
            )
        except Exception:
            saved_path.unlink(missing_ok=True)
            raise

        return saved_path, file_hash, extracted_metadata, report

    async def submit_practical(
        self,
        *,
        student: User,
        practical_id: uuid.UUID,
        file_bytes: bytes | None = None,
        filename: str | None = None,
        raw_code: str | None = None,
        payload_error: DomainError | None = None,
        reject_on_plagiarism: bool = False,
    ) -> SubmissionRead:
        """Оркеструє перевірку допуску, оцінювання роботи, антиплагіат та збереження здачі."""
        practical = await self._load_practical_or_404(practical_id)

        await self._quiz_service.ensure_quiz_passed(
            student_id=student.id,
            module_id=practical.module_id,
        )

        if payload_error is not None:
            raise payload_error

        variant_index, _variant_number, variant = resolve_student_variant(
            practical=practical,
            list_number=student.list_number,
        )
        variant_data: dict[str, object] = {
            **variant.model_dump(mode="python"),
            **variant.parameters,
        }
        rules = [GradingRule.model_validate(item) for item in practical.grading_rules]

        submission_id = uuid.uuid4()
        saved_path: Path | None = None
        stored_file_path: str | None = None
        stored_raw_code: str | None = None

        if practical.format_type == PracticalFormat.HTML:
            (
                stored_raw_code,
                file_hash,
                extracted_metadata,
                report,
            ) = self._evaluate_html_submission(
                practical=practical,
                rules=rules,
                variant_data=variant_data,
                raw_code=raw_code,
                file_bytes=file_bytes,
                filename=filename,
            )
        else:
            (
                saved_path,
                file_hash,
                extracted_metadata,
                report,
            ) = self._evaluate_file_submission(
                submission_id=submission_id,
                student_id=student.id,
                practical=practical,
                rules=rules,
                variant_data=variant_data,
                file_bytes=file_bytes,
                filename=filename,
            )
            stored_file_path = saved_path.as_posix()

        plagiarism_result = await check_submission_plagiarism(
            self._db,
            practical_id=practical.id,
            student_id=student.id,
            file_hash=file_hash,
            metadata=extracted_metadata,
        )

        if reject_on_plagiarism and plagiarism_result.is_flagged:
            if saved_path is not None:
                saved_path.unlink(missing_ok=True)
            raise PlagiarismDetectedError(
                plagiarism_result.reason
                or "Виявлено збіг хешу або метаданих роботи з іншим студентом.",
                context={
                    "practical_id": str(practical.id),
                    "matched_submission_id": (
                        str(plagiarism_result.matched_submission_id)
                        if plagiarism_result.matched_submission_id is not None
                        else None
                    ),
                    "matched_student_id": (
                        str(plagiarism_result.matched_student_id)
                        if plagiarism_result.matched_student_id is not None
                        else None
                    ),
                },
            )

        raw_auto_score = Decimal(str(report.total_points)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        auto_score = min(raw_auto_score, practical.max_score)
        final_score = auto_score

        submission = Submission(
            id=submission_id,
            practical_id=practical.id,
            student_id=student.id,
            variant_index=variant_index,
            file_path=stored_file_path,
            raw_code=stored_raw_code,
            file_hash=file_hash,
            extracted_metadata=extracted_metadata.model_dump(
                mode="json",
                exclude_none=True,
            ),
            is_plagiarism_flagged=plagiarism_result.is_flagged,
            plagiarism_reason=plagiarism_result.reason,
            auto_score=auto_score,
            final_score=final_score,
            grading_report=report.model_dump(mode="json"),
            teacher_comment=None,
        )
        self._db.add(submission)
        await self._db.commit()

        loaded_submission = await self._load_submission_or_404(submission.id)
        return serialize_submission(loaded_submission)

    async def update_grading_rules(
        self,
        *,
        practical_id: uuid.UUID,
        payload: GradingRulesUpdateRequest,
    ) -> PracticalTeacherRead:
        """Оновлює JSONB-правила автоперевірки практичної роботи з валідацією сумісності."""
        practical = await self._load_practical_or_404(practical_id)
        expected_prefix = f"{practical.format_type.value}_"

        seen_rule_ids: set[str] = set()
        for rule in payload.grading_rules:
            if rule.id in seen_rule_ids:
                raise DomainError(
                    f"Дублікат ідентифікатора правила автоперевірки: '{rule.id}'.",
                    code="DUPLICATE_RULE_ID",
                    status_code=422,
                    context={"rule_id": rule.id, "practical_id": str(practical.id)},
                )
            seen_rule_ids.add(rule.id)

            if not rule.type.value.startswith(expected_prefix):
                raise DomainError(
                    f"Правило '{rule.id}' типу '{rule.type.value}' не сумісне з форматом "
                    f"практичної роботи '{practical.format_type.value}'.",
                    code="INVALID_RULE_TYPE_FOR_FORMAT",
                    status_code=422,
                    context={
                        "rule_id": rule.id,
                        "rule_type": rule.type.value,
                        "format_type": practical.format_type.value,
                    },
                )

        total_points = sum(rule.points for rule in payload.grading_rules)
        practical.grading_rules = [
            rule.model_dump(mode="json") for rule in payload.grading_rules
        ]
        practical.max_score = Decimal(str(round(total_points, 2))).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        await self._db.commit()
        await self._db.refresh(practical)
        return serialize_practical_teacher(practical)

    async def update_manual_grade(
        self,
        *,
        submission_id: uuid.UUID,
        payload: ManualGradeUpdateRequest,
    ) -> SubmissionRead:
        """Виконує ручне коригування оцінки та коментаря викладача для здачі студента."""
        submission = await self._load_submission_or_404(submission_id)
        max_score = submission.practical.max_score

        final_score_decimal = Decimal(str(payload.final_score)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        if final_score_decimal > max_score:
            raise DomainError(
                f"Підсумковий бал ({final_score_decimal}) не може перевищувати "
                f"максимальний бал практичної роботи ({max_score}).",
                code="SCORE_EXCEEDS_MAX",
                status_code=422,
                context={
                    "final_score": float(final_score_decimal),
                    "max_score": float(max_score),
                    "submission_id": str(submission_id),
                },
            )

        submission.final_score = final_score_decimal
        submission.teacher_comment = payload.teacher_comment

        await self._db.commit()
        refreshed = await self._load_submission_or_404(submission.id)
        return serialize_submission(refreshed)

    async def get_submission(
        self,
        *,
        submission_id: uuid.UUID,
        requester: User,
    ) -> SubmissionRead:
        """Повертає деталі здачі з перевіркою прав доступу (студент бачить лише власні)."""
        submission = await self._load_submission_or_404(submission_id)
        if (
            requester.role == UserRole.STUDENT
            and submission.student_id != requester.id
        ):
            raise DomainError(
                "Доступ до чужої здачі практичної роботи заборонено.",
                code="FORBIDDEN_SUBMISSION_ACCESS",
                status_code=403,
                context={"submission_id": str(submission_id)},
            )
        return serialize_submission(submission)

    async def list_submissions(
        self,
        *,
        requester: User,
        practical_id: uuid.UUID | None = None,
        student_id: uuid.UUID | None = None,
        group_id: uuid.UUID | None = None,
        plagiarism_only: bool = False,
    ) -> list[SubmissionRead]:
        """Повертає список здач практичних робіт із фільтрацією за роллю та параметрами."""
        stmt = (
            select(Submission)
            .options(
                selectinload(Submission.practical)
                .selectinload(Practical.module)
                .selectinload(Module.course),
                selectinload(Submission.student),
            )
            .order_by(Submission.submitted_at.desc())
        )

        if requester.role == UserRole.STUDENT:
            stmt = stmt.where(Submission.student_id == requester.id)
        else:
            if student_id is not None:
                stmt = stmt.where(Submission.student_id == student_id)
            if group_id is not None:
                stmt = stmt.join(User, Submission.student_id == User.id).where(
                    User.group_id == group_id
                )

        if practical_id is not None:
            stmt = stmt.where(Submission.practical_id == practical_id)
        if plagiarism_only:
            stmt = stmt.where(Submission.is_plagiarism_flagged.is_(True))

        result = await self._db.execute(stmt)
        submissions = list(result.scalars().all())
        return [serialize_submission(item) for item in submissions]


__all__ = [
    "SubmissionService",
    "serialize_practical_teacher",
    "serialize_submission",
]
