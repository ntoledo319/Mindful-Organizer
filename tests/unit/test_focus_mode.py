"""Tests for the Focus Mode manager."""
from __future__ import annotations

from core.focus_mode import FocusModeManager, FocusModeState
from core.platform_actions import StubBackend


class TestFocusModeActivation:
    """Test focus mode lifecycle."""

    def test_activate_creates_session(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        result = mgr.activate(reason="test", trigger="user", duration_minutes=25)
        assert result["status"] == "activated"
        assert result["session_id"] is not None
        assert mgr.state == FocusModeState.ACTIVE
        assert mgr.current_session is not None
        assert mgr.current_session.reason == "test"

    def test_activate_when_already_active(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        mgr.activate()
        result = mgr.activate()
        assert result["status"] == "already_active"

    def test_deactivate_saves_session(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        mgr.activate()
        result = mgr.deactivate()
        assert result["status"] == "deactivated"
        assert result["duration_minutes"] >= 0
        assert mgr.state == FocusModeState.INACTIVE
        assert mgr.current_session is None

    def test_deactivate_when_not_active(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        result = mgr.deactivate()
        assert result["status"] == "not_active"

    def test_pause_and_resume(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        mgr.activate()
        pause_result = mgr.pause()
        assert pause_result["status"] == "paused"
        assert mgr.state == FocusModeState.PAUSED
        resume_result = mgr.resume()
        assert resume_result["status"] == "resumed"
        assert mgr.state == FocusModeState.ACTIVE


class TestFocusConfiguration:
    """Test focus mode configuration."""

    def test_default_distracting_apps(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        apps = mgr.get_distracting_apps()
        assert "Discord" in apps
        assert "Slack" in apps
        assert "Twitter" in apps

    def test_add_remove_distracting_app(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        mgr.add_distracting_app("MyGame")
        assert "MyGame" in mgr.get_distracting_apps()
        mgr.remove_distracting_app("MyGame")
        assert "MyGame" not in mgr.get_distracting_apps()

    def test_config_persistence(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        mgr.add_distracting_app("PersistentApp")
        # Create new manager instance reading same dir
        mgr2 = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        assert "PersistentApp" in mgr2.get_distracting_apps()


class TestFocusAnalytics:
    """Test focus session analytics."""

    def test_statistics_with_no_sessions(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        stats = mgr.get_statistics(days=7)
        assert stats["total_sessions"] == 0
        assert stats["total_minutes"] == 0

    def test_session_history_persistence(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        mgr.activate(reason="test", trigger="user")
        mgr.deactivate()

        sessions = mgr.get_sessions(days=1)
        assert len(sessions) == 1
        assert sessions[0].reason == "test"

    def test_statistics_after_sessions(self, tmp_path):
        mgr = FocusModeManager(data_dir=tmp_path, backend=StubBackend())
        for _ in range(3):
            mgr.activate()
            mgr.deactivate()
        stats = mgr.get_statistics(days=1)
        assert stats["total_sessions"] == 3
