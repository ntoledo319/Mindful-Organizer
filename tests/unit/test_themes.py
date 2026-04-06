"""
Tests for ThemeManager (src/gui/themes.py).

Covers theme validation, switching, color-blind overrides,
stylesheet generation, font scaling, and condition recommendations.
"""

import pytest

try:
    from src.gui.themes import (
        ThemeManager,
        Theme,
        THEMES,
        COLOR_BLIND_OVERRIDES,
    )
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="themes module not available")


@pytest.fixture
def tm():
    return ThemeManager()


# ---------------------------------------------------------------------------
# All themes valid
# ---------------------------------------------------------------------------

class TestAllThemesValid:

    def test_all_themes_have_required_fields(self):
        required = {
            "background", "text", "accent", "secondary", "success",
            "warning", "danger", "card_bg", "border", "hover",
            "disabled", "input_bg", "tab_active", "tab_inactive",
            "scrollbar", "shadow",
        }
        for name, theme in THEMES.items():
            colors = theme.to_dict()
            for field in required:
                assert field in colors, f"Theme '{name}' missing '{field}'"
                assert colors[field], f"Theme '{name}' has empty '{field}'"

    def test_all_themes_have_names(self):
        for name, theme in THEMES.items():
            assert theme.name == name
            assert theme.display_name
            assert theme.description

    def test_minimum_theme_count(self):
        assert len(THEMES) >= 6

    def test_all_themes_have_condition_suitability(self):
        for name, theme in THEMES.items():
            assert isinstance(theme.condition_suitability, list)

    def test_color_values_look_like_colors(self):
        """All color values should start with # or rgba."""
        for name, theme in THEMES.items():
            colors = theme.to_dict()
            for key, value in colors.items():
                assert (
                    value.startswith("#") or value.startswith("rgba")
                ), f"Theme '{name}' key '{key}' has unusual color: {value}"


# ---------------------------------------------------------------------------
# Theme switching
# ---------------------------------------------------------------------------

class TestThemeSwitching:

    def test_default_theme_is_light(self, tm):
        assert tm.current_theme_name == "light"
        assert tm.current_theme.name == "light"

    def test_set_theme(self, tm):
        tm.set_theme("dark")
        assert tm.current_theme_name == "dark"
        assert tm.current_theme.background == THEMES["dark"].background

    def test_set_invalid_theme_ignored(self, tm):
        tm.set_theme("nonexistent")
        assert tm.current_theme_name == "light"

    def test_get_theme_names(self, tm):
        names = tm.get_theme_names()
        assert len(names) >= 6
        assert all(isinstance(n, tuple) and len(n) == 3 for n in names)

    def test_switch_all_themes(self, tm):
        """Switching to every theme should not raise."""
        for name in THEMES:
            tm.set_theme(name)
            assert tm.current_theme.name == name


# ---------------------------------------------------------------------------
# Color-blind overrides
# ---------------------------------------------------------------------------

class TestColorBlindOverrides:

    def test_protanopia_overrides(self, tm):
        tm.color_blind_mode = "protanopia"
        colors = tm.get_colors()

        expected = COLOR_BLIND_OVERRIDES["protanopia"]
        for key, value in expected.items():
            assert colors[key] == value

    def test_deuteranopia_overrides(self, tm):
        tm.color_blind_mode = "deuteranopia"
        colors = tm.get_colors()

        expected = COLOR_BLIND_OVERRIDES["deuteranopia"]
        for key, value in expected.items():
            assert colors[key] == value

    def test_tritanopia_overrides(self, tm):
        tm.color_blind_mode = "tritanopia"
        colors = tm.get_colors()

        expected = COLOR_BLIND_OVERRIDES["tritanopia"]
        for key, value in expected.items():
            assert colors[key] == value

    def test_no_color_blind_mode(self, tm):
        tm.color_blind_mode = None
        colors = tm.get_colors()
        # Should use original theme colors
        assert colors["success"] == THEMES["light"].success

    def test_invalid_color_blind_mode(self, tm):
        tm.color_blind_mode = "invalid"
        colors = tm.get_colors()
        # Should use original colors
        assert colors["success"] == THEMES["light"].success


# ---------------------------------------------------------------------------
# Stylesheet generation
# ---------------------------------------------------------------------------

class TestStylesheetGeneration:

    def test_generate_stylesheet(self, tm):
        stylesheet = tm.generate_stylesheet()

        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 100
        assert "QMainWindow" in stylesheet
        assert "QPushButton" in stylesheet

    def test_stylesheet_contains_theme_colors(self, tm):
        tm.set_theme("dark")
        stylesheet = tm.generate_stylesheet()

        assert THEMES["dark"].background in stylesheet
        assert THEMES["dark"].accent in stylesheet

    def test_stylesheet_with_color_blind(self, tm):
        tm.color_blind_mode = "protanopia"
        stylesheet = tm.generate_stylesheet()

        assert COLOR_BLIND_OVERRIDES["protanopia"]["success"] in stylesheet

    def test_stylesheet_with_reduced_motion(self, tm):
        tm.reduced_motion = True
        stylesheet = tm.generate_stylesheet()
        # The animation duration should be 0 when reduced motion is on
        assert stylesheet  # Should not crash

    def test_stylesheet_with_dyslexia_font(self, tm):
        tm.dyslexia_font = True
        stylesheet = tm.generate_stylesheet()
        assert "OpenDyslexic" in stylesheet

    def test_stylesheet_default_font(self, tm):
        tm.dyslexia_font = False
        stylesheet = tm.generate_stylesheet()
        assert "Segoe UI" in stylesheet

    def test_get_card_style(self, tm):
        style = tm.get_card_style()
        assert "background-color" in style
        assert "border-radius" in style

    def test_get_card_style_variants(self, tm):
        for variant in ("default", "accent", "success", "warning", "danger"):
            style = tm.get_card_style(variant)
            assert "background-color" in style


# ---------------------------------------------------------------------------
# Font scaling
# ---------------------------------------------------------------------------

class TestFontScaling:

    def test_default_font_scale(self, tm):
        assert tm.font_scale == 1.0

    def test_font_scale_in_stylesheet(self, tm):
        tm.font_scale = 1.5
        stylesheet = tm.generate_stylesheet()
        # Default 12px * 1.5 = 18px
        assert "18px" in stylesheet

    def test_large_font_scale(self, tm):
        tm.font_scale = 2.0
        stylesheet = tm.generate_stylesheet()
        # 12 * 2.0 = 24px base
        assert "24px" in stylesheet

    def test_small_font_scale(self, tm):
        tm.font_scale = 0.8
        stylesheet = tm.generate_stylesheet()
        # 12 * 0.8 = 9.6 -> int = 9
        assert "9px" in stylesheet


# ---------------------------------------------------------------------------
# Condition recommendations
# ---------------------------------------------------------------------------

class TestConditionRecommendations:

    def test_anxiety_recommends_calm(self, tm):
        recs = tm.get_recommended_themes({"anxiety"})
        names = [r[0] for r in recs]

        assert "calm" in names
        # Calm should rank highly
        calm_idx = names.index("calm")
        assert calm_idx < 3

    def test_adhd_recommends_focus(self, tm):
        recs = tm.get_recommended_themes({"adhd"})
        names = [r[0] for r in recs]
        assert "focus" in names or "high_contrast" in names

    def test_depression_recommends_warm(self, tm):
        recs = tm.get_recommended_themes({"depression"})
        names = [r[0] for r in recs]
        assert "warm" in names

    def test_ocd_recommends_structured(self, tm):
        recs = tm.get_recommended_themes({"ocd"})
        names = [r[0] for r in recs]
        assert "structured" in names

    def test_ptsd_recommends_gentle(self, tm):
        recs = tm.get_recommended_themes({"ptsd"})
        names = [r[0] for r in recs]
        assert "gentle" in names

    def test_general_condition(self, tm):
        recs = tm.get_recommended_themes({"general"})
        assert len(recs) > 0

    def test_multiple_conditions(self, tm):
        recs = tm.get_recommended_themes({"anxiety", "ptsd"})
        assert len(recs) > 0
        # Dark and calm/gentle should rank high for both
        names = [r[0] for r in recs[:4]]
        assert any(n in names for n in ("calm", "gentle", "dark"))

    def test_empty_conditions(self, tm):
        recs = tm.get_recommended_themes(set())
        # Should still return themes with "general" suitability
        assert len(recs) >= 1
