from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    referral_code: Optional[str] = None
    invite_token: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # For production, consider enabling these additional checks:
        # if not any(c.isupper() for c in v):
        #     raise ValueError("Password must contain at least one uppercase letter")
        # if not any(c.islower() for c in v):
        #     raise ValueError("Password must contain at least one lowercase letter")
        # if not any(c.isdigit() for c in v):
        #     raise ValueError("Password must contain at least one number")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_verified: bool
    is_admin: bool
    beta_user: bool = False
    subscription_status: Optional[str] = None
    subscription_current_period_end: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    auth_provider: str = "email"
    totp_enabled: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class PartialTokenResponse(BaseModel):
    """Returned by /login when the account has 2FA enabled.
    The frontend must POST this token + a TOTP code to /auth/2fa/verify
    to receive a full TokenResponse."""
    requires_2fa: bool = True
    partial_token: str  # short-lived JWT, only valid for /auth/2fa/verify


class GoogleLoginRequest(BaseModel):
    id_token: str          # Google ID token from @react-oauth/google
    invite_token: Optional[str] = None
    referral_code: Optional[str] = None


class TotpVerifyRequest(BaseModel):
    partial_token: str
    code: str              # 6-digit TOTP code


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"



class TotpSetupResponse(BaseModel):
    secret: str            # base32 secret (show to user once for manual entry)
    uri: str               # otpauth:// URI — encode as QR code on the frontend


class TotpEnableRequest(BaseModel):
    code: str              # verify the user can actually generate a valid code


class TotpDisableRequest(BaseModel):
    password: str          # require password confirmation to disable 2FA


class EmailVerify(BaseModel):
    token: str


class ResendVerification(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # For production, consider enabling these additional checks:
        # if not any(c.isupper() for c in v):
        #     raise ValueError("Password must contain at least one uppercase letter")
        # if not any(c.islower() for c in v):
        #     raise ValueError("Password must contain at least one lowercase letter")
        # if not any(c.isdigit() for c in v):
        #     raise ValueError("Password must contain at least one number")
        return v


class UpdateProfile(BaseModel):
    full_name: Optional[str] = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # For production, consider enabling these additional checks:
        # if not any(c.isupper() for c in v):
        #     raise ValueError("Password must contain at least one uppercase letter")
        # if not any(c.islower() for c in v):
        #     raise ValueError("Password must contain at least one lowercase letter")
        # if not any(c.isdigit() for c in v):
        #     raise ValueError("Password must contain at least one number")
        return v
