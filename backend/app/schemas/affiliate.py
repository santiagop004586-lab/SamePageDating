from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ---------------------------------------------------------------------------
# Affiliate
# ---------------------------------------------------------------------------
class AffiliateOut(BaseModel):
    id: int
    user_id: int
    code: str
    status: str
    commission_pct: Decimal
    max_months: Optional[int]
    hold_days: int
    total_referred: int
    total_earned_cents: int
    total_paid_cents: int
    payout_email: Optional[str]
    created_at: datetime
    
    # Stripe Connect fields
    stripe_account_id: Optional[str] = None
    stripe_onboarding_completed: bool = False
    payouts_enabled: bool = False
    stripe_account_status: Optional[str] = None
    stripe_charges_enabled: bool = False

    model_config = {"from_attributes": True}


class PayoutInfoUpdate(BaseModel):
    payout_email: Optional[str] = None


class AffiliateCreate(BaseModel):
    pass  # enrollment requires no extra input — code generated server-side


class AffiliateUpdate(BaseModel):
    status: Optional[str] = None
    commission_pct: Optional[Decimal] = None
    max_months: Optional[int] = None
    hold_days: Optional[int] = None


# ---------------------------------------------------------------------------
# ReferralAttribution
# ---------------------------------------------------------------------------
class AttributionOut(BaseModel):
    id: int
    affiliate_id: int
    referred_user_id: int
    referral_code: str
    status: str
    attributed_at: datetime
    first_payment_at: Optional[datetime]
    stripe_subscription_id: Optional[str]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# CommissionLedger
# ---------------------------------------------------------------------------
class CommissionOut(BaseModel):
    id: int
    affiliate_id: int
    attribution_id: int
    referred_user_id: int
    stripe_invoice_id: str
    invoice_amount_cents: int
    commission_pct: Decimal
    commission_amount_cents: int
    status: str
    hold_until: Optional[datetime]
    billing_cycle_number: int
    payout_batch_id: Optional[int]
    notes: Optional[str]
    created_at: datetime
    approved_at: Optional[datetime]
    paid_at: Optional[datetime]
    voided_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# PayoutBatch
# ---------------------------------------------------------------------------
class PayoutBatchOut(BaseModel):
    id: int
    affiliate_id: int
    period_start: datetime
    period_end: datetime
    total_amount_cents: int
    commission_count: int
    status: str
    payout_method: str
    payout_reference: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PayoutBatchCreate(BaseModel):
    period_start: datetime
    period_end: datetime


class MarkBatchPaid(BaseModel):
    payout_reference: str


class PaySelectedCommissions(BaseModel):
    """Request to create and pay a batch with selected commissions."""
    affiliate_id: int
    commission_ids: list[int]
    payout_reference: str


# ---------------------------------------------------------------------------
# AffiliateTaxProfile
# ---------------------------------------------------------------------------
class TaxProfileOut(BaseModel):
    id: int
    affiliate_id: int
    legal_name: Optional[str]
    business_name: Optional[str]
    tax_classification: Optional[str]
    tin_last4: Optional[str]
    w9_collected: bool
    w9_collected_at: Optional[datetime]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: str
    ytd_paid_cents: dict
    signature_text: Optional[str]
    perjury_acknowledged: bool
    certification_confirmed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TaxProfileUpsert(BaseModel):
    legal_name: Optional[str] = None
    business_name: Optional[str] = None
    tax_classification: Optional[str] = None
    # Accept full TIN from user; full TIN is encrypted before storing
    tin: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    w9_collected: Optional[bool] = None
    signature_text: Optional[str] = None
    perjury_acknowledged: Optional[bool] = None
    certification_confirmed: Optional[bool] = None


# ---------------------------------------------------------------------------
# Dashboard summary (public-facing affiliate portal)
# ---------------------------------------------------------------------------
class AffiliateDashboard(BaseModel):
    affiliate: AffiliateOut
    referral_link: str
    commissions: List[CommissionOut]
    pending_amount_cents: int
    approved_amount_cents: int
    paid_amount_cents: int
    w9_collected: bool = False
    
    # Detailed user metrics
    total_signups: int  # Total users who signed up with referral link
    users_in_trial: int  # Users currently in free trial
    users_paid_in_hold: int  # Users who paid but commissions still in hold period
    users_approved_current_cycle: int  # Users with approved commissions this cycle
    all_time_paid_users: int  # Total users who have ever paid


# ---------------------------------------------------------------------------
# Admin list entries
# ---------------------------------------------------------------------------
class AdminAffiliateRow(BaseModel):
    id: int
    user_id: int
    email: str
    code: str
    status: str
    commission_pct: Decimal
    total_referred: int
    total_earned_cents: int
    total_paid_cents: int
    payout_email: Optional[str]
    approved_amount_cents: int = 0
    w9_collected: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminCommissionReviewRow(BaseModel):
    """Detailed commission row for admin review with affiliate & user info"""
    # Commission fields
    commission_id: int
    status: str
    commission_amount_cents: int
    invoice_amount_cents: int
    commission_pct: Decimal
    billing_cycle_number: int
    stripe_invoice_id: str
    stripe_subscription_id: Optional[str]
    hold_until: Optional[datetime]
    created_at: datetime
    approved_at: Optional[datetime]
    voided_at: Optional[datetime]
    notes: Optional[str]
    
    # Affiliate info
    affiliate_id: int
    affiliate_email: str
    affiliate_name: Optional[str]
    affiliate_code: str
    affiliate_payout_email: Optional[str]
    
    # Referred user info  
    referred_user_id: int
    referred_user_email: str
    referred_user_name: Optional[str]
    referred_user_subscription_status: Optional[str]

    model_config = {"from_attributes": True}
