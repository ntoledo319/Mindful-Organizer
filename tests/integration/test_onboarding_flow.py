"""
Integration tests for the Onboarding → Profile Creation → Dashboard Display flow.

Validates that completing onboarding produces a persisted profile and that the
dashboard widget surfaces that profile data to the user.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from core.constants import Condition, TherapyType
from profiles.mental_health_profile_builder import ProfileManager
from gui.widgets.dashboard import DashboardWidget


@pytest.fixture
def profile_manager(tmp_data_dir):
    """Fresh ProfileManager backed by a temporary directory."""
    return ProfileManager(tmp_data_dir)


@pytest.mark.integration
class TestOnboardingToProfileFlow:
    def test_create_profile_through_onboarding(self, profile_manager):
        """Simulating onboarding completion produces a valid persisted profile."""
        conditions = {Condition.ADHD, Condition.ANXIETY}
        profile = profile_manager.create_profile(
            name="Alex",
            conditions=conditions,
            therapy_types={TherapyType.CBT, TherapyType.DBT},
        )

        assert profile.id
        assert profile.name == "Alex"
        assert profile.conditions == conditions
        assert TherapyType.CBT in profile.therapy_types
        assert profile.created_at

        # Profile should be the current profile
        assert profile_manager.current_profile is not None
        assert profile_manager.current_profile.id == profile.id

        # Profile should be listable
        listed = profile_manager.list_profiles()
        assert any(p["id"] == profile.id for p in listed)

        # File should exist on disk
        profile_file = profile_manager.profiles_dir / f"{profile.id}.json"
        assert profile_file.exists()

    def test_profile_recommendations_based_on_conditions(self, profile_manager):
        """A completed profile should yield condition-aware feature recommendations."""
        profile_manager.create_profile(
            name="Jordan",
            conditions={Condition.DEPRESSION, Condition.ANXIETY},
        )

        features = profile_manager.get_recommended_features()
        assert "Mood Tracking" in features
        assert "Sleep Tracker" in features
        assert "Breathing Exercises" in features


@pytest.mark.integration
class TestProfileToDashboardFlow:
    def test_dashboard_reflects_new_profile(self, qtbot, profile_manager):
        """The DashboardWidget welcome section shows the newly-created profile name."""
        profile_manager.create_profile(
            name="Sam",
            conditions={Condition.ADHD},
        )

        widget = DashboardWidget(
            theme={"background": "#0F0F11", "text": "#F2EDE6"},
            task_manager=None,
            profile_manager=profile_manager,
            mood_manager=None,
            energy_predictor=None,
            gamification_manager=None,
            wellness_orchestrator=None,
            subscription_manager=None,
        )
        qtbot.addWidget(widget)

        # The welcome label should greet the user by name
        assert "Sam" in widget._welcome_label.text()

    def test_dashboard_suggestions_are_condition_aware(self, qtbot, profile_manager):
        """Dashboard suggestions should mention condition-specific guidance."""
        profile_manager.create_profile(
            name="Taylor",
            conditions={Condition.PTSD},
        )

        widget = DashboardWidget(
            theme={"background": "#0F0F11", "text": "#F2EDE6"},
            task_manager=None,
            profile_manager=profile_manager,
            mood_manager=None,
            energy_predictor=None,
            gamification_manager=None,
            wellness_orchestrator=None,
            subscription_manager=None,
        )
        qtbot.addWidget(widget)

        widget._refresh_suggestions()
        text = widget._suggestions_label.text()
        assert (
            "grounding" in text.lower() or "safe" in text.lower() or "crisis plan" in text.lower()
        )

    def test_dashboard_falls_back_gracefully_without_profile(self, qtbot):
        """Dashboard should still render when no profile exists."""
        widget = DashboardWidget(
            theme={"background": "#0F0F11", "text": "#F2EDE6"},
            task_manager=None,
            profile_manager=None,
            mood_manager=None,
            energy_predictor=None,
            gamification_manager=None,
            wellness_orchestrator=None,
            subscription_manager=None,
        )
        qtbot.addWidget(widget)

        assert "there" in widget._welcome_label.text()
