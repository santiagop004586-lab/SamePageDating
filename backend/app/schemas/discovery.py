from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class SwipeActionEnum(str, Enum):
    """Swipe actions"""
    LIKE = "like"
    PASS = "pass"
    SUPER_LIKE = "super_like"
    SAVE = "save"


class SwipeCreate(BaseModel):
    """Create swipe action"""
    target_profile_id: int
    action: SwipeActionEnum


class SwipeResponse(BaseModel):
    """Swipe response"""
    id: int
    swiper_id: int
    swiped_id: int
    action: str
    is_match: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MatchNotification(BaseModel):
    """Match notification response"""
    is_match: bool
    match_id: Optional[int] = None
    profile: Optional[dict] = None  # Profile info of matched user
