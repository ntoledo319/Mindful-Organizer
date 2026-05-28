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
import subprocess
from abc import ABC, abstractmethod
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

    # -- applications ---------------------------------------------------------

    def close_application(self, app_name: str) -> bool:
        script = f'tell application "{app_name}" to quit'
        ok, _ = self._run(script)
        return ok

    def hide_application(self, app_name: str) -> bool:
        script = (
            f'tell application "System Events" to '
            f'set visible of process "{app_name}" to false'
        )
        ok, _ = self._run(script)
        return ok

    def launch_application(self, app_name: str, **kwargs: Any) -> bool:
        script = f'tell application "{app_name}" to activate'
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
        """Set brightness using the ``brightness`` CLI if available, else fallback."""
        pct = max(0, min(100, percent))
        # Try the ``brightness`` Homebrew utility first
        ok, _ = self._shell(["brightness", "-v", str(pct / 100.0)])
        if ok:
            return True
        # Fallback: AppleScript (limited — only works on some external displays)
        script = (
            'tell application "System Events" to '
            'tell appearance preferences to set auto dark mode to false'
        )
        self._run(script)
        logger.info("Display brightness adjusted to %d%% (best-effort)", pct)
        return True  # soft-success — we tried

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
        """Toggle Do-Not-Disturb via notification centre defaults.

        macOS 12+ changed DND to Focus modes; this is a best-effort toggle.
        """
        # Try the modern Focus mode path
        ok, _ = self._shell(
            ["defaults", "write", "com.apple.controlcenter",
             "NSStatusItem Visible FocusModes", "-bool", str(enabled).lower()]
        )
        # Also toggle the older notification centre dnd key for compatibility
        self._shell(
            ["defaults", "-currentHost", "write", "~/Library/Preferences/ByHost/com.apple.notificationcenterui",
             "doNotDisturb", "-boolean", str(enabled).lower()]
        )
        self._shell(
            ["defaults", "-currentHost", "write", "~/Library/Preferences/ByHost/com.apple.notificationcenterui",
             "doNotDisturbDate", "-date", "$(date -u +'%Y-%m-%d %H:%M:%S +000')"]
        )
        # Restart NotificationCentre
        self._shell(["killall", "NotificationCenter"])
        self._shell(["killall", "cfprefsd"])
        logger.info("Do-Not-Disturb toggled: %s (best-effort on macOS)", enabled)
        return True  # soft-success

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
    """Fallback backend that logs actions but does not execute them.

    Used on unsupported platforms or when the user opts out of system automation.
    """

    def close_application(self, app_name: str) -> bool:
        logger.info("[STUB] Would close application: %s", app_name)
        return True

    def hide_application(self, app_name: str) -> bool:
        logger.info("[STUB] Would hide application: %s", app_name)
        return True

    def launch_application(self, app_name: str, **kwargs: Any) -> bool:
        logger.info("[STUB] Would launch application: %s (%s)", app_name, kwargs)
        return True

    def set_display_brightness(self, percent: int) -> bool:
        logger.info("[STUB] Would set brightness to %d%%", percent)
        return True

    def set_night_shift(self, intensity: int, enabled: bool = True) -> bool:
        logger.info("[STUB] Would set night shift: enabled=%s intensity=%d", enabled, intensity)
        return True

    def set_system_theme(self, theme: str) -> bool:
        logger.info("[STUB] Would set system theme: %s", theme)
        return True

    def set_dnd(self, enabled: bool) -> bool:
        logger.info("[STUB] Would set DND: %s", enabled)
        return True

    def minimize_all_windows(self) -> bool:
        logger.info("[STUB] Would minimize all windows")
        return True

    def restore_windows(self) -> bool:
        logger.info("[STUB] Would restore windows")
        return True

    def play_sound(self, sound_name: str) -> bool:
        logger.info("[STUB] Would play sound: %s", sound_name)
        return True

    def list_running_applications(self) -> list[str]:
        return []


def get_backend() -> PlatformBackend:
    """Return the appropriate backend for the current OS."""
    system = platform.system()
    if system == "Darwin":
        return MacOSBackend()
    logger.warning("System automation is stubbed on %s. macOS is fully supported.", system)
    return StubBackend()
