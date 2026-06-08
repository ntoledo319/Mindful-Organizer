"""pytest-qt tests for the SettingsWidget."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtWidgets import QComboBox, QGroupBox, QSlider

from gui.widgets.settings_widget import SettingsWidget


@pytest.fixture
def fake_main_window(tmp_path):
    """Return a lightweight stand-in for the main window."""
    mw = MagicMock()

    # Theme manager
    tm = MagicMock()
    tm.current_theme_name = "ember"
    tm.font_scale = 1.0
    tm.color_blind_mode = None
    tm.reduced_motion = False
    tm.dyslexia_font = False
    tm.get_theme_names.return_value = [
        ("ember", "Ember", "Warm dark default"),
        ("linen", "Linen", "Light warm"),
    ]
    tm.generate_stylesheet.return_value = ""
    mw.theme_manager = tm

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
    mw.save_settings.return_value = None
    mw.change_theme.return_value = None

    return mw


def test_can_be_instantiated(qtbot, fake_main_window):
    widget = SettingsWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)
    assert widget is not None


def test_settings_sections_exist(qtbot, fake_main_window):
    widget = SettingsWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    group_boxes = widget.findChildren(QGroupBox)
    titles = {gb.title() for gb in group_boxes}
    assert "Profile" in titles
    assert "Subscription" in titles
    assert "Theme" in titles
    assert "Accessibility" in titles
    assert "Notifications" in titles
    assert "Data" in titles
    assert "About" in titles


def test_theme_combo_populated(qtbot, fake_main_window):
    widget = SettingsWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    combo = widget._theme_combo
    assert combo.count() >= 1
    assert combo.itemData(0) is not None


def test_accessibility_controls_exist(qtbot, fake_main_window):
    widget = SettingsWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    assert widget._font_slider is not None
    assert isinstance(widget._font_slider, QSlider)
    assert widget._cb_combo is not None
    assert isinstance(widget._cb_combo, QComboBox)


def test_save_settings_emits_signal(qtbot, fake_main_window):
    widget = SettingsWidget(main_window=fake_main_window)
    qtbot.addWidget(widget)

    # Prevent QMessageBox from blocking the test
    with (
        patch("gui.widgets.settings_widget.QMessageBox"),
        qtbot.waitSignal(widget.settings_changed, timeout=1000),
    ):
        widget._save_settings()
