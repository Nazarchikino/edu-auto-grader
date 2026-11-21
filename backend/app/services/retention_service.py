import argparse
import asyncio
import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.progress import Submission

RETENTION_CLEANUP_INTERVAL_SECONDS: int = 24 * 60 * 60

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

    current_time = now if now is not None else datetime.now(UTC)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=UTC)
    else:
        current_time = current_time.astimezone(UTC)

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
        for submission in expired_submissions:
            if submission.file_path is not None and submission.file_path.strip():
                resolved_path = resolve_submission_file_path(
                    submission.file_path,
                    effective_upload_dir,
                )
                if resolved_path is None:
                    skipped_unsafe_paths += 1
                elif resolved_path.is_file():
                    deleted_files += 1
                else:
                    missing_files += 1
            if submission.raw_code is not None:
                cleared_raw_code += 1
            cleaned_submissions += 1

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

    for raw_path in paths_to_delete:
        outcome = delete_submission_file_safely(
            raw_path,
            upload_dir=effective_upload_dir,
        )
        if outcome == "deleted":
            deleted_files += 1
        elif outcome == "missing":
            missing_files += 1
        elif outcome == "unsafe":
            skipped_unsafe_paths += 1

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


async def run_retention_cleanup_once(
    *,
    retention_days: int | None = None,
    upload_dir: Path | None = None,
    dry_run: bool = False,
) -> RetentionCleanupSummary:
    """Виконує один запуск очищення прострочених робіт у власній сесії БД."""
    async with AsyncSessionLocal() as session:
        return await cleanup_expired_submissions(
            session,
            retention_days=retention_days,
            upload_dir=upload_dir,
            dry_run=dry_run,
        )


async def run_periodic_retention_cleanup(
    *,
    interval_seconds: float = RETENTION_CLEANUP_INTERVAL_SECONDS,
) -> None:
    """Фоновий цикл очищення прострочених файлів робіт: при старті та кожні 24 години."""
    while True:
        try:
            summary = await run_retention_cleanup_once(
                retention_days=settings.SUBMISSION_FILE_RETENTION_DAYS,
                upload_dir=settings.UPLOADS_DIR,
                dry_run=False,
            )
            logger.info(
                "Автоочищення файлів робіт завершено: перевірено=%d, очищено=%d, "
                "видалено_файлів=%d, відсутніх=%d, очищено_html=%d, небезпечних=%d.",
                summary.inspected_submissions,
                summary.cleaned_submissions,
                summary.deleted_files,
                summary.missing_files,
                summary.cleared_raw_code,
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
            "Автоочищення фізичних файлів та HTML-коду практичних робіт, "
            "старших за налаштований термін зберігання (за замовчуванням 90 днів)."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показати кількість прострочених робіт без видалення файлів та змін у БД.",
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
    args = parser.parse_args(argv)

    if args.retention_days is not None and args.retention_days < 1:
        parser.error("--retention-days має бути не меншим за 1.")

    summary = asyncio.run(
        run_retention_cleanup_once(
            retention_days=args.retention_days,
            upload_dir=settings.UPLOADS_DIR,
            dry_run=bool(args.dry_run),
        )
    )
    mode_label = "DRY-RUN" if summary.dry_run else "APPLIED"
    print(
        f"[retention:{mode_label}] retention_days={summary.retention_days} "
        f"cutoff={summary.cutoff.isoformat()} "
        f"inspected={summary.inspected_submissions} "
        f"cleaned={summary.cleaned_submissions} "
        f"deleted_files={summary.deleted_files} "
        f"missing_files={summary.missing_files} "
        f"cleared_raw_code={summary.cleared_raw_code} "
        f"skipped_unsafe={summary.skipped_unsafe_paths}"
    )
    return 0


__all__ = [
    "RETENTION_CLEANUP_INTERVAL_SECONDS",
    "RetentionCleanupSummary",
    "cleanup_expired_submissions",
    "delete_submission_file_safely",
    "delete_submission_files_for_paths",
    "main",
    "resolve_submission_file_path",
    "run_periodic_retention_cleanup",
    "run_retention_cleanup_once",
]


if __name__ == "__main__":
    raise SystemExit(main())
