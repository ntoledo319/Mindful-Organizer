"""
Values-based weekly review for ACT (Acceptance and Commitment Therapy) integration.

Tracks which personal values received attention through aligned tasks
and generates a weekly values report with visualisations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from core.database import DatabaseManager, TableName

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ValueScore:
    """Score for a single personal value."""
    value_name: str
    tasks_aligned: int = 0
    time_estimate_minutes: int = 0
    energy_invested: float = 0.0
    last_week_tasks: int = 0
    trend: str = "stable"  # improving, declining, stable, new


@dataclass
class WeeklyValuesReport:
    """Complete weekly values review."""
    week_start: date
    week_end: date
    value_scores: list[ValueScore] = field(default_factory=list)
    top_value: str | None = None
    neglected_value: str | None = None
    insights: list[str] = field(default_factory=list)
    suggested_action: str | None = None


# ---------------------------------------------------------------------------
# Tracker
# ---------------------------------------------------------------------------

class ValuesTracker:
    """Track and report on values-aligned task completion."""

    # Common ACT values
    DEFAULT_VALUES = [
        "Family", "Friendship", "Health", "Career", "Creativity",
        "Learning", "Community", "Nature", "Spirituality", "Fun",
        "Independence", "Security", "Authenticity", "Kindness",
    ]

    def __init__(self, db: DatabaseManager | None = None) -> None:
        self.db = db or DatabaseManager()
        self.db.initialize()

    def generate_weekly_report(
        self,
        user_values: list[str] | None = None,
        week_start: date | None = None,
    ) -> WeeklyValuesReport:
        """Generate a values report for the given week."""
        week_start = week_start or (date.today() - timedelta(days=date.today().weekday()))
        week_end = week_start + timedelta(days=6)

        values = user_values or self.DEFAULT_VALUES

        # Current week tasks
        current_tasks = self.db.query(
            TableName.TASKS,
            where="completed = 1 AND completed_at >= ? AND completed_at <= ?",
            params=(week_start.isoformat(), week_end.isoformat()),
        )

        # Previous week for trend comparison
        prev_start = week_start - timedelta(days=7)
        prev_end = week_start - timedelta(days=1)
        prev_tasks = self.db.query(
            TableName.TASKS,
            where="completed = 1 AND completed_at >= ? AND completed_at <= ?",
            params=(prev_start.isoformat(), prev_end.isoformat()),
        )

        # Score each value
        scores: list[ValueScore] = []
        for val in values:
            current_count = sum(
                1 for t in current_tasks.rows
                if t.get("values_alignment", "").lower() == val.lower()
            )
            prev_count = sum(
                1 for t in prev_tasks.rows
                if t.get("values_alignment", "").lower() == val.lower()
            )

            energy = sum(
                t.get("energy_required", 5)
                for t in current_tasks.rows
                if t.get("values_alignment", "").lower() == val.lower()
            )

            trend = "stable"
            if current_count > prev_count:
                trend = "improving"
            elif current_count < prev_count:
                trend = "declining"
            elif current_count > 0 and prev_count == 0:
                trend = "new"

            scores.append(ValueScore(
                value_name=val,
                tasks_aligned=current_count,
                energy_invested=energy,
                last_week_tasks=prev_count,
                trend=trend,
            ))

        # Determine top and neglected
        scored_values = [s for s in scores if s.tasks_aligned > 0]
        if scored_values:
            top = max(scored_values, key=lambda s: s.tasks_aligned)
            top_value = top.value_name
        else:
            top_value = None

        neglected_candidates = [s for s in scores if s.tasks_aligned == 0]
        if neglected_candidates:
            # Pick a value that was active in previous weeks
            previously_active = [
                s for s in neglected_candidates if s.last_week_tasks > 0
            ]
            if previously_active:
                neglected_value = previously_active[0].value_name
            else:
                neglected_value = neglected_candidates[0].value_name
        else:
            neglected_value = None

        # Generate insights
        insights: list[str] = []
        if top_value:
            insights.append(
                f"'{top_value}' received the most attention this week "
                f"({top.tasks_aligned} tasks)."
            )
        if neglected_value:
            insights.append(
                f"'{neglected_value}' had no aligned tasks this week. "
                f"Consider scheduling one small action."
            )

        # Suggested action
        suggested_action = None
        if neglected_value:
            suggested_action = (
                f"Add one small task aligned with '{neglected_value}' "
                f"for next week — even 15 minutes counts."
            )

        return WeeklyValuesReport(
            week_start=week_start,
            week_end=week_end,
            value_scores=scores,
            top_value=top_value,
            neglected_value=neglected_value,
            insights=insights,
            suggested_action=suggested_action,
        )
