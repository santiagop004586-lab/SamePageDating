from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.match import Match
from app.models.profile import Profile
from app.models.message import Message
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MatchService:
    """Service for match management"""

    @staticmethod
    def get_user_matches(
        db: Session,
        profile_id: int,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> List[Match]:
        """Get all matches for a user"""
        query = db.query(Match).filter(
            or_(
                Match.profile1_id == profile_id,
                Match.profile2_id == profile_id
            )
        )
        
        if active_only:
            query = query.filter(Match.is_active == True)
        
        return query.order_by(Match.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def get_match_by_id(db: Session, match_id: int) -> Optional[Match]:
        """Get match by ID"""
        return db.query(Match).filter(Match.id == match_id).first()

    @staticmethod
    def get_match_between_profiles(
        db: Session,
        profile1_id: int,
        profile2_id: int
    ) -> Optional[Match]:
        """Get match between two specific profiles"""
        # Ensure consistent ordering
        pid1 = min(profile1_id, profile2_id)
        pid2 = max(profile1_id, profile2_id)
        
        return db.query(Match).filter(
            and_(
                Match.profile1_id == pid1,
                Match.profile2_id == pid2,
                Match.is_active == True
            )
        ).first()

    @staticmethod
    def unmatch(
        db: Session,
        match: Match,
        unmatched_by_profile_id: int,
        reason: Optional[str] = None
    ) -> Match:
        """Unmatch two users"""
        match.is_active = False
        match.unmatched_by = unmatched_by_profile_id
        match.unmatched_at = datetime.utcnow()
        match.unmatch_reason = reason
        
        db.commit()
        db.refresh(match)
        logger.info(f"Unmatch: {match.id} by profile {unmatched_by_profile_id}")
        return match

    @staticmethod
    def update_last_message(db: Session, match: Match, message_time: datetime) -> None:
        """Update last message timestamp for a match"""
        match.has_messages = True
        match.last_message_at = message_time
        db.commit()

    @staticmethod
    def get_match_stats(db: Session, profile_id: int) -> dict:
        """Get match statistics for a profile"""
        total_matches = db.query(Match).filter(
            and_(
                or_(
                    Match.profile1_id == profile_id,
                    Match.profile2_id == profile_id
                ),
                Match.is_active == True
            )
        ).count()
        
        matches_with_messages = db.query(Match).filter(
            and_(
                or_(
                    Match.profile1_id == profile_id,
                    Match.profile2_id == profile_id
                ),
                Match.is_active == True,
                Match.has_messages == True
            )
        ).count()
        
        return {
            "total_matches": total_matches,
            "matches_with_messages": matches_with_messages,
            "matches_no_messages": total_matches - matches_with_messages
        }

    @staticmethod
    def get_matched_profile_id(match: Match, requester_profile_id: int) -> int:
        """Get the other profile ID in a match"""
        if match.profile1_id == requester_profile_id:
            return match.profile2_id
        else:
            return match.profile1_id
