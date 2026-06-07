from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.discovery import SwipeCreate, SwipeResponse, MatchNotification
from app.schemas.profile import DiscoveryProfileResponse, PhotoSchema
from app.services.discovery_service import DiscoveryService
from app.services.profile_service import ProfileService
from app.services.compatibility_service import CompatibilityService
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/feed", response_model=List[DiscoveryProfileResponse])
def get_discovery_feed(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get profiles for discovery feed"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create profile first.")
    
    if not profile.is_complete:
        raise HTTPException(status_code=400, detail="Complete your profile before discovering others")
    
    # Update last active
    ProfileService.update_last_active(db, profile)
    
    # Get discovery profiles
    discovery_profiles = DiscoveryService.get_discovery_profiles(db, profile, limit, offset)
    
    # Format response
    result = []
    for dp in discovery_profiles:
        # Calculate age
        age = ProfileService.calculate_age(dp.date_of_birth)
        
        # Calculate distance
        distance_km = ProfileService.calculate_distance(profile, dp)
        
        # Calculate compatibility score
        compat = CompatibilityService.calculate_compatibility(db, profile.id, dp.id)
        
        # Get approved photos only
        approved_photos = [PhotoSchema.model_validate(p) for p in dp.photos if p.is_approved]
        
        result.append(DiscoveryProfileResponse(
            id=dp.id,
            display_name=dp.display_name,
            age=age,
            bio=dp.bio,
            city=dp.city,
            state=dp.state,
            distance_km=distance_km,
            photos=approved_photos,
            compatibility_score=compat["overall_score"],
            is_verified=dp.is_verified
        ))
    
    return result


@router.post("/swipe", response_model=MatchNotification)
def create_swipe(
    swipe_data: SwipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a swipe action (like/pass/save)"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if not profile.is_complete:
        raise HTTPException(status_code=400, detail="Complete your profile before swiping")
    
    # Verify target profile exists
    target_profile = ProfileService.get_profile_by_id(db, swipe_data.target_profile_id)
    if not target_profile:
        raise HTTPException(status_code=404, detail="Target profile not found")
    
    try:
        result = DiscoveryService.create_swipe(
            db, profile, swipe_data.target_profile_id, swipe_data.action.value
        )
        
        # If it's a match, include matched profile info
        matched_profile_info = None
        if result["is_match"]:
            age = ProfileService.calculate_age(target_profile.date_of_birth)
            approved_photos = [PhotoSchema.model_validate(p) for p in target_profile.photos if p.is_approved]
            
            matched_profile_info = {
                "id": target_profile.id,
                "display_name": target_profile.display_name,
                "age": age,
                "photos": approved_photos
            }
        
        return MatchNotification(
            is_match=result["is_match"],
            match_id=result["match_id"],
            profile=matched_profile_info
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/swipes/history", response_model=List[SwipeResponse])
def get_swipe_history(
    action: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get swipe history"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    swipes = DiscoveryService.get_swipe_history(db, profile.id, action, limit)
    return swipes
