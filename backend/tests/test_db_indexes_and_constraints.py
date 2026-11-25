import importlib.util
import json
import uuid
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import Base
from app.core.security import hash_password
from app.models.course import Course, CourseSlug, Module, QuizQuestion
from app.models.progress import QuizAttempt, Submission
from app.models.user import AcademicGroup, User, UserRole
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


async def test_quiz_questions_preserve_order_index_independently_of_uuids(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє order_index 1..N при сидінгу, створенні та поверненні з API незалежно від UUID."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    student = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    student_headers = make_auth_headers(student.id, student.role)

    # 1. Засіяні питання з html.json зберігають порядок JSON (order_index 1..N) у БД і API
    html_json = json.loads(
        (settings.COURSE_CONTENT_DIR / "html.json").read_text(encoding="utf-8")
    )
    expected_m1_texts = [
        item["question_text"]
        for item in html_json["modules"][0]["quiz_questions"]
    ]

    html_course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.HTML))
    ).scalar_one()
    assert isinstance(html_course, Course)

    html_m1 = (
        await db_session.execute(
            select(Module).where(
                Module.course_id == html_course.id,
                Module.order_index == 1,
            )
        )
    ).scalar_one()
    assert isinstance(html_m1, Module)

    seeded_questions = list(
        (
            await db_session.execute(
                select(QuizQuestion)
                .where(QuizQuestion.module_id == html_m1.id)
                .order_by(QuizQuestion.order_index.asc(), QuizQuestion.id.asc())
            )
        )
        .scalars()
        .all()
    )
    assert [q.order_index for q in seeded_questions] == list(
        range(1, len(expected_m1_texts) + 1)
    )
    assert [q.question_text for q in seeded_questions] == expected_m1_texts

    m1_student_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}",
        headers=student_headers,
    )
    assert m1_student_resp.status_code == 200
    assert [
        item["question_text"] for item in m1_student_resp.json()["quiz_questions"]
    ] == expected_m1_texts

    m1_teacher_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}/quiz/questions",
        headers=teacher_headers,
    )
    assert m1_teacher_resp.status_code == 200
    assert [item["question_text"] for item in m1_teacher_resp.json()] == expected_m1_texts

    # 2. Новий модуль із питаннями, чиї UUID навмисно спадають (ffff > 8888 > 0000),
    # але order_index зростає 1, 2, 3 -> API має повертати порядок за order_index, а не UUID
    create_mod_resp = await async_client.post(
        f"/api/v1/courses/{html_course.id}/modules",
        headers=teacher_headers,
        json={
            "order_index": 77,
            "title": "Тестовий модуль порядку питань",
            "lecture_content": "Конспект лекції для перевірки порядку питань.",
        },
    )
    assert create_mod_resp.status_code == 201
    custom_module_id = uuid.UUID(create_mod_resp.json()["id"])

    crafted_questions = [
        QuizQuestion(
            id=uuid.UUID("ffffffff-0000-4000-8000-000000000001"),
            module_id=custom_module_id,
            order_index=1,
            question_text="Питання №1 (найбільший UUID)",
            options=["Так", "Ні"],
            correct_option_index=0,
        ),
        QuizQuestion(
            id=uuid.UUID("88888888-0000-4000-8000-000000000002"),
            module_id=custom_module_id,
            order_index=2,
            question_text="Питання №2 (середній UUID)",
            options=["А", "Б"],
            correct_option_index=1,
        ),
        QuizQuestion(
            id=uuid.UUID("00000001-0000-4000-8000-000000000003"),
            module_id=custom_module_id,
            order_index=3,
            question_text="Питання №3 (найменший UUID)",
            options=["X", "Y"],
            correct_option_index=0,
        ),
    ]
    db_session.add_all(crafted_questions)
    await db_session.commit()

    # 3. Створення нових питань через API автоматично призначає max(order_index) + 1 (4 та 5)
    q4_resp = await async_client.post(
        f"/api/v1/modules/{custom_module_id}/quiz/questions",
        headers=teacher_headers,
        json={
            "question_text": "Питання №4 (додане через API)",
            "options": ["Опція 1", "Опція 2"],
            "correct_option_index": 1,
        },
    )
    assert q4_resp.status_code == 201
    q4_id = uuid.UUID(q4_resp.json()["id"])

    q5_resp = await async_client.post(
        f"/api/v1/modules/{custom_module_id}/quiz/questions",
        headers=teacher_headers,
        json={
            "question_text": "Питання №5 (додане через API)",
            "options": ["Варіант 1", "Варіант 2"],
            "correct_option_index": 0,
        },
    )
    assert q5_resp.status_code == 201
    q5_id = uuid.UUID(q5_resp.json()["id"])

    db_ordered = list(
        (
            await db_session.execute(
                select(QuizQuestion)
                .where(QuizQuestion.module_id == custom_module_id)
                .order_by(QuizQuestion.order_index.asc(), QuizQuestion.id.asc())
            )
        )
        .scalars()
        .all()
    )
    assert [q.order_index for q in db_ordered] == [1, 2, 3, 4, 5]
    assert db_ordered[3].id == q4_id
    assert db_ordered[4].id == q5_id

    expected_texts = [
        "Питання №1 (найбільший UUID)",
        "Питання №2 (середній UUID)",
        "Питання №3 (найменший UUID)",
        "Питання №4 (додане через API)",
        "Питання №5 (додане через API)",
    ]

    mod_detail_resp = await async_client.get(
        f"/api/v1/modules/{custom_module_id}",
        headers=student_headers,
    )
    assert mod_detail_resp.status_code == 200
    assert [
        item["question_text"] for item in mod_detail_resp.json()["quiz_questions"]
    ] == expected_texts

    teacher_list_resp = await async_client.get(
        f"/api/v1/modules/{custom_module_id}/quiz/questions",
        headers=teacher_headers,
    )
    assert teacher_list_resp.status_code == 200
    teacher_questions = teacher_list_resp.json()
    assert [item["question_text"] for item in teacher_questions] == expected_texts

    # 4. QuizService коректно оцінює повну здачу тесту для впорядкованих питань
    submit_resp = await async_client.post(
        f"/api/v1/modules/{custom_module_id}/quiz/submit",
        headers=student_headers,
        json={
            "answers": [
                {
                    "question_id": item["id"],
                    "selected_option_index": item["correct_option_index"],
                }
                for item in teacher_questions
            ]
        },
    )
    assert submit_resp.status_code == 200
    assert submit_resp.json()["passed"] is True
    assert submit_resp.json()["correct_count"] == 5

    # 5. Після видалення питання №2 наступне створене питання отримує order_index = 6
    del_q2_resp = await async_client.delete(
        "/api/v1/quiz/questions/88888888-0000-4000-8000-000000000002",
        headers=teacher_headers,
    )
    assert del_q2_resp.status_code == 204

    q6_resp = await async_client.post(
        f"/api/v1/modules/{custom_module_id}/quiz/questions",
        headers=teacher_headers,
        json={
            "question_text": "Питання №6 (після видалення №2)",
            "options": ["Так", "Ні"],
            "correct_option_index": 0,
        },
    )
    assert q6_resp.status_code == 201
    q6_row = (
        await db_session.execute(
            select(QuizQuestion).where(QuizQuestion.id == uuid.UUID(q6_resp.json()["id"]))
        )
    ).scalar_one()
    assert q6_row.order_index == 6


async def test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє 409 Conflict для дубліката (group_id, list_number) і дозвіл у різних групах."""
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    headers = make_auth_headers(admin.id, admin.role)

    group_a = (
        await db_session.execute(
            select(AcademicGroup).where(AcademicGroup.code == "КН-31")
        )
    ).scalar_one()
    assert isinstance(group_a, AcademicGroup)
    assert student1.group_id == group_a.id
    assert student1.list_number == 1

    group_b_resp = await async_client.post(
        "/api/v1/admin/groups",
        headers=headers,
        json={
            "code": "КН-32",
            "specialty": "122 Комп'ютерні науки",
            "course_year": 3,
        },
    )
    assert group_b_resp.status_code == 201
    group_b_id = group_b_resp.json()["id"]

    # 1. Дубльований list_number=1 у тій самій групі КН-31 -> 409 Conflict
    dup_create_resp = await async_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": "dup.listnum@kpefk.lcloud.in.ua",
            "full_name": "Дублікат Номера У Списку",
            "role": "student",
            "group_id": str(group_a.id),
            "list_number": 1,
            "password": "Password123!",
        },
    )
    assert dup_create_resp.status_code == 409
    dup_body = dup_create_resp.json()
    assert dup_body["code"] == "USER_GROUP_LIST_NUMBER_EXISTS"
    assert "№1" in dup_body["detail"]

    # 2. Той самий list_number=1 в іншій групі КН-32 -> 201 Created (дозволено)
    other_group_resp = await async_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": "kn32.student1@kpefk.lcloud.in.ua",
            "full_name": "Перший Студент КН-32",
            "role": "student",
            "group_id": group_b_id,
            "list_number": 1,
            "password": "Password123!",
        },
    )
    assert other_group_resp.status_code == 201
    kn32_student_id = other_group_resp.json()["id"]

    # 3. Частковий унікальний індекс дозволяє кількох студентів з list_number=None в одній групі
    null_num_1 = await async_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": "null.num1@kpefk.lcloud.in.ua",
            "full_name": "Студент Без Номера 1",
            "role": "student",
            "group_id": str(group_a.id),
            "list_number": None,
            "password": "Password123!",
        },
    )
    assert null_num_1.status_code == 201
    null_num_1_id = null_num_1.json()["id"]

    null_num_2 = await async_client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": "null.num2@kpefk.lcloud.in.ua",
            "full_name": "Студент Без Номера 2",
            "role": "student",
            "group_id": str(group_a.id),
            "list_number": None,
            "password": "Password123!",
        },
    )
    assert null_num_2.status_code == 201

    # 4. PATCH: переведення студента з КН-32 (list_number=1) у КН-31 -> 409 Conflict
    move_conflict_resp = await async_client.patch(
        f"/api/v1/admin/users/{kn32_student_id}",
        headers=headers,
        json={"group_id": str(group_a.id)},
    )
    assert move_conflict_resp.status_code == 409
    assert move_conflict_resp.json()["code"] == "USER_GROUP_LIST_NUMBER_EXISTS"

    # 5. PATCH: присвоєння зайнятого list_number=1 студенту групи КН-31 -> 409 Conflict
    patch_conflict_resp = await async_client.patch(
        f"/api/v1/admin/users/{null_num_1_id}",
        headers=headers,
        json={"list_number": 1},
    )
    assert patch_conflict_resp.status_code == 409
    assert patch_conflict_resp.json()["code"] == "USER_GROUP_LIST_NUMBER_EXISTS"

    # 6. PATCH: оновлення власного профілю student1 зі збереженням list_number=1 -> 200 OK
    self_patch_resp = await async_client.patch(
        f"/api/v1/admin/users/{student1.id}",
        headers=headers,
        json={"full_name": "Бондаренко Ірина Василівна (оновлено)", "list_number": 1},
    )
    assert self_patch_resp.status_code == 200
    assert self_patch_resp.json()["list_number"] == 1

    # 7. Обмеження працює на рівні самої БД (частковий унікальний індекс uq_users_group_list_number)
    db_session.add(
        User(
            email="raw.db.conflict@kpefk.lcloud.in.ua",
            password_hash=hash_password("Password123!"),
            full_name="Прямий Конфлікт БД",
            role=UserRole.STUDENT,
            group_id=group_a.id,
            list_number=1,
        )
    )
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


async def test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє видалення модуля й перенумерацію 1..N при uq_modules_course_order_index."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    headers = make_auth_headers(teacher.id, teacher.role)

    html_course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.HTML))
    ).scalar_one()
    assert isinstance(html_course, Course)

    # Очищуємо модулі курсу HTML та додаємо 4 модулі зі спадними UUID для тесту flush-порядку
    await db_session.execute(delete(Module).where(Module.course_id == html_course.id))
    await db_session.commit()

    m1_id = uuid.UUID("ffffffff-0000-4000-8000-000000000001")
    m2_id = uuid.UUID("cccccccc-0000-4000-8000-000000000002")
    m3_id = uuid.UUID("88888888-0000-4000-8000-000000000003")
    m4_id = uuid.UUID("00000001-0000-4000-8000-000000000004")

    db_session.add_all(
        [
            Module(
                id=m1_id,
                course_id=html_course.id,
                order_index=1,
                title="Модуль 1",
                lecture_content="Лекція 1",
            ),
            Module(
                id=m2_id,
                course_id=html_course.id,
                order_index=2,
                title="Модуль 2",
                lecture_content="Лекція 2",
            ),
            Module(
                id=m3_id,
                course_id=html_course.id,
                order_index=3,
                title="Модуль 3",
                lecture_content="Лекція 3",
            ),
            Module(
                id=m4_id,
                course_id=html_course.id,
                order_index=4,
                title="Модуль 4",
                lecture_content="Лекція 4",
            ),
        ]
    )
    await db_session.commit()

    # 1. Дублікат (course_id, order_index) повертає 409 у POST/PATCH і IntegrityError у БД
    dup_mod_resp = await async_client.post(
        f"/api/v1/courses/{html_course.id}/modules",
        headers=headers,
        json={
            "order_index": 2,
            "title": "Дубльований модуль",
            "lecture_content": "Контент",
        },
    )
    assert dup_mod_resp.status_code == 409
    assert dup_mod_resp.json()["code"] == "MODULE_ORDER_INDEX_EXISTS"

    patch_dup_resp = await async_client.patch(
        f"/api/v1/modules/{m3_id}",
        headers=headers,
        json={"order_index": 2},
    )
    assert patch_dup_resp.status_code == 409
    assert patch_dup_resp.json()["code"] == "MODULE_ORDER_INDEX_EXISTS"

    db_session.add(
        Module(
            course_id=html_course.id,
            order_index=2,
            title="Прямий дублікат БД",
            lecture_content="Лекція",
        )
    )
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # 2. Видалення першого модуля (зсув 2->1, 3->2, 4->3 попри спадні UUID) проходить без конфлікту
    del_first_resp = await async_client.delete(
        f"/api/v1/modules/{m1_id}",
        headers=headers,
    )
    assert del_first_resp.status_code == 204

    remaining_1 = list(
        (
            await db_session.execute(
                select(Module)
                .where(Module.course_id == html_course.id)
                .order_by(Module.order_index.asc(), Module.id.asc())
            )
        )
        .scalars()
        .all()
    )
    assert [m.id for m in remaining_1] == [m2_id, m3_id, m4_id]
    assert [m.order_index for m in remaining_1] == [1, 2, 3]

    # 3. Видалення середнього модуля (m3, order_index=2 -> m4 стає 2) також проходить без конфлікту
    del_mid_resp = await async_client.delete(
        f"/api/v1/modules/{m3_id}",
        headers=headers,
    )
    assert del_mid_resp.status_code == 204

    remaining_2 = list(
        (
            await db_session.execute(
                select(Module)
                .where(Module.course_id == html_course.id)
                .order_by(Module.order_index.asc(), Module.id.asc())
            )
        )
        .scalars()
        .all()
    )
    assert [m.id for m in remaining_2] == [m2_id, m4_id]
    assert [m.order_index for m in remaining_2] == [1, 2]


async def test_schema_indexes_constraints_and_alembic_0004_backfill(
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє наявність усіх індексів/обмежень у ORM і БД та коректність міграції 0004."""
    expected_indexes: dict[str, set[str]] = {
        Course.__tablename__: {"ix_courses_teacher_id"},
        Module.__tablename__: {"ix_modules_course_order"},
        QuizQuestion.__tablename__: {"ix_quiz_questions_module_order"},
        QuizAttempt.__tablename__: {"ix_quiz_attempts_student_module"},
        Submission.__tablename__: {
            "ix_submissions_student_practical",
            "ix_submissions_practical_submitted_at",
        },
        User.__tablename__: {
            "ix_users_group_id",
            "uq_users_group_list_number",
        },
    }

    for table_name, index_names in expected_indexes.items():
        table = Base.metadata.tables[table_name]
        metadata_index_names = {idx.name for idx in table.indexes}
        assert index_names.issubset(metadata_index_names), (
            f"У таблиці {table_name} відсутні очікувані індекси: "
            f"{index_names - metadata_index_names}"
        )

    module_constraints = {
        c.name for c in Base.metadata.tables[Module.__tablename__].constraints
    }
    assert "uq_modules_course_order_index" in module_constraints

    sqlite_indexes_res = await db_session.execute(
        text("SELECT name FROM sqlite_master WHERE type = 'index'")
    )
    sqlite_index_names = {row[0] for row in sqlite_indexes_res.all()}
    for index_names in expected_indexes.values():
        assert index_names.issubset(sqlite_index_names)

    # Перевіряємо ревізію та ланцюжок Alembic 0004
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0004_add_indexes_constraints_and_quiz_order.py"
    )
    assert migration_path.is_file()
    spec = importlib.util.spec_from_file_location("migration_0004", migration_path)
    assert spec is not None and spec.loader is not None
    migration_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_module)
    assert migration_module.down_revision == "0003_add_user_auth_security_fields"

    # Перевіряємо backfill SQL (ROW_NUMBER() OVER (PARTITION BY module_id ORDER BY id))
    await db_session.execute(text("UPDATE quiz_questions SET order_index = 0"))
    await db_session.execute(
        text(
            """
            UPDATE quiz_questions
            SET order_index = numbered.rn
            FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (PARTITION BY module_id ORDER BY id) AS rn
                FROM quiz_questions
            ) AS numbered
            WHERE quiz_questions.id = numbered.id
            """
        )
    )
    await db_session.commit()

    rows = (
        await db_session.execute(
            select(QuizQuestion.module_id, QuizQuestion.order_index).order_by(
                QuizQuestion.module_id.asc(),
                QuizQuestion.order_index.asc(),
            )
        )
    ).all()
    by_module: dict[uuid.UUID, list[int]] = {}
    for module_id, order_idx in rows:
        by_module.setdefault(module_id, []).append(order_idx)

    assert len(by_module) > 0
    for module_id, indices in by_module.items():
        assert indices == list(range(1, len(indices) + 1)), (
            f"Некоректний backfill order_index для module_id={module_id}: {indices}"
        )
