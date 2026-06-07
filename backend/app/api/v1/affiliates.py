"""
Affiliate program API routes (authenticated, affiliate-facing)
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet, InvalidToken

from app.db.session import get_db
from app.core.dependencies import get_verified_user
from app.core.config import settings
from app.models.user import User
from app.models.affiliate import Affiliate, CommissionLedger, PayoutBatch, AffiliateTaxProfile
from app.services import affiliate_service
from app.schemas.affiliate import (
    AffiliateOut,
    AffiliateDashboard,
    CommissionOut,
    PayoutBatchOut,
    PayoutBatchCreate,
    TaxProfileOut,
    TaxProfileUpsert,
    PayoutInfoUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def check_referral_access(current_user: User = Depends(get_verified_user)):
    """
    Check if current user can access referral routes.
    Referral routes are available when REFERRALS_ENABLED is True.
    """
    if not settings.REFERRALS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral system is not available."
        )
    
    # Admin bypass - always allow admin access.
    if current_user.is_admin:
        return current_user
    
    return current_user


def _get_fernet():
    from app.core.config import settings
    key = settings.TIN_ENCRYPTION_KEY
    if not key:
        raise HTTPException(status_code=503, detail="TIN encryption not configured.")
    return Fernet(key.encode() if isinstance(key, str) else key)


def _encrypt_tin(tin: str) -> str:
    """Encrypt full TIN and return base64 ciphertext."""
    f = _get_fernet()
    return f.encrypt(tin.encode()).decode()


def _decrypt_tin(ciphertext: str) -> str:
    """Decrypt stored TIN ciphertext; returns plaintext or '---------' on failure."""
    try:
        f = _get_fernet()
        return f.decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        return "---------"


def _mask_tin(tin: str) -> str:
    """Return masked TIN: 9-digit → ***-**-1234, other → ****1234."""
    digits = tin.replace("-", "").replace(" ", "")
    if len(digits) == 9:
        return f"***-**-{digits[-4:]}"
    return f"****{digits[-4:] if len(digits) >= 4 else digits}"


def _get_affiliate_or_404(db: Session, user: User) -> Affiliate:
    aff = db.query(Affiliate).filter(Affiliate.user_id == user.id).first()
    if not aff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in affiliate program. POST /affiliates/enroll first.",
        )
    return aff


# ---------------------------------------------------------------------------
# POST /affiliates/enroll
# Enroll the current user in the affiliate program and create Stripe Connect account
# Returns affiliate record with onboarding URL
# ---------------------------------------------------------------------------
@router.post("/enroll")
def enroll(
    current_user: User = Depends(check_referral_access),
    db: Session = Depends(get_db),
):
    from app.services import stripe_service
    
    aff = affiliate_service.create_affiliate(db, current_user)
    
    # Generate Stripe Connect onboarding link
    onboarding_url = None
    if aff.stripe_account_id and not aff.stripe_onboarding_completed:
        try:
            onboarding_url = stripe_service.create_onboarding_link(
                account_id=aff.stripe_account_id,
                refresh_url=f"{settings.FRONTEND_URL}/affiliates/onboarding",
                return_url=f"{settings.FRONTEND_URL}/affiliates/connect/return",
            )
        except Exception as e:
            logger.error(f"Failed to create onboarding link for affiliate {aff.id}: {e}")
    
    return {
        "id": aff.id,
        "code": aff.code,
        "status": aff.status,
        "commission_pct": float(aff.commission_pct),
        "stripe_onboarding_completed": aff.stripe_onboarding_completed,
        "payouts_enabled": aff.payouts_enabled,
        "onboarding_url": onboarding_url,
        "message": "Enrollment successful. Complete Stripe Connect onboarding to enable payouts."
    }


# ---------------------------------------------------------------------------
# GET /affiliates/onboarding-link
# Generate fresh Stripe Connect onboarding link (if not completed)
# ---------------------------------------------------------------------------
@router.get("/onboarding-link")
def get_onboarding_link(
    current_user: User = Depends(check_referral_access),
    db: Session = Depends(get_db),
):
    from app.services import stripe_service
    
    aff = _get_affiliate_or_404(db, current_user)
    
    if aff.stripe_onboarding_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe Connect onboarding already completed"
        )
    
    if not aff.stripe_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe Connect account found. Please re-enroll."
        )
    
    try:
        onboarding_url = stripe_service.create_onboarding_link(
            account_id=aff.stripe_account_id,
            refresh_url=f"{settings.FRONTEND_URL}/affiliates/onboarding",
            return_url=f"{settings.FRONTEND_URL}/affiliates/connect/return",
        )
        return {"onboarding_url": onboarding_url}
    except Exception as e:
        logger.error(f"Failed to create onboarding link for affiliate {aff.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate onboarding link"
        )


# ---------------------------------------------------------------------------
# GET /affiliates/connect/refresh
# Check Stripe Connect account status after onboarding return
# ---------------------------------------------------------------------------
@router.get("/connect/refresh")
def refresh_connect_status(
    current_user: User = Depends(check_referral_access),
    db: Session = Depends(get_db),
):
    from app.services import stripe_service
    
    aff = _get_affiliate_or_404(db, current_user)
    
    if not aff.stripe_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe Connect account found"
        )
    
    try:
        account_info = stripe_service.check_account_capabilities(aff.stripe_account_id)
        
        # Update database with latest status
        aff.payouts_enabled = account_info["payouts_enabled"]
        aff.stripe_charges_enabled = account_info["charges_enabled"]
        aff.stripe_onboarding_completed = account_info["details_submitted"]
        aff.stripe_account_status = account_info["account_status"]
        
        db.commit()
        
        return {
            "payouts_enabled": aff.payouts_enabled,
            "onboarding_completed": aff.stripe_onboarding_completed,
            "account_status": aff.stripe_account_status,
            "message": "Setup complete! You can now earn commissions." if aff.payouts_enabled 
                      else "Onboarding pending. Please complete all required steps."
        }
    except Exception as e:
        logger.error(f"Failed to refresh connect status for affiliate {aff.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check account status"
        )


# ---------------------------------------------------------------------------
# GET /affiliates/me
# Fetch logged-in user's affiliate record + dashboard summary
# ---------------------------------------------------------------------------
@router.get("/me", response_model=AffiliateDashboard)
def get_my_affiliate(
    current_user: User = Depends(check_referral_access),
    db: Session = Depends(get_db),
):
    from app.models.affiliate import ReferralAttribution
    
    aff = _get_affiliate_or_404(db, current_user)

    commissions = (
        db.query(CommissionLedger)
        .filter(CommissionLedger.affiliate_id == aff.id)
        .order_by(CommissionLedger.created_at.desc())
        .limit(100)
        .all()
    )

    pending_cents = sum(
        c.commission_amount_cents for c in commissions if c.status == "pending"
    )
    approved_cents = sum(
        c.commission_amount_cents for c in commissions if c.status == "approved"
    )
    paid_cents = sum(
        c.commission_amount_cents for c in commissions if c.status == "paid"
    )

    referral_link = f"{settings.FRONTEND_URL}/signup?ref={aff.code}"

    tax_profile = db.query(AffiliateTaxProfile).filter(AffiliateTaxProfile.affiliate_id == aff.id).first()
    w9_collected = bool(tax_profile and tax_profile.w9_collected)

    # Calculate detailed user metrics
    # Get all referral attributions for this affiliate
    attributions = (
        db.query(ReferralAttribution)
        .filter(ReferralAttribution.affiliate_id == aff.id)
        .all()
    )
    
    # Get all referred user IDs
    referred_user_ids = [attr.referred_user_id for attr in attributions]
    
    # Get all referred users with their subscription status
    referred_users = (
        db.query(User)
        .filter(User.id.in_(referred_user_ids))
        .all()
    ) if referred_user_ids else []
    
    # Count users in trial
    users_in_trial = sum(1 for u in referred_users if u.subscription_status == 'trialing')
    
    # Count users who paid (have any subscription status that's not None and not just trialing)
    all_time_paid_users = sum(
        1 for u in referred_users 
        if u.subscription_status in ['active', 'past_due', 'canceled', 'unpaid']
    )
    
    # Get unique user IDs with pending commissions (in hold period)
    users_with_pending = set(
        c.referred_user_id for c in commissions if c.status == "pending"
    )
    users_paid_in_hold = len(users_with_pending)
    
    # Get unique user IDs with approved commissions (this cycle)
    users_with_approved = set(
        c.referred_user_id for c in commissions if c.status == "approved"
    )
    users_approved_current_cycle = len(users_with_approved)

    return AffiliateDashboard(
        affiliate=AffiliateOut.model_validate(aff),
        referral_link=referral_link,
        commissions=[CommissionOut.model_validate(c) for c in commissions],
        pending_amount_cents=pending_cents,
        approved_amount_cents=approved_cents,
        paid_amount_cents=paid_cents,
        w9_collected=w9_collected,
        total_signups=aff.total_referred,
        users_in_trial=users_in_trial,
        users_paid_in_hold=users_paid_in_hold,
        users_approved_current_cycle=users_approved_current_cycle,
        all_time_paid_users=all_time_paid_users,
    )


# ---------------------------------------------------------------------------
# GET /affiliates/commissions
# Paginated commission history
# ---------------------------------------------------------------------------
@router.get("/commissions", response_model=list[CommissionOut])
def list_commissions(
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(check_referral_access),
    db: Session = Depends(get_db),
):
    aff = _get_affiliate_or_404(db, current_user)
    offset = (page - 1) * page_size
    entries = (
        db.query(CommissionLedger)
        .filter(CommissionLedger.affiliate_id == aff.id)
        .order_by(CommissionLedger.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return entries


# ---------------------------------------------------------------------------
# GET /affiliates/payouts
# List payout batches for current affiliate
# ---------------------------------------------------------------------------
@router.get("/payouts", response_model=list[PayoutBatchOut])
def list_payouts(
    current_user: User = Depends(check_referral_access),
    db: Session = Depends(get_db),
):
    aff = _get_affiliate_or_404(db, current_user)
    batches = (
        db.query(PayoutBatch)
        .filter(PayoutBatch.affiliate_id == aff.id)
        .order_by(PayoutBatch.created_at.desc())
        .all()
    )
    return batches


# ---------------------------------------------------------------------------
# GET /affiliates/tax-profile
# ---------------------------------------------------------------------------
@router.get("/tax-profile", response_model=TaxProfileOut)
def get_tax_profile(
    current_user: User = Depends(check_referral_access),
    db: Session = Depends(get_db),
):
    aff = _get_affiliate_or_404(db, current_user)
    profile = db.query(AffiliateTaxProfile).filter(AffiliateTaxProfile.affiliate_id == aff.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Tax profile not found.")
    # Decrypt and mask TIN before returning
    out = TaxProfileOut.model_validate(profile)
    if profile.tin_last4:
        full_tin = _decrypt_tin(profile.tin_last4)
        out.tin_last4 = _mask_tin(full_tin)
    return out


# ---------------------------------------------------------------------------
# PUT /affiliates/tax-profile
# Upsert tax/W-9 profile — stores only last 4 digits of TIN for security
# ---------------------------------------------------------------------------
@router.put("/tax-profile", response_model=TaxProfileOut)
def upsert_tax_profile(
    body: TaxProfileUpsert,
    current_user: User = Depends(check_referral_access),
    db: Session = Depends(get_db),
):
    aff = _get_affiliate_or_404(db, current_user)
    profile = db.query(AffiliateTaxProfile).filter(AffiliateTaxProfile.affiliate_id == aff.id).first()
    if not profile:
        profile = AffiliateTaxProfile(affiliate_id=aff.id)
        db.add(profile)

    if body.legal_name is not None:
        profile.legal_name = body.legal_name
    if body.business_name is not None:
        profile.business_name = body.business_name
    if body.tax_classification is not None:
        profile.tax_classification = body.tax_classification
    if body.tin is not None:
        # Encrypt the full TIN before storing
        tin_clean = body.tin.replace("-", "").replace(" ", "")
        if len(tin_clean) < 4:
            raise HTTPException(status_code=400, detail="Invalid TIN — must be at least 4 digits.")
        if len(tin_clean) != 9:
            logger.warning("TIN submitted with unexpected length %d for affiliate %d", len(tin_clean), aff.id)
        profile.tin_last4 = _encrypt_tin(tin_clean)
    if body.address_line1 is not None:
        profile.address_line1 = body.address_line1
    if body.address_line2 is not None:
        profile.address_line2 = body.address_line2
    if body.city is not None:
        profile.city = body.city
    if body.state is not None:
        profile.state = body.state
    if body.zip_code is not None:
        profile.zip_code = body.zip_code
    if body.country is not None:
        profile.country = body.country
    if body.signature_text is not None:
        profile.signature_text = body.signature_text.strip() if body.signature_text else None
    if body.perjury_acknowledged is not None:
        profile.perjury_acknowledged = body.perjury_acknowledged
    if body.certification_confirmed is not None:
        profile.certification_confirmed = body.certification_confirmed
    if body.w9_collected is not None:
        profile.w9_collected = body.w9_collected
        if body.w9_collected:
            from datetime import timezone
            profile.w9_collected_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(profile)
    # Return masked TIN
    out = TaxProfileOut.model_validate(profile)
    if profile.tin_last4:
        full_tin = _decrypt_tin(profile.tin_last4)
        out.tin_last4 = _mask_tin(full_tin)
    return out


# ---------------------------------------------------------------------------
# PUT /affiliates/payout-info
# Save payout destination (PayPal email, Venmo, etc.)
# ---------------------------------------------------------------------------
@router.put("/payout-info", response_model=AffiliateOut)
def update_payout_info(
    body: PayoutInfoUpdate,
    current_user: User = Depends(check_referral_access),
    db: Session = Depends(get_db),
):
    aff = _get_affiliate_or_404(db, current_user)
    if body.payout_email is not None:
        aff.payout_email = body.payout_email.strip() or None
    db.commit()
    db.refresh(aff)
    return aff
