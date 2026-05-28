"""Back-compatibility shim — the StateBus now lives in ``core.state_bus``.

This file re-exports the framework-agnostic bus so existing imports
(``from gui.state_bus import StateBus, get_state_bus, set_state_bus``)
keep working during the Tauri/Next.js migration. New code should import
from ``core.state_bus`` directly.
"""
from core.state_bus import (
    Signal,
    StateBus,
    get_state_bus,
    reset_state_bus,
    set_state_bus,
)

__all__ = [
    "Signal",
    "StateBus",
    "get_state_bus",
    "reset_state_bus",
    "set_state_bus",
]
