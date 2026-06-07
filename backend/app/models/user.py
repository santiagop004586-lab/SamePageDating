from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # Email verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True, index=True)
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Password reset
    reset_token = Column(String(255), nullable=True, index=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Account state
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    # Stripe / subscription
    stripe_customer_id = Column(String(255), nullable=True, unique=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    subscription_status = Column(String(50), nullable=True)  # trialing, active, past_due, canceled, unpaid
    trial_end = Column(DateTime(timezone=True), nullable=True)
    subscription_current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)  # True if subscription is set to cancel at period end

    # Beta / invite
    beta_user = Column(Boolean, default=False, nullable=False)

    # Affiliate / referral
    referred_by_code = Column(String(20), nullable=True)  # snapshot of code used at signup

    # Fraud detection — IP and user agent at signup
    signup_ip = Column(String(45), nullable=True)  # IPv4 or IPv6
    signup_user_agent = Column(Text, nullable=True)  # Browser user agent string

    # Google OAuth
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    auth_provider = Column(String(20), nullable=False, default="email")  # email | google

    # Two-factor authentication (TOTP)
    totp_secret = Column(Text, nullable=True)   # Fernet-encrypted TOTP secret
    totp_enabled = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
