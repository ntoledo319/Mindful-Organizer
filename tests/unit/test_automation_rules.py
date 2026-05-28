"""Tests for the automation rule system."""
from __future__ import annotations

from core.automation_rules import (
    ActionType,
    AutomationAction,
    AutomationRule,
    TriggerType,
    get_default_rules,
    rules_for_trigger,
)
from core.constants import Condition


class TestRuleMatching:
    """Test trigger + condition matching logic."""

    def test_rules_for_trigger_exact_match(self):
        rules = [
            AutomationRule("r1", TriggerType.ENERGY_LOW),
            AutomationRule("r2", TriggerType.ENERGY_HIGH),
        ]
        matched = rules_for_trigger(rules, TriggerType.ENERGY_LOW, set())
        assert len(matched) == 1
        assert matched[0].name == "r1"

    def test_rules_for_trigger_with_required_conditions(self):
        rules = [
            AutomationRule(
                "adhd_rule",
                TriggerType.ADHD_SLUMP,
                required_conditions={Condition.ADHD},
            ),
            AutomationRule(
                "generic_rule",
                TriggerType.ENERGY_LOW,
            ),
        ]
        # No ADHD in user conditions
        matched = rules_for_trigger(rules, TriggerType.ADHD_SLUMP, set())
        assert len(matched) == 0

        # ADHD in user conditions
        matched = rules_for_trigger(rules, TriggerType.ADHD_SLUMP, {Condition.ADHD})
        assert len(matched) == 1
        assert matched[0].name == "adhd_rule"

    def test_rule_with_multiple_conditions_matches_any(self):
        rule = AutomationRule(
            "anxiety_rule",
            TriggerType.ANXIETY_SPIKE,
            required_conditions={Condition.ANXIETY, Condition.PANIC},
        )
        matched = rules_for_trigger([rule], TriggerType.ANXIETY_SPIKE, {Condition.PANIC})
        assert len(matched) == 1


class TestDefaultRules:
    """Test the built-in default rule set."""

    def test_default_rules_not_empty(self):
        rules = get_default_rules()
        assert len(rules) > 0

    def test_default_rules_have_actions(self):
        rules = get_default_rules()
        for rule in rules:
            assert len(rule.actions) > 0, f"Rule {rule.name} has no actions"

    def test_manual_focus_rule_has_close_actions(self):
        rules = get_default_rules()
        focus_rule = next((r for r in rules if r.trigger == TriggerType.MANUAL_FOCUS), None)
        assert focus_rule is not None
        close_actions = [a for a in focus_rule.actions if a.action_type == ActionType.CLOSE_APPLICATION]
        assert len(close_actions) >= 3

    def test_crisis_rule_minimizes_windows(self):
        rules = get_default_rules()
        crisis_rule = next((r for r in rules if r.trigger == TriggerType.MANUAL_CRISIS), None)
        assert crisis_rule is not None
        minimize_actions = [a for a in crisis_rule.actions if a.action_type == ActionType.MINIMIZE_ALL_WINDOWS]
        assert len(minimize_actions) == 1

    def test_cooldown_prevents_spam(self):
        rules = get_default_rules()
        burnout_rule = next((r for r in rules if r.trigger == TriggerType.BURNOUT_RISK), None)
        assert burnout_rule is not None
        assert burnout_rule.cooldown_minutes >= 60


class TestAutomationAction:
    """Test AutomationAction data class."""

    def test_action_creation(self):
        action = AutomationAction(
            action_type=ActionType.SET_DISPLAY_BRIGHTNESS,
            target="50",
            reason="Test reason",
        )
        assert action.action_type == ActionType.SET_DISPLAY_BRIGHTNESS
        assert action.target == "50"
        assert action.reason == "Test reason"

    def test_action_with_payload(self):
        action = AutomationAction(
            action_type=ActionType.SHOW_OVERLAY,
            target="test_overlay",
            payload={"message": "Hello"},
        )
        assert action.payload["message"] == "Hello"
