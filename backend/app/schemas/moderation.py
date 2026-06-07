from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ActionTypeEnum(str, Enum):
    """Moderation action types"""
    WARN = "warn"
    SUSPEND = "suspend"
    BAN = "ban"
    UNBAN = "unban"
    VERIFY = "verify"
    FLAG_PHOTO = "flag_photo"
    APPROVE_PHOTO = "approve_photo"
    DELETE_PHOTO = "delete_photo"
    DELETE_MESSAGE = "delete_message"


class ModerationActionCreate(BaseModel):
    """Create moderation action"""
    action_type: ActionTypeEnum
    target_user_id: Optional[int] = None
    target_profile_id: Optional[int] = None
    target_photo_id: Optional[int] = None
    target_message_id: Optional[int] = None
    reason: str = Field(..., min_length=10, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    duration_days: Optional[int] = Field(None, ge=1, le=365)


class ModerationActionResponse(BaseModel):
    """Moderation action response"""
    id: int
    moderator_id: Optional[int]
    target_user_id: Optional[int]
    target_profile_id: Optional[int]
    target_photo_id: Optional[int]
    target_message_id: Optional[int]
    action_type: str
    reason: str
    notes: Optional[str]
    duration_days: Optional[int]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class FlaggedContentResponse(BaseModel):
    """Flagged content for review"""
    content_type: str  # profile, photo, message
    content_id: int
    user_id: int
    user_email: str
    flag_count: int
    recent_flags: List[str]  # Recent flag reasons
    created_at: datetime


class ModerationStatsResponse(BaseModel):
    """Moderation statistics"""
    total_users: int
    active_users: int
    banned_users: int
    suspended_users: int
    flagged_profiles: int
    flagged_photos: int
    flagged_messages: int
    pending_photo_approvals: int
