"""
App Guardian — monitors and manages applications based on psychological state.

- Closes distracting apps during focus mode or low energy
- Can enforce "app blackouts" during certain hours or states
- Tracks which apps are most disruptive per condition
- Provides gentle warnings before closing (configurable)
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from core.paths import get_data_dir
from core.platform_actions import PlatformBackend, get_backend

logger = logging.getLogger(__name__)


@dataclass
class AppInterruptionEvent:
    """Record of an app being closed by the guardian."""

    app_name: str
    timestamp: datetime
    reason: str
    trigger: str
    user_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "trigger": self.trigger,
            "user_conditions": self.user_conditions,
        }


class AppGuardian:
    """Manages application lifecycle based on user state."""

    def __init__(
        self,
        data_dir: Path | None = None,
        backend: PlatformBackend | None = None,
    ) -> None:
        self.data_dir = data_dir or get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / "app_guardian_history.json"
        self.config_file = self.data_dir / "app_guardian_config.json"

        self.backend = backend or get_backend()
        self._history: list[AppInterruptionEvent] = []
        self._blacklisted_apps: set[str] = set()
        self._enforce_mode: bool = False  # if True, closes without warning

        self._load_config()
        self._load_history()

    # -- persistence ----------------------------------------------------------

    def _load_config(self) -> None:
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    cfg = json.load(f)
                self._blacklisted_apps = set(cfg.get("blacklisted_apps", []))
                self._enforce_mode = cfg.get("enforce_mode", False)
            except (json.JSONDecodeError, OSError):
                pass

    def _save_config(self) -> None:
        with open(self.config_file, "w") as f:
            json.dump({
                "blacklisted_apps": sorted(self._blacklisted_apps),
                "enforce_mode": self._enforce_mode,
            }, f, indent=2)

    def _load_history(self) -> None:
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    raw = json.load(f)
                self._history = [
                    AppInterruptionEvent(
                        app_name=r["app_name"],
                        timestamp=datetime.fromisoformat(r["timestamp"]),
                        reason=r.get("reason", ""),
                        trigger=r.get("trigger", ""),
                        user_conditions=r.get("user_conditions", []),
                    )
                    for r in raw
                ]
            except (json.JSONDecodeError, OSError, KeyError):
                self._history = []

    def _save_history(self) -> None:
        with open(self.history_file, "w") as f:
            json.dump(
                [h.to_dict() for h in self._history[-1000:]],
                f,
                indent=2,
                default=str,
            )

    # -- actions --------------------------------------------------------------

    def close_app(self, app_name: str, reason: str, trigger: str, conditions: list[str] | None = None) -> bool:
        """Close an application and log the event."""
        ok = self.backend.close_application(app_name)
        if ok:
            event = AppInterruptionEvent(
                app_name=app_name,
                timestamp=datetime.now(),
                reason=reason,
                trigger=trigger,
                user_conditions=conditions or [],
            )
            self._history.append(event)
            self._save_history()
            logger.info("AppGuardian closed %s: %s", app_name, reason)
        return ok

    def hide_app(self, app_name: str, reason: str) -> bool:
        """Hide an application (minimise)."""
        ok = self.backend.hide_application(app_name)
        if ok:
            logger.info("AppGuardian hid %s: %s", app_name, reason)
        return ok

    def close_distractions(
        self,
        app_names: set[str] | None = None,
        reason: str = "focus_mode",
        trigger: str = "automation",
        conditions: list[str] | None = None,
    ) -> list[str]:
        """Close a set of distracting apps, returning those successfully closed."""
        targets = app_names or self._blacklisted_apps
        running = set(self.backend.list_running_applications())
        to_close = targets.intersection(running)
        closed: list[str] = []
        for app in to_close:
            if self.close_app(app, reason, trigger, conditions):
                closed.append(app)
        return closed

    # -- analytics ------------------------------------------------------------

    def get_top_disruptors(self, days: int = 30, top_n: int = 5) -> list[tuple[str, int]]:
        """Return the most frequently closed apps."""
        cutoff = datetime.now() - timedelta(days=days)
        counts: dict[str, int] = defaultdict(int)
        for event in self._history:
            if event.timestamp >= cutoff:
                counts[event.app_name] += 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def get_interruption_summary(self, days: int = 7) -> dict[str, Any]:
        """Summary stats for the guardian's activity."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in self._history if e.timestamp >= cutoff]
        if not recent:
            return {"total_interruptions": 0, "top_app": None, "by_trigger": {}}

        by_trigger: dict[str, int] = defaultdict(int)
        app_counts: dict[str, int] = defaultdict(int)
        for e in recent:
            by_trigger[e.trigger] += 1
            app_counts[e.app_name] += 1

        top_app = max(app_counts, key=app_counts.get)
        return {
            "total_interruptions": len(recent),
            "top_app": top_app,
            "top_app_count": app_counts[top_app],
            "by_trigger": dict(by_trigger),
        }

    # -- configuration --------------------------------------------------------

    def blacklist_app(self, app_name: str) -> None:
        self._blacklisted_apps.add(app_name)
        self._save_config()

    def unblacklist_app(self, app_name: str) -> None:
        self._blacklisted_apps.discard(app_name)
        self._save_config()

    def get_blacklist(self) -> set[str]:
        return set(self._blacklisted_apps)

    def set_enforce_mode(self, enabled: bool) -> None:
        self._enforce_mode = enabled
        self._save_config()

    @property
    def enforce_mode(self) -> bool:
        return self._enforce_mode
