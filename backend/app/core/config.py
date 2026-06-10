from pydantic_settings import BaseSettings
from pydantic import model_validator, field_validator
from typing import List, Optional, Union
import sys
import json


class Settings(BaseSettings):
    # App settings
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    
    # App Mode: controls signup gating, subscriptions, referrals, and landing page
    # Options: "waitlist", "active_beta", "production"
    #   waitlist:     Landing shows waitlist, invite required, subscription required, referrals visible
    #   active_beta:  Landing shows signup, invite code required, NO subscription (beta bypass), referrals hidden
    #   production:   Landing shows signup, no invite code, subscription required, referrals visible
    APP_MODE: str = "active_beta"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or JSON array"""
        if isinstance(v, str):
            # Try parsing as JSON first
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Fall back to comma-separated values
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # API Keys
    ATTOM_API_KEY: str = ""
    ESTATED_API_KEY: str = ""
    REALTOR_API_KEY: str = ""  # RapidAPI key for Realtor.com
    MAPBOX_TOKEN: str = ""
    GEOCODING_API_KEY: str = ""
    GEOCODING_PROVIDER: str = "mapbox"
    HUD_API_TOKEN: str = ""  # Free token from https://www.huduser.gov/hudapi/public/register/form
    
    # Stripe - Test Mode (for local/development)
    STRIPE_TEST_SECRET_KEY: str = ""
    STRIPE_TEST_PUBLISHABLE_KEY: str = ""
    STRIPE_TEST_WEBHOOK_SECRET: str = ""
    STRIPE_TEST_PRICE_ID: str = ""  # $19.99/month test price
    STRIPE_TEST_CONNECT_WEBHOOK_SECRET: str = ""
    
    # Stripe - Live Mode (for production)
    STRIPE_LIVE_SECRET_KEY: str = ""
    STRIPE_LIVE_PUBLISHABLE_KEY: str = ""
    STRIPE_LIVE_WEBHOOK_SECRET: str = ""
    STRIPE_LIVE_PRICE_ID: str = ""  # $29.99/month live price (prod_UEYce3CWxPU53D / price_1TG5VXGommygx45nPUb8ywur)
    STRIPE_LIVE_CONNECT_WEBHOOK_SECRET: str = ""
    
    # Active Stripe keys (computed based on ENVIRONMENT)
    @property
    def STRIPE_SECRET_KEY(self) -> str:
        """Return test or live secret key based on ENVIRONMENT"""
        return self.STRIPE_LIVE_SECRET_KEY if self.ENVIRONMENT == "production" else self.STRIPE_TEST_SECRET_KEY
    
    @property
    def STRIPE_PUBLISHABLE_KEY(self) -> str:
        """Return test or live publishable key based on ENVIRONMENT"""
        return self.STRIPE_LIVE_PUBLISHABLE_KEY if self.ENVIRONMENT == "production" else self.STRIPE_TEST_PUBLISHABLE_KEY
    
    @property
    def STRIPE_WEBHOOK_SECRET(self) -> str:
        """Return test or live webhook secret based on ENVIRONMENT"""
        return self.STRIPE_LIVE_WEBHOOK_SECRET if self.ENVIRONMENT == "production" else self.STRIPE_TEST_WEBHOOK_SECRET
    
    @property
    def STRIPE_PRICE_ID(self) -> str:
        """Return test or live price ID based on ENVIRONMENT"""
        return self.STRIPE_LIVE_PRICE_ID if self.ENVIRONMENT == "production" else self.STRIPE_TEST_PRICE_ID
    
    @property
    def STRIPE_CONNECT_WEBHOOK_SECRET(self) -> str:
        """Return test or live Connect webhook secret based on ENVIRONMENT"""
        return self.STRIPE_LIVE_CONNECT_WEBHOOK_SECRET if self.ENVIRONMENT == "production" else self.STRIPE_TEST_CONNECT_WEBHOOK_SECRET

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""  # From Google Cloud Console → OAuth 2.0 Client ID

    # Affiliate system
    REFERRALS_ENABLED: bool = False  # Master toggle for entire referral/affiliate system
    AFFILIATE_COMMISSION_PCT: float = 30.0
    AFFILIATE_HOLD_DAYS: int = 90
    AFFILIATE_MAX_MONTHS: Optional[int] = None
    AFFILIATE_MIN_PAYOUT_CENTS: int = 10000  # $100 minimum payout threshold
    TIN_ENCRYPTION_KEY: str = ""  # Fernet key for encrypting stored TIN last-4 (deprecated)

    # Auth / JWT
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_HOURS: int = 2

    # Email (Resend)
    RESEND_API_KEY: str = ""
    EMAILS_FROM: str = "noreply@send.samepagedating.com"
    EMAILS_FROM_NAME: str = "SamePageDating"
    FRONTEND_URL: str = "http://localhost:3000"

    # Investment Assumption Defaults (applied when ZIP-specific data is unavailable)
    DEFAULT_DOWN_PAYMENT_PCT: float = 0.20
    DEFAULT_INTEREST_RATE: float = 0.07
    DEFAULT_LOAN_TERM_YEARS: int = 30
    DEFAULT_CLOSING_COSTS_PCT: float = 0.06
    DEFAULT_PROPERTY_TAX_RATE: float = 0.0267  # National fallback (override per-county at runtime)
    DEFAULT_INSURANCE_PCT: float = 0.01
    DEFAULT_MAINTENANCE_PCT: float = 0.01
    DEFAULT_PROPERTY_MGMT_PCT: float = 0.10
    DEFAULT_VACANCY_RATE: float = 0.08
    DEFAULT_CAPEX_RESERVE_PCT: float = 0.10
    DEFAULT_REHAB_RATE_PER_SQFT: float = 15.0
    DEFAULT_PRICE_PER_SQFT: float = 50.0  # For comps adjustment
    DEFAULT_PER_BEDROOM: float = 5000.0
    DEFAULT_PER_BATHROOM: float = 3000.0
    
    @model_validator(mode='after')
    def validate_secret_key(self):
        """Ensure SECRET_KEY is changed in production"""
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == "change-me-in-production-use-openssl-rand-hex-32":
            print("FATAL: SECRET_KEY must be changed in production! Generate one with: openssl rand -hex 32", file=sys.stderr)
            sys.exit(1)
        if len(self.SECRET_KEY) < 32:
            print("WARNING: SECRET_KEY should be at least 32 characters for security", file=sys.stderr)
        return self

    @model_validator(mode='after')
    def validate_app_mode(self):
        """Validate APP_MODE."""
        if self.APP_MODE not in ("waitlist", "active_beta", "production"):
            print(
                "FATAL: APP_MODE must be one of: waitlist, active_beta, production",
                file=sys.stderr,
            )
            sys.exit(1)
        return self
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
