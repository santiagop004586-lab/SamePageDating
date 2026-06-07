from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.moderation_action import ModerationAction
from app.models.profile import Profile
from app.models.photo import Photo
from app.models.message import Message
from app.models.user import User
from typing import List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ModerationService:
    """Service for admin moderation actions"""

    @staticmethod
    def create_action(
        db: Session,
        moderator_id: int,
        action_type: str,
        reason: str,
        target_user_id: Optional[int] = None,
        target_profile_id: Optional[int] = None,
        target_photo_id: Optional[int] = None,
        target_message_id: Optional[int] = None,
        notes: Optional[str] = None,
        duration_days: Optional[int] = None
    ) -> ModerationAction:
        """Create a moderation action and execute it"""
        
        # Calculate expiration if duration provided
        expires_at = None
        if duration_days:
            expires_at = datetime.utcnow() + timedelta(days=duration_days)
        
        # Create action record
        action = ModerationAction(
            moderator_id=moderator_id,
            action_type=action_type,
            target_user_id=target_user_id,
            target_profile_id=target_profile_id,
            target_photo_id=target_photo_id,
            target_message_id=target_message_id,
            reason=reason,
            notes=notes,
            duration_days=duration_days,
            expires_at=expires_at
        )
        
        db.add(action)
        
        # Execute the action
        ModerationService._execute_action(db, action)
        
        db.commit()
        db.refresh(action)
        logger.info(f"Moderation action {action_type} created by user {moderator_id}")
        return action

    @staticmethod
    def _execute_action(db: Session, action: ModerationAction) -> None:
        """Execute the moderation action"""
        
        if action.action_type == "ban":
            if action.target_profile_id:
                profile = db.query(Profile).filter(Profile.id == action.target_profile_id).first()
                if profile:
                    profile.is_banned = True
                    profile.ban_reason = action.reason
                    profile.is_active = False
        
        elif action.action_type == "unban":
            if action.target_profile_id:
                profile = db.query(Profile).filter(Profile.id == action.target_profile_id).first()
                if profile:
                    profile.is_banned = False
                    profile.ban_reason = None
                    profile.is_active = True
        
        elif action.action_type == "suspend":
            if action.target_profile_id:
                profile = db.query(Profile).filter(Profile.id == action.target_profile_id).first()
                if profile:
                    profile.is_active = False
        
        elif action.action_type == "verify":
            if action.target_profile_id:
                profile = db.query(Profile).filter(Profile.id == action.target_profile_id).first()
                if profile:
                    profile.is_verified = True
        
        elif action.action_type == "approve_photo":
            if action.target_photo_id:
                photo = db.query(Photo).filter(Photo.id == action.target_photo_id).first()
                if photo:
                    photo.is_approved = True
                    photo.is_flagged = False
        
        elif action.action_type == "flag_photo":
            if action.target_photo_id:
                photo = db.query(Photo).filter(Photo.id == action.target_photo_id).first()
                if photo:
                    photo.is_flagged = True
        
        elif action.action_type == "delete_photo":
            if action.target_photo_id:
                photo = db.query(Photo).filter(Photo.id == action.target_photo_id).first()
                if photo:
                    db.delete(photo)
        
        elif action.action_type == "delete_message":
            if action.target_message_id:
                message = db.query(Message).filter(Message.id == action.target_message_id).first()
                if message:
                    message.is_deleted = True

    @staticmethod
    def get_flagged_content(db: Session, content_type: str = None) -> List[dict]:
        """Get flagged content for review"""
        flagged_items = []
        
        if not content_type or content_type == "profile":
            profiles = db.query(Profile).filter(Profile.is_flagged == True).all()
            for profile in profiles:
                user = db.query(User).filter(User.id == profile.user_id).first()
                flagged_items.append({
                    "content_type": "profile",
                    "content_id": profile.id,
                    "user_id": user.id if user else None,
                    "user_email": user.email if user else None,
                    "created_at": profile.created_at
                })
        
        if not content_type or content_type == "photo":
            photos = db.query(Photo).filter(Photo.is_flagged == True).all()
            for photo in photos:
                profile = db.query(Profile).filter(Profile.id == photo.profile_id).first()
                user = db.query(User).filter(User.id == profile.user_id).first() if profile else None
                flagged_items.append({
                    "content_type": "photo",
                    "content_id": photo.id,
                    "user_id": user.id if user else None,
                    "user_email": user.email if user else None,
                    "photo_url": photo.url,
                    "created_at": photo.created_at
                })
        
        if not content_type or content_type == "message":
            messages = db.query(Message).filter(Message.is_flagged == True).all()
            for message in messages:
                sender = db.query(Profile).filter(Profile.id == message.sender_id).first()
                user = db.query(User).filter(User.id == sender.user_id).first() if sender else None
                flagged_items.append({
                    "content_type": "message",
                    "content_id": message.id,
                    "user_id": user.id if user else None,
                    "user_email": user.email if user else None,
                    "message_content": message.content[:100],
                    "created_at": message.created_at
                })
        
        return flagged_items

    @staticmethod
    def get_pending_photo_approvals(db: Session, limit: int = 50) -> List[Photo]:
        """Get photos pending approval"""
        return db.query(Photo).filter(
            and_(
                Photo.is_approved == False,
                Photo.is_flagged == False
            )
        ).limit(limit).all()

    @staticmethod
    def get_moderation_stats(db: Session) -> dict:
        """Get moderation statistics"""
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        banned_profiles = db.query(Profile).filter(Profile.is_banned == True).count()
        suspended_profiles = db.query(Profile).filter(
            and_(
                Profile.is_active == False,
                Profile.is_banned == False
            )
        ).count()
        
        flagged_profiles = db.query(Profile).filter(Profile.is_flagged == True).count()
        flagged_photos = db.query(Photo).filter(Photo.is_flagged == True).count()
        flagged_messages = db.query(Message).filter(Message.is_flagged == True).count()
        
        pending_photos = db.query(Photo).filter(
            and_(
                Photo.is_approved == False,
                Photo.is_flagged == False
            )
        ).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "banned_users": banned_profiles,
            "suspended_users": suspended_profiles,
            "flagged_profiles": flagged_profiles,
            "flagged_photos": flagged_photos,
            "flagged_messages": flagged_messages,
            "pending_photo_approvals": pending_photos
        }

    @staticmethod
    def get_action_history(
        db: Session,
        moderator_id: Optional[int] = None,
        target_user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[ModerationAction]:
        """Get moderation action history"""
        query = db.query(ModerationAction)
        
        if moderator_id:
            query = query.filter(ModerationAction.moderator_id == moderator_id)
        
        if target_user_id:
            query = query.filter(ModerationAction.target_user_id == target_user_id)
        
        return query.order_by(ModerationAction.created_at.desc()).limit(limit).all()
