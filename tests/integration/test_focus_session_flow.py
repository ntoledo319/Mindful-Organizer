"""
Integration tests for the Task Creation → Focus Session → Automation Analytics flow.

Validates that FocusModeManager can start a session, persist it, and that
analytics layers can read the recorded data. OS-level actions are fully mocked.
"""

from __future__ import annotations

from typing import Any

import pytest

from core.automation_analytics import AutomationAnalytics
from core.focus_mode import FocusModeManager, FocusModeState
from core.platform_actions import PlatformBackend


class _MockPlatformBackend(PlatformBackend):
    """No-op backend for focus-mode tests so we never touch the OS."""

    def __init__(self):
        self.dnd_state = False
        self.brightness = 50
        self.closed: list[str] = []

    def close_application(self, app_name: str) -> bool:
        self.closed.append(app_name)
        return True

    def hide_application(self, app_name: str) -> bool:
        return True

    def launch_application(self, app_name: str, **kwargs: Any) -> bool:
        return True

    def set_display_brightness(self, percent: int) -> bool:
        self.brightness = percent
        return True

    def set_night_shift(self, intensity: int, enabled: bool = True) -> bool:
        return True

    def set_system_theme(self, theme: str) -> bool:
        return True

    def set_dnd(self, enabled: bool) -> bool:
        self.dnd_state = enabled
        return True

    def minimize_all_windows(self) -> bool:
        return True

    def restore_windows(self) -> bool:
        return True

    def play_sound(self, sound_name: str) -> bool:
        return True

    def list_running_applications(self) -> list[str]:
        return ["Discord", "Slack", "Spotify"]


@pytest.fixture
def mock_backend():
    return _MockPlatformBackend()


@pytest.fixture
def focus_manager(tmp_data_dir, mock_backend):
    return FocusModeManager(data_dir=tmp_data_dir, backend=mock_backend)


@pytest.mark.integration
class TestFocusSessionFlow:
    def test_start_focus_session(self, focus_manager, mock_backend):
        """Activating focus mode should return success and track closed apps."""
        result = focus_manager.activate(reason="deep_work", trigger="user", duration_minutes=25)

        assert result["status"] == "activated"
        assert result["session_id"] is not None
        assert result["dnd_enabled"] is True
        assert focus_manager.state == FocusModeState.ACTIVE
        assert mock_backend.dnd_state is True
        assert "Discord" in result["closed_apps"] or "Slack" in result["closed_apps"]

    def test_persist_session_on_deactivate(self, focus_manager, tmp_data_dir):
        """Ending a session should persist it to disk."""
        focus_manager.activate()
        # Small sleep not needed; we can compute duration from timestamps
        result = focus_manager.deactivate(interrupted=False)

        assert result["status"] == "deactivated"
        assert result["duration_minutes"] >= 0
        assert result["interrupted"] is False

        # Verify file exists
        session_file = tmp_data_dir / "focus_sessions.json"
        assert session_file.exists()
        raw = session_file.read_text()
        assert result["session_id"] in raw

    def test_analytics_can_read_session(self, focus_manager):
        """FocusModeManager analytics should surface the persisted session."""
        focus_manager.activate()
        focus_manager.deactivate(interrupted=False)

        stats = focus_manager.get_statistics(days=1)
        assert stats["total_sessions"] == 1
        assert stats["total_minutes"] >= 0
        assert stats["interruption_rate"] == 0.0

    def test_automation_analytics_integration(self, focus_manager, tmp_data_dir):
        """AutomationAnalytics should be able to record and report focus sessions."""
        focus_manager.activate()
        focus_manager.deactivate(interrupted=False)

        # Record the session into the automation analytics layer
        session = focus_manager.get_sessions(days=1)[0]
        analytics = AutomationAnalytics(data_dir=tmp_data_dir)
        analytics.record_focus_session(
            duration_minutes=max(session.duration_minutes, 1),
            interrupted=session.interrupted,
        )

        trends = analytics.get_focus_trends(days=1)
        assert trends["total_sessions"] == 1
        assert trends["total_minutes"] > 0

    def test_session_pause_and_resume(self, focus_manager, mock_backend):
        """Pausing and resuming should toggle DND without ending the session."""
        focus_manager.activate()
        session_id = focus_manager.current_session.session_id

        pause_result = focus_manager.pause()
        assert pause_result["status"] == "paused"
        assert mock_backend.dnd_state is False

        resume_result = focus_manager.resume()
        assert resume_result["status"] == "resumed"
        assert mock_backend.dnd_state is True
        assert focus_manager.current_session.session_id == session_id

    def test_no_duplicate_activation(self, focus_manager):
        """Activating while already active should return already_active."""
        focus_manager.activate()
        second = focus_manager.activate()
        assert second["status"] == "already_active"

    def test_interrupted_session_tracked(self, focus_manager):
        """An interrupted session should reflect in stats."""
        focus_manager.activate()
        focus_manager.deactivate(interrupted=True)

        stats = focus_manager.get_statistics(days=1)
        assert stats["interruption_rate"] == 1.0
