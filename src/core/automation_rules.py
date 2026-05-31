"""
Automation rule definitions for the System Automation Engine.

Maps psychological states and conditions to concrete system actions.
Rules are evidence-informed heuristics, not medical advice.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from core.constants import Condition


class ActionType(Enum):
    """Categories of system actions the automation engine can perform."""

    ENABLE_FOCUS_MODE = auto()
    DISABLE_FOCUS_MODE = auto()
    CLOSE_APPLICATION = auto()
    HIDE_APPLICATION = auto()
    LAUNCH_APPLICATION = auto()
    SET_DND = auto()
    UNSET_DND = auto()
    SET_DISPLAY_BRIGHTNESS = auto()
    SET_NIGHT_SHIFT = auto()
    SET_SYSTEM_THEME = auto()
    MINIMIZE_ALL_WINDOWS = auto()
    RESTORE_WINDOWS = auto()
    PLAY_SOUND = auto()
    SHOW_OVERLAY = auto()
    LOG_STATE = auto()


class TriggerType(Enum):
    """What causes a rule to fire."""

    ENERGY_LOW = auto()  # energy <= 3
    ENERGY_VERY_LOW = auto()  # energy <= 2
    ENERGY_HIGH = auto()  # energy >= 7
    ENERGY_PEAK = auto()  # energy >= 8
    MOOD_LOW = auto()  # mood <= 3
    MOOD_VERY_LOW = auto()  # mood <= 2
    ANXIETY_SPIKE = auto()  # anxiety detected / panic flagged
    ADHD_SLUMP = auto()  # 3-3:30 PM + ADHD profile
    BURNOUT_RISK = auto()  # burnout risk >= moderate
    HYPOMANIA_SIGNS = auto()  # hypomania pattern detected
    MANUAL_FOCUS = auto()  # user pressed focus hotkey
    MANUAL_CRISIS = auto()  # user pressed crisis hotkey
    MANUAL_GROUNDING = auto()  # user pressed grounding hotkey
    SCHEDULED_FOCUS = auto()  # scheduled focus block
    SLEEP_DEBT = auto()  # < 5 hours sleep


@dataclass(frozen=True)
class AutomationAction:
    """A single concrete action the engine can execute."""

    action_type: ActionType
    target: str | None = None  # app name, brightness value, etc.
    payload: dict = field(default_factory=dict)
    reason: str = ""


@dataclass
class AutomationRule:
    """A rule: when TRIGGER and CONDITIONS match, execute ACTIONS."""

    name: str
    trigger: TriggerType
    required_conditions: set[Condition] = field(default_factory=set)
    actions: list[AutomationAction] = field(default_factory=list)
    cooldown_minutes: int = 30  # prevent spam
    enabled_by_default: bool = True


# ---------------------------------------------------------------------------
# Default rule set — evidence-informed, not medical advice
# ---------------------------------------------------------------------------

_DEFAULT_RULES: list[AutomationRule] = [
    # --- Energy-based rules -------------------------------------------------
    AutomationRule(
        name="low_energy_simplify",
        trigger=TriggerType.ENERGY_LOW,
        actions=[
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Discord",
                reason="Low energy — reducing stimulation",
            ),
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Slack",
                reason="Low energy — reducing stimulation",
            ),
            AutomationAction(
                ActionType.HIDE_APPLICATION,
                target="Mail",
                reason="Low energy — hiding distractions",
            ),
            AutomationAction(
                ActionType.SET_DISPLAY_BRIGHTNESS,
                target="40",
                reason="Low energy — dimming display",
            ),
            AutomationAction(
                ActionType.SET_NIGHT_SHIFT,
                target="75",
                payload={"enabled": True},
                reason="Low energy — warmer display reduces eye strain",
            ),
        ],
        cooldown_minutes=60,
    ),
    AutomationRule(
        name="very_low_energy_minimal",
        trigger=TriggerType.ENERGY_VERY_LOW,
        actions=[
            AutomationAction(
                ActionType.MINIMIZE_ALL_WINDOWS,
                reason="Very low energy — clearing workspace",
            ),
            AutomationAction(
                ActionType.SET_DISPLAY_BRIGHTNESS,
                target="25",
                reason="Very low energy — minimal brightness",
            ),
            AutomationAction(
                ActionType.SET_SYSTEM_THEME,
                target="dark",
                reason="Very low energy — dark mode reduces visual load",
            ),
            AutomationAction(
                ActionType.SHOW_OVERLAY,
                target="gentle_reminder",
                payload={"message": "Your energy is very low. One tiny task is enough."},
                reason="Gentle nudge for self-compassion",
            ),
        ],
        cooldown_minutes=120,
    ),
    AutomationRule(
        name="peak_energy_protect",
        trigger=TriggerType.ENERGY_PEAK,
        actions=[
            AutomationAction(
                ActionType.SET_DND,
                reason="Peak energy — protecting deep work window",
            ),
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Messages",
                reason="Peak energy — removing interruptions",
            ),
            AutomationAction(
                ActionType.SET_DISPLAY_BRIGHTNESS,
                target="80",
                reason="Peak energy — bright, alert display",
            ),
        ],
        cooldown_minutes=180,
    ),
    # --- Condition-specific rules -------------------------------------------
    AutomationRule(
        name="adhd_afternoon_transition",
        trigger=TriggerType.ADHD_SLUMP,
        required_conditions={Condition.ADHD},
        actions=[
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Twitter",
                reason="ADHD afternoon slump — removing dopamine traps",
            ),
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Reddit",
                reason="ADHD afternoon slump — removing dopamine traps",
            ),
            AutomationAction(
                ActionType.SHOW_OVERLAY,
                target="focus_prompt",
                payload={
                    "message": "Afternoon transition detected. 5-min movement break, then one task."
                },
                reason="ADHD-specific transition support",
            ),
        ],
        cooldown_minutes=240,  # once per afternoon
    ),
    AutomationRule(
        name="anxiety_calm_environment",
        trigger=TriggerType.ANXIETY_SPIKE,
        required_conditions={Condition.ANXIETY, Condition.PANIC, Condition.PTSD},
        actions=[
            AutomationAction(
                ActionType.SET_DISPLAY_BRIGHTNESS,
                target="35",
                reason="Anxiety spike — dimming for calm",
            ),
            AutomationAction(
                ActionType.SET_NIGHT_SHIFT,
                target="90",
                payload={"enabled": True},
                reason="Anxiety spike — warmest display setting",
            ),
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Mail",
                reason="Anxiety spike — removing demand sources",
            ),
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Calendar",
                reason="Anxiety spike — removing demand sources",
            ),
            AutomationAction(
                ActionType.SET_SYSTEM_THEME,
                target="dark",
                reason="Anxiety spike — dark mode reduces visual overwhelm",
            ),
        ],
        cooldown_minutes=60,
    ),
    AutomationRule(
        name="burnout_protection",
        trigger=TriggerType.BURNOUT_RISK,
        actions=[
            AutomationAction(
                ActionType.MINIMIZE_ALL_WINDOWS,
                reason="Burnout risk detected — workspace reset",
            ),
            AutomationAction(
                ActionType.SET_DISPLAY_BRIGHTNESS,
                target="30",
                reason="Burnout risk — reducing sensory input",
            ),
            AutomationAction(
                ActionType.SHOW_OVERLAY,
                target="burnout_warning",
                payload={"message": "Burnout risk detected. Consider ending work early today."},
                reason="Burnout prevention alert",
            ),
        ],
        cooldown_minutes=360,  # once per 6 hours
    ),
    AutomationRule(
        name="hypomania_pacing",
        trigger=TriggerType.HYPOMANIA_SIGNS,
        required_conditions={Condition.BIPOLAR},
        actions=[
            AutomationAction(
                ActionType.SHOW_OVERLAY,
                target="pacing_reminder",
                payload={
                    "message": "High activity pattern detected. Remember: rest is productive too."
                },
                reason="Bipolar pacing support",
            ),
            AutomationAction(
                ActionType.SET_DND,
                reason="Hypomania signs — reducing stimulation triggers",
            ),
        ],
        cooldown_minutes=240,
    ),
    AutomationRule(
        name="sleep_debt_gentle",
        trigger=TriggerType.SLEEP_DEBT,
        actions=[
            AutomationAction(
                ActionType.SET_DISPLAY_BRIGHTNESS,
                target="30",
                reason="Sleep debt — dimming to reduce wakefulness",
            ),
            AutomationAction(
                ActionType.SET_NIGHT_SHIFT,
                target="100",
                payload={"enabled": True},
                reason="Sleep debt — maximum warmth",
            ),
            AutomationAction(
                ActionType.SHOW_OVERLAY,
                target="sleep_reminder",
                payload={"message": "Low sleep detected. Prioritise rest over productivity today."},
                reason="Sleep hygiene support",
            ),
        ],
        cooldown_minutes=360,
    ),
    # --- Manual triggers ----------------------------------------------------
    AutomationRule(
        name="manual_focus_deep_work",
        trigger=TriggerType.MANUAL_FOCUS,
        actions=[
            AutomationAction(
                ActionType.ENABLE_FOCUS_MODE,
                reason="User activated focus mode",
            ),
            AutomationAction(
                ActionType.SET_DND,
                reason="Focus mode — Do Not Disturb enabled",
            ),
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Discord",
                reason="Focus mode — closing distractions",
            ),
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Slack",
                reason="Focus mode — closing distractions",
            ),
            AutomationAction(
                ActionType.CLOSE_APPLICATION,
                target="Twitter",
                reason="Focus mode — closing distractions",
            ),
            AutomationAction(
                ActionType.MINIMIZE_ALL_WINDOWS,
                reason="Focus mode — clean slate",
            ),
            AutomationAction(
                ActionType.SET_DISPLAY_BRIGHTNESS,
                target="70",
                reason="Focus mode — bright, alert display",
            ),
        ],
        cooldown_minutes=0,  # manual — no cooldown
    ),
    AutomationRule(
        name="manual_crisis_safety",
        trigger=TriggerType.MANUAL_CRISIS,
        actions=[
            AutomationAction(
                ActionType.MINIMIZE_ALL_WINDOWS,
                reason="Crisis mode — clearing workspace",
            ),
            AutomationAction(
                ActionType.SET_DISPLAY_BRIGHTNESS,
                target="20",
                reason="Crisis mode — minimal stimulation",
            ),
            AutomationAction(
                ActionType.SET_NIGHT_SHIFT,
                target="100",
                payload={"enabled": True},
                reason="Crisis mode — warmest display",
            ),
            AutomationAction(
                ActionType.SET_SYSTEM_THEME,
                target="dark",
                reason="Crisis mode — dark mode",
            ),
            AutomationAction(
                ActionType.LAUNCH_APPLICATION,
                target="Mindful Organizer",
                payload={"tab": "crisis"},
                reason="Crisis mode — opening crisis plan",
            ),
            AutomationAction(
                ActionType.PLAY_SOUND,
                target="gentle_chime",
                reason="Crisis mode — grounding audio cue",
            ),
        ],
        cooldown_minutes=0,
    ),
    AutomationRule(
        name="manual_grounding_reset",
        trigger=TriggerType.MANUAL_GROUNDING,
        actions=[
            AutomationAction(
                ActionType.MINIMIZE_ALL_WINDOWS,
                reason="Grounding — clearing visual field",
            ),
            AutomationAction(
                ActionType.SET_DISPLAY_BRIGHTNESS,
                target="30",
                reason="Grounding — dim display",
            ),
            AutomationAction(
                ActionType.LAUNCH_APPLICATION,
                target="Mindful Organizer",
                payload={"tab": "breathing"},
                reason="Grounding — opening breathing exercise",
            ),
        ],
        cooldown_minutes=0,
    ),
]


def get_default_rules() -> list[AutomationRule]:
    """Return a deep copy of the default rule set."""
    import copy

    return copy.deepcopy(_DEFAULT_RULES)


def rules_for_trigger(
    rules: list[AutomationRule],
    trigger: TriggerType,
    user_conditions: set[Condition],
) -> list[AutomationRule]:
    """Filter rules that match a trigger and the user's conditions."""
    matched: list[AutomationRule] = []
    for rule in rules:
        if rule.trigger != trigger:
            continue
        if rule.required_conditions and not rule.required_conditions.intersection(user_conditions):
            continue
        matched.append(rule)
    return matched
