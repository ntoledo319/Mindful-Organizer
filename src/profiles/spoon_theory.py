"""
Spoon Theory energy budgeting system.

Implements the Spoon Theory model for chronic illness / mental health
energy management.  Provides daily allocation, real-time tracking,
spoon recovery, warnings, historical analysis, and condition-aware defaults.
"""

from __future__ import annotations

import contextlib
import uuid
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np

from core.constants import Condition

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ActivityType(Enum):
    """Built-in activity categories."""
    SELF_CARE = "self_care"
    SIMPLE_TASK = "simple_task"
    MODERATE_TASK = "moderate_task"
    COMPLEX_TASK = "complex_task"
    SOCIAL_INTERACTION = "social_interaction"
    EXERCISE = "exercise"
    ERRANDS = "errands"
    COOKING = "cooking"
    CLEANING = "cleaning"
    WORK_MEETING = "work_meeting"
    REST = "rest"
    MEDITATION = "meditation"
    NATURE = "nature"
    NAP = "nap"
    LIGHT_HOBBY = "light_hobby"


class WarningLevel(Enum):
    """Spoon warning severity."""
    OK = "ok"
    CAUTION = "caution"        # <= 3 spoons remaining
    LOW = "low"                # <= 1 spoon remaining
    OVERDRAFT = "overdraft"    # negative spoons (spoon debt)


# ---------------------------------------------------------------------------
# Data-classes
# ---------------------------------------------------------------------------

@dataclass
class SpoonCostEntry:
    """A record of spoons spent or recovered."""
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    activity: str = ""
    activity_type: ActivityType = ActivityType.SIMPLE_TASK
    spoon_cost: float = 0.0     # positive = spent, negative = recovered
    note: str = ""


@dataclass
class DailySpoonState:
    """Snapshot of a single day's spoon budget."""
    day: date
    total_spoons: float
    spent: float
    recovered: float
    remaining: float
    entries: list[SpoonCostEntry] = field(default_factory=list)
    warning: WarningLevel = WarningLevel.OK
    in_debt: bool = False
    debt_amount: float = 0.0

    @property
    def used_percentage(self) -> float:
        if self.total_spoons <= 0:
            return 100.0
        return round((self.spent / self.total_spoons) * 100, 1)


@dataclass
class WeeklySpoonSummary:
    """Summary of a full week's spoon usage."""
    start_date: date
    end_date: date
    daily_states: list[DailySpoonState]
    total_budget: float
    total_spent: float
    total_recovered: float
    avg_daily_spent: float
    most_expensive_activity: str | None = None
    debt_days: int = 0
    description: str = ""


@dataclass
class SpoonDisplay:
    """Data for rendering a visual spoon display."""
    total: float
    remaining: float
    spent: float
    recovered: float
    filled_spoons: int      # number of full spoon icons
    empty_spoons: int       # number of empty spoon icons
    partial_spoon: float    # 0.0-1.0 for a partially filled spoon
    warning: WarningLevel
    message: str


@dataclass
class RecoveryRecommendation:
    """A recommendation for recovering spoons."""
    activity: str
    activity_type: ActivityType
    estimated_recovery: float
    description: str


# ---------------------------------------------------------------------------
# Default spoon costs
# ---------------------------------------------------------------------------

_DEFAULT_COSTS: dict[ActivityType, float] = {
    ActivityType.SELF_CARE: 1.0,
    ActivityType.SIMPLE_TASK: 1.0,
    ActivityType.MODERATE_TASK: 2.0,
    ActivityType.COMPLEX_TASK: 3.0,
    ActivityType.SOCIAL_INTERACTION: 2.0,
    ActivityType.EXERCISE: 2.0,
    ActivityType.ERRANDS: 2.5,
    ActivityType.COOKING: 2.0,
    ActivityType.CLEANING: 2.0,
    ActivityType.WORK_MEETING: 2.0,
    ActivityType.LIGHT_HOBBY: 1.0,
    # Recovery activities (negative = restore spoons)
    ActivityType.REST: -1.0,
    ActivityType.MEDITATION: -0.5,
    ActivityType.NATURE: -0.75,
    ActivityType.NAP: -1.5,
}

_DEFAULT_DAILY_SPOONS = 12.0

# Condition-specific adjustments
_CONDITION_SPOON_ADJUSTMENTS: dict[Condition, dict[str, Any]] = {
    Condition.DEPRESSION: {
        "daily_spoons": 8.0,
        "cost_overrides": {
            ActivityType.SELF_CARE: 1.5,
            ActivityType.SOCIAL_INTERACTION: 3.0,
            ActivityType.EXERCISE: 2.5,
        },
    },
    Condition.ANXIETY: {
        "daily_spoons": 10.0,
        "cost_overrides": {
            ActivityType.SOCIAL_INTERACTION: 3.0,
            ActivityType.WORK_MEETING: 3.0,
            ActivityType.ERRANDS: 3.0,
        },
    },
    Condition.ADHD: {
        "daily_spoons": 11.0,
        "cost_overrides": {
            ActivityType.COMPLEX_TASK: 3.5,
            ActivityType.MODERATE_TASK: 2.5,
            # Stimulating activities may cost less
            ActivityType.EXERCISE: 1.5,
        },
    },
    Condition.OCD: {
        "daily_spoons": 10.0,
        "cost_overrides": {
            ActivityType.CLEANING: 3.0,
            ActivityType.SELF_CARE: 2.0,
        },
    },
    Condition.PTSD: {
        "daily_spoons": 9.0,
        "cost_overrides": {
            ActivityType.SOCIAL_INTERACTION: 3.0,
            ActivityType.ERRANDS: 3.0,
        },
    },
    Condition.BIPOLAR: {
        "daily_spoons": 10.0,
        "cost_overrides": {},
    },
    Condition.CHRONIC_FATIGUE: {
        "daily_spoons": 6.0,
        "cost_overrides": {
            ActivityType.EXERCISE: 3.0,
            ActivityType.ERRANDS: 3.5,
            ActivityType.COOKING: 2.5,
            ActivityType.CLEANING: 3.0,
        },
    },
    Condition.GENERAL: {
        "daily_spoons": _DEFAULT_DAILY_SPOONS,
        "cost_overrides": {},
    },
}


# ---------------------------------------------------------------------------
# Main system
# ---------------------------------------------------------------------------

class SpoonBudget:
    """Spoon Theory energy budgeting system.

    Parameters
    ----------
    daily_spoons : float, optional
        Override default daily spoon allocation.
    conditions : list of str, optional
        User's conditions, e.g. ``["depression", "anxiety"]``.
    custom_costs : dict, optional
        Custom spoon costs keyed by ``ActivityType`` or activity name string.
    """

    def __init__(
        self,
        daily_spoons: float | None = None,
        conditions: list[str] | None = None,
        custom_costs: dict[str, float] | None = None,
    ) -> None:
        # Resolve conditions
        self._conditions: list[Condition] = []
        for c in (conditions or []):
            matched: Condition | None = None
            for cond in Condition:
                if cond.name.lower() == c.lower() or cond.value.lower() == c.lower():
                    matched = cond
                    break
            if matched is not None:
                self._conditions.append(matched)
        if not self._conditions:
            self._conditions = [Condition.GENERAL]

        # Build effective costs
        self._costs: dict[ActivityType, float] = dict(_DEFAULT_COSTS)
        # Apply condition overrides (first condition is primary)
        primary = self._conditions[0]
        adjustments = _CONDITION_SPOON_ADJUSTMENTS.get(primary, {})
        for atype, cost in adjustments.get("cost_overrides", {}).items():
            self._costs[atype] = cost

        # Apply user custom costs
        if custom_costs:
            for key, val in custom_costs.items():
                if isinstance(key, ActivityType):
                    self._costs[key] = val
                else:
                    with contextlib.suppress(ValueError):
                        self._costs[ActivityType(key)] = val

        # Daily spoon allocation
        if daily_spoons is not None:
            self._daily_spoons = daily_spoons
        else:
            self._daily_spoons = adjustments.get("daily_spoons", _DEFAULT_DAILY_SPOONS)

        # Daily tracking: date -> list of entries
        self._history: dict[date, list[SpoonCostEntry]] = defaultdict(list)

    # -- configuration --------------------------------------------------------

    @property
    def daily_spoons(self) -> float:
        return self._daily_spoons

    @daily_spoons.setter
    def daily_spoons(self, value: float) -> None:
        self._daily_spoons = max(1.0, value)

    def set_custom_cost(self, activity_type: ActivityType, cost: float) -> None:
        """Override the spoon cost for a specific activity type."""
        self._costs[activity_type] = cost

    def get_cost(self, activity_type: ActivityType) -> float:
        """Return the current spoon cost for an activity type."""
        return self._costs.get(activity_type, 1.0)

    # -- spending & recovery ---------------------------------------------------

    def spend(
        self,
        activity_type: ActivityType,
        *,
        activity_name: str = "",
        note: str = "",
        when: datetime | None = None,
        cost_override: float | None = None,
    ) -> SpoonCostEntry:
        """Record spoons spent on an activity.

        Returns the created entry.
        """
        ts = when or datetime.now()
        cost = cost_override if cost_override is not None else abs(self._costs.get(activity_type, 1.0))
        entry = SpoonCostEntry(
            timestamp=ts,
            activity=activity_name or activity_type.value,
            activity_type=activity_type,
            spoon_cost=cost,
            note=note,
        )
        self._history[ts.date()].append(entry)
        return entry

    def recover(
        self,
        activity_type: ActivityType,
        *,
        activity_name: str = "",
        note: str = "",
        when: datetime | None = None,
        recovery_override: float | None = None,
    ) -> SpoonCostEntry:
        """Record spoon recovery from a restorative activity.

        Returns the created entry.
        """
        ts = when or datetime.now()
        base_cost = self._costs.get(activity_type, -0.5)
        recovery = recovery_override if recovery_override is not None else abs(base_cost)
        entry = SpoonCostEntry(
            timestamp=ts,
            activity=activity_name or activity_type.value,
            activity_type=activity_type,
            spoon_cost=-recovery,  # negative = recovery
            note=note,
        )
        self._history[ts.date()].append(entry)
        return entry

    # -- querying today -------------------------------------------------------

    def today_state(self, for_date: date | None = None) -> DailySpoonState:
        """Get the current spoon state for a given day (default: today)."""
        day = for_date or date.today()
        entries = self._history.get(day, [])
        return self._build_daily_state(day, entries)

    def remaining_spoons(self, for_date: date | None = None) -> float:
        """Shorthand for today's remaining spoons."""
        return self.today_state(for_date).remaining

    def warning_level(self, for_date: date | None = None) -> WarningLevel:
        """Get the current warning level."""
        return self.today_state(for_date).warning

    def can_afford(self, activity_type: ActivityType, for_date: date | None = None) -> bool:
        """Check whether you can afford an activity without going into debt."""
        remaining = self.remaining_spoons(for_date)
        cost = abs(self._costs.get(activity_type, 1.0))
        return remaining >= cost

    # -- visual display -------------------------------------------------------

    def display(self, for_date: date | None = None) -> SpoonDisplay:
        """Generate data for a visual spoon display."""
        state = self.today_state(for_date)
        remaining_clamped = max(0.0, state.remaining)
        filled = int(remaining_clamped)
        partial = remaining_clamped - filled
        empty = max(0, int(state.total_spoons) - filled - (1 if partial > 0 else 0))

        if state.warning == WarningLevel.OVERDRAFT:
            message = (
                f"You are in spoon debt ({abs(state.remaining):.1f} spoons over budget). "
                "Please rest and recover."
            )
        elif state.warning == WarningLevel.LOW:
            message = "You are running very low on spoons. Consider only essential activities."
        elif state.warning == WarningLevel.CAUTION:
            message = f"Caution: only {state.remaining:.1f} spoons remaining. Plan carefully."
        else:
            message = f"You have {state.remaining:.1f} of {state.total_spoons:.0f} spoons remaining."

        return SpoonDisplay(
            total=state.total_spoons,
            remaining=state.remaining,
            spent=state.spent,
            recovered=state.recovered,
            filled_spoons=filled,
            empty_spoons=empty,
            partial_spoon=round(partial, 2),
            warning=state.warning,
            message=message,
        )

    # -- recovery recommendations ----------------------------------------------

    def recovery_recommendations(self) -> list[RecoveryRecommendation]:
        """Suggest restorative activities to recover spoons."""
        recs: list[RecoveryRecommendation] = []
        recovery_activities = [
            (ActivityType.NAP, "Take a 20-minute nap to recharge."),
            (ActivityType.REST, "Lie down or sit quietly for 15-30 minutes."),
            (ActivityType.NATURE, "Spend time outdoors — even 10 minutes helps."),
            (ActivityType.MEDITATION, "Do a 5-10 minute guided meditation."),
        ]
        for atype, desc in recovery_activities:
            recovery_amount = abs(self._costs.get(atype, 0.5))
            recs.append(RecoveryRecommendation(
                activity=atype.value,
                activity_type=atype,
                estimated_recovery=recovery_amount,
                description=desc,
            ))
        return recs

    # -- debt tracking ---------------------------------------------------------

    def spoon_debt(self, for_date: date | None = None) -> tuple[bool, float, str]:
        """Check if the user is in spoon debt.

        Returns (is_in_debt, debt_amount, recommendation).
        """
        state = self.today_state(for_date)
        if state.remaining >= 0:
            return False, 0.0, "You are within your spoon budget."

        debt = abs(state.remaining)
        if debt <= 1.0:
            rec = "You are slightly over budget. A short rest should help you recover."
        elif debt <= 3.0:
            rec = (
                "You have spent significantly more than your budget. "
                "Cancel non-essential plans and prioritise rest."
            )
        else:
            rec = (
                "You are in significant spoon debt. "
                "Tomorrow may be harder as a result. "
                "Please rest as much as possible and consider asking for help."
            )
        return True, round(debt, 1), rec

    # -- history & analytics ---------------------------------------------------

    def add_historical_day(
        self,
        day: date,
        entries: Sequence[dict[str, Any]],
    ) -> None:
        """Load historical data for analytics.

        Each dict should have: activity_type, spoon_cost (positive=spent,
        negative=recovered), and optionally activity, note, timestamp.
        """
        for d in entries:
            atype_raw = d.get("activity_type", "simple_task")
            try:
                atype = ActivityType(atype_raw)
            except ValueError:
                atype = ActivityType.SIMPLE_TASK

            ts_raw = d.get("timestamp")
            if isinstance(ts_raw, str):
                ts = datetime.fromisoformat(ts_raw)
            elif isinstance(ts_raw, datetime):
                ts = ts_raw
            else:
                ts = datetime.combine(day, datetime.min.time())

            entry = SpoonCostEntry(
                timestamp=ts,
                activity=d.get("activity", atype.value),
                activity_type=atype,
                spoon_cost=float(d.get("spoon_cost", 1.0)),
                note=d.get("note", ""),
            )
            self._history[day].append(entry)

    def weekly_summary(self, end_date: date | None = None) -> WeeklySpoonSummary:
        """Generate a summary for the 7-day window ending on *end_date*."""
        end = end_date or date.today()
        start = end - timedelta(days=6)
        daily_states: list[DailySpoonState] = []

        for i in range(7):
            day = start + timedelta(days=i)
            entries = self._history.get(day, [])
            daily_states.append(self._build_daily_state(day, entries))

        total_budget = sum(s.total_spoons for s in daily_states)
        total_spent = sum(s.spent for s in daily_states)
        total_recovered = sum(s.recovered for s in daily_states)
        debt_days = sum(1 for s in daily_states if s.in_debt)

        # Most expensive activity across the week
        activity_totals: dict[str, float] = defaultdict(float)
        for s in daily_states:
            for e in s.entries:
                if e.spoon_cost > 0:
                    activity_totals[e.activity] += e.spoon_cost

        most_expensive = max(activity_totals, key=activity_totals.get) if activity_totals else None  # type: ignore[arg-type]

        avg_daily = total_spent / max(len(daily_states), 1)

        desc_parts = [
            f"This week you spent {total_spent:.1f} of {total_budget:.0f} available spoons.",
        ]
        if total_recovered > 0:
            desc_parts.append(f"You recovered {total_recovered:.1f} spoons through restorative activities.")
        if debt_days > 0:
            desc_parts.append(f"You went into spoon debt on {debt_days} day(s).")
        if most_expensive:
            desc_parts.append(f"Your most costly activity was '{most_expensive}'.")

        return WeeklySpoonSummary(
            start_date=start,
            end_date=end,
            daily_states=daily_states,
            total_budget=total_budget,
            total_spent=round(total_spent, 1),
            total_recovered=round(total_recovered, 1),
            avg_daily_spent=round(avg_daily, 1),
            most_expensive_activity=most_expensive,
            debt_days=debt_days,
            description=" ".join(desc_parts),
        )

    def historical_average_daily_usage(self) -> float:
        """Average spoons spent per day across all tracked days."""
        if not self._history:
            return 0.0
        daily_totals = []
        for _day, entries in self._history.items():
            spent = sum(e.spoon_cost for e in entries if e.spoon_cost > 0)
            daily_totals.append(spent)
        return round(float(np.mean(daily_totals)), 1) if daily_totals else 0.0

    def most_expensive_activities(self, top_n: int = 5) -> list[tuple[str, float]]:
        """Return the top-N most costly activities across all history."""
        totals: dict[str, float] = defaultdict(float)
        for entries in self._history.values():
            for e in entries:
                if e.spoon_cost > 0:
                    totals[e.activity] += e.spoon_cost
        ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
        return ranked[:top_n]

    # -- internal helpers ------------------------------------------------------

    def _build_daily_state(
        self, day: date, entries: list[SpoonCostEntry],
    ) -> DailySpoonState:
        spent = sum(e.spoon_cost for e in entries if e.spoon_cost > 0)
        recovered = sum(abs(e.spoon_cost) for e in entries if e.spoon_cost < 0)
        remaining = self._daily_spoons - spent + recovered

        if remaining < 0:
            warning = WarningLevel.OVERDRAFT
        elif remaining <= 1.0:
            warning = WarningLevel.LOW
        elif remaining <= 3.0:
            warning = WarningLevel.CAUTION
        else:
            warning = WarningLevel.OK

        return DailySpoonState(
            day=day,
            total_spoons=self._daily_spoons,
            spent=round(spent, 1),
            recovered=round(recovered, 1),
            remaining=round(remaining, 1),
            entries=entries,
            warning=warning,
            in_debt=remaining < 0,
            debt_amount=round(abs(remaining), 1) if remaining < 0 else 0.0,
        )
