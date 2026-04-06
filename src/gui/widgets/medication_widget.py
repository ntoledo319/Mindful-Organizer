"""
Medication tracking widget -- schedule, adherence, side effects, and export.

Provides a medication list, daily schedule with check-off, adherence calendar,
side effect logging, refill reminders, and doctor-ready export functionality.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QListWidget, QListWidgetItem,
    QLineEdit, QSpinBox, QComboBox, QTextEdit, QTimeEdit,
    QCheckBox, QDialog, QDialogButtonBox, QGroupBox,
    QMessageBox, QFileDialog, QGridLayout,
)
from PyQt6.QtCore import Qt, QTime, pyqtSignal
from PyQt6.QtGui import QFont, QColor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _card_frame(theme: Dict[str, str]) -> QFrame:
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
    label.setStyleSheet(f"color: {theme.get('text', '#333')}; padding-bottom: 4px;")
    return label


def _body_label(text: str, theme: Dict[str, str]) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {theme.get('text', '#555')};")
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


# ---------------------------------------------------------------------------
# Add/Edit medication dialog
# ---------------------------------------------------------------------------

class _MedicationDialog(QDialog):
    """Dialog for adding or editing a medication."""

    def __init__(
        self,
        theme: Dict[str, str],
        med: Optional[Dict[str, Any]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Medication" if not med else f"Edit: {med.get('name', '')}")
        self.setMinimumWidth(450)
        self._theme = theme

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Name
        layout.addWidget(_body_label("Medication name:", theme))
        self._name = QLineEdit(med.get("name", "") if med else "")
        self._name.setPlaceholderText("e.g. Sertraline")
        layout.addWidget(self._name)

        # Dosage
        layout.addWidget(_body_label("Dosage:", theme))
        self._dosage = QLineEdit(med.get("dosage", "") if med else "")
        self._dosage.setPlaceholderText("e.g. 50mg")
        layout.addWidget(self._dosage)

        # Frequency
        layout.addWidget(_body_label("Frequency:", theme))
        self._frequency = QComboBox()
        self._frequency.addItems([
            "Once daily", "Twice daily", "Three times daily",
            "Every other day", "Weekly", "As needed",
        ])
        if med and med.get("frequency"):
            idx = self._frequency.findText(med["frequency"])
            if idx >= 0:
                self._frequency.setCurrentIndex(idx)
        layout.addWidget(self._frequency)

        # Time
        layout.addWidget(_body_label("Time(s) to take:", theme))
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

        # Refill date
        layout.addWidget(_body_label("Refill reminder days before:", theme))
        self._refill_days = QSpinBox()
        self._refill_days.setRange(0, 30)
        self._refill_days.setValue(med.get("refill_days", 7) if med else 7)
        layout.addWidget(self._refill_days)

        # Notes
        layout.addWidget(_body_label("Notes:", theme))
        self._notes = QTextEdit()
        self._notes.setMaximumHeight(80)
        self._notes.setPlainText(med.get("notes", "") if med else "")
        layout.addWidget(self._notes)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self) -> Dict[str, Any]:
        return {
            "name": self._name.text().strip(),
            "dosage": self._dosage.text().strip(),
            "frequency": self._frequency.currentText(),
            "time": self._time.time().toString("HH:mm"),
            "refill_days": self._refill_days.value(),
            "notes": self._notes.toPlainText().strip(),
        }


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

class MedicationWidget(QWidget):
    """Medication tracking tab with schedule, adherence, and export."""

    medication_taken = pyqtSignal(str)  # med name
    medication_updated = pyqtSignal()

    def __init__(
        self,
        theme: Dict[str, str],
        medication_manager: Any = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._medication_manager = medication_manager

        self._medications: List[Dict[str, Any]] = []
        self._adherence: Dict[str, Dict[str, str]] = {}  # date -> {med_name: status}
        self._side_effects: List[Dict[str, Any]] = []

        self._load_data()
        self._build_ui()
        self._refresh_all()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _data_dir(self) -> Path:
        if self._medication_manager and hasattr(self._medication_manager, "data_dir"):
            return Path(self._medication_manager.data_dir)
        p = Path.home() / ".mindful_optimizer" / "medication"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _load_data(self) -> None:
        dd = self._data_dir()
        meds_file = dd / "medications.json"
        adherence_file = dd / "adherence.json"
        side_effects_file = dd / "side_effects.json"

        for fpath, attr in [
            (meds_file, "_medications"),
            (adherence_file, "_adherence"),
            (side_effects_file, "_side_effects"),
        ]:
            if fpath.exists():
                try:
                    with open(fpath) as fh:
                        setattr(self, attr, json.load(fh))
                except Exception:
                    pass

    def _save_data(self) -> None:
        dd = self._data_dir()
        dd.mkdir(parents=True, exist_ok=True)
        try:
            with open(dd / "medications.json", "w") as fh:
                json.dump(self._medications, fh, indent=2, default=str)
            with open(dd / "adherence.json", "w") as fh:
                json.dump(self._adherence, fh, indent=2, default=str)
            with open(dd / "side_effects.json", "w") as fh:
                json.dump(self._side_effects, fh, indent=2, default=str)
        except Exception:
            pass

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

        self._root.addWidget(_section_title("Medication Tracker", self._theme))

        # Disclaimer
        disclaimer = _body_label(
            "Not medical advice -- consult your healthcare provider for all "
            "medication decisions. This tool is for personal tracking only.",
            self._theme,
        )
        disclaimer.setStyleSheet(
            f"color: {self._theme.get('warning', '#e67e22')}; "
            "font-style: italic; font-weight: bold; padding: 8px;"
        )
        self._root.addWidget(disclaimer)

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
        self._build_adherence_calendar(right)
        self._build_side_effects(right)
        self._build_refill_reminders(right)
        right.addStretch()
        body.addLayout(right, stretch=3)

        self._root.addLayout(body)

        # Export
        export_btn = _accent_button("Export for Doctor", self._theme)
        export_btn.clicked.connect(self._export_for_doctor)
        self._root.addWidget(export_btn)

        self._root.addStretch()

    # -- medication list ------------------------------------------------

    def _build_medication_list(self, parent: QVBoxLayout) -> None:
        card = _card_frame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(_section_title("My Medications", self._theme))

        self._med_list = QListWidget()
        self._med_list.setMinimumHeight(200)
        self._med_list.setStyleSheet(
            f"QListWidget {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; }}"
            f"QListWidget::item {{ padding: 8px; }}"
            f"QListWidget::item:selected {{ background-color: {self._theme.get('accent', '#4a90d9')}; color: #fff; }}"
        )
        layout.addWidget(self._med_list)

        btn_row = QHBoxLayout()
        add_btn = _accent_button("Add", self._theme)
        add_btn.clicked.connect(self._add_medication)
        btn_row.addWidget(add_btn)

        edit_btn = _accent_button("Edit", self._theme)
        edit_btn.clicked.connect(self._edit_medication)
        btn_row.addWidget(edit_btn)

        remove_btn = _accent_button("Remove", self._theme)
        remove_btn.setStyleSheet(
            remove_btn.styleSheet().replace(
                self._theme.get("accent", "#4a90d9"),
                self._theme.get("danger", "#e74c3c"),
            )
        )
        remove_btn.clicked.connect(self._remove_medication)
        btn_row.addWidget(remove_btn)
        layout.addLayout(btn_row)
        parent.addWidget(card)

    # -- today's schedule -----------------------------------------------

    def _build_today_schedule(self, parent: QVBoxLayout) -> None:
        card = _card_frame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(_section_title("Today's Schedule", self._theme))

        self._schedule_layout = QVBoxLayout()
        layout.addLayout(self._schedule_layout)
        parent.addWidget(card)

    # -- adherence calendar ---------------------------------------------

    def _build_adherence_calendar(self, parent: QVBoxLayout) -> None:
        card = _card_frame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(_section_title("Adherence Calendar (Last 30 Days)", self._theme))

        self._adherence_grid = QGridLayout()
        self._adherence_grid.setSpacing(4)
        layout.addLayout(self._adherence_grid)
        parent.addWidget(card)

    # -- side effects ---------------------------------------------------

    def _build_side_effects(self, parent: QVBoxLayout) -> None:
        card = _card_frame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(_section_title("Side Effect Log", self._theme))

        self._side_effect_list = QListWidget()
        self._side_effect_list.setMaximumHeight(150)
        self._side_effect_list.setStyleSheet(
            f"QListWidget {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; }}"
        )
        layout.addWidget(self._side_effect_list)

        log_row = QHBoxLayout()
        self._side_effect_input = QLineEdit()
        self._side_effect_input.setPlaceholderText("Describe side effect...")
        self._side_effect_input.setStyleSheet(
            f"QLineEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; padding: 6px; }}"
        )
        log_row.addWidget(self._side_effect_input)

        self._side_effect_med = QComboBox()
        log_row.addWidget(self._side_effect_med)

        log_btn = _accent_button("Log", self._theme)
        log_btn.clicked.connect(self._log_side_effect)
        log_row.addWidget(log_btn)
        layout.addLayout(log_row)
        parent.addWidget(card)

    # -- refill reminders -----------------------------------------------

    def _build_refill_reminders(self, parent: QVBoxLayout) -> None:
        card = _card_frame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(_section_title("Refill Reminders", self._theme))
        self._refill_label = _body_label("No refill reminders set.", self._theme)
        layout.addWidget(self._refill_label)
        parent.addWidget(card)

    # ------------------------------------------------------------------
    # Data operations
    # ------------------------------------------------------------------

    def _refresh_all(self) -> None:
        self._refresh_med_list()
        self._refresh_schedule()
        self._refresh_adherence_calendar()
        self._refresh_side_effects()
        self._refresh_refill_reminders()

    def _refresh_med_list(self) -> None:
        self._med_list.clear()
        self._side_effect_med.clear()
        for med in self._medications:
            name = med.get("name", "?")
            dosage = med.get("dosage", "?")
            freq = med.get("frequency", "?")
            time_str = med.get("time", "?")
            text = f"{name} -- {dosage} -- {freq} @ {time_str}"
            self._med_list.addItem(text)
            self._side_effect_med.addItem(name)

    def _refresh_schedule(self) -> None:
        # Clear existing
        while self._schedule_layout.count():
            item = self._schedule_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        today_str = date.today().isoformat()
        today_adherence = self._adherence.get(today_str, {})

        if not self._medications:
            self._schedule_layout.addWidget(
                _body_label("No medications scheduled.", self._theme)
            )
            return

        for med in self._medications:
            name = med.get("name", "?")
            dosage = med.get("dosage", "?")
            time_str = med.get("time", "?")
            status = today_adherence.get(name, "pending")

            row = QHBoxLayout()
            cb = QCheckBox(f"{time_str} -- {name} ({dosage})")
            cb.setChecked(status == "taken")
            cb.setStyleSheet(f"color: {self._theme.get('text', '#333')}; font-size: 13px;")

            def _on_toggled(checked: bool, med_name: str = name) -> None:
                self._mark_taken(med_name, checked)

            cb.toggled.connect(_on_toggled)
            row.addWidget(cb)

            if status == "taken":
                taken_label = QLabel("Taken")
                taken_label.setStyleSheet(
                    f"color: {self._theme.get('success', '#27ae60')}; font-weight: bold;"
                )
                row.addWidget(taken_label)

            row.addStretch()
            self._schedule_layout.addLayout(row)

    def _mark_taken(self, med_name: str, taken: bool) -> None:
        today_str = date.today().isoformat()
        if today_str not in self._adherence:
            self._adherence[today_str] = {}
        self._adherence[today_str][med_name] = "taken" if taken else "missed"
        self._save_data()
        self.medication_taken.emit(med_name)
        self._refresh_adherence_calendar()

    def _refresh_adherence_calendar(self) -> None:
        # Clear grid
        while self._adherence_grid.count():
            item = self._adherence_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        today = date.today()
        med_names = [m.get("name", "?") for m in self._medications]

        if not med_names:
            return

        # Header row
        self._adherence_grid.addWidget(_body_label("Date", self._theme), 0, 0)
        for col, name in enumerate(med_names, start=1):
            lbl = _body_label(name[:10], self._theme)
            lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self._adherence_grid.addWidget(lbl, 0, col)

        # Last 30 days
        for i in range(min(30, 15)):  # Show 15 rows to keep compact
            d = today - timedelta(days=i)
            d_str = d.isoformat()
            day_data = self._adherence.get(d_str, {})

            date_label = _body_label(d.strftime("%m/%d"), self._theme)
            date_label.setFont(QFont("Segoe UI", 9))
            self._adherence_grid.addWidget(date_label, i + 1, 0)

            for col, name in enumerate(med_names, start=1):
                status = day_data.get(name, "")
                cell = QLabel()
                cell.setFixedSize(24, 24)
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                if status == "taken":
                    cell.setStyleSheet(
                        f"background-color: {self._theme.get('success', '#27ae60')}; "
                        "border-radius: 12px;"
                    )
                    cell.setToolTip("Taken")
                elif status == "missed":
                    cell.setStyleSheet(
                        f"background-color: {self._theme.get('danger', '#e74c3c')}; "
                        "border-radius: 12px;"
                    )
                    cell.setToolTip("Missed")
                elif status == "late":
                    cell.setStyleSheet(
                        f"background-color: {self._theme.get('warning', '#f39c12')}; "
                        "border-radius: 12px;"
                    )
                    cell.setToolTip("Late")
                else:
                    cell.setStyleSheet(
                        f"background-color: {self._theme.get('secondary', '#ddd')}; "
                        "border-radius: 12px;"
                    )
                    cell.setToolTip("No record")
                self._adherence_grid.addWidget(cell, i + 1, col)

    def _refresh_side_effects(self) -> None:
        self._side_effect_list.clear()
        for se in reversed(self._side_effects[-30:]):
            dt = se.get("date", "?")
            med = se.get("medication", "?")
            effect = se.get("effect", "?")
            self._side_effect_list.addItem(f"{dt} | {med} | {effect}")

    def _refresh_refill_reminders(self) -> None:
        reminders: List[str] = []
        for med in self._medications:
            refill_days = med.get("refill_days", 0)
            if refill_days > 0:
                reminders.append(
                    f"{med.get('name', '?')}: refill reminder {refill_days} days before running out"
                )
        self._refill_label.setText(
            "\n".join(reminders) if reminders else "No refill reminders set."
        )

    # -- medication CRUD ------------------------------------------------

    def _add_medication(self) -> None:
        dialog = _MedicationDialog(self._theme, parent=self)
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
        dialog = _MedicationDialog(self._theme, med=med, parent=self)
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
            self, "Remove",
            f"Remove '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._medications.pop(row)
            self._save_data()
            self.medication_updated.emit()
            self._refresh_all()

    # -- side effects ---------------------------------------------------

    def _log_side_effect(self) -> None:
        effect = self._side_effect_input.text().strip()
        if not effect:
            return
        med = self._side_effect_med.currentText()
        entry = {
            "date": date.today().isoformat(),
            "timestamp": datetime.now().isoformat(),
            "medication": med,
            "effect": effect,
        }
        self._side_effects.append(entry)
        self._side_effect_input.clear()
        self._save_data()
        self._refresh_side_effects()

    # -- export ---------------------------------------------------------

    def _export_for_doctor(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Medication Report",
            "medication_report.json", "JSON (*.json)"
        )
        if not path:
            return
        report = {
            "exported_at": datetime.now().isoformat(),
            "medications": self._medications,
            "adherence_summary": self._compute_adherence_summary(),
            "side_effects": self._side_effects,
        }
        try:
            with open(path, "w") as fh:
                json.dump(report, fh, indent=2, default=str)
            QMessageBox.information(self, "Exported", f"Report saved to {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Export failed: {exc}")

    def _compute_adherence_summary(self) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        for med in self._medications:
            name = med.get("name", "?")
            total = 0
            taken = 0
            for day_data in self._adherence.values():
                if name in day_data:
                    total += 1
                    if day_data[name] == "taken":
                        taken += 1
            rate = round(taken / total * 100, 1) if total > 0 else 0
            summary[name] = {
                "total_days_tracked": total,
                "days_taken": taken,
                "adherence_rate": rate,
            }
        return summary

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, theme: Dict[str, str]) -> None:
        self._theme = theme
