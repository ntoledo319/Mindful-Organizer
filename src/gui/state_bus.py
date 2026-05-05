"""
Reactive state bus for cross-widget communication.

Eliminates manual _refresh_*() chains by emitting typed events whenever
managers mutate data. Widgets subscribe to relevant events and update
automatically.
"""

from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal


class StateBus(QObject):
    """Central pub/sub bus for application state changes.

    Usage::

        bus = StateBus()
        bus.task_changed.connect(my_widget.on_task_changed)
        bus.emit_task_changed("completed", task_id="abc")
    """

    # Task events
    task_changed = pyqtSignal(str, object)  # (action, payload_dict)
    task_added = pyqtSignal(object)
    task_completed = pyqtSignal(str)
    task_deleted = pyqtSignal(str)

    # Wellness events
    mood_logged = pyqtSignal(object)
    energy_updated = pyqtSignal(int)
    sleep_logged = pyqtSignal(object)
    medication_taken = pyqtSignal(str)
    medication_missed = pyqtSignal(str)

    # Crisis / safety
    crisis_signal_detected = pyqtSignal(object)

    # Profile / settings
    profile_changed = pyqtSignal(object)
    theme_changed = pyqtSignal(str)
    settings_changed = pyqtSignal()

    # Journal
    journal_entry_saved = pyqtSignal(object)

    # ERP / grounding / breathing
    exposure_completed = pyqtSignal(object)
    grounding_session_completed = pyqtSignal(object)
    breathing_session_completed = pyqtSignal(object)
    meditation_session_completed = pyqtSignal(object)
    panic_logged = pyqtSignal(object)

    # Values / weekly review
    values_review_ready = pyqtSignal(object)

    # Daily briefing
    daily_briefing_ready = pyqtSignal(object)

    # ------------------------------------------------------------------
    # Convenience emitters
    # ------------------------------------------------------------------

    def emit_task_changed(self, action: str, **payload: Any) -> None:
        self.task_changed.emit(action, payload)

    def emit_mood_logged(self, entry: dict[str, Any]) -> None:
        self.mood_logged.emit(entry)

    def emit_energy_updated(self, level: int) -> None:
        self.energy_updated.emit(level)

    def emit_crisis_signal(self, signal: dict[str, Any]) -> None:
        self.crisis_signal_detected.emit(signal)

    def emit_daily_briefing(self, briefing: dict[str, Any]) -> None:
        self.daily_briefing_ready.emit(briefing)


# Singleton instance reference — set by AdaptiveMainWindow on init.
_state_bus: StateBus | None = None


def get_state_bus() -> StateBus:
    """Return the global StateBus instance.

    Raises RuntimeError if the bus hasn't been initialised yet.
    """
    if _state_bus is None:
        raise RuntimeError("StateBus has not been initialised. "
                           "It should be created by AdaptiveMainWindow.")
    return _state_bus


def set_state_bus(bus: StateBus) -> None:
    """Set the global StateBus instance."""
    global _state_bus
    _state_bus = bus
