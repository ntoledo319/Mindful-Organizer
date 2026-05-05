"""
AI-powered task decomposition for overwhelming tasks.

Breaks complex tasks into condition-aware micro-steps using keyword
matching and a built-in template library.  No external AI API required.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from core.constants import Condition

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TaskComplexity(Enum):
    """Estimated complexity of a task."""
    TRIVIAL = "trivial"        # already micro-sized
    SIMPLE = "simple"          # 1-3 steps
    MODERATE = "moderate"      # 4-8 steps
    COMPLEX = "complex"        # 9+ steps


class EnergyLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


# ---------------------------------------------------------------------------
# Data-classes
# ---------------------------------------------------------------------------

@dataclass
class SubTask:
    """A single micro-step within a decomposed task."""
    title: str
    estimated_minutes: int
    energy_required: EnergyLevel
    order: int
    parent_task_id: str
    subtask_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    completion_criteria: str | None = None
    prep_note: str | None = None
    reward: str | None = None
    is_first_step: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "subtask_id": self.subtask_id,
            "title": self.title,
            "estimated_minutes": self.estimated_minutes,
            "energy_required": self.energy_required.value,
            "order": self.order,
            "parent_task_id": self.parent_task_id,
            "completion_criteria": self.completion_criteria,
            "prep_note": self.prep_note,
            "reward": self.reward,
            "is_first_step": self.is_first_step,
        }


@dataclass
class DecompositionResult:
    """Complete decomposition of a task."""
    task_title: str
    task_id: str
    complexity: TaskComplexity
    condition: Condition
    subtasks: list[SubTask]
    total_estimated_minutes: int
    just_start_step: SubTask | None = None
    encouragement: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_title": self.task_title,
            "task_id": self.task_id,
            "complexity": self.complexity.value,
            "condition": self.condition.value,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "total_estimated_minutes": self.total_estimated_minutes,
            "just_start_step": self.just_start_step.to_dict() if self.just_start_step else None,
            "encouragement": self.encouragement,
        }


# ---------------------------------------------------------------------------
# Micro-reward library
# ---------------------------------------------------------------------------

_REWARDS = [
    "Take 3 deep breaths and smile.",
    "Stand up and stretch for 30 seconds.",
    "Drink a glass of water.",
    "Look out the window for a minute.",
    "Give yourself a mental high-five.",
    "Listen to one favourite song.",
    "Do a quick hand massage.",
    "Enjoy a small healthy snack.",
    "Doodle something fun for 1 minute.",
    "Text someone something kind.",
    "Celebrate: you are making progress!",
    "Close your eyes and relax your shoulders.",
    "Write down one thing you are grateful for.",
    "Take a short walk around the room.",
    "Do 5 gentle neck rolls.",
]


def _pick_reward(index: int) -> str:
    """Deterministically pick a reward based on step index."""
    return _REWARDS[index % len(_REWARDS)]


# ---------------------------------------------------------------------------
# Complexity estimation
# ---------------------------------------------------------------------------

_COMPLEX_KEYWORDS = [
    "project", "report", "presentation", "thesis", "paper", "plan",
    "organize", "organise", "reorganize", "renovate", "move",
    "deep clean", "spring clean", "meal prep for the week",
    "tax", "taxes", "budget", "application", "proposal",
]

_MODERATE_KEYWORDS = [
    "clean", "cook", "study", "prepare", "write", "email",
    "shopping", "grocery", "groceries", "laundry", "pack",
    "exercise", "workout", "errand", "appointment",
]

_SIMPLE_KEYWORDS = [
    "call", "text", "message", "reply", "send", "pick up",
    "buy", "take out", "water", "feed", "charge",
]


def _estimate_complexity(title: str) -> TaskComplexity:
    """Estimate task complexity from title keywords."""
    lower = title.lower()
    word_count = len(lower.split())

    for kw in _COMPLEX_KEYWORDS:
        if kw in lower:
            return TaskComplexity.COMPLEX

    for kw in _MODERATE_KEYWORDS:
        if kw in lower:
            return TaskComplexity.MODERATE

    for kw in _SIMPLE_KEYWORDS:
        if kw in lower:
            return TaskComplexity.SIMPLE

    # Heuristic: longer titles often describe more complex tasks
    if word_count >= 8:
        return TaskComplexity.COMPLEX
    if word_count >= 4:
        return TaskComplexity.MODERATE
    return TaskComplexity.SIMPLE


# ---------------------------------------------------------------------------
# Template library
# ---------------------------------------------------------------------------

# Each template: list of (title_template, estimated_minutes, energy)
# Titles use {task} as placeholder for the original task title.

_TEMPLATES: dict[str, list[tuple]] = {
    "cleaning": [
        ("Gather cleaning supplies", 3, EnergyLevel.LOW),
        ("Pick up visible clutter from surfaces", 5, EnergyLevel.LOW),
        ("Put clutter items where they belong", 5, EnergyLevel.MODERATE),
        ("Wipe down surfaces with a damp cloth", 5, EnergyLevel.MODERATE),
        ("Sweep or vacuum the floor", 7, EnergyLevel.MODERATE),
        ("Mop or spot-clean the floor", 5, EnergyLevel.MODERATE),
        ("Take out the rubbish", 3, EnergyLevel.LOW),
        ("Put cleaning supplies away", 2, EnergyLevel.LOW),
        ("Do a final walkthrough check", 2, EnergyLevel.LOW),
    ],
    "studying": [
        ("Choose the specific topic or chapter to study", 2, EnergyLevel.LOW),
        ("Gather materials (notes, textbook, laptop)", 3, EnergyLevel.LOW),
        ("Set a 25-minute timer (Pomodoro)", 1, EnergyLevel.LOW),
        ("Read through the material once without notes", 10, EnergyLevel.MODERATE),
        ("Write down key concepts in your own words", 10, EnergyLevel.HIGH),
        ("Take a 5-minute break", 5, EnergyLevel.LOW),
        ("Create flashcards or summary notes", 10, EnergyLevel.HIGH),
        ("Quiz yourself on the material", 10, EnergyLevel.HIGH),
        ("Review mistakes and re-read weak areas", 5, EnergyLevel.MODERATE),
        ("Write one sentence summarizing what you learned", 2, EnergyLevel.LOW),
    ],
    "work_project": [
        ("Open the project files and review where you left off", 3, EnergyLevel.LOW),
        ("List the 3 most important things to accomplish", 5, EnergyLevel.MODERATE),
        ("Set up your workspace (close distractions, water nearby)", 3, EnergyLevel.LOW),
        ("Work on the highest-priority item for 15 minutes", 15, EnergyLevel.HIGH),
        ("Take a 3-minute movement break", 3, EnergyLevel.LOW),
        ("Continue or start the second priority item", 15, EnergyLevel.HIGH),
        ("Save your work and make notes on progress", 3, EnergyLevel.LOW),
        ("Update any tracking tools or team members", 5, EnergyLevel.MODERATE),
        ("Plan the next session's first task", 2, EnergyLevel.LOW),
    ],
    "errands": [
        ("Write a list of all errands to run", 3, EnergyLevel.LOW),
        ("Check that you have keys, wallet, phone, bags", 2, EnergyLevel.LOW),
        ("Plan the most efficient route", 3, EnergyLevel.MODERATE),
        ("Complete the first stop", 10, EnergyLevel.MODERATE),
        ("Check the errand off your list", 1, EnergyLevel.LOW),
        ("Complete the next stop", 10, EnergyLevel.MODERATE),
        ("Head home and put things away", 5, EnergyLevel.LOW),
        ("Rest for a few minutes — you did it!", 5, EnergyLevel.LOW),
    ],
    "cooking": [
        ("Decide on the recipe or meal", 3, EnergyLevel.LOW),
        ("Check that you have all ingredients", 3, EnergyLevel.LOW),
        ("Gather pots, pans, and utensils", 3, EnergyLevel.LOW),
        ("Wash and prep vegetables/ingredients", 10, EnergyLevel.MODERATE),
        ("Start cooking (follow the recipe step by step)", 15, EnergyLevel.HIGH),
        ("Set a timer if anything needs to simmer/bake", 1, EnergyLevel.LOW),
        ("Plate the food", 3, EnergyLevel.LOW),
        ("Enjoy your meal — you cooked!", 10, EnergyLevel.LOW),
        ("Soak dishes and wipe down the kitchen", 5, EnergyLevel.MODERATE),
    ],
    "exercise": [
        ("Put on workout clothes and shoes", 3, EnergyLevel.LOW),
        ("Fill a water bottle", 1, EnergyLevel.LOW),
        ("Do a 3-minute gentle warm-up (marching, stretching)", 3, EnergyLevel.LOW),
        ("Start the first set or first 5 minutes of cardio", 5, EnergyLevel.MODERATE),
        ("Continue for another 5-10 minutes", 10, EnergyLevel.HIGH),
        ("Cool down with gentle stretches", 5, EnergyLevel.LOW),
        ("Drink water and rest", 3, EnergyLevel.LOW),
        ("Log the workout if you track it", 2, EnergyLevel.LOW),
    ],
    "email": [
        ("Open your inbox", 1, EnergyLevel.LOW),
        ("Scan subject lines and star important ones", 3, EnergyLevel.LOW),
        ("Reply to the quickest email first (under 2 min)", 2, EnergyLevel.LOW),
        ("Draft a response to the most important email", 5, EnergyLevel.MODERATE),
        ("Review and send the draft", 2, EnergyLevel.LOW),
        ("Archive or delete emails you have handled", 2, EnergyLevel.LOW),
    ],
    "appointment": [
        ("Look up the address and travel time", 3, EnergyLevel.LOW),
        ("Write down any questions you want to ask", 5, EnergyLevel.MODERATE),
        ("Gather any documents or ID you need", 3, EnergyLevel.LOW),
        ("Set an alarm for when to leave", 1, EnergyLevel.LOW),
        ("Travel to the appointment", 10, EnergyLevel.MODERATE),
        ("Attend the appointment", 15, EnergyLevel.MODERATE),
        ("Write down key takeaways afterwards", 3, EnergyLevel.LOW),
    ],
}

# Map keywords to template names
_TEMPLATE_KEYWORD_MAP: dict[str, str] = {
    "clean": "cleaning", "cleaning": "cleaning", "tidy": "cleaning",
    "deep clean": "cleaning", "declutter": "cleaning",
    "study": "studying", "studying": "studying", "homework": "studying",
    "learn": "studying", "revision": "studying", "revise": "studying",
    "exam": "studying", "research": "studying",
    "project": "work_project", "report": "work_project",
    "presentation": "work_project", "proposal": "work_project",
    "errand": "errands", "errands": "errands", "shopping": "errands",
    "grocery": "errands", "groceries": "errands",
    "cook": "cooking", "cooking": "cooking", "meal prep": "cooking",
    "bake": "cooking", "recipe": "cooking",
    "exercise": "exercise", "workout": "exercise", "gym": "exercise",
    "run": "exercise", "jog": "exercise", "yoga": "exercise",
    "email": "email", "emails": "email", "inbox": "email",
    "appointment": "appointment", "doctor": "appointment",
    "dentist": "appointment", "therapist": "appointment",
    "meeting": "appointment",
}


def _find_template(title: str) -> str | None:
    """Match a task title to a template name."""
    lower = title.lower()
    # Try multi-word keys first (longer = more specific)
    sorted_keys = sorted(_TEMPLATE_KEYWORD_MAP.keys(), key=len, reverse=True)
    for kw in sorted_keys:
        if kw in lower:
            return _TEMPLATE_KEYWORD_MAP[kw]
    return None


# ---------------------------------------------------------------------------
# Condition-aware step modifiers
# ---------------------------------------------------------------------------

def _apply_adhd_style(steps: list[SubTask]) -> list[SubTask]:
    """ADHD: very small steps, action verbs, estimated time per step (already done).

    Splits any step longer than 10 minutes and adds transition cues.
    """
    result: list[SubTask] = []
    order = 1
    for s in steps:
        if s.estimated_minutes > 10:
            half = s.estimated_minutes // 2
            s1 = SubTask(
                title=f"Start: {s.title} (first half)",
                estimated_minutes=half,
                energy_required=s.energy_required,
                order=order,
                parent_task_id=s.parent_task_id,
                completion_criteria=s.completion_criteria,
                reward=_pick_reward(order),
            )
            result.append(s1)
            order += 1
            s2 = SubTask(
                title=f"Continue: {s.title} (second half)",
                estimated_minutes=s.estimated_minutes - half,
                energy_required=s.energy_required,
                order=order,
                parent_task_id=s.parent_task_id,
                completion_criteria=s.completion_criteria,
                reward=_pick_reward(order),
            )
            result.append(s2)
            order += 1
        else:
            s.order = order
            s.reward = _pick_reward(order)
            result.append(s)
            order += 1
    if result:
        result[0].is_first_step = True
    return result


def _apply_depression_style(steps: list[SubTask]) -> list[SubTask]:
    """Depression: start with the easiest step, build momentum (success spirals).

    Sorts by energy (low first) and adds encouragement rewards.
    """
    # Stable sort: within same energy, preserve original order
    energy_rank = {EnergyLevel.LOW: 0, EnergyLevel.MODERATE: 1, EnergyLevel.HIGH: 2}
    sorted_steps = sorted(steps, key=lambda s: energy_rank.get(s.energy_required, 1))

    for i, s in enumerate(sorted_steps):
        s.order = i + 1
        if i == 0:
            s.is_first_step = True
            s.reward = "You started — that is the hardest part. Be proud of yourself."
        elif i < len(sorted_steps) // 2:
            s.reward = "You are building momentum. Keep going, one step at a time."
        else:
            s.reward = _pick_reward(i)
    return sorted_steps


def _apply_anxiety_style(steps: list[SubTask]) -> list[SubTask]:
    """Anxiety: add preparation steps, clear expectations per step."""
    parent_id = steps[0].parent_task_id if steps else ""
    result: list[SubTask] = []
    order = 1

    # Add a preparation step at the beginning
    prep = SubTask(
        title="Take 3 slow breaths and remind yourself: you can do this one step at a time.",
        estimated_minutes=2,
        energy_required=EnergyLevel.LOW,
        order=order,
        parent_task_id=parent_id,
        completion_criteria="You have taken 3 slow breaths.",
        prep_note="This is a grounding step. There is no wrong way to do it.",
        is_first_step=True,
    )
    result.append(prep)
    order += 1

    for s in steps:
        s.order = order
        s.prep_note = s.prep_note or f"You only need to do this one step. It should take about {s.estimated_minutes} minutes."
        if not s.completion_criteria:
            s.completion_criteria = f"You have finished: {s.title.lower()}"
        s.reward = _pick_reward(order)
        result.append(s)
        order += 1

    return result


def _apply_ocd_style(steps: list[SubTask]) -> list[SubTask]:
    """OCD: structured steps with defined completion criteria."""
    for i, s in enumerate(steps):
        s.order = i + 1
        if not s.completion_criteria:
            s.completion_criteria = f"Step '{s.title}' is done. Move to the next step."
        s.prep_note = (
            f"Step {i + 1} of {len(steps)}. "
            f"Expected duration: {s.estimated_minutes} min. "
            "When the criteria is met, this step is complete."
        )
        s.reward = _pick_reward(i)
        if i == 0:
            s.is_first_step = True
    return steps


# ---------------------------------------------------------------------------
# Generic decomposition (no template match)
# ---------------------------------------------------------------------------

def _generic_decompose(title: str, task_id: str) -> list[SubTask]:
    """Generate generic micro-steps when no template matches."""
    return [
        SubTask(
            title=f"Decide specifically what '{title}' means right now",
            estimated_minutes=2, energy_required=EnergyLevel.LOW,
            order=1, parent_task_id=task_id,
        ),
        SubTask(
            title="Gather any materials, tools, or information you need",
            estimated_minutes=3, energy_required=EnergyLevel.LOW,
            order=2, parent_task_id=task_id,
        ),
        SubTask(
            title="Set up your workspace and remove distractions",
            estimated_minutes=2, energy_required=EnergyLevel.LOW,
            order=3, parent_task_id=task_id,
        ),
        SubTask(
            title=f"Do the first small piece of '{title}'",
            estimated_minutes=10, energy_required=EnergyLevel.MODERATE,
            order=4, parent_task_id=task_id,
        ),
        SubTask(
            title="Take a short break (2-3 minutes)",
            estimated_minutes=3, energy_required=EnergyLevel.LOW,
            order=5, parent_task_id=task_id,
        ),
        SubTask(
            title=f"Continue working on '{title}'",
            estimated_minutes=15, energy_required=EnergyLevel.HIGH,
            order=6, parent_task_id=task_id,
        ),
        SubTask(
            title="Review what you have done so far",
            estimated_minutes=3, energy_required=EnergyLevel.LOW,
            order=7, parent_task_id=task_id,
        ),
        SubTask(
            title="Finish up or plan the next session",
            estimated_minutes=5, energy_required=EnergyLevel.MODERATE,
            order=8, parent_task_id=task_id,
        ),
    ]


# ---------------------------------------------------------------------------
# Encouragement messages
# ---------------------------------------------------------------------------

_ENCOURAGEMENTS: dict[Condition, str] = {
    Condition.GENERAL: "You have a plan now. Take it one step at a time.",
    Condition.ADHD: (
        "Each step is small and concrete. If you lose focus, "
        "just come back to the current step — no need to remember the whole list."
    ),
    Condition.DEPRESSION: (
        "Starting is the bravest part. The steps are ordered so the easiest one "
        "comes first. You only need to do the next one."
    ),
    Condition.ANXIETY: (
        "Every step has clear expectations. You know exactly what to do and "
        "when it is done. There are no surprises."
    ),
    Condition.OCD: (
        "Each step has a defined completion point. Once the criteria is met, "
        "you can move forward with confidence."
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class SmartTaskDecomposer:
    """Decompose overwhelming tasks into manageable micro-steps.

    Parameters
    ----------
    conditions : list of str, optional
        User's conditions, e.g. ``["adhd", "depression"]``.
        The first listed condition drives the decomposition style.
    """

    def __init__(self, conditions: list[str] | None = None) -> None:
        self._conditions: list[Condition] = []
        for c in (conditions or []):
            cond = Condition.from_string(c)
            if cond != Condition.GENERAL or c.lower() == "general":
                self._conditions.append(cond)
        if not self._conditions:
            self._conditions = [Condition.GENERAL]

    @property
    def primary_condition(self) -> Condition:
        return self._conditions[0]

    def decompose(
        self,
        task_title: str,
        *,
        task_id: str | None = None,
        condition_override: str | None = None,
    ) -> DecompositionResult:
        """Break a task into micro-steps.

        Parameters
        ----------
        task_title : str
            The task to decompose.
        task_id : str, optional
            ID for the parent task. Generated if not provided.
        condition_override : str, optional
            Override the primary condition for this decomposition.
        """
        tid = task_id or uuid.uuid4().hex[:12]
        title = task_title.strip()
        if not title:
            return DecompositionResult(
                task_title=title,
                task_id=tid,
                complexity=TaskComplexity.TRIVIAL,
                condition=self.primary_condition,
                subtasks=[],
                total_estimated_minutes=0,
                encouragement="Please provide a task title.",
            )

        complexity = _estimate_complexity(title)

        # Determine condition
        if condition_override:
            condition = Condition.from_string(condition_override)
            if condition == Condition.GENERAL and condition_override.lower() != "general":
                condition = self.primary_condition
        else:
            condition = self.primary_condition

        # Build base steps from template or generic
        template_name = _find_template(title)
        if template_name and template_name in _TEMPLATES:
            raw_steps = _TEMPLATES[template_name]
            steps: list[SubTask] = []
            for i, (step_title, est_min, energy) in enumerate(raw_steps):
                steps.append(SubTask(
                    title=step_title,
                    estimated_minutes=est_min,
                    energy_required=energy,
                    order=i + 1,
                    parent_task_id=tid,
                ))
        else:
            steps = _generic_decompose(title, tid)

        # Trivial tasks don't need decomposition
        if complexity == TaskComplexity.TRIVIAL:
            steps = [SubTask(
                title=f"Do: {title}",
                estimated_minutes=5,
                energy_required=EnergyLevel.LOW,
                order=1,
                parent_task_id=tid,
                is_first_step=True,
                reward="Done! That was quick.",
            )]
        else:
            # Apply condition-specific modifications
            steps = self._apply_condition_style(steps, condition)

        # Add rewards where missing
        for i, s in enumerate(steps):
            if not s.reward:
                s.reward = _pick_reward(i)

        # Ensure first step is marked
        if steps and not any(s.is_first_step for s in steps):
            steps[0].is_first_step = True

        total_minutes = sum(s.estimated_minutes for s in steps)
        just_start = next((s for s in steps if s.is_first_step), steps[0] if steps else None)

        return DecompositionResult(
            task_title=title,
            task_id=tid,
            complexity=complexity,
            condition=condition,
            subtasks=steps,
            total_estimated_minutes=total_minutes,
            just_start_step=just_start,
            encouragement=_ENCOURAGEMENTS.get(condition, _ENCOURAGEMENTS[Condition.GENERAL]),
        )

    def just_start(
        self,
        task_title: str,
        *,
        task_id: str | None = None,
    ) -> SubTask | None:
        """Return only the very first tiny step to reduce overwhelm.

        This is the 'Just Start' mode: ignore the full plan and focus
        on the single smallest action.
        """
        result = self.decompose(task_title, task_id=task_id)
        return result.just_start_step

    def _apply_condition_style(
        self, steps: list[SubTask], condition: Condition,
    ) -> list[SubTask]:
        """Apply condition-specific modifications to the step list."""
        if condition == Condition.ADHD:
            return _apply_adhd_style(steps)
        if condition == Condition.DEPRESSION:
            return _apply_depression_style(steps)
        if condition == Condition.ANXIETY:
            return _apply_anxiety_style(steps)
        if condition == Condition.OCD:
            return _apply_ocd_style(steps)
        # GENERAL: just add rewards and mark first step
        for i, s in enumerate(steps):
            s.order = i + 1
            if i == 0:
                s.is_first_step = True
        return steps

    @staticmethod
    def available_templates() -> list[str]:
        """Return the names of all built-in task templates."""
        return sorted(_TEMPLATES.keys())

    @staticmethod
    def template_steps(template_name: str) -> list[dict[str, Any]] | None:
        """Return the raw steps for a named template, or None."""
        raw = _TEMPLATES.get(template_name)
        if raw is None:
            return None
        return [
            {"title": t, "estimated_minutes": m, "energy_required": e.value}
            for t, m, e in raw
        ]
