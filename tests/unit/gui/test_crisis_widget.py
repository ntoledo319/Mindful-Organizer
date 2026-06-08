"""pytest-qt tests for the CrisisWidget safety surface."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QAbstractButton, QLabel

from gui.widgets.crisis_widget import CrisisWidget


@pytest.fixture
def fake_main_window(tmp_path):
    """Return a lightweight stand-in for the main window."""
    mw = MagicMock()
    mw.theme_manager.get_colors.return_value = {}
    mw.theme_manager.reduced_motion = False
    mw.data_dir = tmp_path
    mw.crisis_plan_manager = None
    return mw


def _find_button(widget, text: str) -> QAbstractButton | None:
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def _find_label(widget, text: str) -> QLabel | None:
    for lbl in widget.findChildren(QLabel):
        if text in lbl.text():
            return lbl
    return None


def test_displays_crisis_contacts(qtbot, fake_main_window):
    widget = CrisisWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    assert _find_button(widget, "Call 988") is not None
    assert _find_button(widget, "Text instead") is not None
    assert _find_button(widget, "SAMHSA helpline") is not None


def test_988_button_visible_and_clickable(qtbot, fake_main_window, monkeypatch):
    widget = CrisisWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    btn = _find_button(widget, "Call 988")
    assert btn is not None
    assert not btn.isHidden()

    # Prevent actually opening a tel: URL during the test
    monkeypatch.setattr("gui.widgets.crisis_widget.QDesktopServices", MagicMock())

    btn.click()

    assert not widget._confirm.isHidden()
    assert "988" in widget._confirm.text().lower() or "clipboard" in widget._confirm.text().lower()
    assert "Stay" in widget._sentence.text()


def test_risk_heuristics_displayed(qtbot, fake_main_window):
    widget = CrisisWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    # Coping strategies from the default plan should appear on the live screen
    assert _find_label(widget, "Take slow, deep breaths") is not None

    # Warning signs are kept off the live screen (calm-state editor only)
    assert _find_label(widget, "Withdrawing from others") is None
