"""pytest-qt tests for the PanicTrackerWidget."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.panic_tracker_widget import PanicTrackerWidget


@pytest.fixture
def fake_main_window(tmp_path):
    """Return a lightweight stand-in for the main window."""
    mw = MagicMock()
    mw.data_dir = tmp_path
    return mw


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot, fake_main_window):
    widget = PanicTrackerWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)
    assert widget is not None


def test_now_page_has_breathing_room(qtbot, fake_main_window):
    widget = PanicTrackerWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    # Starts on the "now" page (index 0)
    assert widget._stack.currentIndex() == 0
    assert widget._pacer is not None


def test_to_later_button_exists(qtbot, fake_main_window):
    widget = PanicTrackerWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    btn = _find_button(widget, "When it eases, set down what happened")
    assert btn is not None


def test_enter_later_transitions_to_log(qtbot, fake_main_window):
    widget = PanicTrackerWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    widget._enter_later()
    assert widget._stack.currentIndex() == 1
    assert widget._step == 0


def test_logging_panic_emits_signal(qtbot, fake_main_window):
    widget = PanicTrackerWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    # Move into later mode and advance through the steps
    widget._enter_later()

    # Step 0: what happened (skip trigger selection)
    widget._step_next()
    assert widget._step == 1

    # Step 1: intensity (skip adjusting slider)
    widget._step_next()
    assert widget._step == 2

    # Step 2: what helped (skip selection)
    # Commit happens here and emits panic_logged
    with qtbot.waitSignal(widget.panic_logged, timeout=1000):
        widget._step_next()

    assert len(widget._entries) == 1
    entry = widget._entries[0]
    assert "timestamp" in entry
    assert "peak_distress" in entry
