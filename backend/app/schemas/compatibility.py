from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CompatibilityQuestionResponse(BaseModel):
    """Question response schema"""
    id: int
    question_text: str
    category: str  # Changed from enum to string to support dynamic categories
    question_type: str  # Changed from enum to string
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
    # User's answer
    text_answer: Optional[str] = None
    choice_answer: Optional[str] = None
    numeric_answer: Optional[float] = None
    boolean_answer: Optional[bool] = None
    # Preferred partner answer
    preferred_text_answer: Optional[str] = None
    preferred_choice_answer: Optional[str] = None
    preferred_numeric_answer: Optional[float] = None
    preferred_boolean_answer: Optional[bool] = None
    # Importance level (0-4: 0=Not Important, 1=Somewhat Important, 2=Important, 3=Very Important, 4=Deal Breaker)
    importance: int = Field(default=0, ge=0, le=4)
    # Filter out non-matching profiles (for deal breakers)
    exclude_non_matching: bool = Field(default=False)


class CompatibilityAnswerResponse(BaseModel):
    """Answer response schema"""
    id: int
    profile_id: int
    question_id: int
    # User's answer
    text_answer: Optional[str]
    choice_answer: Optional[str]
    numeric_answer: Optional[float]
    boolean_answer: Optional[bool]
    # Preferred partner answer
    preferred_text_answer: Optional[str]
    preferred_choice_answer: Optional[str]
    preferred_numeric_answer: Optional[float]
    preferred_boolean_answer: Optional[bool]
    # Settings
    importance: int
    exclude_non_matching: bool
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
