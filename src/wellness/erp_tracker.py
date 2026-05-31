"""
ERP (Exposure and Response Prevention) tracker for the Mindful Organizer application.

Provides structured tracking of exposure hierarchies, exposure sessions,
response prevention logs, safety behaviors, habituation data, and
progress summaries for OCD support.

DISCLAIMER: ERP is most effective when guided by a trained therapist
specializing in OCD support.  This tool is designed to supplement
professional care, not replace it.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

DISCLAIMER = (
    "ERP is most effective when guided by a trained therapist specializing "
    "in OCD support. This tool is designed to supplement professional care, "
    "not replace it. Please work with a qualified mental health professional "
    "when implementing exposure and response prevention exercises."
)


# ── dataclasses ──────────────────────────────────────────────────────


@dataclass
class HierarchyItem:
    """An item in the exposure hierarchy.

    Attributes:
        item_id: Unique identifier.
        situation: Description of the feared situation or trigger.
        suds_rating: Subjective Units of Distress (0-100).
        notes: Additional notes about this item.
        created_at: When the item was added.
    """

    item_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    situation: str = ""
    suds_rating: int = 50
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if not 0 <= self.suds_rating <= 100:
            raise ValueError("suds_rating must be between 0 and 100")

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "situation": self.situation,
            "suds_rating": self.suds_rating,
            "notes": self.notes,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HierarchyItem":
        return cls(
            item_id=data["item_id"],
            situation=data["situation"],
            suds_rating=data["suds_rating"],
            notes=data.get("notes", ""),
            created_at=data.get("created_at", ""),
        )


@dataclass
class ExposureSession:
    """A single exposure practice session.

    Attributes:
        session_id: Unique identifier.
        hierarchy_item_id: Which hierarchy item was targeted.
        predicted_anxiety: Expected peak SUDS before starting (0-100).
        actual_anxiety_readings: List of (minutes, suds) measurements.
        duration_minutes: How long the exposure lasted.
        compulsion_performed: Whether a compulsion was performed.
        notes: Session notes.
        date: ISO date string for when the session occurred.
    """

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    hierarchy_item_id: str = ""
    predicted_anxiety: int = 50
    actual_anxiety_readings: list[tuple[int, int]] = field(default_factory=list)
    duration_minutes: int = 0
    compulsion_performed: bool = False
    notes: str = ""
    date: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if not 0 <= self.predicted_anxiety <= 100:
            raise ValueError("predicted_anxiety must be between 0 and 100")

    @property
    def peak_anxiety(self) -> int | None:
        """Return the highest SUDS recorded during the session."""
        if not self.actual_anxiety_readings:
            return None
        return max(suds for _, suds in self.actual_anxiety_readings)

    @property
    def final_anxiety(self) -> int | None:
        """Return the last SUDS reading of the session."""
        if not self.actual_anxiety_readings:
            return None
        return self.actual_anxiety_readings[-1][1]

    @property
    def anxiety_reduction(self) -> int | None:
        """Difference between peak and final SUDS."""
        peak = self.peak_anxiety
        final = self.final_anxiety
        if peak is not None and final is not None:
            return peak - final
        return None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "hierarchy_item_id": self.hierarchy_item_id,
            "predicted_anxiety": self.predicted_anxiety,
            "actual_anxiety_readings": self.actual_anxiety_readings,
            "duration_minutes": self.duration_minutes,
            "compulsion_performed": self.compulsion_performed,
            "notes": self.notes,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExposureSession":
        readings = [(int(r[0]), int(r[1])) for r in data.get("actual_anxiety_readings", [])]
        return cls(
            session_id=data["session_id"],
            hierarchy_item_id=data["hierarchy_item_id"],
            predicted_anxiety=data.get("predicted_anxiety", 50),
            actual_anxiety_readings=readings,
            duration_minutes=data.get("duration_minutes", 0),
            compulsion_performed=data.get("compulsion_performed", False),
            notes=data.get("notes", ""),
            date=data.get("date", ""),
        )


@dataclass
class ResponsePreventionLog:
    """A log entry for response prevention practice.

    Attributes:
        log_id: Unique identifier.
        session_id: Linked exposure session (if any).
        urge_intensity: Strength of the compulsion urge (0-100).
        urge_resisted: Whether the urge was successfully resisted.
        duration_resisted_minutes: How long the urge was resisted.
        strategy_used: What strategy helped resist the urge.
    """

    log_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    session_id: str = ""
    urge_intensity: int = 50
    urge_resisted: bool = True
    duration_resisted_minutes: int = 0
    strategy_used: str = ""

    def __post_init__(self) -> None:
        if not 0 <= self.urge_intensity <= 100:
            raise ValueError("urge_intensity must be between 0 and 100")

    def to_dict(self) -> dict:
        return {
            "log_id": self.log_id,
            "session_id": self.session_id,
            "urge_intensity": self.urge_intensity,
            "urge_resisted": self.urge_resisted,
            "duration_resisted_minutes": self.duration_resisted_minutes,
            "strategy_used": self.strategy_used,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResponsePreventionLog":
        return cls(
            log_id=data["log_id"],
            session_id=data.get("session_id", ""),
            urge_intensity=data.get("urge_intensity", 50),
            urge_resisted=data.get("urge_resisted", True),
            duration_resisted_minutes=data.get("duration_resisted_minutes", 0),
            strategy_used=data.get("strategy_used", ""),
        )


@dataclass
class SafetyBehavior:
    """A tracked safety behavior to reduce over time.

    Attributes:
        behavior_id: Unique identifier.
        description: What the safety behavior is.
        identified_date: When it was first identified.
        times_used: How many times it has been used since tracking began.
        working_on_reducing: Whether the user is actively reducing this.
    """

    behavior_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    description: str = ""
    identified_date: str = field(default_factory=lambda: date.today().isoformat())
    times_used: int = 0
    working_on_reducing: bool = False

    def to_dict(self) -> dict:
        return {
            "behavior_id": self.behavior_id,
            "description": self.description,
            "identified_date": self.identified_date,
            "times_used": self.times_used,
            "working_on_reducing": self.working_on_reducing,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SafetyBehavior":
        return cls(
            behavior_id=data["behavior_id"],
            description=data["description"],
            identified_date=data.get("identified_date", ""),
            times_used=data.get("times_used", 0),
            working_on_reducing=data.get("working_on_reducing", False),
        )


# ── tracker ──────────────────────────────────────────────────────────


class ERPTracker:
    """Manages ERP hierarchy items, sessions, response prevention logs,
    and safety behaviors with JSON persistence.

    Args:
        data_dir: Directory to persist ERP data.
    """

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._data_file = self.data_dir / "erp_data.json"
        self._hierarchy: list[HierarchyItem] = []
        self._sessions: list[ExposureSession] = []
        self._rp_logs: list[ResponsePreventionLog] = []
        self._safety_behaviors: list[SafetyBehavior] = []
        self._load()

    # ── persistence ──────────────────────────────────────────────

    def _load(self) -> None:
        """Load all ERP data from disk."""
        if self._data_file.exists():
            try:
                with open(self._data_file) as fh:
                    data = json.load(fh)
                self._hierarchy = [HierarchyItem.from_dict(h) for h in data.get("hierarchy", [])]
                self._sessions = [ExposureSession.from_dict(s) for s in data.get("sessions", [])]
                self._rp_logs = [
                    ResponsePreventionLog.from_dict(r) for r in data.get("rp_logs", [])
                ]
                self._safety_behaviors = [
                    SafetyBehavior.from_dict(b) for b in data.get("safety_behaviors", [])
                ]
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self) -> None:
        """Persist all ERP data to disk."""
        data = {
            "hierarchy": [h.to_dict() for h in self._hierarchy],
            "sessions": [s.to_dict() for s in self._sessions],
            "rp_logs": [r.to_dict() for r in self._rp_logs],
            "safety_behaviors": [b.to_dict() for b in self._safety_behaviors],
        }
        with open(self._data_file, "w") as fh:
            json.dump(data, fh, indent=2)

    # ── hierarchy management ─────────────────────────────────────

    def add_hierarchy_item(
        self,
        situation: str,
        suds_rating: int,
        notes: str = "",
    ) -> HierarchyItem:
        """Add a new item to the exposure hierarchy.

        Args:
            situation: Description of the feared situation.
            suds_rating: Subjective Units of Distress (0-100).
            notes: Additional notes.

        Returns:
            The newly created HierarchyItem.

        Raises:
            ValueError: If suds_rating is out of range.
        """
        item = HierarchyItem(
            situation=situation,
            suds_rating=suds_rating,
            notes=notes,
        )
        self._hierarchy.append(item)
        self._save()
        return item

    def update_hierarchy_item(
        self,
        item_id: str,
        situation: str | None = None,
        suds_rating: int | None = None,
        notes: str | None = None,
    ) -> HierarchyItem | None:
        """Update an existing hierarchy item.

        Args:
            item_id: The item to update.
            situation: New situation description.
            suds_rating: New SUDS rating (0-100).
            notes: New notes.

        Returns:
            The updated item, or None if not found.
        """
        for item in self._hierarchy:
            if item.item_id == item_id:
                if situation is not None:
                    item.situation = situation
                if suds_rating is not None:
                    if not 0 <= suds_rating <= 100:
                        raise ValueError("suds_rating must be between 0 and 100")
                    item.suds_rating = suds_rating
                if notes is not None:
                    item.notes = notes
                self._save()
                return item
        return None

    def remove_hierarchy_item(self, item_id: str) -> bool:
        """Remove a hierarchy item.

        Args:
            item_id: The item to remove.

        Returns:
            True if removed, False if not found.
        """
        for i, item in enumerate(self._hierarchy):
            if item.item_id == item_id:
                self._hierarchy.pop(i)
                self._save()
                return True
        return False

    def get_hierarchy(self) -> list[HierarchyItem]:
        """Return the full hierarchy sorted by SUDS rating (lowest first).

        Returns:
            Sorted list of hierarchy items.
        """
        return sorted(self._hierarchy, key=lambda h: h.suds_rating)

    def get_hierarchy_item(self, item_id: str) -> HierarchyItem | None:
        """Retrieve a single hierarchy item by ID.

        Args:
            item_id: The item identifier.

        Returns:
            The item if found, otherwise None.
        """
        for item in self._hierarchy:
            if item.item_id == item_id:
                return item
        return None

    # ── session management ───────────────────────────────────────

    def record_session(
        self,
        hierarchy_item_id: str,
        predicted_anxiety: int,
        actual_anxiety_readings: list[tuple[int, int]],
        duration_minutes: int,
        compulsion_performed: bool = False,
        notes: str = "",
    ) -> ExposureSession:
        """Record a completed exposure session.

        Args:
            hierarchy_item_id: Which hierarchy item was targeted.
            predicted_anxiety: Expected peak SUDS (0-100).
            actual_anxiety_readings: List of (minutes, suds) tuples.
            duration_minutes: Total session duration.
            compulsion_performed: Whether a compulsion occurred.
            notes: Session notes.

        Returns:
            The newly created ExposureSession.

        Raises:
            ValueError: If hierarchy_item_id does not exist or anxiety out of range.
        """
        if not any(h.item_id == hierarchy_item_id for h in self._hierarchy):
            raise ValueError(f"Hierarchy item '{hierarchy_item_id}' not found.")

        # Validate readings
        for minutes, suds in actual_anxiety_readings:
            if not 0 <= suds <= 100:
                raise ValueError(f"SUDS reading {suds} at {minutes}min is out of range (0-100).")

        session = ExposureSession(
            hierarchy_item_id=hierarchy_item_id,
            predicted_anxiety=predicted_anxiety,
            actual_anxiety_readings=actual_anxiety_readings,
            duration_minutes=duration_minutes,
            compulsion_performed=compulsion_performed,
            notes=notes,
        )
        self._sessions.append(session)
        self._save()
        return session

    def get_sessions_for_item(self, item_id: str) -> list[ExposureSession]:
        """Return all sessions for a given hierarchy item, sorted by date.

        Args:
            item_id: The hierarchy item to filter by.

        Returns:
            Sessions sorted chronologically.
        """
        return sorted(
            [s for s in self._sessions if s.hierarchy_item_id == item_id],
            key=lambda s: s.date,
        )

    def get_all_sessions(self) -> list[ExposureSession]:
        """Return all exposure sessions sorted by date."""
        return sorted(self._sessions, key=lambda s: s.date)

    # ── response prevention ──────────────────────────────────────

    def log_response_prevention(
        self,
        session_id: str,
        urge_intensity: int,
        urge_resisted: bool,
        duration_resisted_minutes: int = 0,
        strategy_used: str = "",
    ) -> ResponsePreventionLog:
        """Log a response prevention attempt.

        Args:
            session_id: Linked exposure session.
            urge_intensity: Strength of the compulsion urge (0-100).
            urge_resisted: Whether the urge was resisted.
            duration_resisted_minutes: How long the urge was resisted.
            strategy_used: What helped resist the urge.

        Returns:
            The new ResponsePreventionLog.

        Raises:
            ValueError: If urge_intensity is out of range.
        """
        log = ResponsePreventionLog(
            session_id=session_id,
            urge_intensity=urge_intensity,
            urge_resisted=urge_resisted,
            duration_resisted_minutes=duration_resisted_minutes,
            strategy_used=strategy_used,
        )
        self._rp_logs.append(log)
        self._save()
        return log

    def get_rp_logs_for_session(self, session_id: str) -> list[ResponsePreventionLog]:
        """Return all response prevention logs for a given session.

        Args:
            session_id: The session to filter by.

        Returns:
            Matching logs.
        """
        return [r for r in self._rp_logs if r.session_id == session_id]

    # ── safety behaviors ─────────────────────────────────────────

    def track_safety_behavior(
        self,
        description: str,
        working_on_reducing: bool = False,
    ) -> SafetyBehavior:
        """Add a newly identified safety behavior.

        Args:
            description: What the safety behavior is.
            working_on_reducing: Whether actively working to reduce it.

        Returns:
            The new SafetyBehavior.
        """
        behavior = SafetyBehavior(
            description=description,
            working_on_reducing=working_on_reducing,
        )
        self._safety_behaviors.append(behavior)
        self._save()
        return behavior

    def increment_safety_behavior(self, behavior_id: str) -> SafetyBehavior | None:
        """Record one use of a safety behavior.

        Args:
            behavior_id: The behavior to increment.

        Returns:
            The updated SafetyBehavior, or None if not found.
        """
        for behavior in self._safety_behaviors:
            if behavior.behavior_id == behavior_id:
                behavior.times_used += 1
                self._save()
                return behavior
        return None

    def update_safety_behavior(
        self,
        behavior_id: str,
        working_on_reducing: bool | None = None,
        description: str | None = None,
    ) -> SafetyBehavior | None:
        """Update a safety behavior record.

        Args:
            behavior_id: The behavior to update.
            working_on_reducing: New reduction status.
            description: New description.

        Returns:
            The updated behavior, or None if not found.
        """
        for behavior in self._safety_behaviors:
            if behavior.behavior_id == behavior_id:
                if working_on_reducing is not None:
                    behavior.working_on_reducing = working_on_reducing
                if description is not None:
                    behavior.description = description
                self._save()
                return behavior
        return None

    def get_safety_behaviors(self) -> list[SafetyBehavior]:
        """Return all tracked safety behaviors."""
        return list(self._safety_behaviors)

    # ── habituation data ─────────────────────────────────────────

    def get_habituation_data(self, item_id: str) -> list[dict]:
        """Return SUDS data over sessions for a hierarchy item (for charting).

        Each entry contains the session date, predicted anxiety, peak anxiety,
        final anxiety, and whether habituation occurred within the session.

        Args:
            item_id: The hierarchy item to get data for.

        Returns:
            List of dicts, one per session, chronologically ordered.
        """
        sessions = self.get_sessions_for_item(item_id)
        data: list[dict] = []
        for session in sessions:
            entry: dict = {
                "session_id": session.session_id,
                "date": session.date,
                "predicted_anxiety": session.predicted_anxiety,
                "peak_anxiety": session.peak_anxiety,
                "final_anxiety": session.final_anxiety,
                "anxiety_reduction": session.anxiety_reduction,
                "duration_minutes": session.duration_minutes,
                "compulsion_performed": session.compulsion_performed,
            }
            # Include full anxiety curve for detailed charting
            entry["anxiety_curve"] = [
                {"minutes": m, "suds": s} for m, s in session.actual_anxiety_readings
            ]
            data.append(entry)
        return data

    # ── progress summary ─────────────────────────────────────────

    def get_progress_summary(self) -> dict:
        """Compute an overall progress summary.

        Returns:
            Dictionary with items_total, items_worked_on, sessions_completed,
            average_suds_reduction, compulsion_free_sessions, rp_success_rate,
            safety_behaviors_tracked, and safety_behaviors_reducing.
        """
        if not self._hierarchy:
            return {
                "items_total": 0,
                "items_worked_on": 0,
                "sessions_completed": len(self._sessions),
                "average_suds_reduction": None,
                "compulsion_free_sessions": 0,
                "compulsion_free_rate": None,
                "rp_success_rate": None,
                "safety_behaviors_tracked": 0,
                "safety_behaviors_reducing": 0,
            }

        # Items that have at least one session
        items_with_sessions = {s.hierarchy_item_id for s in self._sessions}
        items_worked_on = len(items_with_sessions & {h.item_id for h in self._hierarchy})

        # Average SUDS reduction across sessions
        reductions = [
            s.anxiety_reduction for s in self._sessions if s.anxiety_reduction is not None
        ]
        avg_reduction = round(sum(reductions) / len(reductions), 1) if reductions else None

        # Compulsion-free sessions
        compulsion_free = sum(1 for s in self._sessions if not s.compulsion_performed)
        compulsion_free_rate = (
            round(compulsion_free / len(self._sessions) * 100, 1) if self._sessions else None
        )

        # Response prevention success rate
        resisted = sum(1 for r in self._rp_logs if r.urge_resisted)
        rp_rate = round(resisted / len(self._rp_logs) * 100, 1) if self._rp_logs else None

        # Safety behaviors
        reducing = sum(1 for b in self._safety_behaviors if b.working_on_reducing)

        return {
            "items_total": len(self._hierarchy),
            "items_worked_on": items_worked_on,
            "sessions_completed": len(self._sessions),
            "average_suds_reduction": avg_reduction,
            "compulsion_free_sessions": compulsion_free,
            "compulsion_free_rate": compulsion_free_rate,
            "rp_success_rate": rp_rate,
            "safety_behaviors_tracked": len(self._safety_behaviors),
            "safety_behaviors_reducing": reducing,
        }

    # ── export ───────────────────────────────────────────────────

    def export_report(self) -> dict:
        """Export a therapist-shareable data dictionary.

        Returns:
            Dictionary containing the full hierarchy, sessions with
            habituation data, response prevention summary, safety
            behaviors, progress summary, and disclaimer.
        """
        hierarchy_data = []
        for item in self.get_hierarchy():
            sessions = self.get_sessions_for_item(item.item_id)
            hierarchy_data.append(
                {
                    "situation": item.situation,
                    "initial_suds": item.suds_rating,
                    "sessions_completed": len(sessions),
                    "habituation_data": self.get_habituation_data(item.item_id),
                }
            )

        rp_summary: dict = {
            "total_logs": len(self._rp_logs),
            "urges_resisted": sum(1 for r in self._rp_logs if r.urge_resisted),
            "average_urge_intensity": (
                round(
                    sum(r.urge_intensity for r in self._rp_logs) / len(self._rp_logs),
                    1,
                )
                if self._rp_logs
                else None
            ),
            "strategies_used": list({r.strategy_used for r in self._rp_logs if r.strategy_used}),
        }

        return {
            "disclaimer": DISCLAIMER,
            "generated_at": datetime.now().isoformat(),
            "hierarchy": hierarchy_data,
            "response_prevention": rp_summary,
            "safety_behaviors": [b.to_dict() for b in self._safety_behaviors],
            "progress_summary": self.get_progress_summary(),
        }
