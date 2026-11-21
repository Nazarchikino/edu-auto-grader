import json
import re
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.core.config import settings
from app.core.security import hash_password
from app.models.course import (
    ALLOWED_COURSE_SLUGS,
    Course,
    CourseSlug,
    Module,
    Practical,
    QuizQuestion,
)
from app.models.progress import QuizAttempt, Submission
from app.models.user import AcademicGroup, User, UserRole
from app.schemas.grading import GradingRule
from app.seed import build_seed_bundle, seed_database, summarize_bundle
from tests.conftest import (
    SqliteAsyncSessionAdapter,
    build_sample_docx,
    make_auth_headers,
)

_MEDIA_URL_PATTERN = re.compile(r"/media/courses/[^\s\"'\)>]+")


def test_full_course_json_bundle_validation() -> None:
    """Перевіряє цілісність повного JSON-пакета 4 курсів, правил GradingRule та медіафайлів."""
    bundle = build_seed_bundle()
    summary = summarize_bundle(bundle)

    assert summary.courses_count == 4
    assert tuple(course.slug for course in bundle.courses) == ALLOWED_COURSE_SLUGS
    assert summary.modules_count == 40
    assert summary.practicals_count == 37
    assert summary.questions_count == 240
    assert summary.variants_count == 254

    media_references: set[str] = set()
    validated_rules_count = 0

    for course in bundle.courses:
        assert course.modules
        for module in course.modules:
            media_references.update(_MEDIA_URL_PATTERN.findall(module.lecture_content))
            for question in module.quiz_questions:
                assert len(question.options) >= 2
                assert 0 <= question.correct_option_index < len(question.options)

            if module.practical is not None:
                practical = module.practical
                media_references.update(_MEDIA_URL_PATTERN.findall(practical.instructions))
                variants_json = json.dumps(practical.variants, ensure_ascii=False)
                media_references.update(_MEDIA_URL_PATTERN.findall(variants_json))

                assert not hasattr(practical, "meta")
                assert len(practical.grading_rules) >= 1
                for raw_rule in practical.grading_rules:
                    parsed_rule = GradingRule.model_validate(raw_rule)
                    assert parsed_rule.points > 0
                    validated_rules_count += 1

    assert validated_rules_count >= 190
    assert len(media_references) > 0

    media_root = settings.COURSE_MEDIA_DIR
    assert media_root.is_dir()

    missing_files: list[str] = []
    for raw_ref in sorted(media_references):
        clean_ref = raw_ref.rstrip(".,;")
        rel_path = clean_ref.removeprefix("/media/courses/")
        candidate = media_root / rel_path
        if not candidate.is_file():
            missing_files.append(clean_ref)

    assert missing_files == [], f"Відсутні медіафайли курсів на диску: {missing_files}"

    disk_media_files = [path for path in media_root.rglob("*") if path.is_file()]
    assert len(disk_media_files) == 184


@pytest.mark.asyncio
async def test_media_courses_static_serving(async_client: AsyncClient) -> None:
    """Перевіряє статичну роздачу медіафайлів курсів через GET /media/courses/..."""
    sample_media_paths = (
        ("/media/courses/access/lectures/1.1.webp", b"RIFF"),
        ("/media/courses/access/lectures/1.5.png", b"\x89PNG"),
        ("/media/courses/excel/test/question16.jpg", b"\xff\xd8\xff"),
        ("/media/courses/excel/excel-tutorial.pdf", b"%PDF-"),
    )

    for url_path, expected_magic in sample_media_paths:
        response = await async_client.get(url_path)
        assert response.status_code == 200, f"Очікувався 200 OK для {url_path}"
        assert response.content.startswith(expected_magic)

    missing_response = await async_client.get("/media/courses/word/does-not-exist.png")
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_seed_database_sync_courses_preserves_users_and_groups(
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє ідемпотентність seed та режим --sync-courses зі збереженням користувачів і груп."""
    extra_group = AcademicGroup(
        code="ІПЗ-21",
        specialty="121 Інженерія програмного забезпечення",
        course_year=2,
    )
    db_session.add(extra_group)
    await db_session.flush()

    extra_student = User(
        email="custom.student@kpefk.com.ua",
        password_hash=hash_password("Custom123!"),
        full_name="Коваленко Марія Ігорівна",
        role=UserRole.STUDENT,
        group_id=extra_group.id,
        list_number=1,
    )
    db_session.add(extra_student)

    # Навмисно змінюємо заголовок курсу та видаляємо один модуль
    word_course_res = await db_session.execute(
        select(Course).where(Course.slug == CourseSlug.WORD)
    )
    word_course = word_course_res.scalar_one()
    assert isinstance(word_course, Course)
    original_course_id = word_course.id
    word_course.title = "Тимчасова змінена назва Word"

    first_mod_res = await db_session.execute(
        select(Module)
        .where(Module.course_id == word_course.id)
        .order_by(Module.order_index.asc())
        .limit(1)
    )
    first_mod = first_mod_res.scalar_one()
    await db_session.delete(first_mod)
    await db_session.commit()

    # 1. Без --sync-courses існуючі курси НЕ перезаписуються (ідемпотентна поведінка)
    # justified Any: SqliteAsyncSessionAdapter structural duck-typing for AsyncSession
    typed_db: Any = db_session
    await seed_database(typed_db, sync_courses=False)

    word_after_noop_res = await db_session.execute(
        select(Course).where(Course.slug == CourseSlug.WORD)
    )
    word_after_noop = word_after_noop_res.scalar_one()
    assert word_after_noop.title == "Тимчасова змінена назва Word"

    modules_after_noop_res = await db_session.execute(select(func.count(Module.id)))
    assert int(modules_after_noop_res.scalar_one()) == 39

    # 2. Із --sync-courses курси перезаписуються з JSON, а користувачі та групи зберігаються
    summary = await seed_database(typed_db, sync_courses=True)
    assert summary.courses_count == 4
    assert summary.modules_count == 40
    assert summary.practicals_count == 37
    assert summary.questions_count == 240

    word_synced_res = await db_session.execute(
        select(Course).where(Course.slug == CourseSlug.WORD)
    )
    word_synced = word_synced_res.scalar_one()
    assert word_synced.id == original_course_id
    assert word_synced.title != "Тимчасова змінена назва Word"

    modules_count_res = await db_session.execute(select(func.count(Module.id)))
    practicals_count_res = await db_session.execute(select(func.count(Practical.id)))
    questions_count_res = await db_session.execute(select(func.count(QuizQuestion.id)))
    assert int(modules_count_res.scalar_one()) == 40
    assert int(practicals_count_res.scalar_one()) == 37
    assert int(questions_count_res.scalar_one()) == 240

    # Користувачі та академічні групи залишилися недоторканими
    extra_group_check = await db_session.execute(
        select(AcademicGroup).where(AcademicGroup.code == "ІПЗ-21")
    )
    assert extra_group_check.scalar_one_or_none() is not None

    extra_student_check = await db_session.execute(
        select(User).where(User.email == "custom.student@kpefk.com.ua")
    )
    assert extra_student_check.scalar_one_or_none() is not None


async def _get_user_by_email(
    db_session: SqliteAsyncSessionAdapter,
    email: str,
) -> User:
    """Повертає користувача з тестової БД за його email."""
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    assert isinstance(user, User)
    return user


@pytest.mark.asyncio
async def test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє видалення модуля викладачем/адміном: каскад, файли й перенумерацію 1..N."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    student2 = await _get_user_by_email(db_session, "student2@kpefk.lcloud.in.ua")
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    admin_headers = make_auth_headers(admin.id, admin.role)

    course_res = await db_session.execute(
        select(Course).where(Course.slug == CourseSlug.WORD)
    )
    course = course_res.scalar_one()
    assert isinstance(course, Course)

    # Попередньо завантажуємо курс через API, щоб перевірити коректність identity map у сесії
    before_course_resp = await async_client.get(
        f"/api/v1/courses/{course.id}",
        headers=teacher_headers,
    )
    assert before_course_resp.status_code == 200

    all_modules_res = await db_session.execute(
        select(Module)
        .where(Module.course_id == course.id)
        .order_by(Module.order_index.asc(), Module.id.asc())
    )
    all_modules = list(all_modules_res.scalars().all())
    assert len(all_modules) >= 3

    practical_rows_res = await db_session.execute(
        select(Module, Practical)
        .join(Practical, Practical.module_id == Module.id)
        .where(Module.course_id == course.id)
        .order_by(Module.order_index.asc())
    )
    practical_pairs = list(practical_rows_res.all())
    assert len(practical_pairs) >= 2

    surviving_module, surviving_practical = practical_pairs[0]
    target_module, target_practical = practical_pairs[1]
    assert isinstance(surviving_module, Module)
    assert isinstance(surviving_practical, Practical)
    assert isinstance(target_module, Module)
    assert isinstance(target_practical, Practical)

    # Переконуємося, що в цільового модуля є питання тесту
    target_questions_count = int(
        (
            await db_session.execute(
                select(func.count(QuizQuestion.id)).where(
                    QuizQuestion.module_id == target_module.id
                )
            )
        ).scalar_one()
    )
    assert target_questions_count > 0

    # Додаємо спроби тесту-допуску для цільового та сусіднього модулів
    for st_id, mod_id in (
        (student1.id, target_module.id),
        (student2.id, target_module.id),
        (student1.id, surviving_module.id),
    ):
        db_session.add(
            QuizAttempt(
                student_id=st_id,
                module_id=mod_id,
                score_percent=Decimal("100.00"),
                passed=True,
            )
        )
    await db_session.commit()

    # Завантажуємо реальні .docx файли студентів на цільову та сусідню практичні
    st1_target_bytes = build_sample_docx(
        tmp_path / "mod_del_st1.docx",
        creator="Student One",
    ).read_bytes()
    st1_target_resp = await async_client.post(
        f"/api/v1/practicals/{target_practical.id}/submit",
        headers=make_auth_headers(student1.id, student1.role),
        files={
            "file": (
                "mod_del_st1.docx",
                st1_target_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert st1_target_resp.status_code == 201
    st1_target_file = Path(st1_target_resp.json()["file_path"])

    st2_target_bytes = build_sample_docx(
        tmp_path / "mod_del_st2.docx",
        creator="Student Two",
        created_iso="2026-11-19T12:00:00Z",
    ).read_bytes()
    st2_target_resp = await async_client.post(
        f"/api/v1/practicals/{target_practical.id}/submit",
        headers=make_auth_headers(student2.id, student2.role),
        files={
            "file": (
                "mod_del_st2.docx",
                st2_target_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert st2_target_resp.status_code == 201
    st2_target_file = Path(st2_target_resp.json()["file_path"])

    surviving_bytes = build_sample_docx(
        tmp_path / "mod_keep_st1.docx",
        creator="Student Keep",
    ).read_bytes()
    surviving_resp = await async_client.post(
        f"/api/v1/practicals/{surviving_practical.id}/submit",
        headers=make_auth_headers(student1.id, student1.role),
        files={
            "file": (
                "mod_keep_st1.docx",
                surviving_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert surviving_resp.status_code == 201
    surviving_file = Path(surviving_resp.json()["file_path"])

    # Додаємо здачу з небезпечним шляхом поза UPLOADS_DIR для перевірки захисту від Path Traversal
    outside_secret = tmp_path / "outside_module_secret.docx"
    outside_secret.write_bytes(b"do-not-delete")
    db_session.add(
        Submission(
            practical_id=target_practical.id,
            student_id=student1.id,
            variant_index=0,
            file_path=str(outside_secret),
            auto_score=Decimal("5.00"),
            final_score=Decimal("5.00"),
            grading_report={},
        )
    )
    await db_session.commit()

    assert st1_target_file.is_file()
    assert st2_target_file.is_file()
    assert surviving_file.is_file()
    assert outside_secret.is_file()

    expected_remaining_ids = [
        mod.id for mod in all_modules if mod.id != target_module.id
    ]

    # 1. Викладач курсу видаляє середній модуль -> 204
    delete_resp = await async_client.delete(
        f"/api/v1/modules/{target_module.id}",
        headers=teacher_headers,
    )
    assert delete_resp.status_code == 204

    # Перевірка каскадного видалення у БД
    assert (
        await db_session.execute(
            select(Module).where(Module.id == target_module.id)
        )
    ).scalar_one_or_none() is None
    assert (
        int(
            (
                await db_session.execute(
                    select(func.count(QuizQuestion.id)).where(
                        QuizQuestion.module_id == target_module.id
                    )
                )
            ).scalar_one()
        )
        == 0
    )
    assert (
        int(
            (
                await db_session.execute(
                    select(func.count(QuizAttempt.id)).where(
                        QuizAttempt.module_id == target_module.id
                    )
                )
            ).scalar_one()
        )
        == 0
    )
    assert (
        await db_session.execute(
            select(Practical).where(Practical.id == target_practical.id)
        )
    ).scalar_one_or_none() is None
    assert (
        int(
            (
                await db_session.execute(
                    select(func.count(Submission.id)).where(
                        Submission.practical_id == target_practical.id
                    )
                )
            ).scalar_one()
        )
        == 0
    )

    # Файли видаленого модуля очищено з UPLOADS_DIR, сторонні та чужі файли недоторкані
    assert not st1_target_file.exists()
    assert not st2_target_file.exists()
    assert outside_secret.is_file()
    assert surviving_file.is_file()

    # Решта модулів перенумеровані послідовно 1..N зі збереженням відносного порядку
    remaining_after_teacher = list(
        (
            await db_session.execute(
                select(Module)
                .where(Module.course_id == course.id)
                .order_by(Module.order_index.asc(), Module.id.asc())
            )
        )
        .scalars()
        .all()
    )
    assert [mod.id for mod in remaining_after_teacher] == expected_remaining_ids
    assert [mod.order_index for mod in remaining_after_teacher] == list(
        range(1, len(expected_remaining_ids) + 1)
    )

    after_course_resp = await async_client.get(
        f"/api/v1/courses/{course.id}",
        headers=teacher_headers,
    )
    assert after_course_resp.status_code == 200
    api_modules = after_course_resp.json()["modules"]
    assert [uuid.UUID(item["id"]) for item in api_modules] == expected_remaining_ids
    assert [item["order_index"] for item in api_modules] == list(
        range(1, len(expected_remaining_ids) + 1)
    )

    # 2. Адміністратор також може видалити модуль (перший у курсі) -> 204 та перенумерація 1..(N-1)
    admin_target_id = expected_remaining_ids[0]
    expected_after_admin_ids = expected_remaining_ids[1:]
    admin_del_resp = await async_client.delete(
        f"/api/v1/modules/{admin_target_id}",
        headers=admin_headers,
    )
    assert admin_del_resp.status_code == 204
    assert not surviving_file.exists()

    remaining_after_admin = list(
        (
            await db_session.execute(
                select(Module)
                .where(Module.course_id == course.id)
                .order_by(Module.order_index.asc(), Module.id.asc())
            )
        )
        .scalars()
        .all()
    )
    assert [mod.id for mod in remaining_after_admin] == expected_after_admin_ids
    assert [mod.order_index for mod in remaining_after_admin] == list(
        range(1, len(expected_after_admin_ids) + 1)
    )


@pytest.mark.asyncio
async def test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє видалення лише практичної: модуль, лекція й тест зберігаються, файли зникають."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    admin_headers = make_auth_headers(admin.id, admin.role)

    word_course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.WORD))
    ).scalar_one()
    row_res = await db_session.execute(
        select(Module, Practical)
        .join(Practical, Practical.module_id == Module.id)
        .where(Module.course_id == word_course.id)
        .order_by(Module.order_index.asc())
        .limit(1)
    )
    module, practical = row_res.one()
    assert isinstance(module, Module)
    assert isinstance(practical, Practical)

    original_title = module.title
    original_order_index = module.order_index
    original_lecture = module.lecture_content
    original_questions_count = int(
        (
            await db_session.execute(
                select(func.count(QuizQuestion.id)).where(
                    QuizQuestion.module_id == module.id
                )
            )
        ).scalar_one()
    )
    assert original_questions_count > 0

    db_session.add(
        QuizAttempt(
            student_id=student1.id,
            module_id=module.id,
            score_percent=Decimal("90.00"),
            passed=True,
        )
    )
    await db_session.commit()

    docx_bytes = build_sample_docx(tmp_path / "prac_only_del.docx").read_bytes()
    submit_resp = await async_client.post(
        f"/api/v1/practicals/{practical.id}/submit",
        headers=make_auth_headers(student1.id, student1.role),
        files={
            "file": (
                "prac_only_del.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert submit_resp.status_code == 201
    uploaded_file = Path(submit_resp.json()["file_path"])
    assert uploaded_file.is_file()

    # Небезпечний шлях поза UPLOADS_DIR не повинен бути видалений
    outside_secret = tmp_path / "outside_practical_secret.docx"
    outside_secret.write_bytes(b"keep-me-safe")
    db_session.add(
        Submission(
            practical_id=practical.id,
            student_id=student1.id,
            variant_index=0,
            file_path=str(outside_secret),
            auto_score=Decimal("7.00"),
            final_score=Decimal("7.00"),
            grading_report={},
        )
    )
    await db_session.commit()

    # 1. Викладач курсу видаляє практичну роботу -> 204
    del_resp = await async_client.delete(
        f"/api/v1/practicals/{practical.id}",
        headers=teacher_headers,
    )
    assert del_resp.status_code == 204

    # Практична й здачі видалені, файл в UPLOADS_DIR очищено, зовнішній файл не зачеплено
    assert (
        await db_session.execute(
            select(Practical).where(Practical.id == practical.id)
        )
    ).scalar_one_or_none() is None
    assert (
        int(
            (
                await db_session.execute(
                    select(func.count(Submission.id)).where(
                        Submission.practical_id == practical.id
                    )
                )
            ).scalar_one()
        )
        == 0
    )
    assert not uploaded_file.exists()
    assert outside_secret.is_file()

    # Сам модуль, його лекція, питання й спроби тесту збережені недоторканими
    preserved_module = (
        await db_session.execute(select(Module).where(Module.id == module.id))
    ).scalar_one_or_none()
    assert preserved_module is not None
    assert preserved_module.title == original_title
    assert preserved_module.order_index == original_order_index
    assert preserved_module.lecture_content == original_lecture

    preserved_questions_count = int(
        (
            await db_session.execute(
                select(func.count(QuizQuestion.id)).where(
                    QuizQuestion.module_id == module.id
                )
            )
        ).scalar_one()
    )
    preserved_attempts_count = int(
        (
            await db_session.execute(
                select(func.count(QuizAttempt.id)).where(
                    QuizAttempt.module_id == module.id
                )
            )
        ).scalar_one()
    )
    assert preserved_questions_count == original_questions_count
    assert preserved_attempts_count == 1

    # API GET /modules/{id} повертає теоретичний модуль без практичної
    module_resp = await async_client.get(
        f"/api/v1/modules/{module.id}",
        headers=teacher_headers,
    )
    assert module_resp.status_code == 200
    module_payload = module_resp.json()
    assert module_payload["practical"] is None
    assert module_payload["lecture_content"] == original_lecture
    assert len(module_payload["quiz_questions"]) == original_questions_count

    # 2. Адміністратор також може видалити практичну роботу (HTML) -> 204
    html_course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.HTML))
    ).scalar_one()
    html_mod, html_prac = (
        await db_session.execute(
            select(Module, Practical)
            .join(Practical, Practical.module_id == Module.id)
            .where(Module.course_id == html_course.id)
            .order_by(Module.order_index.asc())
            .limit(1)
        )
    ).one()
    assert isinstance(html_mod, Module)
    assert isinstance(html_prac, Practical)

    admin_del_prac = await async_client.delete(
        f"/api/v1/practicals/{html_prac.id}",
        headers=admin_headers,
    )
    assert admin_del_prac.status_code == 204
    assert (
        await db_session.execute(
            select(Practical).where(Practical.id == html_prac.id)
        )
    ).scalar_one_or_none() is None
    assert (
        await db_session.execute(select(Module).where(Module.id == html_mod.id))
    ).scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_delete_module_and_practical_rbac_and_not_found(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє RBAC (403 для студента та чужого викладача) і 404 для неіснуючих ID."""
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")

    other_teacher = User(
        email="other.teacher.del@kpefk.lcloud.in.ua",
        password_hash=hash_password("Teacher123!"),
        full_name="Інший Викладач Петрович",
        role=UserRole.TEACHER,
    )
    db_session.add(other_teacher)
    await db_session.commit()

    word_course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.WORD))
    ).scalar_one()
    module, practical = (
        await db_session.execute(
            select(Module, Practical)
            .join(Practical, Practical.module_id == Module.id)
            .where(Module.course_id == word_course.id)
            .order_by(Module.order_index.asc())
            .limit(1)
        )
    ).one()
    assert isinstance(module, Module)
    assert isinstance(practical, Practical)

    student_headers = make_auth_headers(student1.id, student1.role)
    other_teacher_headers = make_auth_headers(other_teacher.id, other_teacher.role)
    teacher_headers = make_auth_headers(teacher.id, teacher.role)
    admin_headers = make_auth_headers(admin.id, admin.role)

    # Студент отримує 403 Forbidden
    student_del_mod = await async_client.delete(
        f"/api/v1/modules/{module.id}",
        headers=student_headers,
    )
    assert student_del_mod.status_code == 403

    student_del_prac = await async_client.delete(
        f"/api/v1/practicals/{practical.id}",
        headers=student_headers,
    )
    assert student_del_prac.status_code == 403

    # Чужий викладач отримує 403 Forbidden
    other_del_mod = await async_client.delete(
        f"/api/v1/modules/{module.id}",
        headers=other_teacher_headers,
    )
    assert other_del_mod.status_code == 403
    assert other_del_mod.json()["code"] == "FORBIDDEN_COURSE_MODIFICATION"

    other_del_prac = await async_client.delete(
        f"/api/v1/practicals/{practical.id}",
        headers=other_teacher_headers,
    )
    assert other_del_prac.status_code == 403
    assert other_del_prac.json()["code"] == "FORBIDDEN_COURSE_MODIFICATION"

    # Модуль і практична залишилися в БД
    assert (
        await db_session.execute(select(Module).where(Module.id == module.id))
    ).scalar_one_or_none() is not None
    assert (
        await db_session.execute(
            select(Practical).where(Practical.id == practical.id)
        )
    ).scalar_one_or_none() is not None

    # Неіснуючі ID повертають 404 Not Found
    missing_mod_id = uuid.uuid4()
    missing_prac_id = uuid.uuid4()

    for headers in (teacher_headers, admin_headers):
        mod_404 = await async_client.delete(
            f"/api/v1/modules/{missing_mod_id}",
            headers=headers,
        )
        assert mod_404.status_code == 404
        assert mod_404.json()["code"] == "MODULE_NOT_FOUND"

        prac_404 = await async_client.delete(
            f"/api/v1/practicals/{missing_prac_id}",
            headers=headers,
        )
        assert prac_404.status_code == 404
        assert prac_404.json()["code"] == "PRACTICAL_NOT_FOUND"
