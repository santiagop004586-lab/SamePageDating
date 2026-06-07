"""
Affiliate system service layer.

All functions are idempotent and safe to call from webhook handlers.
"""
import logging
import random
import string
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.models.affiliate import (
    Affiliate,
    ReferralAttribution,
    CommissionLedger,
    PayoutBatch,
    AffiliateTaxProfile,
)
from app.models.user import User

logger = logging.getLogger(__name__)

_CODE_CHARS = string.ascii_uppercase + string.digits


def generate_referral_code(db: Session, length: int = 8) -> str:
    """Generate a unique 8-character alphanumeric referral code."""
    for _ in range(20):
        code = "".join(random.choices(_CODE_CHARS, k=length))
        if not db.query(Affiliate).filter(Affiliate.code == code).first():
            return code
    raise RuntimeError("Could not generate a unique referral code after 20 attempts.")


def create_affiliate(db: Session, user: User) -> Affiliate:
    """
    Enroll a user in the affiliate program.
    Creates a Stripe Connect Express account for automated payouts.
    Idempotent — returns existing record if already enrolled.
    """
    from app.services import stripe_service
    
    existing = db.query(Affiliate).filter(Affiliate.user_id == user.id).first()
    if existing:
        return existing

    code = generate_referral_code(db)
    commission_pct = settings.AFFILIATE_COMMISSION_PCT
    max_months = settings.AFFILIATE_MAX_MONTHS
    hold_days = settings.AFFILIATE_HOLD_DAYS

    # Create Stripe Connect Express account
    stripe_account = None
    try:
        stripe_account = stripe_service.create_express_account(
            email=user.email,
            country="US"
        )
        logger.info(f"Created Stripe Connect account {stripe_account['account_id']} for user {user.id}")
    except Exception as e:
        logger.error(f"Failed to create Stripe Connect account for user {user.id}: {e}")
        # Continue anyway - can retry onboarding later

    affiliate = Affiliate(
        user_id=user.id,
        code=code,
        status="active",
        commission_pct=commission_pct,
        max_months=max_months,
        hold_days=hold_days,
        stripe_account_id=stripe_account['account_id'] if stripe_account else None,
        stripe_onboarding_completed=False,
        payouts_enabled=False,
    )
    db.add(affiliate)
    db.commit()
    db.refresh(affiliate)
    logger.info(f"New affiliate created: user_id={user.id} code={code}")
    return affiliate


def attribute_referral(db: Session, referred_user: User, code: str) -> Optional[ReferralAttribution]:
    """
    Attribute a new user's signup to an affiliate code.
    Returns None (silently) if the code is invalid, user already attributed,
    or the user tried to use their own code.
    """
    affiliate = db.query(Affiliate).filter(Affiliate.code == code).first()
    if not affiliate:
        logger.info(f"attribution skipped: unknown code={code}")
        return None
    if affiliate.status != "active":
        logger.info(f"attribution skipped: affiliate code={code} not active")
        return None
    if affiliate.user_id == referred_user.id:
        logger.info(f"attribution skipped: self-referral user_id={referred_user.id}")
        return None

    existing = (
        db.query(ReferralAttribution)
        .filter(ReferralAttribution.referred_user_id == referred_user.id)
        .first()
    )
    if existing:
        return existing

    attribution = ReferralAttribution(
        affiliate_id=affiliate.id,
        referred_user_id=referred_user.id,
        referral_code=code,
        status="pending",
    )
    db.add(attribution)
    db.commit()
    db.refresh(attribution)
    logger.info(f"referral attributed: user_id={referred_user.id} → affiliate_id={affiliate.id}")
    return attribution


def process_invoice_commission(
    db: Session,
    stripe_invoice_id: str,
    stripe_sub_id: str,
    stripe_customer_id: str,
    amount_cents: int,
) -> Optional[CommissionLedger]:
    """
    Create a CommissionLedger entry for a paid Stripe invoice.

    Fully idempotent — safe to call multiple times for the same invoice
    (the UNIQUE constraint on stripe_invoice_id prevents duplicates).
    Returns None if no affiliate commission applies.
    """
    if amount_cents <= 0:
        return None

    # Locate the subscriber
    user = db.query(User).filter(User.stripe_customer_id == stripe_customer_id).first()
    if not user:
        return None

    # Find the referral attribution for this subscriber
    attribution = (
        db.query(ReferralAttribution)
        .filter(ReferralAttribution.referred_user_id == user.id)
        .first()
    )
    if not attribution:
        return None

    affiliate = db.query(Affiliate).filter(Affiliate.id == attribution.affiliate_id).first()
    if not affiliate or affiliate.status != "active":
        return None

    # Idempotency: skip if already recorded
    existing = (
        db.query(CommissionLedger)
        .filter(CommissionLedger.stripe_invoice_id == stripe_invoice_id)
        .first()
    )
    if existing:
        return existing

    # Count existing commissions for this subscription to enforce max_months
    if affiliate.max_months is not None:
        paid_cycles = (
            db.query(func.count(CommissionLedger.id))
            .filter(
                CommissionLedger.affiliate_id == affiliate.id,
                CommissionLedger.attribution_id == attribution.id,
                CommissionLedger.status.notin_(["voided", "reversed"]),
            )
            .scalar()
        ) or 0
        if paid_cycles >= affiliate.max_months:
            logger.info(
                f"commission skipped: max_months={affiliate.max_months} reached for attribution_id={attribution.id}"
            )
            return None

    commission_pct = float(affiliate.commission_pct)
    commission_cents = int(amount_cents * commission_pct / 100)
    hold_until = datetime.now(timezone.utc) + timedelta(days=affiliate.hold_days)

    billing_cycle = (
        (
            db.query(func.count(CommissionLedger.id))
            .filter(
                CommissionLedger.attribution_id == attribution.id,
                CommissionLedger.status.notin_(["voided", "reversed"]),
            )
            .scalar()
        )
        or 0
    ) + 1

    entry = CommissionLedger(
        affiliate_id=affiliate.id,
        attribution_id=attribution.id,
        referred_user_id=user.id,
        stripe_invoice_id=stripe_invoice_id,
        stripe_subscription_id=stripe_sub_id,
        invoice_amount_cents=amount_cents,
        commission_pct=affiliate.commission_pct,
        commission_amount_cents=commission_cents,
        status="pending",
        hold_until=hold_until,
        billing_cycle_number=billing_cycle,
        fraud_flagged=False,  # Will be updated by fraud checks
    )
    db.add(entry)

    # Mark attribution as converted on first payment
    if attribution.status == "pending":
        attribution.status = "converted"
        attribution.first_payment_at = datetime.now(timezone.utc)
        attribution.stripe_subscription_id = stripe_sub_id
    
    # Run fraud detection checks on first commission
    if billing_cycle == 1:
        from app.services import fraud_service
        fraud_signals = fraud_service.run_all_fraud_checks(db, affiliate, user, attribution)
        if fraud_signals:
            entry.fraud_flagged = True
            logger.warning(
                f"Fraud signals detected for commission {stripe_invoice_id}: "
                f"{[s.signal_type for s in fraud_signals]}"
            )

    # Update affiliate totals
    affiliate.total_referred = (
        db.query(func.count(ReferralAttribution.id))
        .filter(ReferralAttribution.affiliate_id == affiliate.id)
        .scalar()
    ) or 0
    affiliate.total_earned_cents = (affiliate.total_earned_cents or 0) + commission_cents

    db.commit()
    db.refresh(entry)
    logger.info(
        f"commission created: invoice={stripe_invoice_id} amount={commission_cents}¢ "
        f"affiliate_id={affiliate.id}"
    )
    return entry


def void_commission(db: Session, stripe_invoice_id: str, reason: str) -> Optional[CommissionLedger]:
    """Void a commission entry (refund or chargeback).  Decrements affiliate totals."""
    entry = (
        db.query(CommissionLedger)
        .filter(CommissionLedger.stripe_invoice_id == stripe_invoice_id)
        .first()
    )
    if not entry or entry.status in ("voided", "reversed", "paid"):
        return entry

    prev_status = entry.status
    entry.status = "voided"
    entry.voided_at = datetime.now(timezone.utc)
    entry.notes = (entry.notes or "") + f" | voided: {reason}"

    # Reverse total_earned_cents
    affiliate = db.query(Affiliate).filter(Affiliate.id == entry.affiliate_id).first()
    if affiliate and prev_status != "voided":
        affiliate.total_earned_cents = max(
            0, (affiliate.total_earned_cents or 0) - entry.commission_amount_cents
        )

    db.commit()
    db.refresh(entry)
    return entry


def approve_due_commissions(db: Session) -> int:
    """
    Batch-approve all pending commissions whose hold period has passed.
    Intended to be called daily by the Celery beat scheduler.
    Returns count of newly approved entries.
    """
    now = datetime.now(timezone.utc)
    entries = (
        db.query(CommissionLedger)
        .filter(
            CommissionLedger.status == "pending",
            CommissionLedger.hold_until <= now,
        )
        .all()
    )
    for e in entries:
        e.status = "approved"
        e.approved_at = now
    db.commit()
    if entries:
        logger.info(f"approved {len(entries)} commissions past hold period")
    return len(entries)


def create_payout_batch(
    db: Session,
    affiliate_id: int,
    period_start: datetime,
    period_end: datetime,
) -> PayoutBatch:
    """Gather all approved commissions for an affiliate and group them into a payout batch."""
    commissions = (
        db.query(CommissionLedger)
        .filter(
            CommissionLedger.affiliate_id == affiliate_id,
            CommissionLedger.status == "approved",
            CommissionLedger.payout_batch_id.is_(None),
            CommissionLedger.created_at >= period_start,
            CommissionLedger.created_at <= period_end,
        )
        .all()
    )
    total = sum(c.commission_amount_cents for c in commissions)

    batch = PayoutBatch(
        affiliate_id=affiliate_id,
        period_start=period_start,
        period_end=period_end,
        total_amount_cents=total,
        commission_count=len(commissions),
        status="draft",
    )
    db.add(batch)
    db.flush()

    for c in commissions:
        c.payout_batch_id = batch.id

    db.commit()
    db.refresh(batch)
    return batch


def mark_batch_paid(db: Session, batch_id: int, reference: str) -> PayoutBatch:
    """Mark a payout batch as paid and update affiliate + commission records + YTD totals."""
    batch = db.query(PayoutBatch).filter(PayoutBatch.id == batch_id).first()
    if not batch:
        raise ValueError(f"PayoutBatch {batch_id} not found")

    now = datetime.now(timezone.utc)
    batch.status = "paid"
    batch.payout_reference = reference
    batch.paid_at = now

    commissions = (
        db.query(CommissionLedger)
        .filter(CommissionLedger.payout_batch_id == batch_id)
        .all()
    )
    for c in commissions:
        c.status = "paid"
        c.paid_at = now

    affiliate = db.query(Affiliate).filter(Affiliate.id == batch.affiliate_id).first()
    if affiliate:
        affiliate.total_paid_cents = (affiliate.total_paid_cents or 0) + batch.total_amount_cents

        # Update tax profile YTD totals
        tax_profile = (
            db.query(AffiliateTaxProfile)
            .filter(AffiliateTaxProfile.affiliate_id == affiliate.id)
            .first()
        )
        if tax_profile:
            year = str(now.year)
            ytd = dict(tax_profile.ytd_paid_cents or {})
            ytd[year] = ytd.get(year, 0) + batch.total_amount_cents
            tax_profile.ytd_paid_cents = ytd

    db.commit()
    db.refresh(batch)
    return batch


def create_and_pay_batch(
    db: Session,
    affiliate_id: int,
    commission_ids: list[int],
    payout_reference: str,
) -> PayoutBatch:
    """Create a payout batch with selected commissions and immediately mark as paid."""
    # Verify all commissions exist and are approved
    commissions = (
        db.query(CommissionLedger)
        .filter(
            CommissionLedger.id.in_(commission_ids),
            CommissionLedger.affiliate_id == affiliate_id,
            CommissionLedger.status == "approved",
            CommissionLedger.payout_batch_id.is_(None),
        )
        .all()
    )
    
    if len(commissions) != len(commission_ids):
        raise ValueError("Some commissions are not available for payout")
    
    total = sum(c.commission_amount_cents for c in commissions)
    min_date = min(c.created_at for c in commissions)
    max_date = max(c.created_at for c in commissions)
    
    now = datetime.now(timezone.utc)
    
    # Create batch already in paid state
    batch = PayoutBatch(
        affiliate_id=affiliate_id,
        period_start=min_date,
        period_end=max_date,
        total_amount_cents=total,
        commission_count=len(commissions),
        status="paid",
        payout_reference=payout_reference,
        paid_at=now,
    )
    db.add(batch)
    db.flush()
    
    # Link commissions to batch and mark as paid
    for c in commissions:
        c.payout_batch_id = batch.id
        c.status = "paid"
        c.paid_at = now
    
    # Update affiliate total_paid_cents
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if affiliate:
        affiliate.total_paid_cents = (affiliate.total_paid_cents or 0) + total
        
        # Update tax profile YTD totals
        tax_profile = (
            db.query(AffiliateTaxProfile)
            .filter(AffiliateTaxProfile.affiliate_id == affiliate_id)
            .first()
        )
        if tax_profile:
            year = str(now.year)
            ytd = dict(tax_profile.ytd_paid_cents or {})
            ytd[year] = ytd.get(year, 0) + total
            tax_profile.ytd_paid_cents = ytd
    
    db.commit()
    db.refresh(batch)
    return batch
