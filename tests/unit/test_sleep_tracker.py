"""
Tests for SleepTracker (src/core/sleep_tracker.py).

Covers logging sleep, sleep debt calculation, pattern analysis,
and condition-specific insights.
"""

from datetime import date, timedelta

import pytest

from core.database import DatabaseManager
from core.sleep_tracker import SleepStats, SleepTracker


@pytest.fixture
def db(tmp_data_dir):
    database = DatabaseManager(db_path=tmp_data_dir / "test.db")
    database.initialize()
    yield database
    database.close()


@pytest.fixture
def tracker(db):
    return SleepTracker(db)


def _log_nights(tracker, n=7, base_hours=7.0, quality=7):
    """Log n consecutive nights of sleep ending today."""
    ids = []
    for i in range(n):
        d = (date.today() - timedelta(days=n - 1 - i)).isoformat()
        hours = base_hours + (i % 3 - 1) * 0.5
        rid = tracker.log_sleep(
            date=d,
            bedtime="23:00",
            wake_time=f"{6 + int(hours)}:{int((hours % 1) * 60):02d}",
            quality=quality,
            interruptions=i % 3,
        )
        ids.append(rid)
    return ids


# ---------------------------------------------------------------------------
# Log sleep
# ---------------------------------------------------------------------------


class TestLogSleep:
    def test_log_sleep_basic(self, tracker):
        row_id = tracker.log_sleep(
            date="2026-04-01",
            bedtime="23:00",
            wake_time="07:00",
            quality=7,
        )
        assert row_id > 0

    def test_log_sleep_with_all_fields(self, tracker):
        row_id = tracker.log_sleep(
            date="2026-04-01",
            bedtime="23:30",
            wake_time="06:45",
            quality=6,
            interruptions=2,
            interruption_details="Woke at 2am and 4am",
            sleep_aids="Melatonin",
            dreams="Vivid dream about flying",
            notes="Stressful day",
        )
        entry = tracker.get_entry(row_id)
        assert entry is not None
        assert entry.quality == 6
        assert entry.interruptions == 2
        assert entry.sleep_aids == "Melatonin"

    def test_quality_clamped(self, tracker):
        row_id = tracker.log_sleep(
            date="2026-04-01",
            bedtime="23:00",
            wake_time="07:00",
            quality=15,  # over max
        )
        entry = tracker.get_entry(row_id)
        assert entry.quality == 10

    def test_duration_calculated(self, tracker):
        row_id = tracker.log_sleep(
            date="2026-04-01",
            bedtime="23:00",
            wake_time="07:00",
            quality=7,
        )
        entry = tracker.get_entry(row_id)
        assert entry.duration_hours is not None
        assert abs(entry.duration_hours - 8.0) < 0.1

    def test_get_entries(self, tracker):
        _log_nights(tracker, n=5)
        entries = tracker.get_entries(days=7)
        assert len(entries) == 5

    def test_delete_entry(self, tracker):
        row_id = tracker.log_sleep(
            date="2026-04-01",
            bedtime="23:00",
            wake_time="07:00",
            quality=7,
        )
        affected = tracker.delete_entry(row_id)
        assert affected == 1
        assert tracker.get_entry(row_id) is None


# ---------------------------------------------------------------------------
# Sleep debt
# ---------------------------------------------------------------------------


class TestSleepDebt:
    def test_sleep_debt_with_short_sleep(self, tracker):
        """Logging consistently short sleep should accumulate debt."""
        for i in range(7):
            d = (date.today() - timedelta(days=6 - i)).isoformat()
            tracker.log_sleep(
                date=d,
                bedtime="01:00",
                wake_time="06:00",  # only 5 hours
                quality=5,
            )

        debt = tracker.sleep_debt(days=7)
        # 7 * (8 - 5) = 21 hours of debt
        assert debt > 15

    def test_sleep_debt_with_good_sleep(self, tracker):
        for i in range(7):
            d = (date.today() - timedelta(days=6 - i)).isoformat()
            tracker.log_sleep(
                date=d,
                bedtime="22:30",
                wake_time="07:00",  # 8.5 hours
                quality=8,
            )

        debt = tracker.sleep_debt(days=7)
        assert debt == 0.0

    def test_sleep_debt_empty(self, tracker):
        debt = tracker.sleep_debt(days=7)
        assert debt == 0.0


# ---------------------------------------------------------------------------
# Pattern analysis
# ---------------------------------------------------------------------------


class TestPatternAnalysis:
    def test_get_stats(self, tracker):
        _log_nights(tracker, n=10, base_hours=7.0, quality=6)
        stats = tracker.get_stats(days=14)

        assert isinstance(stats, SleepStats)
        assert stats.total_entries == 10
        assert stats.mean_duration > 0
        assert stats.mean_quality > 0

    def test_stats_empty(self, tracker):
        stats = tracker.get_stats(days=30)
        assert stats.total_entries == 0
        assert stats.mean_duration == 0.0

    def test_consistency_score(self, tracker):
        """Consistent sleep times should give a high consistency score."""
        for i in range(7):
            d = (date.today() - timedelta(days=6 - i)).isoformat()
            tracker.log_sleep(
                date=d,
                bedtime="23:00",
                wake_time="07:00",
                quality=7,
            )

        stats = tracker.get_stats(days=7)
        assert stats.consistency_score > 50

    def test_duration_trend(self, tracker):
        _log_nights(tracker, n=7)
        trend = tracker.duration_trend(days=14)

        assert len(trend) == 7
        assert all(isinstance(t, tuple) and len(t) == 2 for t in trend)

    def test_quality_trend(self, tracker):
        _log_nights(tracker, n=7)
        trend = tracker.quality_trend(days=14)

        assert len(trend) == 7

    def test_sleep_tips_short_sleep(self, tracker):
        for i in range(7):
            d = (date.today() - timedelta(days=6 - i)).isoformat()
            tracker.log_sleep(
                date=d,
                bedtime="02:00",
                wake_time="06:00",  # 4 hours
                quality=3,
            )

        tips = tracker.get_tips(days=14)
        assert len(tips) >= 1
        assert all(isinstance(t, str) and len(t) > 5 for t in tips)

    def test_sleep_tips_empty(self, tracker):
        tips = tracker.get_tips(days=14)
        assert len(tips) >= 1
        assert "start logging" in tips[0].lower()


# ---------------------------------------------------------------------------
# Condition insights
# ---------------------------------------------------------------------------


class TestConditionInsights:
    def test_adhd_insights(self, tracker):
        insights = tracker.get_condition_insights("ADHD")
        assert len(insights) >= 2
        assert any("adhd" in i.lower() for i in insights)

    def test_anxiety_insights(self, tracker):
        insights = tracker.get_condition_insights("Anxiety")
        assert len(insights) >= 2
        assert any("anxiety" in i.lower() or "worry" in i.lower() for i in insights)

    def test_depression_insights(self, tracker):
        insights = tracker.get_condition_insights("Depression")
        assert len(insights) >= 2

    def test_ptsd_insights(self, tracker):
        insights = tracker.get_condition_insights("PTSD")
        assert len(insights) >= 2
        assert any("nightmare" in i.lower() or "safety" in i.lower() for i in insights)

    def test_ocd_insights(self, tracker):
        insights = tracker.get_condition_insights("OCD")
        assert len(insights) >= 2

    def test_generic_insights(self, tracker):
        insights = tracker.get_condition_insights("UnknownCondition")
        assert len(insights) >= 1


# ---------------------------------------------------------------------------
# Correlations
# ---------------------------------------------------------------------------


class TestCorrelations:
    def test_correlate_with_mood_insufficient_data(self, tracker):
        corr = tracker.correlate_with_mood([], days=7)
        assert "not enough" in corr.insight.lower()

    def test_correlate_with_energy_insufficient_data(self, tracker):
        corr = tracker.correlate_with_energy([], days=7)
        assert "not enough" in corr.insight.lower()
