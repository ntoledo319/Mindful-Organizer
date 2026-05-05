"""
WellnessOrchestrator -- cross-module intelligence for Mindful Organizer.

Aggregates data from mood, sleep, energy, medication, and task modules
to surface unified insights, detect crisis patterns, and wire together
the app's core mental-health-aware productivity features.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np

from core.constants import Condition
from core.database import DatabaseManager, TableName

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class WellnessSnapshot:
    """A point-in-time view of the user's wellness state."""

    timestamp: datetime
    mood_score: float | None = None
    energy_score: float | None = None
    sleep_hours: float | None = None
    sleep_quality: int | None = None
    medication_adherence: float | None = None  # 0.0-1.0
    tasks_completed_today: int = 0
    tasks_pending: int = 0
    spoons_remaining: float | None = None


@dataclass
class CrisisSignal:
    """A detected pattern that suggests the user may need extra support."""

    severity: str  # "info", "mild", "moderate", "urgent"
    source_modules: list[str]
    description: str
    recommendation: str
    triggered_at: datetime = field(default_factory=datetime.now)


@dataclass
class DailyBriefing:
    """Morning wellness briefing with actionable suggestions."""

    date: date
    energy_forecast: str | None
    task_recommendations: list[dict[str, Any]]
    wellness_insights: list[str]
    crisis_signals: list[CrisisSignal]
    suggested_skill: str | None = None


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class WellnessOrchestrator:
    """Aggregates cross-module wellness data and produces unified insights.

    This class is the missing link between the app's siloed wellness
    modules.  It reads from the canonical SQLite store, applies
    evidence-based heuristics, and returns structured recommendations
    that the GUI layer can display without reaching into private
    manager internals.
    """

    def __init__(self, db: DatabaseManager | None = None) -> None:
        self.db = db or DatabaseManager()
        self.db.initialize()

    # -- data ingestion ---------------------------------------------------

    def snapshot(self, dt: datetime | None = None) -> WellnessSnapshot:
        """Build a wellness snapshot for the given time (defaults to now)."""
        dt = dt or datetime.now()

        # Latest mood
        moods = self.db.query(
            TableName.MOOD_ENTRIES,
            order_by="timestamp DESC",
            limit=1,
        )
        mood_score = moods.rows[0].get("mood_score") if moods.rows else None

        # Latest energy
        energies = self.db.query(
            TableName.ENERGY_READINGS,
            order_by="timestamp DESC",
            limit=1,
        )
        energy_score = energies.rows[0].get("energy_level") if energies.rows else None

        # Latest sleep
        sleeps = self.db.query(
            TableName.SLEEP_LOGS,
            order_by="date DESC",
            limit=1,
        )
        sleep_hours = sleeps.rows[0].get("duration_hours") if sleeps.rows else None
        sleep_quality = sleeps.rows[0].get("quality") if sleeps.rows else None

        # Medication today
        meds = self.db.query(
            TableName.MEDICATION_LOGS,
            where="date(scheduled_time) = date(?)",
            params=(dt.isoformat(),),
        )
        if meds.rows:
            taken = sum(1 for m in meds.rows if m.get("status") == "taken")
            adherence = taken / len(meds.rows)
        else:
            adherence = None

        # Tasks today
        tasks_today = self.db.query(
            TableName.TASKS,
            where="date(completed_at) = date(?) AND completed = 1",
            params=(dt.isoformat(),),
        )
        pending_tasks = self.db.query(
            TableName.TASKS,
            where="completed = 0",
        )

        return WellnessSnapshot(
            timestamp=dt,
            mood_score=mood_score,
            energy_score=energy_score,
            sleep_hours=sleep_hours,
            sleep_quality=sleep_quality,
            medication_adherence=adherence,
            tasks_completed_today=tasks_today.row_count,
            tasks_pending=pending_tasks.row_count,
        )

    # -- cross-module insights ---------------------------------------------

    def detect_crisis_signals(
        self,
        conditions: Sequence[Condition] | None = None,
    ) -> list[CrisisSignal]:
        """Detect patterns that suggest the user may need extra support.

        Heuristics are deliberately conservative — they flag *observations*
        rather than making definitive claims.
        """
        signals: list[CrisisSignal] = []
        condition_names = {c.name.lower() for c in (conditions or [])}

        avg_sleep: float | None = None

        # --- Mood crash + sleep deprivation ---
        recent_moods = self.db.query(
            TableName.MOOD_ENTRIES,
            where="timestamp >= datetime('now', '-3 days')",
            order_by="timestamp DESC",
        )
        if recent_moods.rows:
            mood_values = [r["mood_score"] for r in recent_moods.rows if r.get("mood_score")]
            avg_mood = np.mean(mood_values) if mood_values else None

            recent_sleep = self.db.query(
                TableName.SLEEP_LOGS,
                where="date >= date('now', '-3 days')",
                order_by="date DESC",
            )
            sleep_values = [r["duration_hours"] for r in recent_sleep.rows if r.get("duration_hours")]
            avg_sleep = np.mean(sleep_values) if sleep_values else None

            if avg_mood is not None and avg_mood <= 3.5 and avg_sleep is not None and avg_sleep < 5:
                signals.append(CrisisSignal(
                    severity="moderate",
                    source_modules=["mood", "sleep"],
                    description=(
                        "Your mood has been low and sleep has been short "
                        f"over the past few days (avg mood {avg_mood:.1f}, "
                        f"avg sleep {avg_sleep:.1f}h)."
                    ),
                    recommendation=(
                        "Consider your crisis plan, reach out to a trusted "
                        "contact, and prioritise rest over productivity today."
                    ),
                ))

            # --- Rapid mood drop ---
            if len(mood_values) >= 2:
                latest = mood_values[0]
                previous = mood_values[1]
                if previous - latest >= 4:
                    signals.append(CrisisSignal(
                        severity="mild",
                        source_modules=["mood"],
                        description=f"Your mood dropped from {previous} to {latest} recently.",
                        recommendation=(
                            "A grounding exercise or brief walk may help stabilise "
                            "your emotional baseline."
                        ),
                    ))

        # --- Medication miss streak ---
        missed_meds = self.db.query(
            TableName.MEDICATION_LOGS,
            where="status = 'missed' AND scheduled_time >= datetime('now', '-7 days')",
        )
        if missed_meds.row_count >= 3:
            signals.append(CrisisSignal(
                severity="mild",
                source_modules=["medication"],
                description=f"{missed_meds.row_count} medications missed in the last week.",
                recommendation="Set a consistent reminder time tied to a daily habit.",
            ))

        # --- Bipolar: elevated energy without sleep ---
        if "bipolar" in condition_names:
            energys = self.db.query(
                TableName.ENERGY_READINGS,
                where="timestamp >= datetime('now', '-7 days')",
                order_by="timestamp DESC",
            )
            if energys.rows:
                energy_vals = [r["energy_level"] for r in energys.rows if r.get("energy_level")]
                if energy_vals and np.mean(energy_vals) >= 8 and (avg_sleep is not None and avg_sleep < 5):
                    signals.append(CrisisSignal(
                        severity="info",
                        source_modules=["energy", "sleep"],
                        description=(
                            "High energy combined with low sleep over the past week. "
                            "If this feels unusual, note it for your clinician."
                        ),
                        recommendation="Maintain consistent sleep timing and avoid overstimulation.",
                    ))

        return signals

    # -- daily briefing ----------------------------------------------------

    def daily_briefing(
        self,
        conditions: Sequence[Condition] | None = None,
        max_tasks: int = 5,
    ) -> DailyBriefing:
        """Generate a morning briefing with task and wellness recommendations."""
        today = date.today()
        signals = self.detect_crisis_signals(conditions)
        insights: list[str] = []

        # Energy forecast text
        snapshot = self.snapshot()
        energy_forecast: str | None = None
        if snapshot.energy_score is not None:
            if snapshot.energy_score >= 7:
                energy_forecast = "Your energy is high — a good day for challenging tasks."
            elif snapshot.energy_score >= 4:
                energy_forecast = "Moderate energy — balance effort with rest."
            else:
                energy_forecast = "Low energy today — prioritise self-care and small wins."

        # Sleep → energy insight
        if snapshot.sleep_hours is not None and snapshot.sleep_hours < 6:
            insights.append(
                f"You slept {snapshot.sleep_hours:.1f} hours. "
                "Consider pacing yourself and a 20-minute nap if possible."
            )

        # Medication insight
        if snapshot.medication_adherence is not None and snapshot.medication_adherence < 1.0:
            insights.append("Don't forget today's medications — consistency supports stability.")

        # Suggested skill based on conditions
        suggested_skill: str | None = None
        condition_names = {c.name.lower() for c in (conditions or [])}
        if "anxiety" in condition_names or "panic" in condition_names:
            suggested_skill = "4-7-8 Breathing"
        elif "depression" in condition_names:
            suggested_skill = "Behavioral Activation (one small activity)"
        elif "adhd" in condition_names:
            suggested_skill = "Body Doubling or Pomodoro"
        elif "ptsd" in condition_names:
            suggested_skill = "Safe Place Visualization"

        # Task recommendations (low-energy-first if energy is low)
        tasks = self.db.query(
            TableName.TASKS,
            where="completed = 0",
            order_by="energy_required ASC",
            limit=max_tasks,
        )
        task_recs: list[dict[str, Any]] = []
        for t in tasks.rows:
            task_recs.append({
                "id": t["id"],
                "title": t["title"],
                "energy_required": t.get("energy_required", 5),
                "priority": t.get("priority", "medium"),
                "due_date": t.get("due_date"),
            })

        return DailyBriefing(
            date=today,
            energy_forecast=energy_forecast,
            task_recommendations=task_recs,
            wellness_insights=insights,
            crisis_signals=signals,
            suggested_skill=suggested_skill,
        )

    # -- unified export ----------------------------------------------------

    def wellness_summary(
        self,
        days: int = 30,
    ) -> dict[str, Any]:
        """Export a unified wellness summary for personal reflection.

        Includes mood trends, sleep averages, medication adherence,
        task completion rates, and wellness signals.
        """
        since = datetime.now() - timedelta(days=days)

        # Mood
        moods = self.db.query(
            TableName.MOOD_ENTRIES,
            where="timestamp >= ?",
            params=(since.isoformat(),),
            order_by="timestamp ASC",
        )
        mood_values = [r["mood_score"] for r in moods.rows if r.get("mood_score")]

        # Energy
        energies = self.db.query(
            TableName.ENERGY_READINGS,
            where="timestamp >= ?",
            params=(since.isoformat(),),
            order_by="timestamp ASC",
        )
        energy_values = [r["energy_level"] for r in energies.rows if r.get("energy_level")]

        # Sleep
        sleeps = self.db.query(
            TableName.SLEEP_LOGS,
            where="date >= date(?)",
            params=(since.isoformat(),),
            order_by="date ASC",
        )
        sleep_hours = [r["duration_hours"] for r in sleeps.rows if r.get("duration_hours")]

        # Medication adherence
        meds = self.db.query(
            TableName.MEDICATION_LOGS,
            where="scheduled_time >= ?",
            params=(since.isoformat(),),
        )
        med_statuses = [r["status"] for r in meds.rows if r.get("status")]
        adherence = (
            med_statuses.count("taken") / len(med_statuses)
            if med_statuses else None
        )

        # Tasks
        tasks = self.db.query(
            TableName.TASKS,
            where="created_at >= ?",
            params=(since.isoformat(),),
        )
        completed = sum(1 for r in tasks.rows if r.get("completed"))
        total = tasks.row_count

        return {
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "mood": {
                "count": len(mood_values),
                "average": round(float(np.mean(mood_values)), 2) if mood_values else None,
                "trend": "improving" if len(mood_values) >= 7 and np.polyfit(range(len(mood_values)), mood_values, 1)[0] > 0.05 else
                         "declining" if len(mood_values) >= 7 and np.polyfit(range(len(mood_values)), mood_values, 1)[0] < -0.05 else
                         "stable",
            },
            "energy": {
                "count": len(energy_values),
                "average": round(float(np.mean(energy_values)), 2) if energy_values else None,
            },
            "sleep": {
                "count": len(sleep_hours),
                "average_hours": round(float(np.mean(sleep_hours)), 2) if sleep_hours else None,
            },
            "medication": {
                "total_scheduled": len(med_statuses),
                "adherence_rate": round(adherence, 2) if adherence is not None else None,
            },
            "tasks": {
                "total": total,
                "completed": completed,
                "completion_rate": round(completed / total, 2) if total else None,
            },
            "crisis_signals": [
                {
                    "severity": s.severity,
                    "description": s.description,
                    "recommendation": s.recommendation,
                }
                for s in self.detect_crisis_signals()
            ],
        }
