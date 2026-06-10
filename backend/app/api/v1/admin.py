"""
Admin-only API routes for managing the affiliate program.
All endpoints require is_admin=True via get_admin_user dependency.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet, InvalidToken

from app.db.session import get_db
from app.core.config import settings
from app.core.dependencies import get_admin_user
from app.models.user import User
from app.models.affiliate import Affiliate, CommissionLedger, PayoutBatch, ReferralAttribution, AffiliateTaxProfile
from app.models.waitlist import WaitlistUser
from app.models.invite import Invite
from app.services import invite_service
from app.services import affiliate_service
from app.services import stripe_service
from app.schemas.affiliate import (
    AffiliateOut,
    AffiliateUpdate,
    AdminAffiliateRow,
    AdminCommissionReviewRow,
    CommissionOut,
    PayoutBatchOut,
    PayoutBatchCreate,
    MarkBatchPaid,
    PaySelectedCommissions,
)
from sqlalchemy import func

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# GET /admin/affiliates
# List all affiliates with user email for admin overview
# ---------------------------------------------------------------------------
@router.get("/affiliates", response_model=list[AdminAffiliateRow])
def list_affiliates(
    page: int = 1,
    page_size: int = 100,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    rows = (
        db.query(Affiliate, User.email)
        .join(User, User.id == Affiliate.user_id)
        .order_by(Affiliate.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    # Get approved amounts per affiliate in one query
    approved = (
        db.query(CommissionLedger.affiliate_id, func.sum(CommissionLedger.commission_amount_cents))
        .filter(CommissionLedger.status == "approved")
        .group_by(CommissionLedger.affiliate_id)
        .all()
    )
    approved_map = {aff_id: total for aff_id, total in approved}
    # Get w9_collected per affiliate in one query
    w9_rows = (
        db.query(AffiliateTaxProfile.affiliate_id, AffiliateTaxProfile.w9_collected)
        .all()
    )
    w9_map = {aff_id: collected for aff_id, collected in w9_rows}
    result = []
    for aff, email in rows:
        result.append(
            AdminAffiliateRow(
                id=aff.id,
                user_id=aff.user_id,
                email=email,
                code=aff.code,
                status=aff.status,
                commission_pct=aff.commission_pct,
                total_referred=aff.total_referred,
                total_earned_cents=aff.total_earned_cents,
                total_paid_cents=aff.total_paid_cents,
                payout_email=aff.payout_email,
                approved_amount_cents=approved_map.get(aff.id, 0),
                w9_collected=w9_map.get(aff.id, False),
                created_at=aff.created_at,
            )
        )
    return result


# ---------------------------------------------------------------------------
# PATCH /admin/affiliates/{affiliate_id}
# Update commission rate, status, hold days, etc.
# ---------------------------------------------------------------------------
@router.patch("/affiliates/{affiliate_id}", response_model=AffiliateOut)
def update_affiliate(
    affiliate_id: int,
    body: AffiliateUpdate,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    aff = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not aff:
        raise HTTPException(status_code=404, detail="Affiliate not found.")

    if body.status is not None:
        aff.status = body.status
    if body.commission_pct is not None:
        aff.commission_pct = body.commission_pct
    if body.max_months is not None:
        aff.max_months = body.max_months
    if body.hold_days is not None:
        aff.hold_days = body.hold_days

    db.commit()
    db.refresh(aff)
    return aff


# ---------------------------------------------------------------------------
# POST /admin/affiliates/{affiliate_id}/manual-payout
# Trigger manual payout for an affiliate (bypasses minimum balance)
# ---------------------------------------------------------------------------
@router.post("/affiliates/{affiliate_id}/manual-payout")
def manual_payout(
    affiliate_id: int,
    force_minimum: bool = Body(False, description="Bypass minimum balance check"),
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    from app.services import payout_service
    
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    
    try:
        batch = payout_service.create_payout_for_affiliate(
            db, 
            affiliate_id, 
            force=force_minimum
        )
        
        if not batch:
            raise HTTPException(
                status_code=400, 
                detail="No eligible commissions or affiliate not ready for payout"
            )
        
        return {
            "batch_id": batch.id,
            "amount_cents": batch.total_amount_cents,
            "commission_count": batch.commission_count,
            "stripe_transfer_id": batch.stripe_transfer_id,
            "message": f"Successfully paid ${batch.total_amount_cents/100:.2f} to affiliate"
        }
    except Exception as e:
        logger.error(f"Manual payout failed for affiliate {affiliate_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Payout failed: {str(e)}")


# ---------------------------------------------------------------------------
# POST /admin/affiliates/{affiliate_id}/block-payouts
# Manually disable payouts for fraud investigation
# ---------------------------------------------------------------------------
@router.post("/affiliates/{affiliate_id}/block-payouts")
def block_payouts(
    affiliate_id: int,
    reason: str = Body(..., description="Reason for blocking payouts"),
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    
    affiliate.payouts_enabled = False
    affiliate.stripe_account_status = "restricted"
    
    # Log the action
    logger.warning(
        f"Admin blocked payouts for affiliate {affiliate_id}: {reason}"
    )
    
    db.commit()
    db.refresh(affiliate)
    
    return {
        "affiliate_id": affiliate.id,
        "payouts_enabled": affiliate.payouts_enabled,
        "status": affiliate.stripe_account_status,
        "message": f"Payouts blocked: {reason}"
    }


# ---------------------------------------------------------------------------
# POST /admin/affiliates/{affiliate_id}/unblock-payouts
# Re-enable payouts after fraud investigation resolved
# ---------------------------------------------------------------------------
@router.post("/affiliates/{affiliate_id}/unblock-payouts")
def unblock_payouts(
    affiliate_id: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    from app.services import stripe_service
    
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    
    if not affiliate.stripe_account_id:
        raise HTTPException(status_code=400, detail="No Stripe Connect account found")
    
    # Check actual Stripe status
    try:
        account_info = stripe_service.check_account_capabilities(affiliate.stripe_account_id)
        affiliate.payouts_enabled = account_info["payouts_enabled"]
        affiliate.stripe_account_status = account_info["account_status"]
    except Exception as e:
        logger.error(f"Failed to check Stripe account status: {e}")
        raise HTTPException(status_code=500, detail="Could not verify Stripe account status")
    
    logger.info(f"Admin unblocked payouts for affiliate {affiliate_id}")
    
    db.commit()
    db.refresh(affiliate)
    
    return {
        "affiliate_id": affiliate.id,
        "payouts_enabled": affiliate.payouts_enabled,
        "status": affiliate.stripe_account_status,
        "message": "Payouts status refreshed from Stripe"
    }


# ---------------------------------------------------------------------------
# GET /admin/fraud-signals
# View all fraud signals (with optional filtering)
# ---------------------------------------------------------------------------
@router.get("/fraud-signals")
def list_fraud_signals(
    affiliate_id: Optional[int] = None,
    signal_type: Optional[str] = None,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    from app.models.affiliate import FraudSignal
    
    query = db.query(FraudSignal)
    
    if affiliate_id is not None:
        query = query.filter(FraudSignal.affiliate_id == affiliate_id)
    if signal_type:
        query = query.filter(FraudSignal.signal_type == signal_type)
    if severity:
        query = query.filter(FraudSignal.severity == severity)
    if resolved is not None:
        query = query.filter(FraudSignal.resolved == resolved)
    
    signals = query.order_by(FraudSignal.created_at.desc()).limit(limit).all()
    
    result = []
    for sig in signals:
        # Get affiliate and user info
        affiliate = db.query(Affiliate).filter(Affiliate.id == sig.affiliate_id).first()
        user = None
        if sig.referred_user_id:
            user = db.query(User).filter(User.id == sig.referred_user_id).first()
        
        result.append({
            "id": sig.id,
            "affiliate_id": sig.affiliate_id,
            "affiliate_code": affiliate.code if affiliate else None,
            "referred_user_id": sig.referred_user_id,
            "referred_user_email": user.email if user else None,
            "signal_type": sig.signal_type,
            "severity": sig.severity,
            "metadata": sig.signal_metadata,
            "resolved": sig.resolved,
            "resolved_at": sig.resolved_at,
            "resolution_notes": sig.resolution_notes,
            "created_at": sig.created_at,
        })
    
    return result


# ---------------------------------------------------------------------------
# POST /admin/fraud-signals/{signal_id}/resolve
# Mark a fraud signal as resolved (false positive)
# ---------------------------------------------------------------------------
@router.post("/fraud-signals/{signal_id}/resolve")
def resolve_fraud_signal(
    signal_id: int,
    notes: str = Body(..., description="Resolution notes"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    from app.models.affiliate import FraudSignal
    
    signal = db.query(FraudSignal).filter(FraudSignal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Fraud signal not found")
    
    signal.resolved = True
    signal.resolved_at = datetime.now(timezone.utc)
    signal.resolved_by_user_id = current_user.id
    signal.resolution_notes = notes
    
    db.commit()
    
    logger.info(f"Admin {current_user.email} resolved fraud signal {signal_id}")
    
    return {
        "signal_id": signal.id,
        "resolved": True,
        "resolved_by": current_user.email,
        "notes": notes
    }


# ---------------------------------------------------------------------------
# GET /admin/commissions
# List all commissions across all affiliates (paginated)
# ---------------------------------------------------------------------------
@router.get("/commissions", response_model=list[CommissionOut])
def list_all_commissions(
    page: int = 1,
    page_size: int = 100,
    affiliate_id: int = None,
    commission_status: str = None,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    q = db.query(CommissionLedger)
    if affiliate_id:
        q = q.filter(CommissionLedger.affiliate_id == affiliate_id)
    if commission_status:
        q = q.filter(CommissionLedger.status == commission_status)
    return q.order_by(CommissionLedger.created_at.desc()).offset(offset).limit(page_size).all()


# ---------------------------------------------------------------------------
# POST /admin/commissions/approve-due
# Manually trigger the hold-period approval batch (normally runs daily)
# ---------------------------------------------------------------------------
@router.post("/commissions/approve-due")
def approve_due(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    count = affiliate_service.approve_due_commissions(db)
    return {"approved": count}


# ---------------------------------------------------------------------------
# POST /admin/commissions/{commission_id}/void
# Void a single commission (refund / chargeback)
# ---------------------------------------------------------------------------
@router.post("/commissions/{commission_id}/void")
def void_commission_by_id(
    commission_id: int,
    reason: str = Body(..., embed=True),
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    entry = db.query(CommissionLedger).filter(CommissionLedger.id == commission_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Commission not found.")
    updated = affiliate_service.void_commission(db, entry.stripe_invoice_id, reason)
    return CommissionOut.model_validate(updated)


# ---------------------------------------------------------------------------
# GET /admin/commissions/review
# Detailed commission review with affiliate & user info, filtering for payment approval
# ---------------------------------------------------------------------------
@router.get("/commissions/review", response_model=list[AdminCommissionReviewRow])
def review_commissions(
    page: int = 1,
    page_size: int = 100,
    status: Optional[str] = None,  # pending, approved, paid, voided
    affiliate_id: Optional[int] = None,
    search: Optional[str] = None,  # Search by email or name
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed commission data for admin review with filtering.
    Includes affiliate info, referred user info, and payment status.
    """
    from sqlalchemy.orm import aliased
    
    offset = (page - 1) * page_size
    
    # Create aliases for the two user joins
    AffiliateUser = aliased(User)
    ReferredUser = aliased(User)
    
    # Join commissions with affiliates and users
    query = (
        db.query(CommissionLedger, Affiliate, AffiliateUser, ReferredUser)
        .join(Affiliate, Affiliate.id == CommissionLedger.affiliate_id)
        .join(AffiliateUser, AffiliateUser.id == Affiliate.user_id)
        .join(ReferredUser, ReferredUser.id == CommissionLedger.referred_user_id)
    )
    
    # Apply filters
    if status:
        query = query.filter(CommissionLedger.status == status)
    if affiliate_id:
        query = query.filter(CommissionLedger.affiliate_id == affiliate_id)
    if search:
        search_pattern = f"%{search}%"
        from sqlalchemy import or_
        query = query.filter(
            or_(
                AffiliateUser.email.ilike(search_pattern),
                AffiliateUser.full_name.ilike(search_pattern),
                ReferredUser.email.ilike(search_pattern),
                ReferredUser.full_name.ilike(search_pattern),
            )
        )
    
    # Order by created date desc
    query = query.order_by(CommissionLedger.created_at.desc())
    
    # Paginate
    results = query.offset(offset).limit(page_size).all()
    
    # Build response rows
    rows = []
    for commission, affiliate, affiliate_user, referred_user in results:
        rows.append(
            AdminCommissionReviewRow(
                # Commission fields
                commission_id=commission.id,
                status=commission.status,
                commission_amount_cents=commission.commission_amount_cents,
                invoice_amount_cents=commission.invoice_amount_cents,
                commission_pct=commission.commission_pct,
                billing_cycle_number=commission.billing_cycle_number,
                stripe_invoice_id=commission.stripe_invoice_id,
                stripe_subscription_id=commission.stripe_subscription_id,
                hold_until=commission.hold_until,
                created_at=commission.created_at,
                approved_at=commission.approved_at,
                voided_at=commission.voided_at,
                notes=commission.notes,
                
                # Affiliate info
                affiliate_id=affiliate.id,
                affiliate_email=affiliate_user.email,
                affiliate_name=affiliate_user.full_name,
                affiliate_code=affiliate.code,
                affiliate_payout_email=affiliate.payout_email,
                
                # Referred user info
                referred_user_id=referred_user.id,
                referred_user_email=referred_user.email,
                referred_user_name=referred_user.full_name,
                referred_user_subscription_status=referred_user.subscription_status,
            )
        )
    
    return rows


# ---------------------------------------------------------------------------
# POST /admin/payouts
# Create a payout batch for an affiliate
# ---------------------------------------------------------------------------
@router.post("/payouts", response_model=PayoutBatchOut)
def create_payout(
    affiliate_id: int,
    body: PayoutBatchCreate,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    aff = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not aff:
        raise HTTPException(status_code=404, detail="Affiliate not found.")
    batch = affiliate_service.create_payout_batch(
        db, affiliate_id, body.period_start, body.period_end
    )
    return batch


# ---------------------------------------------------------------------------
# GET /admin/payouts
# List all payout batches
# ---------------------------------------------------------------------------
@router.get("/payouts", response_model=list[PayoutBatchOut])
def list_payouts(
    page: int = 1,
    page_size: int = 100,
    affiliate_id: int = None,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    q = db.query(PayoutBatch)
    if affiliate_id:
        q = q.filter(PayoutBatch.affiliate_id == affiliate_id)
    return q.order_by(PayoutBatch.created_at.desc()).offset(offset).limit(page_size).all()


# ---------------------------------------------------------------------------
# POST /admin/payouts/{batch_id}/mark-paid
# Mark a payout batch as manually paid
# ---------------------------------------------------------------------------
@router.post("/payouts/{batch_id}/mark-paid", response_model=PayoutBatchOut)
def mark_paid(
    batch_id: int,
    body: MarkBatchPaid,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
        batch = affiliate_service.mark_batch_paid(db, batch_id, body.payout_reference)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return batch


# ---------------------------------------------------------------------------
# POST /admin/payouts/pay-selected
# Create and immediately pay a batch with selected commissions (one-step)
# ---------------------------------------------------------------------------
@router.post("/payouts/pay-selected", response_model=PayoutBatchOut)
def pay_selected_commissions(
    body: PaySelectedCommissions,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    try:
        batch = affiliate_service.create_and_pay_batch(
            db=db,
            affiliate_id=body.affiliate_id,
            commission_ids=body.commission_ids,
            payout_reference=body.payout_reference,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return batch


# ---------------------------------------------------------------------------
# GET /admin/affiliates/{affiliate_id}/tin
# Decrypt and return full TIN for 1099 generation — admin only
# ---------------------------------------------------------------------------
def _admin_decrypt_tin(ciphertext: str) -> str:
    key = settings.TIN_ENCRYPTION_KEY
    if not key:
        raise HTTPException(status_code=503, detail="TIN encryption not configured.")
    try:
        f = Fernet(key.encode() if isinstance(key, str) else key)
        return f.decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception) as exc:
        raise HTTPException(status_code=500, detail="Failed to decrypt TIN.") from exc


@router.get("/affiliates/{affiliate_id}/tin")
def get_affiliate_tin(
    affiliate_id: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Return decrypted TIN for 1099 generation. ADMIN ONLY — never expose to affiliates."""
    aff = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not aff:
        raise HTTPException(status_code=404, detail="Affiliate not found.")
    profile = db.query(AffiliateTaxProfile).filter(AffiliateTaxProfile.affiliate_id == affiliate_id).first()
    if not profile or not profile.tin_last4:
        raise HTTPException(status_code=404, detail="No TIN on file for this affiliate.")
    full_tin = _admin_decrypt_tin(profile.tin_last4)
    # Format for 1099: SSN → XXX-XX-XXXX, EIN → XX-XXXXXXX
    digits = full_tin.replace("-", "").replace(" ", "")
    if len(digits) == 9:
        formatted = f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
    else:
        formatted = full_tin
    return {
        "affiliate_id": affiliate_id,
        "legal_name": profile.legal_name,
        "tin": formatted,
        "tax_classification": profile.tax_classification,
    }


# ============================================================================
# BETA / INVITE / WAITLIST MANAGEMENT
# ============================================================================

# ---------------------------------------------------------------------------
# GET /admin/waitlist
# List all waitlist signups
# ---------------------------------------------------------------------------
@router.get("/waitlist")
def list_waitlist(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    rows = db.query(WaitlistUser).order_by(WaitlistUser.created_at.desc()).all()
    return [
        {"id": r.id, "email": r.email, "name": r.name, "created_at": r.created_at}
        for r in rows
    ]


# ---------------------------------------------------------------------------
# DELETE /admin/waitlist/{waitlist_id}
# Remove someone from the waitlist
# ---------------------------------------------------------------------------
@router.delete("/waitlist/{waitlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_waitlist_entry(
    waitlist_id: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    row = db.query(WaitlistUser).filter(WaitlistUser.id == waitlist_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found.")
    db.delete(row)
    db.commit()


# ---------------------------------------------------------------------------
# GET /admin/invites
# List all invites
# ---------------------------------------------------------------------------
@router.get("/invites")
def list_invites(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    rows = db.query(Invite).order_by(Invite.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "email": r.email,
            "invite_code": r.invite_code,
            "used": r.used,
            "created_at": r.created_at,
            "expires_at": r.expires_at,
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# POST /admin/invites
# Create one or more invites
# ---------------------------------------------------------------------------
class CreateInviteRequest(BaseModel):
    email: Optional[str] = None
    count: int = 1
    expires_days: Optional[int] = None


@router.post("/invites", status_code=status.HTTP_201_CREATED)
def create_invites(
    body: CreateInviteRequest,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    expires_at = None
    if body.expires_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_days)

    created = []
    for _ in range(max(1, body.count)):
        invite = invite_service.create_invite(db, email=body.email, expires_at=expires_at)
        link = f"{settings.FRONTEND_URL}/signup?invite={invite.invite_code}"
        created.append({
            "id": invite.id,
            "email": invite.email,
            "invite_code": invite.invite_code,
            "link": link,
            "expires_at": invite.expires_at,
        })
    return created


# ---------------------------------------------------------------------------
# POST /admin/invites/send
# Send an invite code via email
# ---------------------------------------------------------------------------
class SendInviteRequest(BaseModel):
    email: str
    invite_code: str


@router.post("/invites/send", status_code=status.HTTP_200_OK)
def send_invite_email_endpoint(
    body: SendInviteRequest,
    _: User = Depends(get_admin_user),
):
    """Send an invite code to a user via email."""
    from app.core.email import send_invite_email
    
    success = send_invite_email(body.email, body.invite_code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send invite email"
        )
    
    return {"message": "Invite email sent successfully"}


# ---------------------------------------------------------------------------
# DELETE /admin/invites/{invite_id}
# Revoke (hard-delete) an unused invite
# ---------------------------------------------------------------------------
@router.delete("/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_invite(
    invite_id: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    invite = db.query(Invite).filter(Invite.id == invite_id).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found.")
    if invite.used:
        raise HTTPException(status_code=400, detail="Cannot revoke an already-used invite.")
    db.delete(invite)
    db.commit()


# ---------------------------------------------------------------------------
# GET /admin/beta-users
# List all users with beta_user=True
# ---------------------------------------------------------------------------
@router.get("/beta-users")
def list_beta_users(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    rows = db.query(User).filter(User.beta_user == True).order_by(User.created_at.desc()).all()  # noqa: E712
    return [
        {"id": r.id, "email": r.email, "full_name": r.full_name, "created_at": r.created_at}
        for r in rows
    ]


# ---------------------------------------------------------------------------
# POST /admin/beta-users/{user_id}/revoke
# Remove beta access from a user
# ---------------------------------------------------------------------------
@router.post("/beta-users/{user_id}/revoke", status_code=status.HTTP_204_NO_CONTENT)
def revoke_beta_access(
    user_id: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.beta_user = False
    db.commit()


# ---------------------------------------------------------------------------
# DELETE /admin/users/{user_id}
# Delete a user account completely with automatic subscription cancellation
# and prorated refund. This is the proper way to handle account deletion.
# ---------------------------------------------------------------------------
class UserDeletionResponse(BaseModel):
    user_id: int
    email: str
    deleted: bool
    subscription_canceled: bool
    refund_issued: bool
    message: str


@router.delete("/users/{user_id}", response_model=UserDeletionResponse)
def delete_user_account(
    user_id: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Completely delete a user account from the database.
    
    This will:
    1. Cancel their Stripe subscription (if any) with prorated refund
    2. Delete all user data from the database
    3. Return confirmation with refund details
    
    Use this for:
    - User requests account deletion (GDPR compliance)
    - Admin removes fraudulent/abusive accounts
    
    Note: Subscription cancellation issues a prorated refund for unused time.
    """
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    email = user.email
    subscription_canceled = False
    refund_issued = False
    
    # Cancel Stripe subscription with refund if they have one
    if user.stripe_subscription_id:
        logger.info(f"Canceling subscription {user.stripe_subscription_id} for user {email}")
        result = stripe_service.cancel_subscription_with_refund(user.stripe_subscription_id)
        
        subscription_canceled = result.get("canceled", False)
        refund_issued = result.get("refund_issued", False)
        
        if not subscription_canceled:
            logger.warning(f"Failed to cancel subscription: {result.get('error', 'Unknown error')}")
    
    # Delete the user from database
    # Note: This will cascade delete related records if foreign keys are set up properly
    db.delete(user)
    db.commit()
    
    logger.info(f"Deleted user {user_id} ({email})")
    
    return UserDeletionResponse(
        user_id=user_id,
        email=email,
        deleted=True,
        subscription_canceled=subscription_canceled,
        refund_issued=refund_issued,
        message=f"User account deleted successfully. {'Subscription canceled with prorated refund.' if refund_issued else 'No active subscription found.'}"
    )
