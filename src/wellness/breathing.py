"""
Guided breathing exercises for the Mindful Organizer application.

Provides structured breathing exercises with phase-based timing,
session tracking, mood monitoring, and personalized recommendations
based on mental health conditions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set
from pathlib import Path
import json
import uuid


class BreathingExerciseType(Enum):
    """Available breathing exercise types."""
    BOX_BREATHING = "box_breathing"
    FOUR_SEVEN_EIGHT = "four_seven_eight"
    DEEP_BELLY = "deep_belly"
    CALMING_BREATH = "calming_breath"
    ENERGIZING_BREATH = "energizing_breath"
    GROUNDING_BREATH = "grounding_breath"


class BreathPhase(Enum):
    """Phases within a breathing cycle."""
    INHALE = "inhale"
    HOLD_IN = "hold_in"
    EXHALE = "exhale"
    HOLD_OUT = "hold_out"


class Condition(Enum):
    """Mental health conditions for suitability mapping."""
    ADHD = "ADHD"
    ANXIETY = "Anxiety"
    DEPRESSION = "Depression"
    OCD = "OCD"
    PTSD = "PTSD"
    PANIC = "Panic Disorder"
    INSOMNIA = "Insomnia"
    GENERAL = "General Wellness"


@dataclass
class BreathPhaseData:
    """Timing data for a single phase of a breathing cycle.

    Attributes:
        phase: The type of breath phase.
        duration_seconds: How long this phase lasts.
        instruction: Display text for the user during this phase.
    """
    phase: BreathPhase
    duration_seconds: float
    instruction: str


@dataclass
class BreathingExercise:
    """A complete breathing exercise definition.

    Attributes:
        exercise_type: The category of breathing exercise.
        name: Human-readable exercise name.
        description: Explanation of the exercise and its benefits.
        phases: Ordered list of breath phases forming one cycle.
        default_cycles: Recommended number of cycles.
        condition_suitability: Conditions this exercise helps with.
        difficulty: Difficulty rating from 1 (easiest) to 5.
    """
    exercise_type: BreathingExerciseType
    name: str
    description: str
    phases: List[BreathPhaseData]
    default_cycles: int
    condition_suitability: Set[Condition]
    difficulty: int = 1

    @property
    def cycle_duration_seconds(self) -> float:
        """Total duration of one complete breathing cycle."""
        return sum(p.duration_seconds for p in self.phases)

    @property
    def total_duration_seconds(self) -> float:
        """Total duration for all default cycles."""
        return self.cycle_duration_seconds * self.default_cycles

    def get_timer_data(self, cycles: Optional[int] = None) -> List[Dict]:
        """Generate timer data for the UI to render phase-by-phase.

        Args:
            cycles: Number of cycles to generate. Uses default if None.

        Returns:
            List of dicts with phase timing for each step across all cycles.
        """
        num_cycles = cycles if cycles is not None else self.default_cycles
        timer_data: List[Dict] = []
        elapsed = 0.0
        for cycle_num in range(1, num_cycles + 1):
            for phase_data in self.phases:
                timer_data.append({
                    "cycle": cycle_num,
                    "phase": phase_data.phase.value,
                    "duration_seconds": phase_data.duration_seconds,
                    "instruction": phase_data.instruction,
                    "start_at": elapsed,
                    "end_at": elapsed + phase_data.duration_seconds,
                })
                elapsed += phase_data.duration_seconds
        return timer_data


@dataclass
class BreathingSession:
    """Tracks a single breathing exercise session.

    Attributes:
        session_id: Unique identifier for the session.
        exercise_type: Which exercise was performed.
        cycles_target: How many cycles were planned.
        cycles_completed: How many cycles were actually completed.
        mood_before: Self-reported mood before (1-10).
        mood_after: Self-reported mood after (1-10).
        started_at: When the session began.
        ended_at: When the session ended.
        completed: Whether the session was finished fully.
        notes: Optional user notes about the session.
    """
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    exercise_type: BreathingExerciseType = BreathingExerciseType.BOX_BREATHING
    cycles_target: int = 4
    cycles_completed: int = 0
    mood_before: Optional[int] = None
    mood_after: Optional[int] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    completed: bool = False
    notes: Optional[str] = None

    def start(self, mood_before: Optional[int] = None) -> None:
        """Mark the session as started.

        Args:
            mood_before: Self-reported mood on a 1-10 scale.
        """
        self.started_at = datetime.now().isoformat()
        if mood_before is not None:
            if not 1 <= mood_before <= 10:
                raise ValueError("mood_before must be between 1 and 10")
            self.mood_before = mood_before

    def end(self, cycles_completed: int, mood_after: Optional[int] = None) -> None:
        """Mark the session as ended.

        Args:
            cycles_completed: How many cycles the user finished.
            mood_after: Self-reported mood on a 1-10 scale.
        """
        self.ended_at = datetime.now().isoformat()
        self.cycles_completed = cycles_completed
        self.completed = cycles_completed >= self.cycles_target
        if mood_after is not None:
            if not 1 <= mood_after <= 10:
                raise ValueError("mood_after must be between 1 and 10")
            self.mood_after = mood_after

    @property
    def mood_improvement(self) -> Optional[int]:
        """Calculate mood change from before to after the session."""
        if self.mood_before is not None and self.mood_after is not None:
            return self.mood_after - self.mood_before
        return None

    def to_dict(self) -> Dict:
        """Serialize session to a dictionary for JSON storage."""
        return {
            "session_id": self.session_id,
            "exercise_type": self.exercise_type.value,
            "cycles_target": self.cycles_target,
            "cycles_completed": self.cycles_completed,
            "mood_before": self.mood_before,
            "mood_after": self.mood_after,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "completed": self.completed,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "BreathingSession":
        """Deserialize a session from a dictionary."""
        return cls(
            session_id=data["session_id"],
            exercise_type=BreathingExerciseType(data["exercise_type"]),
            cycles_target=data["cycles_target"],
            cycles_completed=data["cycles_completed"],
            mood_before=data.get("mood_before"),
            mood_after=data.get("mood_after"),
            started_at=data.get("started_at"),
            ended_at=data.get("ended_at"),
            completed=data.get("completed", False),
            notes=data.get("notes"),
        )


def _build_exercise_library() -> Dict[BreathingExerciseType, BreathingExercise]:
    """Build the full library of breathing exercises."""
    exercises: Dict[BreathingExerciseType, BreathingExercise] = {}

    exercises[BreathingExerciseType.BOX_BREATHING] = BreathingExercise(
        exercise_type=BreathingExerciseType.BOX_BREATHING,
        name="Box Breathing",
        description=(
            "Equal-duration inhale, hold, exhale, and hold pattern. "
            "Used by Navy SEALs for calm focus under pressure. "
            "Activates the parasympathetic nervous system."
        ),
        phases=[
            BreathPhaseData(BreathPhase.INHALE, 4.0, "Breathe in slowly through your nose"),
            BreathPhaseData(BreathPhase.HOLD_IN, 4.0, "Hold your breath gently"),
            BreathPhaseData(BreathPhase.EXHALE, 4.0, "Exhale slowly through your mouth"),
            BreathPhaseData(BreathPhase.HOLD_OUT, 4.0, "Rest with lungs empty"),
        ],
        default_cycles=4,
        condition_suitability={
            Condition.ANXIETY, Condition.PTSD, Condition.GENERAL,
            Condition.PANIC, Condition.OCD,
        },
        difficulty=2,
    )

    exercises[BreathingExerciseType.FOUR_SEVEN_EIGHT] = BreathingExercise(
        exercise_type=BreathingExerciseType.FOUR_SEVEN_EIGHT,
        name="4-7-8 Breathing",
        description=(
            "Inhale for 4 counts, hold for 7, exhale for 8. "
            "Developed by Dr. Andrew Weil, this technique acts as a natural "
            "tranquilizer for the nervous system and improves sleep."
        ),
        phases=[
            BreathPhaseData(BreathPhase.INHALE, 4.0, "Inhale quietly through your nose"),
            BreathPhaseData(BreathPhase.HOLD_IN, 7.0, "Hold your breath"),
            BreathPhaseData(BreathPhase.EXHALE, 8.0, "Exhale completely through your mouth"),
        ],
        default_cycles=4,
        condition_suitability={
            Condition.ANXIETY, Condition.INSOMNIA, Condition.GENERAL,
            Condition.PANIC,
        },
        difficulty=3,
    )

    exercises[BreathingExerciseType.DEEP_BELLY] = BreathingExercise(
        exercise_type=BreathingExerciseType.DEEP_BELLY,
        name="Deep Belly Breathing",
        description=(
            "Diaphragmatic breathing that engages the belly rather than the chest. "
            "Place one hand on your chest and one on your belly; only the belly "
            "hand should rise. Reduces cortisol and promotes relaxation."
        ),
        phases=[
            BreathPhaseData(BreathPhase.INHALE, 5.0,
                            "Breathe deeply into your belly, feel it expand"),
            BreathPhaseData(BreathPhase.EXHALE, 5.0,
                            "Let your belly fall as you exhale slowly"),
        ],
        default_cycles=6,
        condition_suitability={
            Condition.ANXIETY, Condition.DEPRESSION, Condition.GENERAL,
            Condition.PTSD, Condition.PANIC,
        },
        difficulty=1,
    )

    exercises[BreathingExerciseType.CALMING_BREATH] = BreathingExercise(
        exercise_type=BreathingExerciseType.CALMING_BREATH,
        name="Calming Breath",
        description=(
            "A slow 6-count breathing pattern with extended exhale. "
            "The longer exhale activates the vagus nerve and shifts the body "
            "into rest-and-digest mode."
        ),
        phases=[
            BreathPhaseData(BreathPhase.INHALE, 4.0,
                            "Breathe in slowly and steadily"),
            BreathPhaseData(BreathPhase.HOLD_IN, 2.0,
                            "Pause briefly at the top"),
            BreathPhaseData(BreathPhase.EXHALE, 6.0,
                            "Exhale slowly, twice as long as you inhaled"),
        ],
        default_cycles=5,
        condition_suitability={
            Condition.ANXIETY, Condition.PANIC, Condition.PTSD,
            Condition.GENERAL, Condition.OCD,
        },
        difficulty=2,
    )

    exercises[BreathingExerciseType.ENERGIZING_BREATH] = BreathingExercise(
        exercise_type=BreathingExerciseType.ENERGIZING_BREATH,
        name="Energizing Breath",
        description=(
            "Quick, rhythmic breathing cycles to increase alertness and energy. "
            "Short, forceful exhales through the nose with passive inhales. "
            "Similar to Kapalabhati. Use cautiously with anxiety conditions."
        ),
        phases=[
            BreathPhaseData(BreathPhase.INHALE, 1.0,
                            "Quick inhale through the nose"),
            BreathPhaseData(BreathPhase.EXHALE, 1.0,
                            "Forceful exhale through the nose"),
        ],
        default_cycles=10,
        condition_suitability={
            Condition.DEPRESSION, Condition.ADHD, Condition.GENERAL,
        },
        difficulty=2,
    )

    exercises[BreathingExerciseType.GROUNDING_BREATH] = BreathingExercise(
        exercise_type=BreathingExerciseType.GROUNDING_BREATH,
        name="Grounding Breath",
        description=(
            "Combines breathing with body awareness. On each inhale, feel your "
            "feet on the floor; on each exhale, release tension downward. "
            "Helpful during dissociation or flashbacks."
        ),
        phases=[
            BreathPhaseData(BreathPhase.INHALE, 4.0,
                            "Breathe in; feel your feet pressing the ground"),
            BreathPhaseData(BreathPhase.HOLD_IN, 2.0,
                            "Notice the weight of your body in your seat"),
            BreathPhaseData(BreathPhase.EXHALE, 6.0,
                            "Exhale and let tension drain down through your feet"),
            BreathPhaseData(BreathPhase.HOLD_OUT, 2.0,
                            "Rest; feel gravity supporting you"),
        ],
        default_cycles=5,
        condition_suitability={
            Condition.PTSD, Condition.ANXIETY, Condition.PANIC,
            Condition.OCD, Condition.GENERAL,
        },
        difficulty=2,
    )

    return exercises


class BreathingManager:
    """Manages breathing exercises, sessions, and statistics.

    Args:
        data_dir: Directory to persist session history.
    """

    EXERCISE_LIBRARY: Dict[BreathingExerciseType, BreathingExercise] = (
        _build_exercise_library()
    )

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._sessions_file = self.data_dir / "breathing_sessions.json"
        self._sessions: List[BreathingSession] = []
        self._load_sessions()

    # ── persistence ──────────────────────────────────────────────

    def _load_sessions(self) -> None:
        """Load session history from disk."""
        if self._sessions_file.exists():
            try:
                with open(self._sessions_file, "r") as fh:
                    data = json.load(fh)
                self._sessions = [BreathingSession.from_dict(s) for s in data]
            except (json.JSONDecodeError, KeyError):
                self._sessions = []

    def _save_sessions(self) -> None:
        """Persist session history to disk."""
        with open(self._sessions_file, "w") as fh:
            json.dump([s.to_dict() for s in self._sessions], fh, indent=2)

    # ── exercise access ──────────────────────────────────────────

    def get_exercise(
        self, exercise_type: BreathingExerciseType
    ) -> BreathingExercise:
        """Retrieve a breathing exercise definition by type.

        Args:
            exercise_type: The exercise type to look up.

        Returns:
            The corresponding BreathingExercise.

        Raises:
            KeyError: If the exercise type is not in the library.
        """
        if exercise_type not in self.EXERCISE_LIBRARY:
            raise KeyError(f"Unknown exercise type: {exercise_type}")
        return self.EXERCISE_LIBRARY[exercise_type]

    def list_exercises(self) -> List[BreathingExercise]:
        """Return all available breathing exercises."""
        return list(self.EXERCISE_LIBRARY.values())

    # ── session management ───────────────────────────────────────

    def create_session(
        self,
        exercise_type: BreathingExerciseType,
        cycles: Optional[int] = None,
        mood_before: Optional[int] = None,
    ) -> BreathingSession:
        """Create and start a new breathing session.

        Args:
            exercise_type: Which exercise to perform.
            cycles: Override the default cycle count.
            mood_before: Pre-session mood (1-10).

        Returns:
            The newly created BreathingSession.
        """
        exercise = self.get_exercise(exercise_type)
        session = BreathingSession(
            exercise_type=exercise_type,
            cycles_target=cycles if cycles is not None else exercise.default_cycles,
        )
        session.start(mood_before)
        return session

    def complete_session(
        self,
        session: BreathingSession,
        cycles_completed: int,
        mood_after: Optional[int] = None,
    ) -> BreathingSession:
        """End a session, record it, and persist.

        Args:
            session: The active session to complete.
            cycles_completed: Number of cycles finished.
            mood_after: Post-session mood (1-10).

        Returns:
            The completed session.
        """
        session.end(cycles_completed, mood_after)
        self._sessions.append(session)
        self._save_sessions()
        return session

    # ── recommendations ──────────────────────────────────────────

    def recommend(
        self,
        mood: Optional[int] = None,
        energy: Optional[int] = None,
        conditions: Optional[Set[Condition]] = None,
    ) -> List[BreathingExercise]:
        """Recommend exercises based on current state.

        Scoring favours exercises whose condition suitability overlaps with
        the user's conditions, adjusts for energy level (low energy prefers
        low difficulty, high energy can handle harder exercises), and weighs
        historical mood improvement.

        Args:
            mood: Current mood (1-10). Lower mood favours calming exercises.
            energy: Current energy (1-100). Lower energy favours easier exercises.
            conditions: Active mental health conditions.

        Returns:
            Exercises sorted by relevance (best first).
        """
        scored: List[tuple] = []
        conditions = conditions or set()

        for exercise in self.EXERCISE_LIBRARY.values():
            score = 0.0

            # Condition overlap
            overlap = len(exercise.condition_suitability & conditions)
            score += overlap * 20

            # General suitability fallback
            if Condition.GENERAL in exercise.condition_suitability:
                score += 5

            # Energy-based difficulty matching
            if energy is not None:
                if energy < 30:
                    score += max(0, (3 - exercise.difficulty)) * 10
                elif energy > 70:
                    score += exercise.difficulty * 5

            # Mood-based adjustments
            if mood is not None and mood <= 4:
                # Low mood: prefer calming, grounding exercises
                if exercise.exercise_type in (
                    BreathingExerciseType.CALMING_BREATH,
                    BreathingExerciseType.GROUNDING_BREATH,
                    BreathingExerciseType.DEEP_BELLY,
                ):
                    score += 15

            # Historical effectiveness for this exercise
            past = [
                s for s in self._sessions
                if s.exercise_type == exercise.exercise_type
                and s.mood_improvement is not None
            ]
            if past:
                avg_improvement = sum(
                    s.mood_improvement for s in past  # type: ignore[arg-type]
                ) / len(past)
                score += avg_improvement * 5

            scored.append((score, exercise))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ex for _, ex in scored]

    # ── statistics ───────────────────────────────────────────────

    def get_statistics(self) -> Dict:
        """Compute aggregate statistics across all sessions.

        Returns:
            Dictionary with total_sessions, completed_sessions,
            favorite_exercise, average_mood_improvement, and
            total_minutes.
        """
        if not self._sessions:
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "favorite_exercise": None,
                "average_mood_improvement": None,
                "total_minutes": 0.0,
            }

        completed = [s for s in self._sessions if s.completed]

        # Favourite exercise by frequency
        type_counts: Dict[str, int] = {}
        for s in self._sessions:
            key = s.exercise_type.value
            type_counts[key] = type_counts.get(key, 0) + 1
        favorite = max(type_counts, key=type_counts.get)  # type: ignore[arg-type]

        # Average mood improvement
        improvements = [
            s.mood_improvement for s in self._sessions
            if s.mood_improvement is not None
        ]
        avg_improvement = (
            sum(improvements) / len(improvements) if improvements else None
        )

        # Total practice time (approximate from cycles and exercise durations)
        total_seconds = 0.0
        for s in self._sessions:
            ex = self.EXERCISE_LIBRARY.get(s.exercise_type)
            if ex:
                total_seconds += ex.cycle_duration_seconds * s.cycles_completed

        return {
            "total_sessions": len(self._sessions),
            "completed_sessions": len(completed),
            "favorite_exercise": favorite,
            "average_mood_improvement": (
                round(avg_improvement, 2) if avg_improvement is not None else None
            ),
            "total_minutes": round(total_seconds / 60, 1),
        }

    @property
    def sessions(self) -> List[BreathingSession]:
        """Read-only access to the session history."""
        return list(self._sessions)
