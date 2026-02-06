import json
import urllib.request
from typing import Any, Dict


def send_slack_message(webhook_url: str, payload: Dict[str, Any]) -> bool:
    lines = [
        f"Cancellation - {payload.get('account_name', '')}",
        f"Reason: {payload.get('reason', '')}",
        f"Note: {payload.get('note', '')}",
        f"Last page: {payload.get('last_page', '')}",
        f"Session duration (sec): {payload.get('session_duration_seconds', '')}",
        f"Browser: {payload.get('browser', '')}",
        f"OS: {payload.get('os', '')}",
    ]
    text = "\n".join(lines).strip()

    body = {"text": text}
    data = json.dumps(body).encode("utf-8")

    try:
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10):
            pass
        return True
    except Exception as exc:
        print(f"Slack send failed: {exc}")
        return False
