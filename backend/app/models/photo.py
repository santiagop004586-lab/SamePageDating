from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Photo(Base):
    """Profile photos"""
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Photo data
    url = Column(String(500), nullable=False)  # S3 or CDN URL
    thumbnail_url = Column(String(500), nullable=True)  # Thumbnail version
    
    # Photo metadata
    is_primary = Column(Boolean, default=False, nullable=False)  # Main profile photo
    order_index = Column(Integer, default=0, nullable=False)  # Display order
    
    # Moderation
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    is_flagged = Column(Boolean, default=False, nullable=False)
    moderation_notes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    profile = relationship("Profile", back_populates="photos")
