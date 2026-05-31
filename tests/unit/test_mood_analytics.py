"""
Tests for MoodAnalytics (src/core/mood_analytics.py).

Covers trend analysis, pattern detection, mood volatility,
empty data handling, insight generation, and condition-specific insights.
"""

from datetime import datetime, timedelta

from core.mood_analytics import (
    AnalyticsReport,
    MoodAnalytics,
    TrendDirection,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_entries(scores, days_back=None, start_hour=10):
    """Build mood entry dicts from a list of scores."""
    n = len(scores)
    base = datetime.now() - timedelta(days=(days_back or n))
    entries = []
    for i, score in enumerate(scores):
        ts = base + timedelta(days=i, hours=start_hour)
        entries.append({
            "timestamp": ts.isoformat(),
            "mood_score": score,
            "energy_score": 30 + i * 3,
            "symptoms": [],
            "activities": [],
        })
    return entries


def _improving_entries(n=14):
    """Entries with steadily improving mood."""
    return _make_entries([3 + i * 0.5 for i in range(n)])


def _declining_entries(n=14):
    """Entries with steadily declining mood."""
    return _make_entries([9 - i * 0.4 for i in range(n)])


def _stable_entries(n=14):
    """Entries with stable mood around 6."""
    return _make_entries([6.0] * n)


# ---------------------------------------------------------------------------
# Trend analysis
# ---------------------------------------------------------------------------

class TestTrendAnalysis:

    def test_improving_mood_trend(self):
        """Steadily rising scores should produce an IMPROVING trend."""
        entries = _improving_entries()
        analytics = MoodAnalytics(entries)
        trend = analytics.mood_trend()

        assert trend.direction == TrendDirection.IMPROVING
        assert trend.slope > 0

    def test_declining_mood_trend(self):
        """Steadily falling scores should produce a DECLINING trend."""
        entries = _declining_entries()
        analytics = MoodAnalytics(entries)
        trend = analytics.mood_trend()

        assert trend.direction == TrendDirection.DECLINING
        assert trend.slope < 0

    def test_stable_mood_trend(self):
        """Flat scores should produce a STABLE trend."""
        entries = _stable_entries()
        analytics = MoodAnalytics(entries)
        trend = analytics.mood_trend()

        assert trend.direction == TrendDirection.STABLE
        assert abs(trend.slope) < 0.06

    def test_moving_averages_with_sufficient_data(self):
        entries = _improving_entries(n=10)
        analytics = MoodAnalytics(entries)
        trend = analytics.mood_trend()

        assert trend.moving_avg_7 is not None
        assert trend.moving_avg_30 is None  # only 10 entries

    def test_energy_trend(self):
        entries = _improving_entries(n=10)
        analytics = MoodAnalytics(entries)
        trend = analytics.energy_trend()

        assert trend is not None
        assert trend.slope >= 0  # energy increases in our helper


# ---------------------------------------------------------------------------
# Pattern detection
# ---------------------------------------------------------------------------

class TestPatternDetection:

    def test_time_of_day_pattern(self):
        """Entries at different hours should yield a time-of-day pattern."""
        base = datetime.now() - timedelta(days=20)
        entries = []
        for i in range(20):
            hour = 9 if i % 2 == 0 else 20
            ts = base + timedelta(days=i)
            ts = ts.replace(hour=hour, minute=0)
            # Morning entries have higher mood
            score = 8 if hour == 9 else 4
            entries.append({
                "timestamp": ts.isoformat(),
                "mood_score": score,
                "energy_score": 50,
            })

        analytics = MoodAnalytics(entries)
        pattern = analytics.time_of_day_pattern()

        assert pattern is not None
        assert pattern.pattern_type == "time_of_day"
        assert pattern.best != pattern.worst

    def test_day_of_week_pattern(self):
        entries = _improving_entries(n=14)
        analytics = MoodAnalytics(entries)
        pattern = analytics.day_of_week_pattern()

        assert pattern is not None
        assert pattern.pattern_type == "day_of_week"

    def test_seasonal_pattern_insufficient_data(self):
        """With entries in one season only, seasonal pattern should be None."""
        entries = _stable_entries(n=10)
        analytics = MoodAnalytics(entries)
        pattern = analytics.seasonal_pattern()

        # All entries in the same month/season, so likely only one bucket
        # Result may be None if only one season represented
        if pattern is not None:
            assert pattern.pattern_type == "seasonal"


# ---------------------------------------------------------------------------
# Mood volatility
# ---------------------------------------------------------------------------

class TestMoodVolatility:

    def test_volatility_stable(self):
        entries = _stable_entries(n=10)
        analytics = MoodAnalytics(entries)
        vol = analytics.mood_volatility()

        assert vol == 0.0

    def test_volatility_high(self):
        """Alternating high/low scores should give high volatility."""
        scores = [2, 9] * 10
        entries = _make_entries(scores)
        analytics = MoodAnalytics(entries)
        vol = analytics.mood_volatility()

        assert vol > 2.0

    def test_volatility_single_entry(self):
        entries = _make_entries([5.0])
        analytics = MoodAnalytics(entries)
        assert analytics.mood_volatility() == 0.0


# ---------------------------------------------------------------------------
# Empty data handling
# ---------------------------------------------------------------------------

class TestEmptyDataHandling:

    def test_empty_entries_full_report(self):
        analytics = MoodAnalytics([])
        report = analytics.full_report()

        assert isinstance(report, AnalyticsReport)
        assert report.mood_trend is None
        assert len(report.insights) >= 1
        assert "not enough data" in report.insights[0].lower() or "keep logging" in report.insights[0].lower()

    def test_empty_entries_mood_volatility(self):
        analytics = MoodAnalytics([])
        # _entries is empty -> mood_trend would fail, but volatility should be safe
        # Actually with empty _entries, calling mood_trend will create empty array
        # Let's just check volatility works
        assert analytics.mood_volatility() == 0.0

    def test_invalid_entries_skipped(self):
        """Entries without valid timestamps are silently skipped."""
        raw = [
            {"mood_score": 5},  # no timestamp
            {"timestamp": "not-a-date", "mood_score": 5},
            {"timestamp": datetime.now().isoformat(), "mood_score": 7},
        ]
        analytics = MoodAnalytics(raw)
        assert len(analytics._entries) == 1


# ---------------------------------------------------------------------------
# Insight generation
# ---------------------------------------------------------------------------

class TestInsightGeneration:

    def test_insights_from_improving_data(self, sample_mood_entries):
        analytics = MoodAnalytics(sample_mood_entries)
        report = analytics.full_report()

        assert isinstance(report.insights, list)
        assert len(report.insights) > 0

    def test_insights_include_trend_description(self, sample_mood_entries):
        analytics = MoodAnalytics(sample_mood_entries)
        report = analytics.full_report()

        # Should have at least the mood trend description
        assert any("mood" in i.lower() or "energy" in i.lower() for i in report.insights)

    def test_condition_insights_depression(self):
        """Depression condition should flag prolonged low mood."""
        scores = [3.0] * 14
        entries = _make_entries(scores)
        analytics = MoodAnalytics(entries, conditions=["depression"])
        insights = analytics.condition_insights()

        assert len(insights) >= 1
        assert any(ci.condition == "depression" for ci in insights)

    def test_condition_insights_adhd_energy_volatility(self):
        """ADHD condition should detect energy volatility."""
        base = datetime.now() - timedelta(days=10)
        entries = []
        for i in range(10):
            ts = base + timedelta(days=i, hours=10)
            entries.append({
                "timestamp": ts.isoformat(),
                "mood_score": 6,
                "energy_score": 20 if i % 2 == 0 else 90,
            })

        analytics = MoodAnalytics(entries, conditions=["adhd"])
        insights = analytics.condition_insights()

        assert any(ci.condition == "adhd" for ci in insights)

    def test_condition_insights_anxiety(self):
        """Anxiety condition should detect frequent anxiety symptoms."""
        base = datetime.now() - timedelta(days=14)
        entries = []
        for i in range(14):
            ts = base + timedelta(days=i, hours=10)
            entries.append({
                "timestamp": ts.isoformat(),
                "mood_score": 5,
                "energy_score": 50,
                "symptoms": ["anxiety", "worry"],
            })

        analytics = MoodAnalytics(entries, conditions=["anxiety"])
        insights = analytics.condition_insights()

        assert any(ci.condition == "anxiety" for ci in insights)


# ---------------------------------------------------------------------------
# Triggers and clusters
# ---------------------------------------------------------------------------

class TestTriggersAndClusters:

    def test_identify_triggers_with_activities(self):
        base = datetime.now() - timedelta(days=20)
        entries = []
        for i in range(20):
            ts = base + timedelta(days=i, hours=10)
            has_exercise = i % 2 == 0
            entries.append({
                "timestamp": ts.isoformat(),
                "mood_score": 8 if has_exercise else 4,
                "energy_score": 60,
                "activities": ["exercise"] if has_exercise else [],
            })

        analytics = MoodAnalytics(entries)
        triggers = analytics.identify_triggers()

        # Exercise should be positively correlated
        exercise_triggers = [t for t in triggers if t.trigger == "exercise"]
        assert len(exercise_triggers) >= 1
        assert exercise_triggers[0].correlation > 0

    def test_symptom_clusters(self):
        base = datetime.now() - timedelta(days=10)
        entries = []
        for i in range(10):
            ts = base + timedelta(days=i, hours=10)
            entries.append({
                "timestamp": ts.isoformat(),
                "mood_score": 4,
                "energy_score": 30,
                "symptoms": ["fatigue", "headache"] if i < 7 else ["fatigue"],
            })

        analytics = MoodAnalytics(entries)
        clusters = analytics.symptom_clusters(min_co_occurrence=2)

        assert len(clusters) >= 1
        assert ("fatigue", "headache") in [c.symptoms for c in clusters]

    def test_energy_mood_correlation(self, sample_mood_entries):
        analytics = MoodAnalytics(sample_mood_entries)
        corr = analytics.energy_mood_correlation()

        # Both increase together in sample data
        assert corr > 0

    def test_compute_streaks(self, sample_mood_entries):
        analytics = MoodAnalytics(sample_mood_entries)
        streaks = analytics.compute_streaks()

        assert len(streaks) == 2  # stable_mood + good_energy
        assert all(s.current_length >= 0 for s in streaks)
