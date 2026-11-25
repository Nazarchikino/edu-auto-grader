import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import hash_password
from app.models.course import Course, CourseSlug, Module, Practical, QuizQuestion
from app.models.progress import QuizAttempt, Submission
from app.models.user import User, UserRole
from tests.conftest import SqliteAsyncSessionAdapter, make_auth_headers

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
    email: str = "other.teacher.rbac@kpefk.lcloud.in.ua",
    full_name: str = "Сторонній Викладач Іванович",
) -> User:
    """Створює стороннього викладача, який не є власником жодного курсу."""
    other_teacher = User(
        email=email,
        password_hash=hash_password("Teacher123!"),
        full_name=full_name,
        role=UserRole.TEACHER,
    )
    db_session.add(other_teacher)
    await db_session.commit()
    return other_teacher


async def _get_html_course_entities(
    db_session: SqliteAsyncSessionAdapter,
) -> tuple[Course, Module, Practical, QuizQuestion]:
    """Завантажує HTML-курс, його перший модуль із практичною та перше питання тесту."""
    course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.HTML))
    ).scalar_one()
    assert isinstance(course, Course)

    module, practical = (
        await db_session.execute(
            select(Module, Practical)
            .join(Practical, Practical.module_id == Module.id)
            .where(Module.course_id == course.id)
            .order_by(Module.order_index.asc())
            .limit(1)
        )
    ).one()
    assert isinstance(module, Module)
    assert isinstance(practical, Practical)

    question = (
        await db_session.execute(
            select(QuizQuestion)
            .where(QuizQuestion.module_id == module.id)
            .limit(1)
        )
    ).scalar_one()
    assert isinstance(question, QuizQuestion)

    return course, module, practical, question


async def test_cross_teacher_bola_blocked_across_all_course_and_submission_endpoints(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Гарантує 403 Forbidden для стороннього викладача на всіх захищених маршрутах курсу."""
    teacher_owner = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    student2 = await _get_user_by_email(db_session, "student2@kpefk.lcloud.in.ua")
    teacher_other = await _create_other_teacher(db_session)

    owner_headers = make_auth_headers(teacher_owner.id, teacher_owner.role)
    other_headers = make_auth_headers(teacher_other.id, teacher_other.role)
    admin_headers = make_auth_headers(admin.id, admin.role)
    student1_headers = make_auth_headers(student1.id, student1.role)
    student2_headers = make_auth_headers(student2.id, student2.role)

    course, module, practical, question = await _get_html_course_entities(db_session)
    assert course.teacher_id == teacher_owner.id

    # Студент складає тест-допуск та надсилає HTML-роботу із raw_code
    db_session.add(
        QuizAttempt(
            student_id=student1.id,
            module_id=module.id,
            score_percent=Decimal("100.00"),
            passed=True,
        )
    )
    await db_session.commit()

    raw_html_code = (
        "<!DOCTYPE html><html lang='uk'><body>"
        "<h1>Приватний код студента</h1></body></html>"
    )
    submit_resp = await async_client.post(
        f"/api/v1/practicals/{practical.id}/submit",
        headers=student1_headers,
        json={"raw_code": raw_html_code},
    )
    assert submit_resp.status_code == 201
    submission_id = uuid.UUID(submit_resp.json()["id"])
    original_score = submit_resp.json()["final_score"]
    original_course_title = course.title
    original_module_title = module.title
    original_practical_title = practical.title

    rules_payload = {
        "grading_rules": [
            {
                "id": "bola_rule_1",
                "type": "html_tag_exists",
                "target": "h1",
                "expected": "true",
                "points": 10.0,
                "description": "Наявний заголовок h1",
            }
        ]
    }
    practical_upsert_payload = {
        "title": "Перезаписана чужа практична",
        "instructions": "Несанкціоновані методичні вказівки",
        "format_type": "html",
        "max_score": 10.0,
        "variants": [],
        "grading_rules": rules_payload["grading_rules"],
    }

    # Усі 11 раніше незахищених + 3 переведені на спільний хелпер маршрути -> 403 для teacher_other
    forbidden_responses = [
        await async_client.patch(
            f"/api/v1/courses/{course.id}",
            headers=other_headers,
            json={"title": "Змінено чужим викладачем"},
        ),
        await async_client.patch(
            f"/api/v1/courses/{course.id}",
            headers=other_headers,
            json={"teacher_id": str(teacher_other.id)},
        ),
        await async_client.post(
            f"/api/v1/courses/{course.id}/modules",
            headers=other_headers,
            json={
                "order_index": 99,
                "title": "Несанкціонований модуль",
                "lecture_content": "Текст чужої лекції",
            },
        ),
        await async_client.patch(
            f"/api/v1/modules/{module.id}",
            headers=other_headers,
            json={"title": "Змінений чужий модуль"},
        ),
        await async_client.delete(
            f"/api/v1/modules/{module.id}",
            headers=other_headers,
        ),
        await async_client.get(
            f"/api/v1/modules/{module.id}/quiz/questions",
            headers=other_headers,
        ),
        await async_client.post(
            f"/api/v1/modules/{module.id}/quiz/questions",
            headers=other_headers,
            json={
                "question_text": "Чуже питання тесту?",
                "options": ["Так", "Ні"],
                "correct_option_index": 0,
            },
        ),
        await async_client.delete(
            f"/api/v1/quiz/questions/{question.id}",
            headers=other_headers,
        ),
        await async_client.post(
            f"/api/v1/modules/{module.id}/practical",
            headers=other_headers,
            json=practical_upsert_payload,
        ),
        await async_client.patch(
            f"/api/v1/practicals/{practical.id}",
            headers=other_headers,
            json={"title": "Змінена чужа практична"},
        ),
        await async_client.delete(
            f"/api/v1/practicals/{practical.id}",
            headers=other_headers,
        ),
        await async_client.put(
            f"/api/v1/practicals/{practical.id}/rules",
            headers=other_headers,
            json=rules_payload,
        ),
        await async_client.get(
            f"/api/v1/submissions/{submission_id}",
            headers=other_headers,
        ),
        await async_client.patch(
            f"/api/v1/submissions/{submission_id}/grade",
            headers=other_headers,
            json={"final_score": 1.0, "teacher_comment": "Чужа оцінка"},
        ),
        await async_client.get(
            f"/api/v1/submissions/{submission_id}/download",
            headers=other_headers,
        ),
    ]

    for resp in forbidden_responses:
        assert resp.status_code == 403, (
            f"Очікувався 403 для {resp.request.method} {resp.request.url}, "
            f"отримано {resp.status_code}: {resp.text}"
        )
        body = resp.json()
        assert body["detail"] == EXPECTED_FORBIDDEN_DETAIL
        assert "raw_code" not in body

    # Жодна сутність у БД не була модифікована або видалена стороннім викладачем
    refreshed_course = (
        await db_session.execute(select(Course).where(Course.id == course.id))
    ).scalar_one()
    assert refreshed_course.title == original_course_title
    assert refreshed_course.teacher_id == teacher_owner.id

    refreshed_module = (
        await db_session.execute(select(Module).where(Module.id == module.id))
    ).scalar_one()
    assert refreshed_module.title == original_module_title

    refreshed_practical = (
        await db_session.execute(select(Practical).where(Practical.id == practical.id))
    ).scalar_one()
    assert refreshed_practical.title == original_practical_title

    refreshed_question = (
        await db_session.execute(
            select(QuizQuestion).where(QuizQuestion.id == question.id)
        )
    ).scalar_one_or_none()
    assert refreshed_question is not None

    refreshed_submission = (
        await db_session.execute(
            select(Submission).where(Submission.id == submission_id)
        )
    ).scalar_one()
    assert float(refreshed_submission.final_score) == pytest.approx(original_score)
    assert refreshed_submission.teacher_comment is None

    # Перевірка ізоляції студентів на GET /submissions/{id}: автор -> 200, інший студент -> 403
    student1_get = await async_client.get(
        f"/api/v1/submissions/{submission_id}",
        headers=student1_headers,
    )
    assert student1_get.status_code == 200
    assert student1_get.json()["raw_code"] == raw_html_code

    student2_get = await async_client.get(
        f"/api/v1/submissions/{submission_id}",
        headers=student2_headers,
    )
    assert student2_get.status_code == 403
    assert student2_get.json()["code"] == "FORBIDDEN_SUBMISSION_ACCESS"

    # Позитивні перевірки: teacher_owner та admin мають повний доступ до свого курсу та здачі
    for allowed_headers in (owner_headers, admin_headers):
        sub_detail = await async_client.get(
            f"/api/v1/submissions/{submission_id}",
            headers=allowed_headers,
        )
        assert sub_detail.status_code == 200
        assert sub_detail.json()["raw_code"] == raw_html_code

        quiz_list = await async_client.get(
            f"/api/v1/modules/{module.id}/quiz/questions",
            headers=allowed_headers,
        )
        assert quiz_list.status_code == 200
        assert len(quiz_list.json()) >= 1

    # Власник курсу може створювати й видаляти модулі, питання, практичні, правила та оцінки
    created_mod_resp = await async_client.post(
        f"/api/v1/courses/{course.id}/modules",
        headers=owner_headers,
        json={
            "order_index": 50,
            "title": "Додатковий модуль власника",
            "lecture_content": "Методичний матеріал власника курсу",
        },
    )
    assert created_mod_resp.status_code == 201
    created_mod_id = created_mod_resp.json()["id"]

    patched_mod_resp = await async_client.patch(
        f"/api/v1/modules/{created_mod_id}",
        headers=owner_headers,
        json={"title": "Оновлений модуль власника"},
    )
    assert patched_mod_resp.status_code == 200

    created_q_resp = await async_client.post(
        f"/api/v1/modules/{created_mod_id}/quiz/questions",
        headers=owner_headers,
        json={
            "question_text": "Який тег визначає головний заголовок?",
            "options": ["<h1>", "<p>"],
            "correct_option_index": 0,
        },
    )
    assert created_q_resp.status_code == 201
    created_q_id = created_q_resp.json()["id"]

    deleted_q_resp = await async_client.delete(
        f"/api/v1/quiz/questions/{created_q_id}",
        headers=owner_headers,
    )
    assert deleted_q_resp.status_code == 204

    created_prac_resp = await async_client.post(
        f"/api/v1/modules/{created_mod_id}/practical",
        headers=owner_headers,
        json=practical_upsert_payload,
    )
    assert created_prac_resp.status_code == 201
    created_prac_id = created_prac_resp.json()["id"]

    patched_prac_resp = await async_client.patch(
        f"/api/v1/practicals/{created_prac_id}",
        headers=owner_headers,
        json={"title": "Оновлена практична власника"},
    )
    assert patched_prac_resp.status_code == 200

    rules_resp = await async_client.put(
        f"/api/v1/practicals/{created_prac_id}/rules",
        headers=owner_headers,
        json=rules_payload,
    )
    assert rules_resp.status_code == 200

    grade_resp = await async_client.patch(
        f"/api/v1/submissions/{submission_id}/grade",
        headers=owner_headers,
        json={"final_score": 9.0, "teacher_comment": "Перевірено власником курсу."},
    )
    assert grade_resp.status_code == 200
    assert grade_resp.json()["final_score"] == 9.0


async def test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє, що змінювати teacher_id курсу може лише адміністратор, але не викладач."""
    teacher_owner = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher_other = await _create_other_teacher(
        db_session,
        email="other.teacher.reassign@kpefk.lcloud.in.ua",
    )

    owner_headers = make_auth_headers(teacher_owner.id, teacher_owner.role)
    other_headers = make_auth_headers(teacher_other.id, teacher_other.role)
    admin_headers = make_auth_headers(admin.id, admin.role)

    course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.WORD))
    ).scalar_one()
    assert isinstance(course, Course)
    assert course.teacher_id == teacher_owner.id

    # 1. Власник курсу отримує 403 при спробі передати курс іншому викладачу
    owner_reassign_resp = await async_client.patch(
        f"/api/v1/courses/{course.id}",
        headers=owner_headers,
        json={"teacher_id": str(teacher_other.id)},
    )
    assert owner_reassign_resp.status_code == 403
    assert owner_reassign_resp.json()["code"] == "FORBIDDEN_COURSE_TEACHER_CHANGE"

    # 2. Якщо teacher_id не змінюється, власник може оновити заголовок курсу -> 200 OK
    owner_same_teacher_resp = await async_client.patch(
        f"/api/v1/courses/{course.id}",
        headers=owner_headers,
        json={
            "teacher_id": str(teacher_owner.id),
            "title": "Microsoft Word — Оновлена назва власником",
        },
    )
    assert owner_same_teacher_resp.status_code == 200
    assert owner_same_teacher_resp.json()["teacher_id"] == str(teacher_owner.id)
    assert (
        owner_same_teacher_resp.json()["title"]
        == "Microsoft Word — Оновлена назва власником"
    )

    # 3. Адміністратор не може призначити студента (422) або неіснуючого користувача (404)
    student_assign_resp = await async_client.patch(
        f"/api/v1/courses/{course.id}",
        headers=admin_headers,
        json={"teacher_id": str(student1.id)},
    )
    assert student_assign_resp.status_code == 422
    assert student_assign_resp.json()["code"] == "INVALID_COURSE_TEACHER"

    missing_assign_resp = await async_client.patch(
        f"/api/v1/courses/{course.id}",
        headers=admin_headers,
        json={"teacher_id": str(uuid.uuid4())},
    )
    assert missing_assign_resp.status_code == 404
    assert missing_assign_resp.json()["code"] == "USER_NOT_FOUND"

    # 4. Адміністратор успішно перепризначає викладача курсу -> 200 OK
    admin_reassign_resp = await async_client.patch(
        f"/api/v1/courses/{course.id}",
        headers=admin_headers,
        json={"teacher_id": str(teacher_other.id)},
    )
    assert admin_reassign_resp.status_code == 200
    assert admin_reassign_resp.json()["teacher_id"] == str(teacher_other.id)

    # 5. Після перепризначення новий власник може редагувати курс, а попередній отримує 403
    new_owner_edit_resp = await async_client.patch(
        f"/api/v1/courses/{course.id}",
        headers=other_headers,
        json={"title": "Microsoft Word — Оновлено новим викладачем"},
    )
    assert new_owner_edit_resp.status_code == 200

    old_owner_edit_resp = await async_client.patch(
        f"/api/v1/courses/{course.id}",
        headers=owner_headers,
        json={"title": "Спроба попереднього власника"},
    )
    assert old_owner_edit_resp.status_code == 403
    assert old_owner_edit_resp.json()["detail"] == EXPECTED_FORBIDDEN_DETAIL


async def test_duplicate_root_auth_router_removed_returns_404(
    async_client: AsyncClient,
) -> None:
    """Перевіряє видалення дублюючого кореневого роутера /auth/* при збереженні /api/v1/auth/*."""
    root_login_resp = await async_client.post(
        "/auth/login",
        json={
            "email": "student1@kpefk.lcloud.in.ua",
            "password": "Student123!",
        },
    )
    assert root_login_resp.status_code == 404

    root_refresh_resp = await async_client.post(
        "/auth/refresh",
        json={"refresh_token": "dummy-token"},
    )
    assert root_refresh_resp.status_code == 404

    root_me_resp = await async_client.get("/auth/me")
    assert root_me_resp.status_code == 404

    # Канонічний шлях /api/v1/auth/login працює коректно
    v1_login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "student1@kpefk.lcloud.in.ua",
            "password": "Student123!",
        },
    )
    assert v1_login_resp.status_code == 200
    assert "access_token" in v1_login_resp.json()
