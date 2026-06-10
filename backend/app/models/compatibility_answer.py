from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class CompatibilityAnswer(Base):
    """User's answers to compatibility questions"""
    __tablename__ = "compatibility_answers"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("compatibility_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # User's answer
    text_answer = Column(Text, nullable=True)  # For text questions
    choice_answer = Column(String(255), nullable=True)  # For multiple choice (store selected option)
    numeric_answer = Column(Float, nullable=True)  # For scale/numeric questions
    boolean_answer = Column(Integer, nullable=True)  # For yes/no (0 or 1)
    
    # Preferred partner answer
    preferred_text_answer = Column(Text, nullable=True)
    preferred_choice_answer = Column(String(255), nullable=True)
    preferred_numeric_answer = Column(Float, nullable=True)
    preferred_boolean_answer = Column(Integer, nullable=True)
    
    # Importance level: 0=Not Important, 1=Somewhat Important, 2=Important, 3=Very Important, 4=Deal Breaker
    importance = Column(Integer, default=0, nullable=False)
    
    # For Deal Breakers: filter out non-matching profiles
    exclude_non_matching = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    profile = relationship("Profile", back_populates="compatibility_answers")
    question = relationship("CompatibilityQuestion", back_populates="answers")
