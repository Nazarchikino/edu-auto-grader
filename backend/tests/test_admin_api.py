import io
import uuid

import docx
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.course import ALLOWED_COURSE_SLUGS, CourseSlug, Practical
from app.models.user import AcademicGroup, User, UserRole
from app.seed import build_seed_bundle
from app.services.quiz_service import calculate_variant_index, resolve_student_variant
from app.services.student_import_service import normalize_full_name, ukrainian_sort_key
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


def _build_college_import_docx(rows: list[list[str]]) -> bytes:
    """Генерує в пам'яті документ .docx із таблицею видачі облікових даних коледжу."""
    document = docx.Document()
    cols = max((len(row) for row in rows), default=4)
    table = document.add_table(rows=len(rows), cols=cols)
    for r_idx, row_values in enumerate(rows):
        for c_idx, cell_value in enumerate(row_values):
            table.cell(r_idx, c_idx).text = cell_value
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


async def test_ukrainian_alphabetical_sorting_and_apostrophe_normalization() -> None:
    """Перевіряє точний порядок української абетки (Ґ, Є, І, Ї) і нормалізацію апострофа."""
    assert normalize_full_name("Дем`яненко  Оксана") == "Дем'яненко Оксана"
    assert normalize_full_name("Лук’яненко Богдан") == "Лук'яненко Богдан"

    scrambled = [
        "Яковенко Олег",
        "Їжакевич Олена",
        "Іваненко Андрій",
        "Ищенко Марія",
        "Йосипенко Дмитро",
        "Євтушенко Софія",
        "Ефімов Максим",
        "Ґалаґан Тарас",
        "Галаган Василь",
        "Дем`яненко Оксана",
        "Даниленко Ігор",
        "Авраменко Артем",
    ]
    sorted_names = [
        normalize_full_name(name)
        for name in sorted(scrambled, key=ukrainian_sort_key)
    ]
    assert sorted_names == [
        "Авраменко Артем",
        "Галаган Василь",
        "Ґалаґан Тарас",
        "Даниленко Ігор",
        "Дем'яненко Оксана",
        "Ефімов Максим",
        "Євтушенко Софія",
        "Ищенко Марія",
        "Іваненко Андрій",
        "Їжакевич Олена",
        "Йосипенко Дмитро",
        "Яковенко Олег",
    ]


async def test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє імпорт таблиці .docx, українське сортування, варіанти й пропуск дублікатів."""
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    headers = make_auth_headers(admin.id, admin.role)

    # Створюємо порожню групу для перевірки нумерації з 1
    group_resp = await async_client.post(
        "/api/v1/admin/groups",
        headers=headers,
        json={
            "code": "ПЗ-21",
            "specialty": "121 Інженерія програмного забезпечення",
            "course_year": 2,
        },
    )
    assert group_resp.status_code == 201
    group_id = group_resp.json()["id"]

    docx_bytes = _build_college_import_docx(
        [
            ["ПІБ", "Логін", "E-mail", "Пароль", "Дод. інформація"],
            ["Їжакевич Олена Петрівна", "yizhak.o", "", "Yizhak2026", "ПЗ-21"],
            [
                "Іваненко Андрій Сергійович",
                "ivanenko.a",
                "ivanenko.a@kpefk.com.ua",
                "Ivan2026",
                "ПЗ-21",
            ],
            [
                "Євтушенко Софія Іванівна",
                "yevtushenko.s",
                "yevtushenko.s@kpefk.com.ua",
                "Yevt2026",
                "ПЗ-21",
            ],
            [
                "Ґалаґан Тарас Олегович",
                "galagan.t",
                "galagan.t@kpefk.com.ua",
                "Gala2026",
                "ПЗ-21",
            ],
            [
                "Дем`яненко Оксана Вікторівна",
                "demyanenko.o",
                "demyanenko.o@kpefk.com.ua",
                "Demy2026",
                "ПЗ-21",
            ],
            [
                "Лук’яненко Богдан Романович",
                "lukyanenko.b",
                "lukyanenko.b@kpefk.com.ua",
                "Luky2026",
                "ПЗ-21",
            ],
            # Дублікат наявного email із seed.py — має бути пропущений без переривання імпорту
            ["Бондаренко Дубль", "student1", "student1@kpefk.lcloud.in.ua", "DupPass1", "ПЗ-21"],
            # Дублікат email всередині того ж файлу
            ["Іваненко Копія", "ivanenko.a", "IVANENKO.A@kpefk.com.ua", "DupPass2", "ПЗ-21"],
        ]
    )

    import_resp = await async_client.post(
        "/api/v1/admin/users/import",
        headers=headers,
        data={"group_id": group_id},
        files={
            "file": (
                "vidomist_pz21.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert import_resp.status_code == 200
    payload = import_resp.json()

    assert payload["group_id"] == group_id
    assert payload["group_code"] == "ПЗ-21"
    assert payload["total_variants"] == 3
    assert payload["created_count"] == 6
    assert payload["skipped_count"] == 2

    created = payload["created"]
    # Перевіряємо український алфавітний порядок: Ґ < Д < Є < І < Ї < Л
    assert [item["full_name"] for item in created] == [
        "Ґалаґан Тарас Олегович",
        "Дем'яненко Оксана Вікторівна",
        "Євтушенко Софія Іванівна",
        "Іваненко Андрій Сергійович",
        "Їжакевич Олена Петрівна",
        "Лук'яненко Богдан Романович",
    ]
    # Перевіряємо присвоєні list_number (без прогалин) і розраховані variant_number
    assert [item["list_number"] for item in created] == [1, 2, 3, 4, 5, 6]
    assert [item["variant_number"] for item in created] == [
        calculate_variant_index(n, 3) + 1 for n in range(1, 7)
    ]
    # Перевіряємо формування {login}@kpefk.com.ua для рядка без заповненої колонки E-mail
    assert created[4]["email"] == "yizhak.o@kpefk.com.ua"
    assert created[4]["temp_password"] == "Yizhak2026"

    # Перевіряємо узгодженість variant_number із практичною через resolve_student_variant
    practical_result = await db_session.execute(select(Practical).limit(1))
    practical = practical_result.scalar_one()
    assert isinstance(practical, Practical)
    for item in created:
        _v_idx, resolved_variant_number, _variant_obj = resolve_student_variant(
            practical,
            item["list_number"],
        )
        assert item["variant_number"] == resolved_variant_number

    # Перевіряємо запис у БД та успішну автентифікацію імпортованого студента
    db_student = await _get_user_by_email(db_session, "yizhak.o@kpefk.com.ua")
    assert db_student.role == UserRole.STUDENT
    assert db_student.group_id == uuid.UUID(group_id)
    assert db_student.list_number == 5

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "yizhak.o@kpefk.com.ua",
            "password": "Yizhak2026",
        },
    )
    assert login_resp.status_code == 200

    # Перевіряємо деталі пропусків дублікатів
    skipped_emails = {entry["email"] for entry in payload["skipped"]}
    assert skipped_emails == {"student1@kpefk.lcloud.in.ua", "ivanenko.a@kpefk.com.ua"}


async def test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє імпорт .txt, генерацію email/пароля, продовження list_number і дублікати."""
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    headers = make_auth_headers(admin.id, admin.role)

    # У групі КН-31 із seed.py вже є 3 студенти з list_number 1, 2, 3
    group_res = await db_session.execute(
        select(AcademicGroup).where(AcademicGroup.code == "КН-31")
    )
    group = group_res.scalar_one()
    assert isinstance(group, AcademicGroup)

    txt_content = "\n".join(
        [
            "",
            "Їжак Роман Іванович; yizhak.r@kpefk.com.ua; CustomPass1",
            "   ",
            "Єременко Ольга Сергіївна; yeremenko.o@kpefk.com.ua",
            "Іванчук Антон Петрович",
            "Іванчук Андрій Олегович",
            "Ґудзь Ірина Василівна",
            "Бондаренко Ірина Василівна; student1@kpefk.lcloud.in.ua; IgnoredPass",
            "",
        ]
    ).encode("utf-8")

    import_resp = await async_client.post(
        "/api/v1/admin/users/import",
        headers=headers,
        data={"group_id": str(group.id)},
        files={"file": ("students_kn31.txt", txt_content, "text/plain")},
    )
    assert import_resp.status_code == 200
    payload = import_resp.json()

    assert payload["group_code"] == "КН-31"
    assert payload["created_count"] == 5
    assert payload["skipped_count"] == 1
    assert payload["skipped"][0]["email"] == "student1@kpefk.lcloud.in.ua"

    created = payload["created"]
    # Очікуваний порядок за українською абеткою: Ґ < Є < І (Андрій < Антон) < Ї
    assert [item["full_name"] for item in created] == [
        "Ґудзь Ірина Василівна",
        "Єременко Ольга Сергіївна",
        "Іванчук Андрій Олегович",
        "Іванчук Антон Петрович",
        "Їжак Роман Іванович",
    ]
    # Продовження нумерації після існуючого max(list_number) = 3 -> 4, 5, 6, 7, 8
    assert [item["list_number"] for item in created] == [4, 5, 6, 7, 8]
    assert [item["variant_number"] for item in created] == [1, 2, 3, 1, 2]

    # Автогенерація унікальних транслітерованих email і 8-символьних паролів
    assert created[0]["email"] == "gudz.i@kpefk.com.ua"
    assert len(created[0]["temp_password"]) == 8

    assert created[1]["email"] == "yeremenko.o@kpefk.com.ua"
    assert len(created[1]["temp_password"]) == 8

    assert created[2]["email"] == "ivanchuk.a@kpefk.com.ua"
    assert created[3]["email"] == "ivanchuk.a2@kpefk.com.ua"
    assert len(created[2]["temp_password"]) == 8
    assert len(created[3]["temp_password"]) == 8

    assert created[4]["email"] == "yizhak.r@kpefk.com.ua"
    assert created[4]["temp_password"] == "CustomPass1"

    # Перевірка входу зі згенерованими обліковими даними
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": created[0]["email"],
            "password": created[0]["temp_password"],
        },
    )
    assert login_resp.status_code == 200


async def test_admin_bulk_import_rbac_and_validation_errors(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє RBAC (403) і коректні коди помилок для некоректних файлів та груп."""
    student = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")

    group_res = await db_session.execute(
        select(AcademicGroup).where(AcademicGroup.code == "КН-31")
    )
    group = group_res.scalar_one()
    assert isinstance(group, AcademicGroup)

    sample_txt = "Авраменко Іван\n".encode()

    # 1. Студент і викладач не мають доступу -> 403 FORBIDDEN
    for user in (student, teacher):
        resp = await async_client.post(
            "/api/v1/admin/users/import",
            headers=make_auth_headers(user.id, user.role),
            data={"group_id": str(group.id)},
            files={"file": ("list.txt", sample_txt, "text/plain")},
        )
        assert resp.status_code == 403
        assert resp.json()["code"] == "FORBIDDEN"

    admin_headers = make_auth_headers(admin.id, admin.role)

    # 2. Неіснуюча група -> 404 GROUP_NOT_FOUND
    missing_group_resp = await async_client.post(
        "/api/v1/admin/users/import",
        headers=admin_headers,
        data={"group_id": str(uuid.uuid4())},
        files={"file": ("list.txt", sample_txt, "text/plain")},
    )
    assert missing_group_resp.status_code == 404
    assert missing_group_resp.json()["code"] == "GROUP_NOT_FOUND"

    # 3. Непідтримуване розширення -> 415 INVALID_FILE_FORMAT
    bad_ext_resp = await async_client.post(
        "/api/v1/admin/users/import",
        headers=admin_headers,
        data={"group_id": str(group.id)},
        files={"file": ("list.csv", sample_txt, "text/csv")},
    )
    assert bad_ext_resp.status_code == 415
    assert bad_ext_resp.json()["code"] == "INVALID_FILE_FORMAT"

    # 4. Пошкоджений .docx -> 415 INVALID_FILE_FORMAT
    corrupt_docx_resp = await async_client.post(
        "/api/v1/admin/users/import",
        headers=admin_headers,
        data={"group_id": str(group.id)},
        files={"file": ("broken.docx", b"not-a-valid-zip-docx", "application/octet-stream")},
    )
    assert corrupt_docx_resp.status_code == 415
    assert corrupt_docx_resp.json()["code"] == "INVALID_FILE_FORMAT"

    # 5. Порожній .txt -> 422 EMPTY_IMPORT_FILE
    empty_txt_resp = await async_client.post(
        "/api/v1/admin/users/import",
        headers=admin_headers,
        data={"group_id": str(group.id)},
        files={"file": ("empty.txt", b"   \n\n  ", "text/plain")},
    )
    assert empty_txt_resp.status_code == 422
    assert empty_txt_resp.json()["code"] == "EMPTY_IMPORT_FILE"
