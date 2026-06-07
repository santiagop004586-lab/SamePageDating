from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MatchResponse(BaseModel):
    """Match response schema"""
    id: int
    profile1_id: int
    profile2_id: int
    compatibility_score: Optional[int]
    has_messages: bool
    last_message_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    # Include matched user's profile info
    matched_profile: Optional[dict] = None

    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    """List of matches"""
    matches: List[MatchResponse]
    total: int
    page: int
    page_size: int


class UnmatchRequest(BaseModel):
    """Unmatch request"""
    reason: Optional[str] = None
