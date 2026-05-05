"""DBT Diary Card widget — daily emotions, urges, skills, targets.

One card per day. Designed for quick evening reflection.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.components import AccentButton, BodyLabel, CardFrame, SectionTitle

logger = logging.getLogger(__name__)

_EFFECTIVENESS_LABELS = {1: "Not helpful", 2: "Slightly helpful", 3: "Moderately helpful", 4: "Very helpful", 5: "Extremely helpful"}


class DiaryCardWidget(QWidget):
    """Daily DBT diary card entry form."""

    card_saved = pyqtSignal(dict)

    def __init__(
        self,
        theme: dict[str, str],
        diary_card_manager: Any = None,
        profile_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._manager = diary_card_manager
        self._profile_manager = profile_manager

        self._emotion_checks: list[QCheckBox] = []
        self._urge_spins: dict[str, QSpinBox] = {}
        self._skill_checks: list[QCheckBox] = []
        self._target_spins: dict[str, QSpinBox] = []

        self._build_ui()
        self._load_today()

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

        self._root.addWidget(SectionTitle("Diary Card", self._theme))

        # Date picker row
        date_row = QHBoxLayout()
        date_row.addWidget(BodyLabel("Date:", self._theme))
        self._calendar = QCalendarWidget()
        self._calendar.setGridVisible(True)
        self._calendar.setMaximumHeight(220)
        self._calendar.setStyleSheet(
            f"QCalendarWidget {{ background-color: {self._theme.get('card_bg', '#fff')}; }}"
        )
        self._calendar.selectionChanged.connect(self._on_date_changed)
        date_row.addWidget(self._calendar)
        date_row.addStretch()
        self._root.addLayout(date_row)

        # Mood
        self._root.addWidget(self._build_mood_card())

        # Emotions
        self._root.addWidget(self._build_emotions_card())

        # Urges
        self._root.addWidget(self._build_urges_card())

        # Skills
        self._root.addWidget(self._build_skills_card())

        # Targets
        self._root.addWidget(self._build_targets_card())

        # Medications & substances
        self._root.addWidget(self._build_meds_card())

        # Notes
        self._root.addWidget(self._build_notes_card())

        # Save
        save_btn = AccentButton("Save Diary Card", self._theme)
        save_btn.clicked.connect(self._save_card)
        self._root.addWidget(save_btn)
        self._root.addStretch()

    def _build_mood_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Overall Mood", self._theme))

        row = QHBoxLayout()
        row.addWidget(BodyLabel("Mood (1-10):", self._theme))
        self._mood_slider = QSlider(Qt.Orientation.Horizontal)
        self._mood_slider.setRange(1, 10)
        self._mood_slider.setValue(5)
        self._mood_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._mood_slider.setTickInterval(1)
        self._mood_label = BodyLabel("5", self._theme)
        self._mood_slider.valueChanged.connect(
            lambda v: self._mood_label.setText(str(v))
        )
        row.addWidget(self._mood_slider)
        row.addWidget(self._mood_label)
        layout.addLayout(row)
        return card

    def _build_emotions_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Emotions Felt Today", self._theme))

        emotions = self._get_emotions()
        grid = QGridLayout()
        grid.setSpacing(8)
        self._emotion_checks.clear()
        for idx, emotion in enumerate(emotions):
            cb = QCheckBox(emotion)
            cb.setStyleSheet(f"color: {self._theme.get('text', '#333')};")
            grid.addWidget(cb, idx // 4, idx % 4)
            self._emotion_checks.append(cb)
        layout.addLayout(grid)
        return card

    def _build_urges_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Urges (0 = none, 5 = strongest)", self._theme))

        urges = self._get_urges()
        grid = QGridLayout()
        grid.setSpacing(8)
        self._urge_spins.clear()
        for idx, (urge, default) in enumerate(urges.items()):
            row = QHBoxLayout()
            lbl = BodyLabel(urge, self._theme)
            lbl.setMinimumWidth(140)
            row.addWidget(lbl)
            spin = QSpinBox()
            spin.setRange(0, 5)
            spin.setValue(default)
            row.addWidget(spin)
            row.addStretch()
            grid.addLayout(row, idx // 2, idx % 2)
            self._urge_spins[urge] = spin
        layout.addLayout(grid)
        return card

    def _build_skills_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Skills Used Today", self._theme))

        skills = self._get_skills()
        grid = QGridLayout()
        grid.setSpacing(8)
        self._skill_checks.clear()
        for idx, skill in enumerate(skills):
            cb = QCheckBox(skill)
            cb.setStyleSheet(f"color: {self._theme.get('text', '#333')};")
            grid.addWidget(cb, idx // 3, idx % 3)
            self._skill_checks.append(cb)

        # Effectiveness
        eff_row = QHBoxLayout()
        eff_row.addWidget(BodyLabel("How effective were they?", self._theme))
        self._effectiveness = QSlider(Qt.Orientation.Horizontal)
        self._effectiveness.setRange(1, 5)
        self._effectiveness.setValue(3)
        self._effectiveness.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._effectiveness.setTickInterval(1)
        self._eff_label = BodyLabel("3 - Moderately helpful", self._theme)
        self._effectiveness.valueChanged.connect(self._on_eff_changed)
        eff_row.addWidget(self._effectiveness)
        eff_row.addWidget(self._eff_label)
        layout.addLayout(grid)
        layout.addLayout(eff_row)
        return card

    def _build_targets_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Target Behaviors (count today)", self._theme))

        targets = self._get_targets()
        grid = QGridLayout()
        grid.setSpacing(8)
        self._target_spins.clear()
        for idx, (target, default) in enumerate(targets.items()):
            row = QHBoxLayout()
            lbl = BodyLabel(target, self._theme)
            lbl.setMinimumWidth(180)
            row.addWidget(lbl)
            spin = QSpinBox()
            spin.setRange(0, 50)
            spin.setValue(default)
            row.addWidget(spin)
            row.addStretch()
            grid.addLayout(row, idx // 2, idx % 2)
            self._target_spins[target] = spin
        layout.addLayout(grid)
        return card

    def _build_meds_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Medications & Substances", self._theme))

        med_row = QHBoxLayout()
        med_row.addWidget(BodyLabel("Took medications as prescribed?", self._theme))
        self._meds_yes = QRadioButton("Yes")
        self._meds_no = QRadioButton("No")
        self._meds_yes.setStyleSheet(f"color: {self._theme.get('text', '#333')};")
        self._meds_no.setStyleSheet(f"color: {self._theme.get('text', '#333')};")
        self._meds_group = QButtonGroup(self)
        self._meds_group.addButton(self._meds_yes)
        self._meds_group.addButton(self._meds_no)
        self._meds_yes.setChecked(True)
        med_row.addWidget(self._meds_yes)
        med_row.addWidget(self._meds_no)
        med_row.addStretch()
        layout.addLayout(med_row)

        sub_row = QHBoxLayout()
        sub_row.addWidget(BodyLabel("Substances used (optional):", self._theme))
        self._substances = QLineEdit()
        self._substances.setPlaceholderText("e.g. alcohol, caffeine, cannabis...")
        self._substances.setStyleSheet(
            f"QLineEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; padding: 6px; }}"
        )
        sub_row.addWidget(self._substances)
        layout.addLayout(sub_row)
        return card

    def _build_notes_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Notes", self._theme))
        self._notes = QTextEdit()
        self._notes.setMaximumHeight(100)
        self._notes.setPlaceholderText("Anything else worth noting today...")
        self._notes.setStyleSheet(
            f"QTextEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; padding: 8px; }}"
        )
        layout.addWidget(self._notes)
        return card

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    def _get_conditions(self) -> list[Any]:
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "conditions") and profile.conditions:
                return list(profile.conditions)
        return []

    def _get_emotions(self) -> list[str]:
        if self._manager and hasattr(self._manager, "emotions_for_conditions"):
            return self._manager.emotions_for_conditions(self._get_conditions())
        from core.diary_card_manager import DiaryCardManager
        return DiaryCardManager.emotions_for_conditions(self._get_conditions())

    def _get_urges(self) -> dict[str, int]:
        if self._manager and hasattr(self._manager, "urges_for_conditions"):
            return self._manager.urges_for_conditions(self._get_conditions())
        from core.diary_card_manager import DiaryCardManager
        return DiaryCardManager.urges_for_conditions(self._get_conditions())

    def _get_skills(self) -> list[str]:
        if self._manager and hasattr(self._manager, "skills_for_conditions"):
            return self._manager.skills_for_conditions(self._get_conditions())
        from core.diary_card_manager import DiaryCardManager
        return DiaryCardManager.skills_for_conditions(self._get_conditions())

    def _get_targets(self) -> dict[str, int]:
        if self._manager and hasattr(self._manager, "targets_for_conditions"):
            return self._manager.targets_for_conditions(self._get_conditions())
        from core.diary_card_manager import DiaryCardManager
        return DiaryCardManager.targets_for_conditions(self._get_conditions())

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_eff_changed(self, value: int) -> None:
        self._eff_label.setText(f"{value} - {_EFFECTIVENESS_LABELS.get(value, '')}")

    def _on_date_changed(self) -> None:
        self._load_today()

    def _save_card(self) -> None:
        from core.diary_card_manager import DiaryCard

        selected_date = self._calendar.selectedDate().toPyDate()

        emotions = [cb.text() for cb in self._emotion_checks if cb.isChecked()]
        skills = [cb.text() for cb in self._skill_checks if cb.isChecked()]
        urges = {name: spin.value() for name, spin in self._urge_spins.items()}
        targets = {name: spin.value() for name, spin in self._target_spins.items()}

        card = DiaryCard(
            date=selected_date,
            mood_score=self._mood_slider.value(),
            emotions=emotions,
            urges=urges,
            skills_used=skills,
            skills_effectiveness=self._effectiveness.value(),
            target_behaviors=targets,
            substances_used=self._substances.text().strip(),
            medications_taken=self._meds_yes.isChecked(),
            notes=self._notes.toPlainText().strip(),
        )

        if self._manager and hasattr(self._manager, "save"):
            try:
                self._manager.save(card)
            except Exception as exc:
                logger.error(f"Diary card save error: {exc}")
                QMessageBox.warning(self, "Error", f"Failed to save: {exc}")
                return

        self.card_saved.emit(card.to_db_dict())
        QMessageBox.information(self, "Saved", f"Diary card for {selected_date.isoformat()} saved.")

    def _load_today(self) -> None:
        if not self._manager or not hasattr(self._manager, "get"):
            return
        selected_date = self._calendar.selectedDate().toPyDate()
        try:
            card = self._manager.get(selected_date)
        except Exception as exc:
            logger.debug(f"Diary card load error: {exc}")
            return
        if not card:
            self._clear_form()
            return

        self._mood_slider.setValue(card.mood_score)
        self._mood_label.setText(str(card.mood_score))

        for cb in self._emotion_checks:
            cb.setChecked(cb.text() in card.emotions)

        for name, spin in self._urge_spins.items():
            spin.setValue(card.urges.get(name, 0))

        for cb in self._skill_checks:
            cb.setChecked(cb.text() in card.skills_used)

        self._effectiveness.setValue(card.skills_effectiveness)
        self._eff_label.setText(
            f"{card.skills_effectiveness} - {_EFFECTIVENESS_LABELS.get(card.skills_effectiveness, '')}"
        )

        for name, spin in self._target_spins.items():
            spin.setValue(card.target_behaviors.get(name, 0))

        self._meds_yes.setChecked(card.medications_taken)
        self._meds_no.setChecked(not card.medications_taken)
        self._substances.setText(card.substances_used)
        self._notes.setPlainText(card.notes)

    def _clear_form(self) -> None:
        self._mood_slider.setValue(5)
        self._mood_label.setText("5")
        for cb in self._emotion_checks:
            cb.setChecked(False)
        for spin in self._urge_spins.values():
            spin.setValue(0)
        for cb in self._skill_checks:
            cb.setChecked(False)
        self._effectiveness.setValue(3)
        self._eff_label.setText("3 - Moderately helpful")
        for spin in self._target_spins.values():
            spin.setValue(0)
        self._meds_yes.setChecked(True)
        self._meds_no.setChecked(False)
        self._substances.clear()
        self._notes.clear()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
