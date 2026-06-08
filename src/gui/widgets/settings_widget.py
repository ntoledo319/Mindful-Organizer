"""
Settings widget for Mindful Organizer.

Provides profile display, theme selection with live preview, font scaling,
color blindness modes, accessibility toggles, notification preferences,
data management, and about information.
"""

from __future__ import annotations

import contextlib
import logging
import shutil
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app_metadata import APP_VERSION
from gui.components.state_controls import sans_font

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _section_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setFont(sans_font(18, QFont.Weight.DemiBold))
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
# Widget
# ---------------------------------------------------------------------------


class SettingsWidget(QWidget):
    """Application settings tab."""

    settings_changed = pyqtSignal()

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self._build_ui()
        self._load_current_settings()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        outer.addWidget(scroll)

        container = QWidget()
        container.setMaximumWidth(860)
        self._root = QVBoxLayout(container)
        self._root.setSpacing(18)
        self._root.setContentsMargins(32, 32, 32, 40)
        scroll.setWidget(container)

        self._root.addWidget(_section_title("Profile"))

        self._build_profile_section()
        self._build_subscription_section()
        self._build_theme_section()
        self._build_accessibility_section()
        self._build_notifications_section()
        self._build_data_section()
        self._build_about_section()

        # Save button
        save_btn = _accent_button("Save")
        save_btn.setFont(sans_font(13, QFont.Weight.Medium))
        save_btn.clicked.connect(self._save_settings)
        self._root.addWidget(save_btn)

        self._root.addStretch()

    # -- profile --------------------------------------------------------

    def _build_profile_section(self) -> None:
        group = QGroupBox("Profile")
        layout = QVBoxLayout(group)

        # Name
        name_row = QHBoxLayout()
        name_row.addWidget(_body_label("Name"))
        self._name_label = QLabel("User")
        self._name_label.setFont(sans_font(12, QFont.Weight.DemiBold))
        name_row.addWidget(self._name_label)
        name_row.addStretch()
        layout.addLayout(name_row)

        # Conditions
        cond_row = QHBoxLayout()
        cond_row.addWidget(_body_label("Conditions"))
        self._conditions_label = QLabel("None")
        cond_row.addWidget(self._conditions_label)
        cond_row.addStretch()
        layout.addLayout(cond_row)

        # Therapy types
        therapy_row = QHBoxLayout()
        therapy_row.addWidget(_body_label("Therapy types"))
        self._therapy_label = QLabel("None")
        therapy_row.addWidget(self._therapy_label)
        therapy_row.addStretch()
        layout.addLayout(therapy_row)

        # Edit profile button
        edit_btn = _accent_button("Edit profile")
        edit_btn.clicked.connect(self._reopen_onboarding)
        layout.addWidget(edit_btn)

        self._root.addWidget(group)

    # -- subscription ---------------------------------------------------

    def _build_subscription_section(self) -> None:
        from gui.subscription_helpers import tier_badge_text, trial_days_text

        group = QGroupBox("Subscription")
        layout = QVBoxLayout(group)

        sm = getattr(self.main_window, "subscription_manager", None)
        tier = tier_badge_text(sm)
        trial = trial_days_text(sm)

        tier_row = QHBoxLayout()
        tier_row.addWidget(_body_label("Current plan"))
        self._tier_label = QLabel(f"<b>{tier}</b>")
        self._tier_label.setFont(sans_font(12, QFont.Weight.Bold))
        tier_row.addWidget(self._tier_label)
        if trial:
            trial_lbl = QLabel(f"<span style='color:#27AE60;'>{trial}</span>")
            tier_row.addWidget(trial_lbl)
        tier_row.addStretch()
        layout.addLayout(tier_row)

        if tier == "FREE" and not trial:
            trial_btn = _accent_button("Start 14-day trial")
            trial_btn.clicked.connect(self._start_trial)
            layout.addWidget(trial_btn)

            upgrade_btn = _accent_button("Enter license key")
            upgrade_btn.clicked.connect(self._enter_license_key)
            layout.addWidget(upgrade_btn)
        elif trial or tier in ("PRO", "PREMIUM"):
            deactivate_btn = _accent_button("Deactivate license")
            deactivate_btn.clicked.connect(self._deactivate_license)
            layout.addWidget(deactivate_btn)

        self._root.addWidget(group)

    def _start_trial(self) -> None:
        sm = getattr(self.main_window, "subscription_manager", None)
        if sm:
            try:
                sm.start_trial()
                self._build_ui()
                self._load_current_settings()
            except Exception as e:
                QMessageBox.warning(self, "Trial", str(e))

    def _enter_license_key(self) -> None:
        from PyQt6.QtWidgets import QInputDialog

        key, ok = QInputDialog.getText(self, "Enter License Key", "License key:")
        if ok and key:
            sm = getattr(self.main_window, "subscription_manager", None)
            if sm:
                try:
                    sm.activate_license(key)
                    QMessageBox.information(self, "Success", "License activated!")
                    self._build_ui()
                    self._load_current_settings()
                except Exception as e:
                    QMessageBox.warning(self, "Invalid License", str(e))

    def _deactivate_license(self) -> None:
        sm = getattr(self.main_window, "subscription_manager", None)
        if sm:
            reply = QMessageBox.question(
                self,
                "Deactivate",
                "Deactivate your license and revert to Free?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                sm.deactivate()
                self._build_ui()
                self._load_current_settings()

    # -- theme ----------------------------------------------------------

    def _build_theme_section(self) -> None:
        group = QGroupBox("Theme")
        layout = QVBoxLayout(group)

        theme_row = QHBoxLayout()
        theme_row.addWidget(_body_label("Theme"))
        self._theme_combo = QComboBox()
        self._theme_combo.setMinimumWidth(200)
        all_themes: list[tuple[str, str, str]] = []
        try:
            all_themes = list(self.main_window.theme_manager.get_theme_names())
        except (AttributeError, TypeError):
            all_themes = [("ember", "Ember", "Warm dark default")]

        for name, display_name, desc in all_themes:
            self._theme_combo.addItem(f"{display_name} - {desc}", name)
        self._theme_combo.currentIndexChanged.connect(self._on_theme_preview)
        theme_row.addWidget(self._theme_combo)
        theme_row.addStretch()
        layout.addLayout(theme_row)

        # Preview swatch
        self._preview_frame = QFrame()
        self._preview_frame.setMinimumHeight(60)
        self._preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(self._preview_frame)

        self._root.addWidget(group)

    # -- accessibility ---------------------------------------------------

    def _build_accessibility_section(self) -> None:
        group = QGroupBox("Accessibility")
        layout = QVBoxLayout(group)

        # Font size slider (0.8x to 1.5x)
        font_row = QHBoxLayout()
        font_row.addWidget(_body_label("Font size"))
        self._font_slider = QSlider(Qt.Orientation.Horizontal)
        self._font_slider.setRange(80, 150)
        self._font_slider.setValue(100)
        self._font_slider.setTickInterval(10)
        self._font_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        font_row.addWidget(self._font_slider)
        self._font_value_label = QLabel("1.0x")
        self._font_slider.valueChanged.connect(
            lambda v: self._font_value_label.setText(f"{v / 100:.1f}x")
        )
        font_row.addWidget(self._font_value_label)
        layout.addLayout(font_row)

        # Color blindness mode
        cb_row = QHBoxLayout()
        cb_row.addWidget(_body_label("Color blindness mode"))
        self._cb_combo = QComboBox()
        self._cb_combo.addItem("None", None)
        self._cb_combo.addItem("Protanopia", "protanopia")
        self._cb_combo.addItem("Deuteranopia", "deuteranopia")
        self._cb_combo.addItem("Tritanopia", "tritanopia")
        cb_row.addWidget(self._cb_combo)
        cb_row.addStretch()
        layout.addLayout(cb_row)

        # Reduced motion
        self._reduced_motion_check = QCheckBox("Reduced motion")
        layout.addWidget(self._reduced_motion_check)

        # Dyslexia font
        self._dyslexia_font_check = QCheckBox("Dyslexia-friendly font")
        layout.addWidget(self._dyslexia_font_check)

        self._root.addWidget(group)

    # -- notifications ---------------------------------------------------

    def _build_notifications_section(self) -> None:
        group = QGroupBox("Notifications")
        layout = QVBoxLayout(group)

        freq_row = QHBoxLayout()
        freq_row.addWidget(_body_label("Notification frequency"))
        self._notif_combo = QComboBox()
        self._notif_combo.addItem("Off", "off")
        self._notif_combo.addItem("Low (hourly)", "low")
        self._notif_combo.addItem("Normal (30 min)", "normal")
        self._notif_combo.addItem("Frequent (15 min)", "frequent")
        freq_row.addWidget(self._notif_combo)
        freq_row.addStretch()
        layout.addLayout(freq_row)

        self._root.addWidget(group)

    # -- data management -------------------------------------------------

    def _build_data_section(self) -> None:
        group = QGroupBox("Data")
        layout = QVBoxLayout(group)

        btn_row = QHBoxLayout()

        export_btn = _accent_button("Export")
        export_btn.clicked.connect(self._export_all_data)
        btn_row.addWidget(export_btn)

        import_btn = _accent_button("Import")
        import_btn.clicked.connect(self._import_data)
        btn_row.addWidget(import_btn)

        sync_btn = _accent_button("Wearable Sync")
        sync_btn.clicked.connect(self._sync_wearables)
        btn_row.addWidget(sync_btn)

        reset_btn = _accent_button("Reset")
        reset_btn.clicked.connect(self._reset_data)
        btn_row.addWidget(reset_btn)

        layout.addLayout(btn_row)
        self._root.addWidget(group)

    # -- about -----------------------------------------------------------

    def _build_about_section(self) -> None:
        group = QGroupBox("About")
        layout = QVBoxLayout(group)

        layout.addWidget(_body_label(f"Hearth v{APP_VERSION}"))
        layout.addWidget(_body_label("All data stored locally on your device."))
        layout.addWidget(_body_label("Licensed under the MIT License."))
        layout.addWidget(
            _body_label(
                "This app is a supplement to professional mental health care, not a replacement."
            )
        )

        self._root.addWidget(group)

    # ------------------------------------------------------------------
    # Settings load / save
    # ------------------------------------------------------------------

    def _load_current_settings(self) -> None:
        """Populate UI controls from current state."""
        try:
            profile = self.main_window.profile_manager.current_profile
            if profile:
                self._name_label.setText(getattr(profile, "name", "User"))
                conditions: set[Any] = getattr(profile, "conditions", set())
                if conditions:
                    cond_text = ", ".join(
                        c.value if hasattr(c, "value") else str(c) for c in conditions
                    )
                    self._conditions_label.setText(cond_text)
                therapy_types: set[Any] = getattr(profile, "therapy_types", set())
                if therapy_types:
                    tt_text = ", ".join(
                        t.value if hasattr(t, "value") else str(t) for t in therapy_types
                    )
                    self._therapy_label.setText(tt_text)
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Settings load error: {exc}")

        try:
            tm = self.main_window.theme_manager
            idx = self._theme_combo.findData(tm.current_theme_name)
            if idx >= 0:
                self._theme_combo.setCurrentIndex(idx)
            self._font_slider.setValue(int(tm.font_scale * 100))
            cb_idx = self._cb_combo.findData(tm.color_blind_mode)
            if cb_idx >= 0:
                self._cb_combo.setCurrentIndex(cb_idx)
            self._reduced_motion_check.setChecked(tm.reduced_motion)
            self._dyslexia_font_check.setChecked(tm.dyslexia_font)
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Settings load error: {exc}")

    def _save_settings(self) -> None:
        """Apply and persist all settings."""
        try:
            tm = self.main_window.theme_manager

            # Theme
            theme_name = self._theme_combo.currentData()
            if theme_name:
                try:
                    self.main_window.change_theme(theme_name)
                except (AttributeError, TypeError):
                    tm.set_theme(theme_name)

            # Font scale
            tm.font_scale = self._font_slider.value() / 100.0

            # Color blind mode
            tm.color_blind_mode = self._cb_combo.currentData()

            # Toggles
            tm.reduced_motion = self._reduced_motion_check.isChecked()
            tm.dyslexia_font = self._dyslexia_font_check.isChecked()

            # Persist
            self.main_window.save_settings()

            # Reapply stylesheet
            try:
                stylesheet = tm.generate_stylesheet()
                self.main_window.setStyleSheet(stylesheet)
            except (AttributeError, TypeError) as exc:
                logger.debug(f"Stylesheet generation error: {exc}")

            self.settings_changed.emit()
            QMessageBox.information(self, "Settings", "Settings saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")

    # ------------------------------------------------------------------
    # Theme preview
    # ------------------------------------------------------------------

    def _on_theme_preview(self, index: int) -> None:
        theme_name = self._theme_combo.itemData(index)
        if not theme_name:
            return
        if theme_name == "__upsell__":
            from gui.subscription_helpers import gated

            gated("all_themes", getattr(self.main_window, "subscription_manager", None), self)
            # Reset to first theme
            self._theme_combo.setCurrentIndex(0)
            return
        try:
            from gui.themes import THEMES

            theme = THEMES.get(theme_name)
            if theme:
                self._preview_frame.setStyleSheet(
                    f"QFrame {{ background-color: {theme.background}; "
                    f"border: 3px solid {theme.accent}; border-radius: 8px; }}"
                )
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Export manager error: {exc}")

    # ------------------------------------------------------------------
    # Data management
    # ------------------------------------------------------------------

    def _export_all_data(self) -> None:
        from gui.subscription_helpers import gated

        if not gated("data_export", getattr(self.main_window, "subscription_manager", None), self):
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "hearth_export.json", "JSON (*.json)"
        )
        if not path:
            return
        try:
            # Export the real SQLite-backed health data (moods, journal,
            # medications, sleep, tasks, ...) via the export manager.
            from core.export_manager import ExportFormat, ExportOptions

            em = self.main_window.export_manager
            options = ExportOptions(
                format=ExportFormat.JSON,
                output_path=Path(path),
                include_settings=True,
            )
            out = em.export(options)
            QMessageBox.information(self, "Export", f"Data exported to {out}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Export failed: {e}")

    def _import_data(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import Data", "", "JSON (*.json)")
        if not path:
            return
        reply = QMessageBox.question(
            self,
            "Import",
            "Importing data may overwrite existing entries. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            em = self.main_window.export_manager
            counts = em.import_from_json(Path(path), merge=True, validate_first=True)
            total = sum(counts.values()) if isinstance(counts, dict) else 0
            QMessageBox.information(
                self,
                "Import",
                f"Imported {total} record(s). You may need to restart to see all changes.",
            )
        except Exception as e:  # noqa: BLE001
            QMessageBox.warning(self, "Import failed", f"Could not import data: {e}")

    def _reset_data(self) -> None:
        reply = QMessageBox.warning(
            self,
            "Reset All Data",
            "This will permanently delete ALL your data including profile, "
            "mood entries, journal entries, tasks, and settings.\n\n"
            "This action cannot be undone. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        confirm = QMessageBox.critical(
            self,
            "Confirm Reset",
            "Last chance. Click Yes to permanently delete all data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            # Close the live DB connection first so we don't unlink the file out
            # from under an open WAL handle (which would leave an orphaned inode).
            db = getattr(self.main_window, "db", None)
            if db is not None:
                with contextlib.suppress(Exception):
                    db.close()

            data_dir = Path(self.main_window.data_dir)
            for item in data_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            QMessageBox.information(
                self, "Reset", "All data has been reset. Please restart the application."
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Reset failed: {e}")

    def _sync_wearables(self) -> None:
        from gui.subscription_helpers import gated

        if not gated(
            "wearable_sync", getattr(self.main_window, "subscription_manager", None), self
        ):
            return

        from core.wearable_sync import WearableSyncManager

        path = QFileDialog.getExistingDirectory(self, "Select Export Directory", str(Path.home()))
        if not path:
            return

        try:
            manager = WearableSyncManager()
            results = manager.sync_all_available(Path(path))
            total = sum(results.values())

            if total > 0:
                msg = (
                    f"Successfully imported {total} records:\n"
                    f"• Apple Health: {results.get('apple_health', 0)}\n"
                    f"• Google Fit: {results.get('google_fit', 0)}"
                )
                QMessageBox.information(self, "Wearable Sync", msg)
            else:
                QMessageBox.information(
                    self,
                    "Wearable Sync",
                    "No valid sleep data found in the selected directory.\n"
                    "Please select an unzipped Apple Health or Google Fit export.",
                )
        except Exception as e:
            logger.error("Failed to sync wearables: %s", e)
            QMessageBox.warning(self, "Error", f"Failed to sync wearables: {e}")

    # ------------------------------------------------------------------
    # Onboarding
    # ------------------------------------------------------------------

    def _reopen_onboarding(self) -> None:
        try:
            from gui.widgets.onboarding import OnboardingWizard

            wizard = OnboardingWizard(
                self.main_window.profile_manager,
                self.main_window.data_dir,
                parent=self.main_window,
            )
            wizard.exec()
            self._load_current_settings()
        except ImportError:
            QMessageBox.information(self, "Onboarding", "Onboarding wizard is not available.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open onboarding: {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Called by main window on close."""
        pass
