"""
Main dashboard widget -- the at-a-glance overview tab.

Displays mood summaries, energy information, task status, streaks,
gamification progress, personalized suggestions, and system health.
"""

from __future__ import annotations

import platform
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QScrollArea, QGridLayout, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _card_frame(theme: Dict[str, str]) -> QFrame:
    """Return a styled QFrame acting as a dashboard card."""
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setStyleSheet(
        f"QFrame {{ background-color: {theme.get('card_bg', '#ffffff')}; "
        f"border-radius: 12px; padding: 16px; }}"
    )
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return frame


def _section_title(text: str, theme: Dict[str, str]) -> QLabel:
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
    label.setStyleSheet(f"color: {theme.get('text', '#333333')}; padding-bottom: 4px;")
    return label


def _body_label(text: str, theme: Dict[str, str]) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {theme.get('text', '#555555')};")
    return label


def _accent_button(text: str, theme: Dict[str, str]) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(
        f"QPushButton {{ background-color: {theme.get('accent', '#4a90d9')}; "
        f"color: #ffffff; border: none; border-radius: 8px; padding: 10px 18px; "
        f"font-weight: bold; font-size: 13px; }}"
        f"QPushButton:hover {{ background-color: {theme.get('secondary', '#357abd')}; }}"
    )
    return btn


def _progress_bar(value: int, maximum: int, theme: Dict[str, str],
                  color_key: str = "accent") -> QProgressBar:
    bar = QProgressBar()
    bar.setMaximum(maximum)
    bar.setValue(value)
    bar.setTextVisible(True)
    bar.setStyleSheet(
        f"QProgressBar {{ border: 1px solid {theme.get('secondary', '#cccccc')}; "
        f"border-radius: 6px; text-align: center; height: 20px; "
        f"background-color: {theme.get('background', '#f0f0f0')}; }}"
        f"QProgressBar::chunk {{ background-color: {theme.get(color_key, '#4a90d9')}; "
        f"border-radius: 6px; }}"
    )
    return bar


# ---------------------------------------------------------------------------
# Dashboard widget
# ---------------------------------------------------------------------------

class DashboardWidget(QWidget):
    """Main dashboard overview tab."""

    # Signals emitted when quick-action buttons are clicked.
    mood_track_requested = pyqtSignal()
    task_add_requested = pyqtSignal()
    breathing_requested = pyqtSignal()
    journal_requested = pyqtSignal()
    stats_requested = pyqtSignal()

    # Auto-refresh interval (ms) -- 5 minutes.
    _REFRESH_INTERVAL_MS = 5 * 60 * 1000

    def __init__(
        self,
        theme: Dict[str, str],
        task_manager: Any = None,
        profile_manager: Any = None,
        mood_manager: Any = None,
        energy_predictor: Any = None,
        gamification_manager: Any = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._task_manager = task_manager
        self._profile_manager = profile_manager
        self._mood_manager = mood_manager
        self._energy_predictor = energy_predictor
        self._gamification_manager = gamification_manager

        self._build_ui()

        # Auto-refresh timer
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start(self._REFRESH_INTERVAL_MS)

        # Initial data load
        self.refresh()

    # ------------------------------------------------------------------
    # UI construction
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
        self._layout = QVBoxLayout(container)
        self._layout.setSpacing(16)
        self._layout.setContentsMargins(24, 24, 24, 24)
        scroll.setWidget(container)

        self._build_welcome_section()
        self._build_quick_actions()
        self._build_cards_grid()
        self._build_suggestions_section()
        self._build_system_health_card()

        self._layout.addStretch()

    # -- welcome -------------------------------------------------------

    def _build_welcome_section(self) -> None:
        row = QHBoxLayout()

        user_name = "there"
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "name") and profile.name:
                user_name = profile.name

        today_str = date.today().strftime("%A, %B %d, %Y")
        self._welcome_label = QLabel(f"Welcome back, {user_name}!")
        self._welcome_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self._welcome_label.setStyleSheet(
            f"color: {self._theme.get('text', '#222222')};"
        )
        row.addWidget(self._welcome_label)

        row.addStretch()

        self._date_label = QLabel(today_str)
        self._date_label.setFont(QFont("Segoe UI", 13))
        self._date_label.setStyleSheet(
            f"color: {self._theme.get('secondary', '#888888')};"
        )
        row.addWidget(self._date_label)

        refresh_btn = _accent_button("Refresh", self._theme)
        refresh_btn.clicked.connect(self.refresh)
        row.addWidget(refresh_btn)

        self._layout.addLayout(row)

    # -- quick actions -------------------------------------------------

    def _build_quick_actions(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(12)

        actions = [
            ("Track Mood", self.mood_track_requested),
            ("Add Task", self.task_add_requested),
            ("Breathing Exercise", self.breathing_requested),
            ("Journal Entry", self.journal_requested),
            ("View Stats", self.stats_requested),
        ]
        for label, signal in actions:
            btn = _accent_button(label, self._theme)
            btn.clicked.connect(signal.emit)
            row.addWidget(btn)

        self._layout.addLayout(row)

    # -- main cards grid -----------------------------------------------

    def _build_cards_grid(self) -> None:
        grid = QGridLayout()
        grid.setSpacing(16)

        # Row 0 --  Mood | Energy
        self._mood_card, self._mood_card_layout = self._make_card("Mood Summary")
        self._mood_today_label = _body_label("No mood entries today.", self._theme)
        self._mood_trend_label = _body_label("7-day trend: --", self._theme)
        self._mood_chart_placeholder = QFrame()
        self._mood_chart_placeholder.setFixedHeight(100)
        self._mood_chart_placeholder.setStyleSheet(
            f"background-color: {self._theme.get('background', '#eee')}; "
            "border-radius: 8px;"
        )
        for w in (self._mood_today_label, self._mood_trend_label, self._mood_chart_placeholder):
            self._mood_card_layout.addWidget(w)
        grid.addWidget(self._mood_card, 0, 0)

        self._energy_card, self._energy_card_layout = self._make_card("Energy")
        self._energy_level_label = _body_label("Current energy: --", self._theme)
        self._spoon_label = _body_label("Spoons remaining: --", self._theme)
        self._energy_prediction_label = _body_label("Prediction: --", self._theme)
        for w in (self._energy_level_label, self._spoon_label, self._energy_prediction_label):
            self._energy_card_layout.addWidget(w)
        grid.addWidget(self._energy_card, 0, 1)

        # Row 1 -- Tasks | Streaks
        self._task_card, self._task_card_layout = self._make_card("Tasks")
        self._tasks_due_label = _body_label("Due today: 0", self._theme)
        self._tasks_overdue_label = _body_label("Overdue: 0", self._theme)
        self._task_progress = _progress_bar(0, 100, self._theme, "success")
        self._task_progress.setFormat("Completion: %p%")
        self._upcoming_tasks_label = _body_label("", self._theme)
        for w in (self._tasks_due_label, self._tasks_overdue_label,
                  self._task_progress, self._upcoming_tasks_label):
            self._task_card_layout.addWidget(w)
        grid.addWidget(self._task_card, 1, 0)

        self._streak_card, self._streak_card_layout = self._make_card("Streaks")
        self._journal_streak_label = _body_label("Journaling: 0 days", self._theme)
        self._med_streak_label = _body_label("Medication adherence: 0 days", self._theme)
        self._org_streak_label = _body_label("Organization: 0 days", self._theme)
        for w in (self._journal_streak_label, self._med_streak_label, self._org_streak_label):
            self._streak_card_layout.addWidget(w)
        grid.addWidget(self._streak_card, 1, 1)

        # Row 2 -- Gamification
        self._game_card, self._game_card_layout = self._make_card("Gamification")
        self._level_label = _body_label("Level: 1", self._theme)
        self._xp_bar = _progress_bar(0, 100, self._theme, "accent")
        self._xp_bar.setFormat("XP: %v / %m")
        self._achievements_label = _body_label("Recent achievements: --", self._theme)
        for w in (self._level_label, self._xp_bar, self._achievements_label):
            self._game_card_layout.addWidget(w)
        grid.addWidget(self._game_card, 2, 0, 1, 2)

        self._layout.addLayout(grid)

    # -- suggestions ---------------------------------------------------

    def _build_suggestions_section(self) -> None:
        card, layout = self._make_card("Personalized Suggestions")
        self._suggestions_label = _body_label(
            "Start tracking your mood and tasks to receive personalized suggestions.",
            self._theme,
        )
        layout.addWidget(self._suggestions_label)
        self._layout.addWidget(card)

    # -- system health -------------------------------------------------

    def _build_system_health_card(self) -> None:
        card, layout = self._make_card("System Health")

        self._cpu_bar = _progress_bar(0, 100, self._theme, "accent")
        self._cpu_bar.setFormat("CPU: %p%")
        self._mem_bar = _progress_bar(0, 100, self._theme, "warning")
        self._mem_bar.setFormat("Memory: %p%")
        self._disk_bar = _progress_bar(0, 100, self._theme, "secondary")
        self._disk_bar.setFormat("Disk: %p%")

        for lbl_text, bar in [("CPU", self._cpu_bar),
                               ("Memory", self._mem_bar),
                               ("Disk", self._disk_bar)]:
            row = QHBoxLayout()
            row.addWidget(QLabel(lbl_text))
            row.addWidget(bar)
            layout.addLayout(row)

        self._layout.addWidget(card)

    # ------------------------------------------------------------------
    # Card factory
    # ------------------------------------------------------------------

    def _make_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        frame = _card_frame(self._theme)
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        layout.addWidget(_section_title(title, self._theme))
        return frame, layout

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Reload data from managers and update all cards."""
        self._refresh_welcome()
        self._refresh_mood()
        self._refresh_energy()
        self._refresh_tasks()
        self._refresh_streaks()
        self._refresh_gamification()
        self._refresh_suggestions()
        self._refresh_system_health()

    def _refresh_welcome(self) -> None:
        user_name = "there"
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "name") and profile.name:
                user_name = profile.name
        self._welcome_label.setText(f"Welcome back, {user_name}!")
        self._date_label.setText(date.today().strftime("%A, %B %d, %Y"))

    def _refresh_mood(self) -> None:
        if not self._mood_manager:
            return
        try:
            today = date.today()
            entries = []
            if hasattr(self._mood_manager, "_entries"):
                entries = [
                    e for e in self._mood_manager._entries
                    if hasattr(e, "timestamp") and e.timestamp.date() == today
                ]
            count = len(entries)
            avg = sum(e.mood_score for e in entries) / count if count else 0
            self._mood_today_label.setText(
                f"Today's entries: {count}" + (f" (avg {avg:.1f}/10)" if count else "")
            )
            # Trend
            if hasattr(self._mood_manager, "mood_trend"):
                trend = self._mood_manager.mood_trend()
                self._mood_trend_label.setText(
                    f"7-day trend: {trend.direction.value.capitalize()}"
                )
        except Exception:
            pass

    def _refresh_energy(self) -> None:
        if not self._energy_predictor:
            return
        try:
            now = datetime.now()
            state = {
                "timestamp": now.isoformat(),
                "energy_score": 50,
                "sleep_hours": 7,
                "sleep_quality": 5,
                "mood_score": 5,
                "tasks_completed_yesterday": 0,
                "medication_taken": False,
            }
            pred = self._energy_predictor.predict_single(state)
            self._energy_level_label.setText(
                f"Current energy: {pred.predicted_energy:.0f}/100 "
                f"({pred.energy_level.value.replace('_', ' ').title()})"
            )
            rest = self._energy_predictor.predict_rest_of_day(state)
            if rest:
                avg_rest = sum(p.predicted_energy for p in rest) / len(rest)
                self._energy_prediction_label.setText(
                    f"Rest-of-day average: {avg_rest:.0f}/100"
                )
        except Exception:
            pass

    def _refresh_tasks(self) -> None:
        if not self._task_manager:
            return
        try:
            all_tasks = self._task_manager.tasks
            today = date.today()
            incomplete = [t for t in all_tasks if not t.completed]
            due_today = [
                t for t in incomplete
                if hasattr(t, "due_date") and t.due_date and (
                    t.due_date == today if isinstance(t.due_date, date) else str(t.due_date) == str(today)
                )
            ]
            overdue = [
                t for t in incomplete
                if hasattr(t, "due_date") and t.due_date and (
                    t.due_date < today if isinstance(t.due_date, date) else str(t.due_date) < str(today)
                )
            ]
            completed = [t for t in all_tasks if t.completed]
            total = len(all_tasks)
            pct = int(len(completed) / total * 100) if total else 0

            self._tasks_due_label.setText(f"Due today: {len(due_today)}")
            self._tasks_overdue_label.setText(f"Overdue: {len(overdue)}")
            self._task_progress.setValue(pct)

            upcoming = sorted(
                [t for t in incomplete if hasattr(t, "due_date") and t.due_date],
                key=lambda t: str(t.due_date),
            )[:3]
            if upcoming:
                lines = [f"  - {t.title} (due {t.due_date})" for t in upcoming]
                self._upcoming_tasks_label.setText("Upcoming:\n" + "\n".join(lines))
            else:
                self._upcoming_tasks_label.setText("No upcoming tasks.")
        except Exception:
            pass

    def _refresh_streaks(self) -> None:
        # Streaks come from various managers; use defaults if unavailable.
        pass

    def _refresh_gamification(self) -> None:
        if not self._gamification_manager:
            return
        try:
            if hasattr(self._gamification_manager, "level"):
                self._level_label.setText(
                    f"Level: {self._gamification_manager.level}"
                )
            if hasattr(self._gamification_manager, "xp"):
                xp = self._gamification_manager.xp
                xp_next = getattr(self._gamification_manager, "xp_for_next_level", 100)
                self._xp_bar.setMaximum(xp_next)
                self._xp_bar.setValue(xp)
            if hasattr(self._gamification_manager, "recent_achievements"):
                achievements = self._gamification_manager.recent_achievements[:3]
                if achievements:
                    self._achievements_label.setText(
                        "Recent: " + ", ".join(str(a) for a in achievements)
                    )
        except Exception:
            pass

    def _refresh_suggestions(self) -> None:
        suggestions: List[str] = []
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "conditions"):
                conditions = profile.conditions
                if conditions:
                    cond_names = set()
                    for c in conditions:
                        cond_names.add(c.value if hasattr(c, "value") else str(c))
                    if "Anxiety" in cond_names or "anxiety" in cond_names:
                        suggestions.append(
                            "Try a breathing exercise to ease anxiety before tackling tasks."
                        )
                    if "Depression" in cond_names or "depression" in cond_names:
                        suggestions.append(
                            "Start with a small, low-energy task to build momentum."
                        )
                    if "ADHD" in cond_names or "adhd" in cond_names:
                        suggestions.append(
                            "Break large tasks into subtasks for quick wins."
                        )
                    if "OCD" in cond_names or "ocd" in cond_names:
                        suggestions.append(
                            "Consider an ERP session for your anxiety hierarchy."
                        )
                    if "PTSD" in cond_names or "ptsd" in cond_names:
                        suggestions.append(
                            "A grounding breathing exercise may help you feel safe and present."
                        )
        if not suggestions:
            suggestions.append(
                "Track your mood and complete tasks to unlock personalized tips!"
            )
        self._suggestions_label.setText("\n".join(f"- {s}" for s in suggestions))

    def _refresh_system_health(self) -> None:
        if not _HAS_PSUTIL:
            self._cpu_bar.setValue(0)
            self._mem_bar.setValue(0)
            self._disk_bar.setValue(0)
            return
        try:
            self._cpu_bar.setValue(int(psutil.cpu_percent(interval=0)))
            mem = psutil.virtual_memory()
            self._mem_bar.setValue(int(mem.percent))
            disk = psutil.disk_usage("/")
            self._disk_bar.setValue(int(disk.percent))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Theme update
    # ------------------------------------------------------------------

    def apply_theme(self, theme: Dict[str, str]) -> None:
        """Re-apply a new theme to the dashboard."""
        self._theme = theme
        # A full rebuild is simplest for a theme change.
        # Clear and rebuild.
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            sub = item.layout()
            if sub:
                while sub.count():
                    child = sub.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        self._build_welcome_section()
        self._build_quick_actions()
        self._build_cards_grid()
        self._build_suggestions_section()
        self._build_system_health_card()
        self._layout.addStretch()
        self.refresh()
