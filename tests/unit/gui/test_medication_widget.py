"""pytest-qt tests for the MedicationWidget (The Shelf)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtWidgets import QAbstractButton, QDialog, QLabel

from gui.widgets.medication_widget import MedicationWidget


@pytest.fixture
def fake_main_window(tmp_path):
    """Return a lightweight stand-in for the main window."""
    mw = MagicMock()
    mw.data_dir = tmp_path
    mw.medication_tracker = MagicMock()
    return mw


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


def test_can_be_instantiated(qtbot, fake_main_window):
    with patch("gui.widgets.medication_widget._detect_reduced_motion", return_value=True):
        widget = MedicationWidget(main_window=fake_main_window)
        qtbot.addWidget(widget)
        assert widget is not None


def test_add_medication(qtbot, fake_main_window):
    with patch("gui.widgets.medication_widget._detect_reduced_motion", return_value=True):
        widget = MedicationWidget(main_window=fake_main_window)
        qtbot.addWidget(widget)

        with patch("gui.widgets.medication_widget._MedicationDialog") as mock_dlg:
            mock_dlg.return_value.exec.return_value = QDialog.DialogCode.Accepted
            mock_dlg.return_value.get_data.return_value = {
                "name": "Sertraline",
                "dosage": "50mg",
                "frequency": "Daily",
                "time": "08:00",
            }
            widget._add_medication()

        assert len(widget._medications) == 1
        assert widget._medications[0]["name"] == "Sertraline"
        assert widget._medications[0]["dosage"] == "50mg"
        assert widget._medications[0]["frequency"] == "Daily"
        assert widget._medications[0]["time"] == "08:00"

        # Should appear in the shelf and today's doses
        assert _find_label(widget, "Sertraline") is not None
        assert _find_button(widget, "Took it") is not None


def test_medication_appears_in_list(qtbot, fake_main_window):
    with patch("gui.widgets.medication_widget._detect_reduced_motion", return_value=True):
        widget = MedicationWidget(main_window=fake_main_window)
        qtbot.addWidget(widget)

        widget._medications = [
            {"name": "Sertraline", "dosage": "50mg", "frequency": "Daily", "time": "08:00"}
        ]
        widget._refresh_all()

        # Dose card should exist with the medication name and action buttons
        assert _find_label(widget, "Sertraline") is not None
        assert _find_button(widget, "Took it") is not None


def test_mark_dose_as_taken(qtbot, fake_main_window):
    with patch("gui.widgets.medication_widget._detect_reduced_motion", return_value=True):
        widget = MedicationWidget(main_window=fake_main_window)
        qtbot.addWidget(widget)

        widget._medications = [
            {"name": "Sertraline", "dosage": "50mg", "frequency": "Daily", "time": "08:00"}
        ]
        widget._refresh_all()

        take_btn = _find_button(widget, "Took it")
        assert take_btn is not None

        with qtbot.waitSignal(widget.medication_taken, timeout=1000):
            take_btn.click()

        # The backend tracker should have been notified
        assert fake_main_window.medication_tracker.record_status.called


def test_delete_medication(qtbot, fake_main_window):
    with patch("gui.widgets.medication_widget._detect_reduced_motion", return_value=True):
        widget = MedicationWidget(main_window=fake_main_window)
        qtbot.addWidget(widget)

        widget._medications = [
            {"name": "Sertraline", "dosage": "50mg", "frequency": "Daily", "time": "08:00"}
        ]
        widget._refresh_all()

        # Trigger the inline confirm on the shelf tile
        remove_btn = _find_button(widget, "Take off the shelf")
        assert remove_btn is not None
        remove_btn.click()

        yes_btn = _find_button(widget, "Yes")
        assert yes_btn is not None
        yes_btn.click()

        assert len(widget._medications) == 0
        # Shelf should now show the empty state
        assert _find_label(widget, "The shelf is empty for now.") is not None
