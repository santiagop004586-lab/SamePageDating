"""
Database initialization script for SamePageDating
Creates all tables for the dating platform
"""
from sqlalchemy import create_engine
from app.core.config import settings
from app.db.session import Base
from app.models import (
    User, Affiliate, Invite, RefreshToken, Feedback, WaitlistUser,
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
    
    # Delete existing questions if any
    db.query(CompatibilityQuestion).delete()
    db.commit()
    
    questions = [
        # Relationship Boundaries
        {
            "question_text": "Are you comfortable with your partner having friends of the opposite sex without you present?",
            "category": "relationship_boundaries",
            "question_type": "yes_no",
            "weight": 5,
            "is_dealbreaker": False,
            "order_index": 1
        },
        {
            "question_text": "Is staying friends with exes acceptable?",
            "category": "relationship_boundaries",
            "question_type": "yes_no",
            "weight": 5,
            "is_dealbreaker": False,
            "order_index": 2
        },
        {
            "question_text": "Should partners share phone passwords?",
            "category": "relationship_boundaries",
            "question_type": "yes_no",
            "weight": 5,
            "is_dealbreaker": False,
           "order_index": 3
        },
        {
            "question_text": "Should partners have access to each other's social media accounts?",
            "category": "relationship_boundaries",
            "question_type": "yes_no",
            "weight": 5,
            "is_dealbreaker": False,
            "order_index": 4
        },
        {
            "question_text": "Should partners share their live location with each other?",
            "category": "relationship_boundaries",
            "question_type": "yes_no",
            "weight": 5,
            "is_dealbreaker": False,
            "order_index": 5
        },
        
        # Intimacy
        {
            "question_text": "How often should you and your partner have sex?",
            "category": "intimacy",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Multiple times a day",
                "Once a day",
                "A few times a week",
                "Once a week",
                "A few times a month",
                "Once a month",
                "Less than once a month",
                "Never/Asexual"
            ]),
            "weight": 8,
            "is_dealbreaker": False,
            "order_index": 6
        },
        
        # Lifestyle
        {
            "question_text": "How often do you drink alcohol?",
            "category": "lifestyle",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Never",
                "Rarely (a few times a year)",
                "Occasionally (once a month)",
                "Socially (a few times a month)",
                "Regularly (a few times a week)",
                "Daily"
            ]),
            "weight": 6,
            "is_dealbreaker": False,
            "order_index": 7
        },
        {
            "question_text": "How often do you smoke nicotine?",
            "category": "lifestyle",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Never",
                "Rarely (a few times a year)",
                "Occasionally (once a month)",
                "Socially (a few times a month)",
                "Regularly (a few times a week)",
                "Daily"
            ]),
            "weight": 7,
            "is_dealbreaker": False,
            "order_index": 8
        },
        {
            "question_text": "How often do you smoke weed?",
            "category": "lifestyle",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Never",
                "Rarely (a few times a year)",
                "Occasionally (once a month)",
                "Socially (a few times a month)",
                "Regularly (a few times a week)",
                "Daily"
            ]),
            "weight": 6,
            "is_dealbreaker": False,
            "order_index": 9
        },
        {
            "question_text": "How often do you do other recreational drugs? (excluding alcohol, nicotine, and weed)",
            "category": "lifestyle",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Never",
                "Rarely (a few times a year)",
                "Occasionally (once a month)",
                "Socially (a few times a month)",
                "Regularly (a few times a week)",
                "Daily"
            ]),
            "weight": 7,
            "is_dealbreaker": False,
            "order_index": 10
        },
        
        # Money & Career
        {
            "question_text": "Do you prioritize spending money (vacations, experiences, purchases) or investing money for the future?",
            "category": "money_career",
            "question_type": "scale",
            "scale_min": 1,
            "scale_max": 10,
            "scale_min_label": "Spending now",
            "scale_max_label": "Investing for future",
            "weight": 6,
            "is_dealbreaker": False,
            "order_index": 11
        },
        {
            "question_text": "Would you consider being a stay at home partner?",
            "category": "money_career",
            "question_type": "yes_no",
            "weight": 5,
            "is_dealbreaker": False,
            "order_index": 12
        },
        
        # Family
        {
            "question_text": "Do you want to have kids?",
            "category": "family",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Yes, definitely",
                "Probably yes",
                "Not sure / Open to discussion",
                "Probably not",
                "No, definitely not",
                "Already have kids, don't want more",
                "Already have kids, open to more"
            ]),
            "weight": 10,
            "is_dealbreaker": True,
            "order_index": 13
        },
        
        # Dating Goals
        {
            "question_text": "What are you looking for? (Select all that apply)",
            "category": "dating_goals",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Marriage",
                "Long Term Relationship",
                "Serious Dating",
                "Casual Dating",
                "Friends First",
                "Unsure"
            ]),
            "weight": 10,
            "is_dealbreaker": False,
            "order_index": 14
        },
        
        # Religion
        {
            "question_text": "What religion should your partner be?",
            "category": "religion",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "No preference",
                "Atheist/Agnostic",
                "Christian",
                "Catholic",
                "Jewish",
                "Muslim",
                "Hindu",
                "Buddhist",
                "Other"
            ]),
            "weight": 7,
            "is_dealbreaker": False,
            "order_index": 15
        },
        
        # Politics
        {
            "question_text": "What political affiliation should your partner have?",
            "category": "politics",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "No preference",
                "Very Liberal",
                "Liberal",
                "Moderate",
                "Conservative",
                "Very Conservative",
                "Libertarian",
                "Other/Non-political"
            ]),
            "weight": 6,
            "is_dealbreaker": False,
            "order_index": 16
        },
        
        # Communication
        {
            "question_text": "How quickly do you want your partner to reply to text messages?",
            "category": "communication",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Immediately (within minutes)",
                "Within an hour",
                "Within a few hours",
                "Same day is fine",
                "Whenever they can, no rush"
            ]),
            "weight": 4,
            "is_dealbreaker": False,
            "order_index": 17
        },
        {
            "question_text": "How often do you want to meet up with your partner in real life?",
            "category": "communication",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Every day",
                "A few times a week",
                "Once a week",
                "A few times a month",
                "Once a month",
                "Less than once a month"
            ]),
            "weight": 7,
            "is_dealbreaker": False,
            "order_index": 18
        },
        {
            "question_text": "How often do you want to go out and do social activities with your partner?",
            "category": "communication",
            "question_type": "multiple_choice",
            "options": json.dumps([
                "Multiple times a week",
                "Once a week",
                "A few times a month",
                "Once a month",
                "Rarely (a few times a year)",
                "Never, I prefer staying in"
            ]),
            "weight": 5,
            "is_dealbreaker": False,
            "order_index": 19
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
