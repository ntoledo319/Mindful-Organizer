"""Framework-agnostic reactive state bus.

Provides the same call surface that the previous Qt-based StateBus exposed
(`bus.event_name.connect(cb)` / `bus.event_name.emit(...)`) but without any
PyQt6 dependency. This lets every manager in `core/`, `wellness/`,
`profiles/`, `security/`, and `utils/` emit state changes without dragging
the GUI framework into the backend — which is the precondition for the
FastAPI/Tauri rebuild.

If the GUI process wants Qt thread-safety semantics on top of this bus, it
can subscribe a Qt signal forwarder; the bus itself stays pure-Python.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class Signal:
    """Pub/sub primitive with the same call shape as `pyqtSignal`.

    - ``connect(callback)`` registers a listener
    - ``disconnect(callback)`` removes one
    - ``emit(*args, **kwargs)`` invokes every listener synchronously

    Failures in one listener never break other listeners — exceptions are
    logged and swallowed. The bus is intentionally synchronous; threading
    semantics belong to the consumer, not the bus.
    """

    __slots__ = ("_listeners", "_lock")

    def __init__(self) -> None:
        self._listeners: list[Callable[..., Any]] = []
        self._lock = threading.RLock()

    def connect(self, callback: Callable[..., Any]) -> None:
        with self._lock:
            if callback not in self._listeners:
                self._listeners.append(callback)

    def disconnect(self, callback: Callable[..., Any]) -> None:
        with self._lock:
            if callback in self._listeners:
                self._listeners.remove(callback)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        with self._lock:
            listeners = list(self._listeners)
        for cb in listeners:
            try:
                cb(*args, **kwargs)
            except Exception:
                logger.exception("StateBus listener raised — continuing")

    def listener_count(self) -> int:
        with self._lock:
            return len(self._listeners)


class StateBus:
    """Central pub/sub for application state changes.

    Every event is a :class:`Signal` instance. The set of events mirrors the
    previous Qt-based bus, so existing call sites do not need to change.
    """

    def __init__(self) -> None:
        # Task events
        self.task_changed = Signal()  # emit(action: str, payload: dict)
        self.task_added = Signal()  # emit(task)
        self.task_completed = Signal()  # emit(task_id: str)
        self.task_deleted = Signal()  # emit(task_id: str)

        # Wellness events
        self.mood_logged = Signal()  # emit(entry)
        self.energy_updated = Signal()  # emit(level: int)
        self.sleep_logged = Signal()  # emit(entry)
        self.medication_taken = Signal()  # emit(medication_id: str)
        self.medication_missed = Signal()  # emit(medication_id: str)

        # Crisis / safety
        self.crisis_signal_detected = Signal()  # emit(signal_dict)

        # Profile / settings
        self.profile_changed = Signal()  # emit(profile)
        self.theme_changed = Signal()  # emit(theme_name: str)
        self.settings_changed = Signal()  # emit()

        # Journal
        self.journal_entry_saved = Signal()  # emit(entry)

        # ERP / grounding / breathing / meditation / panic
        self.exposure_completed = Signal()
        self.grounding_session_completed = Signal()
        self.breathing_session_completed = Signal()
        self.meditation_session_completed = Signal()
        self.panic_logged = Signal()

        # Values / weekly review
        self.values_review_ready = Signal()

        # Daily briefing
        self.daily_briefing_ready = Signal()

    # Convenience emitters — preserved from the Qt-based bus for back-compat
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


# Module-level singleton — get_state_bus() returns the active bus,
# auto-creating one if no consumer has set it yet. This is the key
# difference from the Qt version: in headless mode the bus exists by
# default rather than raising RuntimeError.
_state_bus: StateBus | None = None


def get_state_bus() -> StateBus:
    """Return the global StateBus, lazily creating one if needed."""
    global _state_bus
    if _state_bus is None:
        _state_bus = StateBus()
    return _state_bus


def set_state_bus(bus: StateBus) -> None:
    """Replace the global StateBus instance.

    Useful for tests or for the GUI process that wants to inject a
    pre-configured bus.
    """
    global _state_bus
    _state_bus = bus


def reset_state_bus() -> None:
    """Clear the global StateBus — primarily for test isolation."""
    global _state_bus
    _state_bus = None
