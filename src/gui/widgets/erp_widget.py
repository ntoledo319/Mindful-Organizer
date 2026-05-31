"""
ERP (Exposure and Response Prevention) widget for OCD management.

Provides anxiety hierarchy management, guided exposure sessions with
timed SUDS tracking, habituation monitoring, response prevention logging,
and therapist-shareable report export.
"""

from __future__ import annotations

import contextlib
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _card_frame() -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return frame


def _section_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
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
# Add/Edit hierarchy item dialog
# ---------------------------------------------------------------------------

class _HierarchyItemDialog(QDialog):
    def __init__(
        self,
        title: str = "", suds: int = 50,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Hierarchy Item")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.addWidget(_body_label("Exposure situation:"))
        self._title_edit = QLineEdit(title)
        self._title_edit.setPlaceholderText("Describe the exposure...")
        layout.addWidget(self._title_edit)

        layout.addWidget(_body_label("Predicted SUDS (0-100):"))
        self._suds_spin = QSpinBox()
        self._suds_spin.setRange(0, 100)
        self._suds_spin.setValue(suds)
        layout.addWidget(self._suds_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self) -> dict[str, Any]:
        return {
            "title": self._title_edit.text().strip(),
            "predicted_suds": self._suds_spin.value(),
        }


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

class ERPWidget(QWidget):
    """ERP (Exposure and Response Prevention) tab for OCD management."""

    session_completed = pyqtSignal(dict)

    _SUDS_CHECK_INTERVAL_MS = 5 * 60 * 1000

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        # Try to get ERP manager
        self._erp_manager = None
        with contextlib.suppress(Exception):
            self._erp_manager = main_window.erp_tracker

        # Data
        self._hierarchy: list[dict[str, Any]] = []
        self._sessions: list[dict[str, Any]] = []
        self._active_session: dict[str, Any] | None = None
        self._session_suds: list[dict[str, Any]] = []
        self._session_urges: list[dict[str, Any]] = []

        # Timers
        self._exposure_timer = QTimer(self)
        self._exposure_timer.setInterval(1000)
        self._exposure_timer.timeout.connect(self._tick_exposure)
        self._exposure_elapsed_sec: int = 0

        self._suds_prompt_timer = QTimer(self)
        self._suds_prompt_timer.setInterval(self._SUDS_CHECK_INTERVAL_MS)
        self._suds_prompt_timer.timeout.connect(self._prompt_suds)

        self._load_data()
        self._build_ui()
        self._refresh_hierarchy_list()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _data_dir(self) -> Path:
        try:
            base = Path(self.main_window.data_dir)
        except (AttributeError, TypeError):
            base = get_data_dir()
        p = base / "erp"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _load_data(self) -> None:
        hfile = self._data_dir() / "hierarchy.json"
        sfile = self._data_dir() / "erp_sessions.json"
        if hfile.exists():
            try:
                with open(hfile) as fh:
                    self._hierarchy = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"ERP hierarchy load error: {exc}")
        if sfile.exists():
            try:
                with open(sfile) as fh:
                    self._sessions = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"ERP sessions load error: {exc}")

    def _save_data(self) -> None:
        dd = self._data_dir()
        dd.mkdir(parents=True, exist_ok=True)
        try:
            with open(dd / "hierarchy.json", "w") as fh:
                json.dump(self._hierarchy, fh, indent=2, default=str)
            with open(dd / "erp_sessions.json", "w") as fh:
                json.dump(self._sessions, fh, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save ERP data: {e}")

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

        self._root.addWidget(_section_title("Exposure and Response Prevention"))

        # Disclaimer
        disclaimer = _body_label(
            "ERP should be done under the guidance of a licensed therapist. "
            "This tool is for tracking and support, not a substitute for professional support."
        )
        disclaimer.setStyleSheet("font-style: italic;")
        self._root.addWidget(disclaimer)

        body = QHBoxLayout()
        body.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(12)
        self._build_hierarchy_section(left)
        self._build_session_history(left)
        left.addStretch()
        body.addLayout(left, stretch=2)

        right = QVBoxLayout()
        right.setSpacing(12)
        self._build_exposure_panel(right)
        self._build_progress_summary(right)
        right.addStretch()
        body.addLayout(right, stretch=3)

        self._root.addLayout(body)

        # Export
        export_btn = _accent_button("Export Report for Therapist")
        export_btn.clicked.connect(self._export_report)
        self._root.addWidget(export_btn)

        self._root.addStretch()

    # -- hierarchy section ----------------------------------------------

    def _build_hierarchy_section(self, parent: QVBoxLayout) -> None:
        card = _card_frame()
        layout = QVBoxLayout(card)
        layout.addWidget(_section_title("Anxiety Hierarchy"))

        self._hierarchy_list = QListWidget()
        self._hierarchy_list.setMinimumHeight(250)
        layout.addWidget(self._hierarchy_list)

        btn_row = QHBoxLayout()
        for label, slot in [
            ("Add Item", self._add_hierarchy_item),
            ("Edit Item", self._edit_hierarchy_item),
            ("Remove Item", self._remove_hierarchy_item),
        ]:
            btn = _accent_button(label)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        start_btn = _accent_button("Start Exposure")
        start_btn.clicked.connect(self._start_exposure)
        layout.addWidget(start_btn)

        parent.addWidget(card)

    # -- exposure panel -------------------------------------------------

    def _build_exposure_panel(self, parent: QVBoxLayout) -> None:
        card = _card_frame()
        layout = QVBoxLayout(card)
        layout.addWidget(_section_title("Active Exposure Session"))

        self._exposure_title_label = _body_label("No active session")
        self._exposure_title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(self._exposure_title_label)

        # Timer
        self._timer_label = QLabel("00:00:00")
        self._timer_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._timer_label)

        # SUDS row
        suds_row = QHBoxLayout()
        suds_row.addWidget(_body_label("Predicted SUDS:"))
        self._predicted_suds_label = _body_label("--")
        suds_row.addWidget(self._predicted_suds_label)
        suds_row.addWidget(_body_label("Current SUDS:"))
        self._current_suds_spin = QSpinBox()
        self._current_suds_spin.setRange(0, 100)
        self._current_suds_spin.setValue(0)
        suds_row.addWidget(self._current_suds_spin)
        record_suds_btn = _accent_button("Record SUDS")
        record_suds_btn.clicked.connect(self._record_suds)
        suds_row.addWidget(record_suds_btn)
        layout.addLayout(suds_row)

        # SUDS log
        self._suds_log_list = QListWidget()
        self._suds_log_list.setMaximumHeight(120)
        layout.addWidget(self._suds_log_list)

        # Compulsion urge tracking
        urge_row = QHBoxLayout()
        urge_row.addWidget(_body_label("Compulsion urge (0-100):"))
        self._urge_spin = QSpinBox()
        self._urge_spin.setRange(0, 100)
        urge_row.addWidget(self._urge_spin)
        record_urge_btn = _accent_button("Log Urge")
        record_urge_btn.clicked.connect(self._record_urge)
        urge_row.addWidget(record_urge_btn)
        layout.addLayout(urge_row)

        # Response prevention notes
        layout.addWidget(_body_label("Response Prevention Notes:"))
        self._rp_notes = QTextEdit()
        self._rp_notes.setMaximumHeight(80)
        self._rp_notes.setPlaceholderText("Urges resisted, safety behaviors avoided...")
        layout.addWidget(self._rp_notes)

        # End session
        self._end_btn = _accent_button("End Session")
        self._end_btn.setEnabled(False)
        self._end_btn.clicked.connect(self._end_exposure)
        layout.addWidget(self._end_btn)

        parent.addWidget(card)

    # -- session history ------------------------------------------------

    def _build_session_history(self, parent: QVBoxLayout) -> None:
        card = _card_frame()
        layout = QVBoxLayout(card)
        layout.addWidget(_section_title("Session History"))

        self._session_history_list = QListWidget()
        self._session_history_list.setMaximumHeight(200)
        layout.addWidget(self._session_history_list)
        parent.addWidget(card)

    # -- progress summary -----------------------------------------------

    def _build_progress_summary(self, parent: QVBoxLayout) -> None:
        card = _card_frame()
        layout = QVBoxLayout(card)
        layout.addWidget(_section_title("Progress Summary"))

        self._total_sessions_label = _body_label("Total sessions: 0")
        self._total_urges_resisted = _body_label("Urges resisted: 0")
        self._avg_suds_drop = _body_label("Avg SUDS drop per session: --")
        self._safety_behaviors_label = _body_label("Sessions with RP notes: 0")

        for w in (self._total_sessions_label, self._total_urges_resisted,
                  self._avg_suds_drop, self._safety_behaviors_label):
            layout.addWidget(w)
        parent.addWidget(card)

    # ------------------------------------------------------------------
    # Hierarchy management
    # ------------------------------------------------------------------

    def _refresh_hierarchy_list(self) -> None:
        self._hierarchy_list.clear()
        sorted_h = sorted(self._hierarchy, key=lambda h: h.get("predicted_suds", 0))
        for item in sorted_h:
            title = item.get("title", "Untitled")
            suds = item.get("predicted_suds", 0)
            sessions = len([
                s for s in self._sessions
                if s.get("hierarchy_id") == item.get("id")
            ])
            text = f"SUDS {suds:3d}  |  {title}  ({sessions} sessions)"
            self._hierarchy_list.addItem(text)
        self._refresh_session_history()
        self._refresh_progress()

    def _add_hierarchy_item(self) -> None:
        dialog = _HierarchyItemDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["title"]:
                return
            data["id"] = uuid.uuid4().hex[:12]
            data["created_at"] = datetime.now().isoformat()
            self._hierarchy.append(data)
            self._save_data()
            self._refresh_hierarchy_list()

    def _edit_hierarchy_item(self) -> None:
        row = self._hierarchy_list.currentRow()
        sorted_h = sorted(self._hierarchy, key=lambda h: h.get("predicted_suds", 0))
        if row < 0 or row >= len(sorted_h):
            QMessageBox.information(self, "Edit", "Select an item first.")
            return
        item = sorted_h[row]
        dialog = _HierarchyItemDialog(
            title=item.get("title", ""),
            suds=item.get("predicted_suds", 50),
            parent=self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            item["title"] = data["title"]
            item["predicted_suds"] = data["predicted_suds"]
            self._save_data()
            self._refresh_hierarchy_list()

    def _remove_hierarchy_item(self) -> None:
        row = self._hierarchy_list.currentRow()
        sorted_h = sorted(self._hierarchy, key=lambda h: h.get("predicted_suds", 0))
        if row < 0 or row >= len(sorted_h):
            QMessageBox.information(self, "Remove", "Select an item first.")
            return
        item = sorted_h[row]
        reply = QMessageBox.question(
            self, "Remove",
            f"Remove '{item.get('title', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._hierarchy = [h for h in self._hierarchy if h.get("id") != item.get("id")]
            self._save_data()
            self._refresh_hierarchy_list()

    # ------------------------------------------------------------------
    # Exposure session
    # ------------------------------------------------------------------

    def _start_exposure(self) -> None:
        if self._active_session:
            QMessageBox.information(self, "Active", "End the current session first.")
            return
        row = self._hierarchy_list.currentRow()
        sorted_h = sorted(self._hierarchy, key=lambda h: h.get("predicted_suds", 0))
        if row < 0 or row >= len(sorted_h):
            QMessageBox.information(self, "Start", "Select a hierarchy item first.")
            return

        item = sorted_h[row]
        self._active_session = {
            "id": uuid.uuid4().hex[:12],
            "hierarchy_id": item.get("id"),
            "hierarchy_title": item.get("title"),
            "predicted_suds": item.get("predicted_suds", 0),
            "started_at": datetime.now().isoformat(),
            "suds_log": [],
            "urge_log": [],
            "rp_notes": "",
        }
        self._session_suds.clear()
        self._session_urges.clear()
        self._suds_log_list.clear()
        self._rp_notes.clear()

        self._exposure_title_label.setText(f"Exposure: {item.get('title', '')}")
        self._predicted_suds_label.setText(str(item.get("predicted_suds", 0)))
        self._exposure_elapsed_sec = 0
        self._timer_label.setText("00:00:00")

        self._end_btn.setEnabled(True)
        self._exposure_timer.start()
        self._suds_prompt_timer.start()

    def _tick_exposure(self) -> None:
        self._exposure_elapsed_sec += 1
        h = self._exposure_elapsed_sec // 3600
        m = (self._exposure_elapsed_sec % 3600) // 60
        s = self._exposure_elapsed_sec % 60
        self._timer_label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def _prompt_suds(self) -> None:
        QMessageBox.information(
            self, "SUDS Check",
            "Time for a SUDS check. Rate your current anxiety level (0-100) "
            "and click Record SUDS.",
        )

    def _record_suds(self) -> None:
        if not self._active_session:
            return
        suds_val = self._current_suds_spin.value()
        entry = {
            "time": datetime.now().isoformat(),
            "elapsed_sec": self._exposure_elapsed_sec,
            "suds": suds_val,
        }
        self._session_suds.append(entry)
        elapsed_min = self._exposure_elapsed_sec // 60
        self._suds_log_list.addItem(f"{elapsed_min}m: SUDS {suds_val}")

    def _record_urge(self) -> None:
        if not self._active_session:
            return
        urge_val = self._urge_spin.value()
        entry = {
            "time": datetime.now().isoformat(),
            "elapsed_sec": self._exposure_elapsed_sec,
            "urge_strength": urge_val,
            "resisted": True,
        }
        self._session_urges.append(entry)

    def _end_exposure(self) -> None:
        if not self._active_session:
            return

        self._exposure_timer.stop()
        self._suds_prompt_timer.stop()

        self._active_session["ended_at"] = datetime.now().isoformat()
        self._active_session["duration_sec"] = self._exposure_elapsed_sec
        self._active_session["suds_log"] = list(self._session_suds)
        self._active_session["urge_log"] = list(self._session_urges)
        self._active_session["rp_notes"] = self._rp_notes.toPlainText().strip()
        self._active_session["urges_resisted"] = len(self._session_urges)

        if self._session_suds:
            self._active_session["peak_suds"] = max(s["suds"] for s in self._session_suds)
            self._active_session["final_suds"] = self._session_suds[-1]["suds"]
        else:
            self._active_session["peak_suds"] = 0
            self._active_session["final_suds"] = 0

        self._sessions.append(self._active_session)
        self.session_completed.emit(self._active_session)

        self._active_session = None
        self._end_btn.setEnabled(False)
        self._exposure_title_label.setText("Session complete")
        self._timer_label.setText("00:00:00")

        self._save_data()
        self._refresh_hierarchy_list()

    # ------------------------------------------------------------------
    # History & progress
    # ------------------------------------------------------------------

    def _refresh_session_history(self) -> None:
        self._session_history_list.clear()
        for s in reversed(self._sessions[-50:]):
            dt = s.get("started_at", "?")[:16]
            title = s.get("hierarchy_title", "?")
            peak = s.get("peak_suds", "?")
            final = s.get("final_suds", "?")
            text = f"{dt}  |  {title}  |  Peak: {peak}, Final: {final}"
            self._session_history_list.addItem(text)

    def _refresh_progress(self) -> None:
        total = len(self._sessions)
        self._total_sessions_label.setText(f"Total sessions: {total}")

        urges = sum(s.get("urges_resisted", 0) for s in self._sessions)
        self._total_urges_resisted.setText(f"Urges resisted: {urges}")

        drops: list[int] = []
        for s in self._sessions:
            predicted = s.get("predicted_suds", 0)
            final = s.get("final_suds")
            if final is not None:
                drops.append(predicted - final)
        if drops:
            avg_drop = sum(drops) / len(drops)
            self._avg_suds_drop.setText(f"Avg SUDS drop per session: {avg_drop:.1f}")
        else:
            self._avg_suds_drop.setText("Avg SUDS drop per session: --")

        rp_count = sum(1 for s in self._sessions if s.get("rp_notes"))
        self._safety_behaviors_label.setText(f"Sessions with RP notes: {rp_count}")

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _export_report(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export ERP Report", "erp_report.json", "JSON (*.json)"
        )
        if not path:
            return
        report = {
            "exported_at": datetime.now().isoformat(),
            "hierarchy": self._hierarchy,
            "sessions": self._sessions,
            "summary": {
                "total_sessions": len(self._sessions),
                "total_urges_resisted": sum(
                    s.get("urges_resisted", 0) for s in self._sessions
                ),
            },
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
