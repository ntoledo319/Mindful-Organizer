"""
System Automation Engine

The central conductor that maps psychological state (from the wellness
orchestrator, energy predictor, and user profile) to concrete system actions.

Tier gating:
- FREE: suggestions / notifications only (no system changes)
- PRO: autonomous execution of default rules, manual focus, display adaptation
- PREMIUM: custom rules, multiple profiles, scheduled blocks, analytics

It is NOT a medical device. It is a productivity-optimisation layer that
uses psychological data to adapt the computing environment.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from core.ai_optimizer import AISystemOptimizer
from core.automation_analytics import AutomationAnalytics
from core.automation_config import (
    AutomationConfigManager,
    ExecutionMode,
)
from core.automation_rules import (
    ActionType,
    AutomationAction,
    AutomationRule,
    TriggerType,
    get_default_rules,
    rules_for_trigger,
)
from core.constants import Condition
from core.database import DatabaseManager
from core.display_adaptation import DisplayAdaptationEngine
from core.focus_mode import FocusModeManager
from core.paths import get_data_dir
from core.platform_actions import PlatformBackend, get_backend
from core.subscription_manager import SubscriptionManager
from core.wellness_orchestrator import WellnessOrchestrator

logger = logging.getLogger(__name__)


class SystemAutomationEngine:
    """Central automation engine: state in, actions out."""

    def __init__(
        self,
        data_dir: Path | None = None,
        backend: PlatformBackend | None = None,
        wellness_orchestrator: WellnessOrchestrator | None = None,
        focus_manager: FocusModeManager | None = None,
        display_engine: DisplayAdaptationEngine | None = None,
        ai_optimizer: AISystemOptimizer | None = None,
        subscription_manager: SubscriptionManager | None = None,
        config_manager: AutomationConfigManager | None = None,
        analytics: AutomationAnalytics | None = None,
    ) -> None:
        self.data_dir = data_dir or get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.backend = backend or get_backend()
        wellness_db = DatabaseManager(db_path=self.data_dir / "mindful_organizer.db")
        self.wellness = wellness_orchestrator or WellnessOrchestrator(db=wellness_db)
        self.focus = focus_manager or FocusModeManager(data_dir=self.data_dir, backend=self.backend)
        self.display = display_engine or DisplayAdaptationEngine(backend=self.backend)
        self.ai = ai_optimizer or AISystemOptimizer(self.data_dir)
        self.subscription = subscription_manager or SubscriptionManager(self.data_dir)
        self.config = config_manager or AutomationConfigManager(self.data_dir)
        self.analytics = analytics or AutomationAnalytics(self.data_dir)

        self._base_rules: list[AutomationRule] = get_default_rules()
        self._last_fired: dict[str, datetime] = defaultdict(lambda: datetime.min)
        self._enabled = True
        self._user_conditions: set[Condition] = set()

    # -- tier-aware helpers ---------------------------------------------------

    @property
    def _can_execute_system_actions(self) -> bool:
        """True if the subscription allows actual system changes (PRO+)."""
        return self.subscription.has_feature("system_actions")

    @property
    def _can_use_autonomous_mode(self) -> bool:
        """True if rules fire automatically without manual trigger (PRO+)."""
        return self.subscription.has_feature("autonomous_mode")

    @property
    def _can_use_custom_rules(self) -> bool:
        """True if user can create custom rules (PREMIUM)."""
        return self.subscription.has_feature("custom_rules")

    @property
    def _can_use_scheduled_blocks(self) -> bool:
        """True if scheduled focus blocks are available (PREMIUM)."""
        return self.subscription.has_feature("scheduled_focus_blocks")

    @property
    def _can_use_analytics(self) -> bool:
        """True if automation analytics are tracked (PREMIUM)."""
        return self.subscription.has_feature("automation_analytics")

    @property
    def _can_use_multiple_profiles(self) -> bool:
        """True if multiple automation profiles are available (PREMIUM)."""
        return self.subscription.has_feature("multiple_automation_profiles")

    def _effective_execution_mode(self) -> ExecutionMode:
        """Return the current execution mode respecting tier limits."""
        profile = self.config.active_profile
        mode = profile.execution_mode

        if not self._can_execute_system_actions:
            return ExecutionMode.SUGGESTIONS_ONLY
        if not self._can_use_autonomous_mode and mode == ExecutionMode.AUTONOMOUS:
            return ExecutionMode.ASK_FIRST
        return mode

    def _effective_rules(self) -> list[AutomationRule]:
        """Return the active rule set, including custom rules if allowed."""
        rules = list(self._base_rules)
        if self._can_use_custom_rules:
            profile = self.config.active_profile
            for rule in profile.custom_rules:
                if rule.name in profile.enabled_rules or not profile.enabled_rules:
                    rules.append(rule)
        return rules

    # -- configuration --------------------------------------------------------

    def set_user_conditions(self, conditions: set[Condition]) -> None:
        self._user_conditions = conditions

    def enable(self) -> None:
        self._enabled = True
        logger.info("System automation enabled")

    def disable(self) -> None:
        self._enabled = False
        logger.info("System automation disabled")

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    # -- public triggers ------------------------------------------------------

    def trigger(
        self, trigger_type: TriggerType, context: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Fire all rules matching a trigger and execute (or suggest) their actions."""
        if not self._enabled:
            return [{"status": "disabled", "trigger": trigger_type.name}]

        mode = self._effective_execution_mode()
        rules = self._effective_rules()
        matched = rules_for_trigger(rules, trigger_type, self._user_conditions)
        results: list[dict[str, Any]] = []

        for rule in matched:
            if not rule.enabled_by_default:
                continue

            # Check if rule is enabled in active profile
            profile = self.config.active_profile
            if profile.enabled_rules and rule.name not in profile.enabled_rules:
                continue

            # Cooldown check
            last = self._last_fired.get(rule.name, datetime.min)
            if datetime.now() - last < timedelta(minutes=rule.cooldown_minutes):
                results.append(
                    {
                        "rule": rule.name,
                        "status": "cooldown",
                        "cooldown_minutes": rule.cooldown_minutes,
                    }
                )
                if self._can_use_analytics:
                    self.analytics.record_rule_cooldown(rule.name)
                continue

            # Suggestions-only mode: log + notify, but don't act
            if mode == ExecutionMode.SUGGESTIONS_ONLY:
                results.append(
                    {
                        "rule": rule.name,
                        "status": "suggested",
                        "actions": [a.action_type.name for a in rule.actions],
                        "reason": rule.actions[0].reason if rule.actions else "",
                    }
                )
                continue

            # ASK_FIRST mode: return pending for UI confirmation
            if mode == ExecutionMode.ASK_FIRST:
                results.append(
                    {
                        "rule": rule.name,
                        "status": "pending_confirmation",
                        "actions": [a.action_type.name for a in rule.actions],
                    }
                )
                continue

            # AUTONOMOUS mode: execute immediately
            action_results = []
            succeeded = 0
            failed = 0
            for action in rule.actions:
                result = self._execute_action(action)
                action_results.append(result)
                if result.get("success"):
                    succeeded += 1
                else:
                    failed += 1

            self._last_fired[rule.name] = datetime.now()
            results.append(
                {
                    "rule": rule.name,
                    "status": "executed",
                    "actions": action_results,
                }
            )

            if self._can_use_analytics:
                self.analytics.record_rule_fired(rule.name, succeeded, failed)

        return results

    def confirm_pending_rule(
        self, rule_name: str, actions: list[AutomationAction]
    ) -> dict[str, Any]:
        """Execute a previously pending rule (ASK_FIRST mode)."""
        action_results = []
        succeeded = 0
        failed = 0
        for action in actions:
            result = self._execute_action(action)
            action_results.append(result)
            if result.get("success"):
                succeeded += 1
            else:
                failed += 1

        self._last_fired[rule_name] = datetime.now()
        if self._can_use_analytics:
            self.analytics.record_rule_fired(rule_name, succeeded, failed)

        return {
            "rule": rule_name,
            "status": "executed",
            "actions": action_results,
        }

    def evaluate_current_state(self) -> list[dict[str, Any]]:
        """Read current wellness state and fire appropriate automation triggers."""
        if not self._enabled:
            return []

        # Check scheduled focus blocks (PREMIUM)
        if self._can_use_scheduled_blocks:
            self._check_scheduled_blocks()

        snapshot = self.wellness.snapshot()
        results: list[dict[str, Any]] = []

        # Energy triggers
        if snapshot.energy_score is not None:
            if snapshot.energy_score <= 2:
                results.extend(self.trigger(TriggerType.ENERGY_VERY_LOW))
            elif snapshot.energy_score <= 3:
                results.extend(self.trigger(TriggerType.ENERGY_LOW))
            elif snapshot.energy_score >= 8:
                results.extend(self.trigger(TriggerType.ENERGY_PEAK))
            elif snapshot.energy_score >= 7:
                results.extend(self.trigger(TriggerType.ENERGY_HIGH))

        # Mood triggers
        if snapshot.mood_score is not None:
            if snapshot.mood_score <= 2:
                results.extend(self.trigger(TriggerType.MOOD_VERY_LOW))
            elif snapshot.mood_score <= 3:
                results.extend(self.trigger(TriggerType.MOOD_LOW))

        # Sleep debt
        if snapshot.sleep_hours is not None and snapshot.sleep_hours < 5:
            results.extend(self.trigger(TriggerType.SLEEP_DEBT))

        # Burnout risk
        burnout = self.ai.detect_burnout_risk()
        if burnout.get("risk_level") in ("moderate", "high"):
            results.extend(self.trigger(TriggerType.BURNOUT_RISK))

        # Hypomania (bipolar only)
        if Condition.BIPOLAR in self._user_conditions:
            hypo = self.ai.detect_hypomania_signs()
            if hypo.get("detected"):
                results.extend(self.trigger(TriggerType.HYPOMANIA_SIGNS))

        # ADHD afternoon slump
        now = datetime.now()
        if Condition.ADHD in self._user_conditions and 15 <= now.hour < 16:
            results.extend(self.trigger(TriggerType.ADHD_SLUMP))

        # Display adaptation (PRO+)
        if self._can_execute_system_actions:
            self.display.adapt(
                energy_score=snapshot.energy_score,
                mood_score=snapshot.mood_score,
                burnout_risk=burnout.get("risk_level", "low"),
                sleep_hours=snapshot.sleep_hours,
            )
            if self._can_use_analytics:
                self.analytics.record_display_adaptation()

        return results

    def _check_scheduled_blocks(self) -> None:
        """Activate focus mode for any currently scheduled focus blocks."""
        active_blocks = self.config.get_active_blocks()
        if active_blocks and self.focus.state.name != "ACTIVE":
            # Use the first active block's settings
            block = active_blocks[0]
            self.focus.activate(
                reason=f"scheduled_block:{block.name}",
                trigger="automation",
                distracting_apps=block.distracting_apps,
            )
            if self._can_use_analytics:
                self.analytics.record_focus_session(
                    duration_minutes=0,  # Will be updated on deactivation
                    interrupted=False,
                )

    # -- manual triggers ------------------------------------------------------

    def manual_focus(self, duration_minutes: int = 0) -> dict[str, Any]:
        """User manually activated focus mode."""
        results = self.trigger(TriggerType.MANUAL_FOCUS)
        if self.focus.state.name != "ACTIVE":
            focus_result = self.focus.activate(
                reason="manual_trigger",
                trigger="user",
                duration_minutes=duration_minutes,
            )
        else:
            focus_result = {
                "status": "already_active",
                "session_id": self.focus.current_session.session_id
                if self.focus.current_session
                else None,
            }
        return {
            "trigger": "manual_focus",
            "automation_results": results,
            "focus_mode": focus_result,
        }

    def manual_crisis(self) -> dict[str, Any]:
        """User manually activated crisis mode."""
        results = self.trigger(TriggerType.MANUAL_CRISIS)
        if self._can_execute_system_actions:
            self.display.adapt_for_condition("ptsd")
        return {
            "trigger": "manual_crisis",
            "automation_results": results,
        }

    def manual_grounding(self) -> dict[str, Any]:
        """User manually activated grounding mode."""
        results = self.trigger(TriggerType.MANUAL_GROUNDING)
        if self._can_execute_system_actions:
            self.display.adapt_for_condition("anxiety")
        return {
            "trigger": "manual_grounding",
            "automation_results": results,
        }

    # -- action execution -----------------------------------------------------

    def _execute_action(self, action: AutomationAction) -> dict[str, Any]:
        """Execute a single automation action and return the result."""
        result: dict[str, Any] = {
            "action": action.action_type.name,
            "target": action.target,
            "success": False,
            "reason": action.reason,
        }

        # FREE tier: never execute system actions
        if not self._can_execute_system_actions:
            result["status"] = "gated"
            result["detail"] = "Requires PRO subscription"
            return result

        try:
            if action.action_type == ActionType.ENABLE_FOCUS_MODE:
                res = self.focus.activate(reason=action.reason, trigger="automation")
                result["success"] = res.get("status") == "activated"
                result["detail"] = res

            elif action.action_type == ActionType.DISABLE_FOCUS_MODE:
                res = self.focus.deactivate()
                result["success"] = res.get("status") == "deactivated"
                result["detail"] = res

            elif action.action_type == ActionType.CLOSE_APPLICATION:
                if action.target:
                    result["success"] = self.backend.close_application(action.target)

            elif action.action_type == ActionType.HIDE_APPLICATION:
                if action.target:
                    result["success"] = self.backend.hide_application(action.target)

            elif action.action_type == ActionType.LAUNCH_APPLICATION:
                if action.target:
                    result["success"] = self.backend.launch_application(
                        action.target, **action.payload
                    )

            elif action.action_type == ActionType.SET_DND:
                result["success"] = self.backend.set_dnd(True)

            elif action.action_type == ActionType.UNSET_DND:
                result["success"] = self.backend.set_dnd(False)

            elif action.action_type == ActionType.SET_DISPLAY_BRIGHTNESS:
                if action.target:
                    result["success"] = self.backend.set_display_brightness(int(action.target))

            elif action.action_type == ActionType.SET_NIGHT_SHIFT:
                intensity = int(action.target) if action.target else 50
                enabled = action.payload.get("enabled", True)
                result["success"] = self.backend.set_night_shift(intensity, enabled=enabled)

            elif action.action_type == ActionType.SET_SYSTEM_THEME:
                if action.target:
                    result["success"] = self.backend.set_system_theme(action.target)

            elif action.action_type == ActionType.MINIMIZE_ALL_WINDOWS:
                result["success"] = self.backend.minimize_all_windows()

            elif action.action_type == ActionType.RESTORE_WINDOWS:
                result["success"] = self.backend.restore_windows()

            elif action.action_type == ActionType.PLAY_SOUND:
                if action.target:
                    result["success"] = self.backend.play_sound(action.target)

            elif action.action_type == ActionType.SHOW_OVERLAY:
                # Overlay is handled by the GUI layer; log it here
                result["success"] = True
                result["detail"] = action.payload

            elif action.action_type == ActionType.LOG_STATE:
                logger.info("Automation log: %s — %s", action.target, action.reason)
                result["success"] = True

        except Exception as exc:
            logger.exception("Automation action failed: %s", action)
            result["error"] = str(exc)

        return result

    # -- rule management ------------------------------------------------------

    def enable_rule(self, name: str) -> bool:
        for rule in self._base_rules:
            if rule.name == name:
                rule.enabled_by_default = True
                return True
        return False

    def disable_rule(self, name: str) -> bool:
        for rule in self._base_rules:
            if rule.name == name:
                rule.enabled_by_default = False
                return True
        return False

    def list_rules(self) -> list[dict[str, Any]]:
        rules = self._effective_rules()
        profile = self.config.active_profile
        return [
            {
                "name": r.name,
                "trigger": r.trigger.name,
                "enabled": r.enabled_by_default,
                "in_profile": r.name in profile.enabled_rules if profile.enabled_rules else True,
                "cooldown_minutes": r.cooldown_minutes,
                "actions": len(r.actions),
                "is_custom": r not in self._base_rules,
            }
            for r in rules
        ]

    # -- profile management ---------------------------------------------------

    def get_active_profile(self) -> dict[str, Any]:
        """Return the active profile as a dict."""
        p = self.config.active_profile
        return {
            "profile_id": p.profile_id,
            "name": p.name,
            "description": p.description,
            "execution_mode": p.execution_mode.value,
            "enabled_rules": p.enabled_rules,
            "custom_rules_count": len(p.custom_rules),
            "distracting_apps": p.distracting_apps,
        }

    def list_profiles(self) -> list[dict[str, Any]]:
        """Return all available profiles."""
        if not self._can_use_multiple_profiles:
            p = self.config.active_profile
            return [{"profile_id": p.profile_id, "name": p.name, "is_active": True}]
        return [
            {
                "profile_id": p.profile_id,
                "name": p.name,
                "is_active": p.profile_id == self.config.active_profile_id,
                "is_default": p.is_default,
            }
            for p in self.config.profiles.values()
        ]

    # -- analytics access -----------------------------------------------------

    def get_analytics(self) -> dict[str, Any] | None:
        """Return automation analytics if available (PREMIUM)."""
        if not self._can_use_analytics:
            return None
        return {
            "overall": self.analytics.get_overall_stats(),
            "focus_trends": self.analytics.get_focus_trends(days=30),
            "weekly_summary": self.analytics.get_weekly_summary(),
            "rule_effectiveness": self.analytics.get_rule_effectiveness(days=30),
        }
