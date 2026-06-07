from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class CompatibilityAnswer(Base):
    """User's answers to compatibility questions"""
    __tablename__ = "compatibility_answers"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("compatibility_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Answer data (store in appropriate field based on question type)
    text_answer = Column(Text, nullable=True)  # For text questions
    choice_answer = Column(String(255), nullable=True)  # For multiple choice (store selected option)
    numeric_answer = Column(Float, nullable=True)  # For scale/numeric questions
    boolean_answer = Column(Integer, nullable=True)  # For yes/no (0 or 1)
    
    # Importance to user
    importance = Column(Integer, default=5, nullable=False)  # 1-10: how important this is to the user
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    profile = relationship("Profile", back_populates="compatibility_answers")
    question = relationship("CompatibilityQuestion", back_populates="answers")
