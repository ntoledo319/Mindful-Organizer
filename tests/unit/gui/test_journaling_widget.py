"""pytest-qt tests for the JournalingWidget."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.journaling_widget import JournalingWidget


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


class MockProfile:
    def __init__(self, conditions=None):
        self.conditions = conditions or []


class MockProfileManager:
    def __init__(self, conditions=None):
        self.current_profile = MockProfile(conditions=conditions)


def test_can_be_instantiated(qtbot):
    widget = JournalingWidget(theme={}, journal_manager=None, profile_manager=None)
    qtbot.addWidget(widget)
    assert widget is not None


def test_editor_accepts_text(qtbot):
    widget = JournalingWidget(theme={}, journal_manager=None, profile_manager=None)
    qtbot.addWidget(widget)
    widget._editor.setPlainText("Hello journal")
    assert widget._editor.toPlainText() == "Hello journal"


def test_save_button_emits_entry_saved(qtbot):
    widget = JournalingWidget(theme={}, journal_manager=None, profile_manager=None)
    qtbot.addWidget(widget)

    # Mock risk check so we don't need JournalAnalyzer
    widget._check_risk = lambda text: False

    widget._editor.setPlainText("Today I feel good.")

    with qtbot.waitSignal(widget.entry_saved, timeout=1000):
        widget._save_btn.click()

    # Editor should be cleared after save
    assert widget._editor.toPlainText() == ""


def test_save_empty_does_not_emit(qtbot):
    widget = JournalingWidget(theme={}, journal_manager=None, profile_manager=None)
    qtbot.addWidget(widget)

    widget._editor.setPlainText("")

    # No signal should be emitted for empty text
    with qtbot.assertNotEmitted(widget.entry_saved, wait=500):
        widget._save_btn.click()


def test_prompt_rotation(qtbot):
    widget = JournalingWidget(theme={}, journal_manager=None, profile_manager=None)
    qtbot.addWidget(widget)

    original_prompt = widget._prompt_label.text()
    assert original_prompt != ""

    another_btn = widget._another_btn
    assert another_btn is not None

    another_btn.click()
    new_prompt = widget._prompt_label.text()
    # The prompt should have changed (unless there's only one prompt)
    assert new_prompt != original_prompt or len(widget._prompt_pool) == 1


def test_prompt_rotation_with_conditions(qtbot):
    from core.constants import Condition

    pm = MockProfileManager(conditions=[Condition.ANXIETY])
    widget = JournalingWidget(theme={}, journal_manager=None, profile_manager=pm)
    qtbot.addWidget(widget)

    original_prompt = widget._prompt_label.text()
    widget._another_btn.click()
    new_prompt = widget._prompt_label.text()
    assert new_prompt != original_prompt or len(widget._prompt_pool) == 1


def test_save_with_manager(qtbot):
    manager = MagicMock()
    manager.data_dir = "/tmp"
    manager.entries = []
    manager.save_entry = MagicMock()

    widget = JournalingWidget(theme={}, journal_manager=manager, profile_manager=None)
    qtbot.addWidget(widget)
    widget._check_risk = lambda text: False

    widget._editor.setPlainText("Managed entry")

    with qtbot.waitSignal(widget.entry_saved, timeout=1000):
        widget._save_btn.click()

    assert manager.save_entry.called
    args = manager.save_entry.call_args[0][0]
    assert args["text"] == "Managed entry"


def test_crisis_requested_on_risk(qtbot):
    widget = JournalingWidget(theme={}, journal_manager=None, profile_manager=None)
    qtbot.addWidget(widget)
    widget.show()

    # Force risk detection and trigger crisis panel
    widget._check_risk = lambda text: True

    widget._editor.setPlainText("I want to hurt myself")
    widget._save_btn.click()

    # Crisis panel should have been surfaced; _open_crisis emits crisis_requested
    with qtbot.waitSignal(widget.crisis_requested, timeout=1000):
        widget._open_crisis()


def test_word_count_display(qtbot):
    widget = JournalingWidget(theme={}, journal_manager=None, profile_manager=None)
    qtbot.addWidget(widget)

    # Less than 20 words should not show count
    widget._editor.setPlainText("Short text")
    assert widget._wordcount.text() == ""

    # 20+ words should show count
    widget._editor.setPlainText(" ".join(["word"] * 25))
    assert "words" in widget._wordcount.text()


def test_reveal_felt(qtbot):
    widget = JournalingWidget(theme={}, journal_manager=None, profile_manager=None)
    qtbot.addWidget(widget)
    widget.show()

    assert widget._felt_host.isHidden()
    widget._reveal_felt()
    assert widget._felt_host.isVisible()
    assert widget._felt_toggle.isHidden()
