from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.core.monitoring import HealthCheck, MetricsCollector, configure_production_logging
from app.core.security_validator import validate_on_startup
from app.api.v1 import (
    auth, 
    billing, 
    webhooks,
    affiliates, 
    admin, 
    waitlist, 
    feedback, 
    config,
    # Dating-specific endpoints
    profile,
    compatibility,
    discovery,
    matches,
    messages,
    moderation
)
import logging

logger = logging.getLogger(__name__)

# Run security validation before app starts
validate_on_startup()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SamePageDating API",
    description="Compatibility-first dating platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
)

# Include routers - Reused infrastructure
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(config.router, prefix=f"{settings.API_V1_PREFIX}/config", tags=["config"])
app.include_router(billing.router, prefix=f"{settings.API_V1_PREFIX}/billing", tags=["billing"])
app.include_router(webhooks.router, prefix=f"{settings.API_V1_PREFIX}/webhooks", tags=["webhooks"])
app.include_router(affiliates.router, prefix=f"{settings.API_V1_PREFIX}/affiliates", tags=["affiliates"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["admin"])
app.include_router(waitlist.router, prefix=f"{settings.API_V1_PREFIX}/waitlist", tags=["waitlist"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_PREFIX}", tags=["feedback"])

# Dating-specific routers
app.include_router(profile.router, prefix=f"{settings.API_V1_PREFIX}/profile", tags=["profile"])
app.include_router(compatibility.router, prefix=f"{settings.API_V1_PREFIX}/compatibility", tags=["compatibility"])
app.include_router(discovery.router, prefix=f"{settings.API_V1_PREFIX}/discovery", tags=["discovery"])
app.include_router(matches.router, prefix=f"{settings.API_V1_PREFIX}/matches", tags=["matches"])
app.include_router(messages.router, prefix=f"{settings.API_V1_PREFIX}/messages", tags=["messages"])
app.include_router(moderation.router, prefix=f"{settings.API_V1_PREFIX}/moderation", tags=["moderation"])

# Configure production logging on startup
if settings.ENVIRONMENT == "production":
    configure_production_logging()
    logger.info("Application started in PRODUCTION mode")
else:
    logger.info(f"Application started in {settings.ENVIRONMENT} mode")

@app.get("/")
async def root():
    return {
        "message": "SamePageDating API - Find Someone Who Wants The Same Things You Do",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "app_mode": settings.APP_MODE,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint - returns 200 if app is running"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@app.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check endpoint - checks all critical services.
    Use for monitoring dashboards and alerting.
    """
    checks = {
        "database": HealthCheck.check_database(db),
        "redis": HealthCheck.check_redis(),
        "stripe": HealthCheck.check_stripe(),
    }
    
    all_healthy = all(check.get("healthy", False) for check in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "environment": settings.ENVIRONMENT,
        "checks": checks
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
