"""
Mood tracking widget -- record, review, and analyse mood entries.

Provides a calendar-based mood entry form with condition-specific symptom
tracking, therapy skill logging, history browsing, and analytics display.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from PyQt6.QtCore import Qt, QTime, pyqtSignal
from PyQt6.QtWidgets import (
    QCalendarWidget,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QScrollArea,
    QSlider,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from gui.components import AccentButton, BodyLabel, CardFrame, SectionTitle

logger = logging.getLogger(__name__)


_MOOD_LABELS = {
    1: "Terrible",
    2: "Very Bad",
    3: "Bad",
    4: "Poor",
    5: "Okay",
    6: "Fair",
    7: "Good",
    8: "Very Good",
    9: "Great",
    10: "Excellent",
}


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------


class MoodTrackerWidget(QWidget):
    """Mood tracking tab with entry form, history, and analytics."""

    mood_saved = pyqtSignal(dict)

    def __init__(
        self,
        theme: dict[str, str],
        mood_manager: Any = None,
        profile_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._mood_manager = mood_manager
        self._profile_manager = profile_manager

        self._symptom_checks: list[QCheckBox] = []
        self._skill_checks: list[QCheckBox] = []

        self._build_ui()
        self._refresh_history()
        self._refresh_analytics()

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

        self._root.addWidget(SectionTitle("Mood Tracker", self._theme))

        body = QHBoxLayout()
        body.setSpacing(16)

        # Left column: calendar + entry form
        left = QVBoxLayout()
        left.setSpacing(12)
        self._build_calendar(left)
        self._build_entry_form(left)
        left.addStretch()
        body.addLayout(left, stretch=3)

        # Right column: history + analytics
        right = QVBoxLayout()
        right.setSpacing(12)
        self._build_history(right)
        self._build_analytics(right)
        right.addStretch()
        body.addLayout(right, stretch=2)

        self._root.addLayout(body)
        self._root.addStretch()

    # -- calendar -------------------------------------------------------

    def _build_calendar(self, parent_layout: QVBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Select Date", self._theme))

        self._calendar = QCalendarWidget()
        self._calendar.setGridVisible(True)
        self._calendar.setStyleSheet(
            f"QCalendarWidget {{ background-color: {self._theme.get('card_bg', '#ffffff')}; }}"
        )
        layout.addWidget(self._calendar)
        parent_layout.addWidget(card)

    # -- entry form -----------------------------------------------------

    def _build_entry_form(self, parent_layout: QVBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.addWidget(SectionTitle("New Mood Entry", self._theme))

        # Time
        time_row = QHBoxLayout()
        time_row.addWidget(BodyLabel("Time:", self._theme))
        self._time_edit = QTimeEdit()
        self._time_edit.setTime(QTime.currentTime())
        self._time_edit.setDisplayFormat("HH:mm")
        time_row.addWidget(self._time_edit)
        time_row.addStretch()
        layout.addLayout(time_row)

        # Mood level
        mood_row = QVBoxLayout()
        mood_header = QHBoxLayout()
        mood_header.addWidget(BodyLabel("Mood Level:", self._theme))
        self._mood_value_label = BodyLabel("5 - Okay", self._theme)
        mood_header.addWidget(self._mood_value_label)
        mood_header.addStretch()
        mood_row.addLayout(mood_header)

        self._mood_slider = QSlider(Qt.Orientation.Horizontal)
        self._mood_slider.setRange(1, 10)
        self._mood_slider.setValue(5)
        self._mood_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._mood_slider.setTickInterval(1)
        self._mood_slider.valueChanged.connect(self._on_mood_slider_changed)
        mood_row.addWidget(self._mood_slider)
        layout.addLayout(mood_row)

        # Condition-specific symptoms
        self._symptoms_group = QGroupBox("Symptoms")
        self._symptoms_group.setStyleSheet(
            f"QGroupBox {{ color: {self._theme.get('text', '#333')}; font-weight: bold; }}"
        )
        symptoms_layout = QGridLayout(self._symptoms_group)
        self._populate_symptoms(symptoms_layout)
        layout.addWidget(self._symptoms_group)

        # Therapy skills used
        self._skills_group = QGroupBox("Therapy Skills Used")
        self._skills_group.setStyleSheet(
            f"QGroupBox {{ color: {self._theme.get('text', '#333')}; font-weight: bold; }}"
        )
        skills_layout = QGridLayout(self._skills_group)
        self._populate_skills(skills_layout)
        layout.addWidget(self._skills_group)

        # Notes
        layout.addWidget(BodyLabel("Notes:", self._theme))
        self._notes_edit = QTextEdit()
        self._notes_edit.setMaximumHeight(100)
        self._notes_edit.setPlaceholderText("How are you feeling? Any triggers or context...")
        self._notes_edit.setStyleSheet(
            f"QTextEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; padding: 8px; }}"
        )
        layout.addWidget(self._notes_edit)

        # Save button
        save_btn = AccentButton("Save Entry", self._theme)
        save_btn.clicked.connect(self._save_entry)
        layout.addWidget(save_btn)

        parent_layout.addWidget(card)

    def _populate_symptoms(self, layout: QGridLayout) -> None:
        default_symptoms = [
            "Anxiety",
            "Low Mood",
            "Irritability",
            "Racing Thoughts",
            "Fatigue",
            "Insomnia",
            "Brain Fog",
            "Restlessness",
            "Panic",
            "Intrusive Thoughts",
            "Flashback",
            "Dissociation",
            "Compulsions",
            "Avoidance",
            "Hopelessness",
            "Numbness",
        ]
        conditions_symptoms: dict[str, list[str]] = {
            "ADHD": ["Hyperfocus", "Difficulty Starting", "Time Blindness", "Impulsivity"],
            "Anxiety": ["Worry", "Tension", "Dread", "Nausea"],
            "Depression": ["Anhedonia", "Guilt", "Worthlessness", "Suicidal Ideation"],
            "OCD": ["Checking", "Counting", "Contamination Fear", "Ordering"],
            "PTSD": ["Hypervigilance", "Nightmares", "Emotional Numbness", "Startle Response"],
        }

        symptoms = list(default_symptoms)
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "conditions") and profile.conditions:
                for cond in profile.conditions:
                    cond_name = cond.value if hasattr(cond, "value") else str(cond)
                    extras = conditions_symptoms.get(cond_name, [])
                    for s in extras:
                        if s not in symptoms:
                            symptoms.append(s)

        self._symptom_checks.clear()
        for idx, symptom in enumerate(symptoms):
            cb = QCheckBox(symptom)
            cb.setStyleSheet(f"color: {self._theme.get('text', '#333')};")
            layout.addWidget(cb, idx // 4, idx % 4)
            self._symptom_checks.append(cb)

    def _populate_skills(self, layout: QGridLayout) -> None:
        default_skills = [
            "Deep Breathing",
            "Grounding",
            "Mindfulness",
            "Journaling",
            "Cognitive Restructuring",
            "Progressive Relaxation",
        ]
        therapy_skills: dict[str, list[str]] = {
            "Cognitive Behavioral Therapy": [
                "Thought Record",
                "Behavioral Activation",
                "Exposure",
                "Cognitive Defusion",
            ],
            "Dialectical Behavior Therapy": [
                "Distress Tolerance",
                "Emotion Regulation",
                "Interpersonal Effectiveness",
                "TIPP Skill",
                "Opposite Action",
                "Radical Acceptance",
            ],
            "Acceptance and Commitment Therapy": [
                "Values Clarification",
                "Committed Action",
                "Defusion",
                "Self-as-Context",
            ],
            "Mindfulness-Based Therapy": [
                "Body Scan",
                "Sitting Meditation",
                "Mindful Movement",
                "Loving Kindness",
            ],
        }

        skills = list(default_skills)
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "therapy_types") and profile.therapy_types:
                for tt in profile.therapy_types:
                    tt_name = tt.value if hasattr(tt, "value") else str(tt)
                    extras = therapy_skills.get(tt_name, [])
                    for s in extras:
                        if s not in skills:
                            skills.append(s)

        self._skill_checks.clear()
        for idx, skill in enumerate(skills):
            cb = QCheckBox(skill)
            cb.setStyleSheet(f"color: {self._theme.get('text', '#333')};")
            layout.addWidget(cb, idx // 3, idx % 3)
            self._skill_checks.append(cb)

    # -- history --------------------------------------------------------

    def _build_history(self, parent_layout: QVBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Mood History", self._theme))

        self._history_list = QListWidget()
        self._history_list.setMinimumHeight(200)
        self._history_list.setStyleSheet(
            f"QListWidget {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; }}"
            f"QListWidget::item {{ padding: 6px; }}"
            f"QListWidget::item:selected {{ background-color: {self._theme.get('accent', '#4a90d9')}; color: #fff; }}"
        )
        layout.addWidget(self._history_list)

        export_btn = AccentButton("Export Mood Data", self._theme)
        export_btn.clicked.connect(self._export_data)
        layout.addWidget(export_btn)

        parent_layout.addWidget(card)

    # -- analytics ------------------------------------------------------

    def _build_analytics(self, parent_layout: QVBoxLayout) -> None:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Mood Analytics", self._theme))

        self._avg_7_label = BodyLabel("7-day average: --", self._theme)
        self._trend_30_label = BodyLabel("30-day trend: --", self._theme)
        self._volatility_label = BodyLabel("Mood volatility: --", self._theme)
        self._triggers_label = BodyLabel("Top triggers: --", self._theme)

        for w in (
            self._avg_7_label,
            self._trend_30_label,
            self._volatility_label,
            self._triggers_label,
        ):
            layout.addWidget(w)

        # Chart placeholder
        self._chart_placeholder = QFrame()
        self._chart_placeholder.setFixedHeight(180)
        self._chart_placeholder.setStyleSheet(
            f"background-color: {self._theme.get('background', '#eee')}; border-radius: 8px;"
        )
        chart_label = QLabel("Mood Chart (matplotlib integration)")
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_label.setStyleSheet(f"color: {self._theme.get('secondary', '#999')};")
        cl = QVBoxLayout(self._chart_placeholder)
        cl.addWidget(chart_label)
        layout.addWidget(self._chart_placeholder)

        parent_layout.addWidget(card)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_mood_slider_changed(self, value: int) -> None:
        label = _MOOD_LABELS.get(value, "")
        self._mood_value_label.setText(f"{value} - {label}")

    def _save_entry(self) -> None:
        selected_date = self._calendar.selectedDate().toPyDate()
        selected_time = self._time_edit.time()
        timestamp = datetime(
            selected_date.year,
            selected_date.month,
            selected_date.day,
            selected_time.hour(),
            selected_time.minute(),
        )

        symptoms = [cb.text() for cb in self._symptom_checks if cb.isChecked()]
        skills = [cb.text() for cb in self._skill_checks if cb.isChecked()]

        entry: dict[str, Any] = {
            "timestamp": timestamp.isoformat(),
            "mood_score": self._mood_slider.value(),
            "symptoms": symptoms,
            "therapy_skills": skills,
            "notes": self._notes_edit.toPlainText().strip(),
        }

        if self._mood_manager:
            try:
                if hasattr(self._mood_manager, "add_entry"):
                    self._mood_manager.add_entry(entry)
                elif hasattr(self._mood_manager, "_entries"):
                    from core.mood_analytics import MoodEntry

                    me = MoodEntry(
                        timestamp=timestamp,
                        mood_score=float(entry["mood_score"]),
                        energy_score=50.0,
                        symptoms=symptoms,
                        notes=entry["notes"],
                        activities=skills,
                    )
                    self._mood_manager._entries.append(me)
            except (AttributeError, TypeError) as exc:
                logger.debug(f"Mood save error: {exc}")

        self.mood_saved.emit(entry)

        # Reset form
        self._mood_slider.setValue(5)
        self._notes_edit.clear()
        for cb in self._symptom_checks:
            cb.setChecked(False)
        for cb in self._skill_checks:
            cb.setChecked(False)
        self._time_edit.setTime(QTime.currentTime())

        self._refresh_history()
        self._refresh_analytics()

        QMessageBox.information(self, "Saved", "Mood entry saved successfully.")

    def _refresh_history(self) -> None:
        self._history_list.clear()
        if not self._mood_manager:
            return
        try:
            entries: list = []
            if hasattr(self._mood_manager, "_entries"):
                entries = list(self._mood_manager._entries)
            entries.sort(key=lambda e: e.timestamp, reverse=True)
            for entry in entries[:50]:
                ts = entry.timestamp.strftime("%Y-%m-%d %H:%M")
                mood = entry.mood_score
                mood_label = _MOOD_LABELS.get(int(mood), "")
                text = f"{ts}  |  Mood: {mood:.0f} ({mood_label})"
                item = QListWidgetItem(text)
                if mood <= 3:
                    item.setForeground(
                        self._history_list.palette().color(
                            self._history_list.palette().ColorRole.Text
                        )
                    )
                self._history_list.addItem(item)
        except (AttributeError, TypeError) as exc:
            logger.debug(f"History refresh error: {exc}")

    def _refresh_analytics(self) -> None:
        if not self._mood_manager:
            return
        try:
            if hasattr(self._mood_manager, "mood_trend"):
                trend = self._mood_manager.mood_trend()
                if trend.moving_avg_7 is not None:
                    self._avg_7_label.setText(f"7-day average: {trend.moving_avg_7:.1f}")
                self._trend_30_label.setText(f"30-day trend: {trend.direction.value.capitalize()}")
            if hasattr(self._mood_manager, "mood_volatility"):
                vol = self._mood_manager.mood_volatility()
                self._volatility_label.setText(f"Mood volatility: {vol:.2f}")
            if hasattr(self._mood_manager, "identify_triggers"):
                triggers = self._mood_manager.identify_triggers()[:3]
                if triggers:
                    names = [t.trigger for t in triggers]
                    self._triggers_label.setText(f"Top triggers: {', '.join(names)}")
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Analytics refresh error: {exc}")

    def _export_data(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Mood Data", "mood_data.json", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            import json

            entries: list = []
            if self._mood_manager and hasattr(self._mood_manager, "_entries"):
                for e in self._mood_manager._entries:
                    entries.append(
                        {
                            "timestamp": e.timestamp.isoformat(),
                            "mood_score": e.mood_score,
                            "energy_score": 50,
                            "symptoms": e.symptoms,
                            "notes": e.notes,
                        }
                    )
            with open(path, "w") as fh:
                json.dump(entries, fh, indent=2)
            QMessageBox.information(self, "Exported", f"Mood data exported to {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Export failed: {exc}")

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
