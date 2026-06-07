"""
Public configuration API route - exposes system flags to frontend
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class SystemConfig(BaseModel):
    """Public system configuration"""
    app_mode: str  # "waitlist", "active_beta", or "production"
    referrals_enabled: bool  # Master toggle for referral/affiliate system


@router.get("/system", response_model=SystemConfig)
def get_system_config():
    """Get public system configuration flags"""
    return SystemConfig(
        app_mode=settings.APP_MODE,
        referrals_enabled=settings.REFERRALS_ENABLED,
    )
