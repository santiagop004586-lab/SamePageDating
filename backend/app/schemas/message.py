from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageTypeEnum(str, Enum):
    """Message types"""
    TEXT = "text"
    PHOTO = "photo"
    VOICE = "voice"
    GIF = "gif"


class MessageCreate(BaseModel):
    """Create message request"""
    match_id: int
    message_type: MessageTypeEnum = MessageTypeEnum.TEXT
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    """Message response schema"""
    id: int
    match_id: int
    sender_id: int
    message_type: str
    content: str
    is_read: bool
    read_at: Optional[datetime]
    is_flagged: bool
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """List of messages in a conversation"""
    messages: List[MessageResponse]
    total: int
    page: int
    page_size: int


class MarkReadRequest(BaseModel):
    """Mark messages as read"""
    message_ids: List[int]


class ConversationResponse(BaseModel):
    """Conversation summary"""
    match_id: int
    matched_profile_id: int
    matched_profile_name: str
    matched_profile_photo: Optional[str]
    last_message: Optional[MessageResponse]
    unread_count: int
    created_at: datetime
