from typing import List

from app.config import settings
from app.models.notification import NotificationEvent
from app.services.notification_tasks import process_notification_event
from app.utils.queue import get_queue


def _create_event(channel: str, cancellation_id: str) -> NotificationEvent:
    return NotificationEvent(
        cancellation_id=cancellation_id,
        channel=channel,
        status="pending",
        attempts=0,
    )


def enqueue_founder_notifications(account, cancellation, db) -> List[NotificationEvent]:
    events: List[NotificationEvent] = []
    events.append(_create_event("email", cancellation.id))

    webhook_url = account.slack_webhook_url or settings.default_slack_webhook_url
    if webhook_url:
        events.append(_create_event("slack", cancellation.id))

    for event in events:
        db.add(event)
    db.commit()
    for event in events:
        db.refresh(event)

    queue = get_queue()
    for event in events:
        if queue:
            queue.enqueue(process_notification_event, event.id)
        else:
            process_notification_event(event.id)

    return events
