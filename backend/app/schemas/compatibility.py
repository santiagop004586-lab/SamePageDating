from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class QuestionCategoryEnum(str, Enum):
    """Question categories"""
    LIFESTYLE = "lifestyle"
    VALUES = "values"
    GOALS = "goals"
    PERSONALITY = "personality"
    RELATIONSHIPS = "relationships"
    INTERESTS = "interests"
    DEALBREAKERS = "dealbreakers"


class QuestionTypeEnum(str, Enum):
    """Question types"""
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    YES_NO = "yes_no"
    TEXT = "text"


class CompatibilityQuestionResponse(BaseModel):
    """Question response schema"""
    id: int
    question_text: str
    category: QuestionCategoryEnum
    question_type: QuestionTypeEnum
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    scale_min_label: Optional[str] = None
    scale_max_label: Optional[str] = None
    weight: int
    is_dealbreaker: bool
    order_index: int

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    """Submit answer to a question"""
    question_id: int
    text_answer: Optional[str] = None
    choice_answer: Optional[str] = None
    numeric_answer: Optional[float] = None
    boolean_answer: Optional[bool] = None
    importance: int = Field(default=5, ge=1, le=10)


class CompatibilityAnswerResponse(BaseModel):
    """Answer response schema"""
    id: int
    profile_id: int
    question_id: int
    text_answer: Optional[str]
    choice_answer: Optional[str]
    numeric_answer: Optional[float]
    boolean_answer: Optional[bool]
    importance: int
    created_at: datetime

    class Config:
        from_attributes = True


class CompatibilityScoreResponse(BaseModel):
    """Compatibility score between two users"""
    profile1_id: int
    profile2_id: int
    overall_score: int  # 0-100
    category_scores: dict  # {category: score}
    dealbreaker_count: int
    compatible: bool


class QuestionnaireProgressResponse(BaseModel):
    """User's questionnaire progress"""
    total_questions: int
    answered_questions: int
    completion_percentage: int
    is_complete: bool
