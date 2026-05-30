"""
Global search dialog for Mindful Organizer.

Searches across tasks, journal entries, and mood entries with debounced
real-time filtering, category filter checkboxes, grouped results, and
double-click navigation to the relevant tab.
"""

from __future__ import annotations

import contextlib
import logging
from typing import Any

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Category prefixes
# ---------------------------------------------------------------------------

_CATEGORY_PREFIXES = {
    "tasks": "[T]",
    "journal": "[J]",
    "mood": "[M]",
}

_CATEGORY_TAB_NAMES = {
    "tasks": "task_manager",
    "journal": "journaling",
    "mood": "mood_tracker",
}


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

class SearchWidget(QDialog):
    """Global search dialog with debounced real-time search."""

    result_selected = pyqtSignal(str, str)  # (category, item_id)

    _DEBOUNCE_MS = 300

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.setWindowTitle("Search")
        self.setMinimumSize(600, 500)

        self._current_results: list[dict[str, Any]] = []

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._execute_search)

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(20, 16, 20, 16)

        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search tasks, journal entries, mood logs...")
        self._search_input.setFont(QFont("Segoe UI", 14))
        self._search_input.setMinimumHeight(44)
        self._search_input.textChanged.connect(self._on_text_changed)
        root.addWidget(self._search_input)

        # Filters
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Search in:"))
        self._filter_checks: dict[str, QCheckBox] = {}
        for cat_label, cat_key in [("Tasks", "tasks"), ("Journal", "journal"), ("Mood Entries", "mood")]:
            cb = QCheckBox(cat_label)
            cb.setChecked(True)
            cb.stateChanged.connect(lambda _: self._debounce_search())
            filter_row.addWidget(cb)
            self._filter_checks[cat_key] = cb
        filter_row.addStretch()
        root.addLayout(filter_row)

        # Results
        self._results_list = QListWidget()
        self._results_list.setMinimumHeight(300)
        self._results_list.itemDoubleClicked.connect(self._on_result_double_clicked)
        root.addWidget(self._results_list)

        # Close button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

        # Focus the search input
        self._search_input.setFocus()

    # ------------------------------------------------------------------
    # Key handling
    # ------------------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent | None) -> None:  # noqa: N802
        if event is not None and event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Search logic
    # ------------------------------------------------------------------

    def _on_text_changed(self, text: str) -> None:
        self._debounce_search()

    def _debounce_search(self) -> None:
        self._debounce_timer.stop()
        self._debounce_timer.start(self._DEBOUNCE_MS)

    def _execute_search(self) -> None:
        query = self._search_input.text().strip().lower()
        if not query:
            self._results_list.clear()
            self._current_results.clear()
            return

        results: list[dict[str, Any]] = []

        if self._filter_checks.get("tasks", QCheckBox()).isChecked():
            results.extend(self._search_tasks(query))

        if self._filter_checks.get("journal", QCheckBox()).isChecked():
            results.extend(self._search_journal(query))

        if self._filter_checks.get("mood", QCheckBox()).isChecked():
            results.extend(self._search_mood(query))

        self._current_results = results
        self._display_results(results)

    def _search_tasks(self, query: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            tm = self.main_window.task_manager
            if not tm:
                return results
            tasks = getattr(tm, "tasks", [])
            for task in tasks:
                title = getattr(task, "title", "").lower()
                notes = (getattr(task, "notes", "") or "").lower()
                if query in title or query in notes:
                    results.append({
                        "category": "tasks",
                        "title": getattr(task, "title", ""),
                        "detail": f"Priority: {getattr(task, 'priority', '?')} | "
                                  f"Due: {getattr(task, 'due_date', 'N/A')}",
                        "ref": task,
                    })
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Task search error: {exc}")
        return results

    def _search_journal(self, query: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            jm = self.main_window.journaling_manager
            if not jm:
                return results
            entries = []
            if hasattr(jm, "entries"):
                entries = jm.entries
            elif hasattr(jm, "_entries"):
                entries = jm._entries
            for entry in entries:
                text = ""
                dt = ""
                if isinstance(entry, dict):
                    text = entry.get("text", "").lower()
                    dt = entry.get("date", "")
                elif hasattr(entry, "text"):
                    text = entry.text.lower()
                    dt = getattr(entry, "date", "")
                else:
                    continue
                if query in text:
                    preview = text[:80].replace("\n", " ")
                    results.append({
                        "category": "journal",
                        "title": f"Journal: {dt}",
                        "detail": preview,
                        "ref": entry,
                    })
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Journal search error: {exc}")
        return results

    def _search_mood(self, query: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            # Search the manager that actually holds the entries. (The old code
            # read main_window.mood_analytics, which both crashed on construction
            # and carried no entries, so mood search always returned nothing.)
            mm = self.main_window.mood_manager
            if not mm:
                return results
            entries = getattr(mm, "entries", None) or getattr(mm, "_entries", [])
            for entry in entries:
                notes = ""
                if isinstance(entry, dict):
                    notes = entry.get("notes", "").lower()
                elif hasattr(entry, "notes"):
                    notes = (getattr(entry, "notes", "") or "").lower()
                if query in notes:
                    ts = ""
                    if hasattr(entry, "timestamp"):
                        ts = str(entry.timestamp)[:16]
                    elif isinstance(entry, dict):
                        ts = entry.get("timestamp", "")[:16]
                    score = ""
                    if hasattr(entry, "mood_score"):
                        score = str(entry.mood_score)
                    elif isinstance(entry, dict):
                        score = str(entry.get("mood_score", ""))
                    results.append({
                        "category": "mood",
                        "title": f"Mood: {ts}",
                        "detail": f"Score: {score} | {notes[:60]}",
                        "ref": entry,
                    })
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Mood search error: {exc}")
        return results

    def _display_results(self, results: list[dict[str, Any]]) -> None:
        self._results_list.clear()
        if not results:
            self._results_list.addItem("No results found.")
            return

        # Group by category
        grouped: dict[str, list[dict[str, Any]]] = {}
        for r in results:
            cat = r["category"]
            grouped.setdefault(cat, []).append(r)

        for cat, items in grouped.items():
            prefix = _CATEGORY_PREFIXES.get(cat, "[?]")
            header_item = QListWidgetItem(f"--- {prefix} {cat.upper()} ({len(items)} results) ---")
            header_item.setFlags(Qt.ItemFlag.NoItemFlags)
            header_font = header_item.font()
            header_font.setBold(True)
            header_item.setFont(header_font)
            self._results_list.addItem(header_item)

            for item in items[:20]:
                display = f"  {item['title']}  --  {item['detail']}"
                list_item = QListWidgetItem(display)
                self._results_list.addItem(list_item)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _on_result_double_clicked(self, item: QListWidgetItem) -> None:
        """Navigate to the tab for the selected result."""
        result = self._get_selected_result()
        if not result:
            return
        tab_name = _CATEGORY_TAB_NAMES.get(result["category"])
        if tab_name:
            with contextlib.suppress(Exception):
                self.main_window._switch_to_tab(tab_name)
        self.close()

    def _get_selected_result(self) -> dict[str, Any] | None:
        row = self._results_list.currentRow()
        if row < 0:
            return None
        result_idx = -1
        for i in range(self._results_list.count()):
            item = self._results_list.item(i)
            if item and item.flags() != Qt.ItemFlag.NoItemFlags:
                result_idx += 1
                if i == row and result_idx < len(self._current_results):
                    return self._current_results[result_idx]
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def focus_search(self) -> None:
        self._search_input.setFocus()
        self._search_input.selectAll()
