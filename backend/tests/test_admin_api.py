import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.user import AcademicGroup, User
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
