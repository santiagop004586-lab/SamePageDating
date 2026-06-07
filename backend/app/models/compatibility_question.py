from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class QuestionCategory(str, enum.Enum):
    """Categories for compatibility questions"""
    LIFESTYLE = "lifestyle"
    VALUES = "values"
    GOALS = "goals"
    PERSONALITY = "personality"
    RELATIONSHIPS = "relationships"
    INTERESTS = "interests"
    DEALBREAKERS = "dealbreakers"


class QuestionType(str, enum.Enum):
    """Types of question responses"""
    MULTIPLE_CHOICE = "multiple_choice"  # Single selection from options
    SCALE = "scale"  # Numeric scale (e.g., 1-10)
    YES_NO = "yes_no"  # Binary yes/no
    TEXT = "text"  # Free text response


class CompatibilityQuestion(Base):
    """Questionnaire questions for compatibility scoring"""
    __tablename__ = "compatibility_questions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Question content
    question_text = Column(Text, nullable=False)
    category = Column(SQLEnum(QuestionCategory), nullable=False, index=True)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    
    # For multiple choice questions
    options = Column(Text, nullable=True)  # JSON array of options ["option1", "option2", ...]
    
    # For scale questions
    scale_min = Column(Integer, nullable=True)
    scale_max = Column(Integer, nullable=True)
    scale_min_label = Column(String(100), nullable=True)
    scale_max_label = Column(String(100), nullable=True)
    
    # Importance
    weight = Column(Integer, default=1, nullable=False)  # Weight for scoring algorithm
    is_dealbreaker = Column(Boolean, default=False, nullable=False)  # Critical question
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)  # Display order
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    answers = relationship("CompatibilityAnswer", back_populates="question", cascade="all, delete-orphan")
