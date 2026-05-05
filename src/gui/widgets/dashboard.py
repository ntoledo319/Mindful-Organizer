"""
Main dashboard widget -- the at-a-glance overview tab.

Displays mood summaries, energy information, task status, streaks,
gamification progress, personalized suggestions, and system health.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.components import AccentButton, BodyLabel, CardFrame, SectionTitle, ThemedProgressBar

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

logger = logging.getLogger(__name__)


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
        theme: dict[str, str],
        task_manager: Any = None,
        profile_manager: Any = None,
        mood_manager: Any = None,
        energy_predictor: Any = None,
        gamification_manager: Any = None,
        wellness_orchestrator: Any = None,
        subscription_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._task_manager = task_manager
        self._profile_manager = profile_manager
        self._mood_manager = mood_manager
        self._energy_predictor = energy_predictor
        self._gamification_manager = gamification_manager
        self._wellness_orchestrator = wellness_orchestrator
        self._subscription_manager = subscription_manager

        self._build_ui()

        # Auto-refresh timer
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start(self._REFRESH_INTERVAL_MS)

        # Reactive state-bus subscriptions
        self._subscribe_state_bus()

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

        self._build_tier_banner()
        self._build_crisis_banner()
        self._build_welcome_section()
        self._build_quick_actions()
        self._build_daily_briefing()
        self._build_cards_grid()
        self._build_suggestions_section()
        self._build_system_health_card()

        self._layout.addStretch()

    # -- welcome -------------------------------------------------------

    def _build_tier_banner(self) -> None:
        from gui.subscription_helpers import tier_badge_text, trial_days_text
        tier = tier_badge_text(self._subscription_manager)
        trial = trial_days_text(self._subscription_manager)
        if tier == "FREE" and not trial:
            self._tier_banner = QFrame()
            self._tier_banner.setStyleSheet(
                f"background-color: {self._theme.get('accent_light', '#EBF5FB')}; "
                f"border-radius: 8px; padding: 8px;"
            )
            banner_layout = QHBoxLayout(self._tier_banner)
            banner_layout.setContentsMargins(12, 8, 12, 8)
            lbl = QLabel("✨ You're on the Free plan. Start a 14-day trial to unlock insights, smart notifications, and more.")
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"color: {self._theme.get('accent', '#3498DB')}; font-size: 12px;")
            banner_layout.addWidget(lbl, stretch=1)
            trial_btn = QPushButton("Start Free Trial")
            trial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            trial_btn.setStyleSheet(
                f"QPushButton {{ background-color: {self._theme.get('accent', '#3498DB')}; color: white; "
                f"border-radius: 6px; padding: 6px 12px; font-weight: bold; font-size: 11px; }}"
                f"QPushButton:hover {{ background-color: {self._theme.get('accent_hover', '#2980B9')}; }}"
            )
            trial_btn.clicked.connect(self._on_trial_clicked)
            banner_layout.addWidget(trial_btn)
            self._layout.addWidget(self._tier_banner)
        elif trial:
            self._tier_banner = QFrame()
            self._tier_banner.setStyleSheet(
                f"background-color: {self._theme.get('success_light', '#E8F8F5')}; "
                f"border-radius: 8px; padding: 8px;"
            )
            banner_layout = QHBoxLayout(self._tier_banner)
            banner_layout.setContentsMargins(12, 8, 12, 8)
            lbl = QLabel(f"🎉 {trial}. Enjoy all features!")
            lbl.setStyleSheet(f"color: {self._theme.get('success', '#27AE60')}; font-size: 12px;")
            banner_layout.addWidget(lbl)
            self._layout.addWidget(self._tier_banner)
        else:
            self._tier_banner = None

    def _on_trial_clicked(self) -> None:
        if self._subscription_manager:
            try:
                self._subscription_manager.start_trial()
                self.refresh()
            except Exception:
                pass

    def _build_crisis_banner(self) -> None:
        self._crisis_banner = QFrame()
        self._crisis_banner.setVisible(False)
        self._crisis_banner.setStyleSheet(
            f"background-color: {self._theme.get('warning', '#F39C12')}; "
            f"border-radius: 8px; padding: 12px;"
        )
        banner_layout = QHBoxLayout(self._crisis_banner)
        self._crisis_label = QLabel()
        self._crisis_label.setWordWrap(True)
        self._crisis_label.setStyleSheet("color: #333; font-weight: bold;")
        banner_layout.addWidget(self._crisis_label)
        self._layout.addWidget(self._crisis_banner)

    def _build_daily_briefing(self) -> None:
        self._briefing_card, briefing_layout = self._make_card("Today's Briefing")
        self._briefing_energy = BodyLabel("", self._theme)
        self._briefing_tasks = BodyLabel("", self._theme)
        self._briefing_skill = BodyLabel("", self._theme)
        for w in (self._briefing_energy, self._briefing_tasks, self._briefing_skill):
            briefing_layout.addWidget(w)
        self._layout.addWidget(self._briefing_card)

    def _build_welcome_section(self) -> None:
        row = QHBoxLayout()

        user_name = "there"
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "name") and profile.name:
                user_name = profile.name

        today_str = date.today().strftime("%A, %B %d, %Y")
        self._welcome_label = QLabel(f"Welcome back, {user_name}!")
        self._welcome_label.setFont(QFont(QFont().defaultFamily(), 20, QFont.Weight.Bold))
        self._welcome_label.setStyleSheet(
            f"color: {self._theme.get('text', '#222222')};"
        )
        row.addWidget(self._welcome_label)

        row.addStretch()

        self._date_label = QLabel(today_str)
        self._date_label.setFont(QFont(QFont().defaultFamily(), 13))
        self._date_label.setStyleSheet(
            f"color: {self._theme.get('secondary', '#888888')};"
        )
        row.addWidget(self._date_label)

        refresh_btn = AccentButton("Refresh", self._theme)
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
            btn = AccentButton(label, self._theme)
            btn.clicked.connect(signal.emit)
            row.addWidget(btn)

        self._layout.addLayout(row)

    # -- main cards grid -----------------------------------------------

    def _build_cards_grid(self) -> None:
        grid = QGridLayout()
        grid.setSpacing(16)

        # Row 0 --  Mood | Energy
        self._mood_card, self._mood_card_layout = self._make_card("Mood Summary")
        self._mood_today_label = BodyLabel("No mood entries today.", self._theme)
        self._mood_trend_label = BodyLabel("7-day trend: --", self._theme)
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
        self._energy_level_label = BodyLabel("Current energy: --", self._theme)
        self._spoon_label = BodyLabel("Spoons remaining: --", self._theme)
        self._energy_prediction_label = BodyLabel("Prediction: --", self._theme)
        for w in (self._energy_level_label, self._spoon_label, self._energy_prediction_label):
            self._energy_card_layout.addWidget(w)
        grid.addWidget(self._energy_card, 0, 1)

        # Row 1 -- Tasks | Streaks
        self._task_card, self._task_card_layout = self._make_card("Tasks")
        self._tasks_due_label = BodyLabel("Due today: 0", self._theme)
        self._tasks_overdue_label = BodyLabel("Overdue: 0", self._theme)
        self._task_progress = ThemedProgressBar(self._theme, color_key="success")
        self._task_progress.setMaximum(100)
        self._task_progress.setValue(0)
        self._task_progress.setFormat("Completion: %p%")
        self._upcoming_tasks_label: QLabel = BodyLabel("", self._theme)
        for w in (self._tasks_due_label, self._tasks_overdue_label,
                  self._task_progress, self._upcoming_tasks_label):
            self._task_card_layout.addWidget(w)
        grid.addWidget(self._task_card, 1, 0)

        self._streak_card, self._streak_card_layout = self._make_card("Streaks")
        self._journal_streak_label = BodyLabel("Journaling: 0 days", self._theme)
        self._med_streak_label = BodyLabel("Medication adherence: 0 days", self._theme)
        self._org_streak_label = BodyLabel("Organization: 0 days", self._theme)
        for w in (self._journal_streak_label, self._med_streak_label, self._org_streak_label):
            self._streak_card_layout.addWidget(w)
        grid.addWidget(self._streak_card, 1, 1)

        # Row 2 -- Gamification | Values
        self._game_card, self._game_card_layout = self._make_card("Gamification")
        self._level_label = BodyLabel("Level: 1", self._theme)
        self._xp_bar = ThemedProgressBar(self._theme, color_key="accent")
        self._xp_bar.setMaximum(100)
        self._xp_bar.setValue(0)
        self._xp_bar.setFormat("XP: %v / %m")
        self._achievements_label: QLabel = BodyLabel("Recent achievements: --", self._theme)
        for w in (self._level_label, self._xp_bar, self._achievements_label):
            self._game_card_layout.addWidget(w)
        grid.addWidget(self._game_card, 2, 0)

        self._values_card, self._values_card_layout = self._make_card("Values This Week")
        self._values_top_label = BodyLabel("Top value: --", self._theme)
        self._values_neglect_label = BodyLabel("Neglected: --", self._theme)
        self._values_action_label = BodyLabel("", self._theme)
        for w in (self._values_top_label, self._values_neglect_label, self._values_action_label):
            self._values_card_layout.addWidget(w)
        grid.addWidget(self._values_card, 2, 1)

        self._layout.addLayout(grid)

    # -- suggestions ---------------------------------------------------

    def _build_suggestions_section(self) -> None:
        card, layout = self._make_card("Personalized Suggestions")
        self._suggestions_label = BodyLabel(
            "Start tracking your mood and tasks to receive personalized suggestions.",
            self._theme,
        )
        layout.addWidget(self._suggestions_label)
        self._layout.addWidget(card)

    # -- system health -------------------------------------------------

    def _build_system_health_card(self) -> None:
        card, layout = self._make_card("System Health")

        self._cpu_bar = ThemedProgressBar(self._theme, color_key="accent")
        self._cpu_bar.setMaximum(100)
        self._cpu_bar.setValue(0)
        self._cpu_bar.setFormat("CPU: %p%")
        self._mem_bar = ThemedProgressBar(self._theme, color_key="warning")
        self._mem_bar.setMaximum(100)
        self._mem_bar.setValue(0)
        self._mem_bar.setFormat("Memory: %p%")
        self._disk_bar = ThemedProgressBar(self._theme, color_key="secondary")
        self._disk_bar.setMaximum(100)
        self._disk_bar.setValue(0)
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
        frame = CardFrame(self._theme)
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        layout.addWidget(SectionTitle(title, self._theme))
        return frame, layout

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Reload data from managers and update all cards."""
        self._refresh_crisis_banner()
        self._refresh_daily_briefing()
        self._refresh_welcome()
        self._refresh_mood()
        self._refresh_energy()
        self._refresh_tasks()
        self._refresh_streaks()
        self._refresh_gamification()
        self._refresh_values()
        self._refresh_suggestions()
        self._refresh_system_health()

    def _refresh_crisis_banner(self) -> None:
        from gui.subscription_helpers import check_feature
        if not check_feature("full_dashboard", self._subscription_manager):
            self._crisis_banner.setVisible(False)
            return
        if not self._wellness_orchestrator:
            self._crisis_banner.setVisible(False)
            return
        try:
            conditions = []
            if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
                profile = self._profile_manager.current_profile
                if profile and hasattr(profile, "conditions"):
                    conditions = list(profile.conditions)
            signals = self._wellness_orchestrator.detect_crisis_signals(conditions)
            if signals:
                sig = signals[0]
                self._crisis_label.setText(
                    f"Wellness check-in: {sig.description}\n"
                    f"Suggestion: {sig.recommendation}"
                )
                self._crisis_banner.setVisible(True)
            else:
                self._crisis_banner.setVisible(False)
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug(f"Crisis banner refresh error: {exc}")
            self._crisis_banner.setVisible(False)

    def _refresh_daily_briefing(self) -> None:
        from gui.subscription_helpers import check_feature
        has_pro = check_feature("full_dashboard", self._subscription_manager)
        if not has_pro:
            self._briefing_energy.setVisible(False)
            self._briefing_tasks.setVisible(False)
            self._briefing_skill.setVisible(False)
            if hasattr(self, '_briefing_upsell'):
                self._briefing_upsell.setVisible(True)
            return
        self._briefing_energy.setVisible(True)
        self._briefing_tasks.setVisible(True)
        self._briefing_skill.setVisible(True)
        if hasattr(self, '_briefing_upsell'):
            self._briefing_upsell.setVisible(False)
        if not self._wellness_orchestrator:
            self._briefing_card.setVisible(False)
            return
        try:
            conditions = []
            if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
                profile = self._profile_manager.current_profile
                if profile and hasattr(profile, "conditions"):
                    conditions = list(profile.conditions)
            briefing = self._wellness_orchestrator.daily_briefing(conditions)
            self._briefing_card.setVisible(True)
            self._briefing_energy.setText(
                briefing.energy_forecast or "Energy forecast unavailable."
            )
            if briefing.task_recommendations:
                lines = [f"  • {t['title']} (energy: {t['energy_required']}/10)" for t in briefing.task_recommendations[:3]]
                self._briefing_tasks.setText("Suggested tasks:\n" + "\n".join(lines))
            else:
                self._briefing_tasks.setText("No pending tasks — great job!")
            if briefing.suggested_skill:
                self._briefing_skill.setText(f"Suggested skill: {briefing.suggested_skill}")
            else:
                self._briefing_skill.setText("")
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug(f"Briefing refresh error: {exc}")
            self._briefing_card.setVisible(False)

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
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug(f"Mood refresh error: {exc}")

    def _refresh_energy(self) -> None:
        from gui.subscription_helpers import check_feature
        if not check_feature("energy_predictor", self._subscription_manager):
            self._energy_level_label.setText("Energy prediction available with Pro")
            self._energy_prediction_label.setText("")
            return
        if not self._energy_predictor:
            return
        try:
            now = datetime.now()
            state: dict[str, object] = {"timestamp": now.isoformat()}

            # Attempt to populate real values from managers
            if self._mood_manager and hasattr(self._mood_manager, "latest_mood"):
                latest = self._mood_manager.latest_mood()
                if latest:
                    state["mood_score"] = latest.get("score", 5)
            # Provide safe defaults only when real data is absent
            state.setdefault("energy_score", 50)
            state.setdefault("sleep_hours", 7)
            state.setdefault("sleep_quality", 5)
            state.setdefault("mood_score", 5)
            state.setdefault("tasks_completed_yesterday", 0)
            state.setdefault("medication_taken", False)

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
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug(f"Energy refresh error: {exc}")

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
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug(f"Mood refresh error: {exc}")

    def _refresh_streaks(self) -> None:
        # Streaks come from various managers; use defaults if unavailable.
        pass

    def _refresh_gamification(self) -> None:
        from gui.subscription_helpers import check_feature
        if not check_feature("gamification", self._subscription_manager):
            self._level_label.setText("Gamification available with Pro")
            self._xp_bar.setVisible(False)
            self._achievements_label.setText("")
            return
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
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug(f"Mood refresh error: {exc}")

    def _refresh_values(self) -> None:
        try:
            from core.values_tracker import ValuesTracker
            tracker = ValuesTracker()
            report = tracker.generate_weekly_report()
            if report.top_value:
                top_tasks = next(
                    (s.tasks_aligned for s in report.value_scores if s.value_name == report.top_value),
                    0,
                )
                self._values_top_label.setText(
                    f"Top value: {report.top_value} ({top_tasks} tasks)"
                )
            else:
                self._values_top_label.setText("Top value: No aligned tasks yet.")
            if report.neglected_value:
                self._values_neglect_label.setText(
                    f"Neglected: {report.neglected_value}"
                )
                if report.suggested_action:
                    self._values_action_label.setText(report.suggested_action)
                else:
                    self._values_action_label.setText("")
            else:
                self._values_neglect_label.setText("Neglected: None")
                self._values_action_label.setText("")
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug(f"Mood refresh error: {exc}")

    def _refresh_suggestions(self) -> None:
        suggestions: list[str] = []
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
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug(f"Mood refresh error: {exc}")

    # ------------------------------------------------------------------
    # Theme update
    # ------------------------------------------------------------------

    def _subscribe_state_bus(self) -> None:
        try:
            from gui.state_bus import get_state_bus
            bus = get_state_bus()
            bus.mood_logged.connect(self.refresh)
            bus.energy_updated.connect(self.refresh)
            bus.task_changed.connect(self.refresh)
            bus.crisis_detected.connect(self.refresh)
        except (ImportError, RuntimeError) as exc:
            logger.debug(f"State bus subscription error: {exc}")

    def apply_theme(self, theme: dict[str, str]) -> None:
        """Re-apply a new theme to the dashboard."""
        self._theme = theme
        # A full rebuild is simplest for a theme change.
        # Clear and rebuild.
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget:
                widget.deleteLater()
            sub = item.layout()
            if sub:
                while sub.count():
                    child = sub.takeAt(0)
                    if child is None:
                        continue
                    cw = child.widget()
                    if cw:
                        cw.deleteLater()

        self._build_welcome_section()
        self._build_quick_actions()
        self._build_cards_grid()
        self._build_suggestions_section()
        self._build_system_health_card()
        self._layout.addStretch()
        self.refresh()
