from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.profile import Profile
from app.models.photo import Photo
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate, PhotoUpload
from typing import Optional, List
from datetime import datetime, date
from geopy.distance import geodesic
import logging

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for profile management"""

    @staticmethod
    def create_profile(db: Session, user_id: int, profile_data: ProfileCreate) -> Profile:
        """Create a new dating profile"""
        # Check if profile already exists
        existing = db.query(Profile).filter(Profile.user_id == user_id).first()
        if existing:
            raise ValueError("Profile already exists for this user")

        # Calculate age from date of birth
        today = date.today()
        age = today.year - profile_data.date_of_birth.year - (
            (today.month, today.day) < (profile_data.date_of_birth.month, profile_data.date_of_birth.day)
        )
        
        if age < 18:
            raise ValueError("Must be at least 18 years old")

        profile = Profile(
            user_id=user_id,
            **profile_data.model_dump()
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        logger.info(f"Created profile for user {user_id}")
        return profile

    @staticmethod
    def get_profile_by_user(db: Session, user_id: int) -> Optional[Profile]:
        """Get profile by user ID"""
        return db.query(Profile).filter(Profile.user_id == user_id).first()

    @staticmethod
    def get_profile_by_id(db: Session, profile_id: int) -> Optional[Profile]:
        """Get profile by profile ID"""
        return db.query(Profile).filter(Profile.id == profile_id).first()

    @staticmethod
    def update_profile(db: Session, profile: Profile, update_data: ProfileUpdate) -> Profile:
        """Update profile"""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        logger.info(f"Updated profile {profile.id}")
        return profile

    @staticmethod
    def check_profile_complete(db: Session, profile: Profile) -> bool:
        """Check if profile is complete and ready for matching"""
        # Required fields
        if not all([
            profile.display_name,
            profile.date_of_birth,
            profile.gender,
            profile.looking_for_gender,
            profile.city,
            profile.state
        ]):
            return False
        
        # Must have at least one approved photo
        approved_photos = db.query(Photo).filter(
            and_(
                Photo.profile_id == profile.id,
                Photo.is_approved == True
            )
        ).count()
        
        if approved_photos == 0:
            return False
        
        profile.is_complete = True
        db.commit()
        return True

    @staticmethod
    def add_photo(db: Session, profile: Profile, photo_data: PhotoUpload) -> Photo:
        """Add photo to profile"""
        # If this is set as primary, remove primary from other photos
        if photo_data.is_primary:
            db.query(Photo).filter(Profile.id == profile.id).update({"is_primary": False})
        
        photo = Photo(
            profile_id=profile.id,
            **photo_data.model_dump()
        )
        
        db.add(photo)
        db.commit()
        db.refresh(photo)
        logger.info(f"Added photo {photo.id} to profile {profile.id}")
        return photo

    @staticmethod
    def delete_photo(db: Session, photo: Photo) -> None:
        """Delete photo"""
        profile_id = photo.profile_id
        db.delete(photo)
        db.commit()
        logger.info(f"Deleted photo from profile {profile_id}")

    @staticmethod
    def update_last_active(db: Session, profile: Profile) -> None:
        """Update last active timestamp"""
        profile.last_active_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def calculate_distance(profile1: Profile, profile2: Profile) -> Optional[float]:
        """Calculate distance between two profiles in kilometers"""
        if not all([profile1.latitude, profile1.longitude, profile2.latitude, profile2.longitude]):
            return None
        
        coords1 = (profile1.latitude, profile1.longitude)
        coords2 = (profile2.latitude, profile2.longitude)
        
        return geodesic(coords1, coords2).kilometers

    @staticmethod
    def calculate_age(date_of_birth: date) -> int:
        """Calculate age from date of birth"""
        today = date.today()
        return today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )
