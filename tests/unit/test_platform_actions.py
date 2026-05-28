"""Tests for platform-specific action backends."""
from __future__ import annotations

import platform

from core.platform_actions import MacOSBackend, StubBackend, get_backend


class TestStubBackend:
    """Test the fallback stub backend."""

    def test_stub_close_app_logs(self, caplog):
        import logging
        with caplog.at_level(logging.INFO):
            backend = StubBackend()
            result = backend.close_application("TestApp")
            assert result is True
            assert "Would close application: TestApp" in caplog.text

    def test_stub_set_brightness_logs(self, caplog):
        import logging
        with caplog.at_level(logging.INFO):
            backend = StubBackend()
            result = backend.set_display_brightness(50)
            assert result is True
            assert "Would set brightness to 50%" in caplog.text

    def test_stub_list_running_returns_empty(self):
        backend = StubBackend()
        assert backend.list_running_applications() == []

    def test_stub_close_distracting_apps_returns_empty(self):
        backend = StubBackend()
        closed = backend.close_distracting_apps({"Discord", "Slack"})
        assert closed == []


class TestGetBackend:
    """Test backend selection."""

    def test_returns_macos_on_darwin(self, monkeypatch):
        monkeypatch.setattr(platform, "system", lambda: "Darwin")
        backend = get_backend()
        assert isinstance(backend, MacOSBackend)

    def test_returns_stub_on_linux(self, monkeypatch):
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        backend = get_backend()
        assert isinstance(backend, StubBackend)

    def test_returns_stub_on_windows(self, monkeypatch):
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        backend = get_backend()
        assert isinstance(backend, StubBackend)
