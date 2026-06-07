"""
Fraud detection service for affiliate system
Detects suspicious patterns like IP matches, rapid conversions, and velocity breaches
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.affiliate import Affiliate, FraudSignal, ReferralAttribution
from app.models.user import User

logger = logging.getLogger(__name__)


def check_ip_match(
    db: Session, 
    affiliate: Affiliate, 
    referred_user: User,
    attribution: ReferralAttribution
) -> Optional[FraudSignal]:
    """
    Check if affiliate and referred user signed up from the same IP address.
    Creates high-severity fraud signal if IPs match.
    
    Returns:
        FraudSignal if fraud detected, None otherwise
    """
    # Get affiliate's user record to check their signup IP
    affiliate_user = db.query(User).filter(User.id == affiliate.user_id).first()
    
    if not affiliate_user or not affiliate_user.signup_ip:
        return None  # Can't check if affiliate IP not recorded
    
    if not referred_user.signup_ip:
        return None  # Can't check if referred user IP not recorded
    
    # Check if IPs match
    if affiliate_user.signup_ip == referred_user.signup_ip:
        logger.warning(
            f"IP match detected: affiliate {affiliate.id} and referred user {referred_user.id} "
            f"both signed up from {referred_user.signup_ip}"
        )
        
        # Check if signal already exists for this combination
        existing = db.query(FraudSignal).filter(
            FraudSignal.affiliate_id == affiliate.id,
            FraudSignal.referred_user_id == referred_user.id,
            FraudSignal.signal_type == "ip_match"
        ).first()
        
        if existing:
            return existing  # Already flagged
        
        # Create fraud signal
        signal = FraudSignal(
            affiliate_id=affiliate.id,
            referred_user_id=referred_user.id,
            signal_type="ip_match",
            severity="high",
            metadata={
                "affiliate_ip": affiliate_user.signup_ip,
                "user_ip": referred_user.signup_ip,
                "match_confidence": 1.0,
                "attribution_id": attribution.id if attribution else None
            }
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
        
        logger.info(f"Created fraud signal {signal.id} for IP match")
        return signal
    
    return None


def check_rapid_conversion(
    db: Session, 
    affiliate_id: int,
    hours: int = 24,
    threshold: int = 5
) -> Optional[FraudSignal]:
    """
    Check if affiliate has too many conversions in a short time period.
    Creates high-severity fraud signal if threshold exceeded.
    
    Args:
        db: Database session
        affiliate_id: Affiliate ID to check
        hours: Time window in hours (default 24)
        threshold: Max conversions allowed in window (default 5)
    
    Returns:
        FraudSignal if fraud detected, None otherwise
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Count converted attributions in the time window
    conversion_count = db.query(func.count(ReferralAttribution.id)).filter(
        ReferralAttribution.affiliate_id == affiliate_id,
        ReferralAttribution.status == "converted",
        ReferralAttribution.first_payment_at >= since
    ).scalar()
    
    if conversion_count > threshold:
        logger.warning(
            f"Rapid conversion detected: affiliate {affiliate_id} has {conversion_count} "
            f"conversions in the last {hours} hours (threshold: {threshold})"
        )
        
        # Check if we already flagged this recently
        recent_signal = db.query(FraudSignal).filter(
            FraudSignal.affiliate_id == affiliate_id,
            FraudSignal.signal_type == "rapid_conversion",
            FraudSignal.created_at >= since
        ).first()
        
        if recent_signal:
            # Update metadata with latest count
            recent_signal.signal_metadata["conversions_24h"] = conversion_count
            db.commit()
            return recent_signal
        
        # Create new fraud signal
        signal = FraudSignal(
            affiliate_id=affiliate_id,
            signal_type="rapid_conversion",
            severity="high",
            metadata={
                "conversions_24h": conversion_count,
                "threshold": threshold,
                "window_hours": hours,
                "detected_at": datetime.now(timezone.utc).isoformat()
            }
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
        
        logger.info(f"Created fraud signal {signal.id} for rapid conversion")
        return signal
    
    return None


def check_velocity_breach(
    db: Session,
    affiliate_id: int,
    hours: int = 24,
    threshold: int = 10
) -> Optional[FraudSignal]:
    """
    Check if affiliate has too many signups (not necessarily paid) in a short time.
    Creates medium-severity fraud signal if threshold exceeded.
    
    Args:
        db: Database session
        affiliate_id: Affiliate ID to check
        hours: Time window in hours (default 24)
        threshold: Max signups allowed in window (default 10)
    
    Returns:
        FraudSignal if fraud detected, None otherwise
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Count all attributions (signups) in the time window
    signup_count = db.query(func.count(ReferralAttribution.id)).filter(
        ReferralAttribution.affiliate_id == affiliate_id,
        ReferralAttribution.attributed_at >= since
    ).scalar()
    
    if signup_count > threshold:
        logger.warning(
            f"Velocity breach detected: affiliate {affiliate_id} has {signup_count} "
            f"signups in the last {hours} hours (threshold: {threshold})"
        )
        
        # Check if we already flagged this recently
        recent_signal = db.query(FraudSignal).filter(
            FraudSignal.affiliate_id == affiliate_id,
            FraudSignal.signal_type == "velocity_breach",
            FraudSignal.created_at >= since
        ).first()
        
        if recent_signal:
            # Update metadata with latest count
            recent_signal.signal_metadata["signups_24h"] = signup_count
            db.commit()
            return recent_signal
        
        # Create new fraud signal
        signal = FraudSignal(
            affiliate_id=affiliate_id,
            signal_type="velocity_breach",
            severity="medium",
            metadata={
                "signups_24h": signup_count,
                "threshold": threshold,
                "window_hours": hours,
                "detected_at": datetime.now(timezone.utc).isoformat()
            }
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
        
        logger.info(f"Created fraud signal {signal.id} for velocity breach")
        return signal
    
    return None


def calculate_risk_score(db: Session, affiliate_id: int) -> int:
    """
    Calculate a 0-100 risk score for an affiliate based on unresolved fraud signals.
    
    Scoring:
    - High severity: 40 points each
    - Medium severity: 20 points each
    - Low severity: 10 points each
    
    Returns:
        Risk score (0-100, capped at 100)
    """
    signals = db.query(FraudSignal).filter(
        FraudSignal.affiliate_id == affiliate_id,
        FraudSignal.resolved == False
    ).all()
    
    score = 0
    for signal in signals:
        if signal.severity == "high":
            score += 40
        elif signal.severity == "medium":
            score += 20
        elif signal.severity == "low":
            score += 10
    
    return min(score, 100)  # Cap at 100


def should_block_payout(db: Session, affiliate_id: int, risk_threshold: int = 75) -> bool:
    """
    Determine if an affiliate's payout should be blocked due to fraud risk.
    
    Args:
        db: Database session
        affiliate_id: Affiliate ID to check
        risk_threshold: Minimum risk score to block (default 75)
    
    Returns:
        True if payout should be blocked, False otherwise
    """
    risk_score = calculate_risk_score(db, affiliate_id)
    
    if risk_score >= risk_threshold:
        logger.warning(
            f"Blocking payout for affiliate {affiliate_id} due to high risk score: {risk_score}"
        )
        return True
    
    # Also block if there are any unresolved high-severity signals
    high_severity_count = db.query(func.count(FraudSignal.id)).filter(
        FraudSignal.affiliate_id == affiliate_id,
        FraudSignal.severity == "high",
        FraudSignal.resolved == False
    ).scalar()
    
    if high_severity_count > 0:
        logger.warning(
            f"Blocking payout for affiliate {affiliate_id} due to {high_severity_count} "
            f"unresolved high-severity fraud signals"
        )
        return True
    
    return False


def run_all_fraud_checks(
    db: Session,
    affiliate: Affiliate,
    referred_user: User,
    attribution: ReferralAttribution
) -> list[FraudSignal]:
    """
    Run all fraud detection checks for a new referral.
    Returns list of fraud signals detected (empty if clean).
    """
    signals = []
    
    # Check IP match
    ip_signal = check_ip_match(db, affiliate, referred_user, attribution)
    if ip_signal:
        signals.append(ip_signal)
    
    # Check rapid conversion (only if this is a paid conversion)
    if attribution.status == "converted" and attribution.first_payment_at:
        rapid_signal = check_rapid_conversion(db, affiliate.id)
        if rapid_signal:
            signals.append(rapid_signal)
    
    # Check velocity breach (signups)
    velocity_signal = check_velocity_breach(db, affiliate.id)
    if velocity_signal:
        signals.append(velocity_signal)
    
    return signals
