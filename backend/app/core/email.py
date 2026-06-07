import logging
from app.core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Ensure INFO level


def _send(to_email: str, subject: str, html_body: str) -> bool:
    """Send an email via Resend. Falls back to logging when API key is not configured."""
    if not settings.RESEND_API_KEY:
        logger.info(f"[EMAIL - no RESEND_API_KEY configured] To: {to_email} | Subject: {subject}")
        logger.info(f"[EMAIL BODY]\n{html_body}")
        print(f"⚠️ [EMAIL] No RESEND_API_KEY configured - email NOT sent", flush=True)
        return True

    logger.info(f"[EMAIL] Attempting to send to: {to_email} | Subject: {subject}")
    print(f"📤 [RESEND] Calling Resend API for {to_email} | Subject: {subject}", flush=True)
    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY
        result = resend.Emails.send({
            "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM}>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        })
        logger.info(f"[EMAIL] Successfully sent to {to_email}. Result: {result}")
        print(f"✅ [RESEND] Email sent successfully! Resend ID: {result.get('id', 'unknown')}", flush=True)
        return True
    except Exception as e:
        logger.error(f"[EMAIL] Resend email exception to {to_email}: {e}")
        print(f"❌ [RESEND] Exception: {e}", flush=True)
        return False


def send_verification_email(to_email: str, token: str) -> bool:
    url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto">
      <h2 style="color:#1d4ed8">Verify your email</h2>
      <p>Thanks for signing up for <strong>Find Best Rentals</strong>!</p>
      <p>Click the button below to verify your email address. This link expires in 24 hours.</p>
      <a href="{url}" style="display:inline-block;padding:12px 24px;background:#1d4ed8;color:white;border-radius:6px;text-decoration:none;font-weight:bold;margin:16px 0">
        Verify Email
      </a>
      <p style="color:#6b7280;font-size:13px">Or paste this link: {url}</p>
    </div>
    """
    return _send(to_email, "Verify your Find Best Rentals account", html)


def send_password_reset_email(to_email: str, token: str) -> bool:
    url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto">
      <h2 style="color:#1d4ed8">Reset your password</h2>
      <p>We received a request to reset the password for your <strong>Find Best Rentals</strong> account.</p>
      <p>Click below to set a new password. This link expires in 2 hours.</p>
      <a href="{url}" style="display:inline-block;padding:12px 24px;background:#1d4ed8;color:white;border-radius:6px;text-decoration:none;font-weight:bold;margin:16px 0">
        Reset Password
      </a>
      <p style="color:#6b7280;font-size:13px">If you didn't request this, you can safely ignore this email.</p>
    </div>
    """
    return _send(to_email, "Reset your Find Best Rentals password", html)


def send_subscription_welcome_email(to_email: str, trial_end_date: str) -> bool:
    """Send welcome email when a subscription is created with trial information."""
    dashboard_url = f"{settings.FRONTEND_URL}/dashboard"
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto">
      <h2 style="color:#1d4ed8">🎉 Welcome to Find Best Rentals!</h2>
      <p>Thanks for subscribing! Your <strong>30-day free trial</strong> has started.</p>
      
      <div style="background:#f3f4f6;border-left:4px solid #1d4ed8;padding:16px;margin:20px 0">
        <p style="margin:0;font-weight:bold;color:#1f2937">Trial Details:</p>
        <p style="margin:8px 0 0 0;color:#4b5563">• Your trial ends on <strong>{trial_end_date}</strong></p>
        <p style="margin:4px 0 0 0;color:#4b5563">• After trial: <strong>$29.99/month</strong></p>
        <p style="margin:4px 0 0 0;color:#4b5563">• Cancel anytime before trial ends - no charge</p>
      </div>

      <p><strong>What you get:</strong></p>
      <ul style="color:#4b5563;line-height:1.8">
        <li>Access to exclusive Section 8 deals nationwide</li>
        <li>Automated property analysis & valuation</li>
        <li>Real-time FMR and rent estimates</li>
        <li>Comprehensive rehab cost calculations</li>
      </ul>

      <a href="{dashboard_url}" style="display:inline-block;padding:12px 24px;background:#1d4ed8;color:white;border-radius:6px;text-decoration:none;font-weight:bold;margin:16px 0">
        View Properties Now
      </a>

      <p style="color:#6b7280;font-size:13px;margin-top:24px">Questions? Reply to this email or visit our FAQ section.</p>
      <p style="color:#6b7280;font-size:13px">You can manage your subscription at any time from your account settings.</p>
    </div>
    """
    return _send(to_email, "Welcome to Find Best Rentals - Your Free Trial Has Started!", html)


def send_subscription_cancellation_email(to_email: str, access_end_date: str) -> bool:
    """Send cancellation confirmation when a subscription is cancelled."""
    subscribe_url = f"{settings.FRONTEND_URL}/subscribe"
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto">
      <h2 style="color:#4b5563">Your subscription has been cancelled</h2>
      <p>We've successfully cancelled your <strong>Find Best Rentals</strong> subscription.</p>
      
      <div style="background:#fef3c7;border-left:4px solid #f59e0b;padding:16px;margin:20px 0">
        <p style="margin:0;font-weight:bold;color:#92400e">Access Information:</p>
        <p style="margin:8px 0 0 0;color:#78350f">You'll continue to have full access until <strong>{access_end_date}</strong></p>
        <p style="margin:8px 0 0 0;color:#78350f;font-size:13px">After this date, you won't be charged and your access will end.</p>
      </div>

      <p>We're sorry to see you go! If there's anything we could have done better, we'd love to hear your feedback.</p>

      <p><strong>Changed your mind?</strong></p>
      <p>You can resubscribe anytime to regain full access to all features.</p>

      <a href="{subscribe_url}" style="display:inline-block;padding:12px 24px;background:#1d4ed8;color:white;border-radius:6px;text-decoration:none;font-weight:bold;margin:16px 0">
        Resubscribe
      </a>

      <p style="color:#6b7280;font-size:13px;margin-top:24px">Thank you for being part of Find Best Rentals. We hope to see you again!</p>
    </div>
    """
    return _send(to_email, "Your Find Best Rentals Subscription Has Been Cancelled", html)
