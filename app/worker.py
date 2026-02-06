from rq import Connection, Worker

from app.config import settings
from app.utils.queue import get_redis_connection


def main() -> None:
    conn = get_redis_connection()
    if not conn:
        raise RuntimeError("REDIS_URL is not configured. Cannot start worker.")
    with Connection(conn):
        worker = Worker([settings.notification_queue_name])
        worker.work()


if __name__ == "__main__":
    main()
