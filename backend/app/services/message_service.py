from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from app.models.message import Message
from app.models.match import Match
from app.models.profile import Profile
from app.services.match_service import MatchService
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MessageService:
    """Service for messaging between matched users"""

    @staticmethod
    def send_message(
        db: Session,
        match_id: int,
        sender_profile_id: int,
        message_type: str,
        content: str
    ) -> Message:
        """Send a message in a match conversation"""
        # Verify match exists and is active
        match = MatchService.get_match_by_id(db, match_id)
        if not match:
            raise ValueError("Match not found")
        
        if not match.is_active:
            raise ValueError("Cannot send message to inactive match")
        
        # Verify sender is part of the match
        if sender_profile_id not in [match.profile1_id, match.profile2_id]:
            raise ValueError("Sender is not part of this match")
        
        # Create message
        message = Message(
            match_id=match_id,
            sender_id=sender_profile_id,
            message_type=message_type,
            content=content
        )
        
        db.add(message)
        
        # Update match last_message_at
        MatchService.update_last_message(db, match, datetime.utcnow())
        
        db.commit()
        db.refresh(message)
        logger.info(f"Message sent in match {match_id} by profile {sender_profile_id}")
        return message

    @staticmethod
    def get_conversation(
        db: Session,
        match_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a conversation"""
        return db.query(Message).filter(
            and_(
                Message.match_id == match_id,
                Message.is_deleted == False
            )
        ).order_by(Message.created_at.asc()).limit(limit).offset(offset).all()

    @staticmethod
    def mark_messages_read(
        db: Session,
        message_ids: List[int],
        reader_profile_id: int
    ) -> int:
        """Mark messages as read (only for recipient)"""
        # Get messages
        messages = db.query(Message).filter(
            Message.id.in_(message_ids)
        ).all()
        
        marked_count = 0
        for message in messages:
            # Only mark as read if the reader is NOT the sender
            if message.sender_id != reader_profile_id and not message.is_read:
                message.is_read = True
                message.read_at = datetime.utcnow()
                marked_count += 1
        
        if marked_count > 0:
            db.commit()
        
        logger.info(f"Marked {marked_count} messages as read")
        return marked_count

    @staticmethod
    def get_unread_count(db: Session, match_id: int, profile_id: int) -> int:
        """Get count of unread messages for a user in a match"""
        return db.query(Message).filter(
            and_(
                Message.match_id == match_id,
                Message.sender_id != profile_id,  # Not sent by this user
                Message.is_read == False,
                Message.is_deleted == False
            )
        ).count()

    @staticmethod
    def get_all_conversations(db: Session, profile_id: int) -> List[dict]:
        """Get all conversations for a user with unread counts"""
        # Get all matches
        matches = MatchService.get_user_matches(db, profile_id, active_only=True)
        
        conversations = []
        for match in matches:
            # Get matched profile ID
            matched_profile_id = MatchService.get_matched_profile_id(match, profile_id)
            matched_profile = db.query(Profile).filter(Profile.id == matched_profile_id).first()
            
            if not matched_profile:
                continue
            
            # Get last message
            last_message = db.query(Message).filter(
                and_(
                    Message.match_id == match.id,
                    Message.is_deleted == False
                )
            ).order_by(desc(Message.created_at)).first()
            
            # Get unread count
            unread_count = MessageService.get_unread_count(db, match.id, profile_id)
            
            # Get primary photo
            primary_photo = None
            if matched_profile.photos:
                primary_photos = [p for p in matched_profile.photos if p.is_primary]
                if primary_photos:
                    primary_photo = primary_photos[0].url
                elif matched_profile.photos:
                    primary_photo = matched_profile.photos[0].url
            
            conversations.append({
                "match_id": match.id,
                "matched_profile_id": matched_profile_id,
                "matched_profile_name": matched_profile.display_name,
                "matched_profile_photo": primary_photo,
                "last_message": last_message,
                "unread_count": unread_count,
                "created_at": match.created_at
            })
        
        # Sort by last message time (most recent first)
        conversations.sort(
            key=lambda x: x["last_message"].created_at if x["last_message"] else x["created_at"],
            reverse=True
        )
        
        return conversations

    @staticmethod
    def delete_message(db: Session, message: Message) -> None:
        """Soft delete a message"""
        message.is_deleted = True
        db.commit()
        logger.info(f"Message {message.id} deleted")

    @staticmethod
    def flag_message(db: Session, message: Message) -> None:
        """Flag a message for moderation"""
        message.is_flagged = True
        db.commit()
        logger.info(f"Message {message.id} flagged for moderation")
