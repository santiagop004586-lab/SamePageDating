"""
Unit tests for affiliate_service.py

Covers:
  - generate_referral_code: uniqueness guarantee
  - create_affiliate: happy path, idempotency
  - attribute_referral: happy path, unknown code, self-referral, duplicate
  - process_invoice_commission: happy path, idempotency, max_months limit, void
  - approve_due_commissions: batch approval after hold period
  - create_payout_batch / mark_batch_paid: full payout lifecycle
  - void_commission: decrements affiliate totals
"""
import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.services import affiliate_service
from app.models.affiliate import (
    Affiliate, CommissionLedger, PayoutBatch, AffiliateTaxProfile
)
from app.models.user import User
from app.core.security import hash_password


# ─────────────────────────────────────────────────────────────────────────────
# generate_referral_code
# ─────────────────────────────────────────────────────────────────────────────
class TestGenerateReferralCode:
    def test_returns_8_char_alphanumeric(self, db):
        code = affiliate_service.generate_referral_code(db)
        assert len(code) == 8
        assert code.isalnum()
        assert code == code.upper()

    def test_unique_codes(self, db):
        codes = {affiliate_service.generate_referral_code(db) for _ in range(20)}
        assert len(codes) == 20  # all different (statistically near-certain)


# ─────────────────────────────────────────────────────────────────────────────
# create_affiliate
# ─────────────────────────────────────────────────────────────────────────────
class TestCreateAffiliate:
    def test_creates_affiliate_record(self, db, affiliate_owner):
        aff = affiliate_service.create_affiliate(db, affiliate_owner)
        assert aff.id is not None
        assert aff.user_id == affiliate_owner.id
        assert aff.status == "active"
        assert len(aff.code) == 8

    def test_idempotent_second_call_returns_same(self, db, affiliate_owner):
        aff1 = affiliate_service.create_affiliate(db, affiliate_owner)
        aff2 = affiliate_service.create_affiliate(db, affiliate_owner)
        assert aff1.id == aff2.id
        assert aff1.code == aff2.code

    def test_uses_config_commission_pct(self, db, affiliate_owner):
        from app.core.config import settings
        aff = affiliate_service.create_affiliate(db, affiliate_owner)
        assert float(aff.commission_pct) == settings.AFFILIATE_COMMISSION_PCT

    def test_uses_config_hold_days(self, db, affiliate_owner):
        from app.core.config import settings
        aff = affiliate_service.create_affiliate(db, affiliate_owner)
        assert aff.hold_days == settings.AFFILIATE_HOLD_DAYS


# ─────────────────────────────────────────────────────────────────────────────
# attribute_referral
# ─────────────────────────────────────────────────────────────────────────────
class TestAttributeReferral:
    def test_attributes_correctly(self, db, active_affiliate, referred_customer):
        attr = affiliate_service.attribute_referral(db, referred_customer, active_affiliate.code)
        assert attr is not None
        assert attr.affiliate_id == active_affiliate.id
        assert attr.referred_user_id == referred_customer.id
        assert attr.status == "pending"

    def test_unknown_code_returns_none(self, db, referred_customer):
        result = affiliate_service.attribute_referral(db, referred_customer, "BADCODE!")
        assert result is None

    def test_self_referral_returns_none(self, db, active_affiliate, affiliate_owner):
        result = affiliate_service.attribute_referral(db, affiliate_owner, active_affiliate.code)
        assert result is None

    def test_duplicate_attribution_returns_existing(self, db, active_affiliate, referred_customer):
        first = affiliate_service.attribute_referral(db, referred_customer, active_affiliate.code)
        second = affiliate_service.attribute_referral(db, referred_customer, active_affiliate.code)
        assert first.id == second.id

    def test_paused_affiliate_returns_none(self, db, active_affiliate, referred_customer):
        active_affiliate.status = "paused"
        db.flush()
        result = affiliate_service.attribute_referral(db, referred_customer, active_affiliate.code)
        assert result is None


# ─────────────────────────────────────────────────────────────────────────────
# process_invoice_commission
# ─────────────────────────────────────────────────────────────────────────────
class TestProcessInvoiceCommission:
    def _create_commission(self, db, active_affiliate, attributed_referral, referred_customer,
                           invoice_id="inv_test001", amount=1999):
        return affiliate_service.process_invoice_commission(
            db,
            stripe_invoice_id=invoice_id,
            stripe_sub_id="sub_test001",
            stripe_customer_id=referred_customer.stripe_customer_id,
            amount_cents=amount,
        )

    def test_creates_commission_entry(self, db, active_affiliate, attributed_referral, referred_customer):
        entry = self._create_commission(db, active_affiliate, attributed_referral, referred_customer)
        assert entry is not None
        assert entry.invoice_amount_cents == 1999
        assert entry.status == "pending"
        assert entry.commission_amount_cents == int(1999 * float(active_affiliate.commission_pct) / 100)

    def test_hold_until_is_in_future(self, db, active_affiliate, attributed_referral, referred_customer):
        entry = self._create_commission(db, active_affiliate, attributed_referral, referred_customer)
        now = datetime.now(timezone.utc)
        hold = entry.hold_until
        if hold.tzinfo is None:
            hold = hold.replace(tzinfo=timezone.utc)
        assert hold > now

    def test_idempotent_same_invoice(self, db, active_affiliate, attributed_referral, referred_customer):
        entry1 = self._create_commission(db, active_affiliate, attributed_referral, referred_customer)
        entry2 = self._create_commission(db, active_affiliate, attributed_referral, referred_customer)
        assert entry1.id == entry2.id

    def test_zero_amount_returns_none(self, db, active_affiliate, attributed_referral, referred_customer):
        result = affiliate_service.process_invoice_commission(
            db, "inv_zero", "sub_zero", referred_customer.stripe_customer_id, 0
        )
        assert result is None

    def test_unknown_customer_returns_none(self, db):
        result = affiliate_service.process_invoice_commission(
            db, "inv_none", "sub_none", "cus_DOESNOTEXIST", 1999
        )
        assert result is None

    def test_marks_attribution_converted_on_first_payment(
        self, db, active_affiliate, attributed_referral, referred_customer
    ):
        self._create_commission(db, active_affiliate, attributed_referral, referred_customer)
        db.refresh(attributed_referral)
        assert attributed_referral.status == "converted"
        assert attributed_referral.first_payment_at is not None

    def test_max_months_enforced(self, db, active_affiliate, attributed_referral, referred_customer):
        # Set max_months = 1 on the affiliate
        active_affiliate.max_months = 1
        db.flush()

        # First invoice — should succeed
        e1 = affiliate_service.process_invoice_commission(
            db, "inv_m1", "sub_m", referred_customer.stripe_customer_id, 1999
        )
        assert e1 is not None

        # Second invoice for same sub — should be blocked
        e2 = affiliate_service.process_invoice_commission(
            db, "inv_m2", "sub_m", referred_customer.stripe_customer_id, 1999
        )
        assert e2 is None

    def test_multiple_invoices_counted_as_billing_cycles(
        self, db, active_affiliate, attributed_referral, referred_customer
    ):
        e1 = self._create_commission(
            db, active_affiliate, attributed_referral, referred_customer, invoice_id="inv_c1"
        )
        e2 = affiliate_service.process_invoice_commission(
            db, "inv_c2", "sub_test001", referred_customer.stripe_customer_id, 1999
        )
        assert e1.billing_cycle_number == 1
        assert e2.billing_cycle_number == 2


# ─────────────────────────────────────────────────────────────────────────────
# void_commission
# ─────────────────────────────────────────────────────────────────────────────
class TestVoidCommission:
    def test_sets_status_to_voided(self, db, active_affiliate, attributed_referral, referred_customer):
        entry = affiliate_service.process_invoice_commission(
            db, "inv_void", "sub_void", referred_customer.stripe_customer_id, 2999
        )
        voided = affiliate_service.void_commission(db, "inv_void", "refund requested")
        assert voided.status == "voided"
        assert voided.voided_at is not None

    def test_decrements_affiliate_total_earned(self, db, active_affiliate, attributed_referral, referred_customer):
        affiliate_service.process_invoice_commission(
            db, "inv_dec", "sub_dec", referred_customer.stripe_customer_id, 1000
        )
        db.refresh(active_affiliate)
        earned_before = active_affiliate.total_earned_cents

        affiliate_service.void_commission(db, "inv_dec", "test void")
        db.refresh(active_affiliate)

        assert active_affiliate.total_earned_cents < earned_before

    def test_already_paid_not_voided(self, db, active_affiliate, attributed_referral, referred_customer):
        entry = affiliate_service.process_invoice_commission(
            db, "inv_paid_v", "sub_paid_v", referred_customer.stripe_customer_id, 999
        )
        entry.status = "paid"
        db.flush()

        result = affiliate_service.void_commission(db, "inv_paid_v", "too late")
        # Should not change status — already paid
        assert result.status == "paid"


# ─────────────────────────────────────────────────────────────────────────────
# approve_due_commissions
# ─────────────────────────────────────────────────────────────────────────────
class TestApproveCommissions:
    def test_approves_past_hold_period(self, db, active_affiliate, attributed_referral, referred_customer):
        entry = affiliate_service.process_invoice_commission(
            db, "inv_app", "sub_app", referred_customer.stripe_customer_id, 1999
        )
        # Wind back hold_until
        entry.hold_until = datetime.now(timezone.utc) - timedelta(days=1)
        db.flush()

        approved_count = affiliate_service.approve_due_commissions(db)
        assert approved_count >= 1
        db.refresh(entry)
        assert entry.status == "approved"

    def test_does_not_approve_within_hold_period(self, db, active_affiliate, attributed_referral, referred_customer):
        entry = affiliate_service.process_invoice_commission(
            db, "inv_hold", "sub_hold", referred_customer.stripe_customer_id, 1999
        )
        # hold_until is already in the future
        affiliate_service.approve_due_commissions(db)
        db.refresh(entry)
        assert entry.status == "pending"


# ─────────────────────────────────────────────────────────────────────────────
# Payout batch lifecycle
# ─────────────────────────────────────────────────────────────────────────────
class TestPayoutBatch:
    def _setup_approved_commission(self, db, active_affiliate, attributed_referral, referred_customer):
        entry = affiliate_service.process_invoice_commission(
            db, "inv_batch", "sub_batch", referred_customer.stripe_customer_id, 5000
        )
        entry.status = "approved"
        entry.hold_until = datetime.now(timezone.utc) - timedelta(days=1)
        db.flush()
        return entry

    def test_create_batch_groups_approved_commissions(
        self, db, active_affiliate, attributed_referral, referred_customer
    ):
        self._setup_approved_commission(db, active_affiliate, attributed_referral, referred_customer)

        now = datetime.now(timezone.utc)
        batch = affiliate_service.create_payout_batch(
            db,
            affiliate_id=active_affiliate.id,
            period_start=now - timedelta(days=30),
            period_end=now,
        )
        assert batch.commission_count >= 1
        assert batch.total_amount_cents > 0
        assert batch.status == "draft"

    def test_mark_batch_paid_updates_status(
        self, db, active_affiliate, attributed_referral, referred_customer
    ):
        self._setup_approved_commission(db, active_affiliate, attributed_referral, referred_customer)

        now = datetime.now(timezone.utc)
        batch = affiliate_service.create_payout_batch(
            db,
            affiliate_id=active_affiliate.id,
            period_start=now - timedelta(days=30),
            period_end=now,
        )
        paid_batch = affiliate_service.mark_batch_paid(db, batch.id, "PayPal-TX-123")
        assert paid_batch.status == "paid"
        assert paid_batch.payout_reference == "PayPal-TX-123"
        assert paid_batch.paid_at is not None

    def test_paid_commissions_have_paid_status(
        self, db, active_affiliate, attributed_referral, referred_customer
    ):
        entry = self._setup_approved_commission(db, active_affiliate, attributed_referral, referred_customer)

        now = datetime.now(timezone.utc)
        batch = affiliate_service.create_payout_batch(
            db,
            affiliate_id=active_affiliate.id,
            period_start=now - timedelta(days=30),
            period_end=now,
        )
        affiliate_service.mark_batch_paid(db, batch.id, "ref-xyz")
        db.refresh(entry)
        assert entry.status == "paid"
        assert entry.paid_at is not None

    def test_mark_paid_updates_affiliate_total_paid(
        self, db, active_affiliate, attributed_referral, referred_customer
    ):
        entry = self._setup_approved_commission(db, active_affiliate, attributed_referral, referred_customer)
        paid_before = active_affiliate.total_paid_cents

        now = datetime.now(timezone.utc)
        batch = affiliate_service.create_payout_batch(
            db,
            affiliate_id=active_affiliate.id,
            period_start=now - timedelta(days=30),
            period_end=now,
        )
        affiliate_service.mark_batch_paid(db, batch.id, "ref-totals")
        db.refresh(active_affiliate)
        assert active_affiliate.total_paid_cents == paid_before + batch.total_amount_cents

    def test_mark_paid_invalid_batch_raises(self, db):
        with pytest.raises(ValueError):
            affiliate_service.mark_batch_paid(db, 999999, "ref-bad")
