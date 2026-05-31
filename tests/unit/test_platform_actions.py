"""Tests for platform-specific action backends."""
from __future__ import annotations

import platform

from core.platform_actions import MacOSBackend, StubBackend, get_backend


class TestStubBackend:
    """Test the fallback stub backend."""

    def test_stub_close_app_is_honest_failure(self, caplog):
        """On unsupported platforms the stub must report the action did NOT
        happen (False), not fake success — and log why."""
        import logging
        with caplog.at_level(logging.INFO):
            backend = StubBackend()
            result = backend.close_application("TestApp")
            assert result is False
            assert "TestApp" in caplog.text

    def test_stub_set_brightness_is_honest_failure(self, caplog):
        import logging
        with caplog.at_level(logging.INFO):
            backend = StubBackend()
            result = backend.set_display_brightness(50)
            assert result is False
            assert "brightness" in caplog.text.lower()

    def test_stub_list_running_returns_empty(self):
        backend = StubBackend()
        assert backend.list_running_applications() == []

    def test_stub_close_distracting_apps_returns_empty(self):
        backend = StubBackend()
        closed = backend.close_distracting_apps({"Discord", "Slack"})
        assert closed == []


class _FakeProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class TestMacOSBackendBehavior:
    """Behavioural coverage for the REAL macOS backend.

    The product's core promise is acting on the desktop; previously only the
    no-op StubBackend was tested. These mock subprocess and assert the actual
    commands built and that failures/escaping are handled honestly.
    """

    def _capture(self, monkeypatch, returncode=0, stdout=""):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return _FakeProc(returncode=returncode, stdout=stdout)

        monkeypatch.setattr("core.platform_actions.subprocess.run", fake_run)
        return calls

    def test_close_application_builds_quit_script(self, monkeypatch):
        calls = self._capture(monkeypatch)
        assert MacOSBackend().close_application("Discord") is True
        assert calls and calls[0][:2] == ["osascript", "-e"]
        assert calls[0][2] == 'tell application "Discord" to quit'

    def test_app_name_is_escaped_against_injection(self, monkeypatch):
        calls = self._capture(monkeypatch)
        MacOSBackend().close_application('Evil" to quit\ntell application "Finder')
        script = calls[0][2]
        # The embedded quote must be escaped, not left to break out of the literal.
        assert '\\"' in script

    def test_close_application_reports_real_failure(self, monkeypatch):
        self._capture(monkeypatch, returncode=1)
        assert MacOSBackend().close_application("Discord") is False

    def test_brightness_false_without_cli(self, monkeypatch):
        monkeypatch.setattr("core.platform_actions.shutil.which", lambda _name: None)
        assert MacOSBackend().set_display_brightness(40) is False

    def test_brightness_true_with_cli(self, monkeypatch):
        monkeypatch.setattr(
            "core.platform_actions.shutil.which", lambda _name: "/usr/local/bin/brightness"
        )
        self._capture(monkeypatch, returncode=0)
        assert MacOSBackend().set_display_brightness(40) is True

    def test_dnd_false_when_nothing_available(self, monkeypatch):
        # No shortcuts CLI, and the legacy defaults write fails.
        monkeypatch.setattr("core.platform_actions.shutil.which", lambda _name: None)
        self._capture(monkeypatch, returncode=1)
        assert MacOSBackend().set_dnd(True) is False

    def test_dnd_true_via_shortcuts(self, monkeypatch):
        monkeypatch.setattr(
            "core.platform_actions.shutil.which",
            lambda name: "/usr/bin/shortcuts" if name == "shortcuts" else None,
        )
        calls = self._capture(monkeypatch, returncode=0)
        assert MacOSBackend().set_dnd(True) is True
        assert calls[0][0] == "shortcuts" and calls[0][1] == "run"

    def test_minimize_and_restore_report_real_failure(self, monkeypatch):
        self._capture(monkeypatch, returncode=1)  # every AppleScript fails
        assert MacOSBackend().minimize_all_windows() is False
        assert MacOSBackend().restore_windows() is False

    def test_minimize_reports_success_when_applescript_succeeds(self, monkeypatch):
        self._capture(monkeypatch, returncode=0)
        assert MacOSBackend().minimize_all_windows() is True
        assert MacOSBackend().restore_windows() is True


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
