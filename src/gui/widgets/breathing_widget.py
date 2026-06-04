"""
Guided breathing exercise widget with animated visual guide.

Provides exercise selection, an expanding/contracting circle animation,
phase indicators with countdown, cycle tracking, and pre/post mood checks.
"""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from gui.components import AccentButton, BodyLabel, CardFrame, SectionTitle

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Breathing circle animation
# ---------------------------------------------------------------------------


class BreathingCircle(QWidget):
    """A circle that expands on inhale and contracts on exhale."""

    def __init__(self, theme: dict[str, str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._ratio: float = 0.3  # 0.0 to 1.0
        self._phase_text: str = "Ready"
        self.setMinimumSize(QSize(280, 280))
        self.setMaximumSize(QSize(280, 280))

    def set_ratio(self, ratio: float) -> None:
        self._ratio = max(0.0, min(1.0, ratio))
        self.update()

    def set_phase_text(self, text: str) -> None:
        self._phase_text = text
        self.update()

    def paintEvent(self, event: Any) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2

        min_r = 30
        max_r = min(w, h) // 2 - 10
        radius = int(min_r + (max_r - min_r) * self._ratio)

        # Calming gradient colour
        base = QColor(self._theme.get("accent", "#5dade2"))
        base.setAlpha(int(120 + 100 * self._ratio))
        painter.setBrush(QBrush(base))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

        # Phase text
        painter.setPen(QColor(self._theme.get("text", "#ffffff")))
        font = QFont()
        font.setPointSize(16)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._phase_text)
        painter.end()


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------


class BreathingWidget(QWidget):
    """Guided breathing exercise tab."""

    session_completed = pyqtSignal(dict)

    def __init__(
        self,
        theme: dict[str, str],
        breathing_manager: Any = None,
        profile_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._breathing_manager = breathing_manager
        self._profile_manager = profile_manager

        # Session state
        self._running: bool = False
        self._paused: bool = False
        self._timer_data: list[dict] = []
        self._tick_ms: int = 50
        self._elapsed_ms: int = 0
        self._current_phase_idx: int = 0
        self._current_cycle: int = 0
        self._total_cycles: int = 0
        self._session: Any = None

        self._animation_timer = QTimer(self)
        self._animation_timer.setInterval(self._tick_ms)
        self._animation_timer.timeout.connect(self._tick)

        self._build_ui()
        self._populate_exercises()
        self._refresh_history()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        bg = self._theme.get("background", "#0F0F11")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {bg}; }}")
        outer.addWidget(scroll)

        container = QWidget()
        container.setStyleSheet(f"background-color: {bg};")
        self._root = QVBoxLayout(container)
        self._root.setSpacing(16)
        self._root.setContentsMargins(24, 24, 24, 24)
        scroll.setWidget(container)

        self._root.addWidget(SectionTitle("Breathing Exercises", self._theme))

        top = QHBoxLayout()
        top.setSpacing(16)
        self._build_selector(top)
        self._build_recommendation(top)
        self._root.addLayout(top)

        self._build_exercise_info()
        self._build_visual_guide()
        self._build_mood_checks()
        self._build_controls()
        self._build_history()
        self._root.addStretch()

    # -- selector -------------------------------------------------------

    def _build_selector(self, parent_layout: QHBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Select Exercise", self._theme))

        self._exercise_combo = QComboBox()
        self._exercise_combo.setStyleSheet(
            f"QComboBox {{ padding: 8px; font-size: 13px; "
            f"background-color: {self._theme.get('surface_alt', self._theme.get('card_bg', '#222225'))}; "
            f"color: {self._theme.get('text', '#F3F3F4')}; }}"
        )
        self._exercise_combo.currentIndexChanged.connect(self._on_exercise_changed)
        layout.addWidget(self._exercise_combo)

        parent_layout.addWidget(card, stretch=1)

    def _build_recommendation(self, parent_layout: QHBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Recommended", self._theme))
        self._recommendation_label = BodyLabel(
            "Track your mood and Hearth will suggest a breath that fits.", self._theme
        )
        layout.addWidget(self._recommendation_label)
        parent_layout.addWidget(card, stretch=1)

    # -- exercise info --------------------------------------------------

    def _build_exercise_info(self) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        self._desc_label = BodyLabel("Pick an exercise to read how it works.", self._theme)
        layout.addWidget(self._desc_label)
        self._root.addWidget(card)

    # -- visual guide ---------------------------------------------------

    def _build_visual_guide(self) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._circle = BreathingCircle(self._theme)
        layout.addWidget(self._circle, alignment=Qt.AlignmentFlag.AlignCenter)

        phase_font = QFont()
        phase_font.setPointSize(18)
        phase_font.setWeight(QFont.Weight.Bold)
        self._phase_label = QLabel("Whenever you're ready")
        self._phase_label.setFont(phase_font)
        self._phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._phase_label.setStyleSheet(f"color: {self._theme.get('accent', '#D9A05B')};")
        layout.addWidget(self._phase_label)

        countdown_font = QFont()
        countdown_font.setPointSize(28)
        countdown_font.setWeight(QFont.Weight.Bold)
        self._countdown_label = QLabel("")
        self._countdown_label.setFont(countdown_font)
        self._countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._countdown_label.setStyleSheet(f"color: {self._theme.get('text', '#F3F3F4')};")
        layout.addWidget(self._countdown_label)

        self._cycle_label = BodyLabel("Press Start when you want to begin.", self._theme)
        self._cycle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._cycle_label)

        self._root.addWidget(card)

    # -- mood checks ----------------------------------------------------

    def _build_mood_checks(self) -> None:
        card = CardFrame(self._theme)
        layout = QHBoxLayout(card)
        layout.setSpacing(24)

        # Pre-session
        pre_col = QVBoxLayout()
        pre_col.addWidget(BodyLabel("Pre-session mood (1-10):", self._theme))
        self._pre_mood_slider = QSlider(Qt.Orientation.Horizontal)
        self._pre_mood_slider.setRange(1, 10)
        self._pre_mood_slider.setValue(5)
        self._pre_mood_value = BodyLabel("5", self._theme)
        self._pre_mood_slider.valueChanged.connect(lambda v: self._pre_mood_value.setText(str(v)))
        pre_col.addWidget(self._pre_mood_slider)
        pre_col.addWidget(self._pre_mood_value)
        layout.addLayout(pre_col)

        # Post-session
        post_col = QVBoxLayout()
        post_col.addWidget(BodyLabel("Post-session mood (1-10):", self._theme))
        self._post_mood_slider = QSlider(Qt.Orientation.Horizontal)
        self._post_mood_slider.setRange(1, 10)
        self._post_mood_slider.setValue(5)
        self._post_mood_value = BodyLabel("5", self._theme)
        self._post_mood_slider.valueChanged.connect(lambda v: self._post_mood_value.setText(str(v)))
        post_col.addWidget(self._post_mood_slider)
        post_col.addWidget(self._post_mood_value)
        layout.addLayout(post_col)

        self._root.addWidget(card)

    # -- controls -------------------------------------------------------

    def _build_controls(self) -> None:
        card = CardFrame(self._theme)
        layout = QHBoxLayout(card)

        self._start_btn = AccentButton("Start", self._theme)
        self._start_btn.clicked.connect(self._start_session)
        layout.addWidget(self._start_btn)

        self._pause_btn = AccentButton("Pause", self._theme)
        self._pause_btn.setEnabled(False)
        self._pause_btn.clicked.connect(self._pause_session)
        layout.addWidget(self._pause_btn)

        self._stop_btn = AccentButton("Stop", self._theme)
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_session)
        layout.addWidget(self._stop_btn)

        self._root.addWidget(card)

    # -- history --------------------------------------------------------

    def _build_history(self) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Past Sessions", self._theme))

        self._history_list = QListWidget()
        self._history_list.setMaximumHeight(200)
        self._history_list.setStyleSheet(
            f"QListWidget {{ "
            f"background-color: {self._theme.get('surface_alt', self._theme.get('card_bg', '#222225'))}; "
            f"color: {self._theme.get('text', '#F3F3F4')}; "
            f"border: 1px solid {self._theme.get('border', '#2C2C2E')}; border-radius: 6px; }}"
        )
        layout.addWidget(self._history_list)
        self._root.addWidget(card)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    def _populate_exercises(self) -> None:
        self._exercise_combo.clear()
        if self._breathing_manager and hasattr(self._breathing_manager, "list_exercises"):
            for ex in self._breathing_manager.list_exercises():
                self._exercise_combo.addItem(ex.name, ex.exercise_type)
        else:
            defaults = [
                ("Box Breathing", "box_breathing"),
                ("4-7-8 Breathing", "four_seven_eight"),
                ("Deep Belly Breathing", "deep_belly"),
                ("Calming Breath", "calming_breath"),
                ("Energizing Breath", "energizing_breath"),
                ("Grounding Breath", "grounding_breath"),
            ]
            for name, key in defaults:
                self._exercise_combo.addItem(name, key)

    def _on_exercise_changed(self, index: int) -> None:
        if index < 0:
            return
        if self._breathing_manager and hasattr(self._breathing_manager, "get_exercise"):
            try:
                etype = self._exercise_combo.currentData()
                ex = self._breathing_manager.get_exercise(etype)
                self._desc_label.setText(f"{ex.name}\n\n{ex.description}")
            except (AttributeError, TypeError):
                self._desc_label.setText("")
        else:
            self._desc_label.setText(self._exercise_combo.currentText())

    def _refresh_history(self) -> None:
        self._history_list.clear()
        if not self._breathing_manager:
            return
        try:
            sessions = self._breathing_manager.sessions
            for s in reversed(sessions[-30:]):
                started = s.started_at or "?"
                etype = (
                    s.exercise_type.value
                    if hasattr(s.exercise_type, "value")
                    else str(s.exercise_type)
                )
                improvement = s.mood_improvement
                imp_str = f"  Mood change: {improvement:+d}" if improvement is not None else ""
                text = f"{started[:16]}  |  {etype}{imp_str}"
                self._history_list.addItem(text)
        except (AttributeError, TypeError) as exc:
            logger.debug(f"History refresh error: {exc}")

    def _update_recommendation(self) -> None:
        if not self._breathing_manager or not hasattr(self._breathing_manager, "recommend"):
            return
        try:
            recs = self._breathing_manager.recommend(
                mood=self._pre_mood_slider.value(),
            )
            if recs:
                self._recommendation_label.setText(
                    f"Maybe try {recs[0].name}.\n{recs[0].description[:120]}..."
                )
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Recommendation error: {exc}")

    # ------------------------------------------------------------------
    # Session control
    # ------------------------------------------------------------------

    def _start_session(self) -> None:
        if self._running:
            return

        self._update_recommendation()
        etype = self._exercise_combo.currentData()

        # Build timer data
        if self._breathing_manager and hasattr(self._breathing_manager, "get_exercise"):
            try:
                ex = self._breathing_manager.get_exercise(etype)
                self._timer_data = ex.get_timer_data()
                self._total_cycles = ex.default_cycles
            except (AttributeError, TypeError):
                self._timer_data = self._fallback_timer_data()
                self._total_cycles = 4
        else:
            self._timer_data = self._fallback_timer_data()
            self._total_cycles = 4

        if self._breathing_manager and hasattr(self._breathing_manager, "create_session"):
            try:
                self._session = self._breathing_manager.create_session(
                    etype, mood_before=self._pre_mood_slider.value()
                )
            except (AttributeError, TypeError):
                self._session = None

        self._running = True
        self._paused = False
        self._elapsed_ms = 0
        self._current_phase_idx = 0
        self._current_cycle = 1

        self._start_btn.setEnabled(False)
        self._pause_btn.setEnabled(True)
        self._stop_btn.setEnabled(True)
        self._animation_timer.start()

    def _pause_session(self) -> None:
        if not self._running:
            return
        self._paused = not self._paused
        self._pause_btn.setText("Resume" if self._paused else "Pause")

    def _stop_session(self) -> None:
        self._animation_timer.stop()
        self._running = False
        self._paused = False

        self._start_btn.setEnabled(True)
        self._pause_btn.setEnabled(False)
        self._pause_btn.setText("Pause")
        self._stop_btn.setEnabled(False)

        self._phase_label.setText("That's a good place to stop.")
        self._countdown_label.setText("")
        self._cycle_label.setText("Press Start when you want to begin again.")
        self._circle.set_phase_text("Rest")
        self._circle.set_ratio(0.3)

        # Record session
        if self._session and self._breathing_manager:
            try:
                self._breathing_manager.complete_session(
                    self._session,
                    self._current_cycle - 1,
                    mood_after=self._post_mood_slider.value(),
                )
                result = {
                    "exercise": self._exercise_combo.currentText(),
                    "cycles": self._current_cycle - 1,
                    "mood_before": self._pre_mood_slider.value(),
                    "mood_after": self._post_mood_slider.value(),
                }
                self.session_completed.emit(result)
            except (AttributeError, TypeError) as exc:
                logger.debug(f"Breathing manager session error: {exc}")

        self._refresh_history()

    def _tick(self) -> None:
        if self._paused or not self._running:
            return

        self._elapsed_ms += self._tick_ms
        elapsed_sec = self._elapsed_ms / 1000.0

        # Find current phase
        phase = None
        for i, p in enumerate(self._timer_data):
            if p["start_at"] <= elapsed_sec < p["end_at"]:
                phase = p
                self._current_phase_idx = i
                self._current_cycle = p["cycle"]
                break

        if phase is None:
            # Exercise complete
            self._stop_session()
            return

        phase_name = phase["phase"].replace("_", " ").title()
        remaining = phase["end_at"] - elapsed_sec
        phase_progress = (elapsed_sec - phase["start_at"]) / phase["duration_seconds"]

        # Expand on inhale, contract on exhale
        if "inhale" in phase["phase"]:
            ratio = 0.3 + 0.7 * phase_progress
        elif "exhale" in phase["phase"]:
            ratio = 1.0 - 0.7 * phase_progress
        elif "hold_in" in phase["phase"]:
            ratio = 1.0
        else:
            ratio = 0.3

        self._circle.set_ratio(ratio)
        self._circle.set_phase_text(phase_name)
        self._phase_label.setText(phase["instruction"])
        self._countdown_label.setText(f"{remaining:.0f}s")
        self._cycle_label.setText(f"Cycle: {self._current_cycle} / {self._total_cycles}")

    def _fallback_timer_data(self) -> list[dict]:
        """Fallback box breathing timer data when no manager is available."""
        data: list[dict] = []
        elapsed = 0.0
        phases = [
            ("inhale", 4.0, "Breathe in slowly"),
            ("hold_in", 4.0, "Hold gently"),
            ("exhale", 4.0, "Breathe out slowly"),
            ("hold_out", 4.0, "Rest"),
        ]
        for cycle in range(1, 5):
            for phase, dur, instr in phases:
                data.append(
                    {
                        "cycle": cycle,
                        "phase": phase,
                        "duration_seconds": dur,
                        "instruction": instr,
                        "start_at": elapsed,
                        "end_at": elapsed + dur,
                    }
                )
                elapsed += dur
        return data

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
