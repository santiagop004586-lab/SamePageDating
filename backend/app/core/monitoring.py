"""
Production monitoring and health check utilities
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings

logger = logging.getLogger(__name__)


class HealthCheck:
    """Health check utilities for production monitoring"""
    
    @staticmethod
    def check_database(db: Session) -> Dict[str, Any]:
        """
        Check database connectivity and return status
        
        Returns:
            dict with 'healthy' bool and optional 'error' message
        """
        try:
            # Simple query to verify DB is responsive
            result = db.execute(text("SELECT 1")).scalar()
            if result == 1:
                return {
                    "healthy": True,
                    "service": "database",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "healthy": False,
                "service": "database",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "healthy": False,
            "service": "database",
            "error": "Unexpected health check failure"
        }
    
    @staticmethod
    def check_redis() -> Dict[str, Any]:
        """
        Check Redis connectivity
        
        Returns:
            dict with 'healthy' bool and optional 'error' message
        """
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            r.ping()
            return {
                "healthy": True,
                "service": "redis",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "healthy": False,
                "service": "redis",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    def check_stripe() -> Dict[str, Any]:
        """
        Check Stripe API connectivity
        
        Returns:
            dict with 'healthy' bool and optional 'error' message
        """
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Simple API call to verify credentials
            stripe.Account.retrieve()
            
            return {
                "healthy": True,
                "service": "stripe",
                "mode": "live" if settings.STRIPE_SECRET_KEY.startswith("sk_live_") else "test",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Stripe health check failed: {e}")
            return {
                "healthy": False,
                "service": "stripe",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    def check_email() -> Dict[str, Any]:
        """
        Check email service configuration (Resend)
        
        Returns:
            dict with 'healthy' bool and optional 'error' message
        """
        try:
            if not settings.RESEND_API_KEY:
                return {
                    "healthy": False,
                    "service": "email",
                    "error": "Resend API key not configured",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Don't actually send an email, just verify key is set
            return {
                "healthy": True,
                "service": "email",
                "provider": "resend",
                "configured": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Email service check failed: {e}")
            return {
                "healthy": False,
                "service": "email",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


class MetricsCollector:
    """Collect application metrics for monitoring dashboards"""
    
    @staticmethod
    def get_subscription_metrics(db: Session) -> Dict[str, Any]:
        """
        Get subscription health metrics
        
        Returns:
            dict with subscription counts by status
        """
        try:
            from app.models.user import User
            from sqlalchemy import func
            
            # Count users by subscription status
            status_counts = (
                db.query(
                    User.subscription_status,
                    func.count(User.id).label('count')
                )
                .filter(User.is_active == True)
                .group_by(User.subscription_status)
                .all()
            )
            
            metrics = {
                status or 'none': count 
                for status, count in status_counts
            }
            
            # Calculate totals
            metrics['total_active_users'] = sum(metrics.values())
            metrics['paying_users'] = metrics.get('active', 0) + metrics.get('trialing', 0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting subscription metrics: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_affiliate_metrics(db: Session) -> Dict[str, Any]:
        """
        Get affiliate program metrics
        
        Returns:
            dict with affiliate and commission stats
        """
        try:
            from app.models.affiliate import Affiliate, CommissionLedger
            from sqlalchemy import func
            
            # Count affiliates by status
            affiliate_count = db.query(func.count(Affiliate.id)).scalar() or 0
            
            # Commission summary
            commission_stats = (
                db.query(
                    CommissionLedger.status,
                    func.count(CommissionLedger.id).label('count'),
                    func.sum(CommissionLedger.commission_amount_cents).label('total_cents')
                )
                .group_by(CommissionLedger.status)
                .all()
            )
            
            metrics = {
                'total_affiliates': affiliate_count,
                'commissions': {}
            }
            
            for status, count, total_cents in commission_stats:
                metrics['commissions'][status] = {
                    'count': count,
                    'total_cents': total_cents or 0,
                    'total_dollars': (total_cents or 0) / 100
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting affiliate metrics: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_property_metrics(db: Session) -> Dict[str, Any]:
        """
        Get property data metrics
        
        Returns:
            dict with property counts and freshness
        """
        try:
            from app.models.property import Property
            from sqlalchemy import func
            
            # Count properties by status
            total = db.query(func.count(Property.id)).scalar() or 0
            
            status_counts = (
                db.query(
                    Property.status,
                    func.count(Property.id).label('count')
                )
                .group_by(Property.status)
                .all()
            )
            
            # Most recent property update
            latest_update = (
                db.query(func.max(Property.updated_at))
                .scalar()
            )
            
            metrics = {
                'total_properties': total,
                'by_status': {status: count for status, count in status_counts},
                'latest_update': latest_update.isoformat() if latest_update else None
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting property metrics: {e}")
            return {"error": str(e)}


def configure_production_logging():
    """
    Configure structured logging for production
    Should be called at app startup
    """
    import logging.config
    
    # Production logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            },
            'error_console': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'stream': 'ext://sys.stderr',
            },
        },
        'loggers': {
            'app': {
                'level': 'INFO',
                'handlers': ['console', 'error_console'],
                'propagate': False,
            },
            'uvicorn': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False,
            },
            'sqlalchemy': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False,
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'error_console'],
        },
    }
    
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info(f"Production logging configured - Environment: {settings.ENVIRONMENT}")
