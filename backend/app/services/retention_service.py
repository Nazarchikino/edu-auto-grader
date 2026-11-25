import argparse
import asyncio
import logging
import uuid
from collections import defaultdict
from collections.abc import AsyncIterator, Iterable, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Literal

from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.progress import Submission

RETENTION_CLEANUP_INTERVAL_SECONDS: int = 24 * 60 * 60
RETENTION_ADVISORY_LOCK_ID: int = 74839201
SUPERSEDED_SUBMISSION_GRACE_HOURS: int = 24

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RetentionCleanupSummary:
    """Підсумок очищення прострочених файлів та вихідного HTML-коду практичних робіт."""

    cutoff: datetime
    retention_days: int
    dry_run: bool
    inspected_submissions: int
    cleaned_submissions: int
    deleted_files: int
    missing_files: int
    skipped_unsafe_paths: int
    cleared_raw_code: int
    superseded_inspected_groups: int = 0
    superseded_cleaned_submissions: int = 0
    superseded_deleted_files: int = 0
    skipped_due_to_lock: bool = False


@dataclass(frozen=True, slots=True)
class SupersededCleanupSummary:
    """Підсумок очищення проміжних файлів перездач (залишаються найкраща та остання)."""

    cutoff: datetime
    grace_hours: int
    dry_run: bool
    inspected_groups: int
    inspected_submissions: int
    cleaned_submissions: int
    deleted_files: int
    missing_files: int
    skipped_unsafe_paths: int


def _normalize_utc(value: datetime) -> datetime:
    """Нормалізує мітку часу до UTC для коректного порівняння naive/aware дат."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _is_postgresql_session(session: AsyncSession) -> bool:
    """Визначає, чи підключена сесія БД до діалекту PostgreSQL."""
    bind: object = getattr(session, "bind", None)
    if bind is None:
        get_bind = getattr(session, "get_bind", None)
        if callable(get_bind):
            try:
                bind = get_bind()
            except Exception:
                bind = None
    dialect: object = getattr(bind, "dialect", None)
    dialect_name: object = getattr(dialect, "name", None)
    return isinstance(dialect_name, str) and dialect_name.startswith("postgresql")


@asynccontextmanager
async def _postgresql_retention_advisory_lock(
    session: AsyncSession,
    *,
    lock_id: int = RETENTION_ADVISORY_LOCK_ID,
) -> AsyncIterator[bool]:
    """Бере PostgreSQL advisory lock для ізоляції очищення між воркерами (на SQLite — no-op)."""
    if not _is_postgresql_session(session):
        yield True
        return

    bind: object = getattr(session, "bind", None)
    if bind is None:
        get_bind = getattr(session, "get_bind", None)
        if callable(get_bind):
            try:
                bind = get_bind()
            except Exception:
                bind = None

    if isinstance(bind, AsyncEngine):
        async with bind.connect() as lock_conn:
            lock_result = await lock_conn.execute(
                text("SELECT pg_try_advisory_lock(:lock_id)"),
                {"lock_id": lock_id},
            )
            await lock_conn.commit()
            acquired = bool(lock_result.scalar_one())
            if not acquired:
                logger.info(
                    "Очищення файлів робіт уже виконується іншим воркером "
                    "(pg_try_advisory_lock=%d); поточний цикл пропущено.",
                    lock_id,
                )
                yield False
                return

            try:
                yield True
            finally:
                try:
                    await lock_conn.execute(
                        text("SELECT pg_advisory_unlock(:lock_id)"),
                        {"lock_id": lock_id},
                    )
                    await lock_conn.commit()
                except Exception:
                    logger.warning(
                        "Не вдалося звільнити pg_advisory_unlock(%d).",
                        lock_id,
                        exc_info=True,
                    )
        return

    session_lock_result = await session.execute(
        text("SELECT pg_try_advisory_lock(:lock_id)"),
        {"lock_id": lock_id},
    )
    acquired = bool(session_lock_result.scalar_one())
    if not acquired:
        logger.info(
            "Очищення файлів робіт уже виконується іншим воркером "
            "(pg_try_advisory_lock=%d); поточний цикл пропущено.",
            lock_id,
        )
        yield False
        return

    try:
        yield True
    finally:
        try:
            await session.execute(
                text("SELECT pg_advisory_unlock(:lock_id)"),
                {"lock_id": lock_id},
            )
        except Exception:
            logger.warning(
                "Не вдалося звільнити pg_advisory_unlock(%d).",
                lock_id,
                exc_info=True,
            )


def resolve_submission_file_path(
    raw_file_path: str | None,
    upload_dir: Path,
) -> Path | None:
    """Резолвить шлях до файлу здачі та перевіряє, що він лежить усередині `upload_dir`."""
    if raw_file_path is None:
        return None
    cleaned = raw_file_path.strip()
    if not cleaned or "\x00" in cleaned:
        return None

    try:
        base_dir = upload_dir.resolve()
        candidate = Path(cleaned)

        if candidate.is_absolute():
            resolved = candidate.resolve()
            if resolved != base_dir and resolved.is_relative_to(base_dir):
                return resolved
            return None

        resolved = candidate.resolve()
        if resolved != base_dir and resolved.is_relative_to(base_dir):
            return resolved

        joined = (base_dir / candidate).resolve()
        if joined != base_dir and joined.is_relative_to(base_dir):
            return joined
    except (OSError, ValueError):
        return None

    return None


def delete_submission_file_safely(
    raw_file_path: str | None,
    *,
    upload_dir: Path,
) -> Literal["deleted", "missing", "unsafe", "empty"]:
    """Безпечно видаляє фізичний файл здачі з диска лише в межах `upload_dir`."""
    if raw_file_path is None or not raw_file_path.strip():
        return "empty"

    resolved_path = resolve_submission_file_path(raw_file_path, upload_dir)
    if resolved_path is None:
        logger.warning(
            "Пропущено видалення файлу здачі поза межами UPLOADS_DIR: %s",
            raw_file_path,
        )
        return "unsafe"

    try:
        if not resolved_path.is_file():
            return "missing"
        resolved_path.unlink(missing_ok=True)
        return "deleted"
    except OSError:
        logger.warning(
            "Не вдалося видалити фізичний файл здачі з диска: %s",
            resolved_path,
            exc_info=True,
        )
        return "missing"


def delete_submission_files_for_paths(
    file_paths: Iterable[str | None],
    *,
    upload_dir: Path,
) -> int:
    """Безпечно видаляє з диска унікальні файли здач із переданого списку шляхів."""
    deleted_count = 0
    seen_paths: set[str] = set()

    for raw_path in file_paths:
        if raw_path is None:
            continue
        normalized = raw_path.strip()
        if not normalized or normalized in seen_paths:
            continue
        seen_paths.add(normalized)

        outcome = delete_submission_file_safely(normalized, upload_dir=upload_dir)
        if outcome == "deleted":
            deleted_count += 1

    return deleted_count


async def delete_submission_file_safely_async(
    raw_file_path: str | None,
    *,
    upload_dir: Path,
) -> Literal["deleted", "missing", "unsafe", "empty"]:
    """Асинхронно видаляє фізичний файл здачі у threadpool лише в межах `upload_dir`."""
    return await run_in_threadpool(
        delete_submission_file_safely,
        raw_file_path,
        upload_dir=upload_dir,
    )


async def delete_submission_files_for_paths_async(
    file_paths: Iterable[str | None],
    *,
    upload_dir: Path,
) -> int:
    """Асинхронно видаляє унікальні файли здач у threadpool без блокування Event Loop."""
    materialized_paths = list(file_paths)
    if not materialized_paths:
        return 0
    return await run_in_threadpool(
        delete_submission_files_for_paths,
        materialized_paths,
        upload_dir=upload_dir,
    )


def _inspect_submission_file_paths(
    file_paths: Sequence[str],
    *,
    upload_dir: Path,
) -> tuple[int, int, int]:
    """Перевіряє фізичну наявність файлів на диску для dry-run очищення (у threadpool)."""
    existing_files = 0
    missing_files = 0
    skipped_unsafe_paths = 0
    for raw_path in file_paths:
        resolved_path = resolve_submission_file_path(raw_path, upload_dir)
        if resolved_path is None:
            skipped_unsafe_paths += 1
        elif resolved_path.is_file():
            existing_files += 1
        else:
            missing_files += 1
    return existing_files, missing_files, skipped_unsafe_paths


def _delete_submission_file_paths_with_stats(
    file_paths: Sequence[str],
    *,
    upload_dir: Path,
) -> tuple[int, int, int]:
    """Видаляє список файлів із диска у threadpool і повертає статистику результатів."""
    deleted_files = 0
    missing_files = 0
    skipped_unsafe_paths = 0
    for raw_path in file_paths:
        outcome = delete_submission_file_safely(raw_path, upload_dir=upload_dir)
        if outcome == "deleted":
            deleted_files += 1
        elif outcome == "missing":
            missing_files += 1
        elif outcome == "unsafe":
            skipped_unsafe_paths += 1
    return deleted_files, missing_files, skipped_unsafe_paths


async def cleanup_expired_submissions(
    session: AsyncSession,
    *,
    retention_days: int | None = None,
    upload_dir: Path | None = None,
    dry_run: bool = False,
    now: datetime | None = None,
) -> RetentionCleanupSummary:
    """Очищує файли та raw_code для здач старших за retention_days, зберігаючи оцінки в БД."""
    effective_retention_days = (
        retention_days
        if retention_days is not None
        else settings.SUBMISSION_FILE_RETENTION_DAYS
    )
    if effective_retention_days < 1:
        raise ValueError("Параметр retention_days має бути не меншим за 1 день.")

    effective_upload_dir = upload_dir if upload_dir is not None else settings.UPLOADS_DIR
    current_time = _normalize_utc(now if now is not None else datetime.now(UTC))
    cutoff = current_time - timedelta(days=effective_retention_days)

    stmt = (
        select(Submission)
        .where(
            Submission.submitted_at < cutoff,
            or_(
                Submission.file_path.is_not(None),
                Submission.raw_code.is_not(None),
            ),
        )
        .order_by(Submission.submitted_at.asc())
    )
    result = await session.execute(stmt)
    expired_submissions = list(result.scalars().all())

    inspected_submissions = len(expired_submissions)
    cleaned_submissions = 0
    deleted_files = 0
    missing_files = 0
    skipped_unsafe_paths = 0
    cleared_raw_code = 0

    if dry_run:
        dry_run_paths: list[str] = []
        for submission in expired_submissions:
            if submission.file_path is not None and submission.file_path.strip():
                dry_run_paths.append(submission.file_path)
            if submission.raw_code is not None:
                cleared_raw_code += 1
            cleaned_submissions += 1

        if dry_run_paths:
            deleted_files, missing_files, skipped_unsafe_paths = (
                await run_in_threadpool(
                    _inspect_submission_file_paths,
                    dry_run_paths,
                    upload_dir=effective_upload_dir,
                )
            )

        return RetentionCleanupSummary(
            cutoff=cutoff,
            retention_days=effective_retention_days,
            dry_run=True,
            inspected_submissions=inspected_submissions,
            cleaned_submissions=cleaned_submissions,
            deleted_files=deleted_files,
            missing_files=missing_files,
            skipped_unsafe_paths=skipped_unsafe_paths,
            cleared_raw_code=cleared_raw_code,
        )

    paths_to_delete: list[str] = []
    for submission in expired_submissions:
        if submission.file_path is not None:
            if submission.file_path.strip():
                paths_to_delete.append(submission.file_path)
            submission.file_path = None
        if submission.raw_code is not None:
            submission.raw_code = None
            cleared_raw_code += 1
        cleaned_submissions += 1

    if expired_submissions:
        await session.commit()

    if paths_to_delete:
        deleted_files, missing_files, skipped_unsafe_paths = await run_in_threadpool(
            _delete_submission_file_paths_with_stats,
            paths_to_delete,
            upload_dir=effective_upload_dir,
        )

    return RetentionCleanupSummary(
        cutoff=cutoff,
        retention_days=effective_retention_days,
        dry_run=False,
        inspected_submissions=inspected_submissions,
        cleaned_submissions=cleaned_submissions,
        deleted_files=deleted_files,
        missing_files=missing_files,
        skipped_unsafe_paths=skipped_unsafe_paths,
        cleared_raw_code=cleared_raw_code,
    )


async def cleanup_superseded_submission_files(
    session: AsyncSession,
    *,
    grace_hours: int | None = None,
    upload_dir: Path | None = None,
    dry_run: bool = False,
    now: datetime | None = None,
) -> SupersededCleanupSummary:
    """Видаляє з диска файли проміжних перездач (>24 год), лишаючи найкращу й останню здачі."""
    effective_grace_hours = (
        grace_hours
        if grace_hours is not None
        else settings.SUBMISSION_SUPERSEDED_GRACE_HOURS
    )
    if effective_grace_hours < 0:
        raise ValueError("Параметр grace_hours має бути невід'ємним (>= 0).")

    effective_upload_dir = upload_dir if upload_dir is not None else settings.UPLOADS_DIR
    current_time = _normalize_utc(now if now is not None else datetime.now(UTC))
    cutoff = current_time - timedelta(hours=effective_grace_hours)

    stmt = (
        select(Submission)
        .where(Submission.file_path.is_not(None))
        .order_by(Submission.submitted_at.desc(), Submission.id.desc())
    )
    result = await session.execute(stmt)
    submissions_with_files = [
        item
        for item in result.scalars().all()
        if item.file_path is not None and item.file_path.strip()
    ]

    grouped_by_pair: dict[tuple[uuid.UUID, uuid.UUID], list[Submission]] = defaultdict(list)
    for submission in submissions_with_files:
        grouped_by_pair[(submission.student_id, submission.practical_id)].append(submission)

    inspected_groups = 0
    inspected_submissions = 0
    candidates_to_clean: list[Submission] = []
    paths_to_delete: list[str] = []

    for pair_submissions in grouped_by_pair.values():
        if len(pair_submissions) <= 2:
            continue

        inspected_groups += 1
        inspected_submissions += len(pair_submissions)

        best_submission = max(
            pair_submissions,
            key=lambda item: (
                Decimal(str(item.final_score)),
                _normalize_utc(item.submitted_at),
                str(item.id),
            ),
        )
        latest_submission = max(
            pair_submissions,
            key=lambda item: (
                _normalize_utc(item.submitted_at),
                str(item.id),
            ),
        )
        keep_ids = {best_submission.id, latest_submission.id}
        kept_paths = {
            item.file_path.strip()
            for item in pair_submissions
            if item.id in keep_ids and item.file_path is not None
        }

        for candidate in pair_submissions:
            if candidate.id in keep_ids:
                continue
            if _normalize_utc(candidate.submitted_at) >= cutoff:
                continue
            candidates_to_clean.append(candidate)
            if candidate.file_path is not None:
                stripped_path = candidate.file_path.strip()
                if stripped_path and stripped_path not in kept_paths:
                    paths_to_delete.append(candidate.file_path)

    cleaned_submissions = len(candidates_to_clean)
    deleted_files = 0
    missing_files = 0
    skipped_unsafe_paths = 0

    if dry_run:
        if paths_to_delete:
            deleted_files, missing_files, skipped_unsafe_paths = await run_in_threadpool(
                _inspect_submission_file_paths,
                paths_to_delete,
                upload_dir=effective_upload_dir,
            )
        return SupersededCleanupSummary(
            cutoff=cutoff,
            grace_hours=effective_grace_hours,
            dry_run=True,
            inspected_groups=inspected_groups,
            inspected_submissions=inspected_submissions,
            cleaned_submissions=cleaned_submissions,
            deleted_files=deleted_files,
            missing_files=missing_files,
            skipped_unsafe_paths=skipped_unsafe_paths,
        )

    for candidate in candidates_to_clean:
        candidate.file_path = None

    if candidates_to_clean:
        await session.commit()

    if paths_to_delete:
        deleted_files, missing_files, skipped_unsafe_paths = await run_in_threadpool(
            _delete_submission_file_paths_with_stats,
            paths_to_delete,
            upload_dir=effective_upload_dir,
        )

    return SupersededCleanupSummary(
        cutoff=cutoff,
        grace_hours=effective_grace_hours,
        dry_run=False,
        inspected_groups=inspected_groups,
        inspected_submissions=inspected_submissions,
        cleaned_submissions=cleaned_submissions,
        deleted_files=deleted_files,
        missing_files=missing_files,
        skipped_unsafe_paths=skipped_unsafe_paths,
    )


async def run_retention_cleanup_once(
    *,
    retention_days: int | None = None,
    upload_dir: Path | None = None,
    dry_run: bool = False,
    include_superseded: bool = True,
    superseded_grace_hours: int | None = None,
) -> RetentionCleanupSummary:
    """Виконує один захищений advisory-блокуванням цикл очищення прострочених і проміжних файлів."""
    effective_retention_days = (
        retention_days
        if retention_days is not None
        else settings.SUBMISSION_FILE_RETENTION_DAYS
    )
    async with AsyncSessionLocal() as session, _postgresql_retention_advisory_lock(
        session
    ) as lock_acquired:
        if not lock_acquired:
            now_utc = datetime.now(UTC)
            return RetentionCleanupSummary(
                cutoff=now_utc - timedelta(days=max(effective_retention_days, 1)),
                retention_days=effective_retention_days,
                dry_run=dry_run,
                inspected_submissions=0,
                cleaned_submissions=0,
                deleted_files=0,
                missing_files=0,
                skipped_unsafe_paths=0,
                cleared_raw_code=0,
                skipped_due_to_lock=True,
            )

        expired_summary = await cleanup_expired_submissions(
            session,
            retention_days=retention_days,
            upload_dir=upload_dir,
            dry_run=dry_run,
        )

        superseded_groups = 0
        superseded_cleaned = 0
        superseded_deleted = 0
        superseded_missing = 0
        superseded_unsafe = 0
        if include_superseded:
            superseded_summary = await cleanup_superseded_submission_files(
                session,
                grace_hours=superseded_grace_hours,
                upload_dir=upload_dir,
                dry_run=dry_run,
            )
            superseded_groups = superseded_summary.inspected_groups
            superseded_cleaned = superseded_summary.cleaned_submissions
            superseded_deleted = superseded_summary.deleted_files
            superseded_missing = superseded_summary.missing_files
            superseded_unsafe = superseded_summary.skipped_unsafe_paths

        return RetentionCleanupSummary(
            cutoff=expired_summary.cutoff,
            retention_days=expired_summary.retention_days,
            dry_run=expired_summary.dry_run,
            inspected_submissions=expired_summary.inspected_submissions,
            cleaned_submissions=expired_summary.cleaned_submissions,
            deleted_files=expired_summary.deleted_files,
            missing_files=expired_summary.missing_files + superseded_missing,
            skipped_unsafe_paths=expired_summary.skipped_unsafe_paths + superseded_unsafe,
            cleared_raw_code=expired_summary.cleared_raw_code,
            superseded_inspected_groups=superseded_groups,
            superseded_cleaned_submissions=superseded_cleaned,
            superseded_deleted_files=superseded_deleted,
            skipped_due_to_lock=False,
        )


async def run_periodic_retention_cleanup(
    *,
    interval_seconds: float = RETENTION_CLEANUP_INTERVAL_SECONDS,
) -> None:
    """Фоновий цикл очищення прострочених і проміжних файлів робіт: при старті та кожні 24 год."""
    while True:
        try:
            summary = await run_retention_cleanup_once(
                retention_days=settings.SUBMISSION_FILE_RETENTION_DAYS,
                upload_dir=settings.UPLOADS_DIR,
                dry_run=False,
                include_superseded=True,
                superseded_grace_hours=settings.SUBMISSION_SUPERSEDED_GRACE_HOURS,
            )
            if summary.skipped_due_to_lock:
                logger.info(
                    "Фонове автоочищення пропущено: блокування вже утримується іншим воркером."
                )
            else:
                logger.info(
                    "Автоочищення файлів робіт завершено: прострочених=%d/%d "
                    "(видалено_файлів=%d, очищено_html=%d), проміжних_перездач=%d "
                    "(видалено_файлів=%d, груп=%d), відсутніх=%d, небезпечних=%d.",
                    summary.cleaned_submissions,
                    summary.inspected_submissions,
                    summary.deleted_files,
                    summary.cleared_raw_code,
                    summary.superseded_cleaned_submissions,
                    summary.superseded_deleted_files,
                    summary.superseded_inspected_groups,
                    summary.missing_files,
                    summary.skipped_unsafe_paths,
                )
        except asyncio.CancelledError:
            logger.info("Фонову задачу автоочищення файлів робіт зупинено.")
            raise
        except Exception:
            logger.exception(
                "Помилка фонового автоочищення файлів робіт; "
                "повторна спроба відбудеться у наступному циклі."
            )

        await asyncio.sleep(interval_seconds)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI-точка входу (`python -m app.services.retention_service [--dry-run]`)."""
    parser = argparse.ArgumentParser(
        description=(
            "Автоочищення фізичних файлів і HTML-коду практичних робіт старших за термін "
            "зберігання (90 днів) та проміжних перездач (>24 год)."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показати кількість робіт до очищення без видалення файлів та змін у БД.",
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=None,
        help=(
            "Перевизначити термін зберігання у днях (>= 1). "
            "За замовчуванням використовується SUBMISSION_FILE_RETENTION_DAYS."
        ),
    )
    parser.add_argument(
        "--superseded-grace-hours",
        type=int,
        default=None,
        help=(
            "Мінімальний вік проміжної перездачі в годинах (>= 0) перед видаленням файлу "
            "(за замовчуванням SUBMISSION_SUPERSEDED_GRACE_HOURS = 24)."
        ),
    )
    parser.add_argument(
        "--skip-superseded",
        action="store_true",
        help="Пропустити очищення проміжних файлів перездач (виконати лише 90-денне очищення).",
    )
    args = parser.parse_args(argv)

    if args.retention_days is not None and args.retention_days < 1:
        parser.error("--retention-days має бути не меншим за 1.")
    if args.superseded_grace_hours is not None and args.superseded_grace_hours < 0:
        parser.error("--superseded-grace-hours має бути невід'ємним (>= 0).")

    summary = asyncio.run(
        run_retention_cleanup_once(
            retention_days=args.retention_days,
            upload_dir=settings.UPLOADS_DIR,
            dry_run=bool(args.dry_run),
            include_superseded=not bool(args.skip_superseded),
            superseded_grace_hours=args.superseded_grace_hours,
        )
    )
    mode_label = "DRY-RUN" if summary.dry_run else "APPLIED"
    if summary.skipped_due_to_lock:
        print(f"[retention:{mode_label}] skipped_due_to_lock=True")
        return 0

    print(
        f"[retention:{mode_label}] retention_days={summary.retention_days} "
        f"cutoff={summary.cutoff.isoformat()} "
        f"inspected={summary.inspected_submissions} "
        f"cleaned={summary.cleaned_submissions} "
        f"deleted_files={summary.deleted_files} "
        f"superseded_cleaned={summary.superseded_cleaned_submissions} "
        f"superseded_deleted_files={summary.superseded_deleted_files} "
        f"missing_files={summary.missing_files} "
        f"cleared_raw_code={summary.cleared_raw_code} "
        f"skipped_unsafe={summary.skipped_unsafe_paths}"
    )
    return 0


__all__ = [
    "RETENTION_ADVISORY_LOCK_ID",
    "RETENTION_CLEANUP_INTERVAL_SECONDS",
    "RetentionCleanupSummary",
    "SUPERSEDED_SUBMISSION_GRACE_HOURS",
    "SupersededCleanupSummary",
    "cleanup_expired_submissions",
    "cleanup_superseded_submission_files",
    "delete_submission_file_safely",
    "delete_submission_file_safely_async",
    "delete_submission_files_for_paths",
    "delete_submission_files_for_paths_async",
    "main",
    "resolve_submission_file_path",
    "run_periodic_retention_cleanup",
    "run_retention_cleanup_once",
]


if __name__ == "__main__":
    raise SystemExit(main())
