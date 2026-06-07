"""
Unit tests for auth_service.py

Tests every authentication flow:
  - register_user: happy path, duplicate email
  - verify_email: valid token, invalid token, expired token
  - resend_verification: valid email, unknown email, already-verified
  - login_user: success, wrong password, unverified, inactive
  - request_password_reset / reset_password flow
  - update_profile / change_password
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from app.services import auth_service
from app.core.security import hash_password, verify_password, generate_secure_token
from app.models.user import User


# ─────────────────────────────────────────────────────────────────────────────
# register_user
# ─────────────────────────────────────────────────────────────────────────────
class TestRegisterUser:
    def test_creates_user_successfully(self, db):
        with patch("app.services.auth_service.send_verification_email"):
            user = auth_service.register_user(db, "new@example.com", "StrongPass1!")
        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.is_verified is False
        assert user.verification_token is not None

    def test_email_is_lowercased(self, db):
        with patch("app.services.auth_service.send_verification_email"):
            user = auth_service.register_user(db, "UPPER@EXAMPLE.COM", "StrongPass1!")
        assert user.email == "upper@example.com"

    def test_stores_full_name(self, db):
        with patch("app.services.auth_service.send_verification_email"):
            user = auth_service.register_user(db, "named@example.com", "StrongPass1!", full_name="Jane Doe")
        assert user.full_name == "Jane Doe"

    def test_stores_referral_code(self, db):
        with patch("app.services.auth_service.send_verification_email"):
            user = auth_service.register_user(db, "ref@example.com", "StrongPass1!", referral_code="ABC123")
        assert user.referred_by_code == "ABC123"

    def test_password_is_hashed(self, db):
        with patch("app.services.auth_service.send_verification_email"):
            user = auth_service.register_user(db, "hashed@example.com", "MySecret123!")
        assert user.hashed_password != "MySecret123!"
        assert verify_password("MySecret123!", user.hashed_password)

    def test_duplicate_email_raises_400(self, db, verified_user):
        from fastapi import HTTPException
        with patch("app.services.auth_service.send_verification_email"):
            with pytest.raises(HTTPException) as exc_info:
                auth_service.register_user(db, verified_user.email, "AnotherPass1!")
        assert exc_info.value.status_code == 400

    def test_verification_token_expires_in_future(self, db):
        with patch("app.services.auth_service.send_verification_email"):
            user = auth_service.register_user(db, "tokentest@example.com", "Pass123!")
        now = datetime.now(timezone.utc)
        expires = user.verification_token_expires
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        assert expires > now


# ─────────────────────────────────────────────────────────────────────────────
# verify_email
# ─────────────────────────────────────────────────────────────────────────────
class TestVerifyEmail:
    def test_verifies_with_correct_token(self, db, unverified_user):
        token = unverified_user.verification_token
        user = auth_service.verify_email(db, token)
        assert user.is_verified is True
        assert user.verification_token is None
        assert user.verification_token_expires is None

    def test_invalid_token_raises_400(self, db):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_email(db, "totally-invalid-token")
        assert exc_info.value.status_code == 400

    def test_expired_token_raises_400(self, db, unverified_user):
        from fastapi import HTTPException
        # Wind back expiry to the past
        unverified_user.verification_token_expires = datetime.now(timezone.utc) - timedelta(hours=1)
        db.flush()
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_email(db, unverified_user.verification_token)
        assert exc_info.value.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# resend_verification
# ─────────────────────────────────────────────────────────────────────────────
class TestResendVerification:
    def test_issues_new_token(self, db, unverified_user):
        old_token = unverified_user.verification_token
        with patch("app.services.auth_service.send_verification_email") as mock_send:
            auth_service.resend_verification(db, unverified_user.email)
        db.refresh(unverified_user)
        assert unverified_user.verification_token != old_token
        mock_send.assert_called_once()

    def test_unknown_email_silently_ignored(self, db):
        # Should NOT raise — prevents email enumeration
        auth_service.resend_verification(db, "nobody@example.com")

    def test_already_verified_silently_ignored(self, db, verified_user):
        with patch("app.services.auth_service.send_verification_email") as mock_send:
            auth_service.resend_verification(db, verified_user.email)
        mock_send.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# login_user
# ─────────────────────────────────────────────────────────────────────────────
class TestLoginUser:
    def test_returns_tokens_on_success(self, db, verified_user):
        result = auth_service.login_user(db, verified_user.email, "Password123!")
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["user"].id == verified_user.id

    def test_updates_last_login_at(self, db, verified_user):
        auth_service.login_user(db, verified_user.email, "Password123!")
        db.refresh(verified_user)
        assert verified_user.last_login_at is not None

    def test_wrong_password_raises_401(self, db, verified_user):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login_user(db, verified_user.email, "WrongPassword!")
        assert exc_info.value.status_code == 401

    def test_unknown_email_raises_401(self, db):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login_user(db, "doesnotexist@example.com", "Password123!")
        assert exc_info.value.status_code == 401

    def test_unverified_user_raises_403(self, db, unverified_user):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login_user(db, unverified_user.email, "Password123!")
        assert exc_info.value.status_code == 403

    def test_inactive_user_raises_403(self, db, verified_user):
        from fastapi import HTTPException
        verified_user.is_active = False
        db.flush()
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login_user(db, verified_user.email, "Password123!")
        assert exc_info.value.status_code == 403

    def test_email_case_insensitive_login(self, db, verified_user):
        # Should work regardless of email case
        result = auth_service.login_user(db, verified_user.email.upper(), "Password123!")
        assert result["user"].id == verified_user.id


# ─────────────────────────────────────────────────────────────────────────────
# Password reset flow
# ─────────────────────────────────────────────────────────────────────────────
class TestPasswordReset:
    def test_request_sets_reset_token(self, db, verified_user):
        with patch("app.services.auth_service.send_password_reset_email") as mock_send:
            auth_service.request_password_reset(db, verified_user.email)
        db.refresh(verified_user)
        assert verified_user.reset_token is not None
        assert verified_user.reset_token_expires is not None
        mock_send.assert_called_once()

    def test_request_unknown_email_silently_ignored(self, db):
        # Should NOT raise — prevents email enumeration
        with patch("app.services.auth_service.send_password_reset_email") as mock_send:
            auth_service.request_password_reset(db, "ghost@example.com")
        mock_send.assert_not_called()

    def test_reset_changes_password(self, db, verified_user):
        token = generate_secure_token()
        verified_user.reset_token = token
        verified_user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=2)
        db.flush()

        auth_service.reset_password(db, token, "NewPassword456!")
        db.refresh(verified_user)

        assert verify_password("NewPassword456!", verified_user.hashed_password)
        assert verified_user.reset_token is None

    def test_reset_invalid_token_raises_400(self, db):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_service.reset_password(db, "bad-token", "anything")
        assert exc_info.value.status_code == 400

    def test_reset_expired_token_raises_400(self, db, verified_user):
        from fastapi import HTTPException
        token = generate_secure_token()
        verified_user.reset_token = token
        verified_user.reset_token_expires = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.flush()

        with pytest.raises(HTTPException) as exc_info:
            auth_service.reset_password(db, token, "NewPass123!")
        assert exc_info.value.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# update_profile
# ─────────────────────────────────────────────────────────────────────────────
class TestUpdateProfile:
    def test_updates_full_name(self, db, verified_user):
        updated = auth_service.update_profile(db, verified_user, full_name="New Name")
        assert updated.full_name == "New Name"

    def test_none_name_does_not_overwrite(self, db, verified_user):
        verified_user.full_name = "Original Name"
        db.flush()
        updated = auth_service.update_profile(db, verified_user, full_name=None)
        assert updated.full_name == "Original Name"


# ─────────────────────────────────────────────────────────────────────────────
# change_password
# ─────────────────────────────────────────────────────────────────────────────
class TestChangePassword:
    def test_changes_password_with_correct_current(self, db, verified_user):
        auth_service.change_password(db, verified_user, "Password123!", "Brand_New_Pass1!")
        db.refresh(verified_user)
        assert verify_password("Brand_New_Pass1!", verified_user.hashed_password)

    def test_wrong_current_password_raises_400(self, db, verified_user):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            auth_service.change_password(db, verified_user, "WRONG_PASS!", "NewPass1!")
        assert exc_info.value.status_code == 400
