"""
Medication tracking for Mindful Organizer.

Logs medications, tracks adherence, schedules reminders, records side effects,
correlates with mood, manages refill reminders, and exports history.

DISCLAIMER: This module is a personal tracking tool. It does NOT provide
medical advice, diagnosis, or treatment recommendations. Always consult a
qualified healthcare professional regarding medications.
"""

import json
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta, time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

DATA_DIR = Path.home() / ".mindful_optimizer"

MEDICAL_DISCLAIMER = (
    "DISCLAIMER: This is a personal tracking tool only. It does NOT provide "
    "medical advice, diagnosis, or treatment recommendations. Always consult "
    "your prescribing physician or pharmacist for medical guidance."
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MedicationStatus(Enum):
    TAKEN = "taken"
    MISSED = "missed"
    LATE = "late"
    SKIPPED = "skipped"
    PENDING = "pending"


class Frequency(Enum):
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily"
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"
    EVERY_OTHER_DAY = "every_other_day"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"
    CUSTOM = "custom"

    @property
    def doses_per_day(self) -> float:
        """Approximate daily dose count for supply calculations."""
        return {
            "once_daily": 1.0,
            "twice_daily": 2.0,
            "three_times_daily": 3.0,
            "four_times_daily": 4.0,
            "every_other_day": 0.5,
            "weekly": 1 / 7,
            "as_needed": 0.0,
            "custom": 0.0,
        }.get(self.value, 0.0)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Medication:
    """Represents a medication the user is tracking."""
    name: str
    dosage: str
    frequency: str          # Frequency.value or free-form text
    scheduled_time: str     # HH:MM or ISO time
    prescriber: Optional[str] = None
    supply_count: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class MedicationLogEntry:
    """A single log of taking (or missing) a medication."""
    id: Optional[int] = None
    medication_name: str = ""
    dosage: str = ""
    frequency: str = ""
    scheduled_time: str = ""
    taken_time: Optional[str] = None
    status: str = MedicationStatus.PENDING.value
    side_effects: Optional[str] = None
    notes: Optional[str] = None
    supply_count: Optional[int] = None
    prescriber: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class AdherenceStats:
    """Summary of medication adherence over a period."""
    medication_name: str = ""
    total_logs: int = 0
    taken: int = 0
    missed: int = 0
    late: int = 0
    skipped: int = 0
    adherence_percent: float = 0.0
    on_time_percent: float = 0.0


@dataclass
class SideEffectSummary:
    """Aggregated side-effect information for one medication."""
    medication_name: str = ""
    total_reports: int = 0
    effects: Dict[str, int] = field(default_factory=dict)  # effect -> count


@dataclass
class MoodCorrelation:
    """Correlation between medication adherence and mood."""
    medication_name: str = ""
    data_points: int = 0
    taken_mood_avg: float = 0.0
    missed_mood_avg: float = 0.0
    insight: str = ""


# ---------------------------------------------------------------------------
# MedicationTracker
# ---------------------------------------------------------------------------

class MedicationTracker:
    """Medication logging and adherence analysis.

    Usage::

        from src.core.database import DatabaseManager
        db = DatabaseManager()
        db.initialize()
        mt = MedicationTracker(db)

        # Log a dose
        mt.log_dose("Sertraline", "50mg", "once_daily", "08:00", status="taken")

        # Check adherence
        stats = mt.adherence("Sertraline", days=30)
        print(f"Adherence: {stats.adherence_percent}%")
    """

    DISCLAIMER = MEDICAL_DISCLAIMER

    def __init__(self, db: Any) -> None:
        self._db = db

    def _table(self) -> Any:
        from src.core.database import TableName
        return TableName.MEDICATION_LOGS

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def log_dose(
        self,
        medication_name: str,
        dosage: str,
        frequency: str,
        scheduled_time: str,
        *,
        taken_time: Optional[str] = None,
        status: str = "pending",
        side_effects: Optional[str] = None,
        notes: Optional[str] = None,
        supply_count: Optional[int] = None,
        prescriber: Optional[str] = None,
    ) -> int:
        """Record a medication event. Returns the new row id."""
        # Normalise status
        try:
            status = MedicationStatus(status).value
        except ValueError:
            status = MedicationStatus.PENDING.value

        row_id = self._db.insert(
            self._table(),
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            scheduled_time=scheduled_time,
            taken_time=taken_time,
            status=status,
            side_effects=side_effects,
            notes=notes,
            supply_count=supply_count,
            prescriber=prescriber,
        )
        logger.info("Logged %s dose: %s (%s)", medication_name, status, dosage)
        return row_id

    def mark_taken(
        self,
        log_id: int,
        taken_time: Optional[str] = None,
    ) -> int:
        """Mark an existing pending log as taken."""
        now = taken_time or datetime.now().isoformat()
        return self._db.update(
            self._table(), log_id, status=MedicationStatus.TAKEN.value, taken_time=now,
        )

    def mark_missed(self, log_id: int) -> int:
        return self._db.update(
            self._table(), log_id, status=MedicationStatus.MISSED.value,
        )

    def mark_late(self, log_id: int, taken_time: Optional[str] = None) -> int:
        now = taken_time or datetime.now().isoformat()
        return self._db.update(
            self._table(), log_id, status=MedicationStatus.LATE.value, taken_time=now,
        )

    def mark_skipped(self, log_id: int, notes: Optional[str] = None) -> int:
        kwargs: Dict[str, Any] = {"status": MedicationStatus.SKIPPED.value}
        if notes:
            kwargs["notes"] = notes
        return self._db.update(self._table(), log_id, **kwargs)

    def get_log(self, log_id: int) -> Optional[MedicationLogEntry]:
        row = self._db.get_by_id(self._table(), log_id)
        return self._row_to_entry(row) if row else None

    def update_log(self, log_id: int, **kwargs: Any) -> int:
        return self._db.update(self._table(), log_id, **kwargs)

    def delete_log(self, log_id: int) -> int:
        return self._db.delete(self._table(), log_id)

    def get_logs(
        self,
        medication_name: Optional[str] = None,
        days: Optional[int] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[MedicationLogEntry]:
        """Retrieve medication logs with optional filters."""
        where_parts: List[str] = []
        params: List[Any] = []
        if medication_name:
            where_parts.append("medication_name = ?")
            params.append(medication_name)
        if days is not None:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            where_parts.append("created_at >= ?")
            params.append(cutoff)
        if status:
            where_parts.append("status = ?")
            params.append(status)
        where = " AND ".join(where_parts)
        result = self._db.query(
            self._table(),
            where=where,
            params=params,
            order_by="created_at DESC",
            limit=limit,
        )
        return [self._row_to_entry(r) for r in result.rows]

    def get_medications(self) -> List[str]:
        """Return distinct medication names currently being tracked."""
        result = self._db.query(
            self._table(), columns="DISTINCT medication_name",
        )
        return [r["medication_name"] for r in result.rows]

    # ------------------------------------------------------------------
    # Adherence
    # ------------------------------------------------------------------

    def adherence(
        self, medication_name: Optional[str] = None, days: int = 30,
    ) -> AdherenceStats:
        """Calculate adherence statistics for one or all medications."""
        logs = self.get_logs(medication_name=medication_name, days=days)
        stats = AdherenceStats(
            medication_name=medication_name or "(all)",
            total_logs=len(logs),
        )
        if not logs:
            return stats

        for log in logs:
            if log.status == MedicationStatus.TAKEN.value:
                stats.taken += 1
            elif log.status == MedicationStatus.MISSED.value:
                stats.missed += 1
            elif log.status == MedicationStatus.LATE.value:
                stats.late += 1
            elif log.status == MedicationStatus.SKIPPED.value:
                stats.skipped += 1

        actionable = stats.taken + stats.missed + stats.late
        if actionable > 0:
            stats.adherence_percent = round(
                ((stats.taken + stats.late) / actionable) * 100, 1
            )
            stats.on_time_percent = round(
                (stats.taken / actionable) * 100, 1
            )
        return stats

    def adherence_trend(
        self, medication_name: str, days: int = 30, window: int = 7,
    ) -> List[Tuple[str, float]]:
        """Return a rolling-window adherence trend.

        Returns list of (date_label, adherence_percent) tuples.
        """
        logs = self.get_logs(medication_name=medication_name, days=days)
        if not logs:
            return []

        # Group by date
        by_date: Dict[str, List[str]] = {}
        for log in logs:
            d = (log.created_at or "")[:10]
            if d:
                by_date.setdefault(d, []).append(log.status)

        sorted_dates = sorted(by_date.keys())
        trend: List[Tuple[str, float]] = []

        for i, d in enumerate(sorted_dates):
            window_start = max(0, i - window + 1)
            window_dates = sorted_dates[window_start: i + 1]
            taken_or_late = 0
            total = 0
            for wd in window_dates:
                for st in by_date[wd]:
                    if st in (
                        MedicationStatus.TAKEN.value,
                        MedicationStatus.MISSED.value,
                        MedicationStatus.LATE.value,
                    ):
                        total += 1
                        if st in (MedicationStatus.TAKEN.value, MedicationStatus.LATE.value):
                            taken_or_late += 1
            pct = round((taken_or_late / total) * 100, 1) if total else 0.0
            trend.append((d, pct))

        return trend

    # ------------------------------------------------------------------
    # Side effects
    # ------------------------------------------------------------------

    def log_side_effect(
        self,
        medication_name: str,
        dosage: str,
        frequency: str,
        scheduled_time: str,
        side_effects: str,
        notes: Optional[str] = None,
    ) -> int:
        """Convenience: log a dose entry focused on side effects."""
        return self.log_dose(
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            scheduled_time=scheduled_time,
            status="taken",
            taken_time=datetime.now().isoformat(),
            side_effects=side_effects,
            notes=notes,
        )

    def side_effect_summary(
        self, medication_name: str, days: int = 90,
    ) -> SideEffectSummary:
        """Aggregate reported side effects for a medication."""
        logs = self.get_logs(medication_name=medication_name, days=days)
        summary = SideEffectSummary(medication_name=medication_name)
        for log in logs:
            if log.side_effects:
                summary.total_reports += 1
                # Side effects stored as comma-separated text
                for effect in log.side_effects.split(","):
                    effect = effect.strip().lower()
                    if effect:
                        summary.effects[effect] = summary.effects.get(effect, 0) + 1
        return summary

    # ------------------------------------------------------------------
    # Mood correlation
    # ------------------------------------------------------------------

    def correlate_with_mood(
        self,
        medication_name: str,
        mood_data: List[Dict[str, Any]],
        days: int = 30,
    ) -> MoodCorrelation:
        """Compare average mood on taken vs. missed days.

        Args:
            medication_name: Medication to analyse.
            mood_data: List of dicts with ``timestamp`` (or ``date``) and
                       ``mood_score`` keys.
            days: Lookback period.
        """
        logs = self.get_logs(medication_name=medication_name, days=days)

        # Categorise days
        taken_dates: set[str] = set()
        missed_dates: set[str] = set()
        for log in logs:
            d = (log.created_at or "")[:10]
            if log.status in (MedicationStatus.TAKEN.value, MedicationStatus.LATE.value):
                taken_dates.add(d)
            elif log.status == MedicationStatus.MISSED.value:
                missed_dates.add(d)

        # Map mood to dates
        mood_by_date: Dict[str, List[float]] = {}
        for m in mood_data:
            d = (m.get("timestamp") or m.get("date", ""))[:10]
            score = m.get("mood_score")
            if d and score is not None:
                mood_by_date.setdefault(d, []).append(float(score))

        taken_moods: List[float] = []
        missed_moods: List[float] = []
        for d, scores in mood_by_date.items():
            avg = statistics.mean(scores)
            if d in taken_dates:
                taken_moods.append(avg)
            elif d in missed_dates:
                missed_moods.append(avg)

        correlation = MoodCorrelation(
            medication_name=medication_name,
            data_points=len(taken_moods) + len(missed_moods),
        )
        if taken_moods:
            correlation.taken_mood_avg = round(statistics.mean(taken_moods), 2)
        if missed_moods:
            correlation.missed_mood_avg = round(statistics.mean(missed_moods), 2)

        if taken_moods and missed_moods:
            diff = correlation.taken_mood_avg - correlation.missed_mood_avg
            if abs(diff) < 0.5:
                correlation.insight = (
                    f"Mood on days {medication_name} was taken vs. missed is similar "
                    f"(difference: {diff:+.1f} points)."
                )
            elif diff > 0:
                correlation.insight = (
                    f"Mood tends to be higher on days {medication_name} is taken "
                    f"({correlation.taken_mood_avg}/10 vs. {correlation.missed_mood_avg}/10)."
                )
            else:
                correlation.insight = (
                    f"Mood appears lower on days {medication_name} is taken "
                    f"({correlation.taken_mood_avg}/10 vs. {correlation.missed_mood_avg}/10). "
                    "Consider discussing this pattern with your prescriber."
                )
        elif not taken_moods and not missed_moods:
            correlation.insight = "Not enough overlapping mood and medication data."
        else:
            correlation.insight = (
                "Only one category (taken or missed) has mood data; "
                "a comparison is not yet possible."
            )

        return correlation

    # ------------------------------------------------------------------
    # Refill reminders
    # ------------------------------------------------------------------

    def days_until_refill(
        self, medication_name: str, current_supply: Optional[int] = None,
    ) -> Optional[int]:
        """Estimate days until the medication supply runs out.

        Uses the most recent ``supply_count`` from logs if *current_supply*
        is not provided, combined with the logged frequency.

        Returns ``None`` if there is insufficient data.
        """
        if current_supply is None:
            # Grab most recent log with a supply count
            logs = self.get_logs(medication_name=medication_name, limit=20)
            for log in logs:
                if log.supply_count is not None:
                    current_supply = log.supply_count
                    break
            if current_supply is None:
                return None

        # Determine daily consumption from frequency
        logs = self.get_logs(medication_name=medication_name, limit=1)
        if not logs:
            return None
        freq_str = logs[0].frequency
        try:
            freq = Frequency(freq_str)
            dpd = freq.doses_per_day
        except ValueError:
            dpd = 1.0  # default assumption

        if dpd <= 0:
            return None

        return int(current_supply / dpd)

    def needs_refill(
        self, medication_name: str, threshold_days: int = 7,
    ) -> bool:
        """Return True if the medication will run out within *threshold_days*."""
        remaining = self.days_until_refill(medication_name)
        if remaining is None:
            return False
        return remaining <= threshold_days

    def get_refill_alerts(self, threshold_days: int = 7) -> List[Dict[str, Any]]:
        """Return a list of medications that need refilling soon."""
        meds = self.get_medications()
        alerts: List[Dict[str, Any]] = []
        for name in meds:
            remaining = self.days_until_refill(name)
            if remaining is not None and remaining <= threshold_days:
                alerts.append({
                    "medication_name": name,
                    "days_remaining": remaining,
                    "urgent": remaining <= 2,
                })
        return alerts

    # ------------------------------------------------------------------
    # Export for doctor visits
    # ------------------------------------------------------------------

    def export_history(
        self,
        medication_name: Optional[str] = None,
        days: int = 90,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Export medication history to a JSON file for doctor visits.

        Includes adherence stats, side-effect summary, and raw logs.
        """
        logs = self.get_logs(medication_name=medication_name, days=days)
        meds = [medication_name] if medication_name else self.get_medications()

        report: Dict[str, Any] = {
            "disclaimer": MEDICAL_DISCLAIMER,
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "medications": {},
        }

        for med in meds:
            med_logs = [l for l in logs if l.medication_name == med]
            stats = self.adherence(medication_name=med, days=days)
            effects = self.side_effect_summary(med, days=days)
            report["medications"][med] = {
                "adherence": {
                    "total": stats.total_logs,
                    "taken": stats.taken,
                    "missed": stats.missed,
                    "late": stats.late,
                    "skipped": stats.skipped,
                    "adherence_percent": stats.adherence_percent,
                },
                "side_effects": {
                    "total_reports": effects.total_reports,
                    "effects": effects.effects,
                },
                "logs": [
                    {
                        "date": (l.created_at or "")[:10],
                        "status": l.status,
                        "taken_time": l.taken_time,
                        "side_effects": l.side_effects,
                        "notes": l.notes,
                    }
                    for l in med_logs
                ],
            }

        if output_path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = DATA_DIR / "exports" / f"medication_history_{ts}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, default=str), encoding="utf-8"
        )
        logger.info("Medication history exported to %s", output_path)
        return output_path

    # ------------------------------------------------------------------
    # Scheduling helpers
    # ------------------------------------------------------------------

    def get_todays_schedule(self) -> List[MedicationLogEntry]:
        """Return today's medication schedule (pending and completed)."""
        today = date.today().isoformat()
        result = self._db.query(
            self._table(),
            where="created_at >= ? AND created_at < ?",
            params=(today, (date.today() + timedelta(days=1)).isoformat()),
            order_by="scheduled_time ASC",
        )
        return [self._row_to_entry(r) for r in result.rows]

    def get_pending_doses(self) -> List[MedicationLogEntry]:
        """Return all pending doses for today."""
        today = date.today().isoformat()
        result = self._db.query(
            self._table(),
            where="status = 'pending' AND created_at >= ?",
            params=(today,),
            order_by="scheduled_time ASC",
        )
        return [self._row_to_entry(r) for r in result.rows]

    def create_daily_schedule(
        self, medications: List[Medication],
    ) -> List[int]:
        """Create pending log entries for today for each medication.

        Returns list of new row ids.
        """
        ids: List[int] = []
        for med in medications:
            row_id = self.log_dose(
                medication_name=med.name,
                dosage=med.dosage,
                frequency=med.frequency,
                scheduled_time=med.scheduled_time,
                status="pending",
                supply_count=med.supply_count,
                prescriber=med.prescriber,
                notes=med.notes,
            )
            ids.append(row_id)
        return ids

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_entry(row: Dict[str, Any]) -> MedicationLogEntry:
        return MedicationLogEntry(
            id=row.get("id"),
            medication_name=row.get("medication_name", ""),
            dosage=row.get("dosage", ""),
            frequency=row.get("frequency", ""),
            scheduled_time=row.get("scheduled_time", ""),
            taken_time=row.get("taken_time"),
            status=row.get("status", MedicationStatus.PENDING.value),
            side_effects=row.get("side_effects"),
            notes=row.get("notes"),
            supply_count=row.get("supply_count"),
            prescriber=row.get("prescriber"),
            created_at=row.get("created_at"),
        )
