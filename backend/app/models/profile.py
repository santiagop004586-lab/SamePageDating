from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Profile(Base):
    """User dating profile with personal info and preferences"""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Basic info
    display_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(50), nullable=False)  # male, female, non_binary, other
    bio = Column(Text, nullable=True)
    
    # Location
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    country = Column(String(100), nullable=False, default="USA")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Physical attributes
    height_cm = Column(Integer, nullable=True)  # Height in centimeters
    
    # Preferences
    looking_for_gender = Column(String(200), nullable=False)  # Can be comma-separated: "male,female"
    min_age = Column(Integer, nullable=False, default=18)
    max_age = Column(Integer, nullable=False, default=99)
    max_distance_km = Column(Integer, nullable=False, default=50)  # Maximum distance in kilometers
    
    # Profile status
    is_complete = Column(Boolean, default=False, nullable=False)  # Profile completed and ready for matching
    is_active = Column(Boolean, default=True, nullable=False)  # User wants to appear in discovery
    is_paused = Column(Boolean, default=False, nullable=False)  # Temporarily hidden from discovery
    
    # Moderation
    is_verified = Column(Boolean, default=False, nullable=False)  # Manual verification badge
    is_flagged = Column(Boolean, default=False, nullable=False)  # Flagged for review
    is_banned = Column(Boolean, default=False, nullable=False)  # Banned from platform
    ban_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="profile")
    photos = relationship("Photo", back_populates="profile", cascade="all, delete-orphan")
    compatibility_answers = relationship("CompatibilityAnswer", back_populates="profile", cascade="all, delete-orphan")
    swipes_made = relationship("Swipe", foreign_keys="Swipe.swiper_id", back_populates="swiper", cascade="all, delete-orphan")
    swipes_received = relationship("Swipe", foreign_keys="Swipe.swiped_id", back_populates="swiped", cascade="all, delete-orphan")
