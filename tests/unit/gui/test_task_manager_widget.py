"""pytest-qt tests for the TaskManagerWidget task list."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.task_manager_widget import TaskManagerWidget


class FakeTaskManager:
    """Minimal stand-in for the task manager backend."""

    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def complete_task(self, task):
        task.completed = True
        task.completed_at = datetime.now()

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if getattr(t, "id", t) != task_id]

    def _save_tasks(self):
        pass


class FakeNLP:
    """Stub NLP parser that echoes the raw text back as a parsed task."""

    def parse(self, text: str):
        return SimpleNamespace(
            title=text,
            priority="medium",
            category="Other",
            energy=30,
            due_date=None,
        )


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot):
    widget = TaskManagerWidget(theme={}, task_manager=None, nlp_parser=None)
    qtbot.addWidget(widget)
    assert widget is not None


def test_add_task_via_nlp_parser(qtbot):
    tm = FakeTaskManager()
    nlp = FakeNLP()
    widget = TaskManagerWidget(theme={}, task_manager=tm, nlp_parser=nlp)
    qtbot.addWidget(widget)

    with qtbot.waitSignal(widget.task_added, timeout=1000), patch.object(widget, "_acknowledge"):
        widget._nlp_input.setText("Buy groceries")
        add_btn = _find_button(widget, "Add it")
        assert add_btn is not None
        add_btn.click()

    assert len(tm.tasks) == 1
    assert tm.tasks[0].title == "Buy groceries"


def test_complete_task_emits_signal(qtbot):
    task = SimpleNamespace(
        title="Water plants",
        energy_required=10,
        due_date=None,
        category=None,
        recurrence=None,
        completed=False,
        completed_at=None,
        id=1,
    )
    tm = FakeTaskManager()
    tm.tasks.append(task)

    widget = TaskManagerWidget(theme={}, task_manager=tm, nlp_parser=None)
    qtbot.addWidget(widget)

    # The first (and only) widget in the list layout is the TaskRow
    row_item = widget._list_box.itemAt(0)
    row = row_item.widget()
    assert row is not None

    done_btn = _find_button(row, "Done")
    assert done_btn is not None

    with qtbot.waitSignal(widget.task_completed, timeout=1000):
        done_btn.click()

    assert task.completed is True


def test_undo_redo_buttons_exist_and_function(qtbot):
    tm = FakeTaskManager()
    nlp = FakeNLP()
    widget = TaskManagerWidget(theme={}, task_manager=tm, nlp_parser=nlp)
    qtbot.addWidget(widget)

    undo_btn = _find_button(widget, "Undo")
    redo_btn = _find_button(widget, "Redo")
    assert undo_btn is not None
    assert redo_btn is not None

    # Add a task through the NLP line
    with patch.object(widget, "_acknowledge"):
        widget._nlp_input.setText("Read a book")
        add_btn = _find_button(widget, "Add it")
        add_btn.click()

    assert len(tm.tasks) == 1

    # Undo removes the task
    undo_btn.click()
    assert len(tm.tasks) == 0

    # Redo restores it
    redo_btn.click()
    assert len(tm.tasks) == 1
