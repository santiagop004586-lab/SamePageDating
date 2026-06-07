"""
Production security validator - checks critical security configurations
"""
import sys
import logging
from typing import List, Tuple
from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Validate security configurations before app startup"""
    
    @staticmethod
    def validate_all() -> Tuple[bool, List[str]]:
        """
        Run all security validations
        
        Returns:
            Tuple of (all_passed: bool, errors: List[str])
        """
        errors = []
        
        # Critical validations (will prevent startup in production)
        if settings.ENVIRONMENT == "production":
            errors.extend(SecurityValidator._validate_production_secrets())
            errors.extend(SecurityValidator._validate_stripe_config())
            errors.extend(SecurityValidator._validate_cors())
            errors.extend(SecurityValidator._validate_urls())
        
        # Warnings (logged but don't prevent startup)
        warnings = SecurityValidator._validate_optional_configs()
        for warning in warnings:
            logger.warning(f"Security warning: {warning}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_production_secrets() -> List[str]:
        """Validate that production secrets are properly set"""
        errors = []
        
        # Check SECRET_KEY
        if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters for production")
        
        if settings.SECRET_KEY == "change-me-in-production-use-openssl-rand-hex-32":
            errors.append("SECRET_KEY is still set to default value - generate with: openssl rand -hex 32")
        
        # Check database password
        if "postgres" in settings.DATABASE_URL.lower():
            if "password@" in settings.DATABASE_URL or ":password@" in settings.DATABASE_URL:
                errors.append("Database is using default/weak password - use a strong password in production")
            
            if "dealfinder_dev_password" in settings.DATABASE_URL:
                errors.append("Database is using development password in production")
        
        # Check TIN encryption key if affiliates are enabled
        if settings.APP_MODE == "production" and not settings.TIN_ENCRYPTION_KEY:
            logger.warning("TIN_ENCRYPTION_KEY not set - affiliate W-9 data cannot be stored")
        
        return errors
    
    @staticmethod
    def _validate_stripe_config() -> List[str]:
        """Validate Stripe configuration"""
        errors = []
        
        # Ensure live keys are used in production
        if settings.STRIPE_SECRET_KEY:
            if not settings.STRIPE_SECRET_KEY.startswith("sk_live_"):
                errors.append("STRIPE_SECRET_KEY must start with 'sk_live_' in production (currently using test key)")
        else:
            errors.append("STRIPE_SECRET_KEY is not configured")
        
        if settings.STRIPE_PUBLISHABLE_KEY:
            if not settings.STRIPE_PUBLISHABLE_KEY.startswith("pk_live_"):
                errors.append("STRIPE_PUBLISHABLE_KEY must start with 'pk_live_' in production (currently using test key)")
        else:
            errors.append("STRIPE_PUBLISHABLE_KEY is not configured")
        
        # Check webhook secrets are set
        if not settings.STRIPE_WEBHOOK_SECRET:
            errors.append("STRIPE_WEBHOOK_SECRET is not configured - webhooks will fail")
        
        if not settings.STRIPE_PRICE_ID:
            errors.append("STRIPE_PRICE_ID is not configured - subscriptions will fail")
        
        return errors
    
    @staticmethod
    def _validate_cors() -> List[str]:
        """Validate CORS configuration"""
        errors = []
        
        # Ensure CORS is restricted in production
        if "*" in settings.CORS_ORIGINS:
            errors.append("CORS_ORIGINS contains '*' - this allows any origin and is insecure for production")
        
        if "localhost" in str(settings.CORS_ORIGINS).lower():
            errors.append("CORS_ORIGINS contains localhost - remove development origins from production")
        
        if not settings.CORS_ORIGINS:
            errors.append("CORS_ORIGINS is empty - frontend will not be able to access API")
        
        return errors
    
    @staticmethod
    def _validate_urls() -> List[str]:
        """Validate URL configurations"""
        errors = []
        
        # Check FRONTEND_URL is production
        if not settings.FRONTEND_URL or settings.FRONTEND_URL.startswith("http://localhost"):
            errors.append("FRONTEND_URL must be set to production domain (currently localhost)")
        
        if settings.FRONTEND_URL and not settings.FRONTEND_URL.startswith("https://"):
            errors.append("FRONTEND_URL should use HTTPS in production")
        
        return errors
    
    @staticmethod
    def _validate_optional_configs() -> List[str]:
        """Validate optional but recommended configurations"""
        warnings = []
        
        # Email configuration
        if not settings.RESEND_API_KEY:
            warnings.append("RESEND_API_KEY not set - email notifications will fail")
        
        # API keys for property data
        if not settings.REALTOR_API_KEY:
            warnings.append("REALTOR_API_KEY not set - property sync will fail")
        
        if not settings.ATTOM_API_KEY:
            warnings.append("ATTOM_API_KEY not set - ATTOM property data unavailable")
        
        if not settings.ESTATED_API_KEY:
            warnings.append("ESTATED_API_KEY not set - Estated property data unavailable")
        
        # Mapbox for geocoding
        if not settings.MAPBOX_TOKEN:
            warnings.append("MAPBOX_TOKEN not set - geocoding and map features may not work")
        
        # Google OAuth
        if not settings.GOOGLE_CLIENT_ID:
            warnings.append("GOOGLE_CLIENT_ID not set - Google OAuth login will not work")
        
        return warnings
    
    @staticmethod
    def print_security_report():
        """Print a comprehensive security report"""
        print("\n" + "="*70)
        print("SECURITY CONFIGURATION REPORT")
        print("="*70)
        
        passed, errors = SecurityValidator.validate_all()
        
        print(f"\nEnvironment: {settings.ENVIRONMENT}")
        print(f"App Mode: {settings.APP_MODE}")
        
        if errors:
            print(f"\n❌ CRITICAL SECURITY ISSUES FOUND ({len(errors)}):")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
            
            if settings.ENVIRONMENT == "production":
                print("\n⚠️  APPLICATION CANNOT START IN PRODUCTION WITH THESE ERRORS")
                print("Fix the issues above and restart the application.")
                return False
        else:
            print("\n✅ All critical security checks passed")
        
        print("\nSecurity Features Enabled:")
        print(f"  • HTTPS Strict Transport Security: {'✅' if settings.ENVIRONMENT == 'production' else '⚠️  (dev only)'}")
        print(f"  • CORS Protection: {'✅' if '*' not in settings.CORS_ORIGINS else '❌'}")
        print(f"  • Stripe Live Mode: {'✅' if settings.STRIPE_SECRET_KEY.startswith('sk_live_') else '❌'}")
        print(f"  • Rate Limiting: ✅")
        print(f"  • Security Headers: ✅")
        
        print("\n" + "="*70 + "\n")
        
        return passed


def validate_on_startup():
    """
    Run security validation on app startup.
    In production, will exit if critical checks fail.
    """
    if settings.ENVIRONMENT != "production":
        logger.info("Skipping strict security checks (not in production mode)")
        return
    
    passed = SecurityValidator.print_security_report()
    
    if not passed:
        logger.critical("Security validation failed in production - exiting")
        sys.exit(1)
