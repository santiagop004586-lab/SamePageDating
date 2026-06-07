import secrets
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.invite import Invite

logger = logging.getLogger(__name__)


def generate_invite_code() -> str:
    """Return a cryptographically secure 32-character URL-safe token."""
    return secrets.token_urlsafe(32)


def create_invite(db: Session, email: Optional[str] = None, expires_at=None) -> Invite:
    """Create a new invite record and return it."""
    invite = Invite(
        email=email.lower() if email else None,
        invite_code=generate_invite_code(),
        expires_at=expires_at,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    logger.info("Created invite %s for %s", invite.invite_code, email or "open")
    return invite


def validate_invite(db: Session, token: str) -> Invite:
    """
    Validate an invite token.  Raises HTTP 400 if invalid, used, or expired.
    Returns the Invite row if valid.
    """
    invite = db.query(Invite).filter(Invite.invite_code == token).first()
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite code.",
        )
    if invite.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite has already been used.",
        )
    if invite.expires_at:
        exp = invite.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invite has expired.",
            )
    return invite


def mark_invite_used(db: Session, invite: Invite) -> None:
    invite.used = True
    db.commit()
