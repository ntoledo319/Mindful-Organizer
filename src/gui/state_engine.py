"""Hearth's State Engine — the differentiator made real.

Turns what the app senses (mood, energy, sleep, task pressure, time of day) into a
``HearthState``, then *composes* the room: how warm the ember glows, the one true
sentence Hearth says, which single door is primary, and how much it shows. This is
the "behavioral tokens" idea from docs/design/VISION.md, finally consumed instead of
sitting dead in a dataclass.

Kept deliberately small and pure (no Qt here) so it is testable and reusable; the
widgets read its output. v1 is honest and rule-based; richer inference is future work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


def _clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def _part_of_day(hour: int) -> str:
    if hour < 5:
        return "night"
    if hour < 12:
        return "morning"
    if hour < 17:
        return "afternoon"
    if hour < 22:
        return "evening"
    return "night"


@dataclass
class HearthState:
    """A point-in-time read of the person in front of the screen (all 0..1)."""

    energy: float = 0.5  # drained ↔ wired
    mood: float = 0.5  # low ↔ bright
    arousal: float = 0.4  # calm ↔ activated
    part_of_day: str = "morning"
    has_data: bool = False  # False until the user has told Hearth anything

    @property
    def is_depleted(self) -> bool:
        return self.energy <= 0.34 or self.mood <= 0.3

    @property
    def is_activated(self) -> bool:
        return self.arousal >= 0.66


@dataclass
class Composition:
    """What the room becomes for this state — read directly by the Today widget."""

    glow: float = 0.5  # hearthlight brightness
    density: float = 1.0  # 0.85 spacious (depleted) … 1.0 normal
    line1: str = ""  # serif greeting, plain
    line2: str = ""  # serif greeting, warm/accent — the "let's keep today small"
    caption: str = ""  # quiet muted line (date / nothing due)
    primary_label: str = "Sit with me for a minute"
    primary_tab: str = "breathing"
    doors: list[tuple[str, str]] = field(default_factory=list)  # (label, tab) ghosts


def compute_state(
    snapshot=None,
    profile=None,
    pending_tasks: int = 0,
    now: datetime | None = None,
) -> HearthState:
    """Infer a HearthState from a WellnessSnapshot-like object and context.

    Everything is best-effort and defensive — a missing field never raises; it just
    leaves that axis at its calm default.
    """
    now = now or datetime.now()
    state = HearthState(part_of_day=_part_of_day(now.hour))

    mood = getattr(snapshot, "mood_score", None) if snapshot else None
    energy = getattr(snapshot, "energy_score", None) if snapshot else None
    sleep_h = getattr(snapshot, "sleep_hours", None) if snapshot else None

    if mood is not None:
        state.mood = _clamp01((float(mood) - 1) / 9.0)
        state.has_data = True
    if energy is not None:
        state.energy = _clamp01((float(energy) - 1) / 9.0)
        state.has_data = True

    # Short sleep drains energy and lifts arousal a little.
    if sleep_h is not None and sleep_h < 6:
        state.energy = _clamp01(state.energy - (6 - float(sleep_h)) * 0.06)

    # Task pressure and a low mood read as more activated.
    pressure = _clamp01(pending_tasks / 8.0)
    state.arousal = _clamp01(0.3 + pressure * 0.4 + (0.5 - state.mood) * 0.4)
    # Late night nudges toward winding down.
    if state.part_of_day == "night":
        state.arousal = _clamp01(state.arousal - 0.1)
    return state


def _time_noun(part: str) -> str:
    """The plain noun for the time of day ('a heavy {night}')."""
    return part if part in ("morning", "afternoon", "evening", "night") else "morning"


def _opener(part: str, period_you: str) -> str:
    """A natural greeting opener that reads right at every hour."""
    if part == "night":
        return f"A quiet hour{period_you}"
    return f"Good {part}{period_you}"


def compose(state: HearthState, name: str = "", pending_tasks: int = 0) -> Composition:
    """Compose the room for a state — the one sentence, the one door, the glow."""
    you = (name or "").strip()
    comma_you = f", {you}" if you else ""
    period_you = f", {you}." if you else "."

    c = Composition()
    c.glow = _clamp01(0.32 + state.energy * 0.6)

    if not state.has_data:
        # First contact: receive them, don't interrogate.
        c.line1 = _opener(state.part_of_day, period_you)
        c.line2 = "Tell me how you're landing, and I'll shape the day around it."
        c.primary_label = "Take a moment with me"
        c.primary_tab = "mood_tracker"
        c.density = 0.95
    elif state.is_depleted:
        # Drained / low: dim, quiet, one small thing.
        word = "heavy" if state.mood <= 0.3 else "slow"
        c.line1 = f"It's a {word} {_time_noun(state.part_of_day)}{period_you}"
        c.line2 = "Let's keep today small."
        c.primary_label = "Sit with me for a minute"
        c.primary_tab = "breathing"
        c.glow = _clamp01(c.glow - 0.08)
        c.density = 0.85
    elif state.is_activated:
        # Wired / pressured: steady, narrow to one step.
        c.line1 = f"A lot's moving{comma_you}."
        c.line2 = "We'll take it one thing at a time."
        c.primary_label = "Find the next small step"
        c.primary_tab = "task_manager"
    else:
        # Steady: warm, open the day.
        c.line1 = _opener(state.part_of_day, period_you)
        c.line2 = "There's room in today." if state.mood >= 0.55 else "Let's ease into it."
        c.primary_label = "Look at today together"
        c.primary_tab = "task_manager"

    # The quiet caption: the time, and how today actually sits.
    when = datetime.now().strftime("%A").lower()
    if pending_tasks <= 0:
        c.caption = f"{when.capitalize()}. Nothing's due — this time is yours."
    elif pending_tasks == 1:
        c.caption = f"{when.capitalize()}. One thing waiting, whenever you're ready."
    else:
        c.caption = f"{when.capitalize()}. {pending_tasks} things waiting — no rush."

    # The receding side-doors (never the primary). Crisis lives in the shell, always.
    c.doors = [
        ("A few words about today", "journaling"),
        ("Tend the medication shelf", "medication"),
        ("Quiet everything for a while", "automation"),
    ]
    return c
