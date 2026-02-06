from typing import Optional

from redis import Redis
from rq import Queue

from app.config import settings


def get_redis_connection() -> Optional[Redis]:
    if not settings.redis_url:
        return None
    return Redis.from_url(settings.redis_url)


def get_queue() -> Optional[Queue]:
    conn = get_redis_connection()
    if not conn:
        return None
    return Queue(settings.notification_queue_name, connection=conn)
