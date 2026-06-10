from sqlalchemy import create_engine, text
from app.db.session import Base
from app.core.config import settings

# Import all models so SQLAlchemy can create their tables
from app.models.user import User
from app.models.waitlist import WaitlistUser
from app.models.invite import Invite
from app.models.refresh_token import RefreshToken
from app.models.affiliate import Affiliate, ReferralAttribution, PayoutBatch, CommissionLedger, AffiliateTaxProfile
from app.models.feedback import Feedback

# Dating-specific models
from app.models.profile import Profile
from app.models.compatibility_question import CompatibilityQuestion
from app.models.compatibility_answer import CompatibilityAnswer
from app.models.swipe import Swipe
from app.models.match import Match
from app.models.message import Message
from app.models.photo import Photo
from app.models.moderation_action import ModerationAction


def init_db():
    """Initialize database with all tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create PostGIS extension if not exists (for storing user location coordinates)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
