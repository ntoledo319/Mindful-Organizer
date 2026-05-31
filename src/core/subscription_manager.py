"""
Subscription and licensing engine for Mindful Organizer.

Handles tier management (Free / Pro / Premium), license key validation,
feature gating, and trial tracking. All enforcement is local — the app
works offline, and license keys are validated cryptographically without
phoning home on every launch.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

logger = logging.getLogger(__name__)

# Ed25519 verification key for license signatures. Public-by-design — embedding
# this in source is safe. The private signing key lives only on the build/release
# host and in MINDFUL_LICENSE_PRIVATE_KEY env var when issuing licenses.
_PUBLIC_KEY_B64 = "eukkxUxlPR4XqKpD2KQp84Hk+UZPZ/+SvuX7QAidQjk="

from core.paths import get_data_dir as _get_data_dir  # noqa: E402

DATA_DIR = _get_data_dir(create=False)
LICENSE_FILE = DATA_DIR / "license.json"


# ---------------------------------------------------------------------------
# Enums & dataclasses
# ---------------------------------------------------------------------------


class SubscriptionTier(Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class LicenseStatus(Enum):
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    TRIAL = "trial"


@dataclass
class LicenseInfo:
    tier: SubscriptionTier
    status: LicenseStatus
    expires_at: datetime | None = None
    activated_at: datetime | None = None
    license_key: str = ""
    features: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Feature registry
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Feature tier map (researched against Bearable, Daylio, eMoods, Sanvello)
#
# FREE  = habit-building layer. Must be genuinely usable long-term.
# PRO   = insight layer. The "aha moment" after 2-3 weeks of data.
# PREMIUM = advanced insights, beautiful reports, and sharing.
# ---------------------------------------------------------------------------

FEATURES_BY_TIER: dict[SubscriptionTier, set[str]] = {
    SubscriptionTier.FREE: {
        # Core tracking — unlimited, always free (ethical + habit-forming)
        "basic_tasks",
        "mood_logging",
        "diary_card",
        "sleep_logging",
        "medication_logging",
        "journal_basic",
        # Therapeutic exercises — core mental health tools stay free
        "breathing",
        "grounding",
        "crisis_plan",
        "panic_tracker",
        "erp_tracker",
        "meditation_basic",
        # Utilities
        "file_organizer",
        # Limited view
        "two_themes",
        "seven_day_history",
        "basic_dashboard",
        "basic_medication_reminders",
        # Automation — awareness layer (suggestions only, no system changes)
        "basic_automation",
    },
    SubscriptionTier.PRO: {
        # Everything from FREE
        "basic_tasks",
        "mood_logging",
        "diary_card",
        "sleep_logging",
        "medication_logging",
        "journal_basic",
        "breathing",
        "grounding",
        "crisis_plan",
        "panic_tracker",
        "erp_tracker",
        "meditation_basic",
        "file_organizer",
        # Insight & personalization
        "all_themes",
        "unlimited_history",
        "mood_analytics",
        "energy_predictor",
        "journal_analysis",
        "smart_notifications",
        "calendar_sync",
        "values_tracker",
        "gamification",
        "auto_updater",
        "unlimited_medication_reminders",
        "weekly_insights",
        "data_export",
        "full_dashboard",
        # Automation layer — execute system changes + autonomous mode
        "basic_automation",
        "system_actions",
        "manual_focus_mode",
        "display_adaptation",
        "system_tray",
        "global_hotkeys",
        "autonomous_mode",
    },
    SubscriptionTier.PREMIUM: {
        # Everything from PRO (and by extension FREE)
        "basic_tasks",
        "mood_logging",
        "sleep_logging",
        "medication_logging",
        "journal_basic",
        "breathing",
        "grounding",
        "crisis_plan",
        "panic_tracker",
        "erp_tracker",
        "meditation_basic",
        "file_organizer",
        "all_themes",
        "unlimited_history",
        "mood_analytics",
        "energy_predictor",
        "journal_analysis",
        "smart_notifications",
        "calendar_sync",
        "values_tracker",
        "gamification",
        "auto_updater",
        "unlimited_medication_reminders",
        "weekly_insights",
        "data_export",
        "full_dashboard",
        "basic_automation",
        "system_actions",
        "manual_focus_mode",
        "display_adaptation",
        "system_tray",
        "global_hotkeys",
        "autonomous_mode",
        # Automation Premium
        "custom_rules",
        "automation_analytics",
        "scheduled_focus_blocks",
        "multiple_automation_profiles",
        "advanced_system_integration",
        # Premium magic
        "pdf_reports",
        "shareable_reports",
        "medication_heatmap",
        "values_radar",
        "clinician_sharing",
        "onboarding_analytics",
        "priority_support",
        "wearable_sync",
    },
}

# Trial = full Premium experience for 14 days
TRIAL_FEATURES = FEATURES_BY_TIER[SubscriptionTier.PREMIUM]

# User-friendly feature names for upsell dialogs
FEATURE_DISPLAY_NAMES: dict[str, str] = {
    "all_themes": "All 8 Condition-Aware Themes",
    "unlimited_history": "Unlimited History & Trends",
    "mood_analytics": "Mood Trend Analytics",
    "energy_predictor": "Energy Forecasting",
    "journal_analysis": "Journal Sentiment & Distortion Analysis",
    "smart_notifications": "Smart Context-Aware Notifications",
    "calendar_sync": "Calendar Sync (ICS Export)",
    "values_tracker": "Weekly Values Review",
    "gamification": "Achievements & Gamification",
    "auto_updater": "Automatic Updates",
    "unlimited_medication_reminders": "Unlimited Medication Reminders",
    "weekly_insights": "Weekly Insights Reports",
    "data_export": "Data Export (JSON/CSV)",
    "full_dashboard": "Full Dashboard with Briefing & Forecasts",
    "diary_card": "DBT Diary Card Tracking",
    "pdf_reports": "Personal Wellness Reports with Charts",
    "shareable_reports": "Shareable Web Reports",
    "medication_heatmap": "Medication Adherence Heatmaps",
    "values_radar": "Values Alignment Radar Charts",
    "clinician_sharing": "Share Reports with Your Clinician",
    "onboarding_analytics": "Advanced Usage Analytics",
    "priority_support": "Priority Support",
    "wearable_sync": "Wearable Integration (Apple Health, Fitbit)",
    "basic_automation": "Basic System Automation (Suggestions + Manual Triggers)",
    "manual_focus_mode": "Manual Focus Mode",
    "display_adaptation": "Adaptive Display (Brightness, Night Shift, Themes)",
    "system_tray": "System Tray Quick Actions",
    "global_hotkeys": "Global Keyboard Shortcuts",
    "autonomous_mode": "Autonomous Automation (Auto-Execute Rules)",
    "custom_rules": "Custom Automation Rule Builder",
    "automation_analytics": "Automation Effectiveness Analytics",
    "scheduled_focus_blocks": "Scheduled Focus Blocks",
    "multiple_automation_profiles": "Multiple Automation Profiles",
    "advanced_system_integration": "Advanced System Integration",
}


# ---------------------------------------------------------------------------
# SubscriptionManager
# ---------------------------------------------------------------------------


class SubscriptionManager:
    """Manages subscription state, license validation, and feature access."""

    TRIAL_DAYS = 14

    def __init__(
        self,
        data_dir: Path | None = None,
        public_key_b64: str | None = None,
        private_key_b64: str | None = None,
    ) -> None:
        """Create a SubscriptionManager.

        public_key_b64 / private_key_b64 are for testing only. In production,
        the public key is the embedded constant and the private key is held by
        the issuer (loaded from MINDFUL_LICENSE_PRIVATE_KEY when issuing).
        """
        self._data_dir = data_dir or DATA_DIR
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._license_file = self._data_dir / "license.json"
        self._state: dict[str, Any] = {}

        pub_b64 = public_key_b64 or _PUBLIC_KEY_B64
        self._public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(pub_b64))
        self._private_key_b64 = private_key_b64  # set in tests / issuer tools

        self._load_state()

    # -- persistence -------------------------------------------------------

    def _load_state(self) -> None:
        if self._license_file.exists():
            try:
                self._state = json.loads(self._license_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._state = {}
        else:
            self._state = {}

    def _save_state(self) -> None:
        try:
            self._license_file.write_text(
                json.dumps(self._state, indent=2, default=str), encoding="utf-8"
            )
        except OSError:
            logger.exception("Failed to save license state")

    # -- tier detection ----------------------------------------------------

    @property
    def current_tier(self) -> SubscriptionTier:
        """Return the effective subscription tier."""
        if self._has_valid_license():
            tier_str = self._state.get("tier", "free")
            try:
                return SubscriptionTier(tier_str)
            except ValueError:
                return SubscriptionTier.FREE
        if self._is_trial_active():
            return SubscriptionTier.PREMIUM  # Trial = all features
        return SubscriptionTier.FREE

    @property
    def license_info(self) -> LicenseInfo:
        """Return a human-readable license summary."""
        tier = self.current_tier
        if self._has_valid_license():
            return LicenseInfo(
                tier=tier,
                status=LicenseStatus.VALID,
                expires_at=self._parse_dt(self._state.get("expires_at")),
                activated_at=self._parse_dt(self._state.get("activated_at")),
                license_key=self._state.get("license_key", ""),
                features=sorted(FEATURES_BY_TIER.get(tier, set())),
            )
        if self._is_trial_active():
            return LicenseInfo(
                tier=SubscriptionTier.PREMIUM,
                status=LicenseStatus.TRIAL,
                expires_at=self._trial_end(),
                activated_at=self._trial_start(),
                features=sorted(TRIAL_FEATURES),
            )
        return LicenseInfo(
            tier=SubscriptionTier.FREE,
            status=LicenseStatus.INVALID,
            features=sorted(FEATURES_BY_TIER[SubscriptionTier.FREE]),
        )

    # -- feature gating ----------------------------------------------------

    def has_feature(self, feature: str) -> bool:
        """Check if the current subscription includes a feature."""
        return feature in FEATURES_BY_TIER.get(self.current_tier, set())

    def require_feature(self, feature: str) -> bool:
        """Raise FeatureGateError if the feature is not available."""
        if not self.has_feature(feature):
            raise FeatureGateError(
                f"'{feature}' requires {self._upgrade_target().value.upper()}. "
                f"Please upgrade your subscription."
            )
        return True

    def gated_features(self) -> dict[str, bool]:
        """Return a dict of all features and whether they are enabled."""
        all_features: set[str] = set()
        for feats in FEATURES_BY_TIER.values():
            all_features |= feats
        return {f: self.has_feature(f) for f in sorted(all_features)}

    # -- license key operations --------------------------------------------

    def activate_license(self, license_key: str) -> LicenseInfo:
        """Validate and activate a license key.

        The key format is ``TIER:UNIX_TS:RANDOM:HMAC``.
        """
        license_key = license_key.strip()
        if not license_key:
            raise LicenseValidationError("License key is empty.")

        parts = license_key.split(":")
        if len(parts) != 4:
            raise LicenseValidationError("Invalid license key format.")

        tier_str, ts_str, rand, signature = parts
        try:
            tier = SubscriptionTier(tier_str.lower())
        except ValueError as exc:
            raise LicenseValidationError(f"Unknown tier: {tier_str}") from exc

        # Validate Ed25519 signature
        payload = f"{tier_str}:{ts_str}:{rand}".encode()
        try:
            sig_bytes = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
            self._public_key.verify(sig_bytes, payload)
        except (InvalidSignature, ValueError, base64.binascii.Error) as exc:
            raise LicenseValidationError("License key is invalid.") from exc

        # Check expiration
        try:
            expires_at = datetime.fromtimestamp(int(ts_str))
        except (ValueError, OSError) as exc:
            raise LicenseValidationError("License timestamp is corrupt.") from exc

        if expires_at < datetime.now():
            raise LicenseValidationError("License has expired.")

        self._state = {
            "tier": tier.value,
            "license_key": license_key,
            "activated_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "validated_at": datetime.now().isoformat(),
        }
        self._save_state()
        logger.info("Activated %s license, expires %s", tier.value, expires_at.date())
        return self.license_info

    def deactivate(self) -> None:
        """Clear the current license and revert to free/trial."""
        self._state = {}
        self._save_state()
        logger.info("License deactivated")

    def generate_key(self, tier: SubscriptionTier, days: int = 365) -> str:
        """Generate a license key.

        Requires the Ed25519 private key, loaded from constructor argument
        or the MINDFUL_LICENSE_PRIVATE_KEY environment variable. Intended for
        issuer-side use (sales tool, build pipeline). Client builds will not
        have the private key and will raise RuntimeError if this is called.
        """
        priv_b64 = self._private_key_b64 or os.environ.get("MINDFUL_LICENSE_PRIVATE_KEY")
        if not priv_b64:
            raise RuntimeError(
                "No license signing key available. Set MINDFUL_LICENSE_PRIVATE_KEY "
                "or pass private_key_b64 to SubscriptionManager. License generation "
                "is restricted to the issuer."
            )
        private_key = Ed25519PrivateKey.from_private_bytes(base64.b64decode(priv_b64))
        expires = datetime.now() + timedelta(days=days)
        ts = int(expires.timestamp())
        rand = secrets.token_hex(4)
        payload = f"{tier.value}:{ts}:{rand}".encode()
        sig_bytes = private_key.sign(payload)
        signature = base64.urlsafe_b64encode(sig_bytes).rstrip(b"=").decode()
        return f"{tier.value}:{ts}:{rand}:{signature}"

    # -- trial management --------------------------------------------------

    def start_trial(self) -> LicenseInfo:
        """Start a 14-day trial if one hasn't been started yet."""
        if self._state.get("trial_ended"):
            raise LicenseValidationError("Trial has already been used.")
        if self._has_valid_license():
            raise LicenseValidationError("Already have an active license.")
        if self._is_trial_active():
            raise LicenseValidationError("Trial is already active.")
        self._state["trial_started_at"] = datetime.now().isoformat()
        self._save_state()
        logger.info("Trial started, expires in %d days", self.TRIAL_DAYS)
        return self.license_info

    def end_trial(self) -> None:
        """Force-end the trial (e.g., after purchase)."""
        self._state["trial_ended"] = True
        self._save_state()

    @property
    def trial_days_remaining(self) -> int:
        """Return days left in trial, or 0 if not in trial."""
        if not self._is_trial_active():
            return 0
        end = self._trial_end()
        if end is None:
            return 0
        remaining = (end - datetime.now()).days
        return max(0, remaining)

    # -- internals ---------------------------------------------------------

    def _has_valid_license(self) -> bool:
        if not self._state.get("license_key"):
            return False
        expires = self._parse_dt(self._state.get("expires_at"))
        if expires is None:
            return False
        return expires > datetime.now()

    def _is_trial_active(self) -> bool:
        if self._state.get("trial_ended"):
            return False
        started = self._parse_dt(self._state.get("trial_started_at"))
        if started is None:
            return False
        return datetime.now() < started + timedelta(days=self.TRIAL_DAYS)

    def _trial_start(self) -> datetime | None:
        return self._parse_dt(self._state.get("trial_started_at"))

    def _trial_end(self) -> datetime | None:
        started = self._trial_start()
        if started is None:
            return None
        return started + timedelta(days=self.TRIAL_DAYS)

    def _upgrade_target(self) -> SubscriptionTier:
        """Return the minimum tier needed to upgrade from current."""
        cur = self.current_tier
        if cur == SubscriptionTier.FREE:
            return SubscriptionTier.PRO
        return SubscriptionTier.PREMIUM

    @staticmethod
    def _parse_dt(val: Any) -> datetime | None:
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        try:
            return datetime.fromisoformat(str(val))
        except (ValueError, TypeError):
            return None


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class LicenseValidationError(Exception):
    """Raised when a license key is invalid or expired."""


class FeatureGateError(Exception):
    """Raised when a gated feature is accessed without the right subscription."""
