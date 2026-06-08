"""pytest-qt tests for the BreathingWidget."""

from __future__ import annotations

from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.breathing_widget import BreathingWidget


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot):
    widget = BreathingWidget(theme={}, breathing_manager=None, profile_manager=None)
    qtbot.addWidget(widget)
    assert widget is not None


def test_start_stop_breathing_exercise(qtbot):
    widget = BreathingWidget(theme={}, breathing_manager=None, profile_manager=None)
    qtbot.addWidget(widget)

    # The toggle is positioned manually, not parented to a layout.
    toggle = widget._toggle
    assert toggle is not None
    assert not widget._running

    toggle.click()
    assert widget._running
    assert toggle.text() == "I'm steadier now"

    toggle.click()
    assert not widget._running
    assert toggle.text() == "Begin"


def test_animation_state(qtbot):
    widget = BreathingWidget(theme={}, breathing_manager=None, profile_manager=None)
    qtbot.addWidget(widget)

    # Before show, the orb should not have an active animation group.
    assert widget._orb._group is None

    # showEvent starts the orb in idle mode.
    widget.show()
    assert widget._orb._group is not None

    # hideEvent stops the orb.
    widget.hide()
    assert widget._orb._group is None
