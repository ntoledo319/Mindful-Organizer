"""pytest-qt tests for the DiaryCardWidget evening card."""

from __future__ import annotations

from datetime import date

import pytest
from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.diary_card_widget import DiaryCardWidget


class FakeDiaryManager:
    """Minimal backend that records saved cards."""

    def __init__(self):
        self.saved = []

    def save(self, card):
        self.saved.append(card)

    def get(self, date):
        return None


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot):
    widget = DiaryCardWidget(theme={}, diary_card_manager=None, profile_manager=None)
    qtbot.addWidget(widget)
    assert widget is not None


def test_save_emits_card_saved(qtbot):
    widget = DiaryCardWidget(theme={}, diary_card_manager=None, profile_manager=None)
    qtbot.addWidget(widget)

    save_btn = _find_button(widget, "Set the card down")
    assert save_btn is not None

    with qtbot.waitSignal(widget.card_saved, timeout=1000):
        save_btn.click()


def test_high_risk_care_slider_emits_crisis_requested(qtbot):
    widget = DiaryCardWidget(theme={}, diary_card_manager=None, profile_manager=None)
    qtbot.addWidget(widget)

    # Move the Suicide slider to maximum -> intensity level 5 (> threshold 3)
    widget._care_sliders["Suicide"].setValue(1.0)

    save_btn = _find_button(widget, "Set the card down")
    assert save_btn is not None

    with qtbot.waitSignal(widget.crisis_requested, timeout=1000):
        save_btn.click()


def test_save_calls_manager_mock(qtbot):
    manager = FakeDiaryManager()
    widget = DiaryCardWidget(theme={}, diary_card_manager=manager, profile_manager=None)
    qtbot.addWidget(widget)

    save_btn = _find_button(widget, "Set the card down")
    assert save_btn is not None
    save_btn.click()

    assert len(manager.saved) == 1
    assert manager.saved[0].date == date.today()
