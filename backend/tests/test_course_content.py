import json
import logging
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
from app.graders.accdb_grader import AccdbGrader, build_accdb_bytes
from app.graders.factory import GraderFactory
from app.graders.html_grader import HtmlGrader
from app.graders.xlsx_grader import XlsxGrader, _canonicalize_formula
from app.models.course import (
    ALLOWED_COURSE_SLUGS,
    Course,
    CourseSlug,
    Module,
    Practical,
    PracticalFormat,
    QuizQuestion,
)
from app.models.progress import QuizAttempt, Submission
from app.models.user import AcademicGroup, User, UserRole
from app.schemas.grading import GradingRule, GradingRuleType
from app.seed import build_seed_bundle, seed_database, summarize_bundle
from tests.conftest import (
    SqliteAsyncSessionAdapter,
    build_sample_docx,
    make_auth_headers,
)

_MEDIA_URL_PATTERN = re.compile(r"/media/courses/[^\s\"'\)>]+")
_UNRESOLVED_PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]*\}")


def test_full_course_json_bundle_validation() -> None:
    """Перевіряє цілісність повного JSON-пакета 4 курсів, правил GradingRule та медіафайлів."""
    bundle = build_seed_bundle()
    summary = summarize_bundle(bundle)

    assert summary.courses_count == 4
    assert tuple(course.slug for course in bundle.courses) == ALLOWED_COURSE_SLUGS
    assert summary.modules_count == 40
    assert summary.practicals_count == 37
    assert summary.questions_count == 241
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
                media_references.update(_MEDIA_URL_PATTERN.findall(question.question_text))
                for option in question.options:
                    media_references.update(_MEDIA_URL_PATTERN.findall(option))

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


def test_excel_course_formula_rules_have_valid_supported_expressions() -> None:
    """Гарантує, що всі правила xlsx_formula у excel.json коректні, прохідні й підтримуються."""
    bundle = build_seed_bundle()
    excel_course = next(
        course for course in bundle.courses if course.slug == CourseSlug.EXCEL
    )
    grader = XlsxGrader()
    formula_rules_checked = 0

    for module in excel_course.modules:
        practical = module.practical
        if practical is None:
            continue

        parsed_rules = [
            GradingRule.model_validate(raw_rule)
            for raw_rule in practical.grading_rules
        ]
        assert sum(rule.points for rule in parsed_rules) == pytest.approx(10.0), (
            f"Модуль {module.order_index} ({module.title}) має суму балів != 10.0"
        )

        for rule in parsed_rules:
            if rule.type != GradingRuleType.XLSX_FORMULA:
                continue

            formula_rules_checked += 1
            expected_clean = rule.expected.strip()
            expected_lower = expected_clean.lower()

            # Забороняємо порожні вирази та legacy-записи голого '$' чи '=' у контенті курсу
            assert expected_clean != "", f"Порожній expected у правилі {rule.id}"
            assert expected_clean not in {"$", "="}, (
                f"Непідтримуваний/застарілий вираз '{expected_clean}' у правилі {rule.id}"
            )

            if expected_lower in {"any", "true", "exists", "not_null"}:
                assert grader._matches_expected_formula("=SUM(A1:A5)", expected_clean) is True
                assert grader._matches_expected_formula("=", expected_clean) is False
                continue

            prefix_matched = False
            for prefix in ("contains:", "func:", "function:"):
                if expected_lower.startswith(prefix):
                    prefix_matched = True
                    token = expected_clean[len(prefix) :].strip()
                    assert token != "", f"Порожній токен після '{prefix}' у правилі {rule.id}"
                    canonical_token = _canonicalize_formula(
                        token, strip_dollar="$" not in token
                    )
                    assert canonical_token != "", (
                        f"Токен '{token}' у правилі {rule.id} канонізується у порожній рядок"
                    )
                    if token == "$":
                        assert grader._matches_expected_formula("=B2/$B$10", expected_clean) is True
                        assert grader._matches_expected_formula("=B2/B10", expected_clean) is False
                    else:
                        sample_formula = f"={token}"
                        assert grader._matches_expected_formula(
                            sample_formula, expected_clean
                        ) is True
                    break

            if prefix_matched:
                continue

            canonical_expected = _canonicalize_formula(
                expected_clean, strip_dollar="$" not in expected_clean
            )
            assert canonical_expected != "", (
                f"Вираз '{expected_clean}' у правилі {rule.id} канонізується у порожній рядок"
            )
            sample_formula = (
                f"={canonical_expected}(A1:A5)"
                if re.fullmatch(r"[A-Z_][A-Z_.]*", canonical_expected) is not None
                else f"={expected_clean.lstrip('=')}"
            )
            assert grader._matches_expected_formula(sample_formula, expected_clean) is True

    assert formula_rules_checked >= 25


def test_all_course_variants_resolve_rule_placeholders_without_leftovers() -> None:
    """Інваріант: усі 37 практичних і кожен варіант розкривають {placeholder} без залишків."""
    bundle = build_seed_bundle()
    practicals_checked = 0
    variants_checked = 0
    placeholders_resolved = 0

    for course in bundle.courses:
        for module in course.modules:
            practical = module.practical
            if practical is None:
                continue

            practicals_checked += 1
            grader = GraderFactory.get_grader(practical.format_type)
            parsed_rules = [
                GradingRule.model_validate(raw_rule)
                for raw_rule in practical.grading_rules
            ]
            assert sum(rule.points for rule in parsed_rules) == pytest.approx(10.0), (
                f"{course.slug.value} M{module.order_index:02d}: сума балів != 10.0"
            )
            assert len(practical.variants) >= 1

            for rule in parsed_rules:
                grader.validate_rule_definition(rule)

            for variant in practical.variants:
                variants_checked += 1
                v_num = variant.get("variant_number", "?")
                raw_params = variant.get("parameters")
                assert isinstance(raw_params, dict)

                for rule in parsed_rules:
                    had_placeholder = bool(
                        _UNRESOLVED_PLACEHOLDER_PATTERN.search(rule.target)
                        or _UNRESOLVED_PLACEHOLDER_PATTERN.search(rule.expected)
                    )
                    resolved_target = grader.resolve_expected(rule.target, variant)
                    resolved_expected = grader.resolve_expected(rule.expected, variant)

                    if had_placeholder:
                        placeholders_resolved += 1

                    assert not _UNRESOLVED_PLACEHOLDER_PATTERN.search(resolved_target), (
                        f"Нерозкритий placeholder у target '{resolved_target}' "
                        f"({course.slug.value} M{module.order_index:02d} V{v_num} {rule.id})"
                    )
                    assert not _UNRESOLVED_PLACEHOLDER_PATTERN.search(resolved_expected), (
                        f"Нерозкритий placeholder у expected '{resolved_expected}' "
                        f"({course.slug.value} M{module.order_index:02d} V{v_num} {rule.id})"
                    )
                    assert resolved_target.strip() != ""
                    assert resolved_expected.strip() != ""

                    # Повна перевірка синтаксису кожного розкритого правила відповідним парсером
                    resolved_rule = rule.model_copy(
                        update={"target": resolved_target, "expected": resolved_expected}
                    )
                    grader.validate_rule_definition(resolved_rule)

                # Перевірка цілісності схеми Access M9 (tables збережено, а ключі відповідають їй)
                if course.slug == CourseSlug.ACCESS and module.order_index == 9:
                    raw_tables = raw_params.get("tables")
                    assert isinstance(raw_tables, list) and len(raw_tables) >= 3
                    tables_by_name = {
                        str(tbl["name"]): tbl
                        for tbl in raw_tables
                        if isinstance(tbl, dict) and "name" in tbl
                    }
                    for key in ("table_1", "table_2", "table_3"):
                        table_name = raw_params.get(key)
                        assert isinstance(table_name, str) and table_name in tables_by_name
                    pk_target = raw_params.get("pk_target")
                    assert isinstance(pk_target, str) and "." in pk_target
                    pk_tbl, pk_col = pk_target.split(".", maxsplit=1)
                    assert pk_tbl in tables_by_name
                    assert pk_col in tables_by_name[pk_tbl]["fields"]
                    assert pk_col in tables_by_name[pk_tbl]["primary_keys"]

    assert practicals_checked == 37
    assert variants_checked == 254
    assert placeholders_resolved >= 340


def test_minimal_html_starter_template_scores_zero_across_all_html_course_modules() -> None:
    """Перевіряє, що мінімальний шаблон HtmlSandbox набирає 0.0 у всіх 6 модулях html.json."""
    minimal_starter_html = """<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Практична робота</title>
</head>
<body>
  <!-- Виконайте завдання тут -->
</body>
</html>"""

    bundle = build_seed_bundle()
    html_course = next(
        course for course in bundle.courses if course.slug == CourseSlug.HTML
    )
    html_practicals = [
        (module, module.practical)
        for module in html_course.modules
        if module.practical is not None
    ]
    assert len(html_practicals) == 6

    grader = HtmlGrader()
    for module, practical in html_practicals:
        parsed_rules = [
            GradingRule.model_validate(raw_rule)
            for raw_rule in practical.grading_rules
        ]
        assert len(parsed_rules) >= 1
        for variant in practical.variants:
            report = grader.evaluate(
                raw_code=minimal_starter_html,
                rules=parsed_rules,
                variant_data=variant,
            )
            assert report.total_points == 0.0, (
                f"HTML Модуль {module.order_index} (Варіант {variant.get('variant_number')}) "
                f"набрав {report.total_points} балів на порожньому шаблоні замість 0.0"
            )
            assert report.passed_count == 0
            assert report.failed_count == len(parsed_rules)


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
    assert summary.questions_count == 241

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
    assert int(questions_count_res.scalar_one()) == 241

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


def _copy_course_content_dir(tmp_path: Path) -> Path:
    """Копіює JSON-файли 4 курсів у тимчасову директорію для безпечного тестування sync."""
    target_dir = tmp_path / "courses_content"
    target_dir.mkdir(parents=True, exist_ok=True)
    for slug in ALLOWED_COURSE_SLUGS:
        src = settings.COURSE_CONTENT_DIR / f"{slug.value}.json"
        (target_dir / src.name).write_text(
            src.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    return target_dir


@pytest.mark.asyncio
async def test_seed_sync_courses_upserts_in_place_and_preserves_student_progress(
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє неруйнівний in-place upsert у --sync-courses зі збереженням оцінок і здач."""
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")

    word_course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.WORD))
    ).scalar_one()
    assert isinstance(word_course, Course)
    original_course_id = word_course.id
    original_teacher_id = word_course.teacher_id

    first_mod, first_prac = (
        await db_session.execute(
            select(Module, Practical)
            .join(Practical, Practical.module_id == Module.id)
            .where(Module.course_id == word_course.id)
            .order_by(Module.order_index.asc())
            .limit(1)
        )
    ).one()
    assert isinstance(first_mod, Module)
    assert isinstance(first_prac, Practical)
    original_module_id = first_mod.id
    original_practical_id = first_prac.id

    original_question_ids = [
        row[0]
        for row in (
            await db_session.execute(
                select(QuizQuestion.id).where(QuizQuestion.module_id == first_mod.id)
            )
        ).all()
    ]
    assert len(original_question_ids) >= 1

    # Створюємо реальну спробу тесту та здачу практичної з ручною оцінкою й коментарем
    attempt = QuizAttempt(
        student_id=student1.id,
        module_id=first_mod.id,
        score_percent=Decimal("91.50"),
        passed=True,
    )
    db_session.add(attempt)

    uploaded_file = settings.UPLOADS_DIR / "student1_preserved_work.docx"
    build_sample_docx(uploaded_file, creator="Student One")
    submission = Submission(
        practical_id=first_prac.id,
        student_id=student1.id,
        variant_index=0,
        file_path=str(uploaded_file),
        auto_score=Decimal("7.50"),
        final_score=Decimal("9.25"),
        grading_report={"score": 7.5, "max_score": 10.0, "criteria": []},
        teacher_comment="Враховано додаткове форматування та охайність таблиці.",
    )
    db_session.add(submission)
    await db_session.commit()

    attempt_id = attempt.id
    submission_id = submission.id

    # Готуємо модифікований JSON курсу Word: новий заголовок, лекція та grading_rules
    custom_content_dir = _copy_course_content_dir(tmp_path)
    word_json_path = custom_content_dir / "word.json"
    word_data: dict[str, Any] = json.loads(word_json_path.read_text(encoding="utf-8"))
    word_data["title"] = "Microsoft Word — Оновлена редакція 2026"
    word_data["description"] = "Оновлений опис навчальної дисципліни Word."

    target_json_module = next(
        mod for mod in word_data["modules"] if mod["order_index"] == first_mod.order_index
    )
    updated_module_title = "Оновлена тема 1: Форматування сторінки та тексту"
    updated_lecture = "# Оновлена лекція\n\nРозширений методичний матеріал для першого модуля."
    updated_practical_title = "Практична робота №1 (оновлена)"
    updated_rules: list[dict[str, object]] = [
        {
            "id": "sync_updated_margins",
            "type": "docx_page_margins",
            "target": "section[0]",
            "expected": "left=30,right=15,top=20,bottom=20",
            "points": 5.0,
            "description": "Оновлена перевірка полів сторінки",
        },
        {
            "id": "sync_updated_font",
            "type": "docx_font",
            "target": "all_paragraphs",
            "expected": "Times New Roman, 14pt",
            "points": 5.0,
            "description": "Оновлена перевірка шрифту",
        },
    ]
    target_json_module["title"] = updated_module_title
    target_json_module["lecture_content"] = updated_lecture
    target_json_module["practical"]["title"] = updated_practical_title
    target_json_module["practical"]["grading_rules"] = updated_rules
    word_json_path.write_text(
        json.dumps(word_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 1. Запускаємо неруйнівну синхронізацію з незмінними питаннями тесту
    # justified Any: SqliteAsyncSessionAdapter structural duck-typing for AsyncSession
    typed_db: Any = db_session
    await seed_database(typed_db, sync_courses=True, content_dir=custom_content_dir)

    synced_course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.WORD))
    ).scalar_one()
    assert synced_course.id == original_course_id
    assert synced_course.teacher_id == original_teacher_id
    assert synced_course.title == "Microsoft Word — Оновлена редакція 2026"
    assert synced_course.description == "Оновлений опис навчальної дисципліни Word."

    synced_mod = (
        await db_session.execute(
            select(Module).where(
                Module.course_id == original_course_id,
                Module.order_index == first_mod.order_index,
            )
        )
    ).scalar_one()
    assert synced_mod.id == original_module_id
    assert synced_mod.title == updated_module_title
    assert synced_mod.lecture_content == updated_lecture

    synced_prac = (
        await db_session.execute(
            select(Practical).where(Practical.module_id == original_module_id)
        )
    ).scalar_one()
    assert synced_prac.id == original_practical_id
    assert synced_prac.title == updated_practical_title
    assert [rule["id"] for rule in synced_prac.grading_rules] == [
        "sync_updated_margins",
        "sync_updated_font",
    ]

    # Ідентичні питання тесту не перестворювалися (ID збереглися)
    question_ids_after_unchanged_sync = [
        row[0]
        for row in (
            await db_session.execute(
                select(QuizQuestion.id).where(QuizQuestion.module_id == original_module_id)
            )
        ).all()
    ]
    assert set(question_ids_after_unchanged_sync) == set(original_question_ids)

    # Усі спроби тесту, здачі, ручні оцінки, коментарі та файл на диску збереглися
    preserved_attempt = (
        await db_session.execute(select(QuizAttempt).where(QuizAttempt.id == attempt_id))
    ).scalar_one_or_none()
    assert preserved_attempt is not None
    assert preserved_attempt.module_id == original_module_id
    assert preserved_attempt.score_percent == Decimal("91.50")
    assert preserved_attempt.passed is True

    preserved_submission = (
        await db_session.execute(select(Submission).where(Submission.id == submission_id))
    ).scalar_one_or_none()
    assert preserved_submission is not None
    assert preserved_submission.practical_id == original_practical_id
    assert preserved_submission.auto_score == Decimal("7.50")
    assert preserved_submission.final_score == Decimal("9.25")
    assert (
        preserved_submission.teacher_comment
        == "Враховано додаткове форматування та охайність таблиці."
    )
    assert preserved_submission.file_path == str(uploaded_file)
    assert uploaded_file.is_file()

    # 2. Змінюємо одне питання тесту й додаємо нове -> питання оновлюються, QuizAttempt зберігається
    target_json_module["quiz_questions"][0]["question_text"] = "Оновлений текст першого питання?"
    target_json_module["quiz_questions"].append(
        {
            "question_text": "Нове контрольне питання після sync?",
            "options": ["Варіант А", "Варіант Б"],
            "correct_option_index": 1,
        }
    )
    word_json_path.write_text(
        json.dumps(word_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    await seed_database(typed_db, sync_courses=True, content_dir=custom_content_dir)

    updated_questions = list(
        (
            await db_session.execute(
                select(QuizQuestion).where(QuizQuestion.module_id == original_module_id)
            )
        )
        .scalars()
        .all()
    )
    question_texts = {question.question_text for question in updated_questions}
    assert "Оновлений текст першого питання?" in question_texts
    assert "Нове контрольне питання після sync?" in question_texts
    assert len(updated_questions) == len(original_question_ids) + 1

    attempt_after_quiz_update = (
        await db_session.execute(select(QuizAttempt).where(QuizAttempt.id == attempt_id))
    ).scalar_one_or_none()
    assert attempt_after_quiz_update is not None
    assert attempt_after_quiz_update.module_id == original_module_id


@pytest.mark.asyncio
async def test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress(
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Перевіряє захист зайвих модулів/практичних зі здачами та прапорець примусового видалення."""
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    word_course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.WORD))
    ).scalar_one()
    assert isinstance(word_course, Course)

    # 1. Зайвий модуль #99 зі спробою тесту, практичною, файлом у UPLOADS_DIR та зовнішнім файлом
    protected_extra_mod = Module(
        course_id=word_course.id,
        order_index=99,
        title="Архівний модуль із роботами студентів",
        lecture_content="Лекція архівного модуля",
    )
    protected_extra_prac = Practical(
        title="Архівна практична",
        instructions="Інструкція архівної практичної",
        format_type=PracticalFormat.DOCX,
        max_score=Decimal("10.00"),
        variants=[],
        grading_rules=[
            {
                "id": "archive_r1",
                "type": "docx_table_exists",
                "target": "document",
                "expected": "true",
                "points": 10.0,
                "description": "Наявність таблиці",
            }
        ],
    )
    protected_extra_mod.practical = protected_extra_prac
    db_session.add(protected_extra_mod)

    # 2. Зайвий модуль #98 БЕЗ жодного прогресу студентів -> має безпечно видалитися
    empty_extra_mod = Module(
        course_id=word_course.id,
        order_index=98,
        title="Порожній зайвий модуль",
        lecture_content="Лекція порожнього модуля",
    )
    db_session.add(empty_extra_mod)
    await db_session.flush()

    extra_mod_file = settings.UPLOADS_DIR / "extra_module_submission.docx"
    build_sample_docx(extra_mod_file, creator="Student One")
    outside_secret_file = tmp_path / "outside_seed_secret.docx"
    outside_secret_file.write_bytes(b"keep-outside-file")

    extra_attempt = QuizAttempt(
        student_id=student1.id,
        module_id=protected_extra_mod.id,
        score_percent=Decimal("85.00"),
        passed=True,
    )
    extra_submission = Submission(
        practical_id=protected_extra_prac.id,
        student_id=student1.id,
        variant_index=0,
        file_path=str(extra_mod_file),
        auto_score=Decimal("8.00"),
        final_score=Decimal("8.50"),
        grading_report={},
        teacher_comment="Здача в архівному модулі",
    )
    extra_outside_submission = Submission(
        practical_id=protected_extra_prac.id,
        student_id=student1.id,
        variant_index=0,
        file_path=str(outside_secret_file),
        auto_score=Decimal("6.00"),
        final_score=Decimal("6.00"),
        grading_report={},
    )
    db_session.add_all([extra_attempt, extra_submission, extra_outside_submission])

    # 3. Існуючі модулі #2 (зі здачею) і #3 (без здач), де в JSON прибираємо practical=None
    mod2, prac2 = (
        await db_session.execute(
            select(Module, Practical)
            .join(Practical, Practical.module_id == Module.id)
            .where(Module.course_id == word_course.id, Module.order_index == 2)
        )
    ).one()
    mod3, prac3 = (
        await db_session.execute(
            select(Module, Practical)
            .join(Practical, Practical.module_id == Module.id)
            .where(Module.course_id == word_course.id, Module.order_index == 3)
        )
    ).one()
    assert isinstance(mod2, Module)
    assert isinstance(prac2, Practical)
    assert isinstance(mod3, Module)
    assert isinstance(prac3, Practical)

    mod2_file = settings.UPLOADS_DIR / "mod2_protected_practical.docx"
    build_sample_docx(mod2_file, creator="Student One")
    mod2_submission = Submission(
        practical_id=prac2.id,
        student_id=student1.id,
        variant_index=0,
        file_path=str(mod2_file),
        auto_score=Decimal("9.00"),
        final_score=Decimal("9.50"),
        grading_report={},
        teacher_comment="Оцінка збережена попри practical=None у JSON",
    )
    db_session.add(mod2_submission)
    await db_session.commit()

    protected_extra_mod_id = protected_extra_mod.id
    protected_extra_prac_id = protected_extra_prac.id
    empty_extra_mod_id = empty_extra_mod.id
    prac2_id = prac2.id
    prac3_id = prac3.id

    custom_content_dir = _copy_course_content_dir(tmp_path)
    word_json_path = custom_content_dir / "word.json"
    word_data: dict[str, Any] = json.loads(word_json_path.read_text(encoding="utf-8"))
    for mod_json in word_data["modules"]:
        if mod_json["order_index"] in {2, 3}:
            mod_json["practical"] = None
    word_json_path.write_text(
        json.dumps(word_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Без --allow-destructive-module-delete: об'єкти з прогресом захищені, порожні очищуються
    # justified Any: SqliteAsyncSessionAdapter structural duck-typing for AsyncSession
    typed_db: Any = db_session
    with caplog.at_level(logging.WARNING, logger="app.seed"):
        await seed_database(typed_db, sync_courses=True, content_dir=custom_content_dir)

    assert (
        await db_session.execute(
            select(Module).where(Module.id == protected_extra_mod_id)
        )
    ).scalar_one_or_none() is not None
    assert (
        await db_session.execute(
            select(Practical).where(Practical.id == protected_extra_prac_id)
        )
    ).scalar_one_or_none() is not None
    assert (
        await db_session.execute(
            select(Submission).where(Submission.id == extra_submission.id)
        )
    ).scalar_one_or_none() is not None
    assert extra_mod_file.is_file()

    # Порожній зайвий модуль #98 без прогресу видалено автоматично
    assert (
        await db_session.execute(select(Module).where(Module.id == empty_extra_mod_id))
    ).scalar_one_or_none() is None

    # Практична модуля #2 зі здачею збережена, а порожня практична модуля #3 безпечно видалена
    assert (
        await db_session.execute(select(Practical).where(Practical.id == prac2_id))
    ).scalar_one_or_none() is not None
    assert (
        await db_session.execute(
            select(Submission).where(Submission.id == mod2_submission.id)
        )
    ).scalar_one_or_none() is not None
    assert mod2_file.is_file()
    assert (
        await db_session.execute(select(Practical).where(Practical.id == prac3_id))
    ).scalar_one_or_none() is None

    warning_messages = [record.getMessage() for record in caplog.records]
    assert any("order_index=99" in msg for msg in warning_messages)
    assert any("модуль=2" in msg for msg in warning_messages)

    # Із явним allow_destructive_module_delete=True: зайвий модуль і практична видаляються,
    # а файли з UPLOADS_DIR очищуються після commit (зовнішній файл не зачеплено)
    await seed_database(
        typed_db,
        sync_courses=True,
        allow_destructive_module_delete=True,
        content_dir=custom_content_dir,
    )

    assert (
        await db_session.execute(
            select(Module).where(Module.id == protected_extra_mod_id)
        )
    ).scalar_one_or_none() is None
    assert (
        await db_session.execute(
            select(Practical).where(Practical.id == prac2_id)
        )
    ).scalar_one_or_none() is None
    assert (
        await db_session.execute(select(Module).where(Module.id == mod2.id))
    ).scalar_one_or_none() is not None

    assert not extra_mod_file.exists()
    assert not mod2_file.exists()
    assert outside_secret_file.is_file()


def test_all_course_rules_pass_validate_rule_definition_and_access_modules_separated(
    tmp_path: Path,
) -> None:
    """Інваріант T6.13: усі 37 практичних валідні, а Модулі 5/6/7 Access реально розведені."""
    bundle = build_seed_bundle()
    practicals_validated = 0
    rules_validated = 0

    for course in bundle.courses:
        for module in course.modules:
            practical = module.practical
            if practical is None:
                continue
            practicals_validated += 1
            grader = GraderFactory.get_grader(practical.format_type)
            parsed_rules = [
                GradingRule.model_validate(raw_rule)
                for raw_rule in practical.grading_rules
            ]
            assert sum(rule.points for rule in parsed_rules) == pytest.approx(10.0), (
                f"{course.slug.value} M{module.order_index:02d}: сума балів != 10.0"
            )
            for rule in parsed_rules:
                grader.validate_rule_definition(rule)
                rules_validated += 1

    assert practicals_validated == 37
    assert rules_validated >= 190

    access_course = next(
        course for course in bundle.courses if course.slug == CourseSlug.ACCESS
    )
    access_by_order = {
        module.order_index: module.practical
        for module in access_course.modules
        if module.practical is not None
    }
    m04 = access_by_order[4]
    m05 = access_by_order[5]
    m06 = access_by_order[6]
    m07 = access_by_order[7]

    m04_rules = [GradingRule.model_validate(r) for r in m04.grading_rules]
    m05_rules = [GradingRule.model_validate(r) for r in m05.grading_rules]
    m06_rules = [GradingRule.model_validate(r) for r in m06.grading_rules]
    m07_rules = [GradingRule.model_validate(r) for r in m07.grading_rules]

    assert any(r.type == GradingRuleType.ACCDB_RELATIONSHIP_EXISTS for r in m04_rules)
    assert any(r.type == GradingRuleType.ACCDB_QUERY_EXISTS for r in m05_rules)
    assert any(r.type == GradingRuleType.ACCDB_FORM_EXISTS for r in m06_rules)
    assert any(r.type == GradingRuleType.ACCDB_REPORT_EXISTS for r in m07_rules)

    assert m04.needs_rules_review is False
    assert m05.needs_rules_review is False
    assert m06.needs_rules_review is False
    assert m07.needs_rules_review is False

    # Файл із Модуля 4 (лише таблиці та зв'язки, без запитів/форм/звітів) не може дати 10/10 у M5–M7
    m04_only_accdb = tmp_path / "firma_m04_only.accdb"
    m04_only_accdb.write_bytes(
        build_accdb_bytes(
            tables={
                "Співробітники": [
                    ("Код співробітника", "AUTONUMBER"),
                    ("Прізвище", "TEXT(100)"),
                    ("Заробітна плата", "CURRENCY"),
                ],
                "Клієнти": [
                    ("Код клієнта", "AUTONUMBER"),
                    ("Назва компанії", "TEXT(150)"),
                ],
                "Замовлення": [
                    ("Код замовлення", "AUTONUMBER"),
                    ("Код клієнта", "LONG"),
                    ("Код співробітника", "LONG"),
                    ("Дата розміщення", "DATETIME"),
                    ("Відмітка про виконання", "YES/NO"),
                ],
            },
            relationships=[
                (
                    "Замовлення",
                    "Співробітники",
                    "Код співробітника",
                    "Код співробітника",
                    "FK_Ord_Emp",
                ),
                (
                    "Замовлення",
                    "Клієнти",
                    "Код клієнта",
                    "Код клієнта",
                    "FK_Ord_Cli",
                ),
            ],
        )
    )
    accdb_grader = AccdbGrader()
    report_m04 = accdb_grader.evaluate(
        file_path=m04_only_accdb, rules=m04_rules, variant_data={}
    )
    report_m05 = accdb_grader.evaluate(
        file_path=m04_only_accdb, rules=m05_rules, variant_data={}
    )
    report_m06 = accdb_grader.evaluate(
        file_path=m04_only_accdb, rules=m06_rules, variant_data={}
    )
    report_m07 = accdb_grader.evaluate(
        file_path=m04_only_accdb, rules=m07_rules, variant_data={}
    )

    assert report_m04.total_points == 10.0
    assert report_m05.total_points <= 2.0
    assert report_m06.total_points == 0.0
    assert report_m07.total_points == 0.0


@pytest.mark.asyncio
async def test_seed_and_sync_courses_persist_needs_rules_review(
    db_session: SqliteAsyncSessionAdapter,
    tmp_path: Path,
) -> None:
    """Перевіряє перенесення meta.needs_manual_rules_review у Practical.needs_rules_review."""
    word_course = (
        await db_session.execute(select(Course).where(Course.slug == CourseSlug.WORD))
    ).scalar_one()
    assert isinstance(word_course, Course)

    m01_prac = (
        await db_session.execute(
            select(Practical)
            .join(Module, Practical.module_id == Module.id)
            .where(Module.course_id == word_course.id, Module.order_index == 1)
        )
    ).scalar_one()
    m02_prac = (
        await db_session.execute(
            select(Practical)
            .join(Module, Practical.module_id == Module.id)
            .where(Module.course_id == word_course.id, Module.order_index == 2)
        )
    ).scalar_one()
    assert isinstance(m01_prac, Practical)
    assert isinstance(m02_prac, Practical)
    assert m01_prac.needs_rules_review is False
    assert m02_prac.needs_rules_review is True

    # Перемикаємо прапорці у тимчасовому JSON та запускаємо --sync-courses
    custom_dir = _copy_course_content_dir(tmp_path)
    word_json_path = custom_dir / "word.json"
    word_data: dict[str, Any] = json.loads(word_json_path.read_text(encoding="utf-8"))
    for mod in word_data["modules"]:
        if mod["order_index"] == 1:
            mod["practical"]["meta"]["needs_manual_rules_review"] = True
        elif mod["order_index"] == 2:
            mod["practical"]["meta"]["needs_manual_rules_review"] = False
    word_json_path.write_text(
        json.dumps(word_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # justified Any: SqliteAsyncSessionAdapter structural duck-typing for AsyncSession
    typed_db: Any = db_session
    await seed_database(typed_db, sync_courses=True, content_dir=custom_dir)

    m01_after = (
        await db_session.execute(select(Practical).where(Practical.id == m01_prac.id))
    ).scalar_one()
    m02_after = (
        await db_session.execute(select(Practical).where(Practical.id == m02_prac.id))
    ).scalar_one()
    assert m01_after.needs_rules_review is True
    assert m02_after.needs_rules_review is False
