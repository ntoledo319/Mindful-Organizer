"""
Subscription helper utilities for GUI widgets.

Provides clean, reusable functions for feature-gating UI elements without
cluttering widget code with repeated subscription checks.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def check_feature(feature: str, subscription_manager: Any | None = None) -> bool:
    """Check if a feature is available. Always returns True if no manager."""
    if subscription_manager is None:
        return True
    try:
        return subscription_manager.has_feature(feature)
    except Exception:
        logger.debug("Feature check failed for %s", feature)
        return True


def gated(
    feature: str,
    subscription_manager: Any | None = None,
    parent_widget: Any | None = None,
    theme: dict[str, str] | None = None,
) -> bool:
    """
    Check if a feature is gated. If gated, show an upsell dialog.

    Returns True if the feature IS available (proceed).
    Returns False if gated (upsell was shown).
    """
    if check_feature(feature, subscription_manager):
        return True

    from core.subscription_manager import FEATURE_DISPLAY_NAMES
    from gui.components.upsell_dialog import UpsellDialog

    display_name = FEATURE_DISPLAY_NAMES.get(feature, feature.replace("_", " ").title())
    required_tier = "Pro"
    if feature in {
        "pdf_reports", "medication_heatmap", "values_radar",
        "clinician_sharing", "onboarding_analytics", "priority_support", "wearable_sync",
    }:
        required_tier = "Premium"

    result = UpsellDialog.prompt(display_name, required_tier, parent_widget, theme)
    if result == "trial":
        _start_trial(subscription_manager)
        # After starting trial, re-check
        return check_feature(feature, subscription_manager)
    return False


def _start_trial(subscription_manager: Any | None) -> None:
    """Attempt to start a trial on the subscription manager."""
    if subscription_manager is None:
        return
    try:
        subscription_manager.start_trial()
    except Exception as e:
        logger.info("Trial start result: %s", e)


def tier_badge_text(subscription_manager: Any | None) -> str:
    """Return a short badge label for the current tier."""
    if subscription_manager is None:
        return "Free"
    try:
        tier = subscription_manager.current_tier
        return tier.value.upper()
    except Exception:
        return "Free"


def trial_days_text(subscription_manager: Any | None) -> str:
    """Return trial days remaining text, or empty if not in trial."""
    if subscription_manager is None:
        return ""
    try:
        days = subscription_manager.trial_days_remaining
        if days > 0:
            return f"Trial: {days} days left"
        return ""
    except Exception:
        return ""
