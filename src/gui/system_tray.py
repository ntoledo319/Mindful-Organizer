"""
System Tray Integration for Mindful Organizer.

Provides always-on presence with quick actions:
- Log mood / energy
- Activate focus mode
- Activate crisis / grounding mode
- Open main window
- Daily briefing
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


class SystemTrayController(QSystemTrayIcon):
    """System tray icon with quick-action menu.

    Signals are emitted so the main window or automation engine can
    respond without tight coupling.
    """

    quick_mood_log = pyqtSignal(int)  # mood score 1-10
    quick_energy_log = pyqtSignal(int)  # energy score 1-10
    focus_mode_toggle = pyqtSignal()  # toggle focus mode
    crisis_mode_trigger = pyqtSignal()  # activate crisis mode
    grounding_trigger = pyqtSignal()  # activate grounding mode
    show_main_window = pyqtSignal()  # bring main window to front
    daily_briefing_request = pyqtSignal()  # show daily briefing
    quit_app = pyqtSignal()  # graceful quit

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._focus_active = False
        self._setup_icon()
        self._setup_menu()
        self._setup_tooltip()
        self.activated.connect(self._on_activated)

    # -- setup ----------------------------------------------------------------

    def _setup_icon(self) -> None:
        # Use a standard fallback icon if no custom icon is available
        style = QApplication.style()
        if style:
            pixmap = style.standardPixmap(QApplication.style().StandardPixmap.SP_ComputerIcon)
            self.setIcon(QIcon(pixmap))
        self.setVisible(True)

    def _setup_menu(self) -> None:
        menu = QMenu()

        # Status header (non-interactive)
        self._status_action = QAction("Hearth - Ready")
        self._status_action.setEnabled(False)
        menu.addAction(self._status_action)
        menu.addSeparator()

        # Quick state logging
        menu.addAction("Log Mood ▲", lambda: self.quick_mood_log.emit(7))
        menu.addAction("Log Mood ▼", lambda: self.quick_mood_log.emit(3))
        menu.addAction("Log Energy ▲", lambda: self.quick_energy_log.emit(8))
        menu.addAction("Log Energy ▼", lambda: self.quick_energy_log.emit(2))
        menu.addSeparator()

        # Focus mode
        self._focus_action = QAction("Enter Focus Mode")
        self._focus_action.triggered.connect(self._toggle_focus)
        menu.addAction(self._focus_action)

        # Crisis / Grounding
        menu.addAction("Crisis Mode", self.crisis_mode_trigger.emit)
        menu.addAction("Grounding", self.grounding_trigger.emit)
        menu.addSeparator()

        # Main window
        menu.addAction("Open Today", self.show_main_window.emit)
        menu.addAction("Briefing", self.daily_briefing_request.emit)
        menu.addSeparator()

        # Quit
        menu.addAction("Quit", self.quit_app.emit)

        self.setContextMenu(menu)

    def _setup_tooltip(self) -> None:
        self.setToolTip("Hearth - adaptive desktop environment")

    # -- event handlers -------------------------------------------------------

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window.emit()

    def _toggle_focus(self) -> None:
        self._focus_active = not self._focus_active
        self._focus_action.setText("Exit Focus Mode" if self._focus_active else "Enter Focus Mode")
        self.focus_mode_toggle.emit()

    # -- public API -----------------------------------------------------------

    def set_status(self, text: str) -> None:
        self._status_action.setText(text)
        self.setToolTip(text)

    def set_focus_indicator(self, active: bool) -> None:
        self._focus_active = active
        self._focus_action.setText("Exit Focus Mode" if self._focus_active else "Enter Focus Mode")

    def show_notification(self, title: str, message: str, duration_ms: int = 5000) -> None:
        self.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, duration_ms)
