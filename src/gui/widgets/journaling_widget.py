"""
Journaling widget -- prompted writing with mood tracking.

Features a daily prompt system, rich text editing, mood before/after
sliders, tag entry, search, streak display, and export capability.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QScrollArea,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir
from gui.components import AccentButton, BodyLabel, CardFrame, SectionTitle

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt database (condition-aware)
# ---------------------------------------------------------------------------

_PROMPTS: dict[str, list[str]] = {
    "General": [
        "What are you most grateful for today?",
        "Describe a moment of peace you experienced recently.",
        "What small win can you celebrate today?",
        "Write about something that made you smile this week.",
        "What would you tell your younger self right now?",
        "What does a perfect day look like to you?",
        "What is one thing you want to let go of today?",
        "Describe your ideal morning routine.",
    ],
    "Anxiety": [
        "What is worrying you right now? Can you challenge that thought?",
        "List five things you can see, four you can touch, three you can hear.",
        "What is the worst that could happen? How likely is it really?",
        "When was the last time your worry did NOT come true?",
        "Write a letter to your anxiety. What would you say?",
    ],
    "Depression": [
        "Name one thing you accomplished today, no matter how small.",
        "What would you do if you had unlimited energy right now?",
        "Write about a time you overcame something difficult.",
        "What are three qualities you like about yourself?",
        "Who in your life makes you feel supported?",
    ],
    "ADHD": [
        "What was your biggest distraction today and how did you handle it?",
        "Brain dump: write everything on your mind for 5 minutes.",
        "What systems or tools helped you stay on track this week?",
        "Describe a moment of hyperfocus. What triggered it?",
        "What is one task you keep avoiding and why?",
    ],
    "OCD": [
        "Describe an urge you successfully resisted today.",
        "What would life look like without compulsions?",
        "Write about uncertainty. Can you sit with not knowing?",
        "What would you do with the time spent on rituals?",
        "Describe a values-driven action you took despite discomfort.",
    ],
    "PTSD": [
        "Describe a safe place in vivid detail -- sights, sounds, smells.",
        "What helped you feel grounded today?",
        "Write about a positive memory that brings comfort.",
        "What does safety mean to you right now?",
        "What strengths have carried you through difficult times?",
    ],
}


def _daily_prompt(conditions: list[str]) -> str:
    """Pick a deterministic prompt based on today's date and conditions."""
    today_str = date.today().isoformat()
    seed = int(hashlib.md5(today_str.encode()).hexdigest(), 16)
    pool: list[str] = list(_PROMPTS.get("General", []))
    for cond in conditions:
        pool.extend(_PROMPTS.get(cond, []))
    if not pool:
        pool = ["Write about anything on your mind today."]
    return pool[seed % len(pool)]


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------


class JournalingWidget(QWidget):
    """Journaling tab with prompts, editor, history, and streak tracking."""

    entry_saved = pyqtSignal(dict)
    crisis_requested = pyqtSignal()  # emitted when an entry trips risk-language detection

    def __init__(
        self,
        theme: dict[str, str],
        journal_manager: Any = None,
        profile_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._journal_manager = journal_manager
        self._profile_manager = profile_manager

        # In-memory entries if no manager
        self._entries: list[dict[str, Any]] = []
        self._load_entries()

        self._build_ui()
        self._refresh_prompt()
        self._refresh_history()
        self._update_streak()

    # ------------------------------------------------------------------
    # Persistence fallback
    # ------------------------------------------------------------------

    def _data_file(self) -> Path | None:
        if self._journal_manager and hasattr(self._journal_manager, "data_dir"):
            return Path(self._journal_manager.data_dir) / "journal_entries.json"
        home = get_data_dir() / "journal_entries.json"
        home.parent.mkdir(parents=True, exist_ok=True)
        return home

    def _load_entries(self) -> None:
        if self._journal_manager and hasattr(self._journal_manager, "entries"):
            self._entries = list(self._journal_manager.entries)
            return
        path = self._data_file()
        if path and path.exists():
            try:
                with open(path) as fh:
                    self._entries = json.load(fh)
            except (json.JSONDecodeError, OSError):
                self._entries = []

    def _save_entries(self) -> None:
        if self._journal_manager and hasattr(self._journal_manager, "save_entry"):
            return  # manager handles persistence
        path = self._data_file()
        if path:
            try:
                with open(path, "w") as fh:
                    json.dump(self._entries, fh, indent=2, default=str)
            except (OSError, TypeError) as exc:
                logger.warning(f"Failed to save journal entries: {exc}")

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

        self._root.addWidget(SectionTitle("Journal", self._theme))

        body = QHBoxLayout()
        body.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(12)
        self._build_prompt_section(left)
        self._build_editor(left)
        left.addStretch()
        body.addLayout(left, stretch=3)

        right = QVBoxLayout()
        right.setSpacing(12)
        self._build_streak_card(right)
        self._build_search(right)
        self._build_history_list(right)
        right.addStretch()
        body.addLayout(right, stretch=2)

        self._root.addLayout(body)
        self._root.addStretch()

    # -- prompt ---------------------------------------------------------

    def _build_prompt_section(self, parent: QVBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Prompt of the Day", self._theme))

        self._prompt_label = BodyLabel("", self._theme)
        self._prompt_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Normal))
        self._prompt_label.setMinimumHeight(50)
        layout.addWidget(self._prompt_label)

        row = QHBoxLayout()
        self._prompt_category = QComboBox()
        self._prompt_category.addItems(list(_PROMPTS.keys()))
        row.addWidget(self._prompt_category)

        new_prompt_btn = AccentButton("Get New Prompt", self._theme)
        new_prompt_btn.clicked.connect(self._new_prompt)
        row.addWidget(new_prompt_btn)
        row.addStretch()
        layout.addLayout(row)

        parent.addWidget(card)

    # -- editor ---------------------------------------------------------

    def _build_editor(self, parent: QVBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Write Entry", self._theme))

        # Mood before
        mood_row = QHBoxLayout()
        mood_row.addWidget(BodyLabel("Mood before:", self._theme))
        self._mood_before_slider = QSlider(Qt.Orientation.Horizontal)
        self._mood_before_slider.setRange(1, 10)
        self._mood_before_slider.setValue(5)
        self._mood_before_val = BodyLabel("5", self._theme)
        self._mood_before_slider.valueChanged.connect(
            lambda v: self._mood_before_val.setText(str(v))
        )
        mood_row.addWidget(self._mood_before_slider)
        mood_row.addWidget(self._mood_before_val)
        layout.addLayout(mood_row)

        # Text editor
        self._editor = QTextEdit()
        self._editor.setMinimumHeight(250)
        self._editor.setPlaceholderText("Start writing here...")
        self._editor.setStyleSheet(
            f"QTextEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 8px; "
            f"padding: 12px; font-size: 14px; line-height: 1.6; }}"
        )
        self._editor.textChanged.connect(self._update_word_count)
        layout.addWidget(self._editor)

        # Word count
        self._word_count_label = BodyLabel("Words: 0", self._theme)
        layout.addWidget(self._word_count_label)

        # Mood after
        mood_after_row = QHBoxLayout()
        mood_after_row.addWidget(BodyLabel("Mood after:", self._theme))
        self._mood_after_slider = QSlider(Qt.Orientation.Horizontal)
        self._mood_after_slider.setRange(1, 10)
        self._mood_after_slider.setValue(5)
        self._mood_after_val = BodyLabel("5", self._theme)
        self._mood_after_slider.valueChanged.connect(lambda v: self._mood_after_val.setText(str(v)))
        mood_after_row.addWidget(self._mood_after_slider)
        mood_after_row.addWidget(self._mood_after_val)
        layout.addLayout(mood_after_row)

        # Tags
        tags_row = QHBoxLayout()
        tags_row.addWidget(BodyLabel("Tags (comma-separated):", self._theme))
        self._tags_input = QLineEdit()
        self._tags_input.setPlaceholderText("e.g. gratitude, morning, therapy")
        self._tags_input.setStyleSheet(
            f"QLineEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; padding: 6px; }}"
        )
        tags_row.addWidget(self._tags_input)
        layout.addLayout(tags_row)

        # Buttons
        btn_row = QHBoxLayout()
        save_btn = AccentButton("Save Entry", self._theme)
        save_btn.clicked.connect(self._save_entry)
        btn_row.addWidget(save_btn)

        export_btn = AccentButton("Export Entries", self._theme)
        export_btn.clicked.connect(self._export_entries)
        btn_row.addWidget(export_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        parent.addWidget(card)

    # -- streak ---------------------------------------------------------

    def _build_streak_card(self, parent: QVBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Streak", self._theme))
        self._streak_label = BodyLabel("Current streak: 0 days", self._theme)
        self._streak_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(self._streak_label)
        parent.addWidget(card)

    # -- search ---------------------------------------------------------

    def _build_search(self, parent: QVBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Search Entries", self._theme))

        row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Keyword, date, or tag...")
        self._search_input.setStyleSheet(
            f"QLineEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; padding: 6px; }}"
        )
        self._search_input.textChanged.connect(self._search_entries)
        row.addWidget(self._search_input)
        layout.addLayout(row)
        parent.addWidget(card)

    # -- history --------------------------------------------------------

    def _build_history_list(self, parent: QVBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Journal History", self._theme))

        self._history_list = QListWidget()
        self._history_list.setMinimumHeight(300)
        self._history_list.setStyleSheet(
            f"QListWidget {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; }}"
            f"QListWidget::item {{ padding: 6px; }}"
            f"QListWidget::item:selected {{ background-color: {self._theme.get('accent', '#4a90d9')}; color: #fff; }}"
        )
        self._history_list.currentRowChanged.connect(self._on_history_selected)
        layout.addWidget(self._history_list)
        parent.addWidget(card)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _refresh_prompt(self) -> None:
        conditions = self._get_conditions()
        prompt = _daily_prompt(conditions)
        self._prompt_label.setText(prompt)

    def _new_prompt(self) -> None:
        category = self._prompt_category.currentText()
        pool = _PROMPTS.get(category, _PROMPTS["General"])
        import random

        self._prompt_label.setText(random.choice(pool))

    def _get_conditions(self) -> list[str]:
        conditions: list[str] = []
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "conditions") and profile.conditions:
                for c in profile.conditions:
                    conditions.append(c.value if hasattr(c, "value") else str(c))
        return conditions

    def _update_word_count(self) -> None:
        text = self._editor.toPlainText().strip()
        count = len(text.split()) if text else 0
        self._word_count_label.setText(f"Words: {count}")

    def _save_entry(self) -> None:
        text = self._editor.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Empty", "Write something before saving.")
            return

        tags = [t.strip() for t in self._tags_input.text().split(",") if t.strip()]
        entry: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "text": text,
            "mood_before": self._mood_before_slider.value(),
            "mood_after": self._mood_after_slider.value(),
            "tags": tags,
            "word_count": len(text.split()),
            "prompt": self._prompt_label.text(),
        }

        if self._journal_manager and hasattr(self._journal_manager, "save_entry"):
            with contextlib.suppress(Exception):
                self._journal_manager.save_entry(entry)

        self._entries.append(entry)
        self._save_entries()
        self.entry_saved.emit(entry)

        # Scan the entry for explicit self-harm / ideation language BEFORE the
        # routine "saved" toast. If matched, surface crisis resources prominently.
        risk_flagged = self._check_risk(text)

        # Reset
        self._editor.clear()
        self._tags_input.clear()
        self._mood_before_slider.setValue(5)
        self._mood_after_slider.setValue(5)

        self._refresh_history()
        self._update_streak()

        if risk_flagged:
            self._surface_crisis_resources()
        else:
            QMessageBox.information(self, "Saved", "Journal entry saved successfully.")

    def _check_risk(self, text: str) -> bool:
        """Return True if the entry contains explicit self-harm/ideation language."""
        try:
            from wellness.journal_analyzer import JournalAnalyzer

            return JournalAnalyzer().analyze(text).risk_flagged
        except Exception as exc:  # analysis must never block saving
            logger.debug("Journal risk analysis failed: %s", exc)
            return False

    def _surface_crisis_resources(self) -> None:
        """Show a prominent, supportive crisis prompt with one-tap access to help."""
        from wellness.journal_analyzer import _RISK_RESOURCE_INSIGHT

        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("You're not alone")
        box.setText(_RISK_RESOURCE_INSIGHT)
        open_crisis = box.addButton("Open crisis plan", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        if box.clickedButton() is open_crisis:
            self.crisis_requested.emit()

    def _refresh_history(self, filter_text: str = "") -> None:
        self._history_list.clear()
        entries = sorted(self._entries, key=lambda e: e.get("timestamp", ""), reverse=True)
        for entry in entries[:100]:
            dt = entry.get("date", entry.get("timestamp", "")[:10])
            text = entry.get("text", "")
            preview = text[:60].replace("\n", " ") + ("..." if len(text) > 60 else "")
            mood_b = entry.get("mood_before", "?")
            mood_a = entry.get("mood_after", "?")
            mood_change = ""
            if isinstance(mood_b, int | float) and isinstance(mood_a, int | float):
                diff = mood_a - mood_b
                if diff > 0:
                    mood_change = f" (+{diff})"
                elif diff < 0:
                    mood_change = f" ({diff})"

            display = f"{dt}  |  {preview}{mood_change}"
            if filter_text and filter_text.lower() not in display.lower():
                tags = entry.get("tags", [])
                if not any(filter_text.lower() in t.lower() for t in tags):
                    continue
            self._history_list.addItem(display)

    def _search_entries(self, text: str) -> None:
        self._refresh_history(filter_text=text)

    def _on_history_selected(self, row: int) -> None:
        entries = sorted(self._entries, key=lambda e: e.get("timestamp", ""), reverse=True)
        if 0 <= row < len(entries):
            entry = entries[row]
            self._editor.setPlainText(entry.get("text", ""))
            self._mood_before_slider.setValue(entry.get("mood_before", 5))
            self._mood_after_slider.setValue(entry.get("mood_after", 5))
            tags = entry.get("tags", [])
            self._tags_input.setText(", ".join(tags))

    def _update_streak(self) -> None:
        if not self._entries:
            self._streak_label.setText("Current streak: 0 days")
            return
        dates = sorted(
            {e.get("date", e.get("timestamp", "")[:10]) for e in self._entries}, reverse=True
        )
        streak = 0
        today = date.today()
        for i, d in enumerate(dates):
            try:
                entry_date = date.fromisoformat(d)
            except (ValueError, TypeError):
                continue
            expected = today - __import__("datetime").timedelta(days=i)
            if entry_date == expected:
                streak += 1
            else:
                break
        self._streak_label.setText(f"Current streak: {streak} day(s)")

    def _export_entries(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Journal Entries", "journal_entries.json", "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "w") as fh:
                json.dump(self._entries, fh, indent=2, default=str)
            QMessageBox.information(self, "Exported", f"Entries exported to {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Export failed: {exc}")

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
