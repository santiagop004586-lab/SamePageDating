"""
Shared test fixtures.

Tests run against a dedicated PostgreSQL test database so that PostGIS,
JSONB, and every other production feature works identically.

The DATABASE_URL used by every test is:
  - Inside Docker  : postgresql://dealfinder:dealfinder_dev_password@postgres:5432/dealfinder_test
  - On your machine: postgresql://dealfinder:dealfinder_dev_password@localhost:5432/dealfinder_test

The conftest creates the test database + PostGIS extension automatically.
All tables are created once per pytest session and each test function gets a
clean state via a transactional rollback.
"""
import os
import pytest
from unittest.mock import patch

# ── Environment MUST be set before any app module is imported ─────────────────
# Detect whether we're running inside Docker (hostname "postgres" resolves) or locally
_pg_host = os.getenv("POSTGRES_TEST_HOST", "postgres")
os.environ.setdefault(
    "DATABASE_URL",
    f"postgresql://dealfinder:dealfinder_dev_password@{_pg_host}:5432/dealfinder_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-min-32-chars-long-for-jwt!")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("TIN_ENCRYPTION_KEY", "")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")

# Patch email-sending globally before any import loads the real implementation
_patches = [
    patch("app.core.email.send_verification_email", return_value=None),
    patch("app.core.email.send_password_reset_email", return_value=None),
]
for _p in _patches:
    _p.start()

# ── Now safe to import app code ───────────────────────────────────────────────
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.user import User
from app.models.affiliate import (
    Affiliate,
    ReferralAttribution,
    CommissionLedger,
    PayoutBatch,
    AffiliateTaxProfile,
)
from app.core.security import hash_password


# ── Create the test database if it doesn't exist ─────────────────────────────
def _ensure_test_db():
    base_url = os.environ["DATABASE_URL"].rsplit("/", 1)[0]
    admin_url = base_url + "/dealfinder"
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'dealfinder_test'")
        ).fetchone()
        if not exists:
            conn.execute(text("CREATE DATABASE dealfinder_test"))
    engine.dispose()


# ── Session-scoped engine: tables created once --------------------------------
@pytest.fixture(scope="session")
def engine():
    _ensure_test_db()
    e = create_engine(os.environ["DATABASE_URL"])
    with e.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()
    Base.metadata.create_all(e)
    yield e
    Base.metadata.drop_all(e)
    e.dispose()


# ── Per-test transactional rollback: each test runs in its own SAVEPOINT ------
@pytest.fixture(scope="function")
def db(engine):
    """
    Yields a SQLAlchemy Session bound to a connection that is rolled back
    after each test. Service functions may call session.commit() freely —
    those commits only affect the connection-level transaction, which is
    rolled back at the end.
    """
    connection = engine.connect()
    outer_txn = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    outer_txn.rollback()
    connection.close()


# ── Reusable user fixtures ────────────────────────────────────────────────────
@pytest.fixture
def verified_user(db):
    user = User(
        email="verified@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Test User",
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def unverified_user(db):
    from app.core.security import generate_secure_token
    from datetime import datetime, timezone, timedelta

    token = generate_secure_token()
    user = User(
        email="unverified@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Unverified User",
        is_verified=False,
        is_active=True,
        verification_token=token,
        verification_token_expires=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def affiliate_owner(db):
    user = User(
        email="aff_owner@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Affiliate Owner",
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def referred_customer(db):
    user = User(
        email="customer@example.com",
        hashed_password=hash_password("Password123!"),
        full_name="Referred Customer",
        is_verified=True,
        is_active=True,
        stripe_customer_id="cus_test_referred",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def active_affiliate(db, affiliate_owner):
    from app.services.affiliate_service import create_affiliate
    return create_affiliate(db, affiliate_owner)


@pytest.fixture
def attributed_referral(db, active_affiliate, referred_customer):
    from app.services.affiliate_service import attribute_referral
    return attribute_referral(db, referred_customer, active_affiliate.code)
