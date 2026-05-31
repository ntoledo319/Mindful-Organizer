"""Tests for the System Automation Engine."""

from __future__ import annotations

from core.automation_config import ExecutionMode
from core.automation_rules import TriggerType
from core.constants import Condition
from core.platform_actions import StubBackend
from core.subscription_manager import SubscriptionManager, SubscriptionTier
from core.system_automation import SystemAutomationEngine


class MockSubscriptionManager(SubscriptionManager):
    """Subscription manager that always returns PRO tier for testing."""

    def __init__(self, tier: SubscriptionTier = SubscriptionTier.PRO) -> None:
        self._tier = tier
        super().__init__()

    @property
    def current_tier(self) -> SubscriptionTier:
        return self._tier

    def has_feature(self, feature: str) -> bool:
        from core.subscription_manager import FEATURES_BY_TIER

        return feature in FEATURES_BY_TIER.get(self._tier, set())


class TestAutomationEngineLifecycle:
    """Test basic engine setup and enable/disable."""

    def test_engine_starts_enabled(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        assert engine.is_enabled is True

    def test_disable_prevents_triggers(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.disable()
        results = engine.trigger(TriggerType.MANUAL_FOCUS)
        assert all(r["status"] == "disabled" for r in results)

    def test_enable_allows_triggers(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        engine.disable()
        engine.enable()
        results = engine.trigger(TriggerType.MANUAL_FOCUS)
        assert any(r["status"] == "executed" for r in results)


class TestRuleManagement:
    """Test rule enable/disable/list."""

    def test_list_rules_returns_all(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        rules = engine.list_rules()
        assert len(rules) > 0
        assert all("name" in r and "trigger" in r for r in rules)

    def test_disable_rule(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        assert engine.disable_rule("manual_focus_deep_work") is True
        results = engine.trigger(TriggerType.MANUAL_FOCUS)
        assert not any(
            r["rule"] == "manual_focus_deep_work" and r["status"] == "executed" for r in results
        )

    def test_enable_rule(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.disable_rule("manual_focus_deep_work")
        assert engine.enable_rule("manual_focus_deep_work") is True
        results = engine.trigger(TriggerType.MANUAL_FOCUS)
        assert any(r["rule"] == "manual_focus_deep_work" for r in results)

    def test_disable_unknown_rule_returns_false(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        assert engine.disable_rule("nonexistent") is False


class TestCooldownBehavior:
    """Test that cooldowns prevent rapid re-firing."""

    def test_cooldown_blocks_second_trigger(self, tmp_path):
        from core.automation_rules import ActionType, AutomationAction, AutomationRule

        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        # Inject a test rule with a 60-minute cooldown
        engine._base_rules.append(
            AutomationRule(
                name="test_cooldown_rule",
                trigger=TriggerType.ENERGY_LOW,
                actions=[AutomationAction(ActionType.LOG_STATE, reason="test")],
                cooldown_minutes=60,
            )
        )
        # First trigger should execute
        results1 = engine.trigger(TriggerType.ENERGY_LOW)
        assert any(
            r["status"] == "executed" and r["rule"] == "test_cooldown_rule" for r in results1
        )

        # Second trigger immediately should be on cooldown
        results2 = engine.trigger(TriggerType.ENERGY_LOW)
        assert any(
            r["status"] == "cooldown" and r["rule"] == "test_cooldown_rule" for r in results2
        )


class TestManualTriggers:
    """Test manual hotkey-triggered modes."""

    def test_manual_focus_activates_focus_mode(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        result = engine.manual_focus(duration_minutes=25)
        assert result["trigger"] == "manual_focus"
        # Either the rule activated it or the direct call did — both mean success
        assert result["focus_mode"]["status"] in ("activated", "already_active")
        assert engine.focus.state.name == "ACTIVE"

    def test_manual_crisis_returns_results(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        result = engine.manual_crisis()
        assert result["trigger"] == "manual_crisis"
        assert any(r["status"] == "executed" for r in result["automation_results"])

    def test_manual_grounding_returns_results(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        result = engine.manual_grounding()
        assert result["trigger"] == "manual_grounding"


class TestConditionAwareTriggers:
    """Test that condition-specific rules fire correctly."""

    def test_adhd_rule_requires_adhd_condition(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        engine.set_user_conditions({Condition.ADHD})
        results = engine.trigger(TriggerType.ADHD_SLUMP)
        assert any(r["rule"] == "adhd_afternoon_transition" for r in results)

    def test_adhd_rule_skipped_without_condition(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.set_user_conditions(set())
        results = engine.trigger(TriggerType.ADHD_SLUMP)
        assert not any(r["rule"] == "adhd_afternoon_transition" for r in results)

    def test_bipolar_rule_requires_bipolar(self, tmp_path):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)
        engine.set_user_conditions({Condition.BIPOLAR})
        results = engine.trigger(TriggerType.HYPOMANIA_SIGNS)
        assert any(r["rule"] == "hypomania_pacing" for r in results)


class TestStateEvaluation:
    """Test evaluate_current_state with mocked wellness data."""

    def test_low_energy_triggers_low_energy_rule(self, tmp_path, monkeypatch):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)

        # Mock wellness snapshot to return low energy
        class MockSnapshot:
            energy_score = 2
            mood_score = 5
            sleep_hours = 7

        monkeypatch.setattr(engine.wellness, "snapshot", lambda dt=None: MockSnapshot())
        monkeypatch.setattr(engine.ai, "detect_burnout_risk", lambda **kw: {"risk_level": "low"})
        monkeypatch.setattr(engine.ai, "detect_hypomania_signs", lambda **kw: {"detected": False})

        results = engine.evaluate_current_state()
        assert any(r["rule"] == "very_low_energy_minimal" for r in results)

    def test_high_energy_triggers_peak_rule(self, tmp_path, monkeypatch):
        engine = SystemAutomationEngine(
            data_dir=tmp_path,
            backend=StubBackend(),
            subscription_manager=MockSubscriptionManager(),
        )
        engine.config.set_execution_mode("default", ExecutionMode.AUTONOMOUS)

        class MockSnapshot:
            energy_score = 9
            mood_score = 7
            sleep_hours = 7

        monkeypatch.setattr(engine.wellness, "snapshot", lambda dt=None: MockSnapshot())
        monkeypatch.setattr(engine.ai, "detect_burnout_risk", lambda **kw: {"risk_level": "low"})
        monkeypatch.setattr(engine.ai, "detect_hypomania_signs", lambda **kw: {"detected": False})

        results = engine.evaluate_current_state()
        assert any(r["rule"] == "peak_energy_protect" for r in results)
