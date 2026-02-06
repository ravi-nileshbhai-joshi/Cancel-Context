from typing import Optional

from fastapi import Header, HTTPException, status

from app.config import settings


def require_dashboard_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    if not settings.dashboard_api_key:
        return
    if x_api_key != settings.dashboard_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def require_cancel_key(x_cancel_key: Optional[str] = Header(default=None, alias="X-Cancel-Key")):
    return x_cancel_key
