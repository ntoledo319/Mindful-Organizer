"""
Global Hotkey support for Mindful Organizer.

Uses *pynput* when available (requires Accessibility permission on macOS).
Falls back to in-app shortcuts when pynput is not installed or lacks permissions.

Hotkeys:
- Ctrl+Shift+F  → Toggle Focus Mode
- Ctrl+Shift+C  → Crisis Mode
- Ctrl+Shift+G  → Grounding Mode
- Ctrl+Shift+M  → Quick Mood Log
- Ctrl+Shift+E  → Quick Energy Log
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow

logger = logging.getLogger(__name__)

# Callback type aliases
VoidCallback = Callable[[], None]


class GlobalHotkeyManager(QObject):
    """Manages global (or app-global) hotkeys.

    On macOS, true global hotkeys require *pynput* and Accessibility
    permissions.  When unavailable, shortcuts still work while the app
    is focused.
    """

    focus_toggle = pyqtSignal()
    crisis_trigger = pyqtSignal()
    grounding_trigger = pyqtSignal()
    mood_log = pyqtSignal()
    energy_log = pyqtSignal()

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self._parent = parent
        self._pynput_listener = None
        self._shortcuts: list[QShortcut] = []
        self._has_pynput = False

        self._try_pynput()
        self._setup_fallback_shortcuts()

    # -- pynput setup ---------------------------------------------------------

    def _try_pynput(self) -> None:
        try:
            from pynput import keyboard

            self._has_pynput = True
            self._pynput_listener = keyboard.GlobalHotKeys(
                {
                    "<ctrl>+<shift>+f": self._on_focus,
                    "<ctrl>+<shift>+c": self._on_crisis,
                    "<ctrl>+<shift>+g": self._on_grounding,
                    "<cmd>+<shift>+f": self._on_focus,  # macOS-friendly
                    "<cmd>+<shift>+c": self._on_crisis,  # macOS-friendly
                    "<cmd>+<shift>+g": self._on_grounding,  # macOS-friendly
                }
            )
            self._pynput_listener.start()
            logger.info("Global hotkeys active via pynput")
        except Exception as exc:
            self._has_pynput = False
            logger.info(
                "pynput unavailable or lacks permissions (%s). Using in-app shortcuts only.", exc
            )

    # -- PyQt fallback shortcuts ----------------------------------------------

    def _setup_fallback_shortcuts(self) -> None:
        if self._parent is None:
            return
        shortcuts = [
            ("Ctrl+Shift+F", self._on_focus),
            ("Ctrl+Shift+C", self._on_crisis),
            ("Ctrl+Shift+G", self._on_grounding),
            ("Ctrl+Shift+M", self._on_mood),
            ("Ctrl+Shift+E", self._on_energy),
        ]
        for seq, slot in shortcuts:
            sc = QShortcut(QKeySequence(seq), self._parent)
            sc.activated.connect(slot)
            self._shortcuts.append(sc)

    # -- signal emitters ------------------------------------------------------

    def _on_focus(self) -> None:
        logger.debug("Hotkey: focus toggle")
        self.focus_toggle.emit()

    def _on_crisis(self) -> None:
        logger.debug("Hotkey: crisis mode")
        self.crisis_trigger.emit()

    def _on_grounding(self) -> None:
        logger.debug("Hotkey: grounding mode")
        self.grounding_trigger.emit()

    def _on_mood(self) -> None:
        logger.debug("Hotkey: mood log")
        self.mood_log.emit()

    def _on_energy(self) -> None:
        logger.debug("Hotkey: energy log")
        self.energy_log.emit()

    # -- lifecycle ------------------------------------------------------------

    def stop(self) -> None:
        if self._pynput_listener is not None:
            self._pynput_listener.stop()
            self._pynput_listener = None
            logger.info("Global hotkeys stopped")
