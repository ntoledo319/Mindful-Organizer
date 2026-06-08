"""Tests for cross-platform utilities in windows.platform_utils."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from windows.platform_utils import (
    OperatingSystem,
    PlatformInfo,
    SingleInstance,
    SystemTheme,
    configure_high_dpi,
    detect_os,
    get_config_dir,
    get_data_dir,
    get_log_dir,
    get_platform_info,
    get_scale_factor,
    get_system_theme,
    is_high_dpi,
    is_registered_for_startup,
    register_startup,
    send_desktop_notification,
    system_tray_supported,
)


class _FakeProc:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------


class TestDetectOS:
    def test_macos(self, monkeypatch):
        monkeypatch.setattr("platform.system", lambda: "Darwin")
        assert detect_os() == OperatingSystem.MACOS

    def test_windows(self, monkeypatch):
        monkeypatch.setattr("platform.system", lambda: "Windows")
        assert detect_os() == OperatingSystem.WINDOWS

    def test_linux(self, monkeypatch):
        monkeypatch.setattr("platform.system", lambda: "Linux")
        assert detect_os() == OperatingSystem.LINUX

    def test_unknown(self, monkeypatch):
        monkeypatch.setattr("platform.system", lambda: "FreeBSD")
        assert detect_os() == OperatingSystem.UNKNOWN


# ---------------------------------------------------------------------------
# Data directories
# ---------------------------------------------------------------------------


class TestDataDir:
    def test_returns_path(self, monkeypatch, tmp_path):
        fake = tmp_path / "data"
        monkeypatch.setattr("core.paths.get_data_dir", lambda create=True: fake)
        result = get_data_dir()
        assert isinstance(result, Path)
        assert result == fake

    def test_creates_directory(self, monkeypatch, tmp_path):
        fake = tmp_path / "new_data"
        assert not fake.exists()

        def _fake(create=True):
            if create:
                fake.mkdir(parents=True, exist_ok=True)
            return fake

        monkeypatch.setattr("core.paths.get_data_dir", _fake)
        result = get_data_dir()
        assert result.exists()
        assert result.is_dir()


class TestConfigAndLogDir:
    def test_get_config_dir_creates_path(self, monkeypatch, tmp_path):
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr("windows.platform_utils.Path.home", lambda: home)
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.MACOS)
        result = get_config_dir()
        assert isinstance(result, Path)
        assert result.exists()
        assert "Preferences" in str(result)

    def test_get_log_dir_creates_path(self, monkeypatch, tmp_path):
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr("windows.platform_utils.Path.home", lambda: home)
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.MACOS)
        result = get_log_dir()
        assert isinstance(result, Path)
        assert result.exists()
        assert "Logs" in str(result)


# ---------------------------------------------------------------------------
# Theme detection
# ---------------------------------------------------------------------------


class TestSystemTheme:
    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_dark(self, monkeypatch):
        monkeypatch.setattr(
            "windows.platform_utils.subprocess.run",
            lambda *a, **k: _FakeProc(returncode=0, stdout="Dark"),
        )
        assert get_system_theme() == SystemTheme.DARK

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_light(self, monkeypatch):
        monkeypatch.setattr(
            "windows.platform_utils.subprocess.run",
            lambda *a, **k: _FakeProc(returncode=0, stdout=""),
        )
        assert get_system_theme() == SystemTheme.LIGHT

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_unknown_on_error(self, monkeypatch):
        monkeypatch.setattr(
            "windows.platform_utils.subprocess.run",
            lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError),
        )
        assert get_system_theme() == SystemTheme.UNKNOWN

    def test_windows_theme_dark(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.WINDOWS)
        fake_winreg = MagicMock()
        fake_winreg.OpenKey.return_value = MagicMock()
        fake_winreg.QueryValueEx.return_value = (0, None)
        monkeypatch.setitem(sys.modules, "winreg", fake_winreg)
        assert get_system_theme() == SystemTheme.DARK

    def test_linux_theme_gsettings(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.LINUX)
        monkeypatch.setattr(
            "windows.platform_utils.subprocess.run",
            lambda *a, **k: _FakeProc(returncode=0, stdout="'prefer-dark'"),
        )
        assert get_system_theme() == SystemTheme.DARK


# ---------------------------------------------------------------------------
# Scale / DPI
# ---------------------------------------------------------------------------


class TestScaleFactor:
    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_retina(self, monkeypatch):
        monkeypatch.setattr(
            "windows.platform_utils.subprocess.run",
            lambda *a, **k: _FakeProc(returncode=0, stdout="Retina: Yes"),
        )
        assert get_scale_factor() == 2.0

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_non_retina(self, monkeypatch):
        monkeypatch.setattr(
            "windows.platform_utils.subprocess.run",
            lambda *a, **k: _FakeProc(returncode=0, stdout="Standard Display"),
        )
        assert get_scale_factor() == 1.0

    def test_linux_gdk_scale(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.LINUX)
        monkeypatch.setenv("GDK_SCALE", "1.5")
        assert get_scale_factor() == 1.5

    def test_is_high_dpi_true(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.get_scale_factor", lambda: 2.0)
        assert is_high_dpi() is True

    def test_is_high_dpi_false(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.get_scale_factor", lambda: 1.0)
        assert is_high_dpi() is False

    def test_configure_high_dpi(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.get_scale_factor", lambda: 2.0)
        import os

        for var in (
            "QT_ENABLE_HIGHDPI_SCALING",
            "QT_SCALE_FACTOR_ROUNDING_POLICY",
            "QT_SCALE_FACTOR",
        ):
            os.environ.pop(var, None)

        configure_high_dpi()
        assert os.environ.get("QT_ENABLE_HIGHDPI_SCALING") == "1"
        assert os.environ.get("QT_SCALE_FACTOR_ROUNDING_POLICY") == "PassThrough"
        assert os.environ.get("QT_SCALE_FACTOR") == "2.0"


# ---------------------------------------------------------------------------
# System tray
# ---------------------------------------------------------------------------


class TestSystemTray:
    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_supported_on_macos(self):
        assert system_tray_supported() is True

    def test_supported_on_linux_with_desktop(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.LINUX)
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")
        assert system_tray_supported() is True

    def test_supported_on_linux_via_dbus(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.LINUX)
        monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)
        monkeypatch.setattr(
            "windows.platform_utils.subprocess.run",
            lambda *a, **k: _FakeProc(returncode=0),
        )
        assert system_tray_supported() is True


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


class TestNotifications:
    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_success(self, monkeypatch):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return _FakeProc(returncode=0)

        monkeypatch.setattr("windows.platform_utils.subprocess.run", fake_run)
        assert send_desktop_notification("Title", "Message") is True
        assert calls[0][0] == "osascript"

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_failure(self, monkeypatch):
        monkeypatch.setattr(
            "windows.platform_utils.subprocess.run",
            lambda *a, **k: _FakeProc(returncode=1),
        )
        assert send_desktop_notification("Title", "Message") is False

    def test_linux_notification(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.LINUX)
        monkeypatch.setattr(
            "windows.platform_utils.subprocess.run",
            lambda *a, **k: _FakeProc(returncode=0),
        )
        assert send_desktop_notification("Title", "Message") is True

    def test_windows_notification_fallback(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.WINDOWS)
        monkeypatch.setitem(sys.modules, "win10toast", None)
        monkeypatch.setitem(sys.modules, "winotify", None)
        assert send_desktop_notification("Title", "Message") is False


# ---------------------------------------------------------------------------
# Startup registration
# ---------------------------------------------------------------------------


class TestStartup:
    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_register_startup_macos(self, monkeypatch, tmp_path):
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr("windows.platform_utils.Path.home", lambda: home)
        assert register_startup("/usr/local/bin/python", enabled=True) is True
        plist = home / "Library" / "LaunchAgents" / "com.mindfulorganizer.app.plist"
        assert plist.exists()

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_unregister_startup_macos(self, monkeypatch, tmp_path):
        home = tmp_path / "home"
        home.mkdir()
        plist = home / "Library" / "LaunchAgents" / "com.mindfulorganizer.app.plist"
        plist.parent.mkdir(parents=True, exist_ok=True)
        plist.write_text("old", encoding="utf-8")
        monkeypatch.setattr("windows.platform_utils.Path.home", lambda: home)
        assert register_startup(enabled=False) is True
        assert not plist.exists()

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_is_registered_for_startup_macos(self, monkeypatch, tmp_path):
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr("windows.platform_utils.Path.home", lambda: home)
        assert is_registered_for_startup() is False
        plist = home / "Library" / "LaunchAgents" / "com.mindfulorganizer.app.plist"
        plist.parent.mkdir(parents=True, exist_ok=True)
        plist.write_text("plist", encoding="utf-8")
        assert is_registered_for_startup() is True

    def test_register_startup_linux(self, monkeypatch, tmp_path):
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr("windows.platform_utils.Path.home", lambda: home)
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.LINUX)
        assert register_startup("/usr/bin/python", enabled=True) is True
        desktop = home / ".config" / "autostart" / "mindful-organizer.desktop"
        assert desktop.exists()

    def test_register_startup_windows(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.WINDOWS)
        fake_winreg = MagicMock()
        fake_winreg.OpenKey.return_value = MagicMock()
        monkeypatch.setitem(sys.modules, "winreg", fake_winreg)
        assert register_startup("C:\\app.exe", enabled=True) is True
        fake_winreg.OpenKey.assert_called_once()

    def test_is_registered_for_startup_windows(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.WINDOWS)
        fake_winreg = MagicMock()
        fake_key = MagicMock()
        fake_winreg.OpenKey.return_value = fake_key
        fake_winreg.QueryValueEx.side_effect = FileNotFoundError
        monkeypatch.setitem(sys.modules, "winreg", fake_winreg)
        assert is_registered_for_startup() is False


# ---------------------------------------------------------------------------
# Single instance
# ---------------------------------------------------------------------------


class TestSingleInstance:
    def test_acquire_and_release_posix(self, monkeypatch, tmp_path):
        monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
        instance = SingleInstance(app_id="test-hearth-unique")
        assert instance.acquire() is True
        assert instance._lock_handle is not None
        instance.release()
        assert instance._lock_handle is None

    def test_already_running(self, monkeypatch, tmp_path):
        monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
        app_id = "test-hearth-running"
        first = SingleInstance(app_id=app_id)
        assert first.acquire() is True
        second = SingleInstance(app_id=app_id)
        assert second.acquire() is False
        first.release()

    def test_context_manager(self, monkeypatch, tmp_path):
        monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
        with SingleInstance(app_id="test-ctx") as inst:
            assert inst._lock_handle is not None

    def test_windows_acquire(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.WINDOWS)
        mock_kernel32 = MagicMock()
        mock_kernel32.CreateMutexW.return_value = 12345
        mock_windll = MagicMock()
        mock_windll.kernel32 = mock_kernel32
        import ctypes

        monkeypatch.setattr(ctypes, "windll", mock_windll, raising=False)
        monkeypatch.setattr(ctypes, "GetLastError", lambda: 0, raising=False)
        instance = SingleInstance(app_id="test-win")
        assert instance.acquire() is True
        mock_kernel32.CreateMutexW.assert_called_once()

    def test_windows_release(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.WINDOWS)
        mock_kernel32 = MagicMock()
        mock_windll = MagicMock()
        mock_windll.kernel32 = mock_kernel32
        import ctypes

        monkeypatch.setattr(ctypes, "windll", mock_windll, raising=False)
        monkeypatch.setattr(ctypes, "GetLastError", lambda: 0, raising=False)
        instance = SingleInstance(app_id="test-win")
        instance.acquire()
        instance.release()
        mock_kernel32.CloseHandle.assert_called_once()


# ---------------------------------------------------------------------------
# Platform snapshot
# ---------------------------------------------------------------------------


class TestPlatformInfo:
    def test_returns_snapshot(self, monkeypatch):
        monkeypatch.setattr("windows.platform_utils.detect_os", lambda: OperatingSystem.MACOS)
        monkeypatch.setattr("windows.platform_utils.get_system_theme", lambda: SystemTheme.DARK)
        monkeypatch.setattr("windows.platform_utils.get_scale_factor", lambda: 1.0)
        monkeypatch.setattr("windows.platform_utils.system_tray_supported", lambda: True)
        monkeypatch.setattr("windows.platform_utils.get_data_dir", lambda: Path("/tmp/data"))
        info = get_platform_info()
        assert isinstance(info, PlatformInfo)
        assert info.os == OperatingSystem.MACOS
        assert info.theme == SystemTheme.DARK
        assert isinstance(info.os_version, str)
        assert isinstance(info.architecture, str)
        assert isinstance(info.hostname, str)
        assert info.scale_factor == 1.0
        assert info.system_tray_supported is True
