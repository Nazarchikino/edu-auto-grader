import io
import uuid
import zipfile
from decimal import Decimal
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.core.config import settings
from app.core.security import hash_password
from app.models.course import Course, CourseSlug, Module, Practical, QuizQuestion
from app.models.progress import QuizAttempt, Submission
from app.models.user import User, UserRole
from app.services.submission_service import UNMODIFIED_TEMPLATE_ERROR_MESSAGE
from tests.conftest import (
    SqliteAsyncSessionAdapter,
    build_sample_docx,
    make_auth_headers,
)

pytestmark = pytest.mark.asyncio

# Мінімальний валідний 1x1 PNG із реальними magic bytes
MINIMAL_VALID_PNG: bytes = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00"
    b"\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
)
MINIMAL_VALID_JPEG: bytes = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
)
MINIMAL_VALID_GIF: bytes = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff"
    b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)
MINIMAL_VALID_WEBP: bytes = (
    b"RIFF\x18\x00\x00\x00WEBPVP8L\x0c\x00\x00\x00"
    b"\x2f\x00\x00\x00\x10\x07\x10\x11\x11\x88\x88\xfe"
)


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
    email: str,
) -> User:
    """Створює стороннього викладача, який не є власником жодного курсу."""
    other_teacher = User(
        email=email,
        password_hash=hash_password("Teacher123!"),
        full_name="Інший Викладач Петрович",
        role=UserRole.TEACHER,
    )
    db_session.add(other_teacher)
    await db_session.commit()
    return other_teacher


async def _get_course_by_slug(
    db_session: SqliteAsyncSessionAdapter,
    slug: CourseSlug,
) -> Course:
    """Повертає курс із тестової БД за його slug."""
    result = await db_session.execute(select(Course).where(Course.slug == slug))
    course = result.scalar_one()
    assert isinstance(course, Course)
    return course


async def test_patch_quiz_question_owner_validation_and_rbac(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє PATCH /quiz/questions/{id}: власник, збереження id/order_index, 422 і 403."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    student = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    other_teacher = await _create_other_teacher(
        db_session,
        email="other.teacher.quiz.patch@kpefk.lcloud.in.ua",
    )

    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    other_headers = make_auth_headers(other_teacher.id, other_teacher.role)

    question_result = await db_session.execute(
        select(QuizQuestion)
        .join(Module, Module.id == QuizQuestion.module_id)
        .join(Course, Course.id == Module.course_id)
        .where(Course.slug == CourseSlug.WORD)
        .order_by(QuizQuestion.order_index.asc(), QuizQuestion.id.asc())
        .limit(1)
    )
    question = question_result.scalar_one()
    assert isinstance(question, QuizQuestion)
    original_id = question.id
    original_order_index = question.order_index
    module_id = question.module_id

    # Додаємо спробу тесту, щоб перевірити, що PATCH її не видаляє і не зачіпає
    attempt = QuizAttempt(
        student_id=student.id,
        module_id=module_id,
        score_percent=Decimal("100.00"),
        passed=True,
    )
    db_session.add(attempt)
    await db_session.commit()
    attempt_id = attempt.id

    # 1. Сторонній викладач -> 403, неіснуюче питання -> 404
    not_found_resp = await async_client.patch(
        f"/api/v1/quiz/questions/{uuid.uuid4()}",
        headers=teacher_headers,
        json={"question_text": "Неіснуюче питання"},
    )
    assert not_found_resp.status_code == 404

    forbidden_resp = await async_client.patch(
        f"/api/v1/quiz/questions/{original_id}",
        headers=other_headers,
        json={"question_text": "Спроба чужого викладача"},
    )
    assert forbidden_resp.status_code == 403

    # 2. Невалідний correct_option_index -> 422
    invalid_idx_resp = await async_client.patch(
        f"/api/v1/quiz/questions/{original_id}",
        headers=teacher_headers,
        json={
            "options": ["Варіант А", "Варіант Б"],
            "correct_option_index": 2,
        },
    )
    assert invalid_idx_resp.status_code == 422

    # 3. Порожній варіант відповіді -> 422
    blank_opt_resp = await async_client.patch(
        f"/api/v1/quiz/questions/{original_id}",
        headers=teacher_headers,
        json={"options": ["Варіант А", "   "]},
    )
    assert blank_opt_resp.status_code == 422

    # 4. Успішне редагування власником -> 200 зі збереженням id, order_index та QuizAttempt
    patch_resp = await async_client.patch(
        f"/api/v1/quiz/questions/{original_id}",
        headers=teacher_headers,
        json={
            "question_text": "Оновлене формулювання питання Word?",
            "options": ["Перший оновлений", "Другий оновлений", "Третій оновлений"],
            "correct_option_index": 2,
        },
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["id"] == str(original_id)
    assert body["module_id"] == str(module_id)
    assert body["question_text"] == "Оновлене формулювання питання Word?"
    assert body["options"] == [
        "Перший оновлений",
        "Другий оновлений",
        "Третій оновлений",
    ]
    assert body["correct_option_index"] == 2

    await db_session.refresh(question)
    assert question.id == original_id
    assert question.order_index == original_order_index

    attempt_check = await db_session.execute(
        select(QuizAttempt).where(QuizAttempt.id == attempt_id)
    )
    assert attempt_check.scalar_one_or_none() is not None


async def test_reorder_course_modules_two_step_no_unique_conflict_and_validation(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє PUT /courses/{id}/modules/reorder для 3 модулів [m3, m1, m2], 422 і 403."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    other_teacher = await _create_other_teacher(
        db_session,
        email="other.teacher.reorder@kpefk.lcloud.in.ua",
    )
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    other_headers = make_auth_headers(other_teacher.id, other_teacher.role)

    html_course = await _get_course_by_slug(db_session, CourseSlug.HTML)
    word_course = await _get_course_by_slug(db_session, CourseSlug.WORD)

    # Залишаємо рівно 3 модулі у курсі HTML для чистої перевірки [m3, m1, m2]
    modules_result = await db_session.execute(
        select(Module)
        .where(Module.course_id == html_course.id)
        .order_by(Module.order_index.asc())
    )
    html_modules = list(modules_result.scalars().all())
    assert len(html_modules) >= 3
    for extra_mod in html_modules[3:]:
        del_resp = await async_client.delete(
            f"/api/v1/modules/{extra_mod.id}",
            headers=teacher_headers,
        )
        assert del_resp.status_code == 204

    m1, m2, m3 = html_modules[0], html_modules[1], html_modules[2]

    # 1. Сторонній викладач -> 403
    forbidden_resp = await async_client.put(
        f"/api/v1/courses/{html_course.id}/modules/reorder",
        headers=other_headers,
        json={"module_ids": [str(m3.id), str(m1.id), str(m2.id)]},
    )
    assert forbidden_resp.status_code == 403

    # 2. Неповний список ID -> 422
    incomplete_resp = await async_client.put(
        f"/api/v1/courses/{html_course.id}/modules/reorder",
        headers=teacher_headers,
        json={"module_ids": [str(m3.id), str(m1.id)]},
    )
    assert incomplete_resp.status_code == 422

    # 3. Дублікат ID -> 422
    duplicate_resp = await async_client.put(
        f"/api/v1/courses/{html_course.id}/modules/reorder",
        headers=teacher_headers,
        json={"module_ids": [str(m1.id), str(m1.id), str(m2.id)]},
    )
    assert duplicate_resp.status_code == 422

    # 4. Чужий module_id з іншого курсу -> 422
    foreign_mod_result = await db_session.execute(
        select(Module.id).where(Module.course_id == word_course.id).limit(1)
    )
    foreign_mod_id = foreign_mod_result.scalar_one()
    foreign_resp = await async_client.put(
        f"/api/v1/courses/{html_course.id}/modules/reorder",
        headers=teacher_headers,
        json={"module_ids": [str(m1.id), str(m2.id), str(foreign_mod_id)]},
    )
    assert foreign_resp.status_code == 422

    # 5. Валідна перестановка [m3, m1, m2] -> нові order_index 1, 2, 3 без конфлікту унікальності
    reorder_resp = await async_client.put(
        f"/api/v1/courses/{html_course.id}/modules/reorder",
        headers=teacher_headers,
        json={"module_ids": [str(m3.id), str(m1.id), str(m2.id)]},
    )
    assert reorder_resp.status_code == 200
    reordered = reorder_resp.json()
    assert [(item["id"], item["order_index"]) for item in reordered] == [
        (str(m3.id), 1),
        (str(m1.id), 2),
        (str(m2.id), 3),
    ]

    # Перевіряємо стан у БД
    db_check = await db_session.execute(
        select(Module.id, Module.order_index)
        .where(Module.course_id == html_course.id)
        .order_by(Module.order_index.asc())
    )
    assert list(db_check.all()) == [(m3.id, 1), (m1.id, 2), (m2.id, 3)]


async def test_upload_course_media_raster_magic_bytes_security_and_limits(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє POST /courses/{id}/media: PNG/JPEG/GIF/WebP, блок SVG/XSS, 413 і 403."""
    isolated_media_dir = tmp_path / "course_media"
    isolated_media_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "COURSE_MEDIA_DIR", isolated_media_dir)

    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    other_teacher = await _create_other_teacher(
        db_session,
        email="other.teacher.media@kpefk.lcloud.in.ua",
    )
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    other_headers = make_auth_headers(other_teacher.id, other_teacher.role)

    word_course = await _get_course_by_slug(db_session, CourseSlug.WORD)

    # 1. Чужий викладач -> 403
    forbidden_resp = await async_client.post(
        f"/api/v1/courses/{word_course.id}/media",
        headers=other_headers,
        files={"file": ("diagram.png", MINIMAL_VALID_PNG, "image/png")},
    )
    assert forbidden_resp.status_code == 403

    # 2. Заборонений SVG -> 422
    svg_resp = await async_client.post(
        f"/api/v1/courses/{word_course.id}/media",
        headers=teacher_headers,
        files={
            "file": (
                "xss.svg",
                b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
                "image/svg+xml",
            )
        },
    )
    assert svg_resp.status_code == 422

    # 3. Фейковий PNG із HTML/JS-текстом -> 422
    fake_png_resp = await async_client.post(
        f"/api/v1/courses/{word_course.id}/media",
        headers=teacher_headers,
        files={"file": ("fake.png", b"<script>alert('xss')</script>", "image/png")},
    )
    assert fake_png_resp.status_code == 422

    # 4. Валідні PNG, JPEG, GIF, WebP -> 200 і фізичний файл на диску
    for fname, raw_bytes, mime in (
        ("screenshot.png", MINIMAL_VALID_PNG, "image/png"),
        ("photo.jpg", MINIMAL_VALID_JPEG, "image/jpeg"),
        ("anim.gif", MINIMAL_VALID_GIF, "image/gif"),
        ("pic.webp", MINIMAL_VALID_WEBP, "image/webp"),
    ):
        ok_resp = await async_client.post(
            f"/api/v1/courses/{word_course.id}/media",
            headers=teacher_headers,
            files={"file": (fname, raw_bytes, mime)},
        )
        assert ok_resp.status_code == 200
        data = ok_resp.json()
        expected_prefix = f"/media/courses/{word_course.slug.value}/uploads/"
        assert data["url"].startswith(expected_prefix)
        assert data["markdown"] == f"![Ілюстрація]({data['url']})"
        assert data["size_bytes"] == len(raw_bytes)
        disk_file = (
            isolated_media_dir
            / word_course.slug.value
            / "uploads"
            / data["filename"]
        )
        assert disk_file.is_file()
        assert disk_file.read_bytes() == raw_bytes

    # 5. Перевищення MAX_COURSE_MEDIA_UPLOAD_BYTES -> 413
    monkeypatch.setattr(settings, "MAX_COURSE_MEDIA_UPLOAD_BYTES", 64)
    oversized_png = MINIMAL_VALID_PNG + (b"\x00" * 128)
    too_large_resp = await async_client.post(
        f"/api/v1/courses/{word_course.id}/media",
        headers=teacher_headers,
        files={"file": ("huge.png", oversized_png, "image/png")},
    )
    assert too_large_resp.status_code == 413


async def test_practical_template_lifecycle_student_download_unmodified_reject_and_cleanup(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє POST/GET/DELETE /practicals/{id}/template, блок незміненого шаблону та очищення."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    student = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    other_teacher = await _create_other_teacher(
        db_session,
        email="other.teacher.template@kpefk.lcloud.in.ua",
    )

    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    student_headers = make_auth_headers(student.id, student.role)
    other_headers = make_auth_headers(other_teacher.id, other_teacher.role)

    # Обираємо практичну Word №1
    row = (
        await db_session.execute(
            select(Module, Practical)
            .join(Course, Course.id == Module.course_id)
            .join(Practical, Practical.module_id == Module.id)
            .where(Course.slug == CourseSlug.WORD, Module.order_index == 1)
            .limit(1)
        )
    ).one()
    word_module, word_practical = row
    assert isinstance(word_module, Module)
    assert isinstance(word_practical, Practical)

    # До завантаження шаблону GET повертає 404
    missing_resp = await async_client.get(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=student_headers,
    )
    assert missing_resp.status_code == 404

    template_docx_path = build_sample_docx(
        tmp_path / "template_v1.docx",
        left_mm=20.0,
        right_mm=20.0,
        top_mm=20.0,
        bottom_mm=20.0,
        creator="Teacher Template",
    )
    template_bytes = template_docx_path.read_bytes()

    # Сторонній викладач не може завантажити шаблон -> 403
    forbidden_upload = await async_client.post(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=other_headers,
        files={
            "file": (
                "Заготовка_ЛР1.docx",
                template_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert forbidden_upload.status_code == 403

    # Непідтримуване розширення -> 422
    bad_ext_resp = await async_client.post(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=teacher_headers,
        files={"file": ("script.html", b"<html><body>x</body></html>", "text/html")},
    )
    assert bad_ext_resp.status_code == 422

    # Пошкоджений ZIP -> 422
    bad_zip_resp = await async_client.post(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=teacher_headers,
        files={"file": ("broken.zip", b"not-a-zip-file", "application/zip")},
    )
    assert bad_zip_resp.status_code == 422

    # 1. Успішне завантаження файлу-заготовки викладачем
    upload_resp = await async_client.post(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=teacher_headers,
        files={
            "file": (
                "Заготовка_ЛР1.docx",
                template_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert upload_resp.status_code == 200
    uploaded_body = upload_resp.json()
    assert uploaded_body["has_template_file"] is True
    assert uploaded_body["template_file_name"] == "Заготовка_ЛР1.docx"

    await db_session.refresh(word_practical)
    assert word_practical.template_file_path is not None
    assert word_practical.template_file_hash is not None
    first_template_disk_path = Path(word_practical.template_file_path)
    assert first_template_disk_path.is_file()
    assert first_template_disk_path.parent.name == "templates"

    # 2. Студент скачує файл-заготовку -> 200 із читабельним Content-Disposition
    download_resp = await async_client.get(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=student_headers,
    )
    assert download_resp.status_code == 200
    assert download_resp.content == template_bytes
    content_disp = download_resp.headers.get("content-disposition", "")
    assert "attachment" in content_disp.lower()
    assert ".docx" in content_disp.lower()

    # 3. Зараховуємо тест-допуск студенту і перевіряємо PracticalStudentRead
    db_session.add(
        QuizAttempt(
            student_id=student.id,
            module_id=word_module.id,
            score_percent=Decimal("100.00"),
            passed=True,
        )
    )
    await db_session.commit()

    student_prac_resp = await async_client.get(
        f"/api/v1/practicals/{word_practical.id}",
        headers=student_headers,
    )
    assert student_prac_resp.status_code == 200
    assert student_prac_resp.json()["has_template_file"] is True
    assert student_prac_resp.json()["template_file_name"] == "Заготовка_ЛР1.docx"

    # 4. Спроба студента здати НЕЗМІНЕНИЙ шаблон -> 422 і 0 нових здач у БД
    subs_before = int(
        (await db_session.execute(select(func.count(Submission.id)))).scalar_one()
    )
    unmodified_submit_resp = await async_client.post(
        f"/api/v1/practicals/{word_practical.id}/submit",
        headers=student_headers,
        files={
            "file": (
                "my_work.docx",
                template_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert unmodified_submit_resp.status_code == 422
    assert unmodified_submit_resp.json()["detail"] == UNMODIFIED_TEMPLATE_ERROR_MESSAGE
    subs_after_reject = int(
        (await db_session.execute(select(func.count(Submission.id)))).scalar_one()
    )
    assert subs_after_reject == subs_before

    # 5. Заміна шаблону видаляє старий файл із диска
    second_zip_buf = io.BytesIO()
    with zipfile.ZipFile(second_zip_buf, mode="w") as zf:
        zf.writestr("dataset.csv", "col1,col2\n1,2\n")
    replace_resp = await async_client.post(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=teacher_headers,
        files={"file": ("dataset.zip", second_zip_buf.getvalue(), "application/zip")},
    )
    assert replace_resp.status_code == 200
    assert not first_template_disk_path.exists()
    await db_session.refresh(word_practical)
    assert word_practical.template_file_path is not None
    second_template_disk_path = Path(word_practical.template_file_path)
    assert second_template_disk_path.is_file()

    # 6. DELETE /practicals/{id}/template видаляє файл із диска та повертає 204
    del_tpl_resp = await async_client.delete(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=teacher_headers,
    )
    assert del_tpl_resp.status_code == 204
    assert not second_template_disk_path.exists()

    after_delete_get = await async_client.get(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=student_headers,
    )
    assert after_delete_get.status_code == 404

    # 7. Видалення практичної роботи прибирає файл-заготовку з диска
    reupload_for_prac_delete = await async_client.post(
        f"/api/v1/practicals/{word_practical.id}/template",
        headers=teacher_headers,
        files={"file": ("starter.csv", b"a,b\n1,2\n", "text/csv")},
    )
    assert reupload_for_prac_delete.status_code == 200
    await db_session.refresh(word_practical)
    assert word_practical.template_file_path is not None
    prac_delete_tpl_path = Path(word_practical.template_file_path)
    assert prac_delete_tpl_path.is_file()

    del_prac_resp = await async_client.delete(
        f"/api/v1/practicals/{word_practical.id}",
        headers=teacher_headers,
    )
    assert del_prac_resp.status_code == 204
    assert not prac_delete_tpl_path.exists()

    # 8. Видалення модуля також прибирає файл-заготовку його практичної з диска
    row_mod2 = (
        await db_session.execute(
            select(Module, Practical)
            .join(Course, Course.id == Module.course_id)
            .join(Practical, Practical.module_id == Module.id)
            .where(Course.slug == CourseSlug.WORD, Module.order_index == 2)
            .limit(1)
        )
    ).one()
    word_module_2, word_practical_2 = row_mod2
    assert isinstance(word_module_2, Module)
    assert isinstance(word_practical_2, Practical)

    upload_mod2_tpl = await async_client.post(
        f"/api/v1/practicals/{word_practical_2.id}/template",
        headers=teacher_headers,
        files={"file": ("input_data.txt", b"line1\nline2\n", "text/plain")},
    )
    assert upload_mod2_tpl.status_code == 200
    await db_session.refresh(word_practical_2)
    assert word_practical_2.template_file_path is not None
    mod_delete_tpl_path = Path(word_practical_2.template_file_path)
    assert mod_delete_tpl_path.is_file()

    del_mod_resp = await async_client.delete(
        f"/api/v1/modules/{word_module_2.id}",
        headers=teacher_headers,
    )
    assert del_mod_resp.status_code == 204
    assert not mod_delete_tpl_path.exists()
