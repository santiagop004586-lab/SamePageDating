from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Match(Base):
    """Matched users (mutual likes)"""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    profile1_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    profile2_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Match metadata
    compatibility_score = Column(Integer, nullable=True)  # 0-100 compatibility percentage
    
    # Conversation status
    has_messages = Column(Boolean, default=False, nullable=False)
    last_message_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Unmatch tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    unmatched_by = Column(Integer, ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    unmatched_at = Column(DateTime(timezone=True), nullable=True)
    unmatch_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    profile1 = relationship("Profile", foreign_keys=[profile1_id])
    profile2 = relationship("Profile", foreign_keys=[profile2_id])
    messages = relationship("Message", back_populates="match", cascade="all, delete-orphan")
    
    # Composite index for efficient lookups
    __table_args__ = (
        Index('idx_match_pair', 'profile1_id', 'profile2_id'),
    )
