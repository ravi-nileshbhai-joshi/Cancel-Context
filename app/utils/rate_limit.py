import time
from typing import Dict, List

from fastapi import HTTPException, Request, status

from app.config import settings


class InMemoryRateLimiter:
    def __init__(self):
        self._hits: Dict[str, List[float]] = {}

    def allow(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        window_start = now - window_seconds
        history = self._hits.get(key, [])
        history = [ts for ts in history if ts >= window_start]
        if len(history) >= max_requests:
            self._hits[key] = history
            return False
        history.append(now)
        self._hits[key] = history
        return True


limiter = InMemoryRateLimiter()


def enforce_cancel_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"cancel:{client_host}"
    if not limiter.allow(
        key,
        max_requests=settings.cancel_rate_limit_per_minute,
        window_seconds=settings.cancel_rate_limit_window_seconds,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many cancellation requests. Please try again later.",
        )
