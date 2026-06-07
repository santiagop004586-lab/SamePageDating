from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.photo import Photo
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    PhotoUpload,
    PhotoUpdate,
    PhotoSchema
)
from app.services.profile_service import ProfileService
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new dating profile"""
    try:
        profile = ProfileService.create_profile(db, current_user.id, profile_data)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a profile by ID"""
    profile = ProfileService.get_profile_by_id(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Privacy: only show complete, active, non-banned profiles to others
    if profile.user_id != current_user.id:
        if not profile.is_complete or not profile.is_active or profile.is_banned:
            raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.patch("/me", response_model=ProfileResponse)
def update_my_profile(
    update_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = ProfileService.update_profile(db, profile, update_data)
    
    # Check if profile is now complete
    ProfileService.check_profile_complete(db, profile)
    
    return profile


@router.post("/me/photos", response_model=PhotoSchema, status_code=status.HTTP_201_CREATED)
def add_photo(
    photo_data: PhotoUpload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a photo to current user's profile"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    photo = ProfileService.add_photo(db, profile, photo_data)
    return photo


@router.delete("/me/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a photo from current user's profile"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    if photo.profile_id != profile.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    ProfileService.delete_photo(db, photo)
    return None


@router.get("/me/photos", response_model=List[PhotoSchema])
def get_my_photos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's photos"""
    profile = ProfileService.get_profile_by_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile.photos
