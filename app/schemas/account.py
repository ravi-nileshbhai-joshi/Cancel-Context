from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    id: Optional[str] = None
    name: str
    founder_email: str
    slack_webhook_url: Optional[str] = None
    api_key: Optional[str] = None


class AccountOut(BaseModel):
    id: str
    name: str
    founder_email: str
    slack_webhook_url: Optional[str] = None
    api_key: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
