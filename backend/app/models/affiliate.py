"""
Affiliate / referral system models
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Numeric,
    ForeignKey, Text, UniqueConstraint, BigInteger
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.session import Base


class Affiliate(Base):
    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="active")  # active, paused, banned

    commission_pct = Column(Numeric(5, 2), nullable=False, default=30.00)
    max_months = Column(Integer, nullable=True)   # None = unlimited recurring
    hold_days = Column(Integer, nullable=False, default=30)

    total_referred = Column(Integer, nullable=False, default=0)
    total_earned_cents = Column(Integer, nullable=False, default=0)
    total_paid_cents = Column(Integer, nullable=False, default=0)

    # Stripe Connect integration
    stripe_account_id = Column(String(255), nullable=True, unique=True, index=True)
    stripe_onboarding_completed = Column(Boolean, nullable=False, default=False)
    payouts_enabled = Column(Boolean, nullable=False, default=False)
    stripe_account_status = Column(String(50), nullable=True)  # active, restricted, rejected, pending
    stripe_charges_enabled = Column(Boolean, nullable=False, default=False)

    # Legacy payout destination — deprecated in favor of Stripe Connect
    payout_email = Column(String(255), nullable=True)   # PayPal / Venmo / bank email

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ReferralAttribution(Base):
    __tablename__ = "referral_attributions"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id", ondelete="CASCADE"), nullable=False, index=True)
    referred_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    referral_code = Column(String(20), nullable=False)   # snapshot at time of signup
    status = Column(String(20), nullable=False, default="pending")  # pending, converted, churned
    attributed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    first_payment_at = Column(DateTime(timezone=True), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # Fraud detection — store affiliate's IP at signup for cross-checking
    affiliate_signup_ip = Column(String(45), nullable=True)  # IPv4 or IPv6


class PayoutBatch(Base):
    __tablename__ = "payout_batches"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id", ondelete="CASCADE"), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    total_amount_cents = Column(Integer, nullable=False, default=0)
    commission_count = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="draft")  # draft, processing, paid, failed
    payout_method = Column(String(50), nullable=False, default="manual")  # manual, stripe_connect
    payout_reference = Column(String(255), nullable=True)  # check #, transfer ID, etc.
    stripe_transfer_id = Column(String(255), nullable=True, index=True)  # Stripe Transfer object ID
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)


class CommissionLedger(Base):
    __tablename__ = "commission_ledger"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id", ondelete="CASCADE"), nullable=False, index=True)
    attribution_id = Column(Integer, ForeignKey("referral_attributions.id", ondelete="CASCADE"), nullable=False, index=True)
    referred_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Idempotency — one row per Stripe invoice
    stripe_invoice_id = Column(String(255), nullable=False, unique=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True)

    invoice_amount_cents = Column(Integer, nullable=False)
    commission_pct = Column(Numeric(5, 2), nullable=False)   # snapshot at time of creation
    commission_amount_cents = Column(Integer, nullable=False)

    status = Column(String(20), nullable=False, default="pending")  # pending, approved, paid, voided, reversed
    hold_until = Column(DateTime(timezone=True), nullable=True)
    billing_cycle_number = Column(Integer, nullable=False, default=1)
    fraud_flagged = Column(Boolean, nullable=False, default=False)  # True if fraud signals detected

    payout_batch_id = Column(Integer, ForeignKey("payout_batches.id", ondelete="SET NULL"), nullable=True, index=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    voided_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("stripe_invoice_id", name="uq_commission_stripe_invoice"),
    )


class AffiliateTaxProfile(Base):
    __tablename__ = "affiliate_tax_profiles"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    legal_name = Column(String(255), nullable=True)
    business_name = Column(String(255), nullable=True)
    tax_classification = Column(String(50), nullable=True)  # individual, llc, s_corp, c_corp, partnership

    # Security: store only the last 4 digits, encrypted at rest
    tin_last4 = Column(Text, nullable=True)  # Fernet-encrypted ciphertext
    w9_collected = Column(Boolean, nullable=False, default=False)
    w9_collected_at = Column(DateTime(timezone=True), nullable=True)

    # Electronic signature and IRS certifications
    signature_text = Column(String(255), nullable=True)  # Typed signature (full name)
    perjury_acknowledged = Column(Boolean, nullable=False, default=False)  # User acknowledged penalty of perjury
    certification_confirmed = Column(Boolean, nullable=False, default=False)  # User confirmed information is correct

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(10), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(10), nullable=False, default="US")

    # Year-to-date paid totals for 1099 generation: {"2025": 150000, "2026": 50000}
    ytd_paid_cents = Column(JSONB, nullable=False, server_default="{}")

    # Deprecation marker — Stripe Connect now handles tax compliance
    deprecated_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class FraudSignal(Base):
    __tablename__ = "fraud_signals"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id", ondelete="CASCADE"), nullable=False, index=True)
    referred_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    signal_type = Column(String(50), nullable=False, index=True)  # ip_match, rapid_conversion, velocity_breach, churn_pattern
    severity = Column(String(20), nullable=False, default="medium")  # low, medium, high

    # Additional context stored as JSON
    signal_metadata = Column(JSONB, nullable=False, server_default="{}")
    # Example: {"affiliate_ip": "1.2.3.4", "user_ip": "1.2.3.4", "match_confidence": 1.0}
    # Example: {"conversions_24h": 7, "threshold": 5}

    resolved = Column(Boolean, nullable=False, default=False)  # Admin can mark as false positive
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
