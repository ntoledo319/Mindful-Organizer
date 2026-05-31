"""
Smart, context-aware notification engine for Mindful Organizer.

Goes beyond dumb reminders — it reads wellness data and suggests actions
based on energy patterns, sleep debt, medication adherence, and task context.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, time
from pathlib import Path

from core.database import DatabaseManager, TableName
from core.wellness_orchestrator import WellnessOrchestrator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class SmartNotification:
    """A context-aware notification."""

    id: str
    title: str
    message: str
    priority: str  # info, mild, moderate, urgent
    category: str  # energy, sleep, medication, task, crisis, general
    suggested_action: str | None = None
    dismiss_until: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class SmartNotificationEngine:
    """Generates notifications based on wellness patterns and task context."""

    def __init__(
        self,
        db: DatabaseManager | None = None,
        orchestrator: WellnessOrchestrator | None = None,
        data_dir: Path | None = None,
    ) -> None:
        self.db = db
        if self.db is not None:
            self.db.initialize()
        self.orchestrator = orchestrator
        if self.orchestrator is None and self.db is not None:
            self.orchestrator = WellnessOrchestrator(self.db)
        elif self.orchestrator is None and data_dir is not None:
            self.orchestrator = WellnessOrchestrator(data_dir=data_dir)

    def generate_notifications(
        self,
        conditions: list[str] | None = None,
    ) -> list[SmartNotification]:
        """Generate all relevant notifications for the current moment."""
        notifications: list[SmartNotification] = []
        now = datetime.now()

        # Get latest snapshot
        if self.orchestrator is None:
            return notifications

        snapshot = self.orchestrator.snapshot(now)

        # Energy-based task suggestion
        if snapshot.energy_score is not None:
            if snapshot.energy_score >= 7 and snapshot.tasks_pending > 0:
                notifications.append(
                    SmartNotification(
                        id="energy_peak_task",
                        title="Energy Peak Detected",
                        message=(
                            "Your energy is high right now. "
                            f"You have {snapshot.tasks_pending} pending tasks — "
                            "consider tackling the hardest one."
                        ),
                        priority="info",
                        category="energy",
                        suggested_action="open_tasks",
                    )
                )
            elif snapshot.energy_score <= 3 and snapshot.tasks_pending > 3:
                notifications.append(
                    SmartNotification(
                        id="energy_low_trim",
                        title="Low Energy — Gentle Mode",
                        message=(
                            "Your energy is low. Consider trimming today's list "
                            "to 1-2 small tasks and prioritising rest."
                        ),
                        priority="mild",
                        category="energy",
                        suggested_action="trim_tasks",
                    )
                )

        # Sleep debt warning
        if snapshot.sleep_hours is not None and snapshot.sleep_hours < 5:
            notifications.append(
                SmartNotification(
                    id="sleep_debt",
                    title="Sleep Debt Alert",
                    message=(
                        f"You slept {snapshot.sleep_hours:.1f} hours. "
                        "Low sleep affects mood and focus — pace yourself today."
                    ),
                    priority="mild",
                    category="sleep",
                    suggested_action="breathing",
                )
            )

        # Medication reminder with adherence context
        if (
            self.db is not None
            and snapshot.medication_adherence is not None
            and snapshot.medication_adherence < 1.0
        ):
            missed = self.db.query(
                TableName.MEDICATION_LOGS,
                where="status = 'missed' AND date(scheduled_time) = date('now')",
            )
            if missed.row_count > 0:
                notifications.append(
                    SmartNotification(
                        id="med_missed",
                        title="Medication Reminder",
                        message=(
                            "You have missed medications today. Consistency supports stability."
                        ),
                        priority="moderate",
                        category="medication",
                        suggested_action="open_medication",
                    )
                )

        # Morning briefing (only 6-10 AM)
        if time(6, 0) <= now.time() <= time(10, 0):
            briefing = self.orchestrator.daily_briefing(
                conditions=conditions,
                max_tasks=3,
            )
            if briefing.crisis_signals:
                # crisis_signals are ordered most-severe-first by the orchestrator.
                # For urgent/moderate signals include the recommendation so the
                # 988 lifeline text rides along with the notification itself.
                sig = briefing.crisis_signals[0]
                message = sig.description
                if sig.severity in ("urgent", "moderate"):
                    message = f"{sig.description}\n{sig.recommendation}"
                notifications.append(
                    SmartNotification(
                        id="crisis_signal",
                        title="Wellness Check-In",
                        message=message,
                        priority=sig.severity,
                        category="crisis",
                        suggested_action="open_crisis_plan",
                    )
                )
            elif briefing.suggested_skill:
                notifications.append(
                    SmartNotification(
                        id="morning_briefing",
                        title="Today's Suggestion",
                        message=(
                            f"{briefing.energy_forecast}\n"
                            f"Suggested skill: {briefing.suggested_skill}"
                        ),
                        priority="info",
                        category="general",
                        suggested_action="open_breathing",
                    )
                )

        # ADHD transition support (3:00-3:30 PM slump)
        if (
            conditions
            and "adhd" in [c.lower() for c in conditions]
            and time(15, 0) <= now.time() <= time(15, 30)
        ):
            notifications.append(
                SmartNotification(
                    id="adhd_afternoon",
                    title="Afternoon Transition",
                    message=(
                        "The afternoon slump is common with ADHD. "
                        "Take a 5-minute movement break before your next task."
                    ),
                    priority="info",
                    category="energy",
                    suggested_action="breathing",
                )
            )

        # Depression behavioral activation nudge
        if (
            conditions
            and "depression" in [c.lower() for c in conditions]
            and snapshot.tasks_completed_today == 0
            and now.hour >= 14
        ):
            notifications.append(
                SmartNotification(
                    id="depression_activation",
                    title="Small Win Opportunity",
                    message=(
                        "No tasks completed yet today. "
                        "Even one tiny action counts — choose the easiest task."
                    ),
                    priority="mild",
                    category="task",
                    suggested_action="open_tasks",
                )
            )

        return notifications
