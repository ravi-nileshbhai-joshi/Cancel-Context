import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.auth import require_cancel_key
from app.config import settings
from app.database import get_db
from app.models.account import Account
from app.models.cancellation import Cancellation
from app.schemas.cancellation import CancellationCreate, CancellationOut
from app.services.notification import enqueue_founder_notifications
from app.utils.rate_limit import enforce_cancel_rate_limit
from app.utils.user_agent import parse_user_agent

router = APIRouter(prefix="/api/cancel", tags=["cancel"])


def _safe_json_loads(value: Optional[str]):
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


@router.post("/{account_id}", response_model=CancellationOut)
def create_cancellation(
    account_id: str,
    payload: CancellationCreate,
    request: Request,
    cancel_key: str | None = Depends(require_cancel_key),
    __: None = Depends(enforce_cancel_rate_limit),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        if settings.allow_auto_account and settings.default_founder_email:
            account = Account(
                id=account_id,
                name=settings.default_account_name,
                founder_email=settings.default_founder_email,
                slack_webhook_url=settings.default_slack_webhook_url,
                api_key=settings.default_account_api_key,
            )
            db.add(account)
            db.commit()
            db.refresh(account)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
            )
    if account.api_key:
        if cancel_key != account.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid account cancel API key",
            )
    elif settings.cancel_api_key:
        if cancel_key != settings.cancel_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid cancel API key",
            )

    user_agent = payload.browser or request.headers.get("user-agent", "")
    ua_info = parse_user_agent(user_agent)

    last_events_json = json.dumps(payload.last_events) if payload.last_events else None
    js_errors_json = json.dumps(payload.js_errors) if payload.js_errors else None

    raw_context = payload.context or {}
    if user_agent:
        raw_context["user_agent"] = user_agent
    if payload.os:
        raw_context["platform"] = payload.os
    raw_context_json = json.dumps(raw_context) if raw_context else None

    cancellation = Cancellation(
        account_id=account.id,
        reason=payload.reason,
        note=payload.note,
        last_page=payload.last_page,
        last_events=last_events_json,
        session_duration_seconds=payload.session_duration_seconds,
        browser=ua_info["browser"] or None,
        os=ua_info["os"] or payload.os,
        js_errors=js_errors_json,
        time_to_first_value_seconds=payload.time_to_first_value_seconds,
        raw_context=raw_context_json,
    )

    db.add(cancellation)
    db.commit()
    db.refresh(cancellation)

    enqueue_founder_notifications(account, cancellation, db)

    return CancellationOut(
        id=cancellation.id,
        account_id=cancellation.account_id,
        reason=cancellation.reason,
        note=cancellation.note,
        last_page=cancellation.last_page,
        last_events=_safe_json_loads(cancellation.last_events),
        session_duration_seconds=cancellation.session_duration_seconds,
        browser=cancellation.browser,
        os=cancellation.os,
        js_errors=_safe_json_loads(cancellation.js_errors),
        time_to_first_value_seconds=cancellation.time_to_first_value_seconds,
        created_at=cancellation.created_at,
    )
