from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_, func
from app.models.profile import Profile
from app.models.swipe import Swipe
from app.models.match import Match
from app.models.photo import Photo
from app.services.profile_service import ProfileService
from app.services.compatibility_service import CompatibilityService
from typing import List, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class DiscoveryService:
    """Service for discovery feed and swipe actions"""

    @staticmethod
    def get_discovery_profiles(
        db: Session,
        user_profile: Profile,
        limit: int = 10,
        offset: int = 0
    ) -> List[Profile]:
        """
        Get profiles for discovery feed
        Excludes: self, already swiped, banned/flagged, incomplete profiles
        Filters by: gender preference, age range, distance
        """
        # Calculate age from date_of_birth
        today = date.today()
        
        # Get IDs of profiles already swiped on
        swiped_ids = db.query(Swipe.swiped_id).filter(
            Swipe.swiper_id == user_profile.id
        ).subquery()
        
        # Build query
        query = db.query(Profile).filter(
            and_(
                # Exclude self
                Profile.id != user_profile.id,
                # Only complete profiles
                Profile.is_complete == True,
                # Only active profiles
                Profile.is_active == True,
                Profile.is_paused == False,
                # Not banned or flagged
                Profile.is_banned == False,
                Profile.is_flagged == False,
                # Not already swiped on
                not_(Profile.id.in_(swiped_ids))
            )
        )
        
        # Filter by gender preference
        looking_for_genders = user_profile.looking_for_gender.split(',')
        gender_filters = [Profile.gender == g.strip() for g in looking_for_genders]
        query = query.filter(or_(*gender_filters))
        
        # Get profiles and filter by age and distance in Python
        # (more complex SQL for age calculation from date_of_birth)
        candidates = query.limit(limit * 3).all()  # Get extra to filter
        
        filtered = []
        for profile in candidates:
            # Check age
            age = ProfileService.calculate_age(profile.date_of_birth)
            if not (user_profile.min_age <= age <= user_profile.max_age):
                continue
            
            # Check distance if coordinates available
            if user_profile.latitude and user_profile.longitude:
                distance = ProfileService.calculate_distance(user_profile, profile)
                if distance and distance > user_profile.max_distance_km:
                    continue
            
            filtered.append(profile)
            
            if len(filtered) >= limit:
                break
        
        logger.info(f"Found {len(filtered)} discovery profiles for user {user_profile.id}")
        return filtered

    @staticmethod
    def create_swipe(
        db: Session,
        swiper_profile: Profile,
        target_profile_id: int,
        action: str
    ) -> dict:
        """
        Create a swipe action
        Returns: {swipe, is_match, match_id}
        """
        # Check if already swiped
        existing = db.query(Swipe).filter(
            and_(
                Swipe.swiper_id == swiper_profile.id,
                Swipe.swiped_id == target_profile_id
            )
        ).first()
        
        if existing:
            raise ValueError("Already swiped on this profile")
        
        # Create swipe
        swipe = Swipe(
            swiper_id=swiper_profile.id,
            swiped_id=target_profile_id,
            action=action
        )
        db.add(swipe)
        
        is_match = False
        match_id = None
        
        # Check for mutual like (match)
        if action in ["like", "super_like"]:
            mutual_swipe = db.query(Swipe).filter(
                and_(
                    Swipe.swiper_id == target_profile_id,
                    Swipe.swiped_id == swiper_profile.id,
                    Swipe.action.in_(["like", "super_like"])
                )
            ).first()
            
            if mutual_swipe:
                # Create match
                is_match = True
                
                # Update both swipes
                swipe.is_match = True
                swipe.match_created_at = datetime.utcnow()
                mutual_swipe.is_match = True
                mutual_swipe.match_created_at = datetime.utcnow()
                
                # Calculate compatibility score
                compat = CompatibilityService.calculate_compatibility(
                    db, swiper_profile.id, target_profile_id
                )
                
                # Create match record (ensure profile1_id < profile2_id for consistency)
                profile1_id = min(swiper_profile.id, target_profile_id)
                profile2_id = max(swiper_profile.id, target_profile_id)
                
                match = Match(
                    profile1_id=profile1_id,
                    profile2_id=profile2_id,
                    compatibility_score=compat["overall_score"]
                )
                db.add(match)
                db.commit()
                db.refresh(match)
                
                match_id = match.id
                logger.info(f"Match created: {profile1_id} <-> {profile2_id}")
        
        db.commit()
        db.refresh(swipe)
        
        return {
            "swipe": swipe,
            "is_match": is_match,
            "match_id": match_id
        }

    @staticmethod
    def get_swipe_history(
        db: Session,
        profile_id: int,
        action: Optional[str] = None,
        limit: int = 50
    ) -> List[Swipe]:
        """Get swipe history for a profile"""
        query = db.query(Swipe).filter(Swipe.swiper_id == profile_id)
        
        if action:
            query = query.filter(Swipe.action == action)
        
        return query.order_by(Swipe.created_at.desc()).limit(limit).all()
