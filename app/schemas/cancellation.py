from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import settings


class CancellationCreate(BaseModel):
    reason: str = Field(..., min_length=2)
    note: Optional[str] = None
    last_page: Optional[str] = None
    last_events: Optional[List[Dict[str, Any]]] = None
    session_duration_seconds: Optional[int] = Field(default=None, ge=0)
    browser: Optional[str] = None
    os: Optional[str] = None
    js_errors: Optional[List[str]] = None
    time_to_first_value_seconds: Optional[int] = Field(default=None, ge=0)
    context: Optional[Dict[str, Any]] = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        allowed = settings.allowed_reason_list()
        if allowed and value not in allowed:
            raise ValueError(f"Invalid reason. Allowed: {', '.join(allowed)}")
        return value


class CancellationOut(BaseModel):
    id: str
    account_id: str
    reason: str
    note: Optional[str] = None
    last_page: Optional[str] = None
    last_events: Optional[List[Dict[str, Any]]] = None
    session_duration_seconds: Optional[int] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    js_errors: Optional[List[str]] = None
    time_to_first_value_seconds: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
