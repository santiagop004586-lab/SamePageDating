from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class MessageType(str, enum.Enum):
    """Types of messages"""
    TEXT = "text"
    PHOTO = "photo"
    VOICE = "voice"
    GIF = "gif"


class Message(Base):
    """Chat messages between matched users"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message content
    message_type = Column(String(20), nullable=False, default="text")  # text, photo, voice, gif
    content = Column(Text, nullable=True)  # Text content or file URL
    
    # Status tracking
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    match = relationship("Match", back_populates="messages")
    sender = relationship("Profile", foreign_keys=[sender_id])
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_match_messages', 'match_id', 'created_at'),
        Index('idx_unread_messages', 'match_id', 'is_read'),
    )
