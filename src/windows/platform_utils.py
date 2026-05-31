"""
Cross-platform utilities for Mindful Organizer.

Provides OS detection, platform-specific data paths, theme detection,
high-DPI handling, notification integration, system tray support,
startup registration, and single-instance enforcement.
"""

import contextlib
import ctypes
import logging
import os
import platform
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums & data classes
# ---------------------------------------------------------------------------

class OperatingSystem(Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


class SystemTheme(Enum):
    LIGHT = "light"
    DARK = "dark"
    UNKNOWN = "unknown"


@dataclass
class PlatformInfo:
    """Snapshot of the current platform environment."""
    os: OperatingSystem
    os_version: str
    architecture: str
    hostname: str
    data_dir: Path
    theme: SystemTheme
    high_dpi: bool
    scale_factor: float
    system_tray_supported: bool


# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------

def detect_os() -> OperatingSystem:
    """Return the current operating system."""
    name = platform.system().lower()
    return {
        "windows": OperatingSystem.WINDOWS,
        "darwin": OperatingSystem.MACOS,
        "linux": OperatingSystem.LINUX,
    }.get(name, OperatingSystem.UNKNOWN)


# ---------------------------------------------------------------------------
# Data directory
# ---------------------------------------------------------------------------

def get_data_dir() -> Path:
    """Return the canonical application data directory.

    Delegates to :mod:`core.paths` so every component — main.py, the database
    layer, and the GUI — agrees on a single location and never splits data.

    - Windows:  ``%APPDATA%/.mindful_organizer``
    - macOS:    ``~/Library/Application Support/.mindful_organizer``
    - Linux:    ``~/.mindful_organizer``
    """
    from core.paths import get_data_dir as _canonical

    return _canonical()


def get_config_dir() -> Path:
    """Return the platform-appropriate configuration directory."""
    current_os = detect_os()
    if current_os == OperatingSystem.WINDOWS:
        return get_data_dir()
    elif current_os == OperatingSystem.MACOS:
        config = Path.home() / "Library" / "Preferences" / "MindfulOrganizer"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        if xdg:
            config = Path(xdg) / "mindful_organizer"
        else:
            config = Path.home() / ".config" / "mindful_organizer"
    config.mkdir(parents=True, exist_ok=True)
    return config


def get_log_dir() -> Path:
    """Return the platform-appropriate log directory."""
    current_os = detect_os()
    if current_os == OperatingSystem.WINDOWS:
        return get_data_dir() / "logs"
    elif current_os == OperatingSystem.MACOS:
        log_dir = Path.home() / "Library" / "Logs" / "MindfulOrganizer"
    else:
        log_dir = get_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


# ---------------------------------------------------------------------------
# Theme detection
# ---------------------------------------------------------------------------

def get_system_theme() -> SystemTheme:
    """Detect the operating system's light/dark theme setting."""
    current_os = detect_os()

    if current_os == OperatingSystem.WINDOWS:
        return _windows_theme()
    elif current_os == OperatingSystem.MACOS:
        return _macos_theme()
    elif current_os == OperatingSystem.LINUX:
        return _linux_theme()
    return SystemTheme.UNKNOWN


def _windows_theme() -> SystemTheme:
    """Read the Windows registry for AppsUseLightTheme."""
    try:
        import winreg
        key = winreg.OpenKey(  # type: ignore[attr-defined]
            winreg.HKEY_CURRENT_USER,  # type: ignore[attr-defined]
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")  # type: ignore[attr-defined]
        winreg.CloseKey(key)  # type: ignore[attr-defined]
        return SystemTheme.LIGHT if value == 1 else SystemTheme.DARK
    except (OSError, ImportError):
        return SystemTheme.UNKNOWN


def _macos_theme() -> SystemTheme:
    """Use ``defaults read`` to check macOS appearance."""
    try:
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and "dark" in result.stdout.lower():
            return SystemTheme.DARK
        return SystemTheme.LIGHT
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return SystemTheme.UNKNOWN


def _linux_theme() -> SystemTheme:
    """Attempt to read GTK or KDE theme preference."""
    # Try GTK
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            if "dark" in result.stdout.lower():
                return SystemTheme.DARK
            return SystemTheme.LIGHT
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    # Try KDE
    try:
        result = subprocess.run(
            ["kreadconfig5", "--group", "General", "--key", "ColorScheme"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and "dark" in result.stdout.lower():
            return SystemTheme.DARK
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    return SystemTheme.UNKNOWN


# ---------------------------------------------------------------------------
# High DPI
# ---------------------------------------------------------------------------

def get_scale_factor() -> float:
    """Detect the display scale factor.

    Returns 1.0 for standard DPI, >1.0 for high-DPI displays.
    """
    current_os = detect_os()

    if current_os == OperatingSystem.WINDOWS:
        try:
            user32 = ctypes.windll.user32  # type: ignore[attr-defined]
            user32.SetProcessDPIAware()
            dc = user32.GetDC(0)
            gdi32 = ctypes.windll.gdi32  # type: ignore[attr-defined]
            logpixelsx = 88
            dpi = gdi32.GetDeviceCaps(dc, logpixelsx)
            user32.ReleaseDC(0, dc)
            return float(dpi) / 96.0
        except (OSError, ImportError, AttributeError):
            return 1.0

    elif current_os == OperatingSystem.MACOS:
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if "Retina" in result.stdout:
                return 2.0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
        return 1.0

    else:
        # Linux: check GDK_SCALE or Xft.dpi
        gdk_scale = os.environ.get("GDK_SCALE")
        if gdk_scale:
            try:
                return float(gdk_scale)
            except ValueError:
                pass
        try:
            result = subprocess.run(
                ["xrdb", "-query"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            for line in result.stdout.splitlines():
                if "Xft.dpi" in line:
                    dpi = float(line.split(":")[-1].strip())
                    return dpi / 96.0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError, ValueError):
            pass
        return 1.0


def is_high_dpi() -> bool:
    """Return True if the display is high-DPI (scale > 1.0)."""
    return get_scale_factor() > 1.0


def configure_high_dpi() -> None:
    """Configure Qt for high-DPI scaling. Call before QApplication creation."""
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")
    scale = get_scale_factor()
    if scale > 1.0:
        os.environ.setdefault("QT_SCALE_FACTOR", str(scale))
        logger.info("High DPI detected (scale %.2f); QT_SCALE_FACTOR set", scale)


# ---------------------------------------------------------------------------
# System tray
# ---------------------------------------------------------------------------

def system_tray_supported() -> bool:
    """Check whether the desktop environment supports a system tray."""
    current_os = detect_os()
    if current_os in (OperatingSystem.WINDOWS, OperatingSystem.MACOS):
        return True
    # Linux: check for common tray protocols
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if any(de in desktop for de in ("gnome", "kde", "xfce", "cinnamon", "mate", "lxde", "lxqt")):
        return True
    # Fallback: try to detect via DBus
    try:
        result = subprocess.run(
            ["dbus-send", "--session", "--print-reply",
             "--dest=org.kde.StatusNotifierWatcher",
             "/StatusNotifierWatcher",
             "org.freedesktop.DBus.Properties.Get",
             "string:org.kde.StatusNotifierWatcher",
             "string:IsStatusNotifierHostRegistered"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


# ---------------------------------------------------------------------------
# Desktop notifications
# ---------------------------------------------------------------------------

def send_desktop_notification(
    title: str,
    message: str,
    icon_path: str | None = None,
    timeout: int = 5,
) -> bool:
    """Send a native desktop notification. Returns True on success.

    Falls back gracefully if the required libraries are unavailable.
    """
    current_os = detect_os()

    if current_os == OperatingSystem.WINDOWS:
        return _windows_notification(title, message, icon_path, timeout)
    elif current_os == OperatingSystem.MACOS:
        return _macos_notification(title, message)
    elif current_os == OperatingSystem.LINUX:
        return _linux_notification(title, message, icon_path, timeout)
    return False


def _windows_notification(
    title: str, message: str, icon_path: str | None, timeout: int,
) -> bool:
    """Try win10toast, then winotify, then fall back to a basic messagebox."""
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, icon_path=icon_path, duration=timeout, threaded=True)
        return True
    except ImportError:
        pass

    try:
        from winotify import Notification as WinNotification
        toast = WinNotification(app_id="Mindful Organizer", title=title, msg=message)
        toast.show()
        return True
    except ImportError:
        pass

    logger.debug("Windows notification fallback: using in-app display")
    return False


def _macos_notification(title: str, message: str) -> bool:
    # Escape backslashes and double-quotes so a title/message can't break out of
    # the AppleScript string literal (latent osascript injection).
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    try:
        script = (
            f'display notification "{esc(message)}" with title "{esc(title)}" '
            f'sound name "default"'
        )
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def _linux_notification(
    title: str, message: str, icon_path: str | None, timeout: int,
) -> bool:
    try:
        cmd = ["notify-send", title, message, "-t", str(timeout * 1000)]
        if icon_path:
            cmd.extend(["-i", icon_path])
        subprocess.run(cmd, capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


# ---------------------------------------------------------------------------
# Startup registration
# ---------------------------------------------------------------------------

_APP_NAME = "MindfulOrganizer"


def register_startup(
    executable_path: str | None = None,
    enabled: bool = True,
) -> bool:
    """Register or unregister the app to launch at system login.

    Returns True on success.
    """
    if executable_path is None:
        executable_path = sys.executable
    current_os = detect_os()

    if current_os == OperatingSystem.WINDOWS:
        return _windows_startup(executable_path, enabled)
    elif current_os == OperatingSystem.MACOS:
        return _macos_startup(executable_path, enabled)
    elif current_os == OperatingSystem.LINUX:
        return _linux_startup(executable_path, enabled)
    return False


def _windows_startup(exe: str, enabled: bool) -> bool:
    try:
        import winreg
        key = winreg.OpenKey(  # type: ignore[attr-defined]
            winreg.HKEY_CURRENT_USER,  # type: ignore[attr-defined]
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE,  # type: ignore[attr-defined]
        )
        if enabled:
            winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, f'"{exe}"')  # type: ignore[attr-defined]
        else:
            with contextlib.suppress(FileNotFoundError):
                winreg.DeleteValue(key, _APP_NAME)  # type: ignore[attr-defined]
        winreg.CloseKey(key)  # type: ignore[attr-defined]
        return True
    except (OSError, ImportError) as exc:
        logger.warning("Windows startup registration failed: %s", exc)
        return False


def _macos_startup(exe: str, enabled: bool) -> bool:
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_path = plist_dir / "com.mindfulorganizer.app.plist"

    if not enabled:
        if plist_path.exists():
            plist_path.unlink()
        return True

    plist_dir.mkdir(parents=True, exist_ok=True)
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mindfulorganizer.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
    plist_path.write_text(plist_content, encoding="utf-8")
    return True


def _linux_startup(exe: str, enabled: bool) -> bool:
    autostart_dir = Path.home() / ".config" / "autostart"
    desktop_path = autostart_dir / "mindful-organizer.desktop"

    if not enabled:
        if desktop_path.exists():
            desktop_path.unlink()
        return True

    autostart_dir.mkdir(parents=True, exist_ok=True)
    desktop_entry = f"""[Desktop Entry]
Type=Application
Name=Mindful Organizer
Exec={exe}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Mental health-focused productivity app
"""
    desktop_path.write_text(desktop_entry, encoding="utf-8")
    return True


def is_registered_for_startup() -> bool:
    """Check whether the app is registered to start at login."""
    current_os = detect_os()

    if current_os == OperatingSystem.WINDOWS:
        try:
            import winreg
            key = winreg.OpenKey(  # type: ignore[attr-defined]
                winreg.HKEY_CURRENT_USER,  # type: ignore[attr-defined]
                r"Software\Microsoft\Windows\CurrentVersion\Run",
            )
            try:
                winreg.QueryValueEx(key, _APP_NAME)  # type: ignore[attr-defined]
                winreg.CloseKey(key)  # type: ignore[attr-defined]
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)  # type: ignore[attr-defined]
                return False
        except (OSError, ImportError):
            return False
    elif current_os == OperatingSystem.MACOS:
        return (Path.home() / "Library" / "LaunchAgents" / "com.mindfulorganizer.app.plist").exists()
    elif current_os == OperatingSystem.LINUX:
        return (Path.home() / ".config" / "autostart" / "mindful-organizer.desktop").exists()
    return False


# ---------------------------------------------------------------------------
# Single instance enforcement
# ---------------------------------------------------------------------------

class SingleInstance:
    """Prevents multiple instances of the application from running.

    Usage::

        instance = SingleInstance()
        if not instance.acquire():
            sys.exit("Another instance is already running.")
        # ... run app ...
        instance.release()
    """

    def __init__(self, app_id: str = "mindful-organizer") -> None:
        self._app_id = app_id
        self._lock_file: Path | None = None
        self._lock_handle: Any = None
        self._current_os = detect_os()

    def acquire(self) -> bool:
        """Try to acquire the single-instance lock. Returns True on success."""
        if self._current_os == OperatingSystem.WINDOWS:
            return self._acquire_windows()
        return self._acquire_posix()

    def release(self) -> None:
        """Release the single-instance lock."""
        if self._current_os == OperatingSystem.WINDOWS:
            self._release_windows()
        else:
            self._release_posix()

    def _acquire_windows(self) -> bool:
        try:
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            mutex_name = f"Global\\{self._app_id}"
            handle = kernel32.CreateMutexW(None, False, mutex_name)
            error_already_exists = 183
            last_error = ctypes.GetLastError()  # type: ignore
            if last_error == error_already_exists:
                kernel32.CloseHandle(handle)
                return False
            self._lock_handle = handle
            return True
        except (OSError, ImportError, AttributeError):
            return True  # Fail open

    def _release_windows(self) -> None:
        if self._lock_handle is not None:
            with contextlib.suppress(OSError, AttributeError):
                ctypes.windll.kernel32.CloseHandle(self._lock_handle)  # type: ignore[attr-defined]
            self._lock_handle = None

    def _acquire_posix(self) -> bool:
        self._lock_file = Path(tempfile.gettempdir()) / f"{self._app_id}.lock"
        try:
            import fcntl
            self._lock_handle = self._lock_file.open("w")
            fcntl.flock(self._lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._lock_handle.write(str(os.getpid()))
            self._lock_handle.flush()
            return True
        except OSError:
            return False
        except ImportError:
            # fcntl unavailable (shouldn't happen on POSIX)
            return True

    def _release_posix(self) -> None:
        if self._lock_handle is not None:
            with contextlib.suppress(OSError, ValueError):
                import fcntl
                fcntl.flock(self._lock_handle, fcntl.LOCK_UN)
                self._lock_handle.close()
            self._lock_handle = None
        if self._lock_file and self._lock_file.exists():
            with contextlib.suppress(OSError):
                self._lock_file.unlink()

    def __enter__(self) -> "SingleInstance":
        if not self.acquire():
            raise RuntimeError("Another instance of Mindful Organizer is already running.")
        return self

    def __exit__(self, *args: Any) -> None:
        self.release()


# ---------------------------------------------------------------------------
# Convenience: full platform snapshot
# ---------------------------------------------------------------------------

def get_platform_info() -> PlatformInfo:
    """Collect a complete snapshot of the current platform environment."""
    return PlatformInfo(
        os=detect_os(),
        os_version=platform.version(),
        architecture=platform.machine(),
        hostname=platform.node(),
        data_dir=get_data_dir(),
        theme=get_system_theme(),
        high_dpi=is_high_dpi(),
        scale_factor=get_scale_factor(),
        system_tray_supported=system_tray_supported(),
    )
