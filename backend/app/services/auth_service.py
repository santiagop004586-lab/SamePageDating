import logging
import pyotp
from datetime import datetime, timezone, timedelta
from typing import Optional, Union

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from cryptography.fernet import Fernet, InvalidToken

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_token,
)
from jose import jwt as jose_jwt
from app.core.config import settings
from app.core.email import send_verification_email, send_password_reset_email

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Refresh token DB helpers
# ---------------------------------------------------------------------------

def _store_refresh_token(db: Session, user_id: int, raw_token: str, expires_days: int) -> None:
    """Hash and persist a refresh token in the DB."""
    from app.core.config import settings as _s
    record = RefreshToken(
        user_id=user_id,
        token_hash=RefreshToken.hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=expires_days),
    )
    db.add(record)
    db.commit()


def validate_and_rotate_refresh_token(db: Session, raw_token: str) -> dict:
    """
    Validate a refresh token against the DB and rotate it.
    Returns new {access_token, refresh_token, token_type}.
    Raises 401 on any invalid state.
    If a REVOKED token is presented (reuse detected), all user tokens are revoked.
    """
    payload = decode_token(raw_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    token_hash = RefreshToken.hash_token(raw_token)
    now = datetime.now(timezone.utc)

    record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if record is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not recognised.")

    if record.revoked:
        # Reuse of a revoked token — possible theft. Revoke ALL tokens for this user.
        db.query(RefreshToken).filter(
            RefreshToken.user_id == record.user_id,
            RefreshToken.revoked == False,
        ).update({"revoked": True})
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token already used. All sessions have been revoked.",
        )

    if record.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired.")

    user = db.query(User).filter(User.id == record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or disabled.")

    # Revoke old token
    record.revoked = True
    db.commit()

    # Issue new tokens
    access_token = create_access_token(subject=user.email)
    new_refresh = create_refresh_token(subject=user.email)
    _store_refresh_token(db, user.id, new_refresh, expires_days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return {"access_token": access_token, "refresh_token": new_refresh, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# TOTP secret encryption helpers (reuses TIN_ENCRYPTION_KEY)
# ---------------------------------------------------------------------------

def _get_fernet() -> Optional[Fernet]:
    key = settings.TIN_ENCRYPTION_KEY
    if not key:
        return None
    return Fernet(key.encode() if isinstance(key, str) else key)


def _encrypt_totp_secret(secret: str) -> str:
    f = _get_fernet()
    if not f:
        raise HTTPException(status_code=503, detail="Encryption not configured.")
    return f.encrypt(secret.encode()).decode()


def _decrypt_totp_secret(ciphertext: str) -> str:
    f = _get_fernet()
    if not f:
        raise HTTPException(status_code=503, detail="Encryption not configured.")
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        raise HTTPException(status_code=500, detail="Could not decrypt 2FA secret.")


def register_user(
    db: Session, email: str, password: str, full_name: Optional[str] = None,
    referral_code: Optional[str] = None,
    signup_ip: Optional[str] = None,
    signup_user_agent: Optional[str] = None
) -> User:
    existing = db.query(User).filter(User.email == email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    token = generate_secure_token()
    expires = datetime.now(timezone.utc) + timedelta(
        hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS
    )

    user = User(
        email=email.lower(),
        hashed_password=hash_password(password),
        full_name=full_name,
        verification_token=token,
        verification_token_expires=expires,
        referred_by_code=referral_code or None,
        signup_ip=signup_ip,
        signup_user_agent=signup_user_agent,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    send_verification_email(user.email, token)
    return user


def verify_email(db: Session, token: str) -> User:
    user = (
        db.query(User).filter(User.verification_token == token).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )

    expires = user.verification_token_expires
    if expires:
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired. Please request a new one.",
            )

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    db.refresh(user)
    return user


def resend_verification(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        return  # Don't reveal whether email exists
    if user.is_verified:
        return

    token = generate_secure_token()
    expires = datetime.now(timezone.utc) + timedelta(
        hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS
    )
    user.verification_token = token
    user.verification_token_expires = expires
    db.commit()

    send_verification_email(user.email, token)


def login_user(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email.lower()).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="That username does not exist.",
        )
    
    if not verify_password(password, user.hashed_password or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    # If 2FA is enabled, return a partial token instead of a full session token
    if user.totp_enabled:
        return {
            "requires_2fa": True,
            "partial_token": _create_partial_token(user.id),
        }

    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    _store_refresh_token(db, user.id, refresh_token, expires_days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


def request_password_reset(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        return  # Don't reveal whether email exists

    token = generate_secure_token()
    expires = datetime.now(timezone.utc) + timedelta(
        hours=settings.PASSWORD_RESET_EXPIRE_HOURS
    )
    user.reset_token = token
    user.reset_token_expires = expires
    db.commit()

    send_password_reset_email(user.email, token)


def reset_password(db: Session, token: str, new_password: str) -> None:
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    expires = user.reset_token_expires
    if expires:
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired. Please request a new one.",
            )

    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()


def update_profile(db: Session, user: User, full_name: Optional[str]) -> User:
    if full_name is not None:
        user.full_name = full_name
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.hashed_password or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )
    user.hashed_password = hash_password(new_password)
    db.commit()


# ---------------------------------------------------------------------------
# Partial-token helpers (short-lived tokens used during 2FA challenge)
# ---------------------------------------------------------------------------

def _create_partial_token(user_id: int) -> str:
    """Short-lived JWT (5 min) that is ONLY accepted by /auth/2fa/verify."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    data = {"sub": f"2fa:{user_id}", "exp": expire, "type": "partial"}
    return jose_jwt.encode(
        data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def _verify_partial_token(token: str) -> int:
    """Decode a partial token and return the user_id, or raise 401."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "partial":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired 2FA session.",
        )
    sub: str = payload.get("sub", "")
    if not sub.startswith("2fa:"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA token.",
        )
    try:
        return int(sub.split(":", 1)[1])
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed 2FA token.",
        )


# ---------------------------------------------------------------------------
# 2FA (TOTP) — setup, enable, disable, verify
# ---------------------------------------------------------------------------

def setup_totp(db: Session, user: User) -> dict:
    """Generate a fresh TOTP secret and persist it (unconfirmed).
    Returns the plaintext secret + an otpauth:// URI for QR code rendering.
    """
    secret = pyotp.random_base32()
    user.totp_secret = _encrypt_totp_secret(secret)
    user.totp_enabled = False  # stays False until the user confirms with a valid code
    db.commit()
    uri = pyotp.TOTP(secret).provisioning_uri(
        name=user.email, issuer_name="Section8DealFinder"
    )
    return {"secret": secret, "uri": uri}


def enable_totp(db: Session, user: User, code: str) -> User:
    """Verify a TOTP code against the pending secret and mark 2FA as enabled."""
    if not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No 2FA setup in progress. Call /auth/2fa/setup first.",
        )
    secret = _decrypt_totp_secret(user.totp_secret)
    if not pyotp.TOTP(secret).verify(code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code.",
        )
    user.totp_enabled = True
    db.commit()
    db.refresh(user)
    return user


def disable_totp(db: Session, user: User, password: str) -> User:
    """Disable 2FA after confirming the user's password."""
    if not verify_password(password, user.hashed_password or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password.",
        )
    user.totp_enabled = False
    user.totp_secret = None
    db.commit()
    db.refresh(user)
    return user


def verify_2fa_login(db: Session, partial_token: str, code: str) -> dict:
    """Complete a 2FA login: verify the partial token + TOTP code → return full tokens."""
    user_id = _verify_partial_token(partial_token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.totp_enabled or not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA session.",
        )
    secret = _decrypt_totp_secret(user.totp_secret)
    if not pyotp.TOTP(secret).verify(code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code.",
        )
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    _refresh = create_refresh_token(subject=user.email)
    _store_refresh_token(db, user.id, _refresh, expires_days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return {
        "access_token": create_access_token(subject=user.email),
        "refresh_token": _refresh,
        "token_type": "bearer",
        "user": user,
    }


# ---------------------------------------------------------------------------
# Google OAuth — verify ID token, find-or-create user
# ---------------------------------------------------------------------------

def login_or_register_google(
    db: Session,
    id_token: str,
    invite_token: Optional[str] = None,
    referral_code: Optional[str] = None,
) -> dict:
    """Verify a Google ID token, find or create a matching user, return tokens."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google login is not configured.",
        )

    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests

        idinfo = google_id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception as exc:
        logger.warning("Google ID token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token.",
        )

    google_id: str = idinfo["sub"]
    email: str = idinfo.get("email", "").lower()
    full_name: Optional[str] = idinfo.get("name")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account does not have a public email address.",
        )

    # Find existing user by google_id first, then by email
    user: Optional[User] = (
        db.query(User).filter(User.google_id == google_id).first()
        or db.query(User).filter(User.email == email).first()
    )

    if user is None:
        # Brand-new user via Google — enforce invite gate if active
        invite = None
        if settings.APP_MODE in ("waitlist", "active_beta"):
            if not invite_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Signup is currently in waitlist access mode. Join the waitlist.",
                )
            from app.services import invite_service
            invite = invite_service.validate_invite(db, invite_token)

        user = User(
            email=email,
            full_name=full_name,
            google_id=google_id,
            auth_provider="google",
            is_verified=True,  # Google already verified the email
            hashed_password=None,
            referred_by_code=referral_code or None,
        )
        db.add(user)
        db.flush()  # get user.id for affiliate logic

        if invite:
            from app.services import invite_service
            invite_service.mark_invite_used(db, invite)
            if settings.APP_MODE == "active_beta":
                user.beta_user = True

        db.commit()
        db.refresh(user)
    else:
        # Existing user — link google_id if not yet linked
        if not user.google_id:
            user.google_id = google_id
            user.auth_provider = "google"
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled.",
            )
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

    # If this user also has TOTP enabled, return partial token
    if user.totp_enabled:
        return {
            "requires_2fa": True,
            "partial_token": _create_partial_token(user.id),
        }

    _refresh = create_refresh_token(subject=user.email)
    _store_refresh_token(db, user.id, _refresh, expires_days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return {
        "access_token": create_access_token(subject=user.email),
        "refresh_token": _refresh,
        "token_type": "bearer",
        "user": user,
    }
