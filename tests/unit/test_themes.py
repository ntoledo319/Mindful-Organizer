"""
Tests for ThemeManager (src/gui/themes.py).

Covers theme validation, switching, color-blind overrides,
stylesheet generation, font scaling, and condition recommendations.
"""

import pytest

from gui.themes import (
    COLOR_BLIND_OVERRIDES,
    THEMES,
    ThemeManager,
)


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

    def test_launch_theme_count(self):
        assert set(THEMES) == {"onyx", "alabaster", "slate", "quiet"}

    def test_all_themes_have_condition_suitability(self):
        for _name, theme in THEMES.items():
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

    def test_default_theme_is_onyx(self, tm):
        assert tm.current_theme_name == "onyx"
        assert tm.current_theme.name == "onyx"

    def test_set_theme(self, tm):
        tm.set_theme("alabaster")
        assert tm.current_theme_name == "alabaster"
        assert tm.current_theme.background == THEMES["alabaster"].background

    def test_legacy_theme_names_map_to_new_themes(self, tm):
        tm.set_theme("linen")
        assert tm.current_theme_name == "alabaster"
        tm.set_theme("ember")
        assert tm.current_theme_name == "onyx"

    def test_set_invalid_theme_ignored(self, tm):
        tm.set_theme("nonexistent")
        assert tm.current_theme_name == "onyx"

    def test_get_theme_names(self, tm):
        names = tm.get_theme_names()
        assert len(names) == 4
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
        assert colors["success"] == THEMES["onyx"].success

    def test_invalid_color_blind_mode(self, tm):
        tm.color_blind_mode = "invalid"
        colors = tm.get_colors()
        # Should use original colors
        assert colors["success"] == THEMES["onyx"].success


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
        tm.set_theme("onyx")
        stylesheet = tm.generate_stylesheet()

        assert THEMES["onyx"].background in stylesheet
        assert THEMES["onyx"].accent in stylesheet

    def test_stylesheet_with_color_blind(self, tm):
        tm.color_blind_mode = "protanopia"
        stylesheet = tm.generate_stylesheet()

        assert COLOR_BLIND_OVERRIDES["protanopia"]["accent"] in stylesheet

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
        assert "SF Pro Text" in stylesheet
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
        import re
        tm.font_scale = 1.5
        stylesheet = tm.generate_stylesheet()
        # Default 12px * 1.5 = 18px
        assert re.search(r"font-size:\s*18px", stylesheet)

    def test_large_font_scale(self, tm):
        import re
        tm.font_scale = 2.0
        stylesheet = tm.generate_stylesheet()
        # 12 * 2.0 = 24px base
        assert re.search(r"font-size:\s*24px", stylesheet)

    def test_small_font_scale(self, tm):
        import re
        tm.font_scale = 0.8
        stylesheet = tm.generate_stylesheet()
        # 12 * 0.8 = 9.6 -> int = 9
        assert re.search(r"font-size:\s*9px", stylesheet)


# ---------------------------------------------------------------------------
# Condition recommendations
# ---------------------------------------------------------------------------

class TestConditionRecommendations:

    def test_anxiety_recommends_quiet_or_onyx(self, tm):
        recs = tm.get_recommended_themes({"anxiety"})
        names = [r[0] for r in recs]

        assert "onyx" in names
        assert "quiet" in names

    def test_adhd_recommends_quiet(self, tm):
        recs = tm.get_recommended_themes({"adhd"})
        names = [r[0] for r in recs]
        assert "quiet" in names

    def test_depression_keeps_general_themes(self, tm):
        recs = tm.get_recommended_themes({"depression"})
        names = [r[0] for r in recs]
        assert "onyx" in names
        assert "alabaster" in names

    def test_ocd_recommends_onyx(self, tm):
        recs = tm.get_recommended_themes({"ocd"})
        names = [r[0] for r in recs]
        assert "onyx" in names

    def test_ptsd_recommends_quiet_or_onyx(self, tm):
        recs = tm.get_recommended_themes({"ptsd"})
        names = [r[0] for r in recs]
        assert "onyx" in names
        assert "quiet" in names

    def test_general_condition(self, tm):
        recs = tm.get_recommended_themes({"general"})
        assert len(recs) > 0

    def test_multiple_conditions(self, tm):
        recs = tm.get_recommended_themes({"anxiety", "ptsd"})
        assert len(recs) > 0
        # Launch themes intentionally consolidate condition-specific variants.
        names = [r[0] for r in recs[:4]]
        assert any(n in names for n in ("onyx", "quiet"))

    def test_empty_conditions(self, tm):
        recs = tm.get_recommended_themes(set())
        # Should still return themes with "general" suitability
        assert len(recs) >= 1
