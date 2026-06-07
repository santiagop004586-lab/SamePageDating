from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class ActionType(str, enum.Enum):
    """Types of moderation actions"""
    WARN = "warn"
    SUSPEND = "suspend"
    BAN = "ban"
    UNBAN = "unban"
    VERIFY = "verify"
    FLAG_PHOTO = "flag_photo"
    APPROVE_PHOTO = "approve_photo"
    DELETE_PHOTO = "delete_photo"
    DELETE_MESSAGE = "delete_message"


class ModerationAction(Base):
    """Admin moderation actions log"""
    __tablename__ = "moderation_actions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Who took the action
    moderator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Who was affected
    target_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    target_profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    target_photo_id = Column(Integer, ForeignKey("photos.id", ondelete="SET NULL"), nullable=True)
    target_message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    
    # Action details
    action_type = Column(String(50), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Duration (for temporary actions like suspensions)
    duration_days = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    moderator = relationship("User", foreign_keys=[moderator_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    target_profile = relationship("Profile", foreign_keys=[target_profile_id])
