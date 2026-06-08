"""pytest-qt tests for the VoiceJournalWidget."""

from __future__ import annotations

from unittest.mock import MagicMock

from PyQt6.QtWidgets import QAbstractButton, QLabel

from gui.widgets.voice_journal_widget import VoiceJournalWidget


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def _find_label(widget, text: str):
    for lbl in widget.findChildren(QLabel):
        if text in lbl.text():
            return lbl
    return None


def test_can_be_instantiated(qtbot):
    widget = VoiceJournalWidget()
    qtbot.addWidget(widget)
    assert widget is not None


def test_shows_coming_soon_when_unavailable(qtbot):
    widget = VoiceJournalWidget()
    qtbot.addWidget(widget)

    assert _find_label(widget, "coming soon") is not None
    assert _find_button(widget, "Go to Text Journal") is not None


def test_navigate_button_emits_signal(qtbot):
    widget = VoiceJournalWidget()
    qtbot.addWidget(widget)

    btn = _find_button(widget, "Go to Text Journal")
    assert btn is not None

    with qtbot.waitSignal(widget.navigate_to_text_journal, timeout=500):
        btn.click()


def test_record_button_when_available(qtbot):
    mock_journal = MagicMock()
    mock_journal.is_available = True
    mock_journal.get_status.return_value = {"recording": False}

    widget = VoiceJournalWidget(voice_journal=mock_journal)
    qtbot.addWidget(widget)

    btn = _find_button(widget, "Record")
    assert btn is not None

    # Start recording
    btn.click()
    mock_journal.start_recording.assert_called_once()
    assert btn.text() == "Stop"

    # Now mock as recording
    mock_journal.get_status.return_value = {"recording": True}

    # Stop recording
    btn.click()
    mock_journal.stop_recording.assert_called_once()
    assert btn.text() == "Record"
