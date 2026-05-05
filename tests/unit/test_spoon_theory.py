"""
Tests for SpoonBudget (src/profile/spoon_theory.py).

Covers daily allocation, spending spoons, recovery, spoon debt,
and condition-specific defaults.
"""

from datetime import date, timedelta

import pytest

try:
    from src.profiles.spoon_theory import (
        ActivityType,
        SpoonBudget,
        SpoonCostEntry,
        WarningLevel,
    )
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="spoon_theory module not available")


# ---------------------------------------------------------------------------
# Daily allocation
# ---------------------------------------------------------------------------

class TestDailyAllocation:

    def test_default_daily_spoons(self):
        budget = SpoonBudget()
        assert budget.daily_spoons == 12.0

    def test_custom_daily_spoons(self):
        budget = SpoonBudget(daily_spoons=10.0)
        assert budget.daily_spoons == 10.0

    def test_condition_adjusts_daily_spoons(self):
        budget = SpoonBudget(conditions=["Depression"])
        assert budget.daily_spoons == 8.0

    def test_remaining_spoons_at_start(self):
        budget = SpoonBudget(daily_spoons=12.0)
        assert budget.remaining_spoons() == 12.0

    def test_set_daily_spoons(self):
        budget = SpoonBudget()
        budget.daily_spoons = 15.0
        assert budget.daily_spoons == 15.0

    def test_daily_spoons_min_clamp(self):
        budget = SpoonBudget()
        budget.daily_spoons = -5.0
        assert budget.daily_spoons == 1.0


# ---------------------------------------------------------------------------
# Spend spoons
# ---------------------------------------------------------------------------

class TestSpendSpoons:

    def test_spend_reduces_remaining(self):
        budget = SpoonBudget(daily_spoons=12.0)
        budget.spend(ActivityType.SIMPLE_TASK, activity_name="Reply to email")

        remaining = budget.remaining_spoons()
        assert remaining < 12.0

    def test_spend_multiple_activities(self):
        budget = SpoonBudget(daily_spoons=12.0)
        budget.spend(ActivityType.SIMPLE_TASK)
        budget.spend(ActivityType.MODERATE_TASK)
        budget.spend(ActivityType.COMPLEX_TASK)

        state = budget.today_state()
        assert state.spent > 0
        assert state.remaining < 12.0

    def test_spend_with_cost_override(self):
        budget = SpoonBudget(daily_spoons=12.0)
        budget.spend(ActivityType.SIMPLE_TASK, cost_override=5.0)

        assert budget.remaining_spoons() == 7.0

    def test_spend_returns_entry(self):
        budget = SpoonBudget()
        entry = budget.spend(ActivityType.EXERCISE, activity_name="Morning jog")

        assert isinstance(entry, SpoonCostEntry)
        assert entry.spoon_cost > 0
        assert entry.activity == "Morning jog"

    def test_can_afford_check(self):
        budget = SpoonBudget(daily_spoons=3.0)
        assert budget.can_afford(ActivityType.SIMPLE_TASK) is True
        assert budget.can_afford(ActivityType.COMPLEX_TASK) is True

        budget.spend(ActivityType.COMPLEX_TASK)  # costs 3
        assert budget.can_afford(ActivityType.SIMPLE_TASK) is False


# ---------------------------------------------------------------------------
# Recovery
# ---------------------------------------------------------------------------

class TestRecovery:

    def test_recovery_increases_remaining(self):
        budget = SpoonBudget(daily_spoons=12.0)
        budget.spend(ActivityType.COMPLEX_TASK)  # -3
        before = budget.remaining_spoons()

        budget.recover(ActivityType.NAP)
        after = budget.remaining_spoons()

        assert after > before

    def test_recovery_entry_negative_cost(self):
        budget = SpoonBudget()
        entry = budget.recover(ActivityType.REST)

        assert entry.spoon_cost < 0  # negative means recovery

    def test_recovery_override(self):
        budget = SpoonBudget(daily_spoons=10.0)
        budget.spend(ActivityType.COMPLEX_TASK, cost_override=5.0)
        budget.recover(ActivityType.REST, recovery_override=3.0)

        assert budget.remaining_spoons() == 8.0

    def test_recovery_recommendations(self):
        budget = SpoonBudget()
        recs = budget.recovery_recommendations()

        assert len(recs) >= 3
        assert all(r.estimated_recovery > 0 for r in recs)


# ---------------------------------------------------------------------------
# Spoon debt
# ---------------------------------------------------------------------------

class TestSpoonDebt:

    def test_overdraft_warning(self):
        budget = SpoonBudget(daily_spoons=5.0)
        budget.spend(ActivityType.COMPLEX_TASK, cost_override=6.0)

        state = budget.today_state()
        assert state.warning == WarningLevel.OVERDRAFT
        assert state.in_debt is True
        assert state.debt_amount > 0

    def test_spoon_debt_method(self):
        budget = SpoonBudget(daily_spoons=5.0)
        budget.spend(ActivityType.COMPLEX_TASK, cost_override=8.0)

        in_debt, amount, rec = budget.spoon_debt()
        assert in_debt is True
        assert amount == 3.0
        assert len(rec) > 0

    def test_no_debt(self):
        budget = SpoonBudget(daily_spoons=12.0)
        budget.spend(ActivityType.SIMPLE_TASK)

        in_debt, amount, rec = budget.spoon_debt()
        assert in_debt is False
        assert amount == 0.0

    def test_warning_levels(self):
        budget = SpoonBudget(daily_spoons=10.0)

        assert budget.warning_level() == WarningLevel.OK

        budget.spend(ActivityType.COMPLEX_TASK, cost_override=7.5)
        assert budget.warning_level() == WarningLevel.CAUTION

        budget.spend(ActivityType.SIMPLE_TASK, cost_override=1.5)
        assert budget.warning_level() == WarningLevel.LOW

        budget.spend(ActivityType.SIMPLE_TASK, cost_override=2.0)
        assert budget.warning_level() == WarningLevel.OVERDRAFT


# ---------------------------------------------------------------------------
# Condition defaults
# ---------------------------------------------------------------------------

class TestConditionDefaults:

    def test_depression_lower_spoons(self):
        budget = SpoonBudget(conditions=["depression"])
        assert budget.daily_spoons == 8.0

    def test_anxiety_adjusted_costs(self):
        budget = SpoonBudget(conditions=["anxiety"])
        # Social interaction costs more for anxiety
        assert budget.get_cost(ActivityType.SOCIAL_INTERACTION) == 3.0

    def test_adhd_adjusted_costs(self):
        budget = SpoonBudget(conditions=["adhd"])
        assert budget.daily_spoons == 11.0
        # Exercise is less costly for ADHD
        assert budget.get_cost(ActivityType.EXERCISE) == 1.5

    def test_chronic_fatigue(self):
        budget = SpoonBudget(conditions=["chronic_fatigue"])
        assert budget.daily_spoons == 6.0

    def test_unknown_condition_uses_general(self):
        budget = SpoonBudget(conditions=["nonexistent"])
        assert budget.daily_spoons == 12.0  # general default

    def test_custom_cost_override(self):
        budget = SpoonBudget()
        budget.set_custom_cost(ActivityType.COOKING, 5.0)
        assert budget.get_cost(ActivityType.COOKING) == 5.0


# ---------------------------------------------------------------------------
# Display and history
# ---------------------------------------------------------------------------

class TestDisplayAndHistory:

    def test_display_data(self):
        budget = SpoonBudget(daily_spoons=10.0)
        budget.spend(ActivityType.MODERATE_TASK)
        display = budget.display()

        assert display.total == 10.0
        assert display.spent > 0
        assert display.message

    def test_weekly_summary(self):
        budget = SpoonBudget(daily_spoons=10.0)
        today = date.today()

        for i in range(7):
            day = today - timedelta(days=6 - i)
            budget.add_historical_day(day, [
                {"activity_type": "simple_task", "spoon_cost": 2.0},
                {"activity_type": "moderate_task", "spoon_cost": 3.0},
            ])

        summary = budget.weekly_summary()
        assert summary.total_spent > 0
        assert len(summary.daily_states) == 7

    def test_historical_average(self):
        budget = SpoonBudget(daily_spoons=10.0)
        today = date.today()

        for i in range(3):
            day = today - timedelta(days=i)
            budget.add_historical_day(day, [
                {"activity_type": "simple_task", "spoon_cost": 4.0},
            ])

        avg = budget.historical_average_daily_usage()
        assert avg == 4.0

    def test_most_expensive_activities(self):
        budget = SpoonBudget()
        today = date.today()
        budget.add_historical_day(today, [
            {"activity_type": "complex_task", "spoon_cost": 3.0, "activity": "Big project"},
            {"activity_type": "simple_task", "spoon_cost": 1.0, "activity": "Email"},
            {"activity_type": "complex_task", "spoon_cost": 3.0, "activity": "Big project"},
        ])

        top = budget.most_expensive_activities(top_n=2)
        assert len(top) <= 2
        assert top[0][0] == "Big project"

    def test_today_state_specific_date(self):
        budget = SpoonBudget(daily_spoons=10.0)
        past = date.today() - timedelta(days=5)
        budget.add_historical_day(past, [
            {"activity_type": "exercise", "spoon_cost": 2.0},
        ])

        state = budget.today_state(for_date=past)
        assert state.spent == 2.0
        assert state.day == past
