"""pytest-qt tests for the MeditationWidget."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.meditation_widget import _PRACTICES, MeditationWidget


@pytest.fixture
def fake_main_window(tmp_path):
    """Return a lightweight stand-in for the main window."""
    mw = MagicMock()
    mw.data_dir = tmp_path
    mw.meditation_manager = None
    return mw


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot, fake_main_window):
    widget = MeditationWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)
    assert widget is not None


def test_meditation_list_loads(qtbot, fake_main_window):
    widget = MeditationWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    assert len(widget._practice_rows) == len(_PRACTICES)
    for i, row in enumerate(widget._practice_rows):
        assert row._name == _PRACTICES[i][0]
        assert row._desc == _PRACTICES[i][1]


def test_begin_button_starts_session(qtbot, fake_main_window):
    widget = MeditationWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    toggle = _find_button(widget, "Begin")
    assert toggle is not None
    assert not widget._running

    toggle.click()
    assert widget._running
    assert toggle.text() == "Let it go"

    # Stop the session so the timer does not outlive the test.
    toggle.click()
    assert not widget._running
    assert toggle.text() == "Begin"
