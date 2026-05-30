"""
Sleep logging, analysis, and condition-specific insights for Mindful Organizer.

Tracks sleep entries, computes sleep debt, analyses patterns, correlates
sleep data with mood and energy, and provides sleep hygiene tips tailored
to mental health conditions.
"""

import logging
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_DIR = Path.home() / ".mindful_organizer"

# Recommended sleep duration (hours) by general guidance
_RECOMMENDED_SLEEP_HOURS = 8.0
_MIN_ACCEPTABLE_HOURS = 6.0
_MAX_ACCEPTABLE_HOURS = 10.0


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SleepEntry:
    """Represents a single night of sleep."""
    id: int | None = None
    date: str = ""                      # ISO date string (YYYY-MM-DD)
    bedtime: str = ""                   # ISO datetime or HH:MM
    wake_time: str = ""                 # ISO datetime or HH:MM
    quality: int = 5                    # 1-10
    duration_hours: float | None = None
    interruptions: int = 0
    interruption_details: str | None = None
    sleep_aids: str | None = None
    dreams: str | None = None
    notes: str | None = None
    created_at: str | None = None

    def __post_init__(self) -> None:
        if self.duration_hours is None and self.bedtime and self.wake_time:
            self.duration_hours = self._calc_duration()

    def _calc_duration(self) -> float:
        """Calculate sleep duration in hours from bedtime and wake_time."""
        try:
            bed = self._parse_time(self.bedtime)
            wake = self._parse_time(self.wake_time)
            if wake <= bed:
                # Crossed midnight
                wake += timedelta(days=1)
            delta = wake - bed
            return round(delta.total_seconds() / 3600, 2)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def _parse_time(raw: str) -> datetime:
        """Parse a time/datetime string leniently."""
        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%H:%M:%S",
            "%H:%M",
        ):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        raise ValueError(f"Cannot parse time: {raw!r}")


@dataclass
class SleepStats:
    """Aggregated sleep statistics over a period."""
    total_entries: int = 0
    mean_duration: float = 0.0
    median_duration: float = 0.0
    stdev_duration: float = 0.0
    mean_quality: float = 0.0
    total_interruptions: int = 0
    mean_interruptions: float = 0.0
    sleep_debt_hours: float = 0.0
    consistency_score: float = 0.0  # 0-100; higher = more consistent
    shortest_night: float = 0.0
    longest_night: float = 0.0


@dataclass
class SleepCorrelation:
    """Result of correlating sleep with another metric."""
    metric_name: str = ""
    data_points: int = 0
    correlation: float = 0.0  # Pearson-like, -1 to 1
    insight: str = ""


# ---------------------------------------------------------------------------
# SleepTracker
# ---------------------------------------------------------------------------

class SleepTracker:
    """Sleep logging and analysis engine.

    Usage::

        from src.core.database import DatabaseManager
        db = DatabaseManager()
        db.initialize()
        st = SleepTracker(db)

        entry_id = st.log_sleep(
            date="2025-12-01",
            bedtime="23:30",
            wake_time="07:15",
            quality=7,
            interruptions=1,
            notes="Woke once around 3am",
        )

        stats = st.get_stats(days=30)
        debt = st.sleep_debt(days=7)
    """

    def __init__(self, db: Any) -> None:
        self._db = db

    def _table(self) -> Any:
        from src.core.database import TableName
        return TableName.SLEEP_LOGS

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def log_sleep(
        self,
        date: str,
        bedtime: str,
        wake_time: str,
        quality: int = 5,
        interruptions: int = 0,
        interruption_details: str | None = None,
        sleep_aids: str | None = None,
        dreams: str | None = None,
        notes: str | None = None,
    ) -> int:
        """Log a sleep entry. Returns the new row id."""
        entry = SleepEntry(
            date=date,
            bedtime=bedtime,
            wake_time=wake_time,
            quality=max(1, min(10, quality)),
            interruptions=interruptions,
            interruption_details=interruption_details,
            sleep_aids=sleep_aids,
            dreams=dreams,
            notes=notes,
        )
        row_id = self._db.insert(
            self._table(),
            date=entry.date,
            bedtime=entry.bedtime,
            wake_time=entry.wake_time,
            quality=entry.quality,
            duration_hours=entry.duration_hours,
            interruptions=entry.interruptions,
            interruption_details=entry.interruption_details,
            sleep_aids=entry.sleep_aids,
            dreams=entry.dreams,
            notes=entry.notes,
        )
        logger.info("Logged sleep for %s (%.1fh, quality %d)", date, entry.duration_hours or 0, entry.quality)
        return int(row_id)

    def get_entry(self, entry_id: int) -> SleepEntry | None:
        row = self._db.get_by_id(self._table(), entry_id)
        if row is None:
            return None
        return self._row_to_entry(row)

    def update_entry(self, entry_id: int, **kwargs: Any) -> int:
        return int(self._db.update(self._table(), entry_id, **kwargs))

    def delete_entry(self, entry_id: int) -> int:
        return int(self._db.delete(self._table(), entry_id))

    def get_entries(
        self,
        days: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
    ) -> list[SleepEntry]:
        """Retrieve sleep entries, optionally filtered by date range."""
        where_parts: list[str] = []
        params: list[Any] = []
        if days is not None:
            cutoff = (datetime.now() - timedelta(days=days)).date().isoformat()
            where_parts.append("date >= ?")
            params.append(cutoff)
        if start_date:
            where_parts.append("date >= ?")
            params.append(start_date)
        if end_date:
            where_parts.append("date <= ?")
            params.append(end_date)
        where = " AND ".join(where_parts)
        result = self._db.query(
            self._table(),
            where=where,
            params=params,
            order_by="date DESC",
            limit=limit,
        )
        return [self._row_to_entry(r) for r in result.rows]

    @staticmethod
    def _row_to_entry(row: dict[str, Any]) -> SleepEntry:
        return SleepEntry(
            id=row.get("id"),
            date=row.get("date", ""),
            bedtime=row.get("bedtime", ""),
            wake_time=row.get("wake_time", ""),
            quality=row.get("quality", 5),
            duration_hours=row.get("duration_hours"),
            interruptions=row.get("interruptions", 0),
            interruption_details=row.get("interruption_details"),
            sleep_aids=row.get("sleep_aids"),
            dreams=row.get("dreams"),
            notes=row.get("notes"),
            created_at=row.get("created_at"),
        )

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def get_stats(self, days: int = 30) -> SleepStats:
        """Compute aggregated sleep statistics for the last *days*."""
        entries = self.get_entries(days=days)
        if not entries:
            return SleepStats()

        durations = [
            e.duration_hours for e in entries
            if e.duration_hours is not None and e.duration_hours > 0
        ]
        qualities = [e.quality for e in entries]
        interruptions = [e.interruptions for e in entries]

        stats = SleepStats(total_entries=len(entries))

        if durations:
            stats.mean_duration = round(statistics.mean(durations), 2)
            stats.median_duration = round(statistics.median(durations), 2)
            stats.shortest_night = round(min(durations), 2)
            stats.longest_night = round(max(durations), 2)
            if len(durations) >= 2:
                stats.stdev_duration = round(statistics.stdev(durations), 2)
                # Consistency: lower stdev = more consistent
                # Scale: stdev of 0 -> 100, stdev >= 3 -> 0
                stats.consistency_score = round(
                    max(0.0, 100.0 - (stats.stdev_duration / 3.0) * 100.0), 1
                )
            else:
                stats.consistency_score = 100.0

        if qualities:
            stats.mean_quality = round(statistics.mean(qualities), 2)

        stats.total_interruptions = sum(interruptions)
        if interruptions:
            stats.mean_interruptions = round(statistics.mean(interruptions), 2)

        # Sleep debt over the period
        if durations:
            stats.sleep_debt_hours = round(
                sum(_RECOMMENDED_SLEEP_HOURS - d for d in durations if d < _RECOMMENDED_SLEEP_HOURS),
                2,
            )

        return stats

    def sleep_debt(self, days: int = 7) -> float:
        """Calculate cumulative sleep debt over *days* (hours).

        Returns a positive number if the user has been sleeping less than
        the recommended amount, zero if at or above recommended.
        """
        entries = self.get_entries(days=days)
        if not entries:
            return 0.0
        total_slept = sum(
            e.duration_hours for e in entries
            if e.duration_hours is not None
        )
        expected = _RECOMMENDED_SLEEP_HOURS * len(entries)
        debt = expected - total_slept
        return round(max(0.0, debt), 2)

    def duration_trend(self, days: int = 30) -> list[tuple[str, float]]:
        """Return (date, duration_hours) pairs for trend charting."""
        entries = self.get_entries(days=days)
        entries.reverse()  # chronological order
        return [
            (e.date, e.duration_hours or 0.0)
            for e in entries
        ]

    def quality_trend(self, days: int = 30) -> list[tuple[str, int]]:
        """Return (date, quality) pairs for trend charting."""
        entries = self.get_entries(days=days)
        entries.reverse()
        return [(e.date, e.quality) for e in entries]

    # ------------------------------------------------------------------
    # Correlations
    # ------------------------------------------------------------------

    def correlate_with_mood(
        self, mood_data: list[dict[str, Any]], days: int = 30,
    ) -> SleepCorrelation:
        """Correlate sleep quality/duration with mood scores.

        Args:
            mood_data: List of dicts with at least ``timestamp`` (or ``date``)
                       and ``mood_score`` keys.
            days: Number of recent days to consider.
        """
        entries = self.get_entries(days=days)
        sleep_by_date: dict[str, SleepEntry] = {}
        for e in entries:
            sleep_by_date[e.date] = e

        pairs: list[tuple[float, float]] = []
        for m in mood_data:
            d = (m.get("timestamp") or m.get("date", ""))[:10]
            if d in sleep_by_date and sleep_by_date[d].duration_hours is not None:
                score = m.get("mood_score")
                if score is not None:
                    pairs.append((sleep_by_date[d].duration_hours, float(score)))  # type: ignore[arg-type]

        if len(pairs) < 3:
            return SleepCorrelation(
                metric_name="mood",
                data_points=len(pairs),
                insight="Not enough overlapping data to calculate a correlation.",
            )

        r = self._pearson([p[0] for p in pairs], [p[1] for p in pairs])
        insight = self._interpret_correlation(r, "sleep duration", "mood")
        return SleepCorrelation(
            metric_name="mood",
            data_points=len(pairs),
            correlation=round(r, 3),
            insight=insight,
        )

    def correlate_with_energy(
        self, energy_data: list[dict[str, Any]], days: int = 30,
    ) -> SleepCorrelation:
        """Correlate sleep quality/duration with energy levels.

        Args:
            energy_data: List of dicts with ``timestamp`` and ``energy_level``.
        """
        entries = self.get_entries(days=days)
        sleep_by_date: dict[str, SleepEntry] = {}
        for e in entries:
            sleep_by_date[e.date] = e

        pairs: list[tuple[float, float]] = []
        for en in energy_data:
            d = (en.get("timestamp") or en.get("date", ""))[:10]
            if d in sleep_by_date and sleep_by_date[d].duration_hours is not None:
                level = en.get("energy_level")
                if level is not None:
                    pairs.append((sleep_by_date[d].duration_hours, float(level)))  # type: ignore[arg-type]

        if len(pairs) < 3:
            return SleepCorrelation(
                metric_name="energy",
                data_points=len(pairs),
                insight="Not enough overlapping data to calculate a correlation.",
            )

        r = self._pearson([p[0] for p in pairs], [p[1] for p in pairs])
        insight = self._interpret_correlation(r, "sleep duration", "energy")
        return SleepCorrelation(
            metric_name="energy",
            data_points=len(pairs),
            correlation=round(r, 3),
            insight=insight,
        )

    # ------------------------------------------------------------------
    # Sleep hygiene tips
    # ------------------------------------------------------------------

    def get_tips(self, days: int = 14) -> list[str]:
        """Generate personalised sleep hygiene tips based on recent patterns."""
        stats = self.get_stats(days=days)
        tips: list[str] = []

        if stats.total_entries == 0:
            tips.append("Start logging your sleep to receive personalised tips.")
            return tips

        if stats.mean_duration < _MIN_ACCEPTABLE_HOURS:
            tips.append(
                "Your average sleep is below 6 hours. Try setting a consistent "
                "bedtime 30 minutes earlier this week."
            )
        elif stats.mean_duration > _MAX_ACCEPTABLE_HOURS:
            tips.append(
                "Sleeping over 10 hours regularly can indicate underlying issues. "
                "Consider discussing this with your healthcare provider."
            )

        if stats.consistency_score < 50:
            tips.append(
                "Your sleep schedule is inconsistent. Going to bed and waking "
                "up at the same time each day can improve sleep quality."
            )

        if stats.mean_quality < 5:
            tips.append(
                "Your sleep quality has been low. Consider limiting screen time "
                "30 minutes before bed and keeping your room cool and dark."
            )

        if stats.mean_interruptions > 2:
            tips.append(
                "Frequent night-time waking was detected. Avoiding caffeine "
                "after 2pm and heavy meals before bed may help."
            )

        if stats.sleep_debt_hours > 5:
            tips.append(
                f"You have accumulated ~{stats.sleep_debt_hours}h of sleep debt. "
                "Try to recover gradually with an extra 30 minutes of sleep."
            )

        if not tips:
            tips.append(
                "Your sleep looks healthy! Keep up the good routine."
            )

        return tips

    def get_condition_insights(self, condition: str) -> list[str]:
        """Return sleep insights tailored to a specific mental health condition."""
        condition_upper = condition.upper()
        insights: list[str] = []

        if condition_upper == "ADHD":
            insights.extend([
                "ADHD often causes delayed sleep onset. A wind-down routine "
                "starting 1 hour before bed can help signal your brain to relax.",
                "Stimulant medications can affect sleep if taken too late. "
                "Track your medication timing alongside sleep quality.",
                "White noise or gentle background sounds can help an active "
                "ADHD mind settle at bedtime.",
                "Consider a consistent 'launch pad' routine at night: lay out "
                "tomorrow's essentials to reduce bedtime anxiety.",
            ])
        elif condition_upper == "ANXIETY":
            insights.extend([
                "Anxiety-driven insomnia is common. A breathing exercise or "
                "body scan before bed can help calm racing thoughts.",
                "Keep a 'worry journal' by your bed - writing down concerns "
                "before sleeping can stop thought loops.",
                "Avoid checking the clock when you wake at night; it can "
                "increase anxiety about sleep loss.",
                "Progressive muscle relaxation (tensing and releasing each "
                "muscle group) is evidence-based for sleep-onset anxiety.",
            ])
        elif condition_upper == "DEPRESSION":
            insights.extend([
                "Depression can cause both insomnia and hypersomnia. "
                "Tracking your hours helps identify which pattern is present.",
                "If you find yourself sleeping excessively, setting a gentle "
                "morning alarm and opening curtains can help regulate mood.",
                "Morning light exposure for 15-30 minutes supports circadian "
                "rhythm, which is often disrupted in depression.",
                "Avoid napping longer than 20 minutes during the day, as it "
                "can worsen nighttime sleep for depression.",
            ])
        elif condition_upper == "PTSD":
            insights.extend([
                "Nightmares are common with PTSD. If recurrent, consider "
                "discussing Image Rehearsal Therapy with your therapist.",
                "A sense of safety at bedtime is important. Ensure your "
                "sleeping environment feels secure and comfortable.",
                "Grounding techniques (5-4-3-2-1 senses) before bed can "
                "reduce hypervigilance that disrupts sleep.",
                "Avoid sleeping in complete darkness if it triggers distress; "
                "a dim night-light is perfectly acceptable.",
            ])
        elif condition_upper == "OCD":
            insights.extend([
                "Bedtime rituals can become compulsive. Set a time limit for "
                "your pre-sleep routine and practise flexibility.",
                "If intrusive thoughts increase at bedtime, a brief "
                "mindfulness exercise can create distance from the thoughts.",
                "Avoid 'checking' behaviours related to sleep (e.g. "
                "repeatedly checking the alarm) by using a single, trusted system.",
            ])
        else:
            insights.append(
                "Good sleep hygiene benefits everyone: keep a consistent "
                "schedule, limit caffeine, and create a dark, cool sleeping space."
            )

        return insights

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pearson(x: list[float], y: list[float]) -> float:
        """Compute Pearson correlation coefficient between two lists."""
        from src.utils.statistics import pearson_correlation

        return pearson_correlation(x, y)

    @staticmethod
    def _interpret_correlation(r: float, label_x: str, label_y: str) -> str:
        abs_r = abs(r)
        if abs_r < 0.2:
            strength = "very weak"
        elif abs_r < 0.4:
            strength = "weak"
        elif abs_r < 0.6:
            strength = "moderate"
        elif abs_r < 0.8:
            strength = "strong"
        else:
            strength = "very strong"

        direction = "positive" if r >= 0 else "negative"
        return (
            f"There is a {strength} {direction} correlation (r={r:.2f}) "
            f"between {label_x} and {label_y}."
        )
