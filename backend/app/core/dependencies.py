from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Statuses that grant access to protected content
ACTIVE_SUBSCRIPTION_STATUSES = {"trialing", "active", "past_due"}


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_verified_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified.",
        )
    return user


def get_subscribed_user(user: User = Depends(get_verified_user)) -> User:
    """Requires subscription unless app mode is active_beta."""
    if user.is_admin:
        return user

    # In active beta mode, subscription is not required for any authenticated user.
    if settings.APP_MODE == "active_beta":
        return user
    
    # Otherwise, check for active subscription
    if user.subscription_status not in ACTIVE_SUBSCRIPTION_STATUSES:
        # In waitlist or active_beta mode, show beta access denied message
        if settings.APP_MODE in ("waitlist", "active_beta"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to the beta at this moment. Please contact support if you believe this is an error.",
            )
        # In production mode, require payment
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required.",
        )
    return user


def get_admin_user(user: User = Depends(get_verified_user)) -> User:
    """Requires is_admin=True."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return user
