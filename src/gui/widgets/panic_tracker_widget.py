"""
Panic attack tracker widget for logging, history, and pattern analysis.

Provides a structured panic log with onset, peak distress, symptoms,
triggers, resolution, and technique effectiveness tracking.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SYMPTOM_OPTIONS = [
    "Racing heart", "Sweating", "Trembling", "Shortness of breath",
    "Chest tightness", "Nausea", "Dizziness", "Derealization",
    "Fear of losing control", "Fear of dying", "Numbness", "Chills",
]

_TECHNIQUE_OPTIONS = [
    "4-7-8 Breathing", "Box Breathing", "5-4-3-2-1 Grounding",
    "Cold water on face", "Called someone", "Walked", "Medication",
    "Waited it out", "Other",
]


class _PanicLogDialog(QDialog):
    """Dialog for logging a panic attack."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Log Panic Attack")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Peak distress
        layout.addWidget(QLabel("Peak distress (0-10):"))
        self._distress_spin = QSpinBox()
        self._distress_spin.setRange(0, 10)
        self._distress_spin.setValue(7)
        layout.addWidget(self._distress_spin)

        # Symptoms
        layout.addWidget(QLabel("Symptoms (check all that apply):"))
        symptoms_layout = QVBoxLayout()
        self._symptom_checks: dict[str, QCheckBox] = {}
        for symptom in _SYMPTOM_OPTIONS:
            cb = QCheckBox(symptom)
            self._symptom_checks[symptom] = cb
            symptoms_layout.addWidget(cb)
        layout.addLayout(symptoms_layout)

        # Trigger
        layout.addWidget(QLabel("Trigger (optional):"))
        self._trigger_edit = QLineEdit()
        self._trigger_edit.setPlaceholderText("What happened just before?")
        layout.addWidget(self._trigger_edit)

        # Techniques used
        layout.addWidget(QLabel("Techniques used (check all that apply):"))
        tech_layout = QVBoxLayout()
        self._tech_checks: dict[str, QCheckBox] = {}
        for tech in _TECHNIQUE_OPTIONS:
            cb = QCheckBox(tech)
            self._tech_checks[tech] = cb
            tech_layout.addWidget(cb)
        layout.addLayout(tech_layout)

        # Resolution time
        layout.addWidget(QLabel("Approximate duration (minutes):"))
        self._duration_spin = QSpinBox()
        self._duration_spin.setRange(1, 180)
        self._duration_spin.setValue(15)
        layout.addWidget(self._duration_spin)

        # Notes
        layout.addWidget(QLabel("Notes:"))
        self._notes_edit = QTextEdit()
        self._notes_edit.setMaximumHeight(80)
        layout.addWidget(self._notes_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self) -> dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(),
            "peak_distress": self._distress_spin.value(),
            "symptoms": [s for s, cb in self._symptom_checks.items() if cb.isChecked()],
            "trigger": self._trigger_edit.text().strip(),
            "techniques": [t for t, cb in self._tech_checks.items() if cb.isChecked()],
            "duration_minutes": self._duration_spin.value(),
            "notes": self._notes_edit.toPlainText().strip(),
        }


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

class PanicTrackerWidget(QWidget):
    """Panic attack logging and analysis tab."""

    panic_logged = pyqtSignal(dict)

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self._entries: list[dict[str, Any]] = []
        self._data_dir = self._resolve_data_dir()
        self._load_entries()

        self._build_ui()
        self._refresh_history()
        self._refresh_stats()

    def _resolve_data_dir(self) -> Path:
        try:
            return Path(self.main_window.data_dir) / "panic_logs"
        except (AttributeError, TypeError):
            return Path.home() / ".mindful_optimizer" / "panic_logs"

    def _load_entries(self) -> None:
        file_path = self._data_dir / "panic_logs.json"
        if file_path.exists():
            try:
                with open(file_path) as f:
                    self._entries = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"Panic logs load error: {exc}")

    def _save_entries(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._data_dir / "panic_logs.json", "w") as f:
                json.dump(self._entries, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save panic logs: {e}")

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setSpacing(16)
        root.setContentsMargins(24, 24, 24, 24)
        scroll.setWidget(container)

        # Title
        title = QLabel("Panic Attack Tracker")
        title.setFont(QFont(self.font().family(), 18, QFont.Weight.Bold))
        root.addWidget(title)

        subtitle = QLabel(
            "Log panic attacks to identify patterns, triggers, and "
            "which techniques help you most."
        )
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        # Log button
        log_btn = QPushButton("Log New Panic Attack")
        log_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        log_btn.setMinimumHeight(48)
        log_btn.clicked.connect(self._show_log_dialog)
        root.addWidget(log_btn)

        # Stats
        self._stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(self._stats_group)
        self._stats_label = QLabel("No data yet.")
        self._stats_label.setWordWrap(True)
        stats_layout.addWidget(self._stats_label)
        root.addWidget(self._stats_group)

        # History
        self._history_group = QGroupBox("History")
        history_layout = QVBoxLayout(self._history_group)
        self._history_list = QListWidget()
        history_layout.addWidget(self._history_list)
        root.addWidget(self._history_group)

        # Insights
        self._insights_group = QGroupBox("Insights")
        insights_layout = QVBoxLayout(self._insights_group)
        self._insights_label = QLabel("Log at least 2 entries to see insights.")
        self._insights_label.setWordWrap(True)
        insights_layout.addWidget(self._insights_label)
        root.addWidget(self._insights_group)

        root.addStretch()

    def _show_log_dialog(self) -> None:
        dialog = _PanicLogDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            entry = dialog.get_data()
            self._entries.insert(0, entry)
            self._save_entries()
            self._refresh_history()
            self._refresh_stats()
            self._refresh_insights()
            self.panic_logged.emit(entry)

    def _refresh_history(self) -> None:
        self._history_list.clear()
        for entry in self._entries[:20]:
            ts = entry.get("timestamp", "Unknown")
            distress = entry.get("peak_distress", "?")
            trigger = entry.get("trigger", "")
            text = f"[{ts[:16]}] Distress: {distress}/10"
            if trigger:
                text += f" — Trigger: {trigger}"
            self._history_list.addItem(text)

    def _refresh_stats(self) -> None:
        if not self._entries:
            self._stats_label.setText("No panic attacks logged yet.")
            return

        total = len(self._entries)
        avg_distress = sum(e.get("peak_distress", 0) for e in self._entries) / total
        avg_duration = sum(e.get("duration_minutes", 0) for e in self._entries) / total

        # Most common technique
        tech_counts: dict[str, int] = {}
        for e in self._entries:
            for t in e.get("techniques", []):
                tech_counts[t] = tech_counts.get(t, 0) + 1
        most_common_tech = max(tech_counts, key=lambda k: tech_counts.get(k, 0)) if tech_counts else "None"

        self._stats_label.setText(
            f"Total logged: {total}\n"
            f"Average peak distress: {avg_distress:.1f}/10\n"
            f"Average duration: {avg_duration:.0f} minutes\n"
            f"Most used technique: {most_common_tech}"
        )

    def _refresh_insights(self) -> None:
        if len(self._entries) < 2:
            return

        insights: list[str] = []

        # Frequency trend
        recent = self._entries[:7]
        older = self._entries[7:14]
        if len(older) > 0 and len(recent) > len(older):
            insights.append(
                f"Panic attacks have increased recently ({len(recent)} in last 7 logs vs "
                f"{len(older)} in prior 7). Consider reviewing triggers with your clinician."
            )

        # Distress trend
        recent_distress = [e.get("peak_distress", 0) for e in recent]
        older_distress = [e.get("peak_distress", 0) for e in older]
        if recent_distress and older_distress and (
            sum(recent_distress) / len(recent_distress) < sum(older_distress) / len(older_distress)
        ):
                insights.append(
                    "Your average peak distress has decreased — whatever you're doing is helping."
                )

        # Technique effectiveness
        tech_to_distress: dict[str, list[int]] = {}
        for e in self._entries:
            for t in e.get("techniques", []):
                tech_to_distress.setdefault(t, []).append(e.get("peak_distress", 0))
        if tech_to_distress:
            avg_by_tech = {
                t: sum(vals) / len(vals)
                for t, vals in tech_to_distress.items()
                if len(vals) >= 2
            }
            if avg_by_tech:
                best = min(avg_by_tech, key=lambda k: avg_by_tech[k])
                insights.append(
                    f"'{best}' is associated with lower distress on average. "
                    f"Consider using it earlier in an episode."
                )

        self._insights_label.setText("\n\n".join(insights) if insights else "Keep logging to see insights.")
