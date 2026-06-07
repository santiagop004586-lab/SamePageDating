from sqlalchemy import create_engine, text
from app.db.session import Base
from app.core.config import settings
from app.models.user import User
from app.models.waitlist import WaitlistUser
from app.models.invite import Invite
from app.models.property import Property
from app.models.comparable_sale import ComparableSale
from app.models.hud_fmr import HudFMR
from app.models.zip_boundary import ZipBoundary
from app.models.etl_job import ETLJob
from app.models.zip_sync_cache import ZipSyncCache
from app.models.refresh_token import RefreshToken
from app.models.affiliate import Affiliate, ReferralAttribution, PayoutBatch, CommissionLedger, AffiliateTaxProfile


def init_db():
    """Initialize database with all tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Create PostGIS extension if not exists
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
