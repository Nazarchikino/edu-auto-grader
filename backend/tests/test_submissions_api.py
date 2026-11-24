import io
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote

import openpyxl  # type: ignore[import-untyped]
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from openpyxl.worksheet.worksheet import Worksheet  # type: ignore[import-untyped]
from pydantic import ValidationError
from sqlalchemy import select
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.core.config import Settings, settings
from app.core.security import hash_password
from app.core.upload_utils import read_upload_file_limited
from app.models.course import Course, CourseSlug, Module, Practical
from app.models.progress import QuizAttempt, Submission
from app.models.user import AcademicGroup, User, UserRole
from app.schemas.submission import MAX_HTML_CODE_LENGTH, HtmlSubmissionRequest
from app.services.retention_service import cleanup_expired_submissions
from tests.conftest import (
    SqliteAsyncSessionAdapter,
    build_sample_accdb,
    build_sample_docx,
    make_auth_headers,
    rewrite_openxml_core_metadata,
)

pytestmark = pytest.mark.asyncio


async def _get_user_by_email(
    db_session: SqliteAsyncSessionAdapter,
    email: str,
) -> User:
    """Повертає користувача з тестової БД за його email."""
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    assert isinstance(user, User)
    return user


async def _get_course_module_and_practical(
    db_session: SqliteAsyncSessionAdapter,
    slug: CourseSlug,
) -> tuple[Course, Module, Practical]:
    """Завантажує курс, його перший модуль із практичною та саму практичну роботу."""
    course_res = await db_session.execute(select(Course).where(Course.slug == slug))
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

    return course, module, practical


async def _grant_quiz_pass(
    db_session: SqliteAsyncSessionAdapter,
    *,
    student_id: uuid.UUID,
    module_id: uuid.UUID,
    score_percent: float = 100.0,
) -> None:
    """Фіксує успішне проходження тесту-допуску для студента у тестовій БД."""
    attempt = QuizAttempt(
        student_id=student_id,
        module_id=module_id,
        score_percent=score_percent,
        passed=True,
    )
    db_session.add(attempt)
    await db_session.commit()


async def test_health_check_and_jwt_login_flow(
    async_client: AsyncClient,
) -> None:
    """Перевіряє health-check, JWT-автентифікацію (/auth/login) та профіль (/auth/me)."""
    health_resp = await async_client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "ok"

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "student1@kpefk.lcloud.in.ua",
            "password": "Student123!",
        },
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    me_resp = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "student1@kpefk.lcloud.in.ua"
    assert me_data["role"] == "student"
    assert me_data["list_number"] == 1
    assert me_data["group_code"] == "КН-31"


async def test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє блокування здачі роботи без тесту-допуску (>= 70%) та розрахунок варіанта."""
    student2 = await _get_user_by_email(db_session, "student2@kpefk.lcloud.in.ua")
    headers = make_auth_headers(student2.id, student2.role)
    _course, module, practical = await _get_course_module_and_practical(
        db_session,
        CourseSlug.HTML,
    )

    # 1. До складання тесту доступ до практичної та здачі заблоковано (403 QUIZ_NOT_PASSED)
    get_locked_resp = await async_client.get(
        f"/api/v1/practicals/{practical.id}",
        headers=headers,
    )
    assert get_locked_resp.status_code == 403
    assert get_locked_resp.json()["code"] == "QUIZ_NOT_PASSED"

    submit_locked_resp = await async_client.post(
        f"/api/v1/practicals/{practical.id}/submit",
        headers=headers,
        json={"raw_code": "<!DOCTYPE html><header><h1>Тест</h1></header><main></main>"},
    )
    assert submit_locked_resp.status_code == 403
    assert submit_locked_resp.json()["code"] == "QUIZ_NOT_PASSED"

    # 2. Невдала спроба тесту (1 правильна з 6 = 16.67% < 70%) не відкриває практичну роботу
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    questions_resp = await async_client.get(
        f"/api/v1/modules/{module.id}/quiz/questions",
        headers=teacher_headers,
    )
    assert questions_resp.status_code == 200
    questions = questions_resp.json()
    assert len(questions) == 6

    failed_answers = [
        {
            "question_id": q["id"],
            "selected_option_index": (
                q["correct_option_index"]
                if idx == 0
                else (q["correct_option_index"] + 1) % len(q["options"])
            ),
        }
        for idx, q in enumerate(questions)
    ]
    fail_quiz_resp = await async_client.post(
        f"/api/v1/modules/{module.id}/quiz/submit",
        headers=headers,
        json={"answers": failed_answers},
    )
    assert fail_quiz_resp.status_code == 200
    fail_quiz_data = fail_quiz_resp.json()
    assert fail_quiz_data["passed"] is False
    assert fail_quiz_data["score_percent"] == pytest.approx(16.67, abs=0.01)
    assert fail_quiz_data["practical_unlocked"] is False

    still_locked_resp = await async_client.post(
        f"/api/v1/practicals/{practical.id}/submit",
        headers=headers,
        json={"raw_code": "<!DOCTYPE html><header><h1>Тест</h1></header><main></main>"},
    )
    assert still_locked_resp.status_code == 403
    assert still_locked_resp.json()["code"] == "QUIZ_NOT_PASSED"

    # 3. Успішна спроба тесту (5 правильних з 6 = 83.33% >= 70%) розблоковує практичну роботу
    passed_answers = [
        {
            "question_id": q["id"],
            "selected_option_index": (
                q["correct_option_index"]
                if idx < 5
                else (q["correct_option_index"] + 1) % len(q["options"])
            ),
        }
        for idx, q in enumerate(questions)
    ]
    pass_quiz_resp = await async_client.post(
        f"/api/v1/modules/{module.id}/quiz/submit",
        headers=headers,
        json={"answers": passed_answers},
    )
    assert pass_quiz_resp.status_code == 200
    pass_quiz_data = pass_quiz_resp.json()
    assert pass_quiz_data["passed"] is True
    assert pass_quiz_data["score_percent"] == pytest.approx(83.33, abs=0.01)
    assert pass_quiz_data["practical_unlocked"] is True

    # 4. Перевірка індивідуального варіанта для student2 (list_number=2 -> variant_index=1)
    unlocked_practical_resp = await async_client.get(
        f"/api/v1/practicals/{practical.id}",
        headers=headers,
    )
    assert unlocked_practical_resp.status_code == 200
    practical_data = unlocked_practical_resp.json()
    assert practical_data["variant_index"] == 1
    assert practical_data["variant_number"] == 2


async def test_submit_all_four_practical_formats_via_api(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Інтеграційна перевірка здачі робіт усіх 4 форматів (.docx, .xlsx, .accdb, html)."""
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    headers = make_auth_headers(student1.id, student1.role)

    # 1. Здача Microsoft Word (.docx) — Модуль 1 із word.json
    _, word_mod, word_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.WORD,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=word_mod.id)
    docx_file = build_sample_docx(
        tmp_path / "work1.docx",
        left_mm=20.0,
        right_mm=20.0,
        top_mm=20.0,
        bottom_mm=20.0,
    )

    word_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=headers,
        files={
            "file": (
                "work1.docx",
                docx_file.read_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert word_resp.status_code == 201
    word_sub = word_resp.json()
    assert word_sub["auto_score"] == 10.0
    assert word_sub["final_score"] == 10.0
    assert word_sub["is_plagiarism_flagged"] is False
    assert word_sub["grading_report"]["passed_count"] == 4

    # 2. Здача Microsoft Excel (.xlsx) — Модуль 1 із excel.json
    _, excel_mod, excel_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.EXCEL,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=excel_mod.id)
    xlsx_file = tmp_path / "work2.xlsx"
    wb = openpyxl.Workbook()
    ws_exams = wb.active
    assert isinstance(ws_exams, Worksheet)
    ws_exams.title = "Іспити"
    ws_exams["A1"] = "Прізвище"
    ws_exams["B1"] = "Алгебра"
    ws_budget = wb.create_sheet("Бюджет")
    ws_budget["E10"] = "=SUM(E2:E9)"
    wb.save(str(xlsx_file))
    wb.close()
    rewrite_openxml_core_metadata(
        xlsx_file,
        creator="Student One",
        last_modified_by="Student One",
        created="2026-11-18T11:00:00Z",
        modified="2026-11-18T11:30:00Z",
        revision="1",
    )

    excel_resp = await async_client.post(
        f"/api/v1/practicals/{excel_prac.id}/submit",
        headers=headers,
        files={
            "file": (
                "work2.xlsx",
                xlsx_file.read_bytes(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert excel_resp.status_code == 201
    excel_sub = excel_resp.json()
    assert excel_sub["auto_score"] == 10.0
    assert excel_sub["final_score"] == 10.0
    assert excel_sub["is_plagiarism_flagged"] is False
    assert excel_sub["grading_report"]["passed_count"] == 3

    # 3. Здача Microsoft Access (.accdb) — Модуль 3 із access.json (таблиця 'Друзі')
    _, access_mod, access_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.ACCESS,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=access_mod.id)
    accdb_file = build_sample_accdb(
        tmp_path / "work3.accdb",
        tables={
            "Друзі": [
                ("№ п/п", "AUTONUMBER"),
                ("Прізвище", "SHORT TEXT"),
                ("Ім'я", "SHORT TEXT"),
                ("По батькові", "SHORT TEXT"),
                ("Адреса", "SHORT TEXT"),
                ("Індекс", "LONG"),
                ("Телефон", "SHORT TEXT"),
                ("Захоплення", "SHORT TEXT"),
                ("Ел. пошта", "HYPERLINK"),
                ("Дата народження", "DATE/TIME"),
                ("Сімейний стан", "YES/NO"),
            ]
        },
    )

    access_resp = await async_client.post(
        f"/api/v1/practicals/{access_prac.id}/submit",
        headers=headers,
        files={
            "file": (
                "work3.accdb",
                accdb_file.read_bytes(),
                "application/octet-stream",
            )
        },
    )
    assert access_resp.status_code == 201
    access_sub = access_resp.json()
    assert access_sub["auto_score"] == 10.0
    assert access_sub["final_score"] == 10.0
    assert access_sub["is_plagiarism_flagged"] is False
    assert access_sub["grading_report"]["passed_count"] == 17

    # 4. Здача HTML5 (JSON із пісочниці) — Модуль 1 із html.json
    _, html_mod, html_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.HTML,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=html_mod.id)
    valid_html = """<!DOCTYPE html>
    <html lang="uk">
      <head>
        <meta charset="UTF-8">
        <title>Візитівка студента КН-31</title>
      </head>
      <body>
        <h1>Профіль студента</h1>
        <h2>Навчання</h2>
        <p>Вивчаю <strong>вебтехнології</strong> та основи HTML5.</p>
        <h2>Інтереси</h2>
        <p>Цікавлюся <em>семантичною версткою</em> та доступністю.</p>
        <p>Регулярно виконую практичні роботи коледжу.</p>
        <blockquote>Якісна розмітка — основа сучасного вебу.</blockquote>
      </body>
    </html>
    """

    html_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/submit",
        headers=headers,
        json={"raw_code": valid_html},
    )
    assert html_resp.status_code == 201
    html_sub = html_resp.json()
    assert html_sub["auto_score"] == 10.0
    assert html_sub["final_score"] == 10.0
    assert html_sub["is_plagiarism_flagged"] is False
    assert html_sub["grading_report"]["passed_count"] == 9

    # 5. Перевірка заліковки студента (/submissions/me)
    my_subs_resp = await async_client.get("/api/v1/submissions/me", headers=headers)
    assert my_subs_resp.status_code == 200
    assert len(my_subs_resp.json()) == 4


async def test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє маркування is_plagiarism_flagged=True при збігу SHA-256 або core.xml."""
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    student2 = await _get_user_by_email(db_session, "student2@kpefk.lcloud.in.ua")
    student3 = await _get_user_by_email(db_session, "student3@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")

    _, word_mod, word_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.WORD,
    )
    for st in (student1, student2, student3):
        await _grant_quiz_pass(db_session, student_id=st.id, module_id=word_mod.id)

    # 1. Студент 1 здає оригінальний документ .docx
    original_docx = build_sample_docx(
        tmp_path / "student1.docx",
        creator="Бондаренко Ірина Василівна",
        created_iso="2026-11-18T07:45:00Z",
        modified_iso="2026-11-18T08:30:00Z",
    )
    sub1_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=make_auth_headers(student1.id, student1.role),
        files={
            "file": (
                "student1.docx",
                original_docx.read_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert sub1_resp.status_code == 201
    sub1_data = sub1_resp.json()
    assert sub1_data["is_plagiarism_flagged"] is False
    assert sub1_data["plagiarism_reason"] is None

    # 2. Повторна здача тим самим студентом 1 НЕ маркується як плагіат
    resub1_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=make_auth_headers(student1.id, student1.role),
        files={
            "file": (
                "student1_resubmit.docx",
                original_docx.read_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert resub1_resp.status_code == 201
    assert resub1_resp.json()["is_plagiarism_flagged"] is False

    # 3. Студент 2 завантажує той самий файл (збіг SHA-256)
    sub2_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=make_auth_headers(student2.id, student2.role),
        files={
            "file": (
                "student2_copy.docx",
                original_docx.read_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert sub2_resp.status_code == 201
    sub2_data = sub2_resp.json()
    assert sub2_data["is_plagiarism_flagged"] is True
    assert sub2_data["plagiarism_reason"] is not None
    assert "SHA-256" in sub2_data["plagiarism_reason"]

    # 4. Студент 3 змінює вміст файлу (інший SHA-256), але залишає час створення у docProps/core.xml
    modified_content_docx = build_sample_docx(
        tmp_path / "student3_meta_clone.docx",
        table_rows=6,
        table_cols=4,
        creator="Шевченко Максим",
        created_iso="2026-11-18T07:45:00Z",
        modified_iso="2026-11-18T16:15:00Z",
    )
    sub3_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=make_auth_headers(student3.id, student3.role),
        files={
            "file": (
                "student3_meta_clone.docx",
                modified_content_docx.read_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert sub3_resp.status_code == 201
    sub3_data = sub3_resp.json()
    assert sub3_data["file_hash"] != sub1_data["file_hash"]
    assert sub3_data["is_plagiarism_flagged"] is True
    assert sub3_data["plagiarism_reason"] is not None
    assert "docProps/core.xml" in sub3_data["plagiarism_reason"]

    # 5. Викладач отримує відфільтрований список робіт із підозрою на плагіат
    flagged_list_resp = await async_client.get(
        "/api/v1/submissions?plagiarism_only=true",
        headers=make_auth_headers(teacher.id, teacher.role),
    )
    assert flagged_list_resp.status_code == 200
    flagged_items = flagged_list_resp.json()
    assert len(flagged_items) == 2
    assert all(item["is_plagiarism_flagged"] is True for item in flagged_items)


async def test_teacher_update_rules_manual_grade_and_group_export(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє оновлення правил, ручне оцінювання та експорт відомостей (.xlsx/.pdf)."""
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    student_headers = make_auth_headers(student1.id, student1.role)
    teacher_headers = make_auth_headers(teacher.id, teacher.role)

    _, html_mod, html_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.HTML,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=html_mod.id)

    # 1. Студент не має права змінювати правила автоперевірки (403 FORBIDDEN)
    new_rules_payload = {
        "grading_rules": [
            {
                "id": "custom_html_1",
                "type": "html_tag_exists",
                "target": "header > h1",
                "expected": "true",
                "points": 5.0,
                "description": "Наявний заголовок у шапці",
            },
            {
                "id": "custom_html_2",
                "type": "html_tag_exists",
                "target": "main",
                "expected": "true",
                "points": 5.0,
                "description": "Наявний блок main",
            },
        ]
    }
    forbidden_rules_resp = await async_client.put(
        f"/api/v1/practicals/{html_prac.id}/rules",
        headers=student_headers,
        json=new_rules_payload,
    )
    assert forbidden_rules_resp.status_code == 403

    # 2. Викладач оновлює правила автоперевірки
    update_rules_resp = await async_client.put(
        f"/api/v1/practicals/{html_prac.id}/rules",
        headers=teacher_headers,
        json=new_rules_payload,
    )
    assert update_rules_resp.status_code == 200
    updated_prac = update_rules_resp.json()
    assert updated_prac["max_score"] == 10.0
    assert len(updated_prac["grading_rules"]) == 2

    # 3. Студент здає HTML-код, який виконує лише перше правило (5.0 з 10.0 балів)
    sub_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/submit",
        headers=student_headers,
        json={"raw_code": "<!DOCTYPE html><header><h1>Робота</h1></header>"},
    )
    assert sub_resp.status_code == 201
    sub_data = sub_resp.json()
    assert sub_data["auto_score"] == 5.0
    assert sub_data["final_score"] == 5.0

    # 4. Викладач вручну коригує оцінку та залишає коментар (PATCH /submissions/{id}/grade)
    grade_resp = await async_client.patch(
        f"/api/v1/submissions/{sub_data['id']}/grade",
        headers=teacher_headers,
        json={
            "final_score": 8.5,
            "teacher_comment": "Зараховано додаткові бали після захисту роботи.",
        },
    )
    assert grade_resp.status_code == 200
    graded_data = grade_resp.json()
    assert graded_data["auto_score"] == 5.0
    assert graded_data["final_score"] == 8.5
    assert (
        graded_data["teacher_comment"]
        == "Зараховано додаткові бали після захисту роботи."
    )

    # 5. Перевірка журналу групи та експорту у форматах .xlsx і .pdf
    group_res = await db_session.execute(
        select(AcademicGroup).where(AcademicGroup.code == "КН-31")
    )
    group = group_res.scalar_one()
    assert isinstance(group, AcademicGroup)

    journal_resp = await async_client.get(
        f"/api/v1/analytics/groups/{group.id}/journal",
        headers=teacher_headers,
    )
    assert journal_resp.status_code == 200
    journal_data = journal_resp.json()
    assert journal_data["group_code"] == "КН-31"
    assert len(journal_data["rows"]) == 3
    assert len(journal_data["error_stats"]) >= 1

    xlsx_export_resp = await async_client.get(
        f"/api/v1/analytics/groups/{group.id}/export?format=xlsx",
        headers=teacher_headers,
    )
    assert xlsx_export_resp.status_code == 200
    assert (
        xlsx_export_resp.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert xlsx_export_resp.content.startswith(b"PK")

    pdf_export_resp = await async_client.get(
        f"/api/v1/analytics/groups/{group.id}/export?format=pdf",
        headers=teacher_headers,
    )
    assert pdf_export_resp.status_code == 200
    assert pdf_export_resp.headers["content-type"] == "application/pdf"
    assert pdf_export_resp.content.startswith(b"%PDF-")


async def test_download_submissions_by_course_teacher_and_admin_with_headers_and_content(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє завантаження .docx/.xlsx/.html викладачем курсу та адміном (200 OK)."""
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")

    student_headers = make_auth_headers(student1.id, student1.role)
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    admin_headers = make_auth_headers(admin.id, admin.role)

    # 1. Здача Word (.docx)
    _, word_mod, word_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.WORD,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=word_mod.id)
    docx_bytes = build_sample_docx(
        tmp_path / "download_test.docx",
        left_mm=20.0,
        right_mm=20.0,
        top_mm=20.0,
        bottom_mm=20.0,
    ).read_bytes()

    word_submit = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=student_headers,
        files={
            "file": (
                "download_test.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert word_submit.status_code == 201
    word_sub = word_submit.json()
    assert word_sub["is_file_available"] is True
    assert word_sub["file_expires_at"] is not None
    submitted_dt = datetime.fromisoformat(word_sub["submitted_at"])
    expires_dt = datetime.fromisoformat(word_sub["file_expires_at"])
    assert expires_dt - submitted_dt == timedelta(
        days=settings.SUBMISSION_FILE_RETENTION_DAYS
    )

    # 2. Здача Excel (.xlsx)
    _, excel_mod, excel_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.EXCEL,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=excel_mod.id)
    xlsx_path = tmp_path / "download_test.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    assert isinstance(ws, Worksheet)
    ws.title = "Іспити"
    ws["A1"] = "Прізвище"
    ws_budget = wb.create_sheet("Бюджет")
    ws_budget["E10"] = "=SUM(E2:E9)"
    wb.save(str(xlsx_path))
    wb.close()
    xlsx_bytes = xlsx_path.read_bytes()

    excel_submit = await async_client.post(
        f"/api/v1/practicals/{excel_prac.id}/submit",
        headers=student_headers,
        files={
            "file": (
                "download_test.xlsx",
                xlsx_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert excel_submit.status_code == 201
    excel_sub = excel_submit.json()
    assert excel_sub["is_file_available"] is True
    assert excel_sub["file_expires_at"] is not None

    # 3. Здача HTML5 (raw_code)
    _, html_mod, html_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.HTML,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=html_mod.id)
    raw_html = "<!DOCTYPE html><html lang='uk'><body><h1>Звіт студента</h1></body></html>"
    html_submit = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/submit",
        headers=student_headers,
        json={"raw_code": raw_html},
    )
    assert html_submit.status_code == 201
    html_sub = html_submit.json()
    assert html_sub["is_file_available"] is True
    assert html_sub["file_expires_at"] is not None

    # 4. Викладач курсу завантажує .docx, .xlsx та .html
    for sub_id, expected_bytes, expected_mime, expected_utf8_name, expected_ascii_name in (
        (
            word_sub["id"],
            docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "КН-31_Бондаренко_word_v1.docx",
            "KN-31_Bondarenko_word_v1.docx",
        ),
        (
            excel_sub["id"],
            xlsx_bytes,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "КН-31_Бондаренко_excel_v1.xlsx",
            "KN-31_Bondarenko_excel_v1.xlsx",
        ),
        (
            html_sub["id"],
            raw_html.encode("utf-8"),
            "text/html; charset=utf-8",
            "КН-31_Бондаренко_html_v1.html",
            "KN-31_Bondarenko_html_v1.html",
        ),
    ):
        teacher_dl = await async_client.get(
            f"/api/v1/submissions/{sub_id}/download",
            headers=teacher_headers,
        )
        assert teacher_dl.status_code == 200
        assert teacher_dl.headers["content-type"] == expected_mime
        disposition = teacher_dl.headers["content-disposition"]
        assert f'filename="{expected_ascii_name}"' in disposition
        assert f"filename*=UTF-8''{quote(expected_utf8_name, safe='')}" in disposition
        assert teacher_dl.content == expected_bytes

        # Адміністратор має доступ до завантаження будь-якого курсу
        admin_dl = await async_client.get(
            f"/api/v1/submissions/{sub_id}/download",
            headers=admin_headers,
        )
        assert admin_dl.status_code == 200
        assert admin_dl.content == expected_bytes

    # 5. Безпечний fallback імені файлу, якщо у студента не вказана академічна група
    student1.group_id = None
    await db_session.commit()
    no_group_dl = await async_client.get(
        f"/api/v1/submissions/{word_sub['id']}/download",
        headers=teacher_headers,
    )
    assert no_group_dl.status_code == 200
    assert 'filename="no_group_Bondarenko_word_v1.docx"' in no_group_dl.headers[
        "content-disposition"
    ]


async def test_download_submission_forbidden_for_other_teacher_and_students(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє заборону завантаження (403) чужому викладачу та студентам."""
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    student2 = await _get_user_by_email(db_session, "student2@kpefk.lcloud.in.ua")

    other_teacher = User(
        email="other.teacher@kpefk.lcloud.in.ua",
        password_hash=hash_password("Teacher123!"),
        full_name="Інший Викладач Петрович",
        role=UserRole.TEACHER,
    )
    db_session.add(other_teacher)
    await db_session.commit()

    _, word_mod, word_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.WORD,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=word_mod.id)
    docx_bytes = build_sample_docx(tmp_path / "rbac_test.docx").read_bytes()

    submit_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=make_auth_headers(student1.id, student1.role),
        files={
            "file": (
                "rbac_test.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert submit_resp.status_code == 201
    submission_id = submit_resp.json()["id"]

    # Чужий викладач (не власник курсу) -> 403 FORBIDDEN_SUBMISSION_DOWNLOAD
    other_teacher_resp = await async_client.get(
        f"/api/v1/submissions/{submission_id}/download",
        headers=make_auth_headers(other_teacher.id, other_teacher.role),
    )
    assert other_teacher_resp.status_code == 403
    assert other_teacher_resp.json()["code"] == "FORBIDDEN_SUBMISSION_DOWNLOAD"

    # Студент-автор та інший студент -> 403 FORBIDDEN
    for student in (student1, student2):
        student_resp = await async_client.get(
            f"/api/v1/submissions/{submission_id}/download",
            headers=make_auth_headers(student.id, student.role),
        )
        assert student_resp.status_code == 403
        assert student_resp.json()["code"] == "FORBIDDEN"


async def test_retention_cleanup_purges_expired_files_keeps_grades_and_ignores_fresh(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє 90-денне автоочищення, збереження оцінок/звітів/хешів і недоторканість свіжих."""
    with pytest.raises(ValidationError):
        Settings(SUBMISSION_FILE_RETENTION_DAYS=0)

    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    student2 = await _get_user_by_email(db_session, "student2@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")

    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    st1_headers = make_auth_headers(student1.id, student1.role)
    st2_headers = make_auth_headers(student2.id, student2.role)

    _, word_mod, word_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.WORD,
    )
    _, html_mod, html_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.HTML,
    )
    for st in (student1, student2):
        await _grant_quiz_pass(db_session, student_id=st.id, module_id=word_mod.id)
        await _grant_quiz_pass(db_session, student_id=st.id, module_id=html_mod.id)

    # 1. Створюємо здачі, які стануть простроченими (91 день) — .docx та .html
    expired_docx_bytes = build_sample_docx(
        tmp_path / "expired.docx",
        creator="Expired Author",
        created_iso="2026-08-01T10:00:00Z",
    ).read_bytes()
    exp_docx_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=st1_headers,
        files={
            "file": (
                "expired.docx",
                expired_docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert exp_docx_resp.status_code == 201
    exp_docx_data = exp_docx_resp.json()
    exp_docx_id = uuid.UUID(exp_docx_data["id"])
    exp_docx_disk_path = Path(exp_docx_data["file_path"])
    assert exp_docx_disk_path.is_file()

    # Викладач додає ручну оцінку та коментар, щоб переконатися у їх збереженні
    grade_patch = await async_client.patch(
        f"/api/v1/submissions/{exp_docx_id}/grade",
        headers=teacher_headers,
        json={"final_score": 9.5, "teacher_comment": "Оцінка має зберегтися після 90 днів"},
    )
    assert grade_patch.status_code == 200
    expected_docx_hash = exp_docx_data["file_hash"]
    expected_docx_report = exp_docx_data["grading_report"]

    exp_html_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/submit",
        headers=st1_headers,
        json={"raw_code": "<!DOCTYPE html><body><h1>Стара HTML-робота</h1></body>"},
    )
    assert exp_html_resp.status_code == 201
    exp_html_data = exp_html_resp.json()
    exp_html_id = uuid.UUID(exp_html_data["id"])
    expected_html_hash = exp_html_data["file_hash"]

    # 2. Створюємо свіжі здачі (10 днів тому) — .docx та .html
    fresh_docx_bytes = build_sample_docx(
        tmp_path / "fresh.docx",
        creator="Fresh Author",
        created_iso="2026-11-10T10:00:00Z",
    ).read_bytes()
    fresh_docx_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=st2_headers,
        files={
            "file": (
                "fresh.docx",
                fresh_docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert fresh_docx_resp.status_code == 201
    fresh_docx_data = fresh_docx_resp.json()
    fresh_docx_id = uuid.UUID(fresh_docx_data["id"])
    fresh_docx_disk_path = Path(fresh_docx_data["file_path"])
    assert fresh_docx_disk_path.is_file()

    fresh_html_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/submit",
        headers=st2_headers,
        json={"raw_code": "<!DOCTYPE html><body><h1>Свіжа HTML-робота</h1></body>"},
    )
    assert fresh_html_resp.status_code == 201
    fresh_html_id = uuid.UUID(fresh_html_resp.json()["id"])

    # Зміщуємо submitted_at: 91 день тому для прострочених, 10 днів тому для свіжих
    now_utc = datetime.now(UTC)
    expired_time = now_utc - timedelta(days=91)
    fresh_time = now_utc - timedelta(days=10)

    for sub_id, target_dt in (
        (exp_docx_id, expired_time),
        (exp_html_id, expired_time),
        (fresh_docx_id, fresh_time),
        (fresh_html_id, fresh_time),
    ):
        sub_obj = (
            await db_session.execute(select(Submission).where(Submission.id == sub_id))
        ).scalar_one()
        assert isinstance(sub_obj, Submission)
        sub_obj.submitted_at = target_dt
    await db_session.commit()

    # justified Any: SqliteAsyncSessionAdapter duck-typing for AsyncSession in tests
    typed_session: Any = db_session

    # 3. Перевіряємо dry_run: нічого не видаляє і не змінює БД
    dry_summary = await cleanup_expired_submissions(
        typed_session,
        retention_days=90,
        upload_dir=settings.UPLOADS_DIR,
        dry_run=True,
        now=now_utc,
    )
    assert dry_summary.dry_run is True
    assert dry_summary.inspected_submissions == 2
    assert dry_summary.cleaned_submissions == 2
    assert dry_summary.deleted_files == 1
    assert dry_summary.cleared_raw_code == 1
    assert exp_docx_disk_path.is_file()

    # 4. Реальний запуск автоочищення (90 днів)
    summary = await cleanup_expired_submissions(
        typed_session,
        retention_days=90,
        upload_dir=settings.UPLOADS_DIR,
        dry_run=False,
        now=now_utc,
    )
    assert summary.dry_run is False
    assert summary.inspected_submissions == 2
    assert summary.cleaned_submissions == 2
    assert summary.deleted_files == 1
    assert summary.missing_files == 0
    assert summary.cleared_raw_code == 1
    assert summary.skipped_unsafe_paths == 0

    # 5. Прострочені здачі: файл і raw_code очищено, але запис, оцінки, звіт і хеш збережені
    assert not exp_docx_disk_path.exists()

    exp_docx_detail = await async_client.get(
        f"/api/v1/submissions/{exp_docx_id}",
        headers=teacher_headers,
    )
    assert exp_docx_detail.status_code == 200
    exp_docx_after = exp_docx_detail.json()
    assert exp_docx_after["file_path"] is None
    assert exp_docx_after["raw_code"] is None
    assert exp_docx_after["is_file_available"] is False
    assert exp_docx_after["file_expires_at"] is None
    assert exp_docx_after["final_score"] == 9.5
    assert exp_docx_after["teacher_comment"] == "Оцінка має зберегтися після 90 днів"
    assert exp_docx_after["file_hash"] == expected_docx_hash
    assert exp_docx_after["grading_report"] == expected_docx_report

    exp_html_detail = await async_client.get(
        f"/api/v1/submissions/{exp_html_id}",
        headers=teacher_headers,
    )
    assert exp_html_detail.status_code == 200
    exp_html_after = exp_html_detail.json()
    assert exp_html_after["raw_code"] is None
    assert exp_html_after["is_file_available"] is False
    assert exp_html_after["file_expires_at"] is None
    assert exp_html_after["file_hash"] == expected_html_hash

    # Завантаження очищених робіт повертає 404 зі зрозумілим українським повідомленням
    for purged_id in (exp_docx_id, exp_html_id):
        purged_dl = await async_client.get(
            f"/api/v1/submissions/{purged_id}/download",
            headers=teacher_headers,
        )
        assert purged_dl.status_code == 404
        assert purged_dl.json()["code"] == "SUBMISSION_FILE_NOT_FOUND"
        assert "видалено за терміном зберігання" in purged_dl.json()["detail"]

    # 6. Свіжі здачі (< 90 днів) залишилися повністю недоторканими
    assert fresh_docx_disk_path.is_file()
    for fresh_id in (fresh_docx_id, fresh_html_id):
        fresh_detail = await async_client.get(
            f"/api/v1/submissions/{fresh_id}",
            headers=teacher_headers,
        )
        assert fresh_detail.status_code == 200
        assert fresh_detail.json()["is_file_available"] is True
        assert fresh_detail.json()["file_expires_at"] is not None

        fresh_dl = await async_client.get(
            f"/api/v1/submissions/{fresh_id}/download",
            headers=teacher_headers,
        )
        assert fresh_dl.status_code == 200


async def test_submission_download_and_retention_block_path_traversal(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє захист від Path Traversal при завантаженні та автоочищенні файлів."""
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")

    _, word_mod, word_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.WORD,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=word_mod.id)
    docx_bytes = build_sample_docx(tmp_path / "legit.docx").read_bytes()

    submit_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=make_auth_headers(student1.id, student1.role),
        files={
            "file": (
                "legit.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert submit_resp.status_code == 201
    sub_id = uuid.UUID(submit_resp.json()["id"])

    # Створюємо файл поза UPLOADS_DIR і підміняємо file_path на шлях поза межами
    outside_secret = tmp_path / "secret_outside_uploads.docx"
    outside_secret.write_bytes(b"sensitive-data")

    sub_row = (
        await db_session.execute(select(Submission).where(Submission.id == sub_id))
    ).scalar_one()
    assert isinstance(sub_row, Submission)
    sub_row.file_path = str(outside_secret)
    sub_row.submitted_at = datetime.now(UTC) - timedelta(days=95)
    await db_session.commit()

    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    detail_resp = await async_client.get(
        f"/api/v1/submissions/{sub_id}",
        headers=teacher_headers,
    )
    assert detail_resp.status_code == 200
    assert detail_resp.json()["is_file_available"] is False
    assert detail_resp.json()["file_expires_at"] is None

    dl_resp = await async_client.get(
        f"/api/v1/submissions/{sub_id}/download",
        headers=teacher_headers,
    )
    assert dl_resp.status_code == 404
    assert dl_resp.json()["code"] == "SUBMISSION_FILE_NOT_FOUND"

    # Автоочищення обнуляє небезпечний file_path у БД, але НЕ видаляє сторонній файл
    typed_session: Any = db_session
    cleanup_summary = await cleanup_expired_submissions(
        typed_session,
        retention_days=90,
        upload_dir=settings.UPLOADS_DIR,
    )
    assert cleanup_summary.skipped_unsafe_paths == 1
    assert outside_secret.is_file()


async def test_lifespan_starts_and_cancels_retention_background_task(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє коректний старт і зупинку фонової задачі автоочищення у lifespan."""
    import asyncio

    from app import main as main_module

    started_event = asyncio.Event()
    cancelled_flag = False

    async def _fake_periodic_cleanup() -> None:
        nonlocal cancelled_flag
        started_event.set()
        try:
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            cancelled_flag = True
            raise

    monkeypatch.setattr(settings, "ENABLE_RETENTION_CLEANUP_TASK", True)
    monkeypatch.setattr(
        main_module,
        "run_periodic_retention_cleanup",
        _fake_periodic_cleanup,
    )

    async with main_module.lifespan(main_module.app):
        await asyncio.wait_for(started_event.wait(), timeout=2.0)

    assert cancelled_flag is True


async def test_read_upload_file_limited_stops_reading_chunks_early() -> None:
    """Перевіряє, що read_upload_file_limited читає чанками та зупиняється при перевищенні."""

    class _CountingUploadFile(StarletteUploadFile):
        def __init__(self, payload: bytes) -> None:
            super().__init__(file=io.BytesIO(payload), filename="large.docx")
            self.read_calls = 0

        async def read(self, size: int = -1) -> bytes:
            self.read_calls += 1
            return await super().read(size)

    payload = b"x" * (512 * 1024)
    upload = _CountingUploadFile(payload)
    try:
        with pytest.raises(HTTPException) as exc_info:
            await read_upload_file_limited(
                upload,
                max_bytes=128 * 1024,
                chunk_size=65_536,
            )
    finally:
        await upload.close()

    assert exc_info.value.status_code == 413
    assert "МБ" in str(exc_info.value.detail)
    # 2 чанки по 64 КБ = 128 КБ (у межах ліміту), 3-й чанк перевищує ліміт -> раннє відсікання
    assert upload.read_calls == 3


async def test_submit_practical_returns_413_when_file_exceeds_size_limit(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє HTTP 413 при перевищенні ліміту розміру для Office та Access практичних."""
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    headers = make_auth_headers(student1.id, student1.role)

    _, word_mod, word_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.WORD,
    )
    _, access_mod, access_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.ACCESS,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=word_mod.id)
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=access_mod.id)

    monkeypatch.setattr(settings, "MAX_OFFICE_UPLOAD_BYTES", 1024)
    monkeypatch.setattr(settings, "MAX_ACCDB_UPLOAD_BYTES", 2048)

    oversized_docx = b"A" * 2048
    word_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/submit",
        headers=headers,
        files={
            "file": (
                "too_big.docx",
                oversized_docx,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert word_resp.status_code == 413
    assert "МБ" in word_resp.json()["detail"]

    # .accdb використовує окремий ліміт MAX_ACCDB_UPLOAD_BYTES (2048 > 1024)
    oversized_accdb = b"B" * 3072
    accdb_too_big_resp = await async_client.post(
        f"/api/v1/practicals/{access_prac.id}/submit",
        headers=headers,
        files={
            "file": (
                "too_big.accdb",
                oversized_accdb,
                "application/octet-stream",
            )
        },
    )
    assert accdb_too_big_resp.status_code == 413
    assert "МБ" in accdb_too_big_resp.json()["detail"]

    # Валідний .accdb розміром > MAX_OFFICE_UPLOAD_BYTES, але <= MAX_ACCDB_UPLOAD_BYTES приймається
    sample_accdb = build_sample_accdb(tmp_path / "valid_limit.accdb").read_bytes()
    monkeypatch.setattr(settings, "MAX_OFFICE_UPLOAD_BYTES", 1024)
    monkeypatch.setattr(settings, "MAX_ACCDB_UPLOAD_BYTES", len(sample_accdb) + 512)
    accdb_ok_resp = await async_client.post(
        f"/api/v1/practicals/{access_prac.id}/submit",
        headers=headers,
        files={
            "file": (
                "valid_limit.accdb",
                sample_accdb,
                "application/octet-stream",
            )
        },
    )
    assert accdb_ok_resp.status_code == 201


async def test_submit_html_returns_422_when_raw_code_exceeds_max_length(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє HTTP 422 при відправці HTML-коду довжиною понад 250 000 символів."""
    oversized_html = "a" * (MAX_HTML_CODE_LENGTH + 1)

    with pytest.raises(ValidationError):
        HtmlSubmissionRequest(raw_code=oversized_html)

    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    headers = make_auth_headers(student1.id, student1.role)
    _, html_mod, html_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.HTML,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=html_mod.id)

    json_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/submit",
        headers=headers,
        json={"raw_code": oversized_html},
    )
    assert json_resp.status_code == 422
    assert json_resp.json()["code"] == "RAW_CODE_TOO_LONG"

    form_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/submit",
        headers=headers,
        data={"raw_code": oversized_html},
    )
    assert form_resp.status_code == 422
    assert form_resp.json()["code"] == "RAW_CODE_TOO_LONG"
