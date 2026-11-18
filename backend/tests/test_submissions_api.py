import uuid
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.course import Course, CourseSlug, Module, Practical
from app.models.progress import QuizAttempt
from app.models.user import AcademicGroup, User
from tests.conftest import (
    SqliteAsyncSessionAdapter,
    build_sample_accdb,
    build_sample_docx,
    build_sample_xlsx,
    make_auth_headers,
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
    """Завантажує курс, його перший модуль та практичну роботу за CourseSlug."""
    course_res = await db_session.execute(select(Course).where(Course.slug == slug))
    course = course_res.scalar_one()
    assert isinstance(course, Course)

    module_res = await db_session.execute(
        select(Module).where(Module.course_id == course.id)
    )
    module = module_res.scalar_one()
    assert isinstance(module, Module)

    practical_res = await db_session.execute(
        select(Practical).where(Practical.module_id == module.id)
    )
    practical = practical_res.scalar_one()
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

    # 2. Невдала спроба тесту (1 правильна з 5 = 20% < 70%) не відкриває практичну роботу
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    questions_resp = await async_client.get(
        f"/api/v1/modules/{module.id}/quiz/questions",
        headers=teacher_headers,
    )
    assert questions_resp.status_code == 200
    questions = questions_resp.json()
    assert len(questions) == 5

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
    assert fail_quiz_data["score_percent"] == 20.0
    assert fail_quiz_data["practical_unlocked"] is False

    still_locked_resp = await async_client.post(
        f"/api/v1/practicals/{practical.id}/submit",
        headers=headers,
        json={"raw_code": "<!DOCTYPE html><header><h1>Тест</h1></header><main></main>"},
    )
    assert still_locked_resp.status_code == 403
    assert still_locked_resp.json()["code"] == "QUIZ_NOT_PASSED"

    # 3. Успішна спроба тесту (4 правильні з 5 = 80% >= 70%) розблоковує практичну роботу
    passed_answers = [
        {
            "question_id": q["id"],
            "selected_option_index": (
                q["correct_option_index"]
                if idx < 4
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
    assert pass_quiz_data["score_percent"] == 80.0
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

    # 1. Здача Microsoft Word (.docx)
    _, word_mod, word_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.WORD,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=word_mod.id)
    docx_file = build_sample_docx(tmp_path / "work1.docx")

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
    assert word_sub["grading_report"]["passed_count"] == 6

    # 2. Здача Microsoft Excel (.xlsx)
    _, excel_mod, excel_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.EXCEL,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=excel_mod.id)
    xlsx_file = build_sample_xlsx(tmp_path / "work2.xlsx")

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
    assert excel_sub["grading_report"]["passed_count"] == 4

    # 3. Здача Microsoft Access (.accdb)
    _, access_mod, access_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.ACCESS,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=access_mod.id)
    accdb_file = build_sample_accdb(tmp_path / "work3.accdb")

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
    assert access_sub["grading_report"]["passed_count"] == 4

    # 4. Здача HTML5 (JSON із пісочниці)
    _, html_mod, html_prac = await _get_course_module_and_practical(
        db_session,
        CourseSlug.HTML,
    )
    await _grant_quiz_pass(db_session, student_id=student1.id, module_id=html_mod.id)
    valid_html = """<!DOCTYPE html>
    <html lang="uk">
      <body>
        <header><h1>Розклад занять КН-31</h1></header>
        <main>
          <table>
            <tr><th>Пара</th><th>Предмет</th></tr>
            <tr><td>1</td><td>Інформатика</td></tr>
            <tr><td>2</td><td>Програмування</td></tr>
            <tr><td>3</td><td>Бази даних</td></tr>
          </table>
          <form><input type="text"><button>Надіслати</button></form>
        </main>
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
    assert html_sub["grading_report"]["passed_count"] == 4

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
