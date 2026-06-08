"""pytest-qt tests for the ERPWidget (exposure ladder and in-session)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtWidgets import QAbstractButton, QLabel

from gui.widgets.erp_widget import ERPWidget


@pytest.fixture
def fake_main_window(tmp_path):
    """Return a lightweight stand-in for the main window."""
    mw = MagicMock()
    mw.data_dir = tmp_path
    mw.erp_tracker = MagicMock()
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
    with patch.object(ERPWidget, "_detect_reduced_motion", return_value=True):
        widget = ERPWidget(main_window=fake_main_window)
        qtbot.addWidget(widget)
        assert widget is not None
        assert widget._stack.currentIndex() == 0


def test_add_exposure_item(qtbot, fake_main_window):
    with patch.object(ERPWidget, "_detect_reduced_motion", return_value=True):
        widget = ERPWidget(main_window=fake_main_window)
        qtbot.addWidget(widget)

        widget._open_add()
        widget._add_edit.setText("Touching a doorknob without washing")
        # slider default is ~0.4 -> predicted_suds of 40
        widget._commit_add()

        assert len(widget._hierarchy) == 1
        assert widget._hierarchy[0]["title"] == "Touching a doorknob without washing"
        assert widget._hierarchy[0]["predicted_suds"] == 40

        # Should appear in the ladder (LadderRung paints its title, so inspect the widget)
        assert widget._rungs_box.count() == 1
        rung = widget._rungs_box.itemAt(0).widget()
        assert rung is not None
        assert rung._item["title"] == "Touching a doorknob without washing"


def test_start_and_complete_exposure_session(qtbot, fake_main_window):
    with patch.object(ERPWidget, "_detect_reduced_motion", return_value=True):
        widget = ERPWidget(main_window=fake_main_window)
        qtbot.addWidget(widget)

        rung_id = "test-rung-01"
        widget._hierarchy = [
            {
                "id": rung_id,
                "title": "Touching a doorknob",
                "predicted_suds": 40,
                "created_at": "2026-01-01T00:00:00",
            }
        ]
        widget._refresh_ladder()

        # Start exposure
        widget._start_exposure(rung_id)

        assert widget._active_session is not None
        assert widget._stack.currentIndex() == 1
        assert widget._session_title.text() == "Touching a doorknob"

        # Simulate a SUDS check-in
        widget._record_suds(60)
        assert len(widget._session_suds) == 1
        assert widget._session_suds[0]["suds"] == 60

        # Complete the session
        with qtbot.waitSignal(widget.session_completed, timeout=1000):
            widget._end_exposure()

        assert widget._active_session is None
        assert widget._stack.currentIndex() == 0
        assert len(widget._sessions) == 1
        assert widget._sessions[0]["hierarchy_title"] == "Touching a doorknob"


def test_exposure_history_updates(qtbot, fake_main_window):
    with patch.object(ERPWidget, "_detect_reduced_motion", return_value=True):
        widget = ERPWidget(main_window=fake_main_window)
        qtbot.addWidget(widget)

        rung_id = "test-rung-01"
        widget._hierarchy = [
            {
                "id": rung_id,
                "title": "Touching a doorknob",
                "predicted_suds": 40,
                "created_at": "2026-01-01T00:00:00",
            }
        ]
        widget._sessions = [
            {
                "id": "session-01",
                "hierarchy_id": rung_id,
                "hierarchy_title": "Touching a doorknob",
                "predicted_suds": 40,
                "started_at": "2026-01-01T10:00:00",
                "ended_at": "2026-01-01T10:15:00",
                "duration_sec": 900,
                "suds_log": [],
                "urge_log": [],
                "rp_notes": "",
                "urges_resisted": 0,
                "peak_suds": 0,
                "final_suds": 0,
            }
        ]
        widget._refresh_ladder()

        # Ladder rung should reflect that it has been faced once
        assert widget._rungs_box.count() == 1
        rung = widget._rungs_box.itemAt(0).widget()
        assert rung is not None
        assert rung._faced == 1
