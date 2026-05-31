"""
Meditation session management for the Mindful Organizer application.

Provides meditation type definitions, timer configuration, session tracking,
streaks, statistics, personalized recommendations, favorites, and optional
guided meditation library loading.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path


class MeditationType(Enum):
    """Available meditation practice types."""

    MINDFULNESS = "mindfulness"
    BODY_SCAN = "body_scan"
    LOVING_KINDNESS = "loving_kindness"
    BREATH_FOCUS = "breath_focus"
    PROGRESSIVE_RELAXATION = "progressive_relaxation"
    VISUALIZATION = "visualization"
    WALKING = "walking"


# Descriptions for each meditation type used in recommendations and display.
_MEDITATION_DESCRIPTIONS: dict[MeditationType, dict[str, str]] = {
    MeditationType.MINDFULNESS: {
        "name": "Mindfulness Meditation",
        "description": (
            "Non-judgmental awareness of the present moment. Observe thoughts, "
            "feelings, and sensations as they arise without trying to change them."
        ),
        "best_for": "General stress reduction, building awareness, anxiety management",
    },
    MeditationType.BODY_SCAN: {
        "name": "Body Scan",
        "description": (
            "Progressive attention through each part of the body, noticing "
            "tension and releasing it. Often done lying down."
        ),
        "best_for": "Tension release, sleep preparation, chronic pain, PTSD",
    },
    MeditationType.LOVING_KINDNESS: {
        "name": "Loving-Kindness (Metta)",
        "description": (
            "Generate feelings of warmth and goodwill toward yourself and "
            "others through repeated phrases of kindness and well-wishing."
        ),
        "best_for": "Depression, self-criticism, social anxiety, building compassion",
    },
    MeditationType.BREATH_FOCUS: {
        "name": "Breath Focus",
        "description": (
            "Simple attention to the breath. Count breaths or observe the "
            "natural rhythm of inhaling and exhaling."
        ),
        "best_for": "Beginners, anxiety, ADHD focus training, quick calming",
    },
    MeditationType.PROGRESSIVE_RELAXATION: {
        "name": "Progressive Muscle Relaxation",
        "description": (
            "Systematically tense and release muscle groups to reduce physical "
            "tension and promote deep relaxation."
        ),
        "best_for": "Insomnia, physical tension, panic disorder, general stress",
    },
    MeditationType.VISUALIZATION: {
        "name": "Visualization",
        "description": (
            "Create a vivid mental image of a peaceful scene, a safe place, "
            "or a desired outcome. Engages the imagination for calm and focus."
        ),
        "best_for": "PTSD safe place work, performance anxiety, depression",
    },
    MeditationType.WALKING: {
        "name": "Walking Meditation",
        "description": (
            "Mindful walking with attention to each step, the movement of "
            "the body, and contact with the ground. Good when sitting is hard."
        ),
        "best_for": "ADHD, restlessness, depression, building mindful movement",
    },
}


@dataclass
class TimerConfig:
    """Configuration for a meditation timer.

    Attributes:
        duration_minutes: Total meditation time.
        interval_bell_minutes: Optional interval bell (e.g., every 5 min).
        preparation_seconds: Countdown before meditation starts.
    """

    duration_minutes: int = 10
    interval_bell_minutes: int | None = None
    preparation_seconds: int = 10

    def __post_init__(self) -> None:
        if self.duration_minutes < 1:
            raise ValueError("duration_minutes must be at least 1")
        if self.interval_bell_minutes is not None and self.interval_bell_minutes < 1:
            raise ValueError("interval_bell_minutes must be at least 1")
        if self.preparation_seconds < 0:
            raise ValueError("preparation_seconds must be non-negative")

    def get_bell_times(self) -> list[int]:
        """Return the times (in minutes) when interval bells should sound.

        Returns:
            List of minute marks for bells, excluding the final bell.
        """
        if self.interval_bell_minutes is None:
            return []
        times: list[int] = []
        t = self.interval_bell_minutes
        while t < self.duration_minutes:
            times.append(t)
            t += self.interval_bell_minutes
        return times

    def to_dict(self) -> dict:
        return {
            "duration_minutes": self.duration_minutes,
            "interval_bell_minutes": self.interval_bell_minutes,
            "preparation_seconds": self.preparation_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TimerConfig":
        return cls(
            duration_minutes=data.get("duration_minutes", 10),
            interval_bell_minutes=data.get("interval_bell_minutes"),
            preparation_seconds=data.get("preparation_seconds", 10),
        )


@dataclass
class MeditationSession:
    """A single meditation session.

    Attributes:
        session_id: Unique identifier.
        meditation_type: Type of meditation practiced.
        duration_minutes: Planned duration.
        guided: Whether a guided meditation was used.
        source: Name or URL of the guided meditation (if guided).
        mood_before: Self-reported mood before (1-10).
        mood_after: Self-reported mood after (1-10).
        notes: Session notes.
        date: ISO datetime string.
        completed: Whether the session was finished.
    """

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    meditation_type: MeditationType = MeditationType.MINDFULNESS
    duration_minutes: int = 10
    guided: bool = False
    source: str | None = None
    mood_before: int | None = None
    mood_after: int | None = None
    notes: str = ""
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    completed: bool = False

    def __post_init__(self) -> None:
        if self.mood_before is not None and not 1 <= self.mood_before <= 10:
            raise ValueError("mood_before must be between 1 and 10")
        if self.mood_after is not None and not 1 <= self.mood_after <= 10:
            raise ValueError("mood_after must be between 1 and 10")

    @property
    def mood_improvement(self) -> int | None:
        """Mood change from before to after the session."""
        if self.mood_before is not None and self.mood_after is not None:
            return self.mood_after - self.mood_before
        return None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "meditation_type": self.meditation_type.value,
            "duration_minutes": self.duration_minutes,
            "guided": self.guided,
            "source": self.source,
            "mood_before": self.mood_before,
            "mood_after": self.mood_after,
            "notes": self.notes,
            "date": self.date,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MeditationSession":
        return cls(
            session_id=data["session_id"],
            meditation_type=MeditationType(data["meditation_type"]),
            duration_minutes=data.get("duration_minutes", 10),
            guided=data.get("guided", False),
            source=data.get("source"),
            mood_before=data.get("mood_before"),
            mood_after=data.get("mood_after"),
            notes=data.get("notes", ""),
            date=data.get("date", ""),
            completed=data.get("completed", False),
        )


@dataclass
class GuidedMeditation:
    """A guided meditation from the resource library.

    Attributes:
        guided_id: Unique identifier.
        title: Display name.
        meditation_type: The type of meditation.
        duration_minutes: Length of the guided session.
        description: Brief description of the meditation.
        source: File path, URL, or other reference.
        condition_suitability: Conditions this is suited for.
    """

    guided_id: str = ""
    title: str = ""
    meditation_type: MeditationType = MeditationType.MINDFULNESS
    duration_minutes: int = 10
    description: str = ""
    source: str = ""
    condition_suitability: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "guided_id": self.guided_id,
            "title": self.title,
            "meditation_type": self.meditation_type.value,
            "duration_minutes": self.duration_minutes,
            "description": self.description,
            "source": self.source,
            "condition_suitability": self.condition_suitability,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GuidedMeditation":
        return cls(
            guided_id=data.get("guided_id", ""),
            title=data.get("title", ""),
            meditation_type=MeditationType(data.get("meditation_type", "mindfulness")),
            duration_minutes=data.get("duration_minutes", 10),
            description=data.get("description", ""),
            source=data.get("source", ""),
            condition_suitability=data.get("condition_suitability", []),
        )


# ── manager ──────────────────────────────────────────────────────────


class MeditationManager:
    """Manages meditation sessions, favorites, streaks, and recommendations.

    Args:
        data_dir: Directory for JSON persistence.
    """

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._data_file = self.data_dir / "meditation_data.json"
        self._sessions: list[MeditationSession] = []
        self._favorites: list[str] = []  # meditation type values
        self._guided_library: list[GuidedMeditation] = []
        self._active_session: MeditationSession | None = None
        self._load()

    # ── persistence ──────────────────────────────────────────────

    def _load(self) -> None:
        """Load all meditation data from disk."""
        if self._data_file.exists():
            try:
                with open(self._data_file) as fh:
                    data = json.load(fh)
                self._sessions = [MeditationSession.from_dict(s) for s in data.get("sessions", [])]
                self._favorites = data.get("favorites", [])
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self) -> None:
        """Persist data to disk."""
        data = {
            "sessions": [s.to_dict() for s in self._sessions],
            "favorites": self._favorites,
        }
        with open(self._data_file, "w") as fh:
            json.dump(data, fh, indent=2)

    # ── meditation types ─────────────────────────────────────────

    def get_meditation_types(self) -> list[dict[str, str]]:
        """Return all meditation types with descriptions.

        Returns:
            List of dicts with type, name, description, and best_for.
        """
        result: list[dict[str, str]] = []
        for med_type, info in _MEDITATION_DESCRIPTIONS.items():
            result.append(
                {
                    "type": med_type.value,
                    "name": info["name"],
                    "description": info["description"],
                    "best_for": info["best_for"],
                }
            )
        return result

    # ── session management ───────────────────────────────────────

    def start_session(
        self,
        meditation_type: MeditationType,
        duration_minutes: int = 10,
        guided: bool = False,
        source: str | None = None,
        mood_before: int | None = None,
    ) -> MeditationSession:
        """Start a new meditation session.

        Args:
            meditation_type: The type of meditation.
            duration_minutes: Planned duration.
            guided: Whether using a guided meditation.
            source: Reference for the guided meditation.
            mood_before: Pre-session mood (1-10).

        Returns:
            The newly started MeditationSession.
        """
        session = MeditationSession(
            meditation_type=meditation_type,
            duration_minutes=duration_minutes,
            guided=guided,
            source=source,
            mood_before=mood_before,
        )
        self._active_session = session
        return session

    def complete_session(
        self,
        session: MeditationSession | None = None,
        mood_after: int | None = None,
        notes: str = "",
        actual_duration: int | None = None,
    ) -> MeditationSession:
        """Mark a session as completed and persist it.

        Args:
            session: The session to complete. Uses active session if None.
            mood_after: Post-session mood (1-10).
            notes: Session notes.
            actual_duration: Override duration if different from planned.

        Returns:
            The completed session.

        Raises:
            ValueError: If no session is provided and no active session exists,
                or if mood_after is out of range.
        """
        target = session or self._active_session
        if target is None:
            raise ValueError("No active session to complete.")

        if mood_after is not None:
            if not 1 <= mood_after <= 10:
                raise ValueError("mood_after must be between 1 and 10")
            target.mood_after = mood_after

        if notes:
            target.notes = notes
        if actual_duration is not None:
            target.duration_minutes = actual_duration

        target.completed = True
        self._sessions.append(target)
        self._active_session = None
        self._save()
        return target

    def cancel_session(
        self,
        session: MeditationSession | None = None,
        notes: str = "",
    ) -> MeditationSession | None:
        """Cancel an in-progress session. Records it as incomplete.

        Args:
            session: The session to cancel. Uses active session if None.
            notes: Reason for cancellation.

        Returns:
            The cancelled session, or None if no session was active.
        """
        target = session or self._active_session
        if target is None:
            return None

        target.completed = False
        if notes:
            target.notes = notes
        self._sessions.append(target)
        self._active_session = None
        self._save()
        return target

    # ── history & statistics ─────────────────────────────────────

    def get_session_history(
        self,
        meditation_type: MeditationType | None = None,
        completed_only: bool = False,
    ) -> list[MeditationSession]:
        """Return session history, optionally filtered.

        Args:
            meditation_type: Filter by type.
            completed_only: Only include completed sessions.

        Returns:
            Sessions sorted most-recent-first.
        """
        results = list(self._sessions)
        if meditation_type is not None:
            results = [s for s in results if s.meditation_type == meditation_type]
        if completed_only:
            results = [s for s in results if s.completed]
        return sorted(results, key=lambda s: s.date, reverse=True)

    def get_statistics(self) -> dict:
        """Compute aggregate meditation statistics.

        Returns:
            Dictionary with total_sessions, completed_sessions,
            total_minutes, average_duration, average_mood_improvement,
            favorite_type, streak, and type_breakdown.
        """
        if not self._sessions:
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "total_minutes": 0,
                "average_duration": 0.0,
                "average_mood_improvement": None,
                "favorite_type": None,
                "streak": 0,
                "type_breakdown": {},
            }

        completed = [s for s in self._sessions if s.completed]
        total_minutes = sum(s.duration_minutes for s in completed)
        avg_duration = total_minutes / len(completed) if completed else 0.0

        # Mood improvements
        improvements = [
            s.mood_improvement for s in self._sessions if s.mood_improvement is not None
        ]
        avg_improvement = round(sum(improvements) / len(improvements), 2) if improvements else None

        # Most practiced type
        type_counts: dict[str, int] = {}
        for s in self._sessions:
            key = s.meditation_type.value
            type_counts[key] = type_counts.get(key, 0) + 1
        favorite = max(type_counts, key=type_counts.get) if type_counts else None  # type: ignore[arg-type]

        return {
            "total_sessions": len(self._sessions),
            "completed_sessions": len(completed),
            "total_minutes": total_minutes,
            "average_duration": round(avg_duration, 1),
            "average_mood_improvement": avg_improvement,
            "favorite_type": favorite,
            "streak": self.get_streak(),
            "type_breakdown": type_counts,
        }

    def get_streak(self) -> int:
        """Return the number of consecutive days with a completed session.

        Counts backward from today (or the most recent session date).

        Returns:
            Consecutive meditation days.
        """
        completed = [s for s in self._sessions if s.completed]
        if not completed:
            return 0

        session_dates: set[date] = set()
        for s in completed:
            try:
                dt = datetime.fromisoformat(s.date)
                session_dates.add(dt.date())
            except ValueError:
                continue

        if not session_dates:
            return 0

        today = date.today()
        current = today if today in session_dates else max(session_dates)
        if current not in session_dates:
            return 0

        streak = 0
        while current in session_dates:
            streak += 1
            current -= timedelta(days=1)
        return streak

    # ── recommendations ──────────────────────────────────────────

    def get_recommendation(
        self,
        mood: int | None = None,
        energy: int | None = None,
        conditions: list[str] | None = None,
    ) -> list[dict]:
        """Suggest meditation types based on current state.

        Scoring considers mood level, energy level, condition suitability,
        and historical effectiveness from past sessions.

        Args:
            mood: Current mood (1-10).
            energy: Current energy (1-10).
            conditions: Active conditions (e.g., ["Anxiety", "ADHD"]).

        Returns:
            List of dicts with type info and score, sorted best-first.
        """
        conditions = conditions or []
        cond_lower = {c.lower() for c in conditions}
        scored: list[tuple] = []

        for med_type, info in _MEDITATION_DESCRIPTIONS.items():
            score = 0.0
            best_for_lower = info["best_for"].lower()

            # Condition match
            for cond in cond_lower:
                if cond in best_for_lower:
                    score += 20

            # Mood-based suggestions
            if mood is not None:
                if mood <= 3:
                    # Very low mood: loving-kindness, body scan
                    if med_type in (
                        MeditationType.LOVING_KINDNESS,
                        MeditationType.BODY_SCAN,
                        MeditationType.VISUALIZATION,
                    ):
                        score += 15
                elif mood <= 5:
                    # Moderate: mindfulness, breath focus
                    if med_type in (
                        MeditationType.MINDFULNESS,
                        MeditationType.BREATH_FOCUS,
                    ):
                        score += 10
                else:
                    # Good mood: any type works, slight mindfulness preference
                    if med_type == MeditationType.MINDFULNESS:
                        score += 5

            # Energy-based suggestions
            if energy is not None:
                if energy <= 3:
                    # Low energy: body scan, progressive relaxation (can lie down)
                    if med_type in (
                        MeditationType.BODY_SCAN,
                        MeditationType.PROGRESSIVE_RELAXATION,
                        MeditationType.VISUALIZATION,
                    ):
                        score += 15
                    # Walking is too active for low energy
                    if med_type == MeditationType.WALKING:
                        score -= 10
                elif energy >= 7:
                    # High energy: walking meditation to use the energy
                    if med_type == MeditationType.WALKING:
                        score += 15
                    if med_type == MeditationType.MINDFULNESS:
                        score += 5

            # Historical effectiveness
            past = [
                s
                for s in self._sessions
                if s.meditation_type == med_type and s.mood_improvement is not None
            ]
            if past:
                avg_imp = sum(
                    s.mood_improvement
                    for s in past  # type: ignore[misc]
                ) / len(past)
                score += avg_imp * 3

            # Favorites bonus
            if med_type.value in self._favorites:
                score += 5

            scored.append((score, med_type, info))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "type": med_type.value,
                "name": info["name"],
                "description": info["description"],
                "best_for": info["best_for"],
                "score": round(score, 1),
            }
            for score, med_type, info in scored
        ]

    # ── favorites ────────────────────────────────────────────────

    def get_favorites(self) -> list[str]:
        """Return the list of favorited meditation type values.

        Returns:
            List of MeditationType value strings.
        """
        return list(self._favorites)

    def add_favorite(self, meditation_type: MeditationType) -> None:
        """Add a meditation type to favorites.

        Args:
            meditation_type: The type to favorite.
        """
        if meditation_type.value not in self._favorites:
            self._favorites.append(meditation_type.value)
            self._save()

    def remove_favorite(self, meditation_type: MeditationType) -> bool:
        """Remove a meditation type from favorites.

        Args:
            meditation_type: The type to un-favorite.

        Returns:
            True if removed, False if it was not a favorite.
        """
        if meditation_type.value in self._favorites:
            self._favorites.remove(meditation_type.value)
            self._save()
            return True
        return False

    # ── guided library ───────────────────────────────────────────

    def load_guided_library(self, resources_path: Path | None = None) -> list[GuidedMeditation]:
        """Load guided meditations from a JSON resource file.

        Looks for resources/guideds.json relative to the package, or at
        the explicitly provided path.

        Args:
            resources_path: Optional explicit path to the JSON file.

        Returns:
            List of loaded GuidedMeditation objects.
        """
        if resources_path is None:
            # Try standard resource locations
            candidates = [
                Path(__file__).parent.parent.parent / "resources" / "guideds.json",
                self.data_dir / "guideds.json",
            ]
        else:
            candidates = [resources_path]

        for path in candidates:
            if path.exists():
                try:
                    with open(path) as fh:
                        data = json.load(fh)
                    self._guided_library = [GuidedMeditation.from_dict(g) for g in data]
                    return list(self._guided_library)
                except (json.JSONDecodeError, KeyError):
                    continue

        return []

    def get_guided_library(
        self, meditation_type: MeditationType | None = None
    ) -> list[GuidedMeditation]:
        """Return the loaded guided meditation library, optionally filtered.

        Args:
            meditation_type: Filter by type.

        Returns:
            List of guided meditations.
        """
        if meditation_type is not None:
            return [g for g in self._guided_library if g.meditation_type == meditation_type]
        return list(self._guided_library)

    @property
    def sessions(self) -> list[MeditationSession]:
        """Read-only access to session history."""
        return list(self._sessions)

    @property
    def active_session(self) -> MeditationSession | None:
        """The currently active session, if any."""
        return self._active_session
