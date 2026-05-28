"""
Main dashboard widget -- the at-a-glance overview tab.

Displays a focused Today view with mood, energy, task, and system context.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.components import AccentButton, BodyLabel, CardFrame, GhostButton, SectionTitle

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dashboard widget
# ---------------------------------------------------------------------------

class DashboardWidget(QWidget):
    """Action-oriented Today overview tab."""

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
        scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"QScrollArea {{ background-color: {self._theme.get('background', '#f5f5f5')}; }}"
        )
        outer.addWidget(scroll)

        container = QWidget()
        container.setMaximumWidth(920)
        self._layout = QVBoxLayout(container)
        self._layout.setSpacing(18)
        self._layout.setContentsMargins(32, 32, 32, 40)
        scroll.setWidget(container)

        self._build_sections()

    def _build_sections(self) -> None:
        """Build the Today surface in display order."""
        self._build_tier_banner()
        self._build_crisis_banner()
        self._build_welcome_section()
        self._build_right_now_section()
        self._build_next_action_section()
        self._build_quick_actions()
        self._build_daily_briefing()
        self._build_context_section()
        self._build_suggestions_section()

        self._layout.addStretch()

    # -- welcome -------------------------------------------------------

    def _build_tier_banner(self) -> None:
        from gui.subscription_helpers import tier_badge_text, trial_days_text
        tier = tier_badge_text(self._subscription_manager)
        trial = trial_days_text(self._subscription_manager)
        if tier == "FREE" and not trial:
            self._tier_banner = QFrame()
            self._tier_banner.setStyleSheet(
                f"background-color: {self._theme.get('card_bg', '#221C16')}; "
                f"border: 1px solid {self._theme.get('border', '#3D3128')}; "
                "border-radius: 6px; padding: 8px;"
            )
            banner_layout = QHBoxLayout(self._tier_banner)
            banner_layout.setContentsMargins(12, 8, 12, 8)
            lbl = QLabel("Free plan. Start a 14-day trial for insights, smart notifications, and reports.")
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"color: {self._theme.get('accent', '#3498DB')}; font-size: 12px;")
            banner_layout.addWidget(lbl, stretch=1)
            trial_btn = QPushButton("Start trial")
            trial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            trial_btn.setStyleSheet(
                f"QPushButton {{ background-color: {self._theme.get('accent', '#A8845F')}; color: {self._theme.get('background', '#18130F')}; "
                f"border-radius: 5px; padding: 6px 12px; font-weight: 500; font-size: 11px; }}"
                f"QPushButton:hover {{ background-color: {self._theme.get('accent_hover', '#2980B9')}; }}"
            )
            trial_btn.clicked.connect(self._on_trial_clicked)
            banner_layout.addWidget(trial_btn)
            self._layout.addWidget(self._tier_banner)
        elif trial:
            self._tier_banner = QFrame()
            self._tier_banner.setStyleSheet(
                f"background-color: {self._theme.get('card_bg', '#221C16')}; "
                f"border: 1px solid {self._theme.get('success', '#95B776')}; "
                "border-radius: 6px; padding: 8px;"
            )
            banner_layout = QHBoxLayout(self._tier_banner)
            banner_layout.setContentsMargins(12, 8, 12, 8)
            lbl = QLabel(f"{trial}. Full access is active.")
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
            "border-radius: 6px; padding: 12px;"
        )
        banner_layout = QHBoxLayout(self._crisis_banner)
        self._crisis_label = QLabel()
        self._crisis_label.setWordWrap(True)
        self._crisis_label.setStyleSheet("color: #333; font-weight: bold;")
        banner_layout.addWidget(self._crisis_label)
        self._layout.addWidget(self._crisis_banner)

    def _build_daily_briefing(self) -> None:
        self._briefing_card, briefing_layout = self._make_card("Briefing")
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
        self._welcome_label = QLabel(f"Today, {user_name}")
        self._welcome_label.setFont(QFont(QFont().defaultFamily(), 24, QFont.Weight.DemiBold))
        self._welcome_label.setStyleSheet(
            f"color: {self._theme.get('text', '#222222')}; "
            "font-size: 28px; font-weight: 600;"
        )
        row.addWidget(self._welcome_label)

        row.addStretch()

        self._date_label = QLabel(today_str)
        self._date_label.setFont(QFont(QFont().defaultFamily(), 13))
        self._date_label.setStyleSheet(
            f"color: {self._theme.get('secondary', '#888888')}; font-size: 13px;"
        )
        row.addWidget(self._date_label)

        refresh_btn = GhostButton("Refresh", self._theme)
        refresh_btn.clicked.connect(self.refresh)
        row.addWidget(refresh_btn)

        self._layout.addLayout(row)

    # -- quick actions -------------------------------------------------

    def _build_quick_actions(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(12)

        actions = [
            ("Record mood", self.mood_track_requested, GhostButton),
            ("Add task", self.task_add_requested, AccentButton),
            ("Breathe", self.breathing_requested, GhostButton),
            ("Write", self.journal_requested, GhostButton),
            ("Review", self.stats_requested, GhostButton),
        ]
        for label, signal, button_class in actions:
            btn = button_class(label, self._theme)
            btn.clicked.connect(signal.emit)
            row.addWidget(btn)

        self._layout.addLayout(row)

    def _build_right_now_section(self) -> None:
        self._state_card, layout = self._make_card("Right now")
        self._state_sentence = BodyLabel("Hearth is ready. Record one signal to make this more specific.", self._theme)
        self._state_sentence.setFont(QFont(QFont().defaultFamily(), 16))
        layout.addWidget(self._state_sentence)
        self._layout.addWidget(self._state_card)

    def _build_next_action_section(self) -> None:
        self._next_action_card, layout = self._make_card("Next action")
        self._next_action_label = BodyLabel("Add one task or record how you feel. That gives Hearth enough context to help.", self._theme)
        self._next_action_label.setFont(QFont(QFont().defaultFamily(), 15))
        layout.addWidget(self._next_action_label)
        self._layout.addWidget(self._next_action_card)

    # -- context -------------------------------------------------------

    def _build_context_section(self) -> None:
        self._context_card, layout = self._make_card("Context")
        self._context_mood_label = BodyLabel("Mood has not been recorded today.", self._theme)
        self._context_energy_label = BodyLabel("Energy has not been forecast yet.", self._theme)
        self._context_task_label = BodyLabel("No task pressure is visible yet.", self._theme)
        self._context_values_label = BodyLabel("Values report unavailable.", self._theme)
        for w in (
            self._context_mood_label,
            self._context_energy_label,
            self._context_task_label,
            self._context_values_label,
        ):
            layout.addWidget(w)
        self._layout.addWidget(self._context_card)

    # -- suggestions ---------------------------------------------------

    def _build_suggestions_section(self) -> None:
        card, layout = self._make_card("Suggestions")
        self._suggestions_label = BodyLabel(
            "Record mood and task data to make suggestions more specific.",
            self._theme,
        )
        layout.addWidget(self._suggestions_label)
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
        self._refresh_right_now()
        self._refresh_next_action()
        self._refresh_daily_briefing()
        self._refresh_welcome()
        self._refresh_mood()
        self._refresh_energy()
        self._refresh_tasks()
        self._refresh_values()
        self._refresh_suggestions()

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
            self._briefing_card.setVisible(False)
            self._briefing_energy.setVisible(False)
            self._briefing_tasks.setVisible(False)
            self._briefing_skill.setVisible(False)
            if hasattr(self, '_briefing_upsell'):
                self._briefing_upsell.setVisible(True)
            return
        self._briefing_card.setVisible(True)
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
                self._briefing_tasks.setText("No pending tasks.")
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
        self._welcome_label.setText(f"Today, {user_name}")
        self._date_label.setText(date.today().strftime("%A, %B %d, %Y"))

    def _refresh_right_now(self) -> None:
        try:
            incomplete_count = 0
            if self._task_manager:
                incomplete_count = len([t for t in self._task_manager.tasks if not t.completed])

            energy_text = "Energy has not been logged today."
            if self._energy_predictor:
                energy_text = "Energy forecast is available."

            if incomplete_count:
                self._state_sentence.setText(
                    f"{energy_text} {incomplete_count} open task{'s' if incomplete_count != 1 else ''} need a decision."
                )
            else:
                self._state_sentence.setText(
                    f"{energy_text} No open tasks are pressing right now."
                )
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug("Right-now refresh error: %s", exc)

    def _refresh_next_action(self) -> None:
        try:
            if not self._task_manager:
                self._next_action_label.setText("Record how you feel or add one task to start shaping the day.")
                return
            incomplete = [t for t in self._task_manager.tasks if not t.completed]
            if not incomplete:
                self._next_action_label.setText("No open tasks. Record a mood entry or take a short practice.")
                return
            upcoming = sorted(
                incomplete,
                key=lambda t: (
                    str(getattr(t, "due_date", "") or "9999-99-99"),
                    -int(getattr(t, "priority", 0) or 0),
                ),
            )
            task = upcoming[0]
            title = getattr(task, "title", "Untitled task")
            due = getattr(task, "due_date", None)
            due_text = f" Due {due}." if due else ""
            self._next_action_label.setText(f"Start with: {title}.{due_text}")
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug("Next-action refresh error: %s", exc)

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
            mood_text = (
                f"Mood: {count} entr{'y' if count == 1 else 'ies'} today"
                + (f", average {avg:.1f}/10." if count else ".")
            )
            if hasattr(self._mood_manager, "mood_trend"):
                trend = self._mood_manager.mood_trend()
                mood_text += f" Seven-day trend: {trend.direction.value.lower()}."
            self._context_mood_label.setText(mood_text)
        except (AttributeError, ValueError, TypeError) as exc:
            logger.debug(f"Mood refresh error: {exc}")

    def _refresh_energy(self) -> None:
        from gui.subscription_helpers import check_feature
        if not check_feature("energy_predictor", self._subscription_manager):
            self._context_energy_label.setText("Energy: forecasting is available with Pro.")
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
            energy_text = (
                f"Energy: {pred.predicted_energy:.0f}/100, "
                f"{pred.energy_level.value.replace('_', ' ').lower()}."
            )
            rest = self._energy_predictor.predict_rest_of_day(state)
            if rest:
                avg_rest = sum(p.predicted_energy for p in rest) / len(rest)
                energy_text += f" Rest-of-day average: {avg_rest:.0f}/100."
            self._context_energy_label.setText(energy_text)
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

            upcoming = sorted(
                [t for t in incomplete if hasattr(t, "due_date") and t.due_date],
                key=lambda t: str(t.due_date),
            )[:3]
            parts = [
                f"Tasks: {len(due_today)} due today",
                f"{len(overdue)} overdue",
                f"{len(completed)}/{total} completed" if total else "none logged",
            ]
            if upcoming:
                next_titles = ", ".join(str(t.title) for t in upcoming)
                parts.append(f"next: {next_titles}")
            self._context_task_label.setText("; ".join(parts) + ".")
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
                values_text = f"Values: {report.top_value} is most represented this week ({top_tasks} tasks)."
            else:
                values_text = "Values: no aligned tasks yet."
            if report.neglected_value:
                values_text += f" Least represented: {report.neglected_value}."
                if report.suggested_action:
                    values_text += f" {report.suggested_action}"
            self._context_values_label.setText(values_text)
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
                        suggestions.append("Break a large task into one visible next step.")
                    if "OCD" in cond_names or "ocd" in cond_names:
                        suggestions.append(
                            "Consider an ERP session for your anxiety hierarchy."
                        )
                    if "PTSD" in cond_names or "ptsd" in cond_names:
                        suggestions.append(
                            "A grounding breathing exercise may help you feel safe and present."
                        )
        if not suggestions:
            suggestions.append("Record mood and task data to make suggestions more specific.")
        self._suggestions_label.setText("\n".join(f"- {s}" for s in suggestions))

    # ------------------------------------------------------------------
    # Theme update
    # ------------------------------------------------------------------

    def _subscribe_state_bus(self) -> None:
        try:
            from gui.state_bus import get_state_bus
            bus = get_state_bus()

            def refresh(*_args, **_kwargs) -> None:
                self.refresh()

            bus.mood_logged.connect(refresh)
            bus.energy_updated.connect(refresh)
            bus.task_changed.connect(refresh)
            crisis_signal = getattr(bus, "crisis_signal_detected", None)
            if crisis_signal is None:
                crisis_signal = getattr(bus, "crisis_detected", None)
            if crisis_signal is not None:
                crisis_signal.connect(refresh)
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

        self._build_sections()
        self.refresh()
