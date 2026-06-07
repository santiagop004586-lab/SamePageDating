import logging
from datetime import datetime, timezone
import stripe

from fastapi import APIRouter, Depends, HTTPException, Request, Body, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_verified_user
from app.core.config import settings  # Import settings for config flags
from app.core.email import send_subscription_welcome_email, send_subscription_cancellation_email
from app.models.user import User
from app.models.affiliate import Affiliate
from app.services import stripe_service, affiliate_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /billing/create-checkout-session
# Returns the Stripe-hosted checkout URL for the $19.99/month plan
# ---------------------------------------------------------------------------
@router.post("/create-checkout-session")
def create_checkout_session(
    body: dict = Body(default={}),
    current_user: User = Depends(get_verified_user),
):
    if not current_user.stripe_customer_id and not __import__("app.core.config", fromlist=["settings"]).settings.STRIPE_PRICE_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured yet. Please contact support.",
        )
    referral_code = body.get("referral_code") or None
    try:
        url = stripe_service.create_checkout_session(
            user_email=current_user.email,
            user_id=current_user.id,
            existing_customer_id=current_user.stripe_customer_id,
            referral_code=referral_code,
        )
        return {"url": url}
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail="Could not create checkout session.")


# ---------------------------------------------------------------------------
# POST /billing/sync-from-session
# Safety net: pulls subscription data directly from a completed Stripe
# Checkout Session and writes it to the user record.
#
# In production, Stripe webhooks (checkout.session.completed) handle this
# automatically and this endpoint is a no-op redundancy.
# In local dev, webhooks can't reach localhost, so this is the primary path.
# ---------------------------------------------------------------------------
@router.post("/sync-from-session")
def sync_from_session(
    session_id: str,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db),
):
    try:
        data = stripe_service.sync_subscription_from_session(session_id)
    except Exception as e:
        logger.error(f"sync_from_session error: {e}")
        raise HTTPException(status_code=500, detail="Could not sync from Stripe.")

    if data["customer_id"]:
        current_user.stripe_customer_id = data["customer_id"]
    if data["subscription_id"]:
        current_user.stripe_subscription_id = data["subscription_id"]
    if data["subscription_status"]:
        current_user.subscription_status = data["subscription_status"]
    if data["trial_end"]:
        current_user.trial_end = data["trial_end"]

    db.commit()
    db.refresh(current_user)

    return {
        "subscription_status": current_user.subscription_status,
        "trial_end": current_user.trial_end.isoformat() if current_user.trial_end else None,
    }


# ---------------------------------------------------------------------------
# POST /billing/create-portal-session
# Returns the Stripe Customer Portal URL for subscription management
# ---------------------------------------------------------------------------
@router.post("/create-portal-session")
def create_portal_session(
    current_user: User = Depends(get_verified_user),
):
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found. Please subscribe first.",
        )
    try:
        url = stripe_service.create_portal_session(current_user.stripe_customer_id)
        return {"url": url}
    except Exception as e:
        logger.error(f"Stripe portal error: {e}")
        raise HTTPException(status_code=500, detail="Could not create portal session.")


# ---------------------------------------------------------------------------
# GET /billing/status
# Returns current subscription status for the authenticated user
# ---------------------------------------------------------------------------
@router.get("/status")
def get_billing_status(current_user: User = Depends(get_verified_user)):
    return {
        "subscription_status": current_user.subscription_status,
        "trial_end": current_user.trial_end.isoformat() if current_user.trial_end else None,
        "current_period_end": (
            current_user.subscription_current_period_end.isoformat()
            if current_user.subscription_current_period_end
            else None
        ),
        "has_payment_method": bool(current_user.stripe_customer_id),
    }


# ---------------------------------------------------------------------------
# POST /billing/webhook
# Stripe webhook — NO AUTH, validated by Stripe signature
# ---------------------------------------------------------------------------
@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
    except ValueError:
        logger.error("Stripe webhook: invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        logger.error(f"Stripe webhook signature error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info(f"Stripe webhook received: {event_type}")

    # ------------------------------------------------------------------
    # checkout.session.completed
    # User completed payment (or started free trial)
    # ------------------------------------------------------------------
    if event_type == "checkout.session.completed":
        user_id = int(data.get("metadata", {}).get("user_id", 0))
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        referral_code = data.get("metadata", {}).get("referral_code") or ""

        if user_id and customer_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                if not user.subscription_status:
                    user.subscription_status = "trialing"
                db.commit()
                logger.info(f"User {user_id} checkout complete — customer: {customer_id}")

                # Send welcome email with trial info
                if subscription_id:
                    try:
                        subscription = stripe.Subscription.retrieve(subscription_id)
                        trial_end = subscription.get("trial_end")
                        
                        if trial_end:
                            from datetime import datetime
                            trial_end_date = datetime.fromtimestamp(trial_end)
                            trial_end_formatted = trial_end_date.strftime("%B %d, %Y")
                            
                            result = send_subscription_welcome_email(user.email, trial_end_formatted)
                            
                            if result:
                                logger.info(f"Welcome email sent to {user.email}, trial ends {trial_end_formatted}")
                            else:
                                logger.warning(f"Failed to send welcome email to {user.email}")
                        else:
                            logger.warning(f"No trial_end found in subscription {subscription_id}")
                    except Exception as e:
                        logger.error(f"Error sending welcome email: {e}")

                # Attribute referral if a valid code was embedded in metadata.
                if referral_code and settings.REFERRALS_ENABLED:
                    affiliate_service.attribute_referral(db, user, referral_code)

    # ------------------------------------------------------------------
    # customer.subscription.created / updated
    # ------------------------------------------------------------------
    elif event_type in ("customer.subscription.created", "customer.subscription.updated"):
        from datetime import datetime as dt  # Import locally to avoid scoping issues

        subscription_id = data.get("id")
        sub_status = data.get("status")
        customer_id = data.get("customer")
        current_period_end = data.get("current_period_end")
        trial_end = data.get("trial_end")
        cancel_at = data.get("cancel_at")
        canceled_at = data.get("canceled_at")

        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            # Check previous_attributes from the event for reactivation detection
            previous_attributes = event.get("data", {}).get("object", {})
            if "previous_attributes" in event.get("data", {}):
                previous_attributes = event["data"]["previous_attributes"]
            
            previous_cancel_at = previous_attributes.get("cancel_at") if previous_attributes else None

            user.stripe_subscription_id = subscription_id
            user.subscription_status = sub_status
            if current_period_end:
                user.subscription_current_period_end = dt.fromtimestamp(
                    current_period_end, tz=timezone.utc
                )
            if trial_end:
                user.trial_end = dt.fromtimestamp(trial_end, tz=timezone.utc)

            db.commit()
            logger.info(f"Subscription updated for customer {customer_id}: {sub_status}, cancel_at={cancel_at}, canceled_at={canceled_at}")

            # --- REACTIVATION LOGIC ---
            # If cancel_at changed from a timestamp to null, user reactivated their subscription
            is_reactivation = previous_cancel_at is not None and cancel_at is None
            if is_reactivation:
                try:
                    logger.info(f"Subscription reactivated for {user.email}")
                    # Use current period end as the "next billing date"
                    next_billing = ""
                    if current_period_end:
                        next_billing = dt.fromtimestamp(current_period_end, tz=timezone.utc).strftime("%B %d, %Y")
                    else:
                        next_billing = "your next billing cycle"
                    result = send_subscription_welcome_email(user.email, next_billing)
                    if result:
                        logger.info(f"Reactivation email sent to {user.email}")
                    else:
                        logger.error(f"Failed to send reactivation email to {user.email}")
                except Exception as e:
                    logger.error(f"Exception sending reactivation email to {user.email}: {e}")

            # --- CANCELLATION LOGIC ---
            # If canceled_at is set (immediate cancel), or cancel_at is set (scheduled cancel)
            is_immediate_cancel = canceled_at is not None
            is_scheduled_cancel = cancel_at is not None and (not is_immediate_cancel)
            if is_immediate_cancel or is_scheduled_cancel:
                try:
                    # Determine access end date
                    if is_immediate_cancel:
                        access_end_str = "immediately"
                        if canceled_at:
                            access_end_str = dt.fromtimestamp(canceled_at, tz=timezone.utc).strftime("%B %d, %Y")
                    elif is_scheduled_cancel:
                        access_end_str = "at the end of your billing period"
                        if cancel_at:
                            access_end_str = dt.fromtimestamp(cancel_at, tz=timezone.utc).strftime("%B %d, %Y")
                    else:
                        access_end_str = "immediately"

                    logger.info(f"Subscription cancelled for {user.email}, access until {access_end_str}")
                    result = send_subscription_cancellation_email(user.email, access_end_str)
                    if result:
                        logger.info(f"Cancellation email sent to {user.email}")
                    else:
                        logger.error(f"Failed to send cancellation email to {user.email}")
                except Exception as e:
                    logger.error(f"Exception sending cancellation email to {user.email}: {e}")

    # ------------------------------------------------------------------
    # customer.subscription.deleted
    # ------------------------------------------------------------------
    elif event_type == "customer.subscription.deleted":
        customer_id = data.get("customer")
        current_period_end = data.get("current_period_end")
        
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_status = "canceled"
            user.stripe_subscription_id = None
            db.commit()
            logger.info(f"Subscription canceled for customer {customer_id}")
            
            # Send cancellation email with access end date
            try:
                access_end_date = None
                if current_period_end:
                    access_end_date = datetime.fromtimestamp(current_period_end, tz=timezone.utc).strftime("%B %d, %Y at %I:%M %p UTC")
                elif user.subscription_current_period_end:
                    access_end_date = user.subscription_current_period_end.strftime("%B %d, %Y at %I:%M %p UTC")
                else:
                    access_end_date = "immediately"
                
                result = send_subscription_cancellation_email(user.email, access_end_date)
                if result:
                    logger.info(f"Subscription deletion email sent to {user.email}")
                else:
                    logger.error(f"Failed to send deletion email to {user.email}")
            except Exception as e:
                logger.error(f"Exception sending deletion email to {user.email}: {e}")

    # ------------------------------------------------------------------
    # invoice.payment_failed
    # ------------------------------------------------------------------
    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_status = "past_due"
            db.commit()
            logger.info(f"Payment failed for customer {customer_id} — marked past_due")

    # ------------------------------------------------------------------
    # invoice.payment_succeeded
    # ------------------------------------------------------------------
    elif event_type == "invoice.payment_succeeded":
        customer_id = data.get("customer")
        invoice_id = data.get("id", "")
        stripe_sub_id = data.get("subscription", "")
        amount_paid = data.get("amount_paid", 0)

        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            # Always sync status (not just on past_due recovery)
            user.subscription_status = "active"
            db.commit()
            logger.info(f"Payment succeeded for customer {customer_id} — marked active")

            # Record affiliate commission if applicable
            if amount_paid > 0 and invoice_id:
                affiliate_service.process_invoice_commission(
                    db,
                    stripe_invoice_id=invoice_id,
                    stripe_sub_id=stripe_sub_id or "",
                    stripe_customer_id=customer_id,
                    amount_cents=amount_paid,
                )

    # ------------------------------------------------------------------
    # charge.dispute.created (chargeback) / charge.refunded
    # Void affiliate commissions for refunds and chargebacks
    # ------------------------------------------------------------------
    elif event_type == "charge.dispute.created":
        # Customer initiated a chargeback/dispute
        invoice_id = data.get("invoice")
        if invoice_id:
            affiliate_service.void_commission(
                db,
                stripe_invoice_id=invoice_id,
                reason="chargeback/dispute"
            )
            logger.info(f"Commission voided for invoice {invoice_id} due to chargeback")
        else:
            logger.warning(f"charge.dispute.created received but no invoice ID found")

    elif event_type == "charge.refunded":
        # Refund was issued
        invoice_id = data.get("invoice")
        amount_refunded = data.get("amount_refunded", 0)
        
        if invoice_id and amount_refunded > 0:
            affiliate_service.void_commission(
                db,
                stripe_invoice_id=invoice_id,
                reason=f"refund (${amount_refunded / 100:.2f})"
            )
            logger.info(f"Commission voided for invoice {invoice_id} due to refund")
        else:
            logger.warning(f"charge.refunded received but no invoice ID or zero refund amount")

    # ------------------------------------------------------------------
    # account.updated (Stripe Connect)
    # Update affiliate's Stripe Connect status when onboarding completes
    # ------------------------------------------------------------------
    elif event_type == "account.updated":
        account_id = data.get("id")
        if account_id:
            # Find affiliate by stripe_account_id
            affiliate = db.query(Affiliate).filter(
                Affiliate.stripe_account_id == account_id
            ).first()
            
            if affiliate:
                # Update capabilities from Stripe
                affiliate.payouts_enabled = data.get("payouts_enabled", False)
                affiliate.stripe_charges_enabled = data.get("charges_enabled", False)
                affiliate.stripe_onboarding_completed = data.get("details_submitted", False)
                
                # Determine overall status
                if affiliate.payouts_enabled and affiliate.stripe_charges_enabled:
                    affiliate.stripe_account_status = "active"
                elif data.get("requirements", {}).get("disabled_reason"):
                    affiliate.stripe_account_status = "restricted"
                else:
                    affiliate.stripe_account_status = "pending"
                
                db.commit()
                logger.info(f"Updated Stripe Connect status for affiliate {affiliate.id}: "
                          f"payouts_enabled={affiliate.payouts_enabled}, "
                          f"status={affiliate.stripe_account_status}")
            else:
                logger.warning(f"account.updated received for {account_id} but no matching affiliate found")
        else:
            logger.warning(f"account.updated received but no account ID in event data")

    return {"received": True}
