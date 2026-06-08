"""pytest-qt tests for the DashboardWidget Today overview."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.dashboard import DashboardWidget


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_displays_wellness_summary(qtbot):
    briefing = SimpleNamespace(
        energy_forecast="Gentle morning — 62/100",
        task_recommendations=[
            {"title": "Reply to messages", "energy_required": 2},
        ],
        suggested_skill="TIPP",
    )

    wellness = MagicMock()
    wellness.daily_briefing.return_value = briefing
    wellness.detect_crisis_signals.return_value = [
        SimpleNamespace(
            description="Low mood streak",
            recommendation="Reach out to someone you trust.",
        )
    ]

    profile = SimpleNamespace(name="Alex", conditions=set())
    pm = MagicMock()
    pm.current_profile = profile

    widget = DashboardWidget(
        theme={"background": "#0F0F11", "text": "#F2EDE6"},
        task_manager=None,
        profile_manager=pm,
        mood_manager=None,
        energy_predictor=None,
        gamification_manager=None,
        wellness_orchestrator=wellness,
        subscription_manager=None,
    )
    qtbot.addWidget(widget)

    assert not widget._briefing_card.isHidden()
    assert "Gentle morning" in widget._briefing_energy.text()
    assert not widget._crisis_banner.isHidden()
    assert "Low mood streak" in widget._crisis_label.text()


def test_quick_action_buttons_exist(qtbot):
    widget = DashboardWidget(
        theme={"background": "#0F0F11", "text": "#F2EDE6"},
        task_manager=None,
        profile_manager=None,
        mood_manager=None,
        energy_predictor=None,
        gamification_manager=None,
        wellness_orchestrator=None,
        subscription_manager=None,
    )
    qtbot.addWidget(widget)

    actions = ["Record mood", "Add task", "Breathe", "Write", "Review"]
    for label in actions:
        btn = _find_button(widget, label)
        assert btn is not None, f"{label} button missing"

    with qtbot.waitSignal(widget.mood_track_requested, timeout=500):
        _find_button(widget, "Record mood").click()

    with qtbot.waitSignal(widget.task_add_requested, timeout=500):
        _find_button(widget, "Add task").click()

    with qtbot.waitSignal(widget.breathing_requested, timeout=500):
        _find_button(widget, "Breathe").click()

    with qtbot.waitSignal(widget.journal_requested, timeout=500):
        _find_button(widget, "Write").click()

    with qtbot.waitSignal(widget.stats_requested, timeout=500):
        _find_button(widget, "Review").click()


def test_theme_application(qtbot):
    theme = {"background": "#0F0F11", "text": "#F2EDE6"}
    widget = DashboardWidget(
        theme=theme,
        task_manager=None,
        profile_manager=None,
        mood_manager=None,
        energy_predictor=None,
        gamification_manager=None,
        wellness_orchestrator=None,
        subscription_manager=None,
    )
    qtbot.addWidget(widget)

    new_theme = {"background": "#FFFFFF", "text": "#000000"}
    widget.apply_theme(new_theme)

    assert widget._theme == new_theme
    assert "#000000" in widget._welcome_label.styleSheet()
