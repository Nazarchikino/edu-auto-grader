import math
import threading
import time
from collections import deque
from collections.abc import Callable

_MAX_TRACKED_KEYS_BEFORE_SWEEP: int = 4096


def build_login_rate_limit_key(client_ip: str, normalized_email: str) -> str:
    """Формує складений ключ лімітера за IP клієнта та нормалізованим email."""
    cleaned_ip = client_ip.strip() or "unknown"
    cleaned_email = normalized_email.strip().lower()
    return f"{cleaned_ip}|{cleaned_email}"


class SlidingWindowRateLimiter:
    """Потокобезпечний in-memory sliding-window лімітер невдалих спроб автентифікації."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock: Callable[[], float] = clock
        self._lock = threading.Lock()
        self._attempts: dict[str, deque[float]] = {}

    @staticmethod
    def _prune_expired(
        bucket: deque[float],
        *,
        now: float,
        window_seconds: int,
    ) -> None:
        """Видаляє з черги часові мітки, що вийшли за межі ковзного вікна."""
        cutoff = now - float(window_seconds)
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

    def _sweep_empty_buckets(self, *, now: float, window_seconds: int) -> None:
        """Періодично очищує застарілі ключі для обмеження споживання пам'яті."""
        if len(self._attempts) < _MAX_TRACKED_KEYS_BEFORE_SWEEP:
            return
        stale_keys: list[str] = []
        for tracked_key, tracked_bucket in self._attempts.items():
            self._prune_expired(
                tracked_bucket,
                now=now,
                window_seconds=window_seconds,
            )
            if not tracked_bucket:
                stale_keys.append(tracked_key)
        for stale_key in stale_keys:
            self._attempts.pop(stale_key, None)

    def check_limit(
        self,
        key: str,
        *,
        max_attempts: int,
        window_seconds: int,
    ) -> int | None:
        """Повертає кількість секунд Retry-After при перевищенні ліміту або None."""
        now = self._clock()
        with self._lock:
            bucket = self._attempts.get(key)
            if bucket is None:
                return None
            self._prune_expired(bucket, now=now, window_seconds=window_seconds)
            if not bucket:
                self._attempts.pop(key, None)
                return None
            if len(bucket) < max_attempts:
                return None
            remaining = float(window_seconds) - (now - bucket[0])
            return max(1, math.ceil(remaining))

    def record_failure(
        self,
        key: str,
        *,
        window_seconds: int,
    ) -> int:
        """Фіксує невдалу спробу для ключа та повертає поточну кількість спроб у вікні."""
        now = self._clock()
        with self._lock:
            self._sweep_empty_buckets(now=now, window_seconds=window_seconds)
            bucket = self._attempts.get(key)
            if bucket is None:
                bucket = deque()
                self._attempts[key] = bucket
            self._prune_expired(bucket, now=now, window_seconds=window_seconds)
            bucket.append(now)
            return len(bucket)

    def reset_key(self, key: str) -> None:
        """Скидає лічильник невдалих спроб для ключа (наприклад, після успішного входу)."""
        with self._lock:
            self._attempts.pop(key, None)

    def clear(self) -> None:
        """Повністю очищує стан лімітера (для ізоляції тестів)."""
        with self._lock:
            self._attempts.clear()


login_rate_limiter: SlidingWindowRateLimiter = SlidingWindowRateLimiter()
