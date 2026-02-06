import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Cancellation(Base):
    __tablename__ = "cancellations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(
        String(36), ForeignKey("accounts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reason = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    last_page = Column(String(500), nullable=True)
    last_events = Column(Text, nullable=True)
    session_duration_seconds = Column(Integer, nullable=True)
    browser = Column(String(200), nullable=True)
    os = Column(String(200), nullable=True)
    js_errors = Column(Text, nullable=True)
    time_to_first_value_seconds = Column(Integer, nullable=True)
    raw_context = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
