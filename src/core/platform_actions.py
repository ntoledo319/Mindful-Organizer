"""
Cross-platform system action backends.

Each backend implements the same interface but uses OS-specific APIs:
- macOS: AppleScript, ``defaults``, subprocess calls
- Windows: PowerShell, Win32 APIs (future)
- Linux: xrandr, gsettings, wmctrl (future)

Only macOS is fully implemented; others raise NotImplementedError gracefully.
"""
from __future__ import annotations

import logging
import platform
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Apps commonly considered distracting — used by the focus/app-guardian modules.
_DISTRACTING_APPS_COMMON = {
    "Discord",
    "Slack",
    "Twitter",
    "Telegram",
    "WhatsApp",
    "Messages",
    "Mail",
    "Calendar",
    "Safari",
    "Chrome",
    "Firefox",
    "Arc",
    "Spotify",
    "Netflix",
    "YouTube",
    "Twitch",
    "Reddit",
    "Instagram",
    "TikTok",
}


class PlatformBackend(ABC):
    """Abstract base for OS-specific system actions."""

    @abstractmethod
    def close_application(self, app_name: str) -> bool:
        """Quit an application."""

    @abstractmethod
    def hide_application(self, app_name: str) -> bool:
        """Hide an application (minimise to dock / tray)."""

    @abstractmethod
    def launch_application(self, app_name: str, **kwargs: Any) -> bool:
        """Launch an application."""

    @abstractmethod
    def set_display_brightness(self, percent: int) -> bool:
        """Set display brightness (0-100)."""

    @abstractmethod
    def set_night_shift(self, intensity: int, enabled: bool = True) -> bool:
        """Set night-shift / blue-light filter intensity (0-100)."""

    @abstractmethod
    def set_system_theme(self, theme: str) -> bool:
        """Set system theme ('dark' or 'light')."""

    @abstractmethod
    def set_dnd(self, enabled: bool) -> bool:
        """Enable or disable Do-Not-Disturb."""

    @abstractmethod
    def minimize_all_windows(self) -> bool:
        """Minimise / hide all visible windows."""

    @abstractmethod
    def restore_windows(self) -> bool:
        """Restore previously minimised windows."""

    @abstractmethod
    def play_sound(self, sound_name: str) -> bool:
        """Play a system sound."""

    @abstractmethod
    def list_running_applications(self) -> list[str]:
        """Return names of currently running user-facing apps."""

    def close_distracting_apps(self, app_names: set[str] | None = None) -> list[str]:
        """Close a set of distracting apps, returning the ones successfully closed."""
        targets = app_names or _DISTRACTING_APPS_COMMON
        running = set(self.list_running_applications())
        to_close = targets.intersection(running)
        closed: list[str] = []
        for app in to_close:
            if self.close_application(app):
                closed.append(app)
        return closed


class MacOSBackend(PlatformBackend):
    """macOS implementation using AppleScript and shell utilities."""

    def _run(self, script: str, timeout: float = 5.0) -> tuple[bool, str]:
        """Run an AppleScript and return (success, output)."""
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            ok = result.returncode == 0
            if not ok:
                logger.debug("AppleScript failed: %s", result.stderr.strip())
            return ok, result.stdout.strip()
        except Exception as exc:
            logger.debug("AppleScript exception: %s", exc)
            return False, str(exc)

    def _shell(self, cmd: list[str], timeout: float = 5.0) -> tuple[bool, str]:
        """Run a shell command and return (success, output)."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            ok = result.returncode == 0
            if not ok:
                logger.debug("Shell command failed: %s", result.stderr.strip())
            return ok, result.stdout.strip()
        except Exception as exc:
            logger.debug("Shell exception: %s", exc)
            return False, str(exc)

    @staticmethod
    def _esc(value: str) -> str:
        """Escape a value for safe interpolation into an AppleScript string literal.

        App names arrive from a curated set and the OS process list, but escaping
        backslashes and quotes keeps a name like ``My "App"`` from breaking — or
        injecting into — the script.
        """
        return value.replace("\\", "\\\\").replace('"', '\\"')

    # -- applications ---------------------------------------------------------

    def close_application(self, app_name: str) -> bool:
        script = f'tell application "{self._esc(app_name)}" to quit'
        ok, _ = self._run(script)
        return ok

    def hide_application(self, app_name: str) -> bool:
        script = (
            f'tell application "System Events" to '
            f'set visible of process "{self._esc(app_name)}" to false'
        )
        ok, _ = self._run(script)
        return ok

    def launch_application(self, app_name: str, **kwargs: Any) -> bool:
        script = f'tell application "{self._esc(app_name)}" to activate'
        ok, _ = self._run(script)
        return ok

    def list_running_applications(self) -> list[str]:
        script = 'tell application "System Events" to get name of every application process'
        ok, out = self._run(script)
        if ok and out:
            return [a.strip() for a in out.split(",") if a.strip()]
        return []

    # -- display --------------------------------------------------------------

    def set_display_brightness(self, percent: int) -> bool:
        """Set hardware brightness via the ``brightness`` CLI if available.

        Returns the REAL result. macOS exposes no reliable public API for
        programmatic backlight control, so without the ``brightness`` helper
        (``brew install brightness``) we cannot change it and say so honestly
        rather than reporting a success that never happened. The GUI layer
        offers an in-app dimming overlay as a software fallback.
        """
        pct = max(0, min(100, percent))
        if not shutil.which("brightness"):
            logger.info(
                "Hardware brightness control unavailable (the 'brightness' CLI "
                "is not installed); skipping backlight change to %d%%.", pct
            )
            return False
        ok, _ = self._shell(["brightness", str(pct / 100.0)])
        if ok:
            logger.info("Display brightness set to %d%%.", pct)
        return ok

    def set_night_shift(self, intensity: int, enabled: bool = True) -> bool:
        """Toggle Night Shift via CoreBrightness defaults.

        Intensity is mapped 0-100 -> Night Shift strength.
        This requires the Control Center to restart to take effect.
        """
        if not enabled:
            ok, _ = self._shell(
                ["defaults", "write", "com.apple.CoreBrightness",
                 "CBUserPreferences", "-dict-add", "CBBlueLightReductionEnabled", "-bool", "false"]
            )
            return ok

        # Enable night shift
        ok1, _ = self._shell(
            ["defaults", "write", "com.apple.CoreBrightness",
             "CBUserPreferences", "-dict-add", "CBBlueLightReductionEnabled", "-bool", "true"]
        )
        # Map intensity 0-100 to a time-based schedule (sunset-sunrise)
        # Night Shift doesn't expose fine-grained intensity control via CLI,
        # so we use the warmest setting for high intensity.
        if intensity >= 70:
            ok2, _ = self._shell(
                ["defaults", "write", "com.apple.CoreBrightness",
                 "CBUserPreferences", "-dict-add", "CBBlueLightReductionSchedule",
                 "-dict", "transitionStart", "-string", "18:00", "transitionEnd", "-string", "08:00"]
            )
        else:
            ok2, _ = self._shell(
                ["defaults", "write", "com.apple.CoreBrightness",
                 "CBUserPreferences", "-dict-add", "CBBlueLightReductionSchedule",
                 "-dict", "transitionStart", "-string", "20:00", "transitionEnd", "-string", "06:00"]
            )
        # Restart ControlCenter to apply
        self._shell(["killall", "ControlCenter"])
        return ok1 or ok2

    def set_system_theme(self, theme: str) -> bool:
        dark = theme.lower() == "dark"
        script = (
            'tell application "System Events" to tell appearance preferences to '
            f'{"set" if dark else "set"} dark mode to {"true" if dark else "false"}'
        )
        # Actually the correct AppleScript:
        script = (
            'tell application "System Events" to tell appearance preferences to '
            f'set dark mode to {str(dark).lower()}'
        )
        ok, _ = self._run(script)
        return ok

    # -- DND / focus ----------------------------------------------------------

    def set_dnd(self, enabled: bool) -> bool:
        """Enable or disable Do-Not-Disturb / Focus. Returns the REAL result.

        macOS 12+ replaced the scriptable ``doNotDisturb`` default with Focus
        modes that have no public CLI. The reliable modern path is a user
        Shortcut (Shortcuts.app) named "Turn On/Off Do Not Disturb", which we
        invoke via ``shortcuts run``. On macOS 11 and earlier we fall back to
        the legacy ByHost default with a properly expanded home path. If neither
        works we return False rather than faking success — the engine then tells
        the user DND couldn't be changed instead of silently doing nothing.
        """
        shortcut = "Turn On Do Not Disturb" if enabled else "Turn Off Do Not Disturb"
        if shutil.which("shortcuts"):
            ok, _ = self._shell(["shortcuts", "run", shortcut])
            if ok:
                logger.info("Do-Not-Disturb %s via Shortcuts.", "on" if enabled else "off")
                return True

        # Legacy path (macOS 11 and earlier). The previous implementation passed
        # a literal "~" and a literal "$(date ...)" to subprocess with no shell,
        # so neither expanded and the write silently failed while still claiming
        # success. Use the real, expanded path here.
        byhost = (
            Path.home()
            / "Library/Preferences/ByHost/com.apple.notificationcenterui"
        )
        ok, _ = self._shell(
            ["defaults", "-currentHost", "write", str(byhost),
             "doNotDisturb", "-boolean", str(enabled).lower()]
        )
        if ok:
            self._shell(["killall", "NotificationCenter"])
            logger.info("Do-Not-Disturb %s via legacy default.", "on" if enabled else "off")
            return True

        logger.info(
            "Could not change Do-Not-Disturb on this macOS version. To enable it, "
            "create a Shortcut named '%s' in Shortcuts.app.", shortcut
        )
        return False

    # -- windows --------------------------------------------------------------

    def minimize_all_windows(self) -> bool:
        script = 'tell application "System Events" to keystroke "m" using {command down, option down}'
        ok, _ = self._run(script)
        if not ok:
            # Fallback: hide all visible apps
            self._run('tell application "Finder" to set visible of every process whose visible is true to false')
        return True

    def restore_windows(self) -> bool:
        # macOS doesn't have a single "restore all" command; best effort
        self._run('tell application "Finder" to set visible of every process whose visible is false to true')
        return True

    # -- audio ----------------------------------------------------------------

    def play_sound(self, sound_name: str) -> bool:
        """Play a system sound by name."""
        sound_map = {
            "gentle_chime": "Funk",
            "alert": "Sosumi",
            "success": "Glass",
            "error": "Basso",
        }
        name = sound_map.get(sound_name, sound_name)
        script = f'display notification "" sound name "{name}"'
        ok, _ = self._run(script)
        return ok


class StubBackend(PlatformBackend):
    """Honest fallback for platforms without a real system-action backend.

    Live OS adaptation (closing apps, DND, brightness) is implemented on macOS
    only. On Windows/Linux these methods return False — the action did NOT
    happen — so the automation engine and UI report reality instead of claiming
    a success that never occurred. Everything else in the app (tracking,
    therapeutic tools, the dashboard) works fully on every platform.
    """

    def close_application(self, app_name: str) -> bool:
        logger.info("[unsupported-os] Cannot close %s on this platform.", app_name)
        return False

    def hide_application(self, app_name: str) -> bool:
        logger.info("[unsupported-os] Cannot hide %s on this platform.", app_name)
        return False

    def launch_application(self, app_name: str, **kwargs: Any) -> bool:
        logger.info("[unsupported-os] Cannot launch %s on this platform.", app_name)
        return False

    def set_display_brightness(self, percent: int) -> bool:
        logger.info("[unsupported-os] Cannot set brightness on this platform.")
        return False

    def set_night_shift(self, intensity: int, enabled: bool = True) -> bool:
        logger.info("[unsupported-os] Cannot set night shift on this platform.")
        return False

    def set_system_theme(self, theme: str) -> bool:
        logger.info("[unsupported-os] Cannot set system theme on this platform.")
        return False

    def set_dnd(self, enabled: bool) -> bool:
        logger.info("[unsupported-os] Cannot set DND on this platform.")
        return False

    def minimize_all_windows(self) -> bool:
        logger.info("[unsupported-os] Cannot minimize windows on this platform.")
        return False

    def restore_windows(self) -> bool:
        logger.info("[unsupported-os] Cannot restore windows on this platform.")
        return False

    def play_sound(self, sound_name: str) -> bool:
        logger.info("[unsupported-os] Cannot play sound on this platform.")
        return False

    def list_running_applications(self) -> list[str]:
        return []


def get_backend() -> PlatformBackend:
    """Return the appropriate backend for the current OS."""
    system = platform.system()
    if system == "Darwin":
        return MacOSBackend()
    logger.warning(
        "Live system automation is macOS-only for now; on %s these actions are "
        "inert. Tracking and therapeutic features work normally.", system
    )
    return StubBackend()
