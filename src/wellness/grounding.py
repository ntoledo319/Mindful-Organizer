"""
Grounding techniques for the Mindful Organizer application.

Provides structured grounding exercises for managing dissociation, anxiety,
panic attacks, and flashbacks. Includes sensory grounding, body scan,
object focus, temperature, movement, and safe place visualization techniques.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from core.constants import Condition


class GroundingType(Enum):
    """Available grounding technique types."""
    SENSORY_5_4_3_2_1 = "sensory_5_4_3_2_1"
    BODY_SCAN = "body_scan"
    OBJECT_FOCUS = "object_focus"
    TEMPERATURE = "temperature"
    MOVEMENT = "movement"
    SAFE_PLACE_VISUALIZATION = "safe_place_visualization"


class WhenToUse(Enum):
    """Situations when a grounding technique is most helpful."""
    PANIC_ATTACK = "panic_attack"
    FLASHBACK = "flashback"
    DISSOCIATION = "dissociation"
    ANXIETY_SPIKE = "anxiety_spike"
    RUMINATION = "rumination"
    EMOTIONAL_OVERWHELM = "emotional_overwhelm"
    DIFFICULTY_SLEEPING = "difficulty_sleeping"
    GENERAL_STRESS = "general_stress"


@dataclass
class GroundingTechnique:
    """A complete grounding technique definition.

    Attributes:
        grounding_type: The category of grounding technique.
        name: Human-readable technique name.
        description: Explanation of the technique and its benefits.
        steps: Ordered list of instruction strings guiding the user.
        duration_minutes: Estimated time to complete the technique.
        condition_suitability: Conditions this technique helps with.
        when_to_use: Situations where this technique is most effective.
    """
    grounding_type: GroundingType
    name: str
    description: str
    steps: list[str]
    duration_minutes: float
    condition_suitability: set[Condition]
    when_to_use: set[WhenToUse]

    def to_dict(self) -> dict:
        """Serialize technique to a dictionary."""
        return {
            "grounding_type": self.grounding_type.value,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "duration_minutes": self.duration_minutes,
            "condition_suitability": [c.value for c in self.condition_suitability],
            "when_to_use": [w.value for w in self.when_to_use],
        }


@dataclass
class GroundingSession:
    """Tracks a single grounding technique session.

    Attributes:
        session_id: Unique identifier for the session.
        grounding_type: Which technique was used.
        started_at: When the session began.
        ended_at: When the session ended.
        completed: Whether the technique was finished fully.
        effectiveness_rating: User rating of helpfulness (1-10).
        distress_before: Self-reported distress level before (0-100).
        distress_after: Self-reported distress level after (0-100).
        notes: Optional user notes about the session.
    """
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    grounding_type: GroundingType = GroundingType.SENSORY_5_4_3_2_1
    started_at: str | None = None
    ended_at: str | None = None
    completed: bool = False
    effectiveness_rating: int | None = None
    distress_before: int | None = None
    distress_after: int | None = None
    notes: str | None = None

    def start(self, distress_before: int | None = None) -> None:
        """Mark the session as started.

        Args:
            distress_before: Self-reported distress on a 0-100 scale.
        """
        self.started_at = datetime.now().isoformat()
        if distress_before is not None:
            if not 0 <= distress_before <= 100:
                raise ValueError("distress_before must be between 0 and 100")
            self.distress_before = distress_before

    def end(
        self,
        completed: bool = True,
        effectiveness_rating: int | None = None,
        distress_after: int | None = None,
    ) -> None:
        """Mark the session as ended.

        Args:
            completed: Whether the user finished the full technique.
            effectiveness_rating: How helpful the technique was (1-10).
            distress_after: Self-reported distress on a 0-100 scale.
        """
        self.ended_at = datetime.now().isoformat()
        self.completed = completed
        if effectiveness_rating is not None:
            if not 1 <= effectiveness_rating <= 10:
                raise ValueError("effectiveness_rating must be between 1 and 10")
            self.effectiveness_rating = effectiveness_rating
        if distress_after is not None:
            if not 0 <= distress_after <= 100:
                raise ValueError("distress_after must be between 0 and 100")
            self.distress_after = distress_after

    @property
    def distress_reduction(self) -> int | None:
        """Calculate distress reduction from before to after the session."""
        if self.distress_before is not None and self.distress_after is not None:
            return self.distress_before - self.distress_after
        return None

    def to_dict(self) -> dict:
        """Serialize session to a dictionary for JSON storage."""
        return {
            "session_id": self.session_id,
            "grounding_type": self.grounding_type.value,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "completed": self.completed,
            "effectiveness_rating": self.effectiveness_rating,
            "distress_before": self.distress_before,
            "distress_after": self.distress_after,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GroundingSession":
        """Deserialize a session from a dictionary."""
        return cls(
            session_id=data["session_id"],
            grounding_type=GroundingType(data["grounding_type"]),
            started_at=data.get("started_at"),
            ended_at=data.get("ended_at"),
            completed=data.get("completed", False),
            effectiveness_rating=data.get("effectiveness_rating"),
            distress_before=data.get("distress_before"),
            distress_after=data.get("distress_after"),
            notes=data.get("notes"),
        )


def _build_technique_library() -> dict[GroundingType, GroundingTechnique]:
    """Build the full library of grounding techniques."""
    techniques: dict[GroundingType, GroundingTechnique] = {}

    techniques[GroundingType.SENSORY_5_4_3_2_1] = GroundingTechnique(
        grounding_type=GroundingType.SENSORY_5_4_3_2_1,
        name="5-4-3-2-1 Sensory Grounding",
        description=(
            "Engage each of your five senses to anchor yourself in the present "
            "moment. This technique interrupts anxious or dissociative thought "
            "patterns by redirecting attention to immediate physical reality."
        ),
        steps=[
            "Take a slow, deep breath to begin.",
            "SEE: Look around and name 5 things you can see. Notice their colors, shapes, and textures.",
            "TOUCH: Notice 4 things you can physically feel. The fabric of your clothes, the chair beneath you, the temperature of the air, the ground under your feet.",
            "HEAR: Listen for 3 sounds. Perhaps distant traffic, a fan humming, birds outside, or your own breathing.",
            "SMELL: Identify 2 things you can smell. If you cannot detect anything, move to a different spot or smell your sleeve, hand, or a nearby object.",
            "TASTE: Notice 1 thing you can taste. The residue of your last drink, the freshness of your mouth, or take a small sip of water.",
            "Take another deep breath. Notice how you feel now compared to when you started.",
        ],
        duration_minutes=5.0,
        condition_suitability={
            Condition.ANXIETY, Condition.PTSD, Condition.PANIC,
            Condition.DISSOCIATION, Condition.GENERAL,
        },
        when_to_use={
            WhenToUse.PANIC_ATTACK, WhenToUse.FLASHBACK,
            WhenToUse.DISSOCIATION, WhenToUse.ANXIETY_SPIKE,
        },
    )

    techniques[GroundingType.BODY_SCAN] = GroundingTechnique(
        grounding_type=GroundingType.BODY_SCAN,
        name="Body Scan Grounding",
        description=(
            "A head-to-toe awareness exercise that reconnects you with your "
            "physical body. By systematically noticing sensations in each body "
            "part, you draw attention away from distressing thoughts and into "
            "the present moment."
        ),
        steps=[
            "Sit or lie in a comfortable position. Close your eyes if that feels safe.",
            "Bring your attention to the top of your head. Notice any sensations: warmth, tingling, pressure, or nothing at all.",
            "Move your attention to your forehead and temples. Let any tension soften.",
            "Notice your eyes, cheeks, and jaw. Unclench your jaw if it is tight.",
            "Shift awareness to your neck and shoulders. Breathe into any tightness.",
            "Feel your arms from shoulders to fingertips. Notice temperature, weight, or pulsing.",
            "Bring attention to your chest. Feel the rise and fall of each breath.",
            "Notice your stomach and lower back. Allow your belly to be soft.",
            "Move to your hips and pelvis. Feel the support beneath you.",
            "Travel down through your thighs, knees, and calves.",
            "Finally, notice your feet. Feel the contact with the floor or shoe.",
            "Take a full breath and gently open your eyes. Notice how your body feels as a whole.",
        ],
        duration_minutes=10.0,
        condition_suitability={
            Condition.ANXIETY, Condition.PTSD, Condition.DISSOCIATION,
            Condition.GENERAL, Condition.INSOMNIA,
        },
        when_to_use={
            WhenToUse.DISSOCIATION, WhenToUse.ANXIETY_SPIKE,
            WhenToUse.DIFFICULTY_SLEEPING, WhenToUse.GENERAL_STRESS,
        },
    )

    techniques[GroundingType.OBJECT_FOCUS] = GroundingTechnique(
        grounding_type=GroundingType.OBJECT_FOCUS,
        name="Object Focus Grounding",
        description=(
            "Choose a single object and examine it with intense, mindful "
            "attention. This focused observation anchors the mind in concrete "
            "reality and can break cycles of rumination or panic."
        ),
        steps=[
            "Pick up a small object near you: a pen, a stone, a mug, keys, or anything available.",
            "Hold it in your hands. Feel its weight.",
            "Notice the temperature of the object. Is it cool, warm, or neutral?",
            "Examine its texture. Run your fingers over every surface. Is it smooth, rough, ridged, or bumpy?",
            "Look at its color closely. Are there variations, patterns, or reflections?",
            "Notice its shape and edges. Trace the outline with your finger.",
            "If appropriate, bring it near your nose. Does it have a smell?",
            "Tap it gently. What sound does it make?",
            "Set the object down. Take a breath and notice how you feel.",
        ],
        duration_minutes=3.0,
        condition_suitability={
            Condition.ANXIETY, Condition.PTSD, Condition.PANIC,
            Condition.DISSOCIATION, Condition.OCD, Condition.GENERAL,
        },
        when_to_use={
            WhenToUse.PANIC_ATTACK, WhenToUse.DISSOCIATION,
            WhenToUse.RUMINATION, WhenToUse.ANXIETY_SPIKE,
        },
    )

    techniques[GroundingType.TEMPERATURE] = GroundingTechnique(
        grounding_type=GroundingType.TEMPERATURE,
        name="Temperature Grounding",
        description=(
            "Use temperature change to create a strong physical sensation that "
            "anchors you in the present. Cold stimulation activates the dive "
            "reflex, which slows heart rate and calms the nervous system."
        ),
        steps=[
            "Choose a method: cold water on wrists, holding an ice cube, splashing your face, or holding a cold drink.",
            "If using cold water: run cold water over your wrists for 30 seconds. Focus entirely on the sensation.",
            "If using ice: hold an ice cube in your palm. Notice the cold spreading, the melting, the wetness.",
            "If splashing your face: cup cold water in your hands and gently splash your face. Feel each droplet.",
            "Pay attention to the exact boundary where cold meets warmth on your skin.",
            "Breathe slowly while focusing on the temperature sensation.",
            "When the intensity fades or the ice melts, notice the lingering cool sensation.",
            "Dry your hands. Take a moment to check in with yourself.",
        ],
        duration_minutes=3.0,
        condition_suitability={
            Condition.PANIC, Condition.DISSOCIATION, Condition.BPD,
            Condition.PTSD, Condition.GENERAL,
        },
        when_to_use={
            WhenToUse.PANIC_ATTACK, WhenToUse.DISSOCIATION,
            WhenToUse.EMOTIONAL_OVERWHELM,
        },
    )

    techniques[GroundingType.MOVEMENT] = GroundingTechnique(
        grounding_type=GroundingType.MOVEMENT,
        name="Movement Grounding",
        description=(
            "Physical movement engages the body and breaks the freeze response "
            "common in anxiety and trauma. These gentle exercises require no "
            "equipment and can be done almost anywhere."
        ),
        steps=[
            "Stand up if you are seated. Feel both feet flat on the floor.",
            "WALK: Take 10 slow, deliberate steps. Feel the heel-to-toe roll with each step.",
            "STRETCH: Raise your arms overhead and stretch tall. Hold for 5 seconds, then release.",
            "Slowly roll your shoulders backward 5 times, then forward 5 times.",
            "PUSH: Place your palms flat against a wall. Push firmly for 10 seconds. Feel the resistance in your arms and chest.",
            "STAMP: Gently stamp each foot on the floor 5 times. Feel the vibration travel up your legs.",
            "Shake your hands loosely at your sides for 10 seconds, as if flicking water off.",
            "Stand still. Take a deep breath. Notice the energy in your body.",
        ],
        duration_minutes=5.0,
        condition_suitability={
            Condition.ANXIETY, Condition.PTSD, Condition.DEPRESSION,
            Condition.DISSOCIATION, Condition.ADHD, Condition.GENERAL,
        },
        when_to_use={
            WhenToUse.DISSOCIATION, WhenToUse.ANXIETY_SPIKE,
            WhenToUse.EMOTIONAL_OVERWHELM, WhenToUse.GENERAL_STRESS,
        },
    )

    techniques[GroundingType.SAFE_PLACE_VISUALIZATION] = GroundingTechnique(
        grounding_type=GroundingType.SAFE_PLACE_VISUALIZATION,
        name="Safe Place Visualization",
        description=(
            "Guided imagery to create or revisit a mental safe space. This "
            "technique builds a portable refuge you can access any time you "
            "feel overwhelmed. With practice, the calming effect strengthens."
        ),
        steps=[
            "Sit comfortably and close your eyes if that feels safe. Take three slow breaths.",
            "Imagine a place where you feel completely safe and at peace. This can be real or imagined.",
            "Begin to build the scene. What do you see? Notice colors, light, and shapes.",
            "What sounds are present in your safe place? Gentle waves, birdsong, silence, soft music?",
            "What can you feel? A warm breeze, soft grass, a cozy blanket, warm sunlight?",
            "What scents are in the air? Flowers, ocean salt, fresh rain, baking bread?",
            "Notice the temperature. Let it be exactly what feels most comforting.",
            "Find a spot to settle in your safe place. Sit or lie down there.",
            "Let a sense of safety and calm wash over you. You are protected here.",
            "Spend a few quiet moments in this place. There is nothing you need to do.",
            "When you are ready, take a deep breath and gently bring your awareness back to the room.",
            "Open your eyes slowly. Remember: you can return to this place any time you need it.",
        ],
        duration_minutes=8.0,
        condition_suitability={
            Condition.PTSD, Condition.ANXIETY, Condition.INSOMNIA,
            Condition.BPD, Condition.GENERAL,
        },
        when_to_use={
            WhenToUse.FLASHBACK, WhenToUse.ANXIETY_SPIKE,
            WhenToUse.DIFFICULTY_SLEEPING, WhenToUse.EMOTIONAL_OVERWHELM,
            WhenToUse.GENERAL_STRESS,
        },
    )

    return techniques


class GroundingManager:
    """Manages grounding techniques, sessions, and statistics.

    Args:
        data_dir: Directory to persist session history.
    """

    TECHNIQUE_LIBRARY: dict[GroundingType, GroundingTechnique] = (
        _build_technique_library()
    )

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._sessions_file = self.data_dir / "grounding_sessions.json"
        self._sessions: list[GroundingSession] = []
        self._load_sessions()

    # -- persistence ----------------------------------------------------------

    def _load_sessions(self) -> None:
        """Load session history from disk."""
        if self._sessions_file.exists():
            try:
                with open(self._sessions_file) as fh:
                    data = json.load(fh)
                self._sessions = [GroundingSession.from_dict(s) for s in data]
            except (json.JSONDecodeError, KeyError):
                self._sessions = []

    def _save_sessions(self) -> None:
        """Persist session history to disk."""
        with open(self._sessions_file, "w") as fh:
            json.dump([s.to_dict() for s in self._sessions], fh, indent=2)

    # -- technique access -----------------------------------------------------

    def get_technique(self, grounding_type: GroundingType) -> GroundingTechnique:
        """Retrieve a grounding technique definition by type.

        Args:
            grounding_type: The technique type to look up.

        Returns:
            The corresponding GroundingTechnique.

        Raises:
            KeyError: If the technique type is not in the library.
        """
        if grounding_type not in self.TECHNIQUE_LIBRARY:
            raise KeyError(f"Unknown grounding type: {grounding_type}")
        return self.TECHNIQUE_LIBRARY[grounding_type]

    def list_techniques(self) -> list[GroundingTechnique]:
        """Return all available grounding techniques."""
        return list(self.TECHNIQUE_LIBRARY.values())

    # -- session management ---------------------------------------------------

    def create_session(
        self,
        grounding_type: GroundingType,
        distress_before: int | None = None,
    ) -> GroundingSession:
        """Create and start a new grounding session.

        Args:
            grounding_type: Which technique to use.
            distress_before: Pre-session distress level (0-100).

        Returns:
            The newly created GroundingSession.
        """
        self.get_technique(grounding_type)  # validate type exists
        session = GroundingSession(grounding_type=grounding_type)
        session.start(distress_before)
        return session

    def complete_session(
        self,
        session: GroundingSession,
        completed: bool = True,
        effectiveness_rating: int | None = None,
        distress_after: int | None = None,
    ) -> GroundingSession:
        """End a session, record it, and persist.

        Args:
            session: The active session to complete.
            completed: Whether the user finished the technique.
            effectiveness_rating: How helpful it was (1-10).
            distress_after: Post-session distress (0-100).

        Returns:
            The completed session.
        """
        session.end(completed, effectiveness_rating, distress_after)
        self._sessions.append(session)
        self._save_sessions()
        return session

    # -- recommendations ------------------------------------------------------

    def recommend(
        self,
        situation: WhenToUse | None = None,
        conditions: set[Condition] | None = None,
        max_duration_minutes: float | None = None,
    ) -> list[GroundingTechnique]:
        """Recommend techniques based on the current situation.

        Scoring favours techniques matching the current situation, overlapping
        conditions, good historical effectiveness, and respects time constraints.

        Args:
            situation: What is happening right now.
            conditions: Active mental health conditions.
            max_duration_minutes: Maximum time available.

        Returns:
            Techniques sorted by relevance (best first).
        """
        scored: list[tuple] = []
        conditions = conditions or set()

        for technique in self.TECHNIQUE_LIBRARY.values():
            # Skip if too long
            if (
                max_duration_minutes is not None
                and technique.duration_minutes > max_duration_minutes
            ):
                continue

            score = 0.0

            # Situation match
            if situation is not None and situation in technique.when_to_use:
                score += 30

            # Condition overlap
            overlap = len(technique.condition_suitability & conditions)
            score += overlap * 15

            # General suitability bonus
            if Condition.GENERAL in technique.condition_suitability:
                score += 5

            # Historical effectiveness
            past = [
                s for s in self._sessions
                if s.grounding_type == technique.grounding_type
                and s.effectiveness_rating is not None
            ]
            if past:
                avg_effectiveness = sum(
                    s.effectiveness_rating for s in past  # type: ignore[misc]
                ) / len(past)
                score += avg_effectiveness * 3

            # Historical distress reduction
            past_reduction = [
                s for s in self._sessions
                if s.grounding_type == technique.grounding_type
                and s.distress_reduction is not None
            ]
            if past_reduction:
                avg_reduction = sum(
                    s.distress_reduction for s in past_reduction  # type: ignore[misc]
                ) / len(past_reduction)
                score += avg_reduction * 0.2

            scored.append((score, technique))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored]

    # -- statistics -----------------------------------------------------------

    def get_statistics(self) -> dict:
        """Compute aggregate statistics across all grounding sessions.

        Returns:
            Dictionary with total_sessions, completed_sessions,
            favorite_technique, average_effectiveness,
            average_distress_reduction.
        """
        if not self._sessions:
            return {
                "total_sessions": 0,
                "completed_sessions": 0,
                "favorite_technique": None,
                "average_effectiveness": None,
                "average_distress_reduction": None,
            }

        completed = [s for s in self._sessions if s.completed]

        # Favourite technique by frequency
        type_counts: dict[str, int] = {}
        for s in self._sessions:
            key = s.grounding_type.value
            type_counts[key] = type_counts.get(key, 0) + 1
        favorite = max(type_counts, key=type_counts.get)  # type: ignore[arg-type]

        # Average effectiveness
        ratings = [
            s.effectiveness_rating for s in self._sessions
            if s.effectiveness_rating is not None
        ]
        avg_effectiveness = (
            round(sum(ratings) / len(ratings), 2) if ratings else None
        )

        # Average distress reduction
        reductions = [
            s.distress_reduction for s in self._sessions
            if s.distress_reduction is not None
        ]
        avg_reduction = (
            round(sum(reductions) / len(reductions), 2) if reductions else None
        )

        return {
            "total_sessions": len(self._sessions),
            "completed_sessions": len(completed),
            "favorite_technique": favorite,
            "average_effectiveness": avg_effectiveness,
            "average_distress_reduction": avg_reduction,
        }

    @property
    def sessions(self) -> list[GroundingSession]:
        """Read-only access to the session history."""
        return list(self._sessions)
