import os
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.api.deps import get_db
from app.core.config import _BACKEND_ROOT, Settings, settings
from app.main import MEDIA_PDF_SECURITY_CSP, MEDIA_SECURITY_CSP
from app.main import app as fastapi_app
from app.models.course import Course, CourseSlug, Module, Practical
from app.models.progress import QuizAttempt, Submission
from app.models.user import User
from app.services import retention_service
from app.services.retention_service import (
    RETENTION_ADVISORY_LOCK_ID,
    cleanup_superseded_submission_files,
    run_retention_cleanup_once,
)
from tests.conftest import (
    SqliteAsyncSessionAdapter,
    build_sample_docx,
    make_auth_headers,
)

pytestmark = pytest.mark.asyncio


async def _get_student_and_word_practical(
    db_session: SqliteAsyncSessionAdapter,
) -> tuple[User, Module, Practical]:
    """Повертає тестового студента та першу Word-практичну з пройденим тестом-допуском."""
    user_res = await db_session.execute(
        select(User).where(User.email == "student1@kpefk.lcloud.in.ua")
    )
    student = user_res.scalar_one()
    assert isinstance(student, User)

    course_res = await db_session.execute(
        select(Course).where(Course.slug == CourseSlug.WORD)
    )
    course = course_res.scalar_one()
    assert isinstance(course, Course)

    row_res = await db_session.execute(
        select(Module, Practical)
        .join(Practical, Practical.module_id == Module.id)
        .where(Module.course_id == course.id)
        .order_by(Module.order_index.asc())
        .limit(1)
    )
    module, practical = row_res.one()
    assert isinstance(module, Module)
    assert isinstance(practical, Practical)

    db_session.add(
        QuizAttempt(
            student_id=student.id,
            module_id=module.id,
            score_percent=100.0,
            passed=True,
        )
    )
    await db_session.commit()
    return student, module, practical


async def test_uploads_dir_relative_path_is_anchored_to_backend_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Відносний UPLOADS_DIR завжди резолвиться відносно `backend/`, а абсолютний не змінюється."""
    monkeypatch.chdir(tmp_path)

    expected_uploads_dir = (_BACKEND_ROOT / "uploads").resolve()

    default_uploads = Settings().UPLOADS_DIR
    assert default_uploads == expected_uploads_dir

    relative_uploads = Settings(UPLOADS_DIR=Path("uploads")).UPLOADS_DIR
    assert relative_uploads == expected_uploads_dir

    prefixed_uploads = Settings(UPLOADS_DIR=Path("backend/uploads")).UPLOADS_DIR
    assert prefixed_uploads == expected_uploads_dir

    absolute_target = (tmp_path / "custom_abs_uploads").resolve()
    absolute_uploads = Settings(UPLOADS_DIR=absolute_target).UPLOADS_DIR
    assert absolute_uploads == absolute_target


async def test_health_ready_returns_200_when_healthy_and_503_on_uploads_or_db_failure(
    async_client: AsyncClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє liveness `/api/v1/health` та readiness `/api/v1/health/ready` (200 і 503)."""
    liveness_resp = await async_client.get("/api/v1/health")
    assert liveness_resp.status_code == 200
    assert liveness_resp.json()["status"] == "ok"

    ready_resp = await async_client.get("/api/v1/health/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json() == {
        "status": "ready",
        "database": "ok",
        "uploads": "ok",
    }

    # 1. Недоступна директорія UPLOADS_DIR (не існує) -> 503 Service Unavailable
    missing_uploads_dir = tmp_path / "nonexistent_uploads_dir"
    monkeypatch.setattr(settings, "UPLOADS_DIR", missing_uploads_dir)
    missing_resp = await async_client.get("/api/v1/health/ready")
    assert missing_resp.status_code == 503
    missing_body = missing_resp.json()
    assert missing_body["status"] == "not_ready"
    assert missing_body["database"] == "ok"
    assert missing_body["uploads"] == "error"
    assert "uploads" in missing_body["details"]

    # 2. UPLOADS_DIR вказує на файл замість директорії -> 503 Service Unavailable
    file_not_dir = tmp_path / "not_a_directory.txt"
    file_not_dir.write_text("file", encoding="utf-8")
    monkeypatch.setattr(settings, "UPLOADS_DIR", file_not_dir)
    file_resp = await async_client.get("/api/v1/health/ready")
    assert file_resp.status_code == 503
    assert file_resp.json()["uploads"] == "error"

    # 3. Відновлюємо UPLOADS_DIR і перевіряємо збій БД (SELECT 1 кидає виняток) -> 503
    valid_uploads_dir = tmp_path / "valid_uploads"
    valid_uploads_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "UPLOADS_DIR", valid_uploads_dir)

    class _BrokenSession:
        async def execute(self, *_args: object, **_kwargs: object) -> object:
            raise RuntimeError("Simulated database outage")

    previous_override = fastapi_app.dependency_overrides.get(get_db)

    async def _broken_get_db() -> Any:
        yield _BrokenSession()

    fastapi_app.dependency_overrides[get_db] = _broken_get_db
    try:
        db_fail_resp = await async_client.get("/api/v1/health/ready")
    finally:
        if previous_override is not None:
            fastapi_app.dependency_overrides[get_db] = previous_override
        else:
            fastapi_app.dependency_overrides.pop(get_db, None)

    assert db_fail_resp.status_code == 503
    db_fail_body = db_fail_resp.json()
    assert db_fail_body["status"] == "not_ready"
    assert db_fail_body["database"] == "error"
    assert db_fail_body["uploads"] == "ok"
    assert "Simulated database outage" in db_fail_body["details"]["database"]


async def test_media_courses_responses_include_security_headers(
    async_client: AsyncClient,
) -> None:
    """Перевіряє `X-Content-Type-Options: nosniff` і `CSP` для `/media/courses`."""
    image_resp = await async_client.get("/media/courses/access/lectures/1.5.png")
    assert image_resp.status_code == 200
    assert image_resp.headers.get("x-content-type-options") == "nosniff"
    assert image_resp.headers.get("content-security-policy") == MEDIA_SECURITY_CSP

    pdf_resp = await async_client.get("/media/courses/excel/excel-tutorial.pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers.get("x-content-type-options") == "nosniff"
    assert pdf_resp.headers.get("content-type", "").startswith("application/pdf")
    assert pdf_resp.headers.get("content-security-policy") == MEDIA_PDF_SECURITY_CSP
    assert "sandbox" not in (pdf_resp.headers.get("content-security-policy") or "")


async def test_cleanup_superseded_submission_files_keeps_best_and_latest_only(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """З 4 здач (>24 год) залишає файли найкращої та останньої, зберігаючи всі рядки й хеші в БД."""
    student, _module, practical = await _get_student_and_word_practical(db_session)
    headers = make_auth_headers(student.id, student.role)

    created_ids: list[uuid.UUID] = []
    disk_paths: list[Path] = []
    expected_hashes: dict[uuid.UUID, str | None] = {}
    expected_reports: dict[uuid.UUID, dict[str, object]] = {}

    for idx in range(1, 5):
        docx_bytes = build_sample_docx(
            tmp_path / f"attempt_{idx}.docx",
            creator=f"Attempt Author {idx}",
            table_rows=2 + idx,
        ).read_bytes()
        resp = await async_client.post(
            f"/api/v1/practicals/{practical.id}/submit",
            headers=headers,
            files={
                "file": (
                    f"attempt_{idx}.docx",
                    docx_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
        assert resp.status_code == 201
        payload = resp.json()
        sub_id = uuid.UUID(payload["id"])
        created_ids.append(sub_id)
        disk_path = Path(payload["file_path"])
        assert disk_path.is_file()
        disk_paths.append(disk_path)
        expected_hashes[sub_id] = payload["file_hash"]
        expected_reports[sub_id] = payload["grading_report"]

    # Сценарій: 4 здачі старші за 24 години
    # #1 (40 год тому, 5.0 б.) — проміжна чернетка -> видалити файл
    # #2 (36 год тому, 9.5 б.) — НАЙКРАЩА -> залишити файл
    # #3 (30 год тому, 6.0 б.) — проміжна чернетка -> видалити файл
    # #4 (26 год тому, 7.0 б.) — ОСТАННЯ -> залишити файл
    now_utc = datetime.now(UTC)
    schedule = [
        (created_ids[0], now_utc - timedelta(hours=40), Decimal("5.00")),
        (created_ids[1], now_utc - timedelta(hours=36), Decimal("9.50")),
        (created_ids[2], now_utc - timedelta(hours=30), Decimal("6.00")),
        (created_ids[3], now_utc - timedelta(hours=26), Decimal("7.00")),
    ]
    for sub_id, submitted_at, final_score in schedule:
        row = (
            await db_session.execute(select(Submission).where(Submission.id == sub_id))
        ).scalar_one()
        assert isinstance(row, Submission)
        row.submitted_at = submitted_at
        row.final_score = final_score
    await db_session.commit()

    # justified Any: SqliteAsyncSessionAdapter duck-typing for AsyncSession in tests
    typed_session: Any = db_session

    # Перевірка dry-run: виявляє 2 проміжні файли, але нічого не видаляє
    dry_summary = await cleanup_superseded_submission_files(
        typed_session,
        grace_hours=24,
        upload_dir=settings.UPLOADS_DIR,
        dry_run=True,
        now=now_utc,
    )
    assert dry_summary.dry_run is True
    assert dry_summary.inspected_groups == 1
    assert dry_summary.inspected_submissions == 4
    assert dry_summary.cleaned_submissions == 2
    assert dry_summary.deleted_files == 2
    assert all(path.is_file() for path in disk_paths)

    # Реальне очищення проміжних файлів перездач
    summary = await cleanup_superseded_submission_files(
        typed_session,
        grace_hours=24,
        upload_dir=settings.UPLOADS_DIR,
        dry_run=False,
        now=now_utc,
    )
    assert summary.dry_run is False
    assert summary.inspected_groups == 1
    assert summary.inspected_submissions == 4
    assert summary.cleaned_submissions == 2
    assert summary.deleted_files == 2
    assert summary.missing_files == 0
    assert summary.skipped_unsafe_paths == 0

    # Файли проміжних здач #1 та #3 видалено з диска, а #2 (найкраща) і #4 (остання) збережено
    assert not disk_paths[0].exists()
    assert disk_paths[1].is_file()
    assert not disk_paths[2].exists()
    assert disk_paths[3].is_file()

    # Усі 4 рядки Submission залишились у БД разом з оцінками, звітами та file_hash
    all_rows_res = await db_session.execute(
        select(Submission).where(Submission.id.in_(created_ids))
    )
    rows_by_id = {row.id: row for row in all_rows_res.scalars().all()}
    assert len(rows_by_id) == 4

    assert rows_by_id[created_ids[0]].file_path is None
    assert float(rows_by_id[created_ids[0]].final_score) == 5.0
    assert rows_by_id[created_ids[0]].file_hash == expected_hashes[created_ids[0]]
    assert rows_by_id[created_ids[0]].grading_report == expected_reports[created_ids[0]]

    assert rows_by_id[created_ids[1]].file_path is not None
    assert float(rows_by_id[created_ids[1]].final_score) == 9.5
    assert rows_by_id[created_ids[1]].file_hash == expected_hashes[created_ids[1]]

    assert rows_by_id[created_ids[2]].file_path is None
    assert float(rows_by_id[created_ids[2]].final_score) == 6.0
    assert rows_by_id[created_ids[2]].file_hash == expected_hashes[created_ids[2]]
    assert rows_by_id[created_ids[2]].grading_report == expected_reports[created_ids[2]]

    assert rows_by_id[created_ids[3]].file_path is not None
    assert float(rows_by_id[created_ids[3]].final_score) == 7.0
    assert rows_by_id[created_ids[3]].file_hash == expected_hashes[created_ids[3]]


async def test_cleanup_superseded_respects_24h_grace_window(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Проміжні перездачі молодші за 24 години не видаляються з диска."""
    student, _module, practical = await _get_student_and_word_practical(db_session)
    headers = make_auth_headers(student.id, student.role)

    sub_ids: list[uuid.UUID] = []
    paths: list[Path] = []
    for idx in range(1, 4):
        docx_bytes = build_sample_docx(
            tmp_path / f"recent_{idx}.docx",
            creator=f"Recent {idx}",
            table_rows=2 + idx,
        ).read_bytes()
        resp = await async_client.post(
            f"/api/v1/practicals/{practical.id}/submit",
            headers=headers,
            files={
                "file": (
                    f"recent_{idx}.docx",
                    docx_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        sub_ids.append(uuid.UUID(data["id"]))
        paths.append(Path(data["file_path"]))

    now_utc = datetime.now(UTC)
    for sub_id, hours_ago, score in (
        (sub_ids[0], 30, Decimal("9.00")),  # найкраща
        (sub_ids[1], 4, Decimal("4.00")),   # проміжна, але молодша за 24 год -> не чіпати
        (sub_ids[2], 1, Decimal("6.00")),   # остання
    ):
        row = (
            await db_session.execute(select(Submission).where(Submission.id == sub_id))
        ).scalar_one()
        assert isinstance(row, Submission)
        row.submitted_at = now_utc - timedelta(hours=hours_ago)
        row.final_score = score
    await db_session.commit()

    # justified Any: SqliteAsyncSessionAdapter duck-typing for AsyncSession in tests
    typed_session: Any = db_session
    summary = await cleanup_superseded_submission_files(
        typed_session,
        grace_hours=24,
        upload_dir=settings.UPLOADS_DIR,
        dry_run=False,
        now=now_utc,
    )
    assert summary.inspected_groups == 1
    assert summary.cleaned_submissions == 0
    assert summary.deleted_files == 0
    assert all(path.is_file() for path in paths)


async def test_postgresql_advisory_lock_skips_when_already_held(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """На PostgreSQL `run_retention_cleanup_once` пропускає цикл, якщо advisory lock зайнятий."""
    executed_sql: list[tuple[str, dict[str, object] | None]] = []

    class _FakeDialect:
        name = "postgresql"

    class _FakeBind:
        dialect = _FakeDialect()

    class _FakeScalarResult:
        def __init__(self, value: bool) -> None:
            self._value = value

        def scalar_one(self) -> bool:
            return self._value

    class _FakePgSession:
        bind = _FakeBind()

        async def __aenter__(self) -> "_FakePgSession":
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def execute(
            self,
            statement: object,
            params: dict[str, object] | None = None,
        ) -> _FakeScalarResult:
            executed_sql.append((str(statement), params))
            return _FakeScalarResult(False)

    monkeypatch.setattr(retention_service, "AsyncSessionLocal", lambda: _FakePgSession())

    summary = await run_retention_cleanup_once(dry_run=True)
    assert summary.skipped_due_to_lock is True
    assert len(executed_sql) == 1
    assert "pg_try_advisory_lock" in executed_sql[0][0]
    assert executed_sql[0][1] == {"lock_id": RETENTION_ADVISORY_LOCK_ID}
    assert os.getpid() > 0
