from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class SwipeAction(str, enum.Enum):
    """Types of swipe actions"""
    LIKE = "like"  # Interested
    PASS = "pass"  # Not interested
    SUPER_LIKE = "super_like"  # Very interested (premium feature)
    SAVE = "save"  # Save for later


class Swipe(Base):
    """Discovery swipe actions (like/pass/save)"""
    __tablename__ = "swipes"

    id = Column(Integer, primary_key=True, index=True)
    swiper_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    swiped_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Swipe details
    action = Column(String(20), nullable=False)  # like, pass, super_like, save
    
    # Match tracking
    is_match = Column(Boolean, default=False, nullable=False, index=True)  # True if mutual like
    match_created_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    swiper = relationship("Profile", foreign_keys=[swiper_id], back_populates="swipes_made")
    swiped = relationship("Profile", foreign_keys=[swiped_id], back_populates="swipes_received")
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_swipe_pair', 'swiper_id', 'swiped_id'),
        Index('idx_match_lookup', 'swiper_id', 'is_match'),
    )
