"""pytest-qt tests for the SearchWidget global search dialog."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QAbstractButton, QWidget

from gui.widgets.search_widget import SearchWidget


class FakeMainWindow(QWidget):
    """A real QWidget stand-in so QDialog accepts it as parent."""

    def __init__(self) -> None:
        super().__init__()

        # Task manager
        tm = MagicMock()
        tm.tasks = [
            SimpleNamespace(title="Buy milk", notes="", priority="low", due_date="today"),
            SimpleNamespace(
                title="Write report", notes="urgent", priority="high", due_date="tomorrow"
            ),
        ]
        self.task_manager = tm

        # Journaling manager
        jm = MagicMock()
        jm.entries = [
            {"text": "Had a good day", "date": "2026-01-01"},
            {"text": "Feeling anxious about work", "date": "2026-01-02"},
        ]
        self.journaling_manager = jm

        # Mood manager
        mm = MagicMock()
        mm.entries = [
            {"notes": "rough morning", "timestamp": "2026-01-01T08:00", "mood_score": 3},
        ]
        self.mood_manager = mm


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def _make_widget(qtbot):
    """Create a SearchWidget with a real QWidget parent."""
    mw = FakeMainWindow()
    widget = SearchWidget(main_window=mw)
    qtbot.addWidget(mw)
    qtbot.addWidget(widget)
    return widget


def test_can_be_instantiated(qtbot):
    widget = _make_widget(qtbot)
    assert widget is not None


def test_search_input_accepts_text(qtbot):
    widget = _make_widget(qtbot)

    widget._search_input.setText("milk")
    assert widget._search_input.text() == "milk"


def test_search_executes_and_shows_results(qtbot):
    widget = _make_widget(qtbot)

    widget._search_input.setText("milk")
    # Bypass debounce timer and execute directly
    widget._execute_search()

    assert len(widget._current_results) > 0
    result_titles = [r["title"] for r in widget._current_results]
    assert "Buy milk" in result_titles


def test_filter_checkboxes_exist(qtbot):
    widget = _make_widget(qtbot)

    assert "tasks" in widget._filter_checks
    assert "journal" in widget._filter_checks
    assert "mood" in widget._filter_checks

    for cb in widget._filter_checks.values():
        assert cb.isChecked()


def test_close_button_exists(qtbot):
    widget = _make_widget(qtbot)

    btn = _find_button(widget, "Close")
    assert btn is not None
