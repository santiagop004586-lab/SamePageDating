import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

ACTIVE_SUBSCRIPTION_STATUSES = {"trialing", "active", "past_due"}


def create_checkout_session(
    user_email: str,
    user_id: int,
    existing_customer_id: str = None,
    referral_code: str = None,
) -> str:
    """
    Create a Stripe Checkout session for the $19.99/month plan with a 30-day free trial.
    Returns the hosted checkout URL to redirect the user to.
    """
    meta = {"user_id": str(user_id), "referral_code": referral_code or ""}
    params: dict = {
        "payment_method_types": ["card"],
        "mode": "subscription",
        "line_items": [
            {
                "price": settings.STRIPE_PRICE_ID,
                "quantity": 1,
            }
        ],
        "subscription_data": {
            "trial_period_days": 30,
            "metadata": meta,
        },
        "metadata": meta,
        "success_url": f"{settings.FRONTEND_URL}/subscription-success?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{settings.FRONTEND_URL}/subscribe",
    }

    if existing_customer_id:
        params["customer"] = existing_customer_id
    else:
        params["customer_email"] = user_email

    session = stripe.checkout.Session.create(**params)
    return session.url


def create_portal_session(stripe_customer_id: str) -> str:
    """
    Create a Stripe Billing Portal session so the user can manage their subscription
    (update payment method, cancel, view invoices, etc.).
    """
    session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url=f"{settings.FRONTEND_URL}/app",
    )
    return session.url


def cancel_subscription_with_refund(subscription_id: str) -> dict:
    """
    Cancel a Stripe subscription immediately and issue a prorated refund for unused time.
    Returns dict with cancellation details and refund amount.
    
    Used when user deletes their account - they should get money back for unused days.
    """
    if not subscription_id:
        return {"canceled": False, "refund_issued": False, "reason": "No subscription ID"}
    
    try:
        # Cancel the subscription immediately with proration
        canceled_sub = stripe.Subscription.cancel(
            subscription_id,
            prorate=True,  # Calculate prorated refund automatically
            invoice_now=True  # Create credit/refund invoice immediately
        )
        
        return {
            "canceled": True,
            "subscription_id": subscription_id,
            "status": canceled_sub.status,
            "refund_issued": True,
            "canceled_at": canceled_sub.canceled_at,
        }
    except stripe.error.StripeError as e:
        return {
            "canceled": False,
            "refund_issued": False,
            "error": str(e),
        }


def construct_webhook_event(payload: bytes, sig_header: str):
    """Validate and parse an incoming Stripe webhook event."""
    return stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )


def sync_subscription_from_session(session_id: str) -> dict:
    """
    Retrieve a completed Stripe Checkout Session and return the relevant
    subscription fields so the caller can update the user record.
    Used as a webhook fallback when running locally (webhooks can't reach localhost).
    """
    session = stripe.checkout.Session.retrieve(session_id, expand=["subscription"])
    customer_id = session.get("customer")
    sub = session.get("subscription")

    result = {
        "customer_id": customer_id,
        "subscription_id": None,
        "subscription_status": None,
        "trial_end": None,
    }

    if sub and not isinstance(sub, str):
        from datetime import datetime, timezone
        result["subscription_id"] = sub.id
        result["subscription_status"] = sub.status
        if sub.trial_end:
            result["trial_end"] = datetime.fromtimestamp(sub.trial_end, tz=timezone.utc)

    return result


# ========================================
# Stripe Connect Functions
# ========================================

def create_express_account(email: str, country: str = "US") -> dict:
    """
    Create a Stripe Connect Express account for an affiliate.
    Returns the account object with account_id.
    
    Express accounts are the recommended choice for marketplaces/platforms:
    - Stripe handles all regulatory compliance and tax forms (1099)
    - Affiliates see your brand during onboarding
    - You don't store sensitive bank/tax info
    """
    account = stripe.Account.create(
        type="express",
        country=country,
        email=email,
        capabilities={
            "transfers": {"requested": True},
        },
        settings={
            "payouts": {
                "schedule": {
                    "interval": "manual",  # We control when payouts happen
                }
            }
        }
    )
    return {
        "account_id": account.id,
        "email": account.email,
        "charges_enabled": account.charges_enabled,
        "payouts_enabled": account.payouts_enabled,
        "details_submitted": account.details_submitted,
    }


def create_onboarding_link(
    account_id: str, 
    refresh_url: str, 
    return_url: str
) -> str:
    """
    Generate a Stripe Connect onboarding link for an affiliate.
    
    Args:
        account_id: Stripe Connect account ID
        refresh_url: URL to redirect if onboarding link expires
        return_url: URL to redirect after successful onboarding
    
    Returns:
        Onboarding URL string
    """
    account_link = stripe.AccountLink.create(
        account=account_id,
        refresh_url=refresh_url,
        return_url=return_url,
        type="account_onboarding",
    )
    return account_link.url


def check_account_capabilities(account_id: str) -> dict:
    """
    Retrieve a Stripe Connect account and check its capabilities/status.
    
    Returns:
        Dict with payouts_enabled, charges_enabled, and account_status
    """
    account = stripe.Account.retrieve(account_id)
    
    # Determine overall account status
    status = "pending"
    if account.payouts_enabled and account.charges_enabled:
        status = "active"
    elif account.requirements and account.requirements.get("disabled_reason"):
        status = "restricted"
    elif not account.details_submitted:
        status = "pending"
    
    return {
        "account_id": account.id,
        "payouts_enabled": account.payouts_enabled,
        "charges_enabled": account.charges_enabled,
        "details_submitted": account.details_submitted,
        "account_status": status,
        "email": account.email,
        "requirements": account.requirements,
    }


def create_transfer(
    account_id: str,
    amount_cents: int,
    description: str,
    metadata: dict = None,
) -> dict:
    """
    Create a Stripe Transfer to send funds to a connected account.
    
    Note: This transfers funds from your Stripe balance to the affiliate's
    Stripe balance. The affiliate controls when to withdraw to their bank.
    
    Args:
        account_id: Stripe Connect account ID
        amount_cents: Amount in cents (e.g., 10000 = $100)
        description: Description of the transfer
        metadata: Optional dict with transfer metadata
    
    Returns:
        Dict with transfer_id and details
    
    Raises:
        stripe.error.StripeError: If transfer fails
    """
    if amount_cents <= 0:
        raise ValueError("Transfer amount must be greater than 0")
    
    transfer = stripe.Transfer.create(
        amount=amount_cents,
        currency="usd",
        destination=account_id,
        description=description,
        metadata=metadata or {},
    )
    
    return {
        "transfer_id": transfer.id,
        "amount_cents": transfer.amount,
        "destination": transfer.destination,
        "created": transfer.created,
        "status": transfer.get("status", "succeeded"),  # Transfers are instant
    }


def retrieve_account(account_id: str) -> dict:
    """
    Retrieve full account details for a Stripe Connect account.
    Used for verification and status checks.
    """
    account = stripe.Account.retrieve(account_id)
    return account
