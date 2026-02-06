import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.auth import require_dashboard_key
from app.database import get_db
from app.models.cancellation import Cancellation
from app.schemas.cancellation import CancellationOut
from app.services.email import send_test_email

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _safe_json_loads(value: Optional[str]):
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _apply_filters(
    q,
    account_id: Optional[str],
    reason: Optional[str],
    from_date: Optional[datetime],
    to_date: Optional[datetime],
):
    if account_id:
        q = q.filter(Cancellation.account_id == account_id)
    if reason:
        q = q.filter(Cancellation.reason == reason)
    if from_date:
        q = q.filter(Cancellation.created_at >= from_date)
    if to_date:
        q = q.filter(Cancellation.created_at <= to_date)
    return q


@router.get(
    "/cancellations",
    response_model=List[CancellationOut],
    dependencies=[Depends(require_dashboard_key)],
)
def list_cancellations(
    account_id: Optional[str] = None,
    reason: Optional[str] = None,
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    query = _apply_filters(db.query(Cancellation), account_id, reason, from_date, to_date)
    rows = query.order_by(Cancellation.created_at.desc()).offset(offset).limit(limit).all()

    results: List[CancellationOut] = []
    for row in rows:
        results.append(
            CancellationOut(
                id=row.id,
                account_id=row.account_id,
                reason=row.reason,
                note=row.note,
                last_page=row.last_page,
                last_events=_safe_json_loads(row.last_events),
                session_duration_seconds=row.session_duration_seconds,
                browser=row.browser,
                os=row.os,
                js_errors=_safe_json_loads(row.js_errors),
                time_to_first_value_seconds=row.time_to_first_value_seconds,
                created_at=row.created_at,
            )
        )
    return results


@router.get("/summary", dependencies=[Depends(require_dashboard_key)])
def summary(
    account_id: Optional[str] = None,
    reason: Optional[str] = None,
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
):
    base = _apply_filters(db.query(Cancellation), account_id, reason, from_date, to_date)
    total = base.count()

    reason_rows = (
        _apply_filters(
            db.query(Cancellation.reason, func.count(Cancellation.id)),
            account_id,
            reason,
            from_date,
            to_date,
        )
        .group_by(Cancellation.reason)
        .all()
    )
    reason_counts = {row[0]: row[1] for row in reason_rows}
    top_reason = None
    if reason_counts:
        top_reason = max(reason_counts.items(), key=lambda item: item[1])[0]

    page_rows = (
        _apply_filters(
            db.query(Cancellation.last_page, func.count(Cancellation.id)),
            account_id,
            None,
            from_date,
            to_date,
        )
        .filter(Cancellation.last_page.isnot(None))
        .filter(Cancellation.last_page != "")
        .group_by(Cancellation.last_page)
        .order_by(func.count(Cancellation.id).desc())
        .limit(5)
        .all()
    )

    top_pages = [{"page": row[0], "count": row[1]} for row in page_rows]

    return {
        "total": total,
        "by_reason": reason_counts,
        "top_reason": top_reason,
        "top_pages": top_pages,
    }


@router.post("/test-email", dependencies=[Depends(require_dashboard_key)])
def test_email(to_address: str):
    ok = send_test_email(to_address)
    if not ok:
        return {"ok": False, "message": "Email send failed or SMTP not configured."}
    return {"ok": True, "message": "Test email sent."}
