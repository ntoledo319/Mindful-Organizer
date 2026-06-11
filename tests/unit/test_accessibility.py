"""Tests for src/utils/accessibility.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from utils.accessibility import (
    AccessibilitySettings,
    ColorBlindnessMode,
    ColorPalette,
    ContrastLevel,
    FontScale,
    KeyboardNavigationHelper,
    build_accessibility_stylesheet,
    detect_reduced_motion,
    effective_animation_duration,
    focus_indicator_stylesheet,
    get_palette,
    screen_reader_text,
)


class TestAccessibilitySettings:
    def test_default_creation(self):
        s = AccessibilitySettings()
        assert s.font_scale == FontScale.MEDIUM
        assert s.color_blindness_mode == ColorBlindnessMode.NONE
        assert s.contrast_level == ContrastLevel.NORMAL
        assert s.reduced_motion is False
        assert s.focus_indicators is True

    def test_to_dict_round_trip(self):
        s = AccessibilitySettings(
            font_scale=FontScale.LARGE,
            color_blindness_mode=ColorBlindnessMode.PROTANOPIA,
            contrast_level=ContrastLevel.HIGH,
            reduced_motion=True,
            animation_duration_ms=0,
        )
        d = s.to_dict()
        assert d["font_scale"] == "large"
        assert d["color_blindness_mode"] == "protanopia"
        assert d["reduced_motion"] is True
        assert d["animation_duration_ms"] == 0

    def test_from_dict_round_trip(self):
        original = AccessibilitySettings(
            font_scale=FontScale.EXTRA_LARGE,
            color_blindness_mode=ColorBlindnessMode.DEUTERANOPIA,
            contrast_level=ContrastLevel.EXTRA_HIGH,
            screen_reader_enabled=True,
            dyslexia_font=True,
        )
        restored = AccessibilitySettings.from_dict(original.to_dict())
        assert restored == original

    def test_from_dict_defaults(self):
        s = AccessibilitySettings.from_dict({})
        assert s.font_scale == FontScale.MEDIUM
        assert s.contrast_level == ContrastLevel.NORMAL
        assert s.animation_duration_ms == 200


class TestFontScale:
    def test_multipliers(self):
        assert FontScale.SMALL.multiplier == 0.85
        assert FontScale.MEDIUM.multiplier == 1.0
        assert FontScale.LARGE.multiplier == 1.25
        assert FontScale.EXTRA_LARGE.multiplier == 1.5

    def test_base_point_sizes(self):
        assert FontScale.SMALL.base_point_size == 9
        assert FontScale.MEDIUM.base_point_size == 11
        assert FontScale.LARGE.base_point_size == 14
        assert FontScale.EXTRA_LARGE.base_point_size == 17


class TestColorBlindnessMode:
    def test_descriptions(self):
        assert "Normal" in ColorBlindnessMode.NONE.description
        assert "Red-blind" in ColorBlindnessMode.PROTANOPIA.description
        assert "Green-blind" in ColorBlindnessMode.DEUTERANOPIA.description
        assert "Blue-blind" in ColorBlindnessMode.TRITANOPIA.description


class TestDetectReducedMotion:
    @patch("utils.accessibility.platform.system", return_value="darwin")
    @patch("utils.accessibility.subprocess.run")
    def test_detect_reduced_motion_darwin(self, mock_run, _mock_system):
        mock_run.return_value = MagicMock(stdout="1")
        assert detect_reduced_motion() is True

        mock_run.return_value = MagicMock(stdout="0")
        assert detect_reduced_motion() is False

    @patch("utils.accessibility.platform.system", return_value="linux")
    @patch("utils.accessibility.subprocess.run")
    def test_detect_reduced_motion_linux(self, mock_run, _mock_system):
        mock_run.return_value = MagicMock(stdout="false")
        assert detect_reduced_motion() is True

        mock_run.return_value = MagicMock(stdout="true")
        assert detect_reduced_motion() is False

    @patch("utils.accessibility.platform.system", return_value="unknown")
    def test_detect_reduced_motion_unknown_os(self, _mock_system):
        assert detect_reduced_motion() is False


class TestStylesheets:
    def test_build_accessibility_stylesheet_returns_non_empty(self):
        settings = AccessibilitySettings()
        css = build_accessibility_stylesheet(settings)
        assert isinstance(css, str)
        assert len(css) > 0
        assert "font-size" in css

    def test_build_accessibility_stylesheet_with_high_contrast(self):
        settings = AccessibilitySettings(contrast_level=ContrastLevel.HIGH)
        css = build_accessibility_stylesheet(settings)
        assert "#000000" in css or "#FFFFFF" in css

    def test_focus_indicator_stylesheet_returns_non_empty(self):
        settings = AccessibilitySettings(focus_indicators=True)
        css = focus_indicator_stylesheet(settings)
        assert isinstance(css, str)
        assert len(css) > 0
        assert "outline" in css or "border" in css

    def test_focus_indicator_stylesheet_disabled(self):
        settings = AccessibilitySettings(focus_indicators=False)
        css = focus_indicator_stylesheet(settings)
        assert css == ""


class TestGetPalette:
    def test_normal_palette(self):
        settings = AccessibilitySettings(color_blindness_mode=ColorBlindnessMode.NONE)
        palette = get_palette(settings)
        assert isinstance(palette, ColorPalette)
        assert palette.primary == "#4A90D9"

    def test_protanopia_palette(self):
        settings = AccessibilitySettings(color_blindness_mode=ColorBlindnessMode.PROTANOPIA)
        palette = get_palette(settings)
        assert palette.success == "#4682B4"

    def test_high_contrast_overrides(self):
        settings = AccessibilitySettings(contrast_level=ContrastLevel.HIGH)
        palette = get_palette(settings)
        assert palette.background == "#000000"
        assert palette.text_primary == "#FFFFFF"


class TestEffectiveAnimationDuration:
    def test_reduced_motion_zero(self):
        settings = AccessibilitySettings(reduced_motion=True)
        assert effective_animation_duration(settings) == 0

    def test_normal_duration(self):
        settings = AccessibilitySettings(reduced_motion=False, animation_duration_ms=300)
        assert effective_animation_duration(settings) == 300

    def test_fallback_base(self):
        settings = AccessibilitySettings(reduced_motion=False, animation_duration_ms=0)
        assert effective_animation_duration(settings, base_ms=200) == 200


class TestScreenReaderText:
    def test_basic(self):
        text = screen_reader_text("button", "Submit")
        assert "Submit" in text
        assert "button" in text

    def test_with_value_and_state(self):
        text = screen_reader_text("slider", "Volume", value="50", state="disabled")
        assert "Volume" in text
        assert "50" in text
        assert "disabled" in text


class TestKeyboardNavigationHelper:
    def test_register_and_get_ordered(self):
        helper = KeyboardNavigationHelper()
        w1 = MagicMock()
        w2 = MagicMock()
        helper.register(w1, order=1)
        helper.register(w2, order=0)
        ordered = helper.get_ordered_widgets()
        assert ordered == [w2, w1]

    def test_unregister(self):
        helper = KeyboardNavigationHelper()
        w1 = MagicMock()
        w2 = MagicMock()
        helper.register(w1)
        helper.register(w2)
        helper.unregister(w1)
        assert helper.get_ordered_widgets() == [w2]

    def test_groups(self):
        helper = KeyboardNavigationHelper()
        helper.register(MagicMock(), group="a")
        helper.register(MagicMock(), group="b")
        assert helper.groups() == ["a", "b"]
