import json
import smtplib
from email.message import EmailMessage
from typing import Any, Dict, List

from app.config import settings


def _format_list(items: List[Any]) -> str:
    if not items:
        return "None"
    lines = []
    for item in items:
        if isinstance(item, (dict, list)):
            lines.append(json.dumps(item))
        else:
            lines.append(str(item))
    return "\n".join(f"- {line}" for line in lines)


def send_cancellation_email(to_address: str, data: Dict[str, Any]) -> bool:
    if not settings.smtp_host or not to_address:
        print("Email disabled or missing smtp_host. Skipping email send.")
        return False

    msg = EmailMessage()
    msg["Subject"] = f"Cancellation - {data.get('reason', 'unknown')}"
    msg["From"] = settings.email_from
    msg["To"] = to_address

    body = "\n".join(
        [
            f"Account: {data.get('account_name', '')}",
            f"Reason: {data.get('reason', '')}",
            f"Note: {data.get('note', '')}",
            f"Last page: {data.get('last_page', '')}",
            f"Session duration (sec): {data.get('session_duration_seconds', '')}",
            f"Browser: {data.get('browser', '')}",
            f"OS: {data.get('os', '')}",
            "Last events:",
            _format_list(data.get('last_events') or []),
            "JS errors:",
            _format_list(data.get('js_errors') or []),
            f"Time to first value (sec): {data.get('time_to_first_value_seconds', '')}",
            f"Created at: {data.get('created_at', '')}",
        ]
    )
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f"Email send failed: {exc}")
        return False


def send_test_email(to_address: str) -> bool:
    if not settings.smtp_host or not to_address:
        print("Email disabled or missing smtp_host. Skipping email send.")
        return False

    msg = EmailMessage()
    msg["Subject"] = "Cancel Context Collector - SMTP test"
    msg["From"] = settings.email_from
    msg["To"] = to_address
    msg.set_content(
        "This is a test email from Cancel Context Collector. "
        "If you received this, SMTP is configured correctly."
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f"Email send failed: {exc}")
        return False
