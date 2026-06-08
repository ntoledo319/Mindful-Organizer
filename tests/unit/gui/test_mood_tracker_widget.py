"""pytest-qt tests for the MoodTrackerWidget daily check-in."""

from __future__ import annotations

from unittest.mock import MagicMock

from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.mood_tracker import MoodTrackerWidget


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot):
    widget = MoodTrackerWidget(theme={}, mood_manager=None, profile_manager=None)
    qtbot.addWidget(widget)
    assert widget is not None


def test_mood_slider_change_emits_signal(qtbot):
    widget = MoodTrackerWidget(theme={}, mood_manager=None, profile_manager=None)
    qtbot.addWidget(widget)

    with qtbot.waitSignal(widget._dial.valueChanged, timeout=500):
        widget._dial.setValue(0.8, animate=False)


def test_save_button_calls_manager(qtbot):
    manager = MagicMock()
    widget = MoodTrackerWidget(theme={}, mood_manager=manager, profile_manager=None)
    qtbot.addWidget(widget)

    save_btn = _find_button(widget, "Set it down")
    assert save_btn is not None

    with qtbot.waitSignal(widget.mood_saved, timeout=1000):
        save_btn.click()

    assert manager.add_entry.called
    args = manager.add_entry.call_args[0][0]
    assert "mood_score" in args
    assert "timestamp" in args
    assert "symptoms" in args
