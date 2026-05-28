"""
Focus Mode — a deep-work environment activated manually or by the automation engine.

When active, Focus Mode:
- Closes or hides distracting applications
- Enables Do-Not-Disturb
- Adjusts display for sustained attention
- Can optionally play a focus sound
- Tracks the session for analytics

Sessions are persisted so the AI optimizer can learn from them.
"""
from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from core.platform_actions import PlatformBackend, get_backend

logger = logging.getLogger(__name__)


class FocusModeState(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"


@dataclass
class FocusSession:
    """A single focus-mode session."""

    session_id: str
    started_at: datetime
    ended_at: datetime | None = None
    reason: str = "manual"
    trigger: str = "user"
    closed_apps: list[str] = field(default_factory=list)
    duration_minutes: int = 0
    interrupted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "reason": self.reason,
            "trigger": self.trigger,
            "closed_apps": self.closed_apps,
            "duration_minutes": self.duration_minutes,
            "interrupted": self.interrupted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FocusSession:
        return cls(
            session_id=data["session_id"],
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            reason=data.get("reason", "manual"),
            trigger=data.get("trigger", "user"),
            closed_apps=data.get("closed_apps", []),
            duration_minutes=data.get("duration_minutes", 0),
            interrupted=data.get("interrupted", False),
        )


class FocusModeManager:
    """Manages focus-mode activation, deactivation, and session history."""

    DEFAULT_DISTRACTING_APPS = {
        "Discord",
        "Slack",
        "Twitter",
        "Telegram",
        "WhatsApp",
        "Messages",
        "Mail",
        "Calendar",
        "Spotify",
        "Netflix",
        "Twitch",
        "Reddit",
        "Instagram",
        "TikTok",
    }

    def __init__(
        self,
        data_dir: Path | None = None,
        backend: PlatformBackend | None = None,
    ) -> None:
        self.data_dir = data_dir or Path.home() / ".mindful_optimizer"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.data_dir / "focus_sessions.json"
        self.config_file = self.data_dir / "focus_config.json"

        self.backend = backend or get_backend()
        self.state = FocusModeState.INACTIVE
        self.current_session: FocusSession | None = None
        self._pre_focus_brightness: int | None = None
        self._distracting_apps: set[str] = set(self.DEFAULT_DISTRACTING_APPS)

        self._load_config()
        self._load_history()

    # -- persistence ----------------------------------------------------------

    def _load_config(self) -> None:
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    cfg = json.load(f)
                self._distracting_apps = set(cfg.get("distracting_apps", list(self.DEFAULT_DISTRACTING_APPS)))
            except (json.JSONDecodeError, OSError):
                pass

    def _save_config(self) -> None:
        with open(self.config_file, "w") as f:
            json.dump({
                "distracting_apps": sorted(self._distracting_apps),
            }, f, indent=2)

    def _load_history(self) -> list[FocusSession]:
        if self.session_file.exists():
            try:
                with open(self.session_file) as f:
                    raw = json.load(f)
                return [FocusSession.from_dict(r) for r in raw]
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def _save_history(self, sessions: list[FocusSession]) -> None:
        with open(self.session_file, "w") as f:
            json.dump([s.to_dict() for s in sessions[-500:]], f, indent=2, default=str)

    # -- session control ------------------------------------------------------

    def activate(
        self,
        reason: str = "manual",
        trigger: str = "user",
        duration_minutes: int = 0,
    ) -> dict[str, Any]:
        """Activate focus mode.

        Returns a dict describing what happened.
        """
        if self.state == FocusModeState.ACTIVE:
            return {"status": "already_active", "session_id": self.current_session.session_id if self.current_session else None}

        logger.info("Activating focus mode (reason=%s, trigger=%s)", reason, trigger)

        # Remember current brightness
        self._pre_focus_brightness = None  # We can't read it easily on macOS, so we skip restore

        # Close distracting apps
        closed = self.backend.close_distracting_apps(self._distracting_apps)

        # Enable DND
        dnd_ok = self.backend.set_dnd(True)

        # Bright, alert display for focus
        self.backend.set_display_brightness(70)

        # Create session
        self.current_session = FocusSession(
            session_id=str(uuid.uuid4())[:8],
            started_at=datetime.now(),
            reason=reason,
            trigger=trigger,
            closed_apps=closed,
            duration_minutes=duration_minutes,
        )
        self.state = FocusModeState.ACTIVE

        return {
            "status": "activated",
            "session_id": self.current_session.session_id,
            "closed_apps": closed,
            "dnd_enabled": dnd_ok,
        }

    def deactivate(self, interrupted: bool = False) -> dict[str, Any]:
        """Deactivate focus mode and save the session."""
        if self.state != FocusModeState.ACTIVE or self.current_session is None:
            return {"status": "not_active"}

        logger.info("Deactivating focus mode")

        session = self.current_session
        session.ended_at = datetime.now()
        session.interrupted = interrupted
        delta = session.ended_at - session.started_at
        session.duration_minutes = int(delta.total_seconds() // 60)

        # Disable DND
        self.backend.set_dnd(False)

        # Restore brightness (best effort)
        if self._pre_focus_brightness is not None:
            self.backend.set_display_brightness(self._pre_focus_brightness)

        # Persist
        history = self._load_history()
        history.append(session)
        self._save_history(history)

        self.state = FocusModeState.INACTIVE
        self.current_session = None

        return {
            "status": "deactivated",
            "session_id": session.session_id,
            "duration_minutes": session.duration_minutes,
            "interrupted": interrupted,
        }

    def pause(self) -> dict[str, Any]:
        """Pause focus mode without ending the session."""
        if self.state != FocusModeState.ACTIVE:
            return {"status": "not_active"}
        self.state = FocusModeState.PAUSED
        self.backend.set_dnd(False)
        return {"status": "paused", "session_id": self.current_session.session_id if self.current_session else None}

    def resume(self) -> dict[str, Any]:
        """Resume a paused focus mode."""
        if self.state != FocusModeState.PAUSED:
            return {"status": "not_paused"}
        self.state = FocusModeState.ACTIVE
        self.backend.set_dnd(True)
        self.backend.close_distracting_apps(self._distracting_apps)
        return {"status": "resumed", "session_id": self.current_session.session_id if self.current_session else None}

    # -- configuration --------------------------------------------------------

    def get_distracting_apps(self) -> set[str]:
        return set(self._distracting_apps)

    def add_distracting_app(self, app_name: str) -> None:
        self._distracting_apps.add(app_name)
        self._save_config()

    def remove_distracting_app(self, app_name: str) -> None:
        self._distracting_apps.discard(app_name)
        self._save_config()

    # -- analytics ------------------------------------------------------------

    def get_sessions(self, days: int = 30) -> list[FocusSession]:
        """Return sessions from the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        return [s for s in self._load_history() if s.started_at >= cutoff]

    def get_statistics(self, days: int = 30) -> dict[str, Any]:
        sessions = self.get_sessions(days)
        if not sessions:
            return {
                "total_sessions": 0,
                "total_minutes": 0,
                "avg_duration": 0,
                "interruption_rate": 0.0,
                "most_closed_app": None,
            }

        total_minutes = sum(s.duration_minutes for s in sessions)
        interruptions = sum(1 for s in sessions if s.interrupted)
        app_counts: dict[str, int] = {}
        for s in sessions:
            for app in s.closed_apps:
                app_counts[app] = app_counts.get(app, 0) + 1

        most_closed = max(app_counts, key=app_counts.get) if app_counts else None

        return {
            "total_sessions": len(sessions),
            "total_minutes": total_minutes,
            "avg_duration": round(total_minutes / len(sessions), 1),
            "interruption_rate": round(interruptions / len(sessions), 2),
            "most_closed_app": most_closed,
        }
