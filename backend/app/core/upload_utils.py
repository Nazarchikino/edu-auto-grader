from fastapi import HTTPException
from starlette.datastructures import UploadFile

DEFAULT_UPLOAD_CHUNK_SIZE: int = 65_536
_BYTES_PER_MEGABYTE: int = 1024 * 1024


def format_size_limit_mb(max_bytes: int) -> str:
    """Форматує максимально допустимий розмір файлу в мегабайтах для повідомлень."""
    if max_bytes % _BYTES_PER_MEGABYTE == 0:
        return f"{max_bytes // _BYTES_PER_MEGABYTE} МБ"

    megabytes = max_bytes / _BYTES_PER_MEGABYTE
    if megabytes >= 0.1:
        return f"{megabytes:.1f} МБ"
    if megabytes >= 0.01:
        return f"{megabytes:.2f} МБ"
    return f"{megabytes:.4f} МБ"


def _build_too_large_exception(max_bytes: int) -> HTTPException:
    """Формує HTTP 413 із зрозумілим українським повідомленням про ліміт розміру."""
    return HTTPException(
        status_code=413,
        detail=(
            "Розмір завантаженого файлу перевищує максимально допустимий ліміт "
            f"({format_size_limit_mb(max_bytes)})."
        ),
    )


async def read_upload_file_limited(
    upload_file: UploadFile,
    max_bytes: int,
    chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE,
) -> bytes:
    """Потоково читає UploadFile чанками по 64 КБ із раннім відсіканням (HTTP 413)."""
    if max_bytes <= 0:
        raise ValueError("Параметр max_bytes має бути додатним цілим числом.")
    if chunk_size <= 0:
        raise ValueError("Параметр chunk_size має бути додатним цілим числом.")

    if upload_file.size is not None and upload_file.size > max_bytes:
        raise _build_too_large_exception(max_bytes)

    buffer = bytearray()
    total_bytes = 0

    while True:
        chunk = await upload_file.read(chunk_size)
        if not chunk:
            break
        total_bytes += len(chunk)
        if total_bytes > max_bytes:
            raise _build_too_large_exception(max_bytes)
        buffer.extend(chunk)

    return bytes(buffer)
