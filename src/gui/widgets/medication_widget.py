"""
Medication tracking widget for Mindful Organizer.

Provides a medication list with add/edit/remove, a daily schedule with
take-it checkboxes, a recent forgiving "rhythm" summary (steady days, not a
shrinking percentage), a quiet disclaimer, and export-for-doctor functionality.
"""

from __future__ import annotations

import contextlib
import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QTime, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _section_title(text: str) -> QLabel:
    label = QLabel(text)
    # Keep the family the app theme already set on inherited fonts; only adjust
    # size and weight so headings never pin a hardcoded "Segoe UI".
    font = label.font()
    font.setPointSize(14)
    font.setWeight(QFont.Weight.Bold)
    label.setFont(font)
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
# Add/Edit medication dialog
# ---------------------------------------------------------------------------


class _MedicationDialog(QDialog):
    """Dialog for adding or editing a medication."""

    def __init__(
        self,
        med: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Medication" if not med else f"Edit: {med.get('name', '')}")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Name
        layout.addWidget(_body_label("Medication name:"))
        self._name = QLineEdit(med.get("name", "") if med else "")
        self._name.setPlaceholderText("e.g. Sertraline")
        layout.addWidget(self._name)

        # Dosage
        layout.addWidget(_body_label("Dosage:"))
        self._dosage = QLineEdit(med.get("dosage", "") if med else "")
        self._dosage.setPlaceholderText("e.g. 50mg")
        layout.addWidget(self._dosage)

        # Frequency
        layout.addWidget(_body_label("Frequency:"))
        self._frequency = QComboBox()
        self._frequency.addItems(
            [
                "Daily",
                "Twice daily",
                "Weekly",
                "As needed",
            ]
        )
        if med and med.get("frequency"):
            idx = self._frequency.findText(med["frequency"])
            if idx >= 0:
                self._frequency.setCurrentIndex(idx)
        layout.addWidget(self._frequency)

        # Scheduled time
        layout.addWidget(_body_label("Scheduled time:"))
        self._time = QTimeEdit()
        self._time.setDisplayFormat("HH:mm")
        if med and med.get("time"):
            try:
                parts = med["time"].split(":")
                self._time.setTime(QTime(int(parts[0]), int(parts[1])))
            except (ValueError, IndexError):
                self._time.setTime(QTime(8, 0))
        else:
            self._time.setTime(QTime(8, 0))
        layout.addWidget(self._time)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self) -> dict[str, Any]:
        return {
            "name": self._name.text().strip(),
            "dosage": self._dosage.text().strip(),
            "frequency": self._frequency.currentText(),
            "time": self._time.time().toString("HH:mm"),
        }


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------


class MedicationWidget(QWidget):
    """Medication tracking tab with schedule, adherence, and export."""

    medication_taken = pyqtSignal(str)  # med name
    medication_updated = pyqtSignal()

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        self._medication_tracker = None
        with contextlib.suppress(Exception):
            self._medication_tracker = main_window.medication_tracker

        self._medications: list[dict[str, Any]] = []
        self._adherence: dict[str, dict[str, str]] = {}  # date -> {med_name: status}

        self._load_data()
        self._build_ui()
        self._apply_theme()
        self._refresh_all()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def _theme(self) -> dict[str, str]:
        """Live theme color tokens, with safe fallbacks if unavailable."""
        with contextlib.suppress(Exception):
            return self.main_window.theme_manager.get_colors()
        return {}

    def _apply_theme(self) -> None:
        t = self._theme()
        accent = t.get("accent", "#D9A05B")
        text = t.get("text", "#F3F3F4")
        muted = t.get("text_muted", t.get("secondary", "#8E8E93"))
        self._streak_label.setStyleSheet(
            f"QLabel#medRhythmStreak {{ color: {accent}; font-size: 19px; font-weight: 600; }}"
        )
        self._rhythm_note.setStyleSheet(
            f"QLabel#medRhythmNote {{ color: {muted}; font-size: 13px; }}"
        )
        # Disclaimer stays quiet and unalarming, not bolded shouting.
        self._disclaimer.setStyleSheet(f"QLabel {{ color: {muted}; font-style: italic; }}")
        # Keep header tone aligned with the rest of the app.
        self._header.setStyleSheet(f"QLabel {{ color: {text}; }}")

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _data_dir(self) -> Path:
        try:
            base = Path(self.main_window.data_dir)
        except (AttributeError, TypeError):
            base = get_data_dir()
        p = base / "medication"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _load_data(self) -> None:
        dd = self._data_dir()
        meds_file = dd / "medications.json"
        adherence_file = dd / "adherence.json"

        if meds_file.exists():
            try:
                with open(meds_file) as fh:
                    self._medications = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"Medication load error: {exc}")

        if adherence_file.exists():
            try:
                with open(adherence_file) as fh:
                    self._adherence = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"Adherence load error: {exc}")

    def _save_data(self) -> None:
        dd = self._data_dir()
        dd.mkdir(parents=True, exist_ok=True)
        try:
            with open(dd / "medications.json", "w") as fh:
                json.dump(self._medications, fh, indent=2, default=str)
            with open(dd / "adherence.json", "w") as fh:
                json.dump(self._adherence, fh, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save medication data: {e}")

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

        self._header = _section_title("Medication Tracker")
        self._root.addWidget(self._header)

        # Disclaimer -- present, honest, but never the loudest thing on screen.
        self._disclaimer = _body_label(
            "Not medical advice. Talk to your prescriber or pharmacist about any "
            "medication decision. This is just for keeping track."
        )
        self._root.addWidget(self._disclaimer)

        body = QHBoxLayout()
        body.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(12)
        self._build_medication_list(left)
        self._build_today_schedule(left)
        left.addStretch()
        body.addLayout(left, stretch=2)

        right = QVBoxLayout()
        right.setSpacing(12)
        self._build_adherence_section(right)
        right.addStretch()
        body.addLayout(right, stretch=1)

        self._root.addLayout(body)

        # Export
        export_btn = _accent_button("Export for Healthcare Provider")
        export_btn.clicked.connect(self._export_for_doctor)
        self._root.addWidget(export_btn)

        self._root.addStretch()

    # -- medication list ------------------------------------------------

    def _build_medication_list(self, parent: QVBoxLayout) -> None:
        group = QGroupBox("My Medications")
        layout = QVBoxLayout(group)

        self._med_list = QListWidget()
        self._med_list.setMinimumHeight(180)
        layout.addWidget(self._med_list)

        btn_row = QHBoxLayout()
        add_btn = _accent_button("Add")
        add_btn.clicked.connect(self._add_medication)
        btn_row.addWidget(add_btn)

        edit_btn = _accent_button("Edit")
        edit_btn.clicked.connect(self._edit_medication)
        btn_row.addWidget(edit_btn)

        remove_btn = _accent_button("Remove")
        remove_btn.clicked.connect(self._remove_medication)
        btn_row.addWidget(remove_btn)
        layout.addLayout(btn_row)
        parent.addWidget(group)

    # -- today's schedule -----------------------------------------------

    def _build_today_schedule(self, parent: QVBoxLayout) -> None:
        group = QGroupBox("Today's Schedule")
        self._schedule_group = group
        self._schedule_layout = QVBoxLayout(group)
        parent.addWidget(group)

    # -- adherence section -----------------------------------------------

    def _build_adherence_section(self, parent: QVBoxLayout) -> None:
        group = QGroupBox("Your Rhythm")
        self._rhythm_group = group
        layout = QVBoxLayout(group)

        # A big, plain count of steady days in the recent window -- the number
        # that should grow, not a shrinking failure percentage.
        self._streak_label = QLabel("")
        self._streak_label.setObjectName("medRhythmStreak")
        self._streak_label.setWordWrap(True)

        # One forgiving sentence about how the last couple of weeks have gone.
        self._rhythm_note = QLabel("")
        self._rhythm_note.setObjectName("medRhythmNote")
        self._rhythm_note.setWordWrap(True)

        layout.addWidget(self._streak_label)
        layout.addWidget(self._rhythm_note)
        parent.addWidget(group)

    # ------------------------------------------------------------------
    # Data operations
    # ------------------------------------------------------------------

    def _refresh_all(self) -> None:
        self._refresh_med_list()
        self._refresh_schedule()
        self._refresh_adherence()

    def _refresh_med_list(self) -> None:
        self._med_list.clear()
        for med in self._medications:
            name = med.get("name", "?")
            dosage = med.get("dosage", "?")
            freq = med.get("frequency", "?")
            time_str = med.get("time", "?")
            text = f"{name} -- {dosage} -- {freq} @ {time_str}"
            self._med_list.addItem(text)

    def _refresh_schedule(self) -> None:
        # Clear existing schedule widgets
        while self._schedule_layout.count():
            item = self._schedule_layout.takeAt(0)
            if item is None:
                continue
            w = item.widget()
            if w:
                w.deleteLater()
            sub = item.layout()
            if sub:
                while sub.count():
                    child = sub.takeAt(0)
                    if child is None:
                        continue
                    cw = child.widget()
                    if cw:
                        cw.deleteLater()

        today_str = date.today().isoformat()
        today_adherence = self._adherence.get(today_str, {})

        if not self._medications:
            self._schedule_layout.addWidget(_body_label("No medications scheduled."))
            return

        for med in self._medications:
            name = med.get("name", "?")
            dosage = med.get("dosage", "?")
            time_str = med.get("time", "?")
            status = today_adherence.get(name, "pending")

            row = QHBoxLayout()
            cb = QCheckBox(f"{time_str} -- {name} ({dosage})")
            cb.setChecked(status == "taken")
            cb_font = cb.font()
            cb_font.setPointSize(12)
            cb.setFont(cb_font)

            def _on_toggled(checked: bool, med_name: str = name) -> None:
                self._mark_taken(med_name, checked)

            cb.toggled.connect(_on_toggled)
            row.addWidget(cb)

            if status == "taken":
                kept = self._theme().get("success", "#5E9A68")
                taken_label = QLabel("Kept")
                taken_label.setStyleSheet(f"color: {kept}; font-weight: bold;")
                row.addWidget(taken_label)

            row.addStretch()
            self._schedule_layout.addLayout(row)

    def _mark_taken(self, med_name: str, taken: bool) -> None:
        # Checking the box is a deliberate "I took this." Un-checking is almost
        # always an undo or a misclick -- it is NOT a person telling us they
        # skipped a dose. So an untick clears the day back to pending; it never
        # records a "missed" that would feed the crisis miss-streak heuristic a
        # false alarm. A real miss is inferred elsewhere, not by a stray click.
        today_str = date.today().isoformat()
        status = "taken" if taken else "pending"
        if today_str not in self._adherence:
            self._adherence[today_str] = {}
        self._adherence[today_str][med_name] = status
        self._save_data()
        self._sync_status_to_db(med_name, today_str, status)
        if taken:
            self.medication_taken.emit(med_name)
        self._refresh_adherence()

    def _sync_status_to_db(self, med_name: str, day: str, status: str) -> None:
        """Mirror an adherence change into MEDICATION_LOGS (SQLite).

        The widget keeps a JSON model for its own display, but adherence must
        also reach the database so the wellness orchestrator's medication-miss
        crisis heuristic can see it. Best-effort: a DB hiccup must never block
        the user from checking off a dose.
        """
        tracker = self._medication_tracker
        if tracker is None or not hasattr(tracker, "record_status"):
            return
        dosage = ""
        for med in self._medications:
            if med.get("name") == med_name:
                dosage = med.get("dosage", "") or ""
                break
        try:
            tracker.record_status(med_name, day, status, dosage=dosage)
        except Exception as exc:  # noqa: BLE001 - persistence must not crash the UI
            logger.debug("Medication DB sync failed for %s: %s", med_name, exc)

    # Recent window we summarise. Long enough to see a rhythm, short enough
    # that a rough patch from a month ago never haunts the present.
    _RHYTHM_WINDOW_DAYS = 14

    def _recent_window_days(self) -> list[str]:
        """ISO dates for the last RHYTHM_WINDOW_DAYS, oldest first, today last."""
        today = date.today()
        days = [
            (today - timedelta(days=offset)).isoformat()
            for offset in range(self._RHYTHM_WINDOW_DAYS - 1, -1, -1)
        ]
        return days

    def _refresh_adherence(self) -> None:
        # Forgiving, self-healing rhythm over a short recent window. We count
        # the steady days near the present and never surface a lifetime
        # "missed" tally or a shrinking percentage -- a rough patch in the past
        # should not follow someone around. A day only counts as "kept" if a
        # dose was actually marked taken/late that day; days you never opened
        # the app are simply quiet, not failures.
        recent_days = self._recent_window_days()
        kept_days = 0
        current_streak = 0  # consecutive kept days ending today
        streak_open = True
        last_kept_index = -1

        for i, day in enumerate(recent_days):
            day_data = self._adherence.get(day, {})
            if any(s in ("taken", "late") for s in day_data.values()):
                kept_days += 1
                last_kept_index = i

        # Size the live streak by walking back from the most recent day.
        for day in reversed(recent_days):
            day_data = self._adherence.get(day, {})
            if any(s in ("taken", "late") for s in day_data.values()):
                if streak_open:
                    current_streak += 1
            else:
                streak_open = False

        self._streak_label.setText(self._streak_text(current_streak, kept_days))
        self._rhythm_note.setText(
            self._rhythm_note_text(recent_days, kept_days, current_streak, last_kept_index)
        )

    @staticmethod
    def _streak_text(current_streak: int, kept_days: int) -> str:
        if current_streak >= 2:
            return f"{current_streak} steady days in a row."
        if current_streak == 1:
            return "Marked today. That's the one that counts."
        if kept_days > 0:
            return "Today's still open."
        return "Nothing marked yet."

    def _rhythm_note_text(
        self,
        recent_days: list[str],
        kept_days: int,
        current_streak: int,
        last_kept_index: int,
    ) -> str:
        if not self._medications:
            return "Add a medication and the days you keep will show up here."
        if kept_days == 0:
            return "No pressure -- check one off whenever you take it and we'll start counting."

        window = len(recent_days)
        today_idx = window - 1
        yesterday_idx = window - 2

        def _kept(day_index: int) -> bool:
            if day_index < 0:
                return False
            statuses = self._adherence.get(recent_days[day_index], {}).values()
            return any(s in ("taken", "late") for s in statuses)

        today_kept = _kept(today_idx)
        yesterday_kept = _kept(yesterday_idx)

        # A slip yesterday after a good run is the most forgiving thing to name.
        if not yesterday_kept and yesterday_idx >= 0 and current_streak >= 1:
            return f"{kept_days} kept days these two weeks. Yesterday slipped by -- it happens."
        if current_streak >= 5:
            return f"{kept_days} of the last {window} days kept. This rhythm is holding."
        if today_kept and not yesterday_kept:
            return "Back on it today. One day at a time is plenty."
        return f"{kept_days} of the last {window} days kept. Picking it back up is the whole game."

    # -- medication CRUD ------------------------------------------------

    def _add_medication(self) -> None:
        dialog = _MedicationDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                return
            self._medications.append(data)
            self._save_data()
            self.medication_updated.emit()
            self._refresh_all()

    def _edit_medication(self) -> None:
        row = self._med_list.currentRow()
        if row < 0 or row >= len(self._medications):
            QMessageBox.information(self, "Edit", "Select a medication first.")
            return
        med = self._medications[row]
        dialog = _MedicationDialog(med=med, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self._medications[row] = data
            self._save_data()
            self.medication_updated.emit()
            self._refresh_all()

    def _remove_medication(self) -> None:
        row = self._med_list.currentRow()
        if row < 0 or row >= len(self._medications):
            QMessageBox.information(self, "Remove", "Select a medication first.")
            return
        name = self._medications[row].get("name", "")
        reply = QMessageBox.question(
            self,
            "Remove",
            f"Remove '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._medications.pop(row)
            self._save_data()
            self.medication_updated.emit()
            self._refresh_all()

    # -- export ---------------------------------------------------------

    def _export_for_doctor(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Medication Report", "medication_report.json", "JSON (*.json)"
        )
        if not path:
            return

        # Compute adherence per medication
        adherence_summary: dict[str, Any] = {}
        for med in self._medications:
            name = med.get("name", "?")
            med_total = 0
            med_taken = 0
            for day_data in self._adherence.values():
                if name in day_data:
                    med_total += 1
                    if day_data[name] == "taken":
                        med_taken += 1
            rate = round(med_taken / med_total * 100, 1) if med_total > 0 else 0
            adherence_summary[name] = {
                "total_days_tracked": med_total,
                "days_taken": med_taken,
                "adherence_rate": rate,
            }

        report = {
            "exported_at": datetime.now().isoformat(),
            "medications": self._medications,
            "adherence_summary": adherence_summary,
        }
        try:
            with open(path, "w") as fh:
                json.dump(report, fh, indent=2, default=str)
            QMessageBox.information(self, "Exported", f"Report saved to {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Export failed: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Called by main window on close."""
        self._save_data()
