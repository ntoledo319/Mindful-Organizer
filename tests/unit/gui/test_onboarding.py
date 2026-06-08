"""pytest-qt tests for the OnboardingWizard."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QAbstractButton, QLineEdit, QStackedWidget

from gui.widgets.onboarding import OnboardingWizard


@pytest.fixture
def fake_profile_manager():
    """Return a lightweight profile manager stand-in."""
    pm = MagicMock()
    pm.current_profile = None
    return pm


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot, fake_profile_manager):
    wizard = OnboardingWizard(profile_manager=fake_profile_manager)
    qtbot.addWidget(wizard)
    assert wizard is not None


def test_all_pages_exist(qtbot, fake_profile_manager):
    wizard = OnboardingWizard(profile_manager=fake_profile_manager)
    qtbot.addWidget(wizard)

    assert wizard._stack.count() == 6
    # Page indices: 0 welcome, 1 name, 2 conditions, 3 therapy, 4 theme, 5 summary
    assert wizard._stack.widget(0) is not None
    assert wizard._stack.widget(1) is not None
    assert wizard._stack.widget(2) is not None
    assert wizard._stack.widget(3) is not None
    assert wizard._stack.widget(4) is not None
    assert wizard._stack.widget(5) is not None


def test_navigation_next_advances_pages(qtbot, fake_profile_manager):
    wizard = OnboardingWizard(profile_manager=fake_profile_manager)
    qtbot.addWidget(wizard)

    assert wizard._current_page == 0

    next_btn = _find_button(wizard, "Next")
    assert next_btn is not None
    next_btn.click()

    assert wizard._current_page == 1


def test_navigation_back_returns_pages(qtbot, fake_profile_manager):
    wizard = OnboardingWizard(profile_manager=fake_profile_manager)
    qtbot.addWidget(wizard)

    # Advance to page 1
    wizard._show_page(1)
    assert wizard._current_page == 1

    back_btn = _find_button(wizard, "Back")
    assert back_btn is not None
    back_btn.click()

    assert wizard._current_page == 0


def test_name_input_collected(qtbot, fake_profile_manager):
    wizard = OnboardingWizard(profile_manager=fake_profile_manager)
    qtbot.addWidget(wizard)

    wizard._show_page(1)
    wizard._name_input.setText("Alex")
    wizard._collect_page_data()

    assert wizard._data["name"] == "Alex"


def test_finish_emits_signal_and_creates_profile(qtbot, fake_profile_manager):
    wizard = OnboardingWizard(profile_manager=fake_profile_manager)
    qtbot.addWidget(wizard)

    wizard._data["name"] = "Alex"
    wizard._data["conditions"] = ["Anxiety"]
    wizard._data["therapy_types"] = ["CBT"]
    wizard._data["theme"] = "ember"

    with qtbot.waitSignal(wizard.onboarding_completed, timeout=1000):
        wizard._finish()

    assert fake_profile_manager.current_profile is not None
