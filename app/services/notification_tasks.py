from datetime import datetime, timedelta, timezone
from typing import Optional

from app.config import settings
from app.database import SessionLocal
from app.models.account import Account
from app.models.cancellation import Cancellation
from app.models.notification import NotificationEvent
from app.services.email import send_cancellation_email
from app.services.slack import send_slack_message
from app.utils.queue import get_queue


def _safe_json_loads(value):
    if not value:
        return []
    try:
        import json

        return json.loads(value)
    except Exception:
        return []


def _build_payload(account: Account, cancellation: Cancellation) -> dict:
    return {
        "account_id": account.id,
        "account_name": account.name,
        "reason": cancellation.reason,
        "note": cancellation.note or "",
        "last_page": cancellation.last_page or "",
        "last_events": _safe_json_loads(cancellation.last_events),
        "session_duration_seconds": cancellation.session_duration_seconds,
        "browser": cancellation.browser or "",
        "os": cancellation.os or "",
        "js_errors": _safe_json_loads(cancellation.js_errors),
        "time_to_first_value_seconds": cancellation.time_to_first_value_seconds,
        "created_at": cancellation.created_at,
    }


def _compute_retry_delay(attempts: int) -> Optional[int]:
    intervals = settings.notification_retry_interval_list()
    if not intervals:
        return None
    index = min(max(attempts - 1, 0), len(intervals) - 1)
    return intervals[index]


def process_notification_event(event_id: str) -> None:
    with SessionLocal() as db:
        event = db.query(NotificationEvent).filter(NotificationEvent.id == event_id).first()
        if not event:
            return

        event.attempts = (event.attempts or 0) + 1
        event.status = "processing"
        db.commit()

        cancellation = (
            db.query(Cancellation)
            .filter(Cancellation.id == event.cancellation_id)
            .first()
        )
        if not cancellation:
            event.status = "failed"
            event.last_error = "Cancellation not found"
            db.commit()
            return

        account = db.query(Account).filter(Account.id == cancellation.account_id).first()
        if not account:
            event.status = "failed"
            event.last_error = "Account not found"
            db.commit()
            return

        payload = _build_payload(account, cancellation)
        success = False
        error_message = None

        if event.channel == "email":
            success = send_cancellation_email(account.founder_email, payload)
            if not success:
                error_message = "Email send failed"
        elif event.channel == "slack":
            webhook_url = account.slack_webhook_url or settings.default_slack_webhook_url
            if webhook_url:
                success = send_slack_message(webhook_url, payload)
                if not success:
                    error_message = "Slack send failed"
            else:
                success = True
        else:
            error_message = "Unknown channel"

        if success:
            event.status = "sent"
            event.last_error = None
            event.next_attempt_at = None
            db.commit()
            return

        if event.attempts >= settings.notification_max_attempts:
            event.status = "failed"
            event.last_error = error_message or "Send failed"
            event.next_attempt_at = None
            db.commit()
            return

        delay = _compute_retry_delay(event.attempts)
        if delay is None:
            event.status = "failed"
            event.last_error = error_message or "Send failed"
            event.next_attempt_at = None
            db.commit()
            return

        queue = get_queue()
        if not queue:
            event.status = "failed"
            event.last_error = "Retry queue not configured"
            event.next_attempt_at = None
            db.commit()
            return

        event.status = "retrying"
        event.last_error = error_message or "Send failed"
        event.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        db.commit()

        queue.enqueue_in(timedelta(seconds=delay), process_notification_event, event.id)
