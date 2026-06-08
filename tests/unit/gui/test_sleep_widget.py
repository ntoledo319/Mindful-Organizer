"""pytest-qt tests for the SleepWidget rest check-in."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.sleep_widget import SleepWidget


@pytest.fixture
def fake_main_window(tmp_path):
    """Return a lightweight stand-in for the main window."""
    mw = MagicMock()
    mw.data_dir = tmp_path
    mw.sleep_tracker = None
    mw.profile_manager.current_profile = None
    return mw


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot, fake_main_window):
    widget = SleepWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)
    assert widget is not None


def test_log_sleep_button(qtbot, fake_main_window):
    tracker = MagicMock()
    fake_main_window.sleep_tracker = tracker

    widget = SleepWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    save_btn = _find_button(widget, "Set down the night")
    assert save_btn is not None
    save_btn.click()

    assert tracker.log_sleep.called
    kwargs = tracker.log_sleep.call_args.kwargs
    assert "date" in kwargs
    assert "bedtime" in kwargs
    assert "wake_time" in kwargs


def test_wake_time_after_bed_time(qtbot, fake_main_window):
    widget = SleepWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    # Normal overnight sleep: bed 23:00, wake 07:00 -> ~8 hours
    widget._bed_dial.set_time(23, 0, animate=False)
    widget._wake_dial.set_time(7, 0, animate=False)
    duration = widget._calc_duration(
        widget._bed_dial.time_string(), widget._wake_dial.time_string()
    )
    assert 7.0 < duration < 9.0

    # Same-day wake: bed 07:00, wake 23:00 -> 16 hours
    widget._bed_dial.set_time(7, 0, animate=False)
    widget._wake_dial.set_time(23, 0, animate=False)
    duration = widget._calc_duration(
        widget._bed_dial.time_string(), widget._wake_dial.time_string()
    )
    assert duration == 16.0

    # Wrap-around: bed 23:00, wake 22:00 -> 23 hours (next day)
    widget._bed_dial.set_time(23, 0, animate=False)
    widget._wake_dial.set_time(22, 0, animate=False)
    duration = widget._calc_duration(
        widget._bed_dial.time_string(), widget._wake_dial.time_string()
    )
    assert duration == 23.0
