"""
Integration tests for the Settings → Theme → Accessibility workflow.

Validates that settings changes in the UI propagate to ThemeManager,
generate correct stylesheets, apply accessibility overrides, and
remain consistent across the ThemeManager and AccessibilityManager.
"""

from __future__ import annotations

import json
import re
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from gui.themes import COLOR_BLIND_OVERRIDES, THEMES, ThemeManager
from gui.widgets.settings_widget import SettingsWidget
from utils.accessibility import (
    AccessibilityManager,
    AccessibilitySettings,
    ColorBlindnessMode,
    FontScale,
    effective_animation_duration,
)


@pytest.fixture
def mock_main_window(tmp_path):
    """Return a main-window stand-in with real ThemeManager and AccessibilityManager."""
    mw = MagicMock()

    # Real ThemeManager so stylesheet generation and colour overrides work
    tm = ThemeManager()
    mw.theme_manager = tm

    # Real AccessibilityManager for cross-module consistency checks
    mw.accessibility_manager = AccessibilityManager()

    # Profile manager
    profile = SimpleNamespace(name="Test User", conditions=set(), therapy_types=set())
    pm = MagicMock()
    pm.current_profile = profile
    mw.profile_manager = pm

    # Subscription manager (free tier so no gated dialogs appear)
    sm = MagicMock()
    sm.current_tier = SimpleNamespace(value="free")
    sm.trial_days_remaining = 0
    sm.has_feature.return_value = False
    mw.subscription_manager = sm

    # Export manager
    em = MagicMock()
    mw.export_manager = em

    mw.data_dir = tmp_path
    mw.setStyleSheet.return_value = None

    def _save_settings():
        """Mirror the real main_window save_settings behaviour."""
        settings = {
            "theme": tm.current_theme_name,
            "font_scale": tm.font_scale,
            "color_blind_mode": tm.color_blind_mode,
            "reduced_motion": tm.reduced_motion,
            "dyslexia_font": tm.dyslexia_font,
        }
        settings_file = tmp_path / "settings.json"
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)

    def _change_theme(theme_name: str):
        """Mirror the real main_window change_theme behaviour."""
        tm.set_theme(theme_name)
        _save_settings()

    mw.save_settings.side_effect = _save_settings
    mw.change_theme.side_effect = _change_theme

    return mw


# ---------------------------------------------------------------------------
# 1. Settings persistence
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.gui
class TestSettingsPersistence:
    def test_font_scale_change_is_persisted(self, qtbot, mock_main_window, tmp_path):
        """Changing font scale via SettingsWidget should persist to the settings file."""
        widget = SettingsWidget(main_window=mock_main_window)
        qtbot.addWidget(widget)

        # Change font scale slider from default 100 (medium) to 125 (large)
        widget._font_slider.setValue(125)

        with (
            patch("gui.widgets.settings_widget.QMessageBox"),
            qtbot.waitSignal(widget.settings_changed, timeout=1000),
        ):
            widget._save_settings()

        # Verify settings JSON was written with the new scale
        settings_file = tmp_path / "settings.json"
        assert settings_file.exists()
        data = json.loads(settings_file.read_text())
        assert data["font_scale"] == 1.25

        # Verify ThemeManager reflects the change
        assert mock_main_window.theme_manager.font_scale == 1.25

    def test_theme_change_is_persisted(self, qtbot, mock_main_window, tmp_path):
        """Changing theme via SettingsWidget should persist the new theme name."""
        widget = SettingsWidget(main_window=mock_main_window)
        qtbot.addWidget(widget)

        # Switch theme combo from default "onyx" to "alabaster"
        idx = widget._theme_combo.findData("alabaster")
        assert idx >= 0, "alabaster theme not found in combo"
        widget._theme_combo.setCurrentIndex(idx)

        with (
            patch("gui.widgets.settings_widget.QMessageBox"),
            qtbot.waitSignal(widget.settings_changed, timeout=1000),
        ):
            widget._save_settings()

        settings_file = tmp_path / "settings.json"
        assert settings_file.exists()
        data = json.loads(settings_file.read_text())
        assert data["theme"] == "alabaster"
        assert mock_main_window.theme_manager.current_theme_name == "alabaster"

    def test_settings_changed_signal_emitted_on_save(self, qtbot, mock_main_window):
        """_save_settings must emit the settings_changed signal."""
        widget = SettingsWidget(main_window=mock_main_window)
        qtbot.addWidget(widget)

        with (
            patch("gui.widgets.settings_widget.QMessageBox"),
            qtbot.waitSignal(widget.settings_changed, timeout=1000),
        ):
            widget._save_settings()


# ---------------------------------------------------------------------------
# 2. Theme application after setting change
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestThemeApplication:
    def test_theme_change_reflected_in_stylesheet(self):
        """Switching theme should update generate_stylesheet output colours."""
        tm = ThemeManager()

        tm.set_theme("onyx")
        ss_onyx = tm.generate_stylesheet()
        assert THEMES["onyx"].background in ss_onyx
        assert THEMES["onyx"].accent in ss_onyx

        tm.set_theme("alabaster")
        ss_alabaster = tm.generate_stylesheet()
        assert THEMES["alabaster"].background in ss_alabaster
        assert THEMES["alabaster"].accent in ss_alabaster

        # Old onyx colours should not leak into the new stylesheet
        assert THEMES["onyx"].background not in ss_alabaster

    def test_font_scale_reflected_in_stylesheet(self):
        """Font scale changes should affect computed font sizes in the stylesheet."""
        tm = ThemeManager()
        tm.font_scale = 1.5
        ss = tm.generate_stylesheet()

        # base_font_size = int(14 * 1.5) = 21px
        assert re.search(r"font-size:\s*21px", ss)

    def test_large_font_scale_in_stylesheet(self):
        """A large font scale should produce proportionally larger sizes."""
        tm = ThemeManager()
        tm.font_scale = 2.0
        ss = tm.generate_stylesheet()

        # int(14 * 2.0) = 28px
        assert re.search(r"font-size:\s*28px", ss)


# ---------------------------------------------------------------------------
# 3. Accessibility integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestAccessibilityIntegration:
    def test_deuteranopia_overrides_in_stylesheet(self):
        """Color-blind mode should override theme colours in the generated stylesheet."""
        tm = ThemeManager()
        tm.set_theme("onyx")
        tm.color_blind_mode = "deuteranopia"

        ss = tm.generate_stylesheet()
        expected = COLOR_BLIND_OVERRIDES["deuteranopia"]

        # Accent and danger are referenced directly in the stylesheet;
        # success/warning are part of the token set but not emitted in QSS.
        assert expected["accent"] in ss
        assert expected["danger"] in ss

    def test_protanopia_overrides_in_stylesheet(self):
        """Protanopia should apply its own distinct palette overrides."""
        tm = ThemeManager()
        tm.set_theme("alabaster")
        tm.color_blind_mode = "protanopia"

        ss = tm.generate_stylesheet()
        expected = COLOR_BLIND_OVERRIDES["protanopia"]
        assert expected["accent"] in ss

    def test_reduced_motion_zeroes_animation_duration(self):
        """Reduced motion should force animation duration to 0 ms."""
        settings = AccessibilitySettings(reduced_motion=True, animation_duration_ms=200)
        assert effective_animation_duration(settings) == 0

    def test_reduced_motion_false_uses_base_duration(self):
        """With reduced motion off, the base animation duration is preserved."""
        settings = AccessibilitySettings(reduced_motion=False, animation_duration_ms=350)
        assert effective_animation_duration(settings) == 350

    def test_accessibility_manager_applies_color_blind_palette(self):
        """AccessibilityManager should return a palette adjusted for colour blindness."""
        am = AccessibilityManager()
        am.settings.color_blindness_mode = ColorBlindnessMode.DEUTERANOPIA

        palette = am.get_palette()
        # Deuteranopia palette shifts success to a blue tone
        assert palette.success == "#4682B4"

    def test_accessibility_stylesheet_contains_adjusted_colors(self):
        """AccessibilityManager stylesheet should embed colour-blind-safe colours."""
        am = AccessibilityManager()
        am.settings.color_blindness_mode = ColorBlindnessMode.DEUTERANOPIA
        am.settings.font_scale = FontScale.LARGE

        stylesheet = am.get_stylesheet()
        # Deuteranopia shifts primary to a blue tone that appears in the stylesheet
        assert "#4A7FD9" in stylesheet
        # FontScale.LARGE base_point_size is 14pt
        assert "font-size: 14pt" in stylesheet


# ---------------------------------------------------------------------------
# 4. Cross-module consistency
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.gui
class TestCrossModuleConsistency:
    def test_setting_change_propagates_to_theme_manager(self, qtbot, mock_main_window):
        """Changing settings via SettingsWidget must update ThemeManager state."""
        widget = SettingsWidget(main_window=mock_main_window)
        qtbot.addWidget(widget)

        # Mutate several controls
        idx = widget._theme_combo.findData("alabaster")
        widget._theme_combo.setCurrentIndex(idx)
        widget._font_slider.setValue(150)
        cb_idx = widget._cb_combo.findData("deuteranopia")
        widget._cb_combo.setCurrentIndex(cb_idx)
        widget._reduced_motion_check.setChecked(True)
        widget._dyslexia_font_check.setChecked(True)

        with patch("gui.widgets.settings_widget.QMessageBox"):
            widget._save_settings()

        tm = mock_main_window.theme_manager
        assert tm.current_theme_name == "alabaster"
        assert tm.font_scale == 1.5
        assert tm.color_blind_mode == "deuteranopia"
        assert tm.reduced_motion is True
        assert tm.dyslexia_font is True

    def test_accessibility_manager_reflects_theme_manager_changes(self, qtbot, mock_main_window):
        """After a settings save, AccessibilityManager can be synced and reflects the same values."""
        widget = SettingsWidget(main_window=mock_main_window)
        qtbot.addWidget(widget)

        widget._font_slider.setValue(125)
        cb_idx = widget._cb_combo.findData("deuteranopia")
        widget._cb_combo.setCurrentIndex(cb_idx)
        widget._reduced_motion_check.setChecked(True)

        with patch("gui.widgets.settings_widget.QMessageBox"):
            widget._save_settings()

        # Simulate the app-level sync that would happen after settings change
        tm = mock_main_window.theme_manager
        am = mock_main_window.accessibility_manager

        am.settings.font_scale = FontScale(
            {0.85: "small", 1.0: "medium", 1.25: "large", 1.5: "extra_large"}.get(
                tm.font_scale, "medium"
            )
        )
        am.settings.color_blindness_mode = ColorBlindnessMode(tm.color_blind_mode or "none")
        am.settings.reduced_motion = tm.reduced_motion
        am.settings.dyslexia_font = tm.dyslexia_font

        assert am.settings.font_scale == FontScale.LARGE
        assert am.settings.color_blindness_mode == ColorBlindnessMode.DEUTERANOPIA
        assert am.settings.reduced_motion is True

    def test_stylesheets_remain_consistent_after_sync(self, qtbot, mock_main_window):
        """Both ThemeManager and AccessibilityManager should produce stylesheets that
        contain the same canonical values after a settings change."""
        widget = SettingsWidget(main_window=mock_main_window)
        qtbot.addWidget(widget)

        idx = widget._theme_combo.findData("alabaster")
        widget._theme_combo.setCurrentIndex(idx)
        widget._font_slider.setValue(150)
        cb_idx = widget._cb_combo.findData("deuteranopia")
        widget._cb_combo.setCurrentIndex(cb_idx)
        widget._reduced_motion_check.setChecked(True)

        with patch("gui.widgets.settings_widget.QMessageBox"):
            widget._save_settings()

        tm = mock_main_window.theme_manager
        am = mock_main_window.accessibility_manager

        # Sync accessibility manager to theme manager state
        am.settings.font_scale = FontScale.LARGE
        am.settings.color_blindness_mode = ColorBlindnessMode.DEUTERANOPIA
        am.settings.reduced_motion = tm.reduced_motion

        theme_ss = tm.generate_stylesheet()
        am_ss = am.get_stylesheet()

        # Theme stylesheet should contain the alabaster background
        assert THEMES["alabaster"].background in theme_ss
        # Theme stylesheet should contain deuteranopia accent override
        assert COLOR_BLIND_OVERRIDES["deuteranopia"]["accent"] in theme_ss
        # Accessibility stylesheet should contain deuteranopia primary colour
        assert "#4A7FD9" in am_ss
        # Reduced-motion disable transitions should appear in accessibility stylesheet
        assert "transition: none" in am_ss
