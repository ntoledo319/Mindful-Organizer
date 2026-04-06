"""
Sleep tracking widget for Mindful Organizer.

Provides a sleep entry form with time pickers, quality slider, interruption
count, notes, sleep log, statistics (average duration, quality, debt), and
condition-specific sleep tips.
"""

from __future__ import annotations

import json
import logging
import statistics as stats_mod
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QSlider, QSpinBox,
    QTimeEdit, QTextEdit, QListWidget, QListWidgetItem,
    QGroupBox, QMessageBox,
)
from PyQt6.QtCore import Qt, QTime, pyqtSignal
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Condition-specific sleep tips
# ---------------------------------------------------------------------------

_SLEEP_TIPS: Dict[str, List[str]] = {
    "General": [
        "Keep a consistent sleep schedule, even on weekends.",
        "Avoid screens 30 minutes before bed.",
        "Keep your bedroom cool, dark, and quiet.",
        "Avoid caffeine after 2 PM.",
    ],
    "ADHD": [
        "Use a wind-down routine with clear steps.",
        "Try white noise or background sounds to quiet a busy mind.",
        "Set an alarm to start your bedtime routine.",
        "Keep a notepad by the bed to capture racing thoughts.",
    ],
    "Anxiety": [
        "Practice 4-7-8 breathing before bed.",
        "Write down worries in a journal to externalize them.",
        "Avoid checking news or email close to bedtime.",
        "Use progressive muscle relaxation to release tension.",
    ],
    "Depression": [
        "Aim for 7-9 hours -- oversleeping can worsen low mood.",
        "Get sunlight exposure within 30 minutes of waking.",
        "Avoid naps longer than 20 minutes.",
        "Gentle morning exercise can improve sleep quality.",
    ],
    "OCD": [
        "Set a specific 'lights out' time and stick to it.",
        "Limit checking behaviours before bed.",
        "Use a simple, consistent bedtime ritual.",
        "If intrusive thoughts arise, practice 'noting' them without engaging.",
    ],
    "PTSD": [
        "Create a safe, comforting sleep environment.",
        "Use grounding techniques if you wake from nightmares.",
        "Consider a nightlight if darkness triggers anxiety.",
        "Discuss nightmare-specific treatments with your therapist.",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _section_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
    return label


def _body_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    return label


def _accent_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

class SleepWidget(QWidget):
    """Sleep tracking tab with entry form, log, stats, and tips."""

    entry_saved = pyqtSignal(dict)

    def __init__(self, main_window: Any, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        self._sleep_tracker = None
        try:
            self._sleep_tracker = main_window.sleep_tracker
        except Exception:
            pass

        self._entries: List[Dict[str, Any]] = []
        self._load_entries()
        self._build_ui()
        self._refresh_log()
        self._refresh_stats()
        self._refresh_tips()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _data_dir(self) -> Path:
        try:
            return Path(self.main_window.data_dir)
        except Exception:
            p = Path.home() / ".mindful_optimizer"
            p.mkdir(parents=True, exist_ok=True)
            return p

    def _data_file(self) -> Path:
        d = self._data_dir()
        d.mkdir(parents=True, exist_ok=True)
        return d / "sleep_entries.json"

    def _load_entries(self) -> None:
        path = self._data_file()
        if path.exists():
            try:
                with open(path) as fh:
                    self._entries = json.load(fh)
            except Exception:
                pass

    def _save_entries(self) -> None:
        try:
            with open(self._data_file(), "w") as fh:
                json.dump(self._entries, fh, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save sleep entries: {e}")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        self._root = QVBoxLayout(container)
        self._root.setSpacing(16)
        self._root.setContentsMargins(24, 24, 24, 24)
        scroll.setWidget(container)

        self._root.addWidget(_section_title("Sleep Tracker"))

        body = QHBoxLayout()
        body.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(12)
        self._build_entry_form(left)
        self._build_tips(left)
        left.addStretch()
        body.addLayout(left, stretch=3)

        right = QVBoxLayout()
        right.setSpacing(12)
        self._build_log(right)
        self._build_stats(right)
        right.addStretch()
        body.addLayout(right, stretch=2)

        self._root.addLayout(body)
        self._root.addStretch()

    # -- entry form -----------------------------------------------------

    def _build_entry_form(self, parent: QVBoxLayout) -> None:
        group = QGroupBox("Log Sleep")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Bedtime
        bed_row = QHBoxLayout()
        bed_row.addWidget(_body_label("Bedtime:"))
        self._bedtime = QTimeEdit()
        self._bedtime.setDisplayFormat("HH:mm")
        self._bedtime.setTime(QTime(22, 30))
        bed_row.addWidget(self._bedtime)
        bed_row.addStretch()
        layout.addLayout(bed_row)

        # Wake time
        wake_row = QHBoxLayout()
        wake_row.addWidget(_body_label("Wake time:"))
        self._waketime = QTimeEdit()
        self._waketime.setDisplayFormat("HH:mm")
        self._waketime.setTime(QTime(7, 0))
        wake_row.addWidget(self._waketime)
        wake_row.addStretch()
        layout.addLayout(wake_row)

        # Quality slider
        qual_row = QHBoxLayout()
        qual_row.addWidget(_body_label("Quality:"))
        self._quality_slider = QSlider(Qt.Orientation.Horizontal)
        self._quality_slider.setRange(1, 10)
        self._quality_slider.setValue(5)
        self._quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._quality_slider.setTickInterval(1)
        qual_row.addWidget(self._quality_slider)
        self._quality_value = QLabel("5 / 10")
        self._quality_slider.valueChanged.connect(
            lambda v: self._quality_value.setText(f"{v} / 10")
        )
        qual_row.addWidget(self._quality_value)
        layout.addLayout(qual_row)

        # Interruptions
        int_row = QHBoxLayout()
        int_row.addWidget(_body_label("Interruptions:"))
        self._interruptions = QSpinBox()
        self._interruptions.setRange(0, 20)
        self._interruptions.setValue(0)
        int_row.addWidget(self._interruptions)
        int_row.addStretch()
        layout.addLayout(int_row)

        # Notes
        layout.addWidget(_body_label("Notes:"))
        self._notes = QTextEdit()
        self._notes.setMaximumHeight(80)
        self._notes.setPlaceholderText("Dreams, sleep aids used, anything notable...")
        layout.addWidget(self._notes)

        # Save button
        save_btn = _accent_button("Log Sleep")
        save_btn.clicked.connect(self._save_entry)
        layout.addWidget(save_btn)

        parent.addWidget(group)

    # -- log ------------------------------------------------------------

    def _build_log(self, parent: QVBoxLayout) -> None:
        group = QGroupBox("Sleep Log")
        layout = QVBoxLayout(group)
        self._log_list = QListWidget()
        self._log_list.setMinimumHeight(200)
        layout.addWidget(self._log_list)
        parent.addWidget(group)

    # -- stats ----------------------------------------------------------

    def _build_stats(self, parent: QVBoxLayout) -> None:
        group = QGroupBox("Statistics")
        layout = QVBoxLayout(group)

        self._avg_duration_label = _body_label("Average duration: --")
        self._avg_quality_label = _body_label("Average quality: --")
        self._sleep_debt_label = _body_label("Sleep debt (7 days): --")

        layout.addWidget(self._avg_duration_label)
        layout.addWidget(self._avg_quality_label)
        layout.addWidget(self._sleep_debt_label)
        parent.addWidget(group)

    # -- tips -----------------------------------------------------------

    def _build_tips(self, parent: QVBoxLayout) -> None:
        group = QGroupBox("Condition-Specific Sleep Tips")
        layout = QVBoxLayout(group)
        self._tips_label = _body_label("")
        layout.addWidget(self._tips_label)
        parent.addWidget(group)

    # ------------------------------------------------------------------
    # Data operations
    # ------------------------------------------------------------------

    def _calc_duration(self, bedtime_str: str, waketime_str: str) -> float:
        try:
            bed = datetime.strptime(bedtime_str, "%H:%M")
            wake = datetime.strptime(waketime_str, "%H:%M")
            if wake <= bed:
                wake += timedelta(days=1)
            return round((wake - bed).total_seconds() / 3600, 2)
        except (ValueError, TypeError):
            return 0.0

    def _save_entry(self) -> None:
        bed_str = self._bedtime.time().toString("HH:mm")
        wake_str = self._waketime.time().toString("HH:mm")
        duration = self._calc_duration(bed_str, wake_str)

        entry: Dict[str, Any] = {
            "date": date.today().isoformat(),
            "bedtime": bed_str,
            "wake_time": wake_str,
            "duration_hours": duration,
            "quality": self._quality_slider.value(),
            "interruptions": self._interruptions.value(),
            "notes": self._notes.toPlainText().strip(),
            "created_at": datetime.now().isoformat(),
        }

        # Try to save via sleep tracker backend
        try:
            if self._sleep_tracker and hasattr(self._sleep_tracker, "log_sleep"):
                self._sleep_tracker.log_sleep(
                    date=entry["date"],
                    bedtime=bed_str,
                    wake_time=wake_str,
                    quality=entry["quality"],
                    interruptions=entry["interruptions"],
                    notes=entry["notes"],
                )
        except Exception:
            pass

        self._entries.append(entry)
        self._save_entries()
        self.entry_saved.emit(entry)

        # Reset form
        self._quality_slider.setValue(5)
        self._interruptions.setValue(0)
        self._notes.clear()

        self._refresh_log()
        self._refresh_stats()
        QMessageBox.information(self, "Saved", "Sleep entry saved.")

    def _refresh_log(self) -> None:
        self._log_list.clear()
        entries = sorted(self._entries, key=lambda e: e.get("date", ""), reverse=True)
        for e in entries[:50]:
            dt = e.get("date", "?")
            dur = e.get("duration_hours", 0)
            qual = e.get("quality", "?")
            ints = e.get("interruptions", 0)
            bed = e.get("bedtime", "?")
            wake = e.get("wake_time", "?")
            text = f"{dt} | {bed}-{wake} | {dur:.1f}h | Quality: {qual}/10 | Int: {ints}"
            self._log_list.addItem(text)

    def _refresh_stats(self) -> None:
        if not self._entries:
            return

        durations = [e.get("duration_hours", 0) for e in self._entries if e.get("duration_hours")]
        qualities = [e.get("quality", 0) for e in self._entries if e.get("quality")]

        if durations:
            avg_dur = stats_mod.mean(durations)
            self._avg_duration_label.setText(f"Average duration: {avg_dur:.1f} hours")

            # Sleep debt (8h target, last 7 days)
            recent = durations[-7:]
            debt = sum(max(0, 8.0 - d) for d in recent)
            self._sleep_debt_label.setText(f"Sleep debt (7 days): {debt:.1f} hours")

        if qualities:
            avg_qual = stats_mod.mean(qualities)
            self._avg_quality_label.setText(f"Average quality: {avg_qual:.1f} / 10")

    def _refresh_tips(self) -> None:
        conditions: List[str] = ["General"]
        try:
            profile = self.main_window.profile_manager.current_profile
            if profile and hasattr(profile, "conditions") and profile.conditions:
                for c in profile.conditions:
                    name = c.value if hasattr(c, "value") else str(c)
                    conditions.append(name)
        except Exception:
            pass

        tips: List[str] = []
        for cond in conditions:
            tips.extend(_SLEEP_TIPS.get(cond, []))

        self._tips_label.setText("\n".join(f"- {t}" for t in tips[:8]))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Called by main window on close."""
        self._save_entries()
