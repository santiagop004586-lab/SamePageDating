from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.models.waitlist import WaitlistUser
from app.models.invite import Invite
from app.services import invite_service

router = APIRouter()


# ─── Schemas ────────────────────────────────────────────────────────────────

class WaitlistJoinRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class WaitlistJoinResponse(BaseModel):
    message: str


class InviteCheckResponse(BaseModel):
    valid: bool
    email: Optional[str] = None


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/", response_model=WaitlistJoinResponse, status_code=status.HTTP_201_CREATED)
def join_waitlist(body: WaitlistJoinRequest, db: Session = Depends(get_db)):
    """Add an email to the waitlist.  Idempotent — duplicate emails silently succeed."""
    existing = db.query(WaitlistUser).filter(
        WaitlistUser.email == body.email.lower()
    ).first()
    if not existing:
        entry = WaitlistUser(
            email=body.email.lower(),
            name=body.name,
        )
        db.add(entry)
        db.commit()
    return WaitlistJoinResponse(
        message="You are on the waitlist. We will invite users soon."
    )


@router.get("/check-invite", response_model=InviteCheckResponse)
def check_invite(token: str, db: Session = Depends(get_db)):
    """
    Let the frontend verify an invite token before rendering the signup form.
    Returns {valid: true/false}.  Does NOT consume the token.
    """
    invite = db.query(Invite).filter(Invite.invite_code == token).first()
    if not invite or invite.used:
        return InviteCheckResponse(valid=False)

    from datetime import timezone
    if invite.expires_at:
        exp = invite.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        from datetime import datetime
        if datetime.now(timezone.utc) > exp:
            return InviteCheckResponse(valid=False)

    return InviteCheckResponse(valid=True, email=invite.email)
