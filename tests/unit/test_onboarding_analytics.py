"""Tests for onboarding analytics."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.onboarding_analytics import OnboardingAnalytics, OnboardingStep


@pytest.fixture
def analytics(tmp_path: Path) -> OnboardingAnalytics:
    return OnboardingAnalytics(data_dir=tmp_path)


class TestSessionTracking:
    def test_start_session(self, analytics: OnboardingAnalytics) -> None:
        analytics.start_session()
        assert analytics._current is not None

    def test_log_step_and_complete(self, analytics: OnboardingAnalytics) -> None:
        analytics.start_session()
        analytics.log_step(OnboardingStep.WELCOME, "completed")
        analytics.log_step(OnboardingStep.NAME, "completed")
        analytics.complete()
        assert len(analytics._sessions) == 1
        assert analytics._sessions[0].completed_at is not None

    def test_funnel_report(self, analytics: OnboardingAnalytics) -> None:
        analytics.start_session()
        analytics.log_step(OnboardingStep.WELCOME, "completed")
        analytics.log_step(OnboardingStep.NAME, "completed")
        analytics.log_step(OnboardingStep.CONDITIONS, "abandoned")
        report = analytics.funnel_report()
        assert report["total_sessions"] == 1
        assert report["completion_rate"] == 0.0
        assert report["steps"]["welcome"]["completed"] == 1

    def test_multiple_sessions(self, analytics: OnboardingAnalytics) -> None:
        for _ in range(3):
            analytics.start_session()
            analytics.log_step(OnboardingStep.WELCOME, "completed")
            analytics.complete()
        report = analytics.funnel_report()
        assert report["total_sessions"] == 3
        assert report["completion_rate"] == 1.0
