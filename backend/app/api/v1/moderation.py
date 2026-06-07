from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db, get_admin_user
from app.models.user import User
from app.models.photo import Photo
from app.schemas.moderation import (
    ModerationActionCreate,
    ModerationActionResponse,
    FlaggedContentResponse,
    ModerationStatsResponse
)
from app.schemas.profile import PhotoSchema
from app.services.moderation_service import ModerationService
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/actions", response_model=ModerationActionResponse)
def create_moderation_action(
    action_data: ModerationActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a moderation action (admin only)"""
    action = ModerationService.create_action(
        db,
        moderator_id=current_user.id,
        action_type=action_data.action_type.value,
        reason=action_data.reason,
        target_user_id=action_data.target_user_id,
        target_profile_id=action_data.target_profile_id,
        target_photo_id=action_data.target_photo_id,
        target_message_id=action_data.target_message_id,
        notes=action_data.notes,
        duration_days=action_data.duration_days
    )
    return action


@router.get("/flagged")
def get_flagged_content(
    content_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get flagged content for review (admin only)"""
    flagged = ModerationService.get_flagged_content(db, content_type)
    return flagged


@router.get("/pending-photos", response_model=List[PhotoSchema])
def get_pending_photos(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get photos pending approval (admin only)"""
    photos = ModerationService.get_pending_photo_approvals(db, limit)
    return photos


@router.get("/stats", response_model=ModerationStatsResponse)
def get_moderation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get moderation statistics (admin only)"""
    stats = ModerationService.get_moderation_stats(db)
    return stats


@router.get("/actions/history", response_model=List[ModerationActionResponse])
def get_action_history(
    moderator_id: Optional[int] = Query(None),
    target_user_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get moderation action history (admin only)"""
    actions = ModerationService.get_action_history(
        db, moderator_id, target_user_id, limit
    )
    return actions


@router.post("/photos/{photo_id}/approve", status_code=204)
def approve_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Approve a photo (admin only)"""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    ModerationService.create_action(
        db,
        moderator_id=current_user.id,
        action_type="approve_photo",
        target_photo_id=photo_id,
        reason="Photo approved"
    )
    return None


@router.post("/photos/{photo_id}/flag", status_code=204)
def flag_photo(
    photo_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Flag a photo (admin only)"""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    ModerationService.create_action(
        db,
        moderator_id=current_user.id,
        action_type="flag_photo",
        target_photo_id=photo_id,
        reason=reason
    )
    return None
