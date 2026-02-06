from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


connect_args = {"check_same_thread": False} if _is_sqlite(settings.database_url) else {}
engine_kwargs = {"future": True}
if not _is_sqlite(settings.database_url):
    engine_kwargs.update(
        {
            "pool_pre_ping": settings.db_pool_pre_ping,
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
        }
    )
engine = create_engine(settings.database_url, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
