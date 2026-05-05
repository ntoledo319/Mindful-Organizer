"""
Multi-page onboarding wizard for Mindful Organizer.

Guides the user through profile setup: welcome, name, condition selection,
therapy types, theme selection, and summary -- using a QStackedWidget with
progress dots and Back/Next/Skip/Finish navigation.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _body_label(text: str, size: int = 12) -> QLabel:
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", size))
    label.setWordWrap(True)
    return label


def _title_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


def _accent_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setMinimumHeight(40)
    return btn


# ---------------------------------------------------------------------------
# Condition & therapy data
# ---------------------------------------------------------------------------

_CONDITION_INFO: dict[str, str] = {
    "ADHD": (
        "Attention Deficit Hyperactivity Disorder -- difficulty with focus, "
        "impulse control, and executive function. The app adapts with "
        "gamification, quick wins, and structured reminders."
    ),
    "Anxiety": (
        "Generalised or specific anxiety disorders -- excessive worry, "
        "tension, and avoidance. The app provides calming interfaces, "
        "breathing exercises, and predictable structure."
    ),
    "Depression": (
        "Major Depressive Disorder or related conditions -- low mood, "
        "fatigue, and loss of interest. The app offers encouraging "
        "feedback, energy-aware task scheduling, and mood tracking."
    ),
    "OCD": (
        "Obsessive-Compulsive Disorder -- intrusive thoughts and "
        "compulsive behaviours. The app includes ERP tracking, flexible "
        "structure, and values-based motivation."
    ),
    "PTSD": (
        "Post-Traumatic Stress Disorder -- trauma responses, hypervigilance, "
        "and avoidance. The app provides grounding tools, gentle notifications, "
        "and safe-space features."
    ),
    "Bipolar": (
        "Bipolar Disorder -- mood episodes ranging from depression to mania. "
        "The app helps track mood patterns, sleep, and medication adherence."
    ),
}

_THERAPY_INFO: dict[str, str] = {
    "CBT": (
        "Cognitive Behavioral Therapy -- focuses on identifying and changing "
        "negative thought patterns. The app integrates thought records and "
        "behavioral activation."
    ),
    "DBT": (
        "Dialectical Behavior Therapy -- teaches skills in mindfulness, "
        "distress tolerance, emotion regulation, and interpersonal effectiveness."
    ),
    "ACT": (
        "Acceptance and Commitment Therapy -- emphasises psychological "
        "flexibility through acceptance, mindfulness, and values-driven action."
    ),
    "Mindfulness": (
        "Mindfulness-Based Therapy -- cultivates present-moment awareness "
        "to reduce reactivity and improve wellbeing."
    ),
    "ERP": (
        "Exposure and Response Prevention -- the gold standard for OCD "
        "treatment support. Gradual exposure to feared stimuli while resisting compulsions."
    ),
}


# ---------------------------------------------------------------------------
# Wizard
# ---------------------------------------------------------------------------

class OnboardingWizard(QDialog):
    """Multi-page onboarding wizard (6 pages)."""

    onboarding_completed = pyqtSignal(dict)

    _TOTAL_PAGES = 6

    def __init__(
        self,
        profile_manager: Any,
        data_dir: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to Mindful Organizer")
        self.setMinimumSize(750, 650)
        self._profile_manager = profile_manager
        self._data_dir = data_dir

        # Collected data
        self._data: dict[str, Any] = {
            "name": "",
            "conditions": [],
            "therapy_types": [],
            "theme": "light",
        }

        self._current_page = 0
        self._build_ui()
        self._show_page(0)

    # ------------------------------------------------------------------
    # UI skeleton
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(32, 24, 32, 24)

        # Progress dots
        self._dots_layout = QHBoxLayout()
        self._dots_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dots: list[QLabel] = []
        for _i in range(self._TOTAL_PAGES):
            dot = QLabel()
            dot.setFixedSize(14, 14)
            dot.setStyleSheet("background-color: #ccc; border-radius: 7px;")
            self._dots_layout.addWidget(dot)
            self._dots.append(dot)
        root.addLayout(self._dots_layout)

        # Stacked pages
        self._stack = QStackedWidget()
        self._stack.addWidget(self._page_welcome())       # 0
        self._stack.addWidget(self._page_name())           # 1
        self._stack.addWidget(self._page_conditions())     # 2
        self._stack.addWidget(self._page_therapy())        # 3
        self._stack.addWidget(self._page_theme())          # 4
        self._stack.addWidget(self._page_summary())        # 5
        root.addWidget(self._stack, stretch=1)

        # Navigation buttons
        nav = QHBoxLayout()
        self._back_btn = _accent_button("Back")
        self._back_btn.clicked.connect(self._go_back)
        nav.addWidget(self._back_btn)

        nav.addStretch()

        self._skip_btn = QPushButton("Skip")
        self._skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._skip_btn.clicked.connect(self._go_next)
        nav.addWidget(self._skip_btn)

        self._next_btn = _accent_button("Next")
        self._next_btn.clicked.connect(self._go_next)
        nav.addWidget(self._next_btn)

        root.addLayout(nav)

    def _show_page(self, index: int) -> None:
        self._current_page = max(0, min(index, self._TOTAL_PAGES - 1))
        self._stack.setCurrentIndex(self._current_page)

        # Update dots
        for i, dot in enumerate(self._dots):
            if i == self._current_page:
                dot.setStyleSheet("background-color: #4a90d9; border-radius: 7px;")
            elif i < self._current_page:
                dot.setStyleSheet("background-color: #27ae60; border-radius: 7px;")
            else:
                dot.setStyleSheet("background-color: #ccc; border-radius: 7px;")

        self._back_btn.setVisible(self._current_page > 0)
        is_last = self._current_page == self._TOTAL_PAGES - 1
        self._next_btn.setText("Get Started" if is_last else "Next")
        self._skip_btn.setVisible(not is_last and self._current_page > 0)

        # Refresh summary on last page
        if self._current_page == self._TOTAL_PAGES - 1:
            self._refresh_summary()

    def _go_next(self) -> None:
        self._collect_page_data()
        if self._current_page >= self._TOTAL_PAGES - 1:
            self._finish()
        else:
            self._show_page(self._current_page + 1)

    def _go_back(self) -> None:
        self._collect_page_data()
        self._show_page(self._current_page - 1)

    def _collect_page_data(self) -> None:
        page = self._current_page
        if page == 1:
            self._data["name"] = self._name_input.text().strip()
        elif page == 2:
            self._data["conditions"] = [
                name for name, cb in self._condition_checks.items() if cb.isChecked()
            ]
        elif page == 3:
            self._data["therapy_types"] = [
                name for name, cb in self._therapy_checks.items() if cb.isChecked()
            ]
        elif page == 4:
            self._data["theme"] = self._theme_combo.currentData() or "light"

    def _finish(self) -> None:
        self._collect_page_data()

        # Create profile via profile_manager
        try:
            from profiles.mental_health_profile_builder import (
                Condition,
                OrganizationPreference,
                Profile,
                TherapyType,
                UIPreference,
            )

            # Map condition names to enums
            condition_map = {c.value: c for c in Condition}
            conditions: set[Condition] = set()
            for name in self._data.get("conditions", []):
                if name in condition_map:
                    conditions.add(condition_map[name])

            # Map therapy names to enums
            therapy_map = {
                "CBT": TherapyType.CBT,
                "DBT": TherapyType.DBT,
                "ACT": TherapyType.ACT,
                "Mindfulness": TherapyType.MINDFULNESS,
            }
            therapy_types: set[TherapyType] = set()
            for name in self._data.get("therapy_types", []):
                if name in therapy_map:
                    therapy_types.add(therapy_map[name])

            # Build a profile object
            now = datetime.now().isoformat()
            profile = Profile(
                name=self._data.get("name") or "User",
                conditions=conditions,
                therapy_types=therapy_types,
                therapy_skills=set(),
                ui_preferences=UIPreference(
                    color_scheme=self._data.get("theme", "light"),
                    contrast_level="normal",
                    animation_speed="normal",
                    notification_style="standard",
                    layout_density="medium",
                    font_size="14",
                    use_icons=True,
                    use_sound=True,
                ),
                organization_preferences=OrganizationPreference(
                    folder_depth=3,
                    naming_convention="standard",
                    sort_priority=["priority", "due_date"],
                    automation_level="medium",
                    backup_frequency="daily",
                    reminder_frequency="normal",
                ),
                created_at=now,
                updated_at=now,
            )
            self._profile_manager.current_profile = profile
        except Exception as e:
            logger.error(f"Failed to create profile during onboarding: {e}")
            # Fallback: try simpler creation
            try:
                if hasattr(self._profile_manager, "create_profile"):
                    self._profile_manager.create_profile(
                        name=self._data.get("name") or "User",
                        conditions=set(),
                    )
            except (AttributeError, TypeError) as exc:
                logger.debug(f"Profile creation error: {exc}")

        # Apply selected theme
        try:
            parent_window = self.parent()
            if parent_window and hasattr(parent_window, "change_theme"):
                parent_window.change_theme(self._data.get("theme", "light"))
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Theme change error: {exc}")

        self.onboarding_completed.emit(self._data)
        self.accept()

    # ------------------------------------------------------------------
    # Pages
    # ------------------------------------------------------------------

    def _page_welcome(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.addStretch()

        layout.addWidget(_title_label("Mindful Organizer"))

        tagline = _body_label(
            "Your mental health-aware productivity companion",
            14,
        )
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("font-style: italic;")
        layout.addWidget(tagline)

        desc = _body_label(
            "A desktop organiser that adapts to your needs based on your "
            "mental health conditions, therapy approach, and personal preferences.\n\n"
            "This short setup will personalise your experience. "
            "You can change any of these settings later.",
            13,
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        layout.addStretch()
        return page

    def _page_name(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.addStretch()

        layout.addWidget(_title_label("About You"))
        layout.addWidget(_body_label("What should we call you?", 13))

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Your name or nickname")
        self._name_input.setFont(QFont("Segoe UI", 14))
        self._name_input.setMinimumHeight(44)
        layout.addWidget(self._name_input)

        layout.addStretch()
        return page

    def _page_conditions(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        layout.addWidget(_title_label("Conditions"))
        layout.addWidget(_body_label(
            "Select any conditions that apply. This helps us tailor the experience.",
        ))

        self._condition_checks: dict[str, QCheckBox] = {}
        for name, description in _CONDITION_INFO.items():
            group = QGroupBox(name)
            group.setCheckable(True)
            group.setChecked(False)
            group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            gl = QVBoxLayout(group)
            gl.addWidget(_body_label(description, 11))
            layout.addWidget(group)
            cb = QCheckBox()
            cb.setVisible(False)
            group.toggled.connect(cb.setChecked)
            self._condition_checks[name] = cb

        layout.addStretch()
        return page

    def _page_therapy(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        layout.addWidget(_title_label("Therapy Types"))
        layout.addWidget(_body_label(
            "Select therapy approaches you use or are interested in.",
        ))

        self._therapy_checks: dict[str, QCheckBox] = {}
        for name, description in _THERAPY_INFO.items():
            group = QGroupBox(name)
            group.setCheckable(True)
            group.setChecked(False)
            group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            gl = QVBoxLayout(group)
            gl.addWidget(_body_label(description, 11))
            layout.addWidget(group)
            cb = QCheckBox()
            cb.setVisible(False)
            group.toggled.connect(cb.setChecked)
            self._therapy_checks[name] = cb

        layout.addStretch()
        return page

    def _page_theme(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.addStretch()

        layout.addWidget(_title_label("Choose Your Theme"))

        row = QHBoxLayout()
        row.addWidget(_body_label("Theme:", 13))
        self._theme_combo = QComboBox()
        self._theme_combo.setFont(QFont("Segoe UI", 13))

        # Populate from ThemeManager if available
        try:
            from gui.themes import THEMES
            for name, theme in THEMES.items():
                self._theme_combo.addItem(f"{theme.display_name} - {theme.description}", name)
        except (ImportError, AttributeError):
            self._theme_combo.addItem("Light", "light")
            self._theme_combo.addItem("Dark", "dark")
            self._theme_combo.addItem("Calm", "calm")

        self._theme_combo.currentIndexChanged.connect(self._preview_theme)
        row.addWidget(self._theme_combo)
        row.addStretch()
        layout.addLayout(row)

        # Preview area
        self._theme_preview = QFrame()
        self._theme_preview.setFixedHeight(100)
        self._theme_preview.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(self._theme_preview)
        self._preview_theme(0)

        layout.addStretch()
        return page

    def _preview_theme(self, index: int) -> None:
        theme_name = self._theme_combo.itemData(index) if isinstance(index, int) else index
        try:
            from gui.themes import THEMES
            theme = THEMES.get(theme_name)
            if theme:
                self._theme_preview.setStyleSheet(
                    f"QFrame {{ background-color: {theme.background}; "
                    f"border: 3px solid {theme.accent}; border-radius: 12px; }}"
                )
                return
        except (ImportError, AttributeError) as exc:
            logger.debug(f"Theme preview error: {exc}")
        self._theme_preview.setStyleSheet(
            "QFrame { background-color: #f5f5f5; border: 3px solid #4a90d9; border-radius: 12px; }"
        )

    def _page_summary(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.addStretch()

        layout.addWidget(_title_label("Ready to Start!"))

        self._summary_label = _body_label("", 13)
        self._summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._summary_label)

        layout.addWidget(_body_label(
            "You can change any of these settings later in the Settings tab.",
            12,
        ))
        layout.addStretch()
        return page

    def _refresh_summary(self) -> None:
        self._collect_page_data()
        d = self._data
        theme_display = self._theme_combo.currentText() if hasattr(self, "_theme_combo") else d.get("theme", "Light")
        lines = [
            f"Name: {d.get('name') or 'Not set'}",
            f"Conditions: {', '.join(d.get('conditions', [])) or 'None selected'}",
            f"Therapy types: {', '.join(d.get('therapy_types', [])) or 'None selected'}",
            f"Theme: {theme_display}",
        ]
        self._summary_label.setText("\n".join(lines))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_data(self) -> dict[str, Any]:
        """Return the collected onboarding data."""
        return dict(self._data)
