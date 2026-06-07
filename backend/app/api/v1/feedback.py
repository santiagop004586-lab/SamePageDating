from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.feedback import Feedback

router = APIRouter()


class FeedbackCreate(BaseModel):
    category: str = "general"
    rating: Optional[int] = None   # 1-5
    message: str


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
def submit_feedback(
    body: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not body.message.strip():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    fb = Feedback(
        user_id=current_user.id,
        category=body.category,
        rating=body.rating,
        message=body.message.strip(),
    )
    db.add(fb)
    db.commit()
    return {"ok": True}


@router.get("/feedback")
def list_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin only — list all feedback."""
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin only.")
    rows = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "category": r.category,
            "rating": r.rating,
            "message": r.message,
            "created_at": r.created_at,
        }
        for r in rows
    ]
