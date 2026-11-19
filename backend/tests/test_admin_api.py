import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.course import ALLOWED_COURSE_SLUGS, CourseSlug
from app.models.user import AcademicGroup, User
from app.seed import build_seed_bundle
from tests.conftest import SqliteAsyncSessionAdapter, make_auth_headers

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


async def test_admin_endpoints_enforce_admin_rbac(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє, що студент і викладач отримують 403 FORBIDDEN на admin-ендпоінтах."""
    student = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")

    for user in (student, teacher):
        headers = make_auth_headers(user.id, user.role)
        groups_resp = await async_client.get("/api/v1/admin/groups", headers=headers)
        assert groups_resp.status_code == 403
        assert groups_resp.json()["code"] == "FORBIDDEN"

        users_resp = await async_client.get("/api/v1/admin/users", headers=headers)
        assert users_resp.status_code == 403
        assert users_resp.json()["code"] == "FORBIDDEN"


async def test_admin_academic_groups_crud_and_detachment(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє CRUD академічних груп, контроль дублікатів та відв'язку студентів."""
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    headers = make_auth_headers(admin.id, admin.role)

    # 1. Список початкових груп (з seed.py є КН-31)
    list_resp = await async_client.get("/api/v1/admin/groups", headers=headers)
    assert list_resp.status_code == 200
    initial_groups = list_resp.json()
    assert any(group["code"] == "КН-31" for group in initial_groups)

    # 2. Створення нової групи
    create_resp = await async_client.post(
        "/api/v1/admin/groups",
        headers=headers,
        json={
            "code": "ПЗ-21",
            "specialty": "121 Інженерія програмного забезпечення",
            "course_year": 2,
        },
    )
    assert create_resp.status_code == 201
    created_group = create_resp.json()
    group_id = created_group["id"]
    assert created_group["code"] == "ПЗ-21"
    assert created_group["course_year"] == 2

    # 3. Дублювання шифру -> 409 GROUP_CODE_EXISTS
    dup_resp = await async_client.post(
        "/api/v1/admin/groups",
        headers=headers,
        json={
            "code": "пз-21",
            "specialty": "122 Комп'ютерні науки",
            "course_year": 2,
        },
    )
    assert dup_resp.status_code == 409
    assert dup_resp.json()["code"] == "GROUP_CODE_EXISTS"

    # 4. Оновлення групи
    update_resp = await async_client.patch(
        f"/api/v1/admin/groups/{group_id}",
        headers=headers,
        json={
            "code": "ПЗ-22",
            "specialty": "122 Комп'ютерні науки",
            "course_year": 3,
        },
    )
    assert update_resp.status_code == 200
    updated_group = update_resp.json()
    assert updated_group["code"] == "ПЗ-22"
    assert updated_group["specialty"] == "122 Комп'ютерні науки"
    assert updated_group["course_year"] == 3

    # 5. Прив'язуємо нового студента до групи, потім видаляємо групу
    student_resp = await async_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": "student.temp@kpefk.lcloud.in.ua",
            "full_name": "Тимчасовий Студент",
            "role": "student",
            "group_id": group_id,
            "list_number": 7,
            "password": "TempPassword1!",
        },
    )
    assert student_resp.status_code == 201
    created_student_id = student_resp.json()["id"]
    assert student_resp.json()["group_code"] == "ПЗ-22"

    delete_resp = await async_client.delete(
        f"/api/v1/admin/groups/{group_id}",
        headers=headers,
    )
    assert delete_resp.status_code == 204

    # Перевіряємо, що група видалена, а в студента group_id став None
    refreshed_student_res = await db_session.execute(
        select(User).where(User.id == uuid.UUID(created_student_id))
    )
    refreshed_student = refreshed_student_res.scalar_one()
    assert isinstance(refreshed_student, User)
    assert refreshed_student.group_id is None


async def test_admin_users_crud_filters_and_safety_guards(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє CRUD користувачів, фільтри, зміну ролей/пароля та захист від небезпечних дій."""
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    headers = make_auth_headers(admin.id, admin.role)

    group_res = await db_session.execute(
        select(AcademicGroup).where(AcademicGroup.code == "КН-31")
    )
    group = group_res.scalar_one()
    assert isinstance(group, AcademicGroup)

    # 1. Створення студента з прив'язкою до групи і порядковим номером
    create_resp = await async_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": "New.Student@kpefk.lcloud.in.ua",
            "full_name": "Савченко Олександр Ігорович",
            "role": "student",
            "group_id": str(group.id),
            "list_number": 12,
            "password": "Password123!",
        },
    )
    assert create_resp.status_code == 201
    created_user = create_resp.json()
    new_user_id = created_user["id"]
    assert created_user["email"] == "new.student@kpefk.lcloud.in.ua"
    assert created_user["group_id"] == str(group.id)
    assert created_user["group_code"] == "КН-31"
    assert created_user["list_number"] == 12

    # 2. Вхід щойно створеним користувачем
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "new.student@kpefk.lcloud.in.ua",
            "password": "Password123!",
        },
    )
    assert login_resp.status_code == 200

    # 3. Дублікат email -> 409 USER_EMAIL_EXISTS
    dup_resp = await async_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": "NEW.STUDENT@kpefk.lcloud.in.ua",
            "full_name": "Інший Користувач",
            "role": "teacher",
            "password": "Password123!",
        },
    )
    assert dup_resp.status_code == 409
    assert dup_resp.json()["code"] == "USER_EMAIL_EXISTS"

    # 4. Фільтрація списку за роллю, групою та пошуком (перевірка кирилиці без регістру)
    filtered_resp = await async_client.get(
        "/api/v1/admin/users",
        headers=headers,
        params={
            "role": "student",
            "group_id": str(group.id),
            "search": "савченко",
        },
    )
    assert filtered_resp.status_code == 200
    filtered_users = filtered_resp.json()
    assert len(filtered_users) == 1
    assert filtered_users[0]["id"] == new_user_id

    # 5. Переведення студента у викладачі (group_id і list_number очищаються) + новий пароль
    patch_resp = await async_client.patch(
        f"/api/v1/admin/users/{new_user_id}",
        headers=headers,
        json={
            "full_name": "Савченко Олександр (Викладач)",
            "role": "teacher",
            "password": "NewPassword456!",
        },
    )
    assert patch_resp.status_code == 200
    patched_user = patch_resp.json()
    assert patched_user["role"] == "teacher"
    assert patched_user["group_id"] is None
    assert patched_user["group_code"] is None
    assert patched_user["list_number"] is None

    # Перевірка входу з новим паролем
    new_login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "new.student@kpefk.lcloud.in.ua",
            "password": "NewPassword456!",
        },
    )
    assert new_login_resp.status_code == 200

    # 6. Захист від зняття ролі admin з самого себе -> 409
    demote_self_resp = await async_client.patch(
        f"/api/v1/admin/users/{admin.id}",
        headers=headers,
        json={"role": "teacher"},
    )
    assert demote_self_resp.status_code == 409
    assert demote_self_resp.json()["code"] == "CANNOT_DEMOTE_SELF"

    # 7. Захист від самовидалення -> 409
    delete_self_resp = await async_client.delete(
        f"/api/v1/admin/users/{admin.id}",
        headers=headers,
    )
    assert delete_self_resp.status_code == 409
    assert delete_self_resp.json()["code"] == "CANNOT_DELETE_SELF"

    # 8. Захист від видалення викладача, який веде курси -> 409
    delete_teacher_resp = await async_client.delete(
        f"/api/v1/admin/users/{teacher.id}",
        headers=headers,
    )
    assert delete_teacher_resp.status_code == 409
    assert delete_teacher_resp.json()["code"] == "USER_HAS_COURSES"

    # 9. Видалення створеного користувача без курсів -> 204
    delete_new_resp = await async_client.delete(
        f"/api/v1/admin/users/{new_user_id}",
        headers=headers,
    )
    assert delete_new_resp.status_code == 204


async def test_academic_group_course_year_restricted_to_1_through_4(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє обмеження AcademicGroup.course_year діапазоном 1..4 у API, seed та БД."""
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    headers = make_auth_headers(admin.id, admin.role)

    # 1. Валідні граничні значення 1 та 4 приймаються
    create_y1 = await async_client.post(
        "/api/v1/admin/groups",
        headers=headers,
        json={
            "code": "КН-11",
            "specialty": "122 Комп'ютерні науки",
            "course_year": 1,
        },
    )
    assert create_y1.status_code == 201
    group_id = create_y1.json()["id"]

    patch_y4 = await async_client.patch(
        f"/api/v1/admin/groups/{group_id}",
        headers=headers,
        json={"course_year": 4},
    )
    assert patch_y4.status_code == 200
    assert patch_y4.json()["course_year"] == 4

    # 2. Значення поза 1..4 (0, 5, 6) відхиляються Pydantic із HTTP 422
    for invalid_year in (0, 5, 6):
        create_invalid = await async_client.post(
            "/api/v1/admin/groups",
            headers=headers,
            json={
                "code": f"КН-{invalid_year}1",
                "specialty": "122 Комп'ютерні науки",
                "course_year": invalid_year,
            },
        )
        assert create_invalid.status_code == 422

        patch_invalid = await async_client.patch(
            f"/api/v1/admin/groups/{group_id}",
            headers=headers,
            json={"course_year": invalid_year},
        )
        assert patch_invalid.status_code == 422

    # 3. Перевірка CheckConstraint безпосередньо на рівні БД
    db_session.add(
        AcademicGroup(
            code="КН-51",
            specialty="122 Комп'ютерні науки",
            course_year=5,
        )
    )
    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()

    # 4. Перевірка seed-даних: course_year у межах 1..4
    seed_bundle = build_seed_bundle()
    assert 1 <= seed_bundle.group.course_year <= 4


async def test_courses_restricted_strictly_to_4_disciplines(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє, що в системі присутні виключно 4 дисципліни (word, excel, access, html)."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    headers = make_auth_headers(teacher.id, teacher.role)

    # 1. Seed-набір містить строго 4 дисципліни у канонічному наборі
    seed_bundle = build_seed_bundle()
    assert len(seed_bundle.courses) == 4
    assert tuple(course.slug for course in seed_bundle.courses) == ALLOWED_COURSE_SLUGS

    # 2. API GET /courses повертає рівно 4 курси: word, excel, access, html
    list_resp = await async_client.get("/api/v1/courses", headers=headers)
    assert list_resp.status_code == 200
    courses_payload = list_resp.json()
    assert len(courses_payload) == 4
    returned_slugs = {item["slug"] for item in courses_payload}
    assert returned_slugs == {slug.value for slug in CourseSlug}

    # 3. Створення сторонньої дисципліни відхиляється з HTTP 422
    invalid_slug_resp = await async_client.post(
        "/api/v1/courses",
        headers=headers,
        json={
            "title": "Тестовий 5-й курс",
            "slug": "powerpoint",
            "description": "Зайвий тестовий курс",
        },
    )
    assert invalid_slug_resp.status_code == 422

    # 4. Повторне створення однієї з 4 наявних дисциплін відхиляється з HTTP 409
    duplicate_resp = await async_client.post(
        "/api/v1/courses",
        headers=headers,
        json={
            "title": "Дубль Word",
            "slug": "word",
            "description": "Спроба створити 5-й курс",
        },
    )
    assert duplicate_resp.status_code == 409
    assert duplicate_resp.json()["code"] == "COURSE_SLUG_EXISTS"
