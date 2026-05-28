"""Tests for tier-gated automation features."""
from __future__ import annotations

from datetime import time

from core.automation_analytics import AutomationAnalytics
from core.automation_config import AutomationConfigManager, ExecutionMode, ScheduledFocusBlock
from core.automation_rules import (
    ActionType,
    AutomationAction,
    AutomationRule,
    TriggerType,
)
from core.platform_actions import StubBackend
from core.subscription_manager import SubscriptionManager, SubscriptionTier
from core.system_automation import SystemAutomationEngine


class MockSubscriptionManager(SubscriptionManager):
    """Subscription manager with a fixed tier for testing."""

    def __init__(self, tier: SubscriptionTier = SubscriptionTier.PRO) -> None:
        self._tier = tier
        super().__init__()

    @property
    def current_tier(self) -> SubscriptionTier:
        return self._tier

    def has_feature(self, feature: str) -> bool:
        from core.subscription_manager import FEATURES_BY_TIER
        return feature in FEATURES_BY_TIER.get(self._tier, set())


# ---------------------------------------------------------------------------
# FREE tier
# ---------------------------------------------------------------------------

class TestFreeTier:
    """FREE tier: suggestions only, no system actions executed."""

    def test_free_tier_suggestions_only(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.FREE),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        results = engine.trigger(TriggerType.MANUAL_FOCUS)
        # Should suggest, not execute
        assert all(r["status"] == "suggested" for r in results)

    def test_free_tier_no_system_actions(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.FREE),
        )
        action = AutomationAction(ActionType.CLOSE_APPLICATION, target="Discord")
        result = engine._execute_action(action)
        assert result["status"] == "gated"
        assert "PRO" in result["detail"]

    def test_free_tier_no_analytics(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.FREE),
        )
        assert engine.get_analytics() is None

    def test_free_tier_execution_mode_forced_to_suggestions(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.FREE),
        )
        # Even if profile says AUTONOMOUS, FREE tier forces SUGGESTIONS_ONLY
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        assert engine._effective_execution_mode() == ExecutionMode.SUGGESTIONS_ONLY


# ---------------------------------------------------------------------------
# PRO tier
# ---------------------------------------------------------------------------

class TestProTier:
    """PRO tier: autonomous execution, system actions, no custom rules."""

    def test_pro_can_execute_system_actions(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PRO),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        action = AutomationAction(ActionType.LOG_STATE, reason="test")
        result = engine._execute_action(action)
        assert result["success"] is True

    def test_pro_autonomous_mode_executes_rules(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PRO),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        results = engine.trigger(TriggerType.MANUAL_FOCUS)
        assert any(r["status"] == "executed" for r in results)

    def test_pro_ask_first_returns_pending(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PRO),
        )
        engine.config.set_execution_mode("default", ExecutionMode.ASK_FIRST)
        results = engine.trigger(TriggerType.MANUAL_FOCUS)
        assert any(r["status"] == "pending_confirmation" for r in results)

    def test_pro_no_custom_rules(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PRO),
        )
        assert not engine._can_use_custom_rules
        # Custom rules should not be in effective rules
        rules = engine._effective_rules()
        assert not any(r.name == "My Custom Rule" for r in rules)

    def test_pro_no_analytics(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PRO),
        )
        assert engine.get_analytics() is None

    def test_pro_single_profile_only(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PRO),
        )
        profiles = engine.list_profiles()
        assert len(profiles) == 1


# ---------------------------------------------------------------------------
# PREMIUM tier
# ---------------------------------------------------------------------------

class TestPremiumTier:
    """PREMIUM tier: custom rules, analytics, profiles, scheduled blocks."""

    def test_premium_custom_rules_included(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PREMIUM),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        # Add a custom rule
        rule = AutomationRule(
            name="My Custom Rule",
            trigger=TriggerType.ENERGY_LOW,
            actions=[AutomationAction(ActionType.LOG_STATE, reason="custom")],
        )
        engine.config.add_custom_rule("default", rule)
        engine.config.active_profile.enabled_rules.append("My Custom Rule")

        rules = engine._effective_rules()
        assert any(r.name == "My Custom Rule" for r in rules)

    def test_premium_analytics_available(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PREMIUM),
        )
        analytics = engine.get_analytics()
        assert analytics is not None
        assert "overall" in analytics
        assert "focus_trends" in analytics

    def test_premium_multiple_profiles(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PREMIUM),
        )
        engine.config.create_profile("Work", "Workday automation")
        profiles = engine.list_profiles()
        assert len(profiles) >= 2

    def test_premium_profile_switching(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PREMIUM),
        )
        profile = engine.config.create_profile("Sleep", "Evening wind-down")
        assert engine.config.set_active_profile(profile.profile_id) is True
        assert engine.config.active_profile.name == "Sleep"

    def test_premium_scheduled_blocks_checked(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(SubscriptionTier.PREMIUM),
        )
        assert engine._can_use_scheduled_blocks is True


# ---------------------------------------------------------------------------
# Config Manager
# ---------------------------------------------------------------------------

class TestAutomationConfigManager:
    """Test AutomationConfigManager persistence and operations."""

    def test_creates_default_profile(self, tmp_path):
        mgr = AutomationConfigManager(data_dir=tmp_path)
        assert "default" in mgr.profiles
        assert mgr.active_profile_id == "default"

    def test_create_and_switch_profile(self, tmp_path):
        mgr = AutomationConfigManager(data_dir=tmp_path)
        profile = mgr.create_profile("Work")
        assert profile.profile_id in mgr.profiles
        assert mgr.set_active_profile(profile.profile_id) is True
        assert mgr.active_profile.name == "Work"

    def test_delete_profile(self, tmp_path):
        mgr = AutomationConfigManager(data_dir=tmp_path)
        profile = mgr.create_profile("Temp")
        assert mgr.delete_profile(profile.profile_id) is True
        assert profile.profile_id not in mgr.profiles

    def test_cannot_delete_default_profile(self, tmp_path):
        mgr = AutomationConfigManager(data_dir=tmp_path)
        assert mgr.delete_profile("default") is False

    def test_execution_mode_persistence(self, tmp_path):
        mgr = AutomationConfigManager(data_dir=tmp_path)
        mgr.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        assert mgr.active_profile.execution_mode == ExecutionMode.AUTONOMOUS

        # Re-load and verify
        mgr2 = AutomationConfigManager(data_dir=tmp_path)
        assert mgr2.active_profile.execution_mode == ExecutionMode.AUTONOMOUS

    def test_add_custom_rule(self, tmp_path):
        mgr = AutomationConfigManager(data_dir=tmp_path)
        rule = AutomationRule(
            name="Test Rule",
            trigger=TriggerType.ENERGY_LOW,
            actions=[AutomationAction(ActionType.LOG_STATE)],
        )
        assert mgr.add_custom_rule("default", rule) is True
        assert len(mgr.active_profile.custom_rules) == 1

    def test_remove_custom_rule(self, tmp_path):
        mgr = AutomationConfigManager(data_dir=tmp_path)
        rule = AutomationRule(
            name="Test Rule",
            trigger=TriggerType.ENERGY_LOW,
            actions=[AutomationAction(ActionType.LOG_STATE)],
        )
        mgr.add_custom_rule("default", rule)
        assert mgr.remove_custom_rule("default", "Test Rule") is True
        assert len(mgr.active_profile.custom_rules) == 0

    def test_scheduled_blocks(self, tmp_path):
        mgr = AutomationConfigManager(data_dir=tmp_path)
        block = ScheduledFocusBlock(
            block_id="b1",
            name="Morning Focus",
            start_time=time(9, 0),
            end_time=time(11, 0),
            days_of_week=[0, 1, 2, 3, 4],
        )
        mgr.add_scheduled_block(block)
        assert len(mgr.scheduled_blocks) == 1

        assert mgr.remove_scheduled_block("b1") is True
        assert len(mgr.scheduled_blocks) == 0

    def test_get_active_blocks(self, tmp_path):
        mgr = AutomationConfigManager(data_dir=tmp_path)
        block = ScheduledFocusBlock(
            block_id="b1",
            name="All Day",
            start_time=time(0, 0),
            end_time=time(23, 59),
            days_of_week=list(range(7)),
        )
        mgr.add_scheduled_block(block)
        active = mgr.get_active_blocks()
        assert len(active) == 1
        assert active[0].name == "All Day"


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

class TestAutomationAnalytics:
    """Test AutomationAnalytics event tracking and reporting."""

    def test_record_rule_fired(self, tmp_path):
        analytics = AutomationAnalytics(data_dir=tmp_path)
        analytics.record_rule_fired("test_rule", actions_succeeded=2, actions_failed=1)
        stats = analytics.rule_stats["test_rule"]
        assert stats.times_fired == 1
        assert stats.actions_succeeded == 2
        assert stats.actions_failed == 1

    def test_record_focus_session(self, tmp_path):
        analytics = AutomationAnalytics(data_dir=tmp_path)
        analytics.record_focus_session(duration_minutes=25, interrupted=False)
        today = analytics._today()
        assert today.focus_sessions == 1
        assert today.total_focus_minutes == 25

    def test_focus_trends(self, tmp_path):
        analytics = AutomationAnalytics(data_dir=tmp_path)
        analytics.record_focus_session(duration_minutes=30, interrupted=False)
        analytics.record_focus_session(duration_minutes=20, interrupted=True)
        trends = analytics.get_focus_trends(days=30)
        assert trends["total_sessions"] == 2
        assert trends["total_minutes"] == 50
        assert trends["interruption_rate"] == 0.5

    def test_weekly_summary(self, tmp_path):
        analytics = AutomationAnalytics(data_dir=tmp_path)
        summary = analytics.get_weekly_summary()
        assert len(summary["dates"]) == 7
        assert len(summary["focus_minutes"]) == 7

    def test_overall_stats(self, tmp_path):
        analytics = AutomationAnalytics(data_dir=tmp_path)
        analytics.record_rule_fired("r1", 1, 0)
        analytics.record_rule_fired("r2", 1, 0)
        analytics.record_display_adaptation()
        analytics.record_apps_closed(3)
        stats = analytics.get_overall_stats()
        assert stats["total_rules_fired"] == 2
        assert stats["total_display_adaptations"] == 1
        assert stats["total_apps_closed"] == 3

    def test_persistence(self, tmp_path):
        analytics = AutomationAnalytics(data_dir=tmp_path)
        analytics.record_rule_fired("persisted", 1, 0)
        analytics.record_focus_session(25, False)

        # Reload
        analytics2 = AutomationAnalytics(data_dir=tmp_path)
        assert "persisted" in analytics2.rule_stats
        assert analytics2.rule_stats["persisted"].times_fired == 1
