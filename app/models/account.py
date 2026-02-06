import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), nullable=False)
    founder_email = Column(String(255), nullable=False)
    slack_webhook_url = Column(String(500), nullable=True)
    api_key = Column(String(64), nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
