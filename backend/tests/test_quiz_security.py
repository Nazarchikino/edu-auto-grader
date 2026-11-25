import json
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.config import Settings, settings
from app.models.course import Course, CourseSlug, Module
from app.models.progress import QuizAttempt
from app.models.user import User
from app.seed import run_seed
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


async def _get_module_with_questions(
    db_session: SqliteAsyncSessionAdapter,
    slug: CourseSlug,
    order_index: int = 1,
) -> Module:
    """Завантажує модуль курсу за slug і order_index разом із тестовими питаннями."""
    stmt = (
        select(Module)
        .join(Course, Course.id == Module.course_id)
        .options(selectinload(Module.quiz_questions))
        .where(Course.slug == slug, Module.order_index == order_index)
    )
    result = await db_session.execute(stmt)
    module = result.scalar_one()
    assert isinstance(module, Module)
    return module


def _build_answers_for_score(
    questions: list[dict[str, object]],
    *,
    correct_target: int,
) -> list[dict[str, object]]:
    """Формує повний список відповідей із заданою кількістю правильних пунктів."""
    answers: list[dict[str, object]] = []
    for idx, raw_question in enumerate(questions):
        q_id = raw_question["id"]
        correct_idx = raw_question["correct_option_index"]
        options = raw_question["options"]
        assert isinstance(q_id, str)
        assert isinstance(correct_idx, int)
        assert isinstance(options, list)
        selected_idx = (
            correct_idx if idx < correct_target else (correct_idx + 1) % len(options)
        )
        answers.append(
            {
                "question_id": q_id,
                "selected_option_index": selected_idx,
            }
        )
    return answers


async def test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє відхилення (422) неповної відправки (1 з N), дублікатів і чужих питань."""
    student = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    student_headers = make_auth_headers(student.id, student.role)
    teacher_headers = make_auth_headers(teacher.id, teacher.role)

    html_m1 = await _get_module_with_questions(db_session, CourseSlug.HTML, order_index=1)
    html_m2 = await _get_module_with_questions(db_session, CourseSlug.HTML, order_index=2)

    q_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}/quiz/questions",
        headers=teacher_headers,
    )
    assert q_resp.status_code == 200
    questions: list[dict[str, object]] = q_resp.json()
    assert len(questions) == 6

    # 1. Лише 1 питання з 6 -> 422 INCOMPLETE_QUIZ_SUBMISSION
    single_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={
            "answers": [
                {
                    "question_id": questions[0]["id"],
                    "selected_option_index": questions[0]["correct_option_index"],
                }
            ]
        },
    )
    assert single_resp.status_code == 422
    single_body = single_resp.json()
    assert single_body["code"] == "INCOMPLETE_QUIZ_SUBMISSION"
    assert "1 із 6" in single_body["detail"]

    # 2. N - 1 питань -> 422 INCOMPLETE_QUIZ_SUBMISSION
    partial_answers = _build_answers_for_score(questions, correct_target=5)[:-1]
    partial_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": partial_answers},
    )
    assert partial_resp.status_code == 422
    assert partial_resp.json()["code"] == "INCOMPLETE_QUIZ_SUBMISSION"

    # 3. Дублікат question_id (навіть при довжині == 6) -> 422 DUPLICATE_QUIZ_ANSWER
    dup_answers = _build_answers_for_score(questions, correct_target=6)
    dup_answers[-1] = dict(dup_answers[0])
    dup_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": dup_answers},
    )
    assert dup_resp.status_code == 422
    assert dup_resp.json()["code"] == "DUPLICATE_QUIZ_ANSWER"

    # 4. Чуже question_id з іншого модуля -> 422 INVALID_QUIZ_QUESTION
    foreign_question = html_m2.quiz_questions[0]
    foreign_answers = _build_answers_for_score(questions, correct_target=6)
    foreign_answers[-1] = {
        "question_id": str(foreign_question.id),
        "selected_option_index": 0,
    }
    foreign_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": foreign_answers},
    )
    assert foreign_resp.status_code == 422
    assert foreign_resp.json()["code"] == "INVALID_QUIZ_QUESTION"

    # 5. Індекс відповіді за межами списку варіантів -> 422 INVALID_QUIZ_OPTION_INDEX
    invalid_opt_answers = _build_answers_for_score(questions, correct_target=6)
    invalid_opt_answers[0]["selected_option_index"] = 99
    invalid_opt_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": invalid_opt_answers},
    )
    assert invalid_opt_resp.status_code == 422
    assert invalid_opt_resp.json()["code"] == "INVALID_QUIZ_OPTION_INDEX"

    # Жодної спроби не має бути збережено в БД після відхилених запитів
    attempts_count_res = await db_session.execute(
        select(func.count(QuizAttempt.id)).where(
            QuizAttempt.student_id == student.id,
            QuizAttempt.module_id == html_m1.id,
        )
    )
    assert int(attempts_count_res.scalar_one()) == 0


async def test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє cooldown 5 хв: 200 -> 429 + Retry-After -> зсув attempted_at -> 200."""
    student = await _get_user_by_email(db_session, "student2@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    student_headers = make_auth_headers(student.id, student.role)
    teacher_headers = make_auth_headers(teacher.id, teacher.role)

    html_m1 = await _get_module_with_questions(db_session, CourseSlug.HTML, order_index=1)
    q_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}/quiz/questions",
        headers=teacher_headers,
    )
    questions: list[dict[str, object]] = q_resp.json()

    # До першої спроби cooldown == 0
    initial_mod_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}",
        headers=student_headers,
    )
    assert initial_mod_resp.status_code == 200
    assert initial_mod_resp.json()["quiz_cooldown_remaining_seconds"] == 0

    # 1. Перша невдала спроба -> 200 (passed=False, retry_after_seconds > 0)
    failed_answers = _build_answers_for_score(questions, correct_target=1)
    first_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": failed_answers},
    )
    assert first_resp.status_code == 200
    first_data = first_resp.json()
    assert first_data["passed"] is False
    assert first_data["retry_after_seconds"] == settings.QUIZ_RETRY_COOLDOWN_SECONDS
    assert first_data["retry_after_seconds"] > 0

    # ModuleDetailRead одразу показує активний залишок cooldown для таймера на фронтенді
    cooldown_mod_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}",
        headers=student_headers,
    )
    assert cooldown_mod_resp.status_code == 200
    mod_cooldown_remaining = cooldown_mod_resp.json()["quiz_cooldown_remaining_seconds"]
    assert 1 <= mod_cooldown_remaining <= settings.QUIZ_RETRY_COOLDOWN_SECONDS

    # 2. Негайна друга спроба -> 429 Too Many Requests із заголовком Retry-After
    passing_answers = _build_answers_for_score(questions, correct_target=6)
    blocked_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": passing_answers},
    )
    assert blocked_resp.status_code == 429
    assert "Retry-After" in blocked_resp.headers
    retry_after_header = int(blocked_resp.headers["Retry-After"])
    assert 1 <= retry_after_header <= settings.QUIZ_RETRY_COOLDOWN_SECONDS
    blocked_body = blocked_resp.json()
    assert blocked_body["code"] == "QUIZ_RETRY_COOLDOWN"
    assert "Повторна спроба буде доступна через" in blocked_body["detail"]
    assert "Перечитайте конспект лекції." in blocked_body["detail"]

    # 3. Зсуваємо attempted_at у минуле більше ніж на cooldown -> наступна спроба проходить
    attempt_res = await db_session.execute(
        select(QuizAttempt).where(QuizAttempt.id == uuid.UUID(first_data["id"]))
    )
    attempt = attempt_res.scalar_one()
    assert isinstance(attempt, QuizAttempt)
    attempt.attempted_at = datetime.now(UTC) - timedelta(
        seconds=settings.QUIZ_RETRY_COOLDOWN_SECONDS + 10
    )
    await db_session.commit()

    unlocked_mod_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}",
        headers=student_headers,
    )
    assert unlocked_mod_resp.status_code == 200
    assert unlocked_mod_resp.json()["quiz_cooldown_remaining_seconds"] == 0

    pass_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": passing_answers},
    )
    assert pass_resp.status_code == 200
    pass_data = pass_resp.json()
    assert pass_data["passed"] is True
    assert pass_data["practical_unlocked"] is True
    assert pass_data["retry_after_seconds"] == 0

    # 4. Якщо студент уже склав тест раніше, повторні спроби самоперевірки не блокуються cooldown
    retake_fail_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": failed_answers},
    )
    assert retake_fail_resp.status_code == 200
    retake_fail_data = retake_fail_resp.json()
    assert retake_fail_data["passed"] is False
    assert retake_fail_data["practical_unlocked"] is True
    assert retake_fail_data["retry_after_seconds"] == 0

    after_pass_mod_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}",
        headers=student_headers,
    )
    assert after_pass_mod_resp.status_code == 200
    assert after_pass_mod_resp.json()["quiz_cooldown_remaining_seconds"] == 0


async def test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє, що QUIZ_RETRY_COOLDOWN_SECONDS=0 вимикає затримку, а <0 відхиляється."""
    with pytest.raises(ValidationError):
        Settings(QUIZ_RETRY_COOLDOWN_SECONDS=-1)

    monkeypatch.setattr(settings, "QUIZ_RETRY_COOLDOWN_SECONDS", 0)

    student = await _get_user_by_email(db_session, "student3@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    student_headers = make_auth_headers(student.id, student.role)
    teacher_headers = make_auth_headers(teacher.id, teacher.role)

    html_m1 = await _get_module_with_questions(db_session, CourseSlug.HTML, order_index=1)
    q_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}/quiz/questions",
        headers=teacher_headers,
    )
    questions: list[dict[str, object]] = q_resp.json()

    failed_answers = _build_answers_for_score(questions, correct_target=1)
    first_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": failed_answers},
    )
    assert first_resp.status_code == 200
    assert first_resp.json()["passed"] is False
    assert first_resp.json()["retry_after_seconds"] == 0

    second_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=student_headers,
        json={"answers": failed_answers},
    )
    assert second_resp.status_code == 200
    assert second_resp.json()["passed"] is False
    assert second_resp.json()["retry_after_seconds"] == 0


async def test_quiz_pass_threshold_setting_controls_passed_flag(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє, що зміна settings.QUIZ_PASS_THRESHOLD_PERCENT впливає на passed."""
    monkeypatch.setattr(settings, "QUIZ_RETRY_COOLDOWN_SECONDS", 0)

    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    student2 = await _get_user_by_email(db_session, "student2@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")
    teacher_headers = make_auth_headers(teacher.id, teacher.role)

    html_m1 = await _get_module_with_questions(db_session, CourseSlug.HTML, order_index=1)
    q_resp = await async_client.get(
        f"/api/v1/modules/{html_m1.id}/quiz/questions",
        headers=teacher_headers,
    )
    questions: list[dict[str, object]] = q_resp.json()
    assert len(questions) == 6

    # 4/6 = 66.67%: за замовчуванням (< 70%) було б False, але при порозі 60% -> True
    monkeypatch.setattr(settings, "QUIZ_PASS_THRESHOLD_PERCENT", 60.0)
    four_of_six = _build_answers_for_score(questions, correct_target=4)
    low_threshold_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=make_auth_headers(student1.id, student1.role),
        json={"answers": four_of_six},
    )
    assert low_threshold_resp.status_code == 200
    low_data = low_threshold_resp.json()
    assert low_data["score_percent"] == pytest.approx(66.67, abs=0.01)
    assert low_data["passed"] is True
    assert low_data["practical_unlocked"] is True

    # 5/6 = 83.33%: при підвищеному порозі 90% -> False
    monkeypatch.setattr(settings, "QUIZ_PASS_THRESHOLD_PERCENT", 90.0)
    five_of_six = _build_answers_for_score(questions, correct_target=5)
    high_threshold_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=make_auth_headers(student2.id, student2.role),
        json={"answers": five_of_six},
    )
    assert high_threshold_resp.status_code == 200
    high_data = high_threshold_resp.json()
    assert high_data["score_percent"] == pytest.approx(83.33, abs=0.01)
    assert high_data["passed"] is False
    assert high_data["practical_unlocked"] is False

    # Знижуємо поріг до 80% -> ті самі 5/6 (83.33%) тепер проходять
    monkeypatch.setattr(settings, "QUIZ_PASS_THRESHOLD_PERCENT", 80.0)
    passed_after_adjust_resp = await async_client.post(
        f"/api/v1/modules/{html_m1.id}/quiz/submit",
        headers=make_auth_headers(student2.id, student2.role),
        json={"answers": five_of_six},
    )
    assert passed_after_adjust_resp.status_code == 200
    assert passed_after_adjust_resp.json()["passed"] is True
    assert passed_after_adjust_resp.json()["practical_unlocked"] is True


async def test_excel_q42_imported_in_module_8_with_media_and_dry_run(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє перенесення Q42 у Модуль 8 excel.json, seed --dry-run та наявність медіафайлів."""
    dry_run_summary = await run_seed(dry_run=True)
    assert dry_run_summary.courses_count == 4
    assert dry_run_summary.modules_count == 40
    assert dry_run_summary.questions_count == 241

    # Перевіряємо, що Q42 видалено з excel_quiz_incompatible.json (залишилось 5 checkbox-питань)
    incompatible_path = settings.COURSE_CONTENT_DIR / "excel_quiz_incompatible.json"
    incompatible_data = json.loads(incompatible_path.read_text(encoding="utf-8"))
    assert incompatible_data["total_incompatible"] == 5
    assert len(incompatible_data["questions"]) == 5
    assert all(q["source_number"] != 42 for q in incompatible_data["questions"])
    assert all(q["original_type"] == "checkbox" for q in incompatible_data["questions"])

    # Перевіряємо наявність Q42 у Модулі 8 Excel у засіяній БД
    excel_m8 = await _get_module_with_questions(db_session, CourseSlug.EXCEL, order_index=8)
    assert len(excel_m8.quiz_questions) == 7

    q42_matches = [
        question
        for question in excel_m8.quiz_questions
        if "секторну діаграму" in question.question_text.lower()
    ]
    assert len(q42_matches) == 1
    q42 = q42_matches[0]
    assert q42.correct_option_index == 0
    assert len(q42.options) == 4

    expected_media_urls = [
        "/media/courses/excel/test/42answera.png",
        "/media/courses/excel/test/42answerb.png",
        "/media/courses/excel/test/42answerv.png",
        "/media/courses/excel/test/42answerg.png",
    ]
    for option, media_url in zip(q42.options, expected_media_urls, strict=True):
        assert media_url in option
        rel_path = media_url.removeprefix("/media/courses/")
        disk_file = settings.COURSE_MEDIA_DIR / rel_path
        assert disk_file.is_file(), f"Відсутній файл зображення Q42: {disk_file}"

        http_resp = await async_client.get(media_url)
        assert http_resp.status_code == 200
        assert http_resp.headers["content-type"].startswith("image/")
        assert len(http_resp.content) > 0
