import json
import re
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
from app.models.user import AcademicGroup, User, UserRole
from app.schemas.grading import GradingRule
from app.seed import build_seed_bundle, seed_database, summarize_bundle
from tests.conftest import SqliteAsyncSessionAdapter

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
