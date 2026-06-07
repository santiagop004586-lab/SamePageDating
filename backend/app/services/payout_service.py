"""
Automated payout service for affiliate commissions via Stripe Connect
Handles eligibility checks, balance calculations, and transfer creation
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.affiliate import Affiliate, CommissionLedger, PayoutBatch
from app.core.config import settings
from app.services import stripe_service, fraud_service

logger = logging.getLogger(__name__)


def get_eligible_commissions(db: Session, affiliate_id: int) -> List[CommissionLedger]:
    """
    Get all commissions eligible for payout.
    
    Criteria:
    - status = 'approved'
    - payout_batch_id is NULL (not already paid)
    - hold_until <= now (hold period completed)
    - fraud_flagged = False (not flagged for fraud)
    
    Returns:
        List of eligible CommissionLedger records
    """
    now = datetime.now(timezone.utc)
    
    commissions = db.query(CommissionLedger).filter(
        and_(
            CommissionLedger.affiliate_id == affiliate_id,
            CommissionLedger.status == "approved",
            CommissionLedger.payout_batch_id.is_(None),
            CommissionLedger.hold_until <= now,
            CommissionLedger.fraud_flagged == False,
        )
    ).all()
    
    return commissions


def calculate_affiliate_balance(db: Session, affiliate_id: int) -> int:
    """
    Calculate the total eligible unpaid balance for an affiliate in cents.
    
    Returns:
        Total amount in cents
    """
    eligible = get_eligible_commissions(db, affiliate_id)
    return sum(c.commission_amount_cents for c in eligible)


def can_payout(db: Session, affiliate: Affiliate, balance_cents: int) -> Tuple[bool, Optional[str]]:
    """
    Check if an affiliate is eligible for payout.
    
    Returns:
        (can_payout: bool, reason: str if False)
    """
    # Check Stripe Connect status
    if not affiliate.stripe_account_id:
        return False, "No Stripe Connect account linked"
    
    if not affiliate.payouts_enabled:
        return False, "Stripe Connect payouts not enabled (complete onboarding)"
    
    if not affiliate.stripe_onboarding_completed:
        return False, "Stripe Connect onboarding not completed"
    
    # Check affiliate status
    if affiliate.status != "active":
        return False, f"Affiliate status is {affiliate.status} (not active)"
    
    # Check minimum balance
    min_balance = settings.AFFILIATE_MIN_PAYOUT_CENTS
    if balance_cents < min_balance:
        return False, f"Balance ${balance_cents/100:.2f} below minimum ${min_balance/100:.2f}"
    
    # Check fraud flags
    if fraud_service.should_block_payout(db, affiliate.id):
        return False, "Payout blocked due to unresolved fraud signals"
    
    return True, None


def create_payout_for_affiliate(
    db: Session,
    affiliate_id: int,
    commission_ids: Optional[List[int]] = None,
    force: bool = False
) -> Optional[PayoutBatch]:
    """
    Create a payout batch and transfer funds to affiliate via Stripe Connect.
    
    Args:
        db: Database session
        affiliate_id: Affiliate ID
        commission_ids: Optional list of specific commission IDs to pay (default: all eligible)
        force: If True, bypass minimum balance check (admin override)
    
    Returns:
        PayoutBatch record if successful, None if no payout created
    
    Raises:
        Exception: If payout creation or transfer fails
    """
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    if not affiliate:
        raise ValueError(f"Affiliate {affiliate_id} not found")
    
    # Get commissions to pay
    if commission_ids:
        commissions = db.query(CommissionLedger).filter(
            and_(
                CommissionLedger.id.in_(commission_ids),
                CommissionLedger.affiliate_id == affiliate_id,
                CommissionLedger.status == "approved",
                CommissionLedger.payout_batch_id.is_(None),
            )
        ).all()
    else:
        commissions = get_eligible_commissions(db, affiliate_id)
    
    if not commissions:
        logger.info(f"No eligible commissions for affiliate {affiliate_id}")
        return None
    
    total_cents = sum(c.commission_amount_cents for c in commissions)
    
    # Check eligibility (unless forced by admin)
    if not force:
        can_pay, reason = can_payout(db, affiliate, total_cents)
        if not can_pay:
            logger.info(f"Cannot pay affiliate {affiliate_id}: {reason}")
            return None
    
    # Calculate period
    commission_dates = [c.created_at for c in commissions]
    period_start = min(commission_dates)
    period_end = max(commission_dates)
    
    # Create Stripe Transfer
    try:
        transfer = stripe_service.create_transfer(
            account_id=affiliate.stripe_account_id,
            amount_cents=total_cents,
            description=f"Affiliate payout for {len(commissions)} commissions",
            metadata={
                "affiliate_id": str(affiliate_id),
                "affiliate_code": affiliate.code,
                "commission_count": str(len(commissions)),
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
            }
        )
        
        logger.info(
            f"Created Stripe transfer {transfer['transfer_id']} for affiliate {affiliate_id}: "
            f"${total_cents/100:.2f}"
        )
    except Exception as e:
        logger.error(f"Failed to create Stripe transfer for affiliate {affiliate_id}: {e}")
        raise
    
    # Create payout batch record
    batch = PayoutBatch(
        affiliate_id=affiliate_id,
        period_start=period_start,
        period_end=period_end,
        total_amount_cents=total_cents,
        commission_count=len(commissions),
        status="paid",
        payout_method="stripe_connect",
        payout_reference=f"Automated payout via Stripe",
        stripe_transfer_id=transfer["transfer_id"],
        paid_at=datetime.now(timezone.utc),
    )
    db.add(batch)
    db.flush()  # Get batch ID
    
    # Update commissions
    for commission in commissions:
        commission.status = "paid"
        commission.paid_at = datetime.now(timezone.utc)
        commission.payout_batch_id = batch.id
    
    # Update affiliate totals
    affiliate.total_paid_cents = (affiliate.total_paid_cents or 0) + total_cents
    
    db.commit()
    db.refresh(batch)
    
    logger.info(
        f"Payout batch {batch.id} created for affiliate {affiliate_id}: "
        f"{len(commissions)} commissions, ${total_cents/100:.2f}"
    )
    
    return batch


def process_monthly_payouts(db: Session) -> dict:
    """
    Process monthly payouts for all eligible affiliates.
    
    This is the main function called by the Celery beat task.
    Iterates through all affiliates with payouts_enabled=True and creates
    payouts if they meet eligibility criteria.
    
    Returns:
        Dict with stats: {paid: int, skipped: int, failed: int, total_paid_cents: int}
    """
    stats = {
        "paid": 0,
        "skipped": 0,
        "failed": 0,
        "total_paid_cents": 0,
        "skipped_reasons": {},
    }
    
    # Get all affiliates with Stripe Connect enabled
    affiliates = db.query(Affiliate).filter(
        and_(
            Affiliate.status == "active",
            Affiliate.stripe_account_id.isnot(None),
            Affiliate.payouts_enabled == True,
        )
    ).all()
    
    logger.info(f"Processing monthly payouts for {len(affiliates)} affiliates")
    
    for affiliate in affiliates:
        try:
            balance_cents = calculate_affiliate_balance(db, affiliate.id)
            
            if balance_cents == 0:
                logger.info(f"Skipping affiliate {affiliate.id}: no eligible commissions")
                stats["skipped"] += 1
                stats["skipped_reasons"]["no_balance"] = stats["skipped_reasons"].get("no_balance", 0) + 1
                continue
            
            # Check eligibility
            can_pay, reason = can_payout(db, affiliate, balance_cents)
            if not can_pay:
                logger.info(f"Skipping affiliate {affiliate.id}: {reason}")
                stats["skipped"] += 1
                # Track skip reasons
                reason_key = reason.split(":")[0].split("(")[0].strip().lower().replace(" ", "_")
                stats["skipped_reasons"][reason_key] = stats["skipped_reasons"].get(reason_key, 0) + 1
                continue
            
            # Create payout
            batch = create_payout_for_affiliate(db, affiliate.id)
            
            if batch:
                stats["paid"] += 1
                stats["total_paid_cents"] += batch.total_amount_cents
                logger.info(
                    f"✓ Paid affiliate {affiliate.id} (code: {affiliate.code}): "
                    f"${batch.total_amount_cents/100:.2f}"
                )
            else:
                stats["skipped"] += 1
                stats["skipped_reasons"]["no_batch_created"] = stats["skipped_reasons"].get("no_batch_created", 0) + 1
                
        except Exception as e:
            logger.error(f"Failed to process payout for affiliate {affiliate.id}: {e}", exc_info=True)
            stats["failed"] += 1
    
    logger.info(
        f"Monthly payout processing complete: "
        f"{stats['paid']} paid, {stats['skipped']} skipped, {stats['failed']} failed, "
        f"total: ${stats['total_paid_cents']/100:.2f}"
    )
    
    return stats
