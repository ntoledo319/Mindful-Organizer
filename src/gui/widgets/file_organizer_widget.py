"""Condition-aware file organizer widget.

Adapts organization strategy, UI density, and messaging to the user's
profile conditions (ADHD, OCD, Depression, Anxiety, Generic).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.components import AccentButton, BodyLabel, CardFrame, SectionTitle

logger = logging.getLogger(__name__)


_CONDITION_CONFIGS: dict[str, dict[str, Any]] = {
    "ADHD": {
        "folder_names": [
            "🚀 DO NOW — Urgent",
            "📥 DO LATER — This Week",
            "✅ DONE — Completed",
            "📌 REFERENCE — Keep Handy",
        ],
        "tips": [
            "Use the 'DO NOW' folder for anything that needs action today.",
            "Batch similar tasks together before organizing.",
            "Set a 10-minute timer for cleanup sessions.",
            "Visual cues (emojis) make folders easier to spot.",
        ],
        "button_style": "emoji_heavy",
        "density": "low",
    },
    "OCD": {
        "folder_names": [
            "01_Current",
            "02_Review",
            "03_Archive",
            "04_Scratch",
        ],
        "tips": [
            "Numbered folders provide clear, predictable order.",
            "'Scratch' is a safe place for temporary files — they don't need to be perfect.",
            "One folder level deep keeps things manageable.",
            "If you feel stuck, the dry-run button lets you preview everything first.",
        ],
        "button_style": "minimal",
        "density": "low",
    },
    "Depression": {
        "folder_names": [
            "Gentle — Low Effort",
            "Steady — Medium Effort",
            "Strong — High Effort",
            "Rest — No Action Needed",
        ],
        "tips": [
            "Start with the 'Rest' folder — not everything needs action.",
            "Even organizing one file is a win. Small steps count.",
            "Use dry-run first if energy is low — no pressure.",
            "The organizer remembers your undo history so you can reverse anything.",
        ],
        "button_style": "soft",
        "density": "ultra_low",
    },
    "Anxiety": {
        "folder_names": [
            "01_Current_Projects",
            "02_Resources",
            "03_Archives",
            "04_Templates",
            "05_Documentation",
            "06_Backups",
        ],
        "tips": [
            "Detailed categories reduce uncertainty about where things belong.",
            "The dry-run preview shows exactly what will happen before any files move.",
            "Duplicates are found safely — nothing is deleted automatically.",
            "Everything is reversible with the Undo button.",
        ],
        "button_style": "clear",
        "density": "medium",
    },
    "Generic": {
        "folder_names": [
            "Quick Access",
            "Projects",
            "Resources",
            "Archives",
        ],
        "tips": [
            "Drag files into the organizer or select a folder to scan.",
            "Dry-run lets you preview changes before committing.",
            "Custom rules can handle special file types automatically.",
        ],
        "button_style": "default",
        "density": "medium",
    },
}


def _primary_condition(conditions: set[Any]) -> str:
    """Pick the dominant condition for file organizer behavior."""
    order = ["ADHD", "OCD", "Depression", "Anxiety"]
    for cond in order:
        if any(str(c).upper() == cond.upper() for c in conditions):
            return cond
    return "Generic"


class FileOrganizerWidget(QWidget):
    """File organizer with condition-aware UI and strategies."""

    def __init__(
        self,
        theme: dict[str, str],
        file_organizer: Any = None,
        profile_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._organizer = file_organizer
        self._profile_manager = profile_manager
        self._condition = self._detect_condition()
        self._config = _CONDITION_CONFIGS.get(self._condition, _CONDITION_CONFIGS["Generic"])

        self._build_ui()

    def _detect_condition(self) -> str:
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "conditions") and profile.conditions:
                return _primary_condition(profile.conditions)
        return "Generic"

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
        root = QVBoxLayout(container)
        density = self._config.get("density", "medium")
        root.setSpacing(24 if density == "medium" else 16 if density == "low" else 20)
        root.setContentsMargins(24, 24, 24, 24)
        scroll.setWidget(container)

        root.addWidget(SectionTitle("File Organizer", self._theme))

        # Condition badge
        if self._condition != "Generic":
            badge = BodyLabel(f"Mode: {self._condition}-aware organization", self._theme)
            badge.setStyleSheet(f"color: {self._theme.get('accent', '#4a90d9')}; font-style: italic;")
            root.addWidget(badge)

        # Action cards
        root.addWidget(self._build_organize_card())
        root.addWidget(self._build_structure_card())
        root.addWidget(self._build_tools_card())
        root.addWidget(self._build_tips_card())

        # Results area
        self._results_list = QListWidget()
        self._results_list.setMinimumHeight(180)
        self._results_list.setStyleSheet(
            f"QListWidget {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; }}"
            f"QListWidget::item {{ padding: 6px; }}"
        )
        root.addWidget(BodyLabel("Activity Log", self._theme))
        root.addWidget(self._results_list)

        root.addStretch()

    def _build_organize_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Organize Files", self._theme))

        row = QHBoxLayout()
        row.setSpacing(12)

        select_btn = AccentButton("📁 Select Folder" if self._condition == "ADHD" else "Select Folder", self._theme)
        select_btn.clicked.connect(self._select_and_organize)
        row.addWidget(select_btn)

        dry_btn = QPushButton("Preview First" if self._condition in ("Anxiety", "OCD") else "Dry Run")
        dry_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dry_btn.clicked.connect(self._select_and_dry_run)
        row.addWidget(dry_btn)

        undo_btn = QPushButton("Undo Last")
        undo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        undo_btn.clicked.connect(self._undo_last)
        row.addWidget(undo_btn)

        row.addStretch()
        layout.addLayout(row)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self._progress.setStyleSheet(
            f"QProgressBar {{ border: 1px solid {self._theme.get('secondary', '#ccc')}; "
            f"border-radius: 4px; text-align: center; }}"
            f"QProgressBar::chunk {{ background-color: {self._theme.get('accent', '#4a90d9')}; }}"
        )
        layout.addWidget(self._progress)
        return card

    def _build_structure_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Suggested Structure", self._theme))

        self._structure_edit = QTextEdit()
        self._structure_edit.setReadOnly(True)
        self._structure_edit.setMaximumHeight(120)
        self._structure_edit.setPlainText("\n".join(f"  📂 {name}" for name in self._config["folder_names"]))
        self._structure_edit.setStyleSheet(
            f"QTextEdit {{ background-color: {self._theme.get('background', '#fff')}; "
            f"color: {self._theme.get('text', '#333')}; border: 1px solid "
            f"{self._theme.get('secondary', '#ccc')}; border-radius: 6px; padding: 8px; }}"
        )
        layout.addWidget(self._structure_edit)

        create_btn = AccentButton("Create Structure", self._theme)
        create_btn.clicked.connect(self._create_structure)
        layout.addWidget(create_btn)
        return card

    def _build_tools_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Tools", self._theme))

        row = QHBoxLayout()
        dup_btn = QPushButton("Find Duplicates")
        dup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dup_btn.clicked.connect(self._find_duplicates)
        row.addWidget(dup_btn)

        rename_btn = QPushButton("Batch Rename")
        rename_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rename_btn.clicked.connect(self._batch_rename)
        row.addWidget(rename_btn)

        row.addStretch()
        layout.addLayout(row)
        return card

    def _build_tips_card(self) -> QWidget:
        card = CardFrame(self._theme)
        layout = QVBoxLayout(card)
        layout.addWidget(SectionTitle("Tips", self._theme))

        tips = self._config.get("tips", [])
        for tip in tips:
            layout.addWidget(BodyLabel(f"• {tip}", self._theme))
        return card

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _select_and_organize(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Folder to Organize", str(Path.home()))
        if not path:
            return
        self._run_organization(Path(path), dry_run=False)

    def _select_and_dry_run(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Folder (Preview)", str(Path.home()))
        if not path:
            return
        self._run_organization(Path(path), dry_run=True)

    def _run_organization(self, source: Path, dry_run: bool) -> None:
        if not self._organizer:
            QMessageBox.warning(self, "Error", "File organizer not available.")
            return
        try:
            summary = self._organizer.organize_files(source, dry_run=dry_run)
            self._results_list.clear()
            mode = "Preview" if dry_run else "Organized"
            self._results_list.addItem(
                f"{mode}: {summary.get('moved', 0)} moved, {summary.get('skipped', 0)} skipped, {summary.get('errors', 0)} errors"
            )
            for action in summary.get("actions", [])[:20]:
                cat = action.get("category", "?")
                src_name = Path(action["source"]).name
                self._results_list.addItem(f"  → {cat}: {src_name}")
            self._progress.setValue(100)
        except Exception as exc:
            logger.error(f"Organization error: {exc}")
            QMessageBox.warning(self, "Error", f"Organization failed: {exc}")

    def _undo_last(self) -> None:
        if not self._organizer:
            return
        try:
            result = self._organizer.undo_last_organization()
            self._results_list.clear()
            self._results_list.addItem(result.get("message", "Undo complete."))
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Undo failed: {exc}")

    def _create_structure(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Create Structure In", str(Path.home()))
        if not path:
            return
        root = Path(path)
        created = []
        for name in self._config["folder_names"]:
            # Strip emoji/prefix for actual folder name if desired
            clean_name = name.strip()
            (root / clean_name).mkdir(parents=True, exist_ok=True)
            created.append(clean_name)
        self._results_list.clear()
        self._results_list.addItem(f"Created {len(created)} folders in {root}")
        for c in created:
            self._results_list.addItem(f"  📂 {c}")

    def _find_duplicates(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Find Duplicates In", str(Path.home()))
        if not path:
            return
        if not self._organizer:
            return
        try:
            dups = self._organizer.find_duplicates(Path(path))
            self._results_list.clear()
            if not dups:
                self._results_list.addItem("No duplicates found.")
                return
            self._results_list.addItem(f"Found {len(dups)} duplicate pairs:")
            for orig, dup in dups[:50]:
                self._results_list.addItem(f"  ⚠ {dup.name}")
                self._results_list.addItem(f"     matches {orig}")
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Duplicate scan failed: {exc}")

    def _batch_rename(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Batch Rename In", str(Path.home()))
        if not path:
            return
        if not self._organizer:
            return
        from PyQt6.QtWidgets import QInputDialog
        template, ok = QInputDialog.getText(
            self, "Batch Rename", "Template (use {name}, {ext}, {date}, {n}, {category}):",
            text="{date}_{category}_{n:03d}{ext}",
        )
        if not ok or not template:
            return
        try:
            results = self._organizer.batch_rename(Path(path), template, dry_run=False)
            self._results_list.clear()
            self._results_list.addItem(f"Renamed {len(results)} files:")
            for r in results[:30]:
                self._results_list.addItem(f"  {Path(r['original']).name} → {Path(r['new_name']).name}")
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"Rename failed: {exc}")

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
