"""
Automation Configuration — Pro-tier settings for the System Automation Engine.

Free users get:
- Default rules (suggestions only, manual triggers)
- Single profile
- No custom rules

Pro/Premium users get:
- Autonomous execution mode
- Custom rule builder
- Multiple automation profiles (work, personal, sleep, etc.)
- Scheduled focus blocks
- Advanced system integrations
"""
from __future__ import annotations

import contextlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from pathlib import Path
from typing import Any

from core.automation_rules import (
    ActionType,
    AutomationAction,
    AutomationRule,
    TriggerType,
)

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """How aggressively the automation engine acts."""

    SUGGESTIONS_ONLY = "suggestions_only"   # Free: notifications, no system changes
    ASK_FIRST = "ask_first"                  # Pro: prompt before executing
    AUTONOMOUS = "autonomous"                # Pro: execute immediately


@dataclass
class AutomationProfile:
    """A named automation profile with its own rule set and settings."""

    profile_id: str
    name: str
    description: str = ""
    enabled_rules: list[str] = field(default_factory=list)
    custom_rules: list[AutomationRule] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SUGGESTIONS_ONLY
    distracting_apps: list[str] = field(default_factory=list)
    created_at: str = ""
    is_default: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "description": self.description,
            "enabled_rules": self.enabled_rules,
            "custom_rules": [
                {
                    "name": r.name,
                    "trigger": r.trigger.name,
                    "required_conditions": [c.name for c in r.required_conditions],
                    "actions": [
                        {
                            "action_type": a.action_type.name,
                            "target": a.target,
                            "payload": a.payload,
                            "reason": a.reason,
                        }
                        for a in r.actions
                    ],
                    "cooldown_minutes": r.cooldown_minutes,
                    "enabled_by_default": r.enabled_by_default,
                }
                for r in self.custom_rules
            ],
            "execution_mode": self.execution_mode.value,
            "distracting_apps": self.distracting_apps,
            "created_at": self.created_at or datetime.now().isoformat(),
            "is_default": self.is_default,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AutomationProfile:
        custom_rules = []
        for r in data.get("custom_rules", []):
            actions = [
                AutomationAction(
                    action_type=ActionType[a["action_type"]],
                    target=a.get("target"),
                    payload=a.get("payload", {}),
                    reason=a.get("reason", ""),
                )
                for a in r.get("actions", [])
            ]
            from core.constants import Condition
            req_conditions = set()
            for c in r.get("required_conditions", []):
                with contextlib.suppress(KeyError):
                    req_conditions.add(Condition[c])
            custom_rules.append(AutomationRule(
                name=r["name"],
                trigger=TriggerType[r["trigger"]],
                required_conditions=req_conditions,
                actions=actions,
                cooldown_minutes=r.get("cooldown_minutes", 30),
                enabled_by_default=r.get("enabled_by_default", True),
            ))

        return cls(
            profile_id=data["profile_id"],
            name=data["name"],
            description=data.get("description", ""),
            enabled_rules=data.get("enabled_rules", []),
            custom_rules=custom_rules,
            execution_mode=ExecutionMode(data.get("execution_mode", "suggestions_only")),
            distracting_apps=data.get("distracting_apps", []),
            created_at=data.get("created_at", ""),
            is_default=data.get("is_default", False),
        )


@dataclass
class ScheduledFocusBlock:
    """A recurring focus block on the calendar."""

    block_id: str
    name: str
    start_time: time
    end_time: time
    days_of_week: list[int]  # 0=Mon..6=Sun
    distracting_apps: list[str] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "block_id": self.block_id,
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "days_of_week": self.days_of_week,
            "distracting_apps": self.distracting_apps,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScheduledFocusBlock:
        return cls(
            block_id=data["block_id"],
            name=data["name"],
            start_time=time.fromisoformat(data["start_time"]),
            end_time=time.fromisoformat(data["end_time"]),
            days_of_week=data.get("days_of_week", [0, 1, 2, 3, 4]),
            distracting_apps=data.get("distracting_apps", []),
            enabled=data.get("enabled", True),
        )


class AutomationConfigManager:
    """Manages automation configuration, profiles, and scheduled blocks."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path.home() / ".mindful_optimizer"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.data_dir / "automation_config.json"

        self.profiles: dict[str, AutomationProfile] = {}
        self.scheduled_blocks: list[ScheduledFocusBlock] = []
        self.active_profile_id: str = ""

        self._load()
        if not self.profiles:
            self._create_default_profile()

    # -- persistence ----------------------------------------------------------

    def _load(self) -> None:
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    data = json.load(f)
                self.profiles = {
                    k: AutomationProfile.from_dict(v)
                    for k, v in data.get("profiles", {}).items()
                }
                self.scheduled_blocks = [
                    ScheduledFocusBlock.from_dict(b)
                    for b in data.get("scheduled_blocks", [])
                ]
                self.active_profile_id = data.get("active_profile_id", "")
            except (json.JSONDecodeError, OSError, KeyError) as exc:
                logger.warning("Failed to load automation config: %s", exc)
                self._create_default_profile()
        else:
            self._create_default_profile()

    def _save(self) -> None:
        data = {
            "profiles": {k: v.to_dict() for k, v in self.profiles.items()},
            "scheduled_blocks": [b.to_dict() for b in self.scheduled_blocks],
            "active_profile_id": self.active_profile_id,
            "saved_at": datetime.now().isoformat(),
        }
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    # -- profiles -------------------------------------------------------------

    def _create_default_profile(self) -> None:
        profile = AutomationProfile(
            profile_id="default",
            name="Default",
            description="Your everyday automation profile.",
            is_default=True,
            execution_mode=ExecutionMode.SUGGESTIONS_ONLY,
        )
        self.profiles[profile.profile_id] = profile
        self.active_profile_id = profile.profile_id
        self._save()

    def create_profile(self, name: str, description: str = "") -> AutomationProfile:
        profile = AutomationProfile(
            profile_id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            created_at=datetime.now().isoformat(),
        )
        self.profiles[profile.profile_id] = profile
        self._save()
        return profile

    def delete_profile(self, profile_id: str) -> bool:
        if profile_id == "default":
            return False
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            if self.active_profile_id == profile_id:
                self.active_profile_id = "default"
            self._save()
            return True
        return False

    def set_active_profile(self, profile_id: str) -> bool:
        if profile_id in self.profiles:
            self.active_profile_id = profile_id
            self._save()
            return True
        return False

    @property
    def active_profile(self) -> AutomationProfile:
        return self.profiles.get(self.active_profile_id, next(iter(self.profiles.values())))

    # -- custom rules ---------------------------------------------------------

    def add_custom_rule(self, profile_id: str, rule: AutomationRule) -> bool:
        profile = self.profiles.get(profile_id)
        if not profile:
            return False
        profile.custom_rules.append(rule)
        self._save()
        return True

    def remove_custom_rule(self, profile_id: str, rule_name: str) -> bool:
        profile = self.profiles.get(profile_id)
        if not profile:
            return False
        before = len(profile.custom_rules)
        profile.custom_rules = [r for r in profile.custom_rules if r.name != rule_name]
        if len(profile.custom_rules) < before:
            self._save()
            return True
        return False

    # -- execution mode -------------------------------------------------------

    def set_execution_mode(self, profile_id: str, mode: ExecutionMode) -> bool:
        profile = self.profiles.get(profile_id)
        if not profile:
            return False
        profile.execution_mode = mode
        self._save()
        return True

    # -- scheduled blocks -----------------------------------------------------

    def add_scheduled_block(self, block: ScheduledFocusBlock) -> None:
        self.scheduled_blocks.append(block)
        self._save()

    def remove_scheduled_block(self, block_id: str) -> bool:
        before = len(self.scheduled_blocks)
        self.scheduled_blocks = [b for b in self.scheduled_blocks if b.block_id != block_id]
        if len(self.scheduled_blocks) < before:
            self._save()
            return True
        return False

    def get_active_blocks(self, now: datetime | None = None) -> list[ScheduledFocusBlock]:
        """Return scheduled blocks that should be active right now."""
        now = now or datetime.now()
        current_time = now.time()
        current_dow = now.weekday()
        active: list[ScheduledFocusBlock] = []
        for block in self.scheduled_blocks:
            if not block.enabled:
                continue
            if current_dow not in block.days_of_week:
                continue
            if block.start_time <= current_time <= block.end_time:
                active.append(block)
        return active
