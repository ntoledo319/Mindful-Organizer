"""
Meditation tab for Mindful Organizer.

Provides meditation type selection, duration picker, large countdown timer,
start/pause/stop controls, pre/post session mood sliders, session history,
and mood-based meditation recommendations.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QComboBox, QSlider,
    QListWidget, QListWidgetItem, QGroupBox, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Meditation types
# ---------------------------------------------------------------------------

_MEDITATION_TYPES = [
    ("Mindfulness", "Focus on present-moment awareness and non-judgmental observation."),
    ("Body Scan", "Systematically scan through body parts, noticing sensations."),
    ("Loving Kindness", "Cultivate feelings of goodwill toward self and others."),
    ("Breath Awareness", "Focus attention solely on the breath."),
    ("Guided Visualization", "Follow a mental journey to a peaceful place."),
    ("Progressive Relaxation", "Tense and release muscle groups for deep relaxation."),
    ("Mantra", "Repeat a calming word or phrase to focus the mind."),
    ("Walking Meditation", "Bring mindful awareness to walking."),
    ("Open Awareness", "Rest in awareness itself, noticing whatever arises."),
]

_DURATION_OPTIONS = [5, 10, 15, 20, 30, 45, 60]

_MOOD_RECOMMENDATIONS = {
    (1, 3): ("Loving Kindness", "When mood is low, self-compassion practices can help."),
    (4, 5): ("Body Scan", "A body scan can help reconnect with physical sensations."),
    (6, 7): ("Mindfulness", "Maintain your good state with present-moment awareness."),
    (8, 10): ("Open Awareness", "Enjoy resting in open awareness."),
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

class MeditationWidget(QWidget):
    """Meditation timer and tracking tab."""

    session_completed = pyqtSignal(dict)

    def __init__(self, main_window: Any, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        self._meditation_manager = None
        try:
            self._meditation_manager = main_window.meditation_manager
        except Exception:
            pass

        # Session state
        self._running = False
        self._paused = False
        self._remaining_sec = 0
        self._total_sec = 0

        # Timer
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._tick)

        # Session history (local)
        self._sessions: List[Dict[str, Any]] = []
        self._load_sessions()

        self._build_ui()
        self._refresh_history()
        self._update_recommendation()

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

    def _sessions_file(self) -> Path:
        d = self._data_dir()
        d.mkdir(parents=True, exist_ok=True)
        return d / "meditation_sessions.json"

    def _load_sessions(self) -> None:
        path = self._sessions_file()
        if path.exists():
            try:
                with open(path) as fh:
                    self._sessions = json.load(fh)
            except Exception:
                pass

    def _save_sessions(self) -> None:
        try:
            with open(self._sessions_file(), "w") as fh:
                json.dump(self._sessions, fh, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save meditation sessions: {e}")

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

        self._root.addWidget(_section_title("Meditation"))

        # Type selector
        type_group = QGroupBox("Meditation Type")
        type_layout = QVBoxLayout(type_group)
        self._type_combo = QComboBox()
        for name, desc in _MEDITATION_TYPES:
            self._type_combo.addItem(name, desc)
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self._type_combo)
        self._type_desc_label = _body_label(_MEDITATION_TYPES[0][1])
        self._type_desc_label.setStyleSheet("font-style: italic;")
        type_layout.addWidget(self._type_desc_label)
        self._root.addWidget(type_group)

        # Duration selector
        dur_row = QHBoxLayout()
        dur_row.addWidget(_body_label("Duration:"))
        self._duration_combo = QComboBox()
        for mins in _DURATION_OPTIONS:
            self._duration_combo.addItem(f"{mins} minutes", mins)
        self._duration_combo.setCurrentIndex(1)  # Default 10 min
        dur_row.addWidget(self._duration_combo)
        dur_row.addStretch()
        self._root.addLayout(dur_row)

        # Large timer display
        self._timer_label = QLabel("10:00")
        self._timer_label.setFont(QFont("Segoe UI", 54, QFont.Weight.Bold))
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._root.addWidget(self._timer_label)

        # Controls
        ctrl_row = QHBoxLayout()
        self._start_btn = _accent_button("Start")
        self._start_btn.clicked.connect(self._start_session)
        ctrl_row.addWidget(self._start_btn)

        self._pause_btn = _accent_button("Pause")
        self._pause_btn.setEnabled(False)
        self._pause_btn.clicked.connect(self._pause_session)
        ctrl_row.addWidget(self._pause_btn)

        self._stop_btn = _accent_button("Stop")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_session)
        ctrl_row.addWidget(self._stop_btn)
        self._root.addLayout(ctrl_row)

        # Pre/post mood sliders
        mood_group = QGroupBox("Session Mood")
        mood_layout = QHBoxLayout(mood_group)

        pre_col = QVBoxLayout()
        pre_col.addWidget(_body_label("Pre-session mood (1-10):"))
        self._pre_mood_slider = QSlider(Qt.Orientation.Horizontal)
        self._pre_mood_slider.setRange(1, 10)
        self._pre_mood_slider.setValue(5)
        self._pre_mood_value = QLabel("5")
        self._pre_mood_slider.valueChanged.connect(
            lambda v: self._pre_mood_value.setText(str(v))
        )
        self._pre_mood_slider.valueChanged.connect(
            lambda _: self._update_recommendation()
        )
        pre_col.addWidget(self._pre_mood_slider)
        pre_col.addWidget(self._pre_mood_value)
        mood_layout.addLayout(pre_col)

        post_col = QVBoxLayout()
        post_col.addWidget(_body_label("Post-session mood (1-10):"))
        self._post_mood_slider = QSlider(Qt.Orientation.Horizontal)
        self._post_mood_slider.setRange(1, 10)
        self._post_mood_slider.setValue(5)
        self._post_mood_value = QLabel("5")
        self._post_mood_slider.valueChanged.connect(
            lambda v: self._post_mood_value.setText(str(v))
        )
        post_col.addWidget(self._post_mood_slider)
        post_col.addWidget(self._post_mood_value)
        mood_layout.addLayout(post_col)

        self._root.addWidget(mood_group)

        # Recommended meditation
        rec_group = QGroupBox("Recommended Based on Mood")
        rec_layout = QVBoxLayout(rec_group)
        self._recommendation_label = _body_label("Set your pre-session mood for a recommendation.")
        rec_layout.addWidget(self._recommendation_label)
        self._root.addWidget(rec_group)

        # Session history
        hist_group = QGroupBox("Recent Sessions")
        hist_layout = QVBoxLayout(hist_group)
        self._history_list = QListWidget()
        self._history_list.setMaximumHeight(200)
        hist_layout.addWidget(self._history_list)
        self._root.addWidget(hist_group)

        self._root.addStretch()

    # ------------------------------------------------------------------
    # Type change
    # ------------------------------------------------------------------

    def _on_type_changed(self, index: int) -> None:
        desc = self._type_combo.itemData(index) or ""
        self._type_desc_label.setText(desc)

    # ------------------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------------------

    def _update_recommendation(self) -> None:
        mood = self._pre_mood_slider.value()
        for (lo, hi), (med_type, reason) in _MOOD_RECOMMENDATIONS.items():
            if lo <= mood <= hi:
                self._recommendation_label.setText(
                    f"Recommended: {med_type}\n{reason}"
                )
                return
        self._recommendation_label.setText("Try any meditation that resonates with you.")

    # ------------------------------------------------------------------
    # Session control
    # ------------------------------------------------------------------

    def _start_session(self) -> None:
        if self._running:
            return
        duration_min = self._duration_combo.currentData() or 10
        self._total_sec = duration_min * 60
        self._remaining_sec = self._total_sec
        self._running = True
        self._paused = False

        self._start_btn.setEnabled(False)
        self._pause_btn.setEnabled(True)
        self._stop_btn.setEnabled(True)
        self._duration_combo.setEnabled(False)
        self._type_combo.setEnabled(False)

        self._update_timer_display()
        self._tick_timer.start()

    def _pause_session(self) -> None:
        if not self._running:
            return
        self._paused = not self._paused
        self._pause_btn.setText("Resume" if self._paused else "Pause")

    def _stop_session(self) -> None:
        self._tick_timer.stop()
        elapsed_sec = self._total_sec - self._remaining_sec

        self._running = False
        self._paused = False
        self._start_btn.setEnabled(True)
        self._pause_btn.setEnabled(False)
        self._pause_btn.setText("Pause")
        self._stop_btn.setEnabled(False)
        self._duration_combo.setEnabled(True)
        self._type_combo.setEnabled(True)

        # Record session
        session = {
            "type": self._type_combo.currentText(),
            "duration_sec": elapsed_sec,
            "planned_duration_sec": self._total_sec,
            "mood_before": self._pre_mood_slider.value(),
            "mood_after": self._post_mood_slider.value(),
            "completed": self._remaining_sec <= 0,
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
        }
        self._sessions.append(session)
        self._save_sessions()
        self.session_completed.emit(session)

        # Also save via meditation manager if available
        try:
            if self._meditation_manager and hasattr(self._meditation_manager, "log_session"):
                self._meditation_manager.log_session(session)
        except Exception:
            pass

        self._refresh_history()

        # Reset display
        duration_min = self._duration_combo.currentData() or 10
        self._remaining_sec = duration_min * 60
        self._update_timer_display()

    def _tick(self) -> None:
        if self._paused or not self._running:
            return
        self._remaining_sec -= 1
        self._update_timer_display()
        if self._remaining_sec <= 0:
            self._stop_session()
            QMessageBox.information(
                self, "Session Complete",
                "Your meditation session is complete. "
                "Please rate your post-session mood."
            )

    def _update_timer_display(self) -> None:
        mins = self._remaining_sec // 60
        secs = self._remaining_sec % 60
        self._timer_label.setText(f"{mins:02d}:{secs:02d}")

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def _refresh_history(self) -> None:
        self._history_list.clear()
        for s in reversed(self._sessions[-30:]):
            ts = s.get("timestamp", s.get("date", "?"))[:16]
            mtype = s.get("type", "?")
            dur = s.get("duration_sec", 0) // 60
            mood_b = s.get("mood_before", "?")
            mood_a = s.get("mood_after", "?")
            completed = "Complete" if s.get("completed") else "Partial"
            text = f"{ts} | {mtype} | {dur}m | Mood: {mood_b}->{mood_a} | {completed}"
            self._history_list.addItem(text)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Called by main window on close."""
        if self._running:
            self._stop_session()
        self._save_sessions()
