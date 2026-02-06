import secrets
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import require_dashboard_key
from app.database import get_db
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountOut

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_dashboard_key)])


def _generate_api_key() -> str:
    return secrets.token_urlsafe(32)


@router.get("/accounts", response_model=List[AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    rows = db.query(Account).order_by(Account.created_at.desc()).all()
    return rows


@router.post("/accounts", response_model=AccountOut)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    api_key = payload.api_key or _generate_api_key()
    if payload.id:
        exists = db.query(Account).filter(Account.id == payload.id).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
        account_id = payload.id
    else:
        account_id = str(uuid.uuid4())

    account = Account(
        id=account_id,
        name=payload.name,
        founder_email=payload.founder_email,
        slack_webhook_url=payload.slack_webhook_url,
        api_key=api_key,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.post("/accounts/{account_id}/rotate-key", response_model=AccountOut)
def rotate_account_key(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    account.api_key = _generate_api_key()
    db.commit()
    db.refresh(account)
    return account
