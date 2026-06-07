from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.message import Message
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    MarkReadRequest,
    ConversationResponse
)
from app.services.message_service import MessageService
from app.services.match_service import MatchService
from app.services.profile_service import ProfileService
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=MessageResponse, status_code=201)
def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message in a match conversation"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    try:
        message = MessageService.send_message(
            db,
            message_data.match_id,
            profile.id,
            message_data.message_type.value,
            message_data.content
        )
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conversations for current user"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    conversations = MessageService.get_all_conversations(db, profile.id)
    return conversations


@router.get("/match/{match_id}", response_model=MessageListResponse)
def get_conversation(
    match_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages for a specific match"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Verify match exists and user is part of it
    match = MatchService.get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if profile.id not in [match.profile1_id, match.profile2_id]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    offset = (page - 1) * page_size
    messages = MessageService.get_conversation(db, match_id, page_size, offset)
    
    # Get total count
    total_messages = MessageService.get_conversation(db, match_id, limit=10000)
    total = len(total_messages)
    
    return MessageListResponse(
        messages=messages,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/read", status_code=204)
def mark_read(
    request: MarkReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark messages as read"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    MessageService.mark_messages_read(db, request.message_ids, profile.id)
    return None


@router.get("/match/{match_id}/unread-count")
def get_unread_count(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unread message count for a match"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Verify match exists and user is part of it
    match = MatchService.get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if profile.id not in [match.profile1_id, match.profile2_id]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    count = MessageService.get_unread_count(db, match_id, profile.id)
    return {"unread_count": count}


@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a message (sender only)"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.sender_id != profile.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    MessageService.delete_message(db, message)
    return None


@router.post("/{message_id}/flag", status_code=204)
def flag_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Flag a message for moderation"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Can't flag your own messages
    if message.sender_id == profile.id:
        raise HTTPException(status_code=400, detail="Cannot flag your own message")
    
    MessageService.flag_message(db, message)
    return None
