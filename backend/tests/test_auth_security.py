import threading
import uuid

import bcrypt
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.config import DEFAULT_JWT_SECRET_KEY, Settings, settings
from app.core.rate_limit import SlidingWindowRateLimiter
from app.core.security import (
    PASSWORD_HASH_PREFIX,
    hash_password,
    hash_password_async,
    verify_password,
    verify_password_async,
)
from app.models.user import AcademicGroup, User
from tests.conftest import SqliteAsyncSessionAdapter, make_auth_headers


async def _get_user_by_email(
    db_session: SqliteAsyncSessionAdapter,
    email: str,
) -> User:
    """Повертає користувача з тестової БД за його email."""
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    assert isinstance(user, User)
    return user


def test_settings_production_rejects_default_or_short_jwt_secret() -> None:
    """Перевіряє блокування старту в production із дефолтним або коротким JWT_SECRET_KEY."""
    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        Settings(APP_ENV="production", JWT_SECRET_KEY=DEFAULT_JWT_SECRET_KEY)

    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        Settings(APP_ENV="production", JWT_SECRET_KEY="short-secret-key")

    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        Settings(APP_ENV="production", JWT_SECRET_KEY=" " * 40)

    valid_prod = Settings(
        APP_ENV="production",
        JWT_SECRET_KEY="prod-super-strong-random-jwt-secret-key-2026!",
    )
    assert valid_prod.APP_ENV == "production"

    dev_settings = Settings(
        APP_ENV="development",
        JWT_SECRET_KEY=DEFAULT_JWT_SECRET_KEY,
    )
    assert dev_settings.APP_ENV == "development"

    test_settings = Settings(APP_ENV="test", JWT_SECRET_KEY="short")
    assert test_settings.APP_ENV == "test"


def test_password_hashing_supports_long_cyrillic_and_legacy_bcrypt_hashes() -> None:
    """Перевіряє sha256$<bcrypt> для паролів >72 байтів UTF-8 та сумісність із legacy-хешами."""
    long_cyrillic_password = "ДужеДовгийКириличнийПарольДляСтудентаКоледжу2026РокуБезПомилок!"
    assert len(long_cyrillic_password) >= 50
    assert len(long_cyrillic_password.encode("utf-8")) > 100

    modern_hash = hash_password(long_cyrillic_password)
    assert modern_hash.startswith(PASSWORD_HASH_PREFIX)
    assert verify_password(long_cyrillic_password, modern_hash) is True
    assert verify_password(f"{long_cyrillic_password}1", modern_hash) is False

    # Зворотна сумісність зі старими bcrypt-хешами у БД (без префікса sha256$)
    legacy_hash = bcrypt.hashpw(b"LegacyPass123!", bcrypt.gensalt(rounds=4)).decode("utf-8")
    assert not legacy_hash.startswith(PASSWORD_HASH_PREFIX)
    assert verify_password("LegacyPass123!", legacy_hash) is True
    assert verify_password("WrongPass123!", legacy_hash) is False
    # Довгий кириличний пароль проти legacy-хешу не повинен піднімати ValueError
    assert verify_password(long_cyrillic_password, legacy_hash) is False


def test_sliding_window_rate_limiter_expires_old_attempts() -> None:
    """Перевіряє ковзне вікно та скидання лічильника у SlidingWindowRateLimiter."""
    current_time = 100.0

    def fake_clock() -> float:
        return current_time

    limiter = SlidingWindowRateLimiter(clock=fake_clock)
    key = "127.0.0.1|student@kpefk.lcloud.in.ua"

    assert limiter.check_limit(key, max_attempts=2, window_seconds=60) is None
    assert limiter.record_failure(key, window_seconds=60) == 1
    assert limiter.check_limit(key, max_attempts=2, window_seconds=60) is None

    current_time = 110.0
    assert limiter.record_failure(key, window_seconds=60) == 2

    retry_after = limiter.check_limit(key, max_attempts=2, window_seconds=60)
    assert retry_after == 50

    # Після виходу першої спроби за межі 60-секундного вікна доступ відновлюється
    current_time = 160.5
    assert limiter.check_limit(key, max_attempts=2, window_seconds=60) is None

    limiter.reset_key(key)
    assert limiter.record_failure(key, window_seconds=60) == 1


@pytest.mark.asyncio
async def test_long_cyrillic_password_create_login_and_change_without_500(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє створення, логін і зміну пароля з кирилицею >100 байтів UTF-8 без 500."""
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    admin_headers = make_auth_headers(
        admin.id,
        admin.role,
        token_version=admin.token_version,
    )

    initial_long_password = (
        "НадзвичайноДовгийКириличнийПарольПершоїСпробиКоледжу2026!"
    )
    updated_long_password = (
        "ОновленийКириличнийПарольДовшийЗаСтоБайтДляАвтоперевірки2026!"
    )
    assert len(initial_long_password) > 50
    assert len(initial_long_password.encode("utf-8")) > 100
    assert len(updated_long_password) > 50
    assert len(updated_long_password.encode("utf-8")) > 100

    create_resp = await async_client.post(
        "/api/v1/admin/users",
        headers=admin_headers,
        json={
            "email": "cyrillic.student@kpefk.lcloud.in.ua",
            "full_name": "Шевченко Тарас Григорович",
            "role": "student",
            "password": initial_long_password,
        },
    )
    assert create_resp.status_code == 201

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "cyrillic.student@kpefk.lcloud.in.ua",
            "password": initial_long_password,
        },
    )
    assert login_resp.status_code == 200
    initial_tokens = login_resp.json()

    change_resp = await async_client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {initial_tokens['access_token']}"},
        json={
            "current_password": initial_long_password,
            "new_password": updated_long_password,
        },
    )
    assert change_resp.status_code == 200
    change_data = change_resp.json()
    assert change_data["user"]["must_change_password"] is False

    relogin_resp = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "cyrillic.student@kpefk.lcloud.in.ua",
            "password": updated_long_password,
        },
    )
    assert relogin_resp.status_code == 200

    # Перевіряємо, що legacy bcrypt-хеш у БД повертає 401 (не 500) на пароль >72 байтів
    student1 = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    student1.password_hash = bcrypt.hashpw(
        b"LegacyShort1!",
        bcrypt.gensalt(rounds=4),
    ).decode("utf-8")
    await db_session.commit()

    legacy_long_attempt = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": student1.email,
            "password": initial_long_password,
        },
    )
    assert legacy_long_attempt.status_code == 401
    assert legacy_long_attempt.json()["code"] == "INVALID_CREDENTIALS"

    legacy_valid_attempt = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": student1.email,
            "password": "LegacyShort1!",
        },
    )
    assert legacy_valid_attempt.status_code == 200


@pytest.mark.asyncio
async def test_token_version_revokes_tokens_on_admin_reset_and_self_change(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє відкликання старих access/refresh токенів через token_version."""
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    student = await _get_user_by_email(db_session, "student1@kpefk.lcloud.in.ua")
    teacher = await _get_user_by_email(db_session, "teacher@kpefk.lcloud.in.ua")

    admin_headers = make_auth_headers(
        admin.id,
        admin.role,
        token_version=admin.token_version,
    )

    # 1. RBAC перевірка reset-password для не-адміністраторів та 404 для неіснуючого ID
    for non_admin in (student, teacher):
        forbidden_resp = await async_client.post(
            f"/api/v1/admin/users/{student.id}/reset-password",
            headers=make_auth_headers(
                non_admin.id,
                non_admin.role,
                token_version=non_admin.token_version,
            ),
        )
        assert forbidden_resp.status_code == 403

    not_found_resp = await async_client.post(
        f"/api/v1/admin/users/{uuid.uuid4()}/reset-password",
        headers=admin_headers,
    )
    assert not_found_resp.status_code == 404

    # 2. Студент логіниться та отримує першу пару токенів
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": student.email, "password": "Student123!"},
    )
    assert login_resp.status_code == 200
    tokens_v0 = login_resp.json()

    me_v0 = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens_v0['access_token']}"},
    )
    assert me_v0.status_code == 200
    assert me_v0.json()["must_change_password"] is False

    # 3. Адмін скидає пароль користувача -> token_version++, must_change_password=True
    reset_resp = await async_client.post(
        f"/api/v1/admin/users/{student.id}/reset-password",
        headers=admin_headers,
    )
    assert reset_resp.status_code == 200
    reset_data = reset_resp.json()
    temp_password = reset_data["temp_password"]
    assert isinstance(temp_password, str) and len(temp_password) >= 8
    assert reset_data["user"]["must_change_password"] is True

    # Старі access та refresh токени (v0) мають повернути 401 TOKEN_REVOKED
    revoked_me = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens_v0['access_token']}"},
    )
    assert revoked_me.status_code == 401
    assert revoked_me.json()["code"] == "TOKEN_REVOKED"

    revoked_refresh = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens_v0["refresh_token"]},
    )
    assert revoked_refresh.status_code == 401
    assert revoked_refresh.json()["code"] == "TOKEN_REVOKED"

    # 4. Студент входить за тимчасовим паролем (v1) та бачить must_change_password=True
    login_v1_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": student.email, "password": temp_password},
    )
    assert login_v1_resp.status_code == 200
    tokens_v1 = login_v1_resp.json()

    me_v1 = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens_v1['access_token']}"},
    )
    assert me_v1.status_code == 200
    assert me_v1.json()["must_change_password"] is True

    # 5. Студент самостійно змінює пароль -> отримує валідні токени v2, а v1 відкликано
    change_resp = await async_client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {tokens_v1['access_token']}"},
        json={
            "current_password": temp_password,
            "new_password": "StudentSecure2026!",
        },
    )
    assert change_resp.status_code == 200
    change_data = change_resp.json()
    assert change_data["token_type"] == "bearer"
    assert change_data["user"]["must_change_password"] is False

    # Старі токени v1 більше не працюють
    revoked_v1_me = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens_v1['access_token']}"},
    )
    assert revoked_v1_me.status_code == 401
    assert revoked_v1_me.json()["code"] == "TOKEN_REVOKED"

    revoked_v1_refresh = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens_v1["refresh_token"]},
    )
    assert revoked_v1_refresh.status_code == 401
    assert revoked_v1_refresh.json()["code"] == "TOKEN_REVOKED"

    # Нові токени v2 працюють для /auth/me та /auth/refresh
    me_v2 = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {change_data['access_token']}"},
    )
    assert me_v2.status_code == 200
    assert me_v2.json()["must_change_password"] is False

    refresh_v2 = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": change_data["refresh_token"]},
    )
    assert refresh_v2.status_code == 200

    # 6. Зміна пароля через PATCH /admin/users/{id} також відкликає токени v2
    patch_resp = await async_client.patch(
        f"/api/v1/admin/users/{student.id}",
        headers=admin_headers,
        json={"password": "AdminPatched2026!"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["must_change_password"] is True

    revoked_v2_me = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {change_data['access_token']}"},
    )
    assert revoked_v2_me.status_code == 401
    assert revoked_v2_me.json()["code"] == "TOKEN_REVOKED"


@pytest.mark.asyncio
async def test_change_password_validation_and_imported_student_flag(
    async_client: AsyncClient,
    db_session: SqliteAsyncSessionAdapter,
) -> None:
    """Перевіряє валідацію /auth/change-password та must_change_password після імпорту."""
    admin = await _get_user_by_email(db_session, "admin@kpefk.lcloud.in.ua")
    admin_headers = make_auth_headers(
        admin.id,
        admin.role,
        token_version=admin.token_version,
    )

    group_res = await db_session.execute(
        select(AcademicGroup).where(AcademicGroup.code == "КН-31")
    )
    group = group_res.scalar_one()
    assert isinstance(group, AcademicGroup)

    # Масово імпортований студент повинен мати must_change_password=True
    txt_bytes = "Ковальчук Олена Петрівна; kovalchuk.o@kpefk.com.ua; TempPass99!\n".encode()
    import_resp = await async_client.post(
        "/api/v1/admin/users/import",
        headers=admin_headers,
        data={"group_id": str(group.id)},
        files={"file": ("students.txt", txt_bytes, "text/plain")},
    )
    assert import_resp.status_code == 200
    assert import_resp.json()["created_count"] == 1

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "kovalchuk.o@kpefk.com.ua", "password": "TempPass99!"},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    me_before = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_before.status_code == 200
    assert me_before.json()["must_change_password"] is True

    # Неавторизований запит -> 401
    unauth_resp = await async_client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "TempPass99!", "new_password": "NewPassword2026!"},
    )
    assert unauth_resp.status_code == 401

    # Невірний поточний пароль -> 400
    wrong_current = await async_client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={"current_password": "WrongPassword!", "new_password": "NewPassword2026!"},
    )
    assert wrong_current.status_code == 400
    assert wrong_current.json()["code"] == "INVALID_CURRENT_PASSWORD"

    # Новий пароль коротший за 8 символів -> 422
    too_short = await async_client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={"current_password": "TempPass99!", "new_password": "short"},
    )
    assert too_short.status_code == 422

    # Новий пароль збігається з поточним -> 422
    same_password = await async_client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={"current_password": "TempPass99!", "new_password": "TempPass99!"},
    )
    assert same_password.status_code == 422

    # Валідна зміна скидає must_change_password у False
    success_resp = await async_client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={"current_password": "TempPass99!", "new_password": "NewPassword2026!"},
    )
    assert success_resp.status_code == 200
    assert success_resp.json()["user"]["must_change_password"] is False


@pytest.mark.asyncio
async def test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(
    async_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє rate limiting /api/v1/auth/login: 429 із Retry-After та скидання при успіху."""
    monkeypatch.setattr(settings, "ENABLE_LOGIN_RATE_LIMIT", True)
    monkeypatch.setattr(settings, "LOGIN_RATE_LIMIT_MAX_ATTEMPTS", 3)
    monkeypatch.setattr(settings, "LOGIN_RATE_LIMIT_WINDOW_SECONDS", 60)

    # 1. Успішний вхід до досягнення ліміту скидає лічильник невдалих спроб
    for _ in range(2):
        failed = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "student1@kpefk.lcloud.in.ua", "password": "WrongPassword!"},
        )
        assert failed.status_code == 401

    success_reset = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "student1@kpefk.lcloud.in.ua", "password": "Student123!"},
    )
    assert success_reset.status_code == 200

    # 2. Після скидання можна зробити ще 3 невдалі спроби (401), а 4-та дає 429
    for _ in range(3):
        failed = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "student1@kpefk.lcloud.in.ua", "password": "WrongPassword!"},
        )
        assert failed.status_code == 401

    blocked = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "student1@kpefk.lcloud.in.ua", "password": "Student123!"},
    )
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers
    retry_after = int(blocked.headers["Retry-After"])
    assert 1 <= retry_after <= 60
    blocked_body = blocked.json()
    assert blocked_body["code"] == "TOO_MANY_LOGIN_ATTEMPTS"
    assert "Забагато невдалих спроб входу" in blocked_body["detail"]

    # 3. Інший email із того самого IP не заблокований (ключ = IP + email)
    other_user_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "student2@kpefk.lcloud.in.ua", "password": "Student123!"},
    )
    assert other_user_login.status_code == 200


@pytest.mark.asyncio
async def test_hash_and_verify_password_async_offload_to_worker_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Перевіряє роботу hash_password_async / verify_password_async у пулі потоків."""
    from app.core import security as security_module

    long_cyrillic_password = (
        "АсинхроннийКириличнийПарольДовшийЗа72БайтиДляПеревіркиThreadpool2026!"
    )
    assert len(long_cyrillic_password.encode("utf-8")) > 100

    # 1. Реальне хешування та верифікація через threadpool
    hashed = await hash_password_async(long_cyrillic_password)
    assert hashed.startswith(PASSWORD_HASH_PREFIX)
    assert await verify_password_async(long_cyrillic_password, hashed) is True
    assert await verify_password_async(f"{long_cyrillic_password}x", hashed) is False
    assert await verify_password_async(long_cyrillic_password, "") is False

    # Зворотна сумісність із legacy bcrypt-хешем через async-обгортку
    legacy_hash = bcrypt.hashpw(b"LegacyAsync1!", bcrypt.gensalt(rounds=4)).decode(
        "utf-8"
    )
    assert await verify_password_async("LegacyAsync1!", legacy_hash) is True
    assert await verify_password_async("WrongAsync1!", legacy_hash) is False
    assert await verify_password_async(long_cyrillic_password, legacy_hash) is False

    # 2. Підтверджуємо виконання у фоновому потоці (відмінному від потоку Event Loop)
    event_loop_thread_id = threading.get_ident()
    observed_thread_ids: list[int] = []

    def _recording_hash(plain_password: str) -> str:
        observed_thread_ids.append(threading.get_ident())
        return hash_password(plain_password)

    def _recording_verify(plain_password: str, password_hash: str) -> bool:
        observed_thread_ids.append(threading.get_ident())
        return verify_password(plain_password, password_hash)

    monkeypatch.setattr(security_module, "hash_password", _recording_hash)
    monkeypatch.setattr(security_module, "verify_password", _recording_verify)

    worker_hash = await hash_password_async("WorkerThreadPass1!")
    assert await verify_password_async("WorkerThreadPass1!", worker_hash) is True
    assert len(observed_thread_ids) == 2
    assert all(tid != event_loop_thread_id for tid in observed_thread_ids)
