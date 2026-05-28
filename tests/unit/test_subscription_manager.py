"""Tests for the subscription and licensing engine."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from core.subscription_manager import (
    FeatureGateError,
    LicenseStatus,
    LicenseValidationError,
    SubscriptionManager,
    SubscriptionTier,
)


@pytest.fixture
def manager(tmp_path: Path) -> SubscriptionManager:
    # Each test gets a fresh keypair so the manager can both sign and verify.
    priv = Ed25519PrivateKey.generate()
    priv_b64 = base64.b64encode(
        priv.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )
    ).decode()
    pub_b64 = base64.b64encode(
        priv.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
    ).decode()
    return SubscriptionManager(
        data_dir=tmp_path,
        public_key_b64=pub_b64,
        private_key_b64=priv_b64,
    )


class TestFreeTier:
    def test_default_tier_is_free(self, manager: SubscriptionManager) -> None:
        assert manager.current_tier == SubscriptionTier.FREE

    def test_free_has_basic_features(self, manager: SubscriptionManager) -> None:
        assert manager.has_feature("basic_tasks")
        assert manager.has_feature("mood_logging")
        assert manager.has_feature("breathing")

    def test_free_lacks_pro_features(self, manager: SubscriptionManager) -> None:
        assert not manager.has_feature("pdf_reports")
        assert not manager.has_feature("weekly_insights")
        assert not manager.has_feature("values_tracker")

    def test_license_info_free(self, manager: SubscriptionManager) -> None:
        info = manager.license_info
        assert info.tier == SubscriptionTier.FREE
        assert info.status == LicenseStatus.INVALID


class TestLicenseKeyValidation:
    def test_generate_and_activate_pro(self, manager: SubscriptionManager) -> None:
        key = manager.generate_key(SubscriptionTier.PRO, days=30)
        info = manager.activate_license(key)
        assert info.tier == SubscriptionTier.PRO
        assert info.status == LicenseStatus.VALID
        assert manager.has_feature("mood_analytics")
        assert manager.has_feature("energy_predictor")
        assert not manager.has_feature("pdf_reports")

    def test_generate_and_activate_clinical(self, manager: SubscriptionManager) -> None:
        key = manager.generate_key(SubscriptionTier.PREMIUM, days=30)
        manager.activate_license(key)
        assert manager.current_tier == SubscriptionTier.PREMIUM
        assert manager.has_feature("pdf_reports")
        assert manager.has_feature("values_radar")
        assert manager.has_feature("clinician_sharing")

    def test_invalid_key_format(self, manager: SubscriptionManager) -> None:
        with pytest.raises(LicenseValidationError):
            manager.activate_license("not-a-valid-key")

    def test_empty_key(self, manager: SubscriptionManager) -> None:
        with pytest.raises(LicenseValidationError):
            manager.activate_license("")

    def test_expired_key(self, manager: SubscriptionManager) -> None:
        key = manager.generate_key(SubscriptionTier.PRO, days=-1)
        with pytest.raises(LicenseValidationError, match="expired"):
            manager.activate_license(key)

    def test_tampered_key_fails_hmac(self, manager: SubscriptionManager) -> None:
        key = manager.generate_key(SubscriptionTier.PRO, days=30)
        tampered = key[:-4] + "BAD1"
        with pytest.raises(LicenseValidationError, match="invalid"):
            manager.activate_license(tampered)

    def test_deactivate_reverts_to_free(self, manager: SubscriptionManager) -> None:
        key = manager.generate_key(SubscriptionTier.PRO, days=30)
        manager.activate_license(key)
        manager.deactivate()
        assert manager.current_tier == SubscriptionTier.FREE


class TestFeatureGating:
    def test_require_feature_allows(self, manager: SubscriptionManager) -> None:
        assert manager.require_feature("basic_tasks") is True

    def test_require_feature_blocks(self, manager: SubscriptionManager) -> None:
        with pytest.raises(FeatureGateError):
            manager.require_feature("pdf_reports")

    def test_gated_features_dict(self, manager: SubscriptionManager) -> None:
        gated = manager.gated_features()
        assert gated["basic_tasks"] is True
        assert gated["pdf_reports"] is False
        assert gated["pdf_reports"] is False


class TestTrial:
    def test_start_trial(self, manager: SubscriptionManager) -> None:
        info = manager.start_trial()
        assert info.status == LicenseStatus.TRIAL
        assert manager.current_tier == SubscriptionTier.PREMIUM
        assert manager.trial_days_remaining in (13, 14)

    def test_trial_has_all_features(self, manager: SubscriptionManager) -> None:
        manager.start_trial()
        assert manager.has_feature("pdf_reports")
        assert manager.has_feature("wearable_sync")

    def test_trial_cannot_restart_while_active(self, manager: SubscriptionManager) -> None:
        manager.start_trial()
        with pytest.raises(LicenseValidationError, match="already active"):
            manager.start_trial()

    def test_trial_cannot_restart_after_ended(self, manager: SubscriptionManager) -> None:
        manager.start_trial()
        manager.end_trial()
        with pytest.raises(LicenseValidationError, match="already been used"):
            manager.start_trial()

    def test_trial_cannot_start_with_license(self, manager: SubscriptionManager) -> None:
        key = manager.generate_key(SubscriptionTier.PRO, days=30)
        manager.activate_license(key)
        with pytest.raises(LicenseValidationError, match="Already have"):
            manager.start_trial()

    def test_trial_days_remaining_zero_when_expired(self, manager: SubscriptionManager) -> None:
        manager.start_trial()
        # Simulate expiration by backdating trial start
        manager._state["trial_started_at"] = (
            datetime.now() - timedelta(days=manager.TRIAL_DAYS + 1)
        ).isoformat()
        manager._save_state()
        assert manager.trial_days_remaining == 0
        assert manager.current_tier == SubscriptionTier.FREE

    def test_trial_exact_boundary_not_active(self, manager: SubscriptionManager) -> None:
        manager.start_trial()
        # Set start exactly TRIAL_DAYS ago
        manager._state["trial_started_at"] = (
            datetime.now() - timedelta(days=manager.TRIAL_DAYS)
        ).isoformat()
        manager._save_state()
        # At the exact boundary, trial should not be active
        assert not manager._is_trial_active()
