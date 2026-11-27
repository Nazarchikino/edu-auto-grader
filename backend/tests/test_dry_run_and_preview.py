import copy
import json
import uuid
from decimal import Decimal
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.core.config import settings
from app.core.security import hash_password
from app.models.course import Course, CourseSlug, Module, Practical
from app.models.progress import QuizAttempt, Submission
from app.models.user import User, UserRole
from app.schemas.submission import MAX_HTML_CODE_LENGTH
from tests.conftest import (
    SqliteAsyncSessionAdapter,
    build_sample_docx,
    build_sample_xlsx,
    make_auth_headers,
)

pytestmark = pytest.mark.asyncio

EXPECTED_FORBIDDEN_DETAIL = "Недостатньо прав: цей курс закріплено за іншим викладачем."


async def _get_user_by_email(
    db_session: SqliteAsyncSessionAdapter,
    email: str,
) -> User:
    """Повертає користувача з тестової БД за його email."""
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    assert isinstance(user, User)
    return user


async def _create_other_teacher(
    db_session: SqliteAsyncSessionAdapter,
    *,
    email: str = "other.teacher.dryrun@kpefk.lcloud.in.ua",
) -> User:
    """Створює стороннього викладача, який не є власником жодного курсу."""
    other_teacher = User(
        email=email,
        password_hash=hash_password("Teacher123!"),
        full_name="Сторонній Викладач Олексійович",
        role=UserRole.TEACHER,
    )
    db_session.add(other_teacher)
    await db_session.commit()
    return other_teacher


async def _get_module_and_practical_by_order(
    db_session: SqliteAsyncSessionAdapter,
    slug: CourseSlug,
    order_index: int,
) -> tuple[Module, Practical]:
    """Повертає модуль і практичну роботу курсу за порядковим номером модуля."""
    row = (
        await db_session.execute(
            select(Module, Practical)
            .join(Course, Course.id == Module.course_id)
            .join(Practical, Practical.module_id == Module.id)
            .where(Course.slug == slug, Module.order_index == order_index)
            .limit(1)
        )
    ).one()
    module, practical = row
    assert isinstance(module, Module)
    assert isinstance(practical, Practical)
    return module, practical


async def _count_submissions(db_session: SqliteAsyncSessionAdapter) -> int:
    """Повертає загальну кількість рядків Submission у тестовій БД."""
    result = await db_session.execute(select(func.count(Submission.id)))
    return int(result.scalar_one())


async def _count_quiz_attempts(db_session: SqliteAsyncSessionAdapter) -> int:
    """Повертає загальну кількість рядків QuizAttempt у тестовій БД."""
    result = await db_session.execute(select(func.count(QuizAttempt.id)))
    return int(result.scalar_one())


def _list_uploaded_files() -> list[Path]:
    """Повертає всі фізичні файли, що існують у директорії UPLOADS_DIR."""
    if not settings.UPLOADS_DIR.exists():
        return []
    return [path for path in settings.UPLOADS_DIR.rglob("*") if path.is_file()]


async def test_dry_run_docx_xlsx_and_html_success_with_zero_side_effects(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє dry-run (.docx, .xlsx, .html) власником й адміном без запису в БД/диск."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    admin_headers = make_auth_headers(admin.id, admin.role)

    # 1. Word (.docx) — власник курсу, Варіант 1 (Times New Roman 14 пт, поля 2 см, 1.5, по ширині)
    _word_mod, word_prac = await _get_module_and_practical_by_order(
        db_session,
        CourseSlug.WORD,
        1,
    )
    docx_file = build_sample_docx(
        tmp_path / "reference_v1.docx",
        left_mm=20.0,
        right_mm=20.0,
        top_mm=20.0,
        bottom_mm=20.0,
        font_name="Times New Roman",
        font_size_pt=14.0,
        line_spacing=1.5,
        creator="Teacher Reference Author",
    )
    docx_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/dry-run",
        headers=teacher_headers,
        data={"variant_number": "1"},
        files={
            "file": (
                "reference_v1.docx",
                docx_file.read_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert docx_resp.status_code == 200
    docx_data = docx_resp.json()
    assert docx_data["practical_id"] == str(word_prac.id)
    assert docx_data["format_type"] == "docx"
    assert docx_data["variant_number"] == 1
    assert docx_data["auto_score"] == 10.0
    assert docx_data["auto_max_score"] == 10.0
    assert docx_data["max_score"] == 12.0
    assert docx_data["manual_bonus_max"] == 2.0
    assert docx_data["grading_report"]["passed_count"] == len(word_prac.grading_rules)
    assert docx_data["grading_report"]["failed_count"] == 0
    assert docx_data["extracted_metadata"]["creator"] == "Teacher Reference Author"
    assert isinstance(docx_data["extracted_metadata"]["content_fingerprint"], str)

    # 2. Excel (.xlsx) — адміністратор, Варіант 1
    _excel_mod, excel_prac = await _get_module_and_practical_by_order(
        db_session,
        CourseSlug.EXCEL,
        1,
    )
    xlsx_file = build_sample_xlsx(
        tmp_path / "reference_excel.xlsx",
        creator="Admin Reference Author",
    )
    xlsx_resp = await async_client.post(
        f"/api/v1/practicals/{excel_prac.id}/dry-run",
        headers=admin_headers,
        data={"variant_number": "1"},
        files={
            "file": (
                "reference_excel.xlsx",
                xlsx_file.read_bytes(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert xlsx_resp.status_code == 200
    xlsx_data = xlsx_resp.json()
    assert xlsx_data["practical_id"] == str(excel_prac.id)
    assert xlsx_data["format_type"] == "xlsx"
    assert xlsx_data["variant_number"] == 1
    assert xlsx_data["auto_max_score"] == 10.0
    assert xlsx_data["max_score"] == 12.0
    assert xlsx_data["manual_bonus_max"] == 2.0
    assert 0.0 <= xlsx_data["auto_score"] <= 10.0
    assert len(xlsx_data["grading_report"]["results"]) == len(excel_prac.grading_rules)
    assert xlsx_data["extracted_metadata"]["creator"] == "Admin Reference Author"

    # 3. HTML (.html) — власник курсу й адміністратор
    _html_mod, html_prac = await _get_module_and_practical_by_order(
        db_session,
        CourseSlug.HTML,
        1,
    )
    valid_html = """<!DOCTYPE html>
    <html lang="uk">
      <head>
        <meta charset="UTF-8">
        <title>Еталонна сторінка</title>
      </head>
      <body>
        <h1>Головний заголовок</h1>
        <h2>Розділ 1</h2>
        <p>Перший абзац із <strong>виділенням</strong>.</p>
        <h2>Розділ 2</h2>
        <p>Другий абзац із <em>курсивом</em>.</p>
        <p>Третій змістовний абзац.</p>
        <blockquote>Цитата для перевірки критерію.</blockquote>
      </body>
    </html>"""

    for headers in (teacher_headers, admin_headers):
        html_resp = await async_client.post(
            f"/api/v1/practicals/{html_prac.id}/dry-run",
            headers=headers,
            json={"raw_code": valid_html, "variant_number": 1},
        )
        assert html_resp.status_code == 200
        html_data = html_resp.json()
        assert html_data["practical_id"] == str(html_prac.id)
        assert html_data["format_type"] == "html"
        assert html_data["variant_number"] == 1
        assert html_data["auto_score"] == 10.0
        assert html_data["auto_max_score"] == 10.0
        assert html_data["max_score"] == 12.0
        assert html_data["manual_bonus_max"] == 2.0
        assert html_data["grading_report"]["failed_count"] == 0
        assert isinstance(html_data["extracted_metadata"]["content_fingerprint"], str)

    # Гарантія відсутності побічних ефектів: 0 записів Submission у БД і 0 файлів у UPLOADS_DIR
    assert await _count_submissions(db_session) == 0
    assert _list_uploaded_files() == []


async def test_dry_run_draft_rules_override_and_validation_without_persisting(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє rules_json/rules_override без мутації БД та 422 на невалідні правила/варіанти."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    teacher_headers = make_auth_headers(teacher.id, teacher.role)

    _html_mod, html_prac = await _get_module_and_practical_by_order(
        db_session,
        CourseSlug.HTML,
        1,
    )
    original_html_rules = copy.deepcopy(html_prac.grading_rules)

    # 1. Чернеткові правила у rules_override (HTML) застосовуються без збереження в БД
    draft_html_rules = [
        {
            "id": "draft_aside_rule",
            "type": "html_tag_exists",
            "target": "aside",
            "expected": "true",
            "points": 6.5,
            "description": "Наявний блок <aside>",
        },
        {
            "id": "draft_footer_rule",
            "type": "html_tag_exists",
            "target": "footer",
            "expected": "true",
            "points": 1.5,
            "description": "Наявний блок <footer>",
        },
    ]
    html_override_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/dry-run",
        headers=teacher_headers,
        json={
            "raw_code": (
                "<!DOCTYPE html><html lang='uk'><body>"
                "<aside>Бічна панель</aside></body></html>"
            ),
            "variant_number": 1,
            "rules_override": draft_html_rules,
        },
    )
    assert html_override_resp.status_code == 200
    html_override_data = html_override_resp.json()
    assert html_override_data["auto_score"] == 6.5
    assert html_override_data["auto_max_score"] == 8.0
    assert html_override_data["max_score"] == 12.0
    assert html_override_data["manual_bonus_max"] == 4.0
    assert html_override_data["grading_report"]["passed_count"] == 1
    assert html_override_data["grading_report"]["failed_count"] == 1

    # Збережені правила в БД не змінилися
    await db_session.refresh(html_prac)
    assert html_prac.grading_rules == original_html_rules

    # 2. Чернеткові правила у rules_json (multipart .docx) працюють і не змінюють БД
    _word_mod, word_prac = await _get_module_and_practical_by_order(
        db_session,
        CourseSlug.WORD,
        1,
    )
    original_word_rules = copy.deepcopy(word_prac.grading_rules)
    docx_file = build_sample_docx(
        tmp_path / "draft_check.docx",
        font_name="Arial",
        font_size_pt=12.0,
    )
    draft_docx_rules = [
        {
            "id": "draft_arial_12",
            "type": "docx_font",
            "target": "body",
            "expected": "Arial:12",
            "points": 7.5,
            "description": "Чернеткова перевірка шрифту Arial 12 пт",
        }
    ]
    docx_override_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/dry-run",
        headers=teacher_headers,
        data={
            "variant_number": "1",
            "rules_json": json.dumps(draft_docx_rules, ensure_ascii=False),
        },
        files={
            "file": (
                "draft_check.docx",
                docx_file.read_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert docx_override_resp.status_code == 200
    docx_override_data = docx_override_resp.json()
    assert docx_override_data["auto_score"] == 7.5
    assert docx_override_data["auto_max_score"] == 7.5
    assert docx_override_data["manual_bonus_max"] == 4.5
    assert docx_override_data["grading_report"]["passed_count"] == 1

    await db_session.refresh(word_prac)
    assert word_prac.grading_rules == original_word_rules

    # 3. Невалідні правила в rules_override -> 422 (несумісний формат і невалідний вираз)
    wrong_format_rule_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/dry-run",
        headers=teacher_headers,
        json={
            "raw_code": "<!DOCTYPE html><html><body><p>Текст</p></body></html>",
            "variant_number": 1,
            "rules_override": [
                {
                    "id": "wrong_fmt",
                    "type": "docx_font",
                    "target": "body",
                    "expected": "Arial:12",
                    "points": 5.0,
                    "description": "Чужий тип правила",
                }
            ],
        },
    )
    assert wrong_format_rule_resp.status_code == 422
    assert wrong_format_rule_resp.json()["code"] == "INVALID_RULE_TYPE_FOR_FORMAT"

    bad_syntax_rule_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/dry-run",
        headers=teacher_headers,
        json={
            "raw_code": "<!DOCTYPE html><html><body><p>Текст</p></body></html>",
            "variant_number": 1,
            "rules_override": [
                {
                    "id": "bad_count",
                    "type": "html_tag_count",
                    "target": "p",
                    "expected": "not_a_number",
                    "points": 5.0,
                    "description": "Некоректний числовий вираз",
                }
            ],
        },
    )
    assert bad_syntax_rule_resp.status_code == 422
    assert bad_syntax_rule_resp.json()["code"] == "INVALID_RULE_DEFINITION"

    # 4. Некоректний rules_json у multipart -> 422
    bad_json_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/dry-run",
        headers=teacher_headers,
        data={"variant_number": "1", "rules_json": "{not-valid-json"},
        files={
            "file": (
                "draft_check.docx",
                docx_file.read_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert bad_json_resp.status_code == 422
    assert bad_json_resp.json()["code"] == "INVALID_RULES_JSON"

    # 5. Недопустимий variant_number та перевищення MAX_HTML_CODE_LENGTH -> 422
    bad_variant_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/dry-run",
        headers=teacher_headers,
        json={
            "raw_code": "<!DOCTYPE html><html><body><p>Текст</p></body></html>",
            "variant_number": 999,
        },
    )
    assert bad_variant_resp.status_code == 422
    assert bad_variant_resp.json()["code"] == "INVALID_VARIANT_NUMBER"

    oversized_html_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/dry-run",
        headers=teacher_headers,
        json={"raw_code": "a" * (MAX_HTML_CODE_LENGTH + 1), "variant_number": 1},
    )
    assert oversized_html_resp.status_code == 422
    assert oversized_html_resp.json()["code"] == "RAW_CODE_TOO_LONG"

    # 6. Битий не-ZIP файл для .docx -> 415 INVALID_FILE_FORMAT
    corrupt_docx_resp = await async_client.post(
        f"/api/v1/practicals/{word_prac.id}/dry-run",
        headers=teacher_headers,
        data={"variant_number": "1"},
        files={
            "file": (
                "corrupt.docx",
                b"not-a-zip-archive",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert corrupt_docx_resp.status_code == 415
    assert corrupt_docx_resp.json()["code"] == "INVALID_FILE_FORMAT"

    assert await _count_submissions(db_session) == 0
    assert _list_uploaded_files() == []


async def test_dry_run_rbac_forbidden_for_student_and_other_teacher_and_404(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє 403 для студента і чужого викладача та 404 для неіснуючого practical_id."""
    student = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    other_teacher = await _create_other_teacher(db_session)

    student_headers = make_auth_headers(student.id, student.role)
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    other_headers = make_auth_headers(other_teacher.id, other_teacher.role)

    _html_mod, html_prac = await _get_module_and_practical_by_order(
        db_session,
        CourseSlug.HTML,
        1,
    )
    payload = {
        "raw_code": "<!DOCTYPE html><html><body><h1>Привіт</h1></body></html>",
        "variant_number": 1,
    }

    student_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/dry-run",
        headers=student_headers,
        json=payload,
    )
    assert student_resp.status_code == 403

    other_teacher_resp = await async_client.post(
        f"/api/v1/practicals/{html_prac.id}/dry-run",
        headers=other_headers,
        json=payload,
    )
    assert other_teacher_resp.status_code == 403
    assert other_teacher_resp.json()["detail"] == EXPECTED_FORBIDDEN_DETAIL

    missing_resp = await async_client.post(
        f"/api/v1/practicals/{uuid.uuid4()}/dry-run",
        headers=teacher_headers,
        json=payload,
    )
    assert missing_resp.status_code == 404
    assert missing_resp.json()["code"] == "PRACTICAL_NOT_FOUND"

    assert await _count_submissions(db_session) == 0


async def test_module_preview_variant_for_owner_admin_other_teacher_and_student(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє GET /api/v1/modules/{id}?preview_variant=K для різних ролей."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    other_teacher = await _create_other_teacher(
        db_session,
        email="other.teacher.preview@kpefk.lcloud.in.ua",
    )

    owner_headers = make_auth_headers(teacher.id, teacher.role)
    admin_headers = make_auth_headers(admin.id, admin.role)
    student_headers = make_auth_headers(student1.id, student1.role)
    other_headers = make_auth_headers(other_teacher.id, other_teacher.role)

    # Word M01 має кілька варіантів: Варіант 1 -> Times New Roman, Варіант 2 -> Calibri
    word_m01, word_m01_prac = await _get_module_and_practical_by_order(
        db_session,
        CourseSlug.WORD,
        1,
    )
    expected_total_variants = len(word_m01_prac.variants)
    assert expected_total_variants >= 2

    # 1. Викладач-власник запитує ?preview_variant=2 -> Варіант 2, без запису QuizAttempt
    owner_v2_resp = await async_client.get(
        f"/api/v1/modules/{word_m01.id}",
        params={"preview_variant": 2},
        headers=owner_headers,
    )
    assert owner_v2_resp.status_code == 200
    owner_v2 = owner_v2_resp.json()
    assert owner_v2["quiz_passed"] is True
    assert owner_v2["practical_unlocked"] is True
    assert owner_v2["lecture_content"] == word_m01.lecture_content
    assert len(owner_v2["quiz_questions"]) > 0

    prac_v2 = owner_v2["practical"]
    assert prac_v2 is not None
    assert prac_v2["assigned_variant_number"] == 2
    assert prac_v2["total_variants"] == expected_total_variants
    assert prac_v2["instructions"] == word_m01_prac.instructions
    assert prac_v2["variant"] is not None
    assert prac_v2["variant"]["variant_number"] == 2
    assert prac_v2["max_score"] == 12.0
    assert prac_v2["auto_max_score"] == 10.0
    assert prac_v2["manual_bonus_max"] == 2.0

    v2_criteria_text = " | ".join(
        item["description"] for item in prac_v2["grading_criteria"]
    )
    assert "Calibri" in v2_criteria_text
    assert "Times New Roman" not in v2_criteria_text
    assert "{" not in v2_criteria_text
    assert await _count_quiz_attempts(db_session) == 0

    # 2. Занадто великий preview_variant обмежується (clamp) до total_variants
    owner_clamped_resp = await async_client.get(
        f"/api/v1/modules/{word_m01.id}",
        params={"preview_variant": 999},
        headers=owner_headers,
    )
    assert owner_clamped_resp.status_code == 200
    assert (
        owner_clamped_resp.json()["practical"]["assigned_variant_number"]
        == expected_total_variants
    )

    # 3. Адміністратор може переглядати будь-який варіант модуля (Варіант 1 -> Times New Roman)
    admin_v1_resp = await async_client.get(
        f"/api/v1/modules/{word_m01.id}",
        params={"preview_variant": 1},
        headers=admin_headers,
    )
    assert admin_v1_resp.status_code == 200
    admin_v1_prac = admin_v1_resp.json()["practical"]
    assert admin_v1_prac["assigned_variant_number"] == 1
    assert admin_v1_prac["total_variants"] == expected_total_variants
    admin_v1_criteria = " | ".join(
        item["description"] for item in admin_v1_prac["grading_criteria"]
    )
    assert "Times New Roman" in admin_v1_criteria
    assert await _count_quiz_attempts(db_session) == 0

    # 4. Чужий викладач отримує 403 Forbidden
    other_resp = await async_client.get(
        f"/api/v1/modules/{word_m01.id}",
        params={"preview_variant": 2},
        headers=other_headers,
    )
    assert other_resp.status_code == 403
    assert other_resp.json()["detail"] == EXPECTED_FORBIDDEN_DETAIL

    # 5. Студент (list_number=1) ігнорує preview_variant=2 і бачить свій реальний Варіант 1
    assert student1.list_number == 1
    student_resp = await async_client.get(
        f"/api/v1/modules/{word_m01.id}",
        params={"preview_variant": 2},
        headers=student_headers,
    )
    assert student_resp.status_code == 200
    student_data = student_resp.json()
    assert student_data["quiz_passed"] is False
    assert student_data["practical_unlocked"] is False
    student_prac = student_data["practical"]
    assert student_prac["assigned_variant_number"] == 1
    assert student_prac["total_variants"] == expected_total_variants
    assert student_prac["instructions"] is None
    assert student_prac["variant"] is None
    student_criteria = " | ".join(
        item["description"] for item in student_prac["grading_criteria"]
    )
    assert "Times New Roman" in student_criteria
    assert "Calibri" not in student_criteria

    # 6. Після складання тесту GET /api/v1/practicals/{id} повертає total_variants
    db_session.add(
        QuizAttempt(
            student_id=student1.id,
            module_id=word_m01.id,
            score_percent=Decimal("100.00"),
            passed=True,
        )
    )
    await db_session.commit()

    student_prac_resp = await async_client.get(
        f"/api/v1/practicals/{word_m01_prac.id}",
        headers=student_headers,
    )
    assert student_prac_resp.status_code == 200
    assert student_prac_resp.json()["total_variants"] == expected_total_variants
