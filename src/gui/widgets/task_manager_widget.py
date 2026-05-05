"""
Task management widget -- natural language entry, filtering, detail view.

Provides a full task management interface with NLP parsing, priority
colour indicators, energy badges, undo/redo, sorting, and task statistics.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.components import AccentButton, BodyLabel, CardFrame, SectionTitle

logger = logging.getLogger(__name__)


_PRIORITY_COLOURS = {
    "Urgent": "#e74c3c",
    "High": "#e67e22",
    "Medium": "#f1c40f",
    "Low": "#27ae60",
}


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

class TaskManagerWidget(QWidget):
    """Full task management tab with NLP entry, filtering, and detail panel."""

    task_added = pyqtSignal()
    task_completed = pyqtSignal()

    def __init__(
        self,
        theme: dict[str, str],
        task_manager: Any = None,
        nlp_parser: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._task_manager = task_manager
        self._nlp_parser = nlp_parser
        self._undo_stack: list[dict[str, Any]] = []
        self._redo_stack: list[dict[str, Any]] = []

        self._build_ui()
        self._refresh_task_list()
        self._refresh_statistics()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            f"QScrollArea {{ background-color: {self._theme.get('background', '#f5f5f5')}; }}"
        )
        outer.addWidget(scroll)

        container = QWidget()
        self._root = QVBoxLayout(container)
        self._root.setSpacing(16)
        self._root.setContentsMargins(24, 24, 24, 24)
        scroll.setWidget(container)

        self._build_nlp_entry()
        self._build_filter_row()

        body = QHBoxLayout()
        body.setSpacing(16)
        self._build_task_list(body)
        self._build_detail_panel(body)
        self._root.addLayout(body)

        self._build_action_buttons()
        self._build_statistics()
        self._root.addStretch()

    # -- NLP entry bar --------------------------------------------------

    def _build_nlp_entry(self) -> None:
        card = CardFrame(self._theme)
        layout = QHBoxLayout(card)

        self._nlp_input = QLineEdit()
        self._nlp_input.setPlaceholderText(
            "Type a task... e.g., 'call dentist tomorrow high priority'"
        )
        self._nlp_input.setStyleSheet(
            f"QLineEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 8px; "
            f"padding: 12px; font-size: 14px; }}"
        )
        self._nlp_input.returnPressed.connect(self._add_task_from_nlp)
        layout.addWidget(self._nlp_input, stretch=1)

        add_btn = AccentButton("Add Task", self._theme)
        add_btn.clicked.connect(self._add_task_from_nlp)
        layout.addWidget(add_btn)

        self._root.addWidget(card)

    # -- filter row -----------------------------------------------------

    def _build_filter_row(self) -> None:
        card = CardFrame(self._theme)
        layout = QHBoxLayout(card)
        layout.setSpacing(12)

        # Priority filter
        layout.addWidget(BodyLabel("Priority:", self._theme))
        self._priority_filter = QComboBox()
        self._priority_filter.addItems(["All", "Urgent", "High", "Medium", "Low"])
        self._priority_filter.currentTextChanged.connect(lambda _: self._refresh_task_list())
        layout.addWidget(self._priority_filter)

        # Category filter
        layout.addWidget(BodyLabel("Category:", self._theme))
        self._category_filter = QComboBox()
        self._category_filter.addItems([
            "All", "Work", "Personal", "Health", "Learning", "Social", "Errands", "Other",
        ])
        self._category_filter.currentTextChanged.connect(lambda _: self._refresh_task_list())
        layout.addWidget(self._category_filter)

        # Energy filter
        layout.addWidget(BodyLabel("Max Energy:", self._theme))
        self._energy_filter = QSpinBox()
        self._energy_filter.setRange(0, 100)
        self._energy_filter.setValue(100)
        self._energy_filter.setSuffix(" spoons")
        self._energy_filter.valueChanged.connect(lambda _: self._refresh_task_list())
        layout.addWidget(self._energy_filter)

        # Show completed
        self._show_completed = QCheckBox("Show Completed")
        self._show_completed.setStyleSheet(f"color: {self._theme.get('text', '#333')};")
        self._show_completed.stateChanged.connect(lambda _: self._refresh_task_list())
        layout.addWidget(self._show_completed)

        # Search
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("Search tasks...")
        self._search_box.setStyleSheet(
            f"QLineEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; padding: 6px; }}"
        )
        self._search_box.textChanged.connect(lambda _: self._refresh_task_list())
        layout.addWidget(self._search_box)

        # Sort
        layout.addWidget(BodyLabel("Sort:", self._theme))
        self._sort_combo = QComboBox()
        self._sort_combo.addItems(["Priority", "Due Date", "Energy", "Created Date"])
        self._sort_combo.currentTextChanged.connect(lambda _: self._refresh_task_list())
        layout.addWidget(self._sort_combo)

        self._root.addWidget(card)

    # -- task list ------------------------------------------------------

    def _build_task_list(self, parent_layout: QHBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Tasks", self._theme))

        self._task_list = QListWidget()
        self._task_list.setMinimumHeight(400)
        self._task_list.setStyleSheet(
            f"QListWidget {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; }}"
            f"QListWidget::item {{ padding: 8px; border-bottom: 1px solid "
            f"{self._theme.get('secondary', '#eee')}; }}"
            f"QListWidget::item:selected {{ background-color: {self._theme.get('accent', '#4a90d9')}; color: #fff; }}"
        )
        self._task_list.currentRowChanged.connect(self._on_task_selected)
        layout.addWidget(self._task_list)

        parent_layout.addWidget(card, stretch=3)

    # -- detail panel ---------------------------------------------------

    def _build_detail_panel(self, parent_layout: QHBoxLayout) -> None:
        card = CardFrame(self._theme)
        self._detail_layout = QVBoxLayout(card)
        self._detail_layout.addWidget(SectionTitle("Task Details", self._theme))

        self._detail_title = BodyLabel("Select a task to view details", self._theme)
        self._detail_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._detail_layout.addWidget(self._detail_title)

        self._detail_priority = BodyLabel("Priority: --", self._theme)
        self._detail_category = BodyLabel("Category: --", self._theme)
        self._detail_energy = BodyLabel("Energy: --", self._theme)
        self._detail_due = BodyLabel("Due: --", self._theme)

        for w in (self._detail_priority, self._detail_category,
                  self._detail_energy, self._detail_due):
            self._detail_layout.addWidget(w)

        self._detail_layout.addWidget(BodyLabel("Notes:", self._theme))
        self._detail_notes = QTextEdit()
        self._detail_notes.setReadOnly(True)
        self._detail_notes.setMaximumHeight(100)
        self._detail_notes.setStyleSheet(
            f"QTextEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; padding: 6px; }}"
        )
        self._detail_layout.addWidget(self._detail_notes)

        # Subtasks
        self._detail_layout.addWidget(BodyLabel("Subtasks:", self._theme))
        self._subtask_list = QListWidget()
        self._subtask_list.setMaximumHeight(120)
        self._subtask_list.setStyleSheet(
            f"QListWidget {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; }}"
        )
        self._detail_layout.addWidget(self._subtask_list)

        # Tags
        self._detail_tags = BodyLabel("Tags: --", self._theme)
        self._detail_layout.addWidget(self._detail_tags)

        # Values alignment
        self._detail_values = BodyLabel("Values: --", self._theme)
        self._detail_layout.addWidget(self._detail_values)

        self._detail_layout.addStretch()
        parent_layout.addWidget(card, stretch=2)

    # -- action buttons -------------------------------------------------

    def _build_action_buttons(self) -> None:
        card = CardFrame(self._theme)
        layout = QHBoxLayout(card)
        layout.setSpacing(10)

        actions = [
            ("Add Task", self._add_task_dialog),
            ("Edit Task", self._edit_task),
            ("Delete Task", self._delete_task),
            ("Decompose Task", self._decompose_task),
            ("Mark Complete", self._mark_complete),
        ]
        for label, slot in actions:
            btn = AccentButton(label, self._theme)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        layout.addStretch()

        # Undo / Redo
        undo_btn = AccentButton("Undo", self._theme)
        undo_btn.clicked.connect(self._undo)
        layout.addWidget(undo_btn)

        redo_btn = AccentButton("Redo", self._theme)
        redo_btn.clicked.connect(self._redo)
        layout.addWidget(redo_btn)

        self._root.addWidget(card)

    # -- statistics -----------------------------------------------------

    def _build_statistics(self) -> None:
        card = CardFrame(self._theme)
        layout = QHBoxLayout(card)
        layout.setSpacing(24)

        self._stat_total = BodyLabel("Total: 0", self._theme)
        self._stat_completed_today = BodyLabel("Completed today: 0", self._theme)
        self._stat_rate = BodyLabel("Completion rate: 0%", self._theme)

        self._completion_bar = QProgressBar()
        self._completion_bar.setMaximum(100)
        self._completion_bar.setValue(0)
        self._completion_bar.setTextVisible(True)
        self._completion_bar.setFormat("Completion: %p%")
        self._completion_bar.setStyleSheet(
            f"QProgressBar {{ border: 1px solid {self._theme.get('secondary', '#ccc')}; "
            f"border-radius: 6px; text-align: center; height: 20px; "
            f"background-color: {self._theme.get('background', '#f0f0f0')}; }}"
            f"QProgressBar::chunk {{ background-color: {self._theme.get('success', '#27ae60')}; "
            f"border-radius: 6px; }}"
        )

        for w in (self._stat_total, self._stat_completed_today, self._stat_rate):
            layout.addWidget(w)
        layout.addWidget(self._completion_bar, stretch=1)

        self._root.addWidget(card)

    # ------------------------------------------------------------------
    # Data operations
    # ------------------------------------------------------------------

    def _get_tasks(self) -> list:
        if not self._task_manager:
            return []
        try:
            return list(self._task_manager.tasks)
        except (AttributeError, TypeError):
            return []

    def _get_selected_task(self) -> Any:
        row = self._task_list.currentRow()
        tasks = self._filtered_tasks()
        if 0 <= row < len(tasks):
            return tasks[row]
        return None

    def _filtered_tasks(self) -> list:
        tasks = self._get_tasks()
        priority = self._priority_filter.currentText()
        category = self._category_filter.currentText()
        max_energy = self._energy_filter.value()
        show_completed = self._show_completed.isChecked()
        search = self._search_box.text().strip().lower()

        filtered = []
        for t in tasks:
            if not show_completed and getattr(t, "completed", False):
                continue
            if priority != "All":
                tp = getattr(t, "priority", None)
                tp_name = tp.name if tp is not None and hasattr(tp, "name") else str(tp)
                if tp_name.capitalize() != priority:
                    continue
            if category != "All":
                tc = getattr(t, "category", None)
                tc_name = tc.value if tc is not None and hasattr(tc, "value") else str(tc)
                if tc_name != category:
                    continue
            energy = getattr(t, "energy_required", 0)
            if energy > max_energy:
                continue
            if search and search not in getattr(t, "title", "").lower():
                continue
            filtered.append(t)

        sort_key = self._sort_combo.currentText()
        if sort_key == "Priority":
            filtered.sort(
                key=lambda t: getattr(getattr(t, "priority", None), "value", 0),
                reverse=True,
            )
        elif sort_key == "Due Date":
            filtered.sort(key=lambda t: str(getattr(t, "due_date", "") or "9999"))
        elif sort_key == "Energy":
            filtered.sort(key=lambda t: getattr(t, "energy_required", 0))
        elif sort_key == "Created Date":
            filtered.sort(
                key=lambda t: str(getattr(t, "created_at", "")),
                reverse=True,
            )
        return filtered

    def _refresh_task_list(self) -> None:
        self._task_list.clear()
        tasks = self._filtered_tasks()
        for task in tasks:
            title = getattr(task, "title", "Untitled")
            priority = getattr(task, "priority", None)
            priority_name = priority.name if priority is not None and hasattr(priority, "name") else str(priority)
            energy = getattr(task, "energy_required", 0)
            completed = getattr(task, "completed", False)
            due = getattr(task, "due_date", None)
            recurring = getattr(task, "recurring", False)

            prefix = "[x] " if completed else "[ ] "
            recurring_icon = " [R]" if recurring else ""
            due_str = f" (due {due})" if due else ""
            text = f"{prefix}[{priority_name}] {title}{due_str}  E:{energy}{recurring_icon}"

            item = QListWidgetItem(text)
            colour = _PRIORITY_COLOURS.get(priority_name.capitalize(), "#888")
            item.setForeground(QColor(colour))
            self._task_list.addItem(item)

        self._refresh_statistics()

    def _refresh_statistics(self) -> None:
        tasks = self._get_tasks()
        total = len(tasks)
        completed = [t for t in tasks if getattr(t, "completed", False)]
        today = date.today()
        completed_today = [
            t for t in completed
            if hasattr(t, "completed_at") and t.completed_at
            and str(t.completed_at)[:10] == str(today)
        ]
        rate = int(len(completed) / total * 100) if total else 0

        self._stat_total.setText(f"Total: {total}")
        self._stat_completed_today.setText(f"Completed today: {len(completed_today)}")
        self._stat_rate.setText(f"Completion rate: {rate}%")
        self._completion_bar.setValue(rate)

    def _on_task_selected(self, row: int) -> None:
        task = self._get_selected_task()
        if not task:
            self._detail_title.setText("Select a task to view details")
            return

        self._detail_title.setText(getattr(task, "title", "Untitled"))
        priority = getattr(task, "priority", None)
        priority_name = priority.name if priority is not None and hasattr(priority, "name") else str(priority)
        self._detail_priority.setText(f"Priority: {priority_name}")
        category = getattr(task, "category", None)
        category_name = category.value if category is not None and hasattr(category, "value") else str(category)
        self._detail_category.setText(f"Category: {category_name}")
        self._detail_energy.setText(
            f"Energy required: {getattr(task, 'energy_required', '--')}"
        )
        self._detail_due.setText(
            f"Due: {getattr(task, 'due_date', '--') or 'Not set'}"
        )
        self._detail_notes.setPlainText(getattr(task, "notes", "") or "")

        # Subtasks
        self._subtask_list.clear()
        subtasks = getattr(task, "subtasks", []) or []
        for st in subtasks:
            st_title = st.get("title", str(st)) if isinstance(st, dict) else str(st)
            self._subtask_list.addItem(st_title)

        tags = getattr(task, "tags", []) or []
        self._detail_tags.setText(
            f"Tags: {', '.join(tags)}" if tags else "Tags: --"
        )
        values = getattr(task, "values", []) or []
        self._detail_values.setText(
            f"Values: {', '.join(values)}" if values else "Values: --"
        )

    # -- task actions ---------------------------------------------------

    def _add_task_from_nlp(self) -> None:
        text = self._nlp_input.text().strip()
        if not text:
            return

        if self._nlp_parser and hasattr(self._nlp_parser, "parse"):
            try:
                parsed = self._nlp_parser.parse(text)
                if self._task_manager and hasattr(self._task_manager, "add_task"):
                    from core.task_manager import Task, TaskCategory, TaskPriority
                    priority_map = {
                        "urgent": TaskPriority.Urgent,
                        "high": TaskPriority.High,
                        "medium": TaskPriority.Medium,
                        "low": TaskPriority.Low,
                    }
                    category_map = {c.value: c for c in TaskCategory}
                    p = getattr(parsed, "priority", None)
                    p_val = p.value if p is not None and hasattr(p, "value") else str(p).lower() if p else "medium"
                    task = Task(
                        title=getattr(parsed, "title", text),
                        priority=priority_map.get(p_val, TaskPriority.Medium),
                        category=category_map.get(
                            getattr(parsed, "category", "Other"), TaskCategory.Other
                        ),
                        energy_required=getattr(parsed, "energy", 50),
                        due_date=getattr(parsed, "due_date", None),
                    )
                    self._push_undo("add", task)
                    self._task_manager.add_task(task)
                    self.task_added.emit()
            except (AttributeError, TypeError):
                self._add_task_simple(text)
        else:
            self._add_task_simple(text)

        self._nlp_input.clear()
        self._refresh_task_list()

    def _add_task_simple(self, text: str) -> None:
        if not self._task_manager:
            return
        try:
            from core.task_manager import Task, TaskCategory, TaskPriority
            task = Task(
                title=text,
                priority=TaskPriority.Medium,
                category=TaskCategory.Other,
                energy_required=50,
            )
            self._push_undo("add", task)
            self._task_manager.add_task(task)
            self.task_added.emit()
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Add task error: {exc}")

    def _add_task_dialog(self) -> None:
        self._nlp_input.setFocus()

    def _edit_task(self) -> None:
        task = self._get_selected_task()
        if not task:
            QMessageBox.information(self, "Edit", "Select a task first.")
            return
        QMessageBox.information(
            self, "Edit Task",
            "Edit the task title in the NLP bar and re-add, or modify via the detail panel.",
        )

    def _delete_task(self) -> None:
        task = self._get_selected_task()
        if not task:
            QMessageBox.information(self, "Delete", "Select a task first.")
            return
        reply = QMessageBox.question(
            self, "Delete Task",
            f"Delete '{getattr(task, 'title', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._push_undo("delete", task)
            if self._task_manager:
                try:
                    self._task_manager.tasks.remove(task)
                    if hasattr(self._task_manager, "_save_tasks"):
                        self._task_manager._save_tasks()
                except ValueError:
                    pass
            self._refresh_task_list()

    def _decompose_task(self) -> None:
        task = self._get_selected_task()
        if not task:
            QMessageBox.information(self, "Decompose", "Select a task first.")
            return
        title = getattr(task, "title", "Task")
        subtask_names = [
            f"Plan: {title}",
            f"Start: {title}",
            f"Complete: {title}",
            f"Review: {title}",
        ]
        if self._task_manager:
            try:
                from core.task_manager import Task, TaskCategory, TaskPriority
                for st_name in subtask_names:
                    sub = Task(
                        title=st_name,
                        priority=getattr(task, "priority", TaskPriority.Medium),
                        category=getattr(task, "category", TaskCategory.Other),
                        energy_required=max(1, getattr(task, "energy_required", 50) // 4),
                        due_date=getattr(task, "due_date", None),
                    )
                    self._task_manager.add_task(sub)
            except (AttributeError, TypeError) as exc:
                logger.debug(f"Decompose task error: {exc}")
        self._refresh_task_list()
        QMessageBox.information(self, "Decomposed", f"Created {len(subtask_names)} subtasks.")

    def _mark_complete(self) -> None:
        task = self._get_selected_task()
        if not task:
            QMessageBox.information(self, "Complete", "Select a task first.")
            return
        self._push_undo("complete", task)
        if self._task_manager and hasattr(self._task_manager, "complete_task"):
            self._task_manager.complete_task(task)
        else:
            task.completed = True
            task.completed_at = datetime.now()
        self.task_completed.emit()
        self._refresh_task_list()

    # -- undo / redo ----------------------------------------------------

    def _push_undo(self, action: str, task: Any) -> None:
        self._undo_stack.append({"action": action, "task": task})
        self._redo_stack.clear()

    def _undo(self) -> None:
        if not self._undo_stack:
            QMessageBox.information(self, "Undo", "Nothing to undo.")
            return
        entry = self._undo_stack.pop()
        self._redo_stack.append(entry)
        action = entry["action"]
        task = entry["task"]

        if action == "add" and self._task_manager:
            try:
                self._task_manager.tasks.remove(task)
                if hasattr(self._task_manager, "_save_tasks"):
                    self._task_manager._save_tasks()
            except ValueError:
                pass
        elif action == "delete" and self._task_manager:
            self._task_manager.tasks.append(task)
            if hasattr(self._task_manager, "_save_tasks"):
                self._task_manager._save_tasks()
        elif action == "complete":
            task.completed = False
            task.completed_at = None
            if self._task_manager and hasattr(self._task_manager, "_save_tasks"):
                self._task_manager._save_tasks()
        self._refresh_task_list()

    def _redo(self) -> None:
        if not self._redo_stack:
            QMessageBox.information(self, "Redo", "Nothing to redo.")
            return
        entry = self._redo_stack.pop()
        self._undo_stack.append(entry)
        action = entry["action"]
        task = entry["task"]

        if action == "add" and self._task_manager:
            self._task_manager.tasks.append(task)
            if hasattr(self._task_manager, "_save_tasks"):
                self._task_manager._save_tasks()
        elif action == "delete" and self._task_manager:
            try:
                self._task_manager.tasks.remove(task)
                if hasattr(self._task_manager, "_save_tasks"):
                    self._task_manager._save_tasks()
            except ValueError:
                pass
        elif action == "complete":
            task.completed = True
            task.completed_at = datetime.now()
            if self._task_manager and hasattr(self._task_manager, "_save_tasks"):
                self._task_manager._save_tasks()
        self._refresh_task_list()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
