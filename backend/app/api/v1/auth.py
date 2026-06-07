from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    PartialTokenResponse,
    RefreshRequest,
    RefreshResponse,
    UserOut,
    EmailVerify,
    ResendVerification,
    PasswordResetRequest,
    PasswordReset,
    UpdateProfile,
    ChangePassword,
    GoogleLoginRequest,
    TotpVerifyRequest,
    TotpSetupResponse,
    TotpEnableRequest,
    TotpDisableRequest,
)
from app.services import auth_service
from app.services import invite_service
from app.core.dependencies import get_current_user, get_verified_user
from app.core.config import settings
from app.models.user import User

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.get("/config")
def get_config():
    """Public endpoint — returns site-wide feature flags the frontend needs."""
    return {"app_mode": settings.APP_MODE}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def register(request: Request, body: UserRegister, db: Session = Depends(get_db)):
    # Extract IP and user agent for fraud detection
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", None)
    
    # ── Invite gate ────────────────────────────────────────────────────────
    invite = None
    if settings.APP_MODE in ("waitlist", "active_beta"):
        if not body.invite_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Signup is currently in waitlist access mode. Join the waitlist at /waitlist.",
            )
        invite = invite_service.validate_invite(db, body.invite_token)
    # ── Normal signup ──────────────────────────────────────────────────────
    user = auth_service.register_user(
        db, email=body.email, password=body.password, full_name=body.full_name,
        referral_code=body.referral_code,
        signup_ip=client_ip,
        signup_user_agent=user_agent,
    )
    # ── Post-signup: consume invite, conditionally grant beta access ───────
    if invite:
        invite_service.mark_invite_used(db, invite)
        # Only grant beta_user in active_beta mode (free access without subscription)
        if settings.APP_MODE == "active_beta":
            user.beta_user = True
        db.commit()
        db.refresh(user)
    return user


@router.post("/login", response_model=Union[TokenResponse, PartialTokenResponse])
@limiter.limit("5/minute")
def login(request: Request, body: UserLogin, db: Session = Depends(get_db)):
    result = auth_service.login_user(db, email=body.email, password=body.password)
    return result


@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("10/minute")
def refresh_token(request: Request, body: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a refresh token for a new access + refresh token pair (rotation)."""
    return auth_service.validate_and_rotate_refresh_token(db, raw_token=body.refresh_token)


# ── Google OAuth ────────────────────────────────────────────────────────────

@router.post("/google", response_model=Union[TokenResponse, PartialTokenResponse])
def google_login(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Verify a Google ID token (from @react-oauth/google) and return a session."""
    result = auth_service.login_or_register_google(
        db,
        id_token=body.id_token,
        invite_token=body.invite_token,
        referral_code=body.referral_code,
    )
    return result


# ── Two-Factor Authentication (TOTP) ───────────────────────────────────────

@router.post("/2fa/verify", response_model=TokenResponse)
@limiter.limit("5/minute")
def verify_2fa(request: Request, body: TotpVerifyRequest, db: Session = Depends(get_db)):
    """Complete a 2FA login: exchange a partial token + TOTP code for full tokens."""
    return auth_service.verify_2fa_login(db, partial_token=body.partial_token, code=body.code)
    return auth_service.verify_2fa_login(db, partial_token=body.partial_token, code=body.code)


@router.post("/2fa/setup", response_model=TotpSetupResponse)
def setup_2fa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user),
):
    """Generate a new TOTP secret. Call /2fa/enable with a valid code to activate it."""
    return auth_service.setup_totp(db, user=current_user)


@router.post("/2fa/enable", response_model=UserOut)
def enable_2fa(
    body: TotpEnableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user),
):
    """Confirm 2FA setup with a valid TOTP code to enable 2FA on this account."""
    return auth_service.enable_totp(db, user=current_user, code=body.code)


@router.post("/2fa/disable", response_model=UserOut)
def disable_2fa(
    body: TotpDisableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user),
):
    """Disable 2FA. Requires the account password for confirmation."""
    return auth_service.disable_totp(db, user=current_user, password=body.password)


@router.post("/verify-email", response_model=UserOut)
@limiter.limit("10/minute")
def verify_email(request: Request, body: EmailVerify, db: Session = Depends(get_db)):
    user = auth_service.verify_email(db, token=body.token)
    return user


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("3/minute")
def resend_verification(request: Request, body: ResendVerification, db: Session = Depends(get_db)):
    auth_service.resend_verification(db, email=body.email)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("3/minute")
def forgot_password(request: Request, body: PasswordResetRequest, db: Session = Depends(get_db)):
    auth_service.request_password_reset(db, email=body.email)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def reset_password(request: Request, body: PasswordReset, db: Session = Depends(get_db)):
    auth_service.reset_password(db, token=body.token, new_password=body.new_password)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_verified_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    body: UpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user),
):
    return auth_service.update_profile(db, user=current_user, full_name=body.full_name)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_verified_user),
):
    auth_service.change_password(
        db,
        user=current_user,
        current_password=body.current_password,
        new_password=body.new_password,
    )
