import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class NotificationEvent(Base):
    __tablename__ = "notification_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cancellation_id = Column(
        String(36), ForeignKey("cancellations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    channel = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    attempts = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    next_attempt_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
