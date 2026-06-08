"""Tests for global hotkey management."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QMainWindow

from utils.global_hotkeys import GlobalHotkeyManager


class TestGlobalHotkeyManager:
    def test_instantiation_without_parent(self):
        mgr = GlobalHotkeyManager(parent=None)
        assert mgr._parent is None
        assert mgr._has_pynput is False
        assert mgr._shortcuts == []

    def test_instantiation_with_parent(self, qtbot):
        window = QMainWindow()
        qtbot.add_widget(window)
        mgr = GlobalHotkeyManager(parent=window)
        assert mgr._parent is window
        assert len(mgr._shortcuts) == 5

    def test_fallback_when_pynput_unavailable(self, monkeypatch):
        fake_keyboard = MagicMock()
        fake_keyboard.GlobalHotKeys.side_effect = RuntimeError("No accessibility")
        fake_pynput = MagicMock()
        fake_pynput.keyboard = fake_keyboard
        monkeypatch.setitem(sys.modules, "pynput", fake_pynput)
        monkeypatch.setitem(sys.modules, "pynput.keyboard", fake_keyboard)
        mgr = GlobalHotkeyManager(parent=None)
        assert mgr._has_pynput is False

    def test_signals_emitted(self):
        mgr = GlobalHotkeyManager(parent=None)
        pairs = [
            ("focus_toggle", "_on_focus"),
            ("crisis_trigger", "_on_crisis"),
            ("grounding_trigger", "_on_grounding"),
            ("mood_log", "_on_mood"),
            ("energy_log", "_on_energy"),
        ]
        for signal_name, method_name in pairs:
            sig = getattr(mgr, signal_name)
            slot = MagicMock()
            sig.connect(slot)
            getattr(mgr, method_name)()
            slot.assert_called_once()

    def test_stop(self):
        fake_listener = MagicMock()
        mgr = GlobalHotkeyManager(parent=None)
        mgr._pynput_listener = fake_listener
        mgr.stop()
        fake_listener.stop.assert_called_once()
        assert mgr._pynput_listener is None
