"""
Database initialization script for SamePageDating
Creates all tables for the dating platform
"""
from sqlalchemy import create_engine
from app.core.config import settings
from app.db.session import Base
from app.models import (
    User, Affiliate, Invite, RefreshToken, Feedback, Waitlist,
    Profile, CompatibilityQuestion, CompatibilityAnswer,
    Swipe, Match, Message, Photo, ModerationAction
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize database tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    logger.info("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")
    
    # Log created tables
    tables = Base.metadata.tables.keys()
    logger.info(f"Created tables: {', '.join(tables)}")


def seed_compatibility_questions():
    """Seed initial compatibility questions"""
    from app.db.session import SessionLocal
    from app.models.compatibility_question import CompatibilityQuestion, QuestionCategory, QuestionType
    import json
    
    db = SessionLocal()
    
    # Check if questions already exist
    existing = db.query(CompatibilityQuestion).first()
    if existing:
        logger.info("Compatibility questions already seeded")
        db.close()
        return
    
    questions = [
        # Lifestyle
        {
            "question_text": "How often do you prefer to go out vs. stay in?",
            "category": QuestionCategory.LIFESTYLE,
            "question_type": QuestionType.SCALE,
            "scale_min": 1,
            "scale_max": 10,
            "scale_min_label": "Always stay in",
            "scale_max_label": "Always go out",
            "weight": 5,
            "is_dealbreaker": False,
            "order_index": 1
        },
        {
            "question_text": "Do you want children?",
            "category": QuestionCategory.GOALS,
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "options": json.dumps(["Yes, definitely", "Maybe someday", "Not sure", "No, never"]),
            "weight": 10,
            "is_dealbreaker": True,
            "order_index": 2
        },
        {
            "question_text": "How important is religion/spirituality in your life?",
            "category": QuestionCategory.VALUES,
            "question_type": QuestionType.SCALE,
            "scale_min": 1,
            "scale_max": 10,
            "scale_min_label": "Not important",
            "scale_max_label": "Very important",
            "weight": 8,
            "is_dealbreaker": False,
            "order_index": 3
        },
        {
            "question_text": "Are you a morning person or night owl?",
            "category": QuestionCategory.PERSONALITY,
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "options": json.dumps(["Definitely morning", "Somewhat morning", "Somewhat night", "Definitely night"]),
            "weight": 3,
            "is_dealbreaker": False,
            "order_index": 4
        },
        {
            "question_text": "Would you consider a long-distance relationship?",
            "category": QuestionCategory.RELATIONSHIPS,
            "question_type": QuestionType.YES_NO,
            "weight": 7,
            "is_dealbreaker": False,
            "order_index": 5
        },
        {
            "question_text": "How important is physical fitness to you?",
            "category": QuestionCategory.LIFESTYLE,
            "question_type": QuestionType.SCALE,
            "scale_min": 1,
            "scale_max": 10,
            "scale_min_label": "Not important",
            "scale_max_label": "Very important",
            "weight": 5,
            "is_dealbreaker": False,
            "order_index": 6
        },
        {
            "question_text": "What's your ideal Friday night?",
            "category": QuestionCategory.INTERESTS,
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "options": json.dumps([
                "Netflix and chill",
                "Going to a bar/club",
                "Dinner with friends",
                "Outdoor adventure",
                "Cultural event (museum, theater, etc.)"
            ]),
            "weight": 4,
            "is_dealbreaker": False,
            "order_index": 7
        },
        {
            "question_text": "How do you feel about pets?",
            "category": QuestionCategory.LIFESTYLE,
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "options": json.dumps([
                "Love them, have some",
                "Love them, want some",
                "They're okay",
                "Don't want pets",
                "Allergic/can't have"
            ]),
            "weight": 6,
            "is_dealbreaker": False,
            "order_index": 8
        },
        {
            "question_text": "What's your relationship with alcohol?",
            "category": QuestionCategory.LIFESTYLE,
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "options": json.dumps([
                "Don't drink",
                "Socially/occasionally",
                "Regularly/moderately",
                "Frequently"
            ]),
            "weight": 5,
            "is_dealbreaker": False,
            "order_index": 9
        },
        {
            "question_text": "Do you smoke?",
            "category": QuestionCategory.DEALBREAKERS,
            "question_type": QuestionType.YES_NO,
            "weight": 8,
            "is_dealbreaker": True,
            "order_index": 10
        },
    ]
    
    for q_data in questions:
        question = CompatibilityQuestion(**q_data)
        db.add(question)
    
    db.commit()
    logger.info(f"Seeded {len(questions)} compatibility questions")
    db.close()


if __name__ == "__main__":
    logger.info("Starting database initialization...")
    init_db()
    seed_compatibility_questions()
    logger.info("Database initialization complete!")
