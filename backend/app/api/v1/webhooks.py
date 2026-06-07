"""
Webhook endpoints for external services (Stripe, etc.)
Redirects to appropriate handlers in other modules.
"""
import logging
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1 import billing

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/stripe", include_in_schema=False)
async def stripe_webhook_handler(request: Request, db: Session = Depends(get_db)):
    """
    Stripe webhook endpoint - delegates to billing.stripe_webhook
    This exists at /api/v1/webhooks/stripe for compatibility with Stripe configuration
    """
    return await billing.stripe_webhook(request, db)
