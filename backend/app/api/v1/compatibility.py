from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.compatibility import (
    CompatibilityQuestionResponse,
    AnswerSubmit,
    CompatibilityAnswerResponse,
    CompatibilityScoreResponse,
    QuestionnaireProgressResponse
)
from app.services.compatibility_service import CompatibilityService
from app.services.profile_service import ProfileService
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/questions", response_model=List[CompatibilityQuestionResponse])
def get_questions(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all compatibility questions"""
    questions = CompatibilityService.get_all_questions(db, category)
    
    # Convert options from JSON string to list
    for q in questions:
        if q.options:
            import json
            try:
                q.options = json.loads(q.options)
            except:
                q.options = []
    
    return questions


@router.post("/answers", response_model=CompatibilityAnswerResponse)
def submit_answer(
    answer_data: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit or update an answer to a compatibility question"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create profile first.")
    
    answer = CompatibilityService.submit_answer(db, profile.id, answer_data)
    return answer


@router.get("/answers/me", response_model=List[CompatibilityAnswerResponse])
def get_my_answers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's compatibility answers"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    answers = CompatibilityService.get_profile_answers(db, profile.id)
    return answers


@router.get("/progress", response_model=QuestionnaireProgressResponse)
def get_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get questionnaire completion progress"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    progress = CompatibilityService.get_questionnaire_progress(db, profile.id)
    return progress


@router.get("/score/{other_profile_id}", response_model=CompatibilityScoreResponse)
def get_compatibility_score(
    other_profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate compatibility score with another user"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    other_profile = ProfileService.get_profile_by_id(db, other_profile_id)
    if not other_profile:
        raise HTTPException(status_code=404, detail="Other profile not found")
    
    score = CompatibilityService.calculate_compatibility(db, profile.id, other_profile_id)
    
    return {
        "profile1_id": profile.id,
        "profile2_id": other_profile_id,
        **score
    }
