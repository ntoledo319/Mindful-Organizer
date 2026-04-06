"""
Comprehensive mood and symptom analytics engine.

Provides trend analysis, pattern detection, trigger identification,
symptom clustering, volatility scoring, and condition-specific insights
from mood/energy journal entries.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Enums & data-classes
# ---------------------------------------------------------------------------

class TrendDirection(Enum):
    """Direction a metric is heading."""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"


class TimeOfDay(Enum):
    """Coarse time-of-day buckets."""
    EARLY_MORNING = "early_morning"   # 05-08
    MORNING = "morning"               # 08-12
    AFTERNOON = "afternoon"           # 12-17
    EVENING = "evening"               # 17-21
    NIGHT = "night"                   # 21-05


class Season(Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


@dataclass
class MoodEntry:
    """A single mood journal entry."""
    timestamp: datetime
    mood_score: float            # 1-10
    energy_score: float          # 1-100
    symptoms: List[str] = field(default_factory=list)
    notes: str = ""
    activities: List[str] = field(default_factory=list)
    sleep_hours: Optional[float] = None
    medication_taken: Optional[bool] = None
    tasks_completed: Optional[int] = None


@dataclass
class TrendResult:
    """Result of a trend analysis."""
    direction: TrendDirection
    moving_avg_7: Optional[float]
    moving_avg_30: Optional[float]
    slope: float
    description: str


@dataclass
class PatternResult:
    """Detected temporal pattern."""
    pattern_type: str           # "time_of_day", "day_of_week", "seasonal"
    detail: Dict[str, float]    # bucket -> avg mood
    best: str
    worst: str
    description: str


@dataclass
class TriggerResult:
    """A mood trigger with correlation info."""
    trigger: str
    correlation: float          # -1 to 1
    direction: str              # "positive" or "negative"
    description: str


@dataclass
class ClusterResult:
    """Co-occurring symptom cluster."""
    symptoms: Tuple[str, ...]
    co_occurrence_count: int
    avg_mood_when_present: float
    description: str


@dataclass
class StreakInfo:
    """Information about a streak."""
    streak_type: str
    current_length: int
    longest_length: int
    description: str


@dataclass
class ConditionInsight:
    """A condition-specific clinical insight."""
    condition: str
    insight_type: str
    severity: str               # "info", "mild", "moderate", "severe"
    description: str
    recommendation: str


@dataclass
class AnalyticsReport:
    """Full analytics report."""
    mood_trend: Optional[TrendResult] = None
    energy_trend: Optional[TrendResult] = None
    time_of_day_pattern: Optional[PatternResult] = None
    day_of_week_pattern: Optional[PatternResult] = None
    seasonal_pattern: Optional[PatternResult] = None
    triggers: List[TriggerResult] = field(default_factory=list)
    symptom_clusters: List[ClusterResult] = field(default_factory=list)
    mood_volatility: float = 0.0
    energy_mood_correlation: float = 0.0
    streaks: List[StreakInfo] = field(default_factory=list)
    condition_insights: List[ConditionInsight] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_entries(raw: Sequence[Dict[str, Any]]) -> List[MoodEntry]:
    """Convert list-of-dicts into validated MoodEntry objects."""
    entries: List[MoodEntry] = []
    for d in raw:
        ts = d.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif not isinstance(ts, datetime):
            continue  # skip invalid entries

        mood = float(d.get("mood_score", 5))
        mood = max(1.0, min(10.0, mood))
        energy = float(d.get("energy_score", 50))
        energy = max(1.0, min(100.0, energy))

        entries.append(MoodEntry(
            timestamp=ts,
            mood_score=mood,
            energy_score=energy,
            symptoms=list(d.get("symptoms", [])),
            notes=str(d.get("notes", "")),
            activities=list(d.get("activities", [])),
            sleep_hours=d.get("sleep_hours"),
            medication_taken=d.get("medication_taken"),
            tasks_completed=d.get("tasks_completed"),
        ))
    entries.sort(key=lambda e: e.timestamp)
    return entries


def _moving_average(values: np.ndarray, window: int) -> Optional[float]:
    """Return the latest moving average for *window* or None if insufficient data."""
    if len(values) < window:
        return None
    return float(np.mean(values[-window:]))


def _linear_slope(values: np.ndarray) -> float:
    """Compute the OLS slope of values vs sequential index."""
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values), dtype=np.float64)
    slope, _ = np.polyfit(x, values, 1)
    return float(slope)


def _classify_trend(slope: float, threshold: float = 0.05) -> TrendDirection:
    if slope > threshold:
        return TrendDirection.IMPROVING
    elif slope < -threshold:
        return TrendDirection.DECLINING
    return TrendDirection.STABLE


def _time_of_day(dt: datetime) -> TimeOfDay:
    h = dt.hour
    if 5 <= h < 8:
        return TimeOfDay.EARLY_MORNING
    if 8 <= h < 12:
        return TimeOfDay.MORNING
    if 12 <= h < 17:
        return TimeOfDay.AFTERNOON
    if 17 <= h < 21:
        return TimeOfDay.EVENING
    return TimeOfDay.NIGHT


def _season(dt: datetime) -> Season:
    m = dt.month
    if m in (3, 4, 5):
        return Season.SPRING
    if m in (6, 7, 8):
        return Season.SUMMER
    if m in (9, 10, 11):
        return Season.AUTUMN
    return Season.WINTER


_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ---------------------------------------------------------------------------
# Main analytics engine
# ---------------------------------------------------------------------------

class MoodAnalytics:
    """Analyse mood journal entries and produce actionable insights."""

    def __init__(
        self,
        entries: Sequence[Dict[str, Any]],
        *,
        conditions: Optional[List[str]] = None,
    ) -> None:
        """
        Parameters
        ----------
        entries : list of dict
            Each dict must contain at least ``timestamp`` and ``mood_score``.
        conditions : list of str, optional
            User's diagnosed conditions (e.g. ``["depression", "adhd"]``).
        """
        self._raw = entries
        self._entries = _parse_entries(entries)
        self._conditions = [c.lower() for c in (conditions or [])]

    # -- public API ---------------------------------------------------------

    def full_report(self) -> AnalyticsReport:
        """Run every analysis and return a consolidated report."""
        report = AnalyticsReport()
        if not self._entries:
            report.insights.append("Not enough data to generate insights yet. Keep logging!")
            return report

        report.mood_trend = self.mood_trend()
        report.energy_trend = self.energy_trend()
        report.time_of_day_pattern = self.time_of_day_pattern()
        report.day_of_week_pattern = self.day_of_week_pattern()
        report.seasonal_pattern = self.seasonal_pattern()
        report.triggers = self.identify_triggers()
        report.symptom_clusters = self.symptom_clusters()
        report.mood_volatility = self.mood_volatility()
        report.energy_mood_correlation = self.energy_mood_correlation()
        report.streaks = self.compute_streaks()
        report.condition_insights = self.condition_insights()
        report.insights = self.generate_insights(report)
        return report

    # -- trend analysis -----------------------------------------------------

    def mood_trend(self) -> TrendResult:
        """Compute mood trend with 7-day and 30-day moving averages."""
        values = np.array([e.mood_score for e in self._entries])
        return self._trend_for("mood", values, improving_positive=True)

    def energy_trend(self) -> TrendResult:
        """Compute energy trend with 7-day and 30-day moving averages."""
        values = np.array([e.energy_score for e in self._entries])
        return self._trend_for("energy", values, improving_positive=True)

    def _trend_for(self, label: str, values: np.ndarray, improving_positive: bool) -> TrendResult:
        ma7 = _moving_average(values, 7)
        ma30 = _moving_average(values, 30)
        slope = _linear_slope(values)
        direction = _classify_trend(slope if improving_positive else -slope)

        if direction == TrendDirection.IMPROVING:
            desc = f"Your {label} has been trending upward recently."
        elif direction == TrendDirection.DECLINING:
            desc = f"Your {label} appears to be declining. Consider reaching out for support."
        else:
            desc = f"Your {label} has been relatively stable."

        return TrendResult(
            direction=direction,
            moving_avg_7=round(ma7, 2) if ma7 is not None else None,
            moving_avg_30=round(ma30, 2) if ma30 is not None else None,
            slope=round(slope, 4),
            description=desc,
        )

    # -- pattern detection --------------------------------------------------

    def time_of_day_pattern(self) -> Optional[PatternResult]:
        """Average mood by time-of-day bucket."""
        buckets: Dict[str, List[float]] = defaultdict(list)
        for e in self._entries:
            buckets[_time_of_day(e.timestamp).value].append(e.mood_score)
        return self._pattern_result("time_of_day", buckets, "time of day")

    def day_of_week_pattern(self) -> Optional[PatternResult]:
        """Average mood by day of week."""
        buckets: Dict[str, List[float]] = defaultdict(list)
        for e in self._entries:
            buckets[_DAY_NAMES[e.timestamp.weekday()]].append(e.mood_score)
        return self._pattern_result("day_of_week", buckets, "day of the week")

    def seasonal_pattern(self) -> Optional[PatternResult]:
        """Average mood by season (needs multi-month data)."""
        buckets: Dict[str, List[float]] = defaultdict(list)
        for e in self._entries:
            buckets[_season(e.timestamp).value].append(e.mood_score)
        if len(buckets) < 2:
            return None
        return self._pattern_result("seasonal", buckets, "season")

    def _pattern_result(
        self, ptype: str, buckets: Dict[str, List[float]], label: str
    ) -> Optional[PatternResult]:
        if not buckets:
            return None
        avgs = {k: float(np.mean(v)) for k, v in buckets.items() if v}
        if not avgs:
            return None
        best = max(avgs, key=avgs.get)  # type: ignore[arg-type]
        worst = min(avgs, key=avgs.get)  # type: ignore[arg-type]
        desc = (
            f"Your mood tends to be highest during {best} "
            f"(avg {avgs[best]:.1f}) and lowest during {worst} (avg {avgs[worst]:.1f})."
        )
        return PatternResult(
            pattern_type=ptype,
            detail={k: round(v, 2) for k, v in avgs.items()},
            best=best,
            worst=worst,
            description=desc,
        )

    # -- trigger identification --------------------------------------------

    def identify_triggers(self) -> List[TriggerResult]:
        """Correlate mood changes with activities, sleep, medication, tasks."""
        results: List[TriggerResult] = []
        moods = np.array([e.mood_score for e in self._entries])
        if len(moods) < 3:
            return results

        # Activity triggers
        all_activities: set[str] = set()
        for e in self._entries:
            all_activities.update(e.activities)

        for act in all_activities:
            present = np.array([1.0 if act in e.activities else 0.0 for e in self._entries])
            if present.sum() < 2 or (len(present) - present.sum()) < 2:
                continue
            corr = self._pearson(present, moods)
            if abs(corr) >= 0.15:
                direction = "positive" if corr > 0 else "negative"
                desc = (
                    f"Activity '{act}' is {'positively' if corr > 0 else 'negatively'} "
                    f"correlated with your mood (r={corr:.2f})."
                )
                results.append(TriggerResult(act, round(corr, 3), direction, desc))

        # Sleep trigger
        sleep_vals = [e.sleep_hours for e in self._entries if e.sleep_hours is not None]
        if len(sleep_vals) >= 3:
            idxs = [i for i, e in enumerate(self._entries) if e.sleep_hours is not None]
            sleep_arr = np.array(sleep_vals)
            mood_arr = moods[idxs]
            corr = self._pearson(sleep_arr, mood_arr)
            if abs(corr) >= 0.1:
                direction = "positive" if corr > 0 else "negative"
                desc = f"Sleep hours are {'positively' if corr > 0 else 'negatively'} correlated with mood (r={corr:.2f})."
                results.append(TriggerResult("sleep_hours", round(corr, 3), direction, desc))

        # Medication trigger
        med_vals = [e.medication_taken for e in self._entries if e.medication_taken is not None]
        if len(med_vals) >= 3:
            idxs = [i for i, e in enumerate(self._entries) if e.medication_taken is not None]
            med_arr = np.array([1.0 if v else 0.0 for v in med_vals])
            mood_arr = moods[idxs]
            if med_arr.sum() > 0 and (len(med_arr) - med_arr.sum()) > 0:
                corr = self._pearson(med_arr, mood_arr)
                if abs(corr) >= 0.1:
                    direction = "positive" if corr > 0 else "negative"
                    desc = f"Taking medication is {'positively' if corr > 0 else 'negatively'} correlated with mood (r={corr:.2f})."
                    results.append(TriggerResult("medication", round(corr, 3), direction, desc))

        # Tasks completed trigger
        task_vals = [e.tasks_completed for e in self._entries if e.tasks_completed is not None]
        if len(task_vals) >= 3:
            idxs = [i for i, e in enumerate(self._entries) if e.tasks_completed is not None]
            task_arr = np.array(task_vals, dtype=np.float64)
            mood_arr = moods[idxs]
            corr = self._pearson(task_arr, mood_arr)
            if abs(corr) >= 0.1:
                direction = "positive" if corr > 0 else "negative"
                desc = f"Completing tasks is {'positively' if corr > 0 else 'negatively'} correlated with mood (r={corr:.2f})."
                results.append(TriggerResult("tasks_completed", round(corr, 3), direction, desc))

        results.sort(key=lambda t: abs(t.correlation), reverse=True)
        return results

    # -- symptom clustering -------------------------------------------------

    def symptom_clusters(self, min_co_occurrence: int = 2) -> List[ClusterResult]:
        """Find symptoms that tend to co-occur."""
        pair_counts: Counter[Tuple[str, str]] = Counter()
        pair_moods: Dict[Tuple[str, str], List[float]] = defaultdict(list)

        for e in self._entries:
            syms = sorted(set(e.symptoms))
            for i in range(len(syms)):
                for j in range(i + 1, len(syms)):
                    pair = (syms[i], syms[j])
                    pair_counts[pair] += 1
                    pair_moods[pair].append(e.mood_score)

        results: List[ClusterResult] = []
        for pair, count in pair_counts.most_common():
            if count < min_co_occurrence:
                break
            avg_mood = float(np.mean(pair_moods[pair]))
            desc = (
                f"'{pair[0]}' and '{pair[1]}' co-occurred {count} times "
                f"with an average mood of {avg_mood:.1f}."
            )
            results.append(ClusterResult(pair, count, round(avg_mood, 2), desc))
        return results

    # -- volatility ---------------------------------------------------------

    def mood_volatility(self) -> float:
        """Compute mood volatility as std-dev of day-to-day changes."""
        if len(self._entries) < 2:
            return 0.0
        moods = np.array([e.mood_score for e in self._entries])
        diffs = np.diff(moods)
        return round(float(np.std(diffs)), 3)

    # -- energy-mood correlation -------------------------------------------

    def energy_mood_correlation(self) -> float:
        """Pearson correlation between energy and mood scores."""
        if len(self._entries) < 3:
            return 0.0
        moods = np.array([e.mood_score for e in self._entries])
        energy = np.array([e.energy_score for e in self._entries])
        return round(self._pearson(moods, energy), 3)

    # -- streaks -----------------------------------------------------------

    def compute_streaks(self) -> List[StreakInfo]:
        """Track stable-mood and good-energy streaks."""
        results: List[StreakInfo] = []
        if not self._entries:
            return results

        # Stable mood streak: day-to-day change <= 1
        stable_current, stable_longest = self._streak(
            [abs(self._entries[i].mood_score - self._entries[i - 1].mood_score) <= 1.0
             for i in range(1, len(self._entries))]
        )
        results.append(StreakInfo(
            "stable_mood",
            stable_current,
            stable_longest,
            f"Current stable-mood streak: {stable_current} day(s) (best: {stable_longest}).",
        ))

        # Good energy streak: energy >= 60
        good_current, good_longest = self._streak(
            [e.energy_score >= 60 for e in self._entries]
        )
        results.append(StreakInfo(
            "good_energy",
            good_current,
            good_longest,
            f"Current good-energy streak: {good_current} day(s) (best: {good_longest}).",
        ))

        return results

    # -- condition-specific insights ----------------------------------------

    def condition_insights(self) -> List[ConditionInsight]:
        """Generate insights tailored to the user's conditions."""
        insights: List[ConditionInsight] = []
        if not self._entries or not self._conditions:
            return insights

        moods = np.array([e.mood_score for e in self._entries])
        energies = np.array([e.energy_score for e in self._entries])

        # --- Bipolar: detect potential manic/depressive episodes ---
        if "bipolar" in self._conditions:
            recent = moods[-7:] if len(moods) >= 7 else moods
            avg_recent = float(np.mean(recent))
            if avg_recent >= 8.5 and float(np.mean(energies[-7:] if len(energies) >= 7 else energies)) >= 80:
                insights.append(ConditionInsight(
                    "bipolar", "potential_mania", "moderate",
                    "Your mood and energy have been unusually elevated for several days, "
                    "which may indicate a hypomanic or manic trend.",
                    "Consider contacting your care team and tracking sleep carefully.",
                ))
            if avg_recent <= 3.0:
                insights.append(ConditionInsight(
                    "bipolar", "potential_depressive_episode", "moderate",
                    "Your mood has been consistently low, which may signal a depressive episode.",
                    "Reach out to your therapist or psychiatrist for support.",
                ))

        # --- Depression: prolonged low mood ---
        if "depression" in self._conditions:
            recent = moods[-14:] if len(moods) >= 14 else moods
            low_days = int(np.sum(recent <= 4))
            if low_days >= 10:
                insights.append(ConditionInsight(
                    "depression", "prolonged_low_mood", "severe",
                    f"Your mood has been at 4 or below for {low_days} of the last {len(recent)} entries.",
                    "Please reach out to your mental health provider.",
                ))
            elif low_days >= 5:
                insights.append(ConditionInsight(
                    "depression", "low_mood_trend", "mild",
                    f"You've had {low_days} low-mood days recently.",
                    "Gentle activities like walking or calling a friend may help.",
                ))

        # --- Anxiety: spikes ---
        if "anxiety" in self._conditions:
            anxiety_symptoms = {"anxiety", "panic", "worry", "restless", "nervous", "tense"}
            recent_entries = self._entries[-14:] if len(self._entries) >= 14 else self._entries
            spike_count = sum(
                1 for e in recent_entries
                if any(s.lower() in anxiety_symptoms for s in e.symptoms)
            )
            if spike_count >= 7:
                insights.append(ConditionInsight(
                    "anxiety", "frequent_anxiety", "moderate",
                    f"Anxiety-related symptoms appeared in {spike_count} of the last "
                    f"{len(recent_entries)} entries.",
                    "Consider grounding exercises, and speak with your therapist about adjustments.",
                ))

        # --- ADHD: energy volatility ---
        if "adhd" in self._conditions:
            if len(energies) >= 5:
                vol = float(np.std(np.diff(energies)))
                if vol > 20:
                    insights.append(ConditionInsight(
                        "adhd", "energy_volatility", "info",
                        f"Your energy levels are quite variable (volatility {vol:.1f}). "
                        "This is common with ADHD.",
                        "Try anchoring your day with consistent routines and transition rituals.",
                    ))

        return insights

    # -- human-readable insights -------------------------------------------

    def generate_insights(self, report: AnalyticsReport) -> List[str]:
        """Compile a list of human-readable insight strings."""
        insights: List[str] = []

        if report.mood_trend:
            insights.append(report.mood_trend.description)
        if report.energy_trend:
            insights.append(report.energy_trend.description)

        if report.time_of_day_pattern:
            insights.append(report.time_of_day_pattern.description)
        if report.day_of_week_pattern:
            insights.append(report.day_of_week_pattern.description)
        if report.seasonal_pattern:
            insights.append(report.seasonal_pattern.description)

        if report.mood_volatility > 2.0:
            insights.append(
                f"Your mood volatility is high ({report.mood_volatility:.2f}). "
                "Try grounding routines to steady your emotional baseline."
            )
        elif report.mood_volatility < 0.5 and len(self._entries) >= 7:
            insights.append("Your mood has been very stable recently. Great work!")

        if abs(report.energy_mood_correlation) > 0.5:
            insights.append(
                f"Energy and mood are strongly correlated (r={report.energy_mood_correlation:.2f}). "
                "Prioritising physical energy may also lift your mood."
            )

        for trigger in report.triggers[:3]:
            insights.append(trigger.description)

        for cluster in report.symptom_clusters[:3]:
            insights.append(cluster.description)

        for streak in report.streaks:
            if streak.current_length >= 3:
                insights.append(streak.description)

        for ci in report.condition_insights:
            insights.append(f"[{ci.condition.upper()}] {ci.description} Suggestion: {ci.recommendation}")

        if not insights:
            insights.append("Keep logging daily to unlock personalised insights!")

        return insights

    # -- utility -----------------------------------------------------------

    @staticmethod
    def _pearson(x: np.ndarray, y: np.ndarray) -> float:
        """Pearson correlation, returning 0 on degenerate input."""
        if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
            return 0.0
        r = np.corrcoef(x, y)[0, 1]
        if math.isnan(r):
            return 0.0
        return float(r)

    @staticmethod
    def _streak(flags: Sequence[bool]) -> Tuple[int, int]:
        """Return (current_streak, longest_streak) for a boolean sequence."""
        current = 0
        longest = 0
        for f in flags:
            if f:
                current += 1
                longest = max(longest, current)
            else:
                current = 0
        return current, longest
