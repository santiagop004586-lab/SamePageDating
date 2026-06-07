from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.match import MatchResponse, MatchListResponse, UnmatchRequest
from app.schemas.profile import PhotoSchema
from app.services.match_service import MatchService
from app.services.profile_service import ProfileService
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=MatchListResponse)
def get_matches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's matches"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    offset = (page - 1) * page_size
    matches = MatchService.get_user_matches(db, profile.id, active_only=True, limit=page_size, offset=offset)
    
    # Get total count
    total_matches = MatchService.get_user_matches(db, profile.id, active_only=True)
    total = len(total_matches)
    
    # Format response with matched profile info
    result = []
    for match in matches:
        matched_profile_id = MatchService.get_matched_profile_id(match, profile.id)
        matched_profile = ProfileService.get_profile_by_id(db, matched_profile_id)
        
        if matched_profile:
            age = ProfileService.calculate_age(matched_profile.date_of_birth)
            approved_photos = [PhotoSchema.model_validate(p) for p in matched_profile.photos if p.is_approved]
            primary_photo = None
            if approved_photos:
                primary_photos = [p for p in approved_photos if p.is_primary]
                primary_photo = primary_photos[0].url if primary_photos else approved_photos[0].url
            
            matched_profile_info = {
                "id": matched_profile.id,
                "display_name": matched_profile.display_name,
                "age": age,
                "photo": primary_photo
            }
        else:
            matched_profile_info = None
        
        match_dict = MatchResponse.model_validate(match).model_dump()
        match_dict["matched_profile"] = matched_profile_info
        result.append(match_dict)
    
    return MatchListResponse(
        matches=result,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific match"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    match = MatchService.get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Verify user is part of this match
    if profile.id not in [match.profile1_id, match.profile2_id]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get matched profile info
    matched_profile_id = MatchService.get_matched_profile_id(match, profile.id)
    matched_profile = ProfileService.get_profile_by_id(db, matched_profile_id)
    
    if matched_profile:
        age = ProfileService.calculate_age(matched_profile.date_of_birth)
        approved_photos = [PhotoSchema.model_validate(p) for p in matched_profile.photos if p.is_approved]
        primary_photo = None
        if approved_photos:
            primary_photos = [p for p in approved_photos if p.is_primary]
            primary_photo = primary_photos[0].url if primary_photos else approved_photos[0].url
        
        matched_profile_info = {
            "id": matched_profile.id,
            "display_name": matched_profile.display_name,
            "age": age,
            "photo": primary_photo
        }
    else:
        matched_profile_info = None
    
    match_dict = MatchResponse.model_validate(match).model_dump()
    match_dict["matched_profile"] = matched_profile_info
    
    return match_dict


@router.post("/{match_id}/unmatch", status_code=204)
def unmatch(
    match_id: int,
    request: UnmatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unmatch with a user"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    match = MatchService.get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Verify user is part of this match
    if profile.id not in [match.profile1_id, match.profile2_id]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    MatchService.unmatch(db, match, profile.id, request.reason)
    return None


@router.get("/stats/me")
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get match statistics for current user"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    stats = MatchService.get_match_stats(db, profile.id)
    return stats
