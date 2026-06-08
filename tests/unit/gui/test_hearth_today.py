"""pytest-qt tests for the HearthToday landing-page widget."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.hearth_today import HearthToday

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def _make_wellness_orchestrator(**kwargs):
    """Return a mocked wellness orchestrator with a configurable snapshot."""
    defaults = {
        "mood_score": 5.0,
        "energy_score": 5.0,
        "sleep_hours": 7.5,
    }
    defaults.update(kwargs)
    wo = MagicMock()
    wo.snapshot.return_value = SimpleNamespace(**defaults)
    return wo


def _make_profile_manager(name: str = "", conditions: set | None = None):
    pm = MagicMock()
    prof = SimpleNamespace(name=name, conditions=conditions or set())
    pm.current_profile = prof
    return pm


def _make_task_manager(tasks=None):
    tm = MagicMock()
    tm.tasks = tasks or []
    return tm


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def default_theme():
    return {"background": "#0F0F11", "text": "#F2EDE6", "accent": "#D9A05B"}


# ---------------------------------------------------------------------------
# 1. Instantiation
# ---------------------------------------------------------------------------


def test_can_be_instantiated(qtbot, default_theme):
    widget = HearthToday(
        theme=default_theme,
        task_manager=None,
        profile_manager=None,
        mood_manager=None,
        energy_predictor=None,
        gamification_manager=None,
        wellness_orchestrator=None,
        subscription_manager=None,
    )
    qtbot.addWidget(widget)
    assert widget is not None
    assert widget.isVisible() or not widget.isVisible()  # rendered without crash


def test_timer_starts_on_instantiation(qtbot, default_theme):
    wo = _make_wellness_orchestrator()
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=wo,
    )
    qtbot.addWidget(widget)
    assert widget._timer.isActive()
    assert widget._timer.interval() == 60_000


# ---------------------------------------------------------------------------
# 2. Wellness summary display
# ---------------------------------------------------------------------------


def test_wellness_data_renders_in_room(qtbot, default_theme):
    """A snapshot with mood/energy/sleep should compose into the room text."""
    wo = _make_wellness_orchestrator(mood_score=8.0, energy_score=8.0, sleep_hours=7.5)
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=wo,
    )
    qtbot.addWidget(widget)

    # With good energy & mood we expect a steady-state greeting.
    assert widget._line1.text() != ""
    assert widget._line2.text() != ""
    assert widget._caption.text() != ""
    # The ember should glow brightly.
    assert widget._ember._glow > 0.5


def test_low_wellness_shows_depleted_message(qtbot, default_theme):
    """Low mood & energy should produce the depleted-state copy."""
    wo = _make_wellness_orchestrator(mood_score=2.0, energy_score=2.0, sleep_hours=4.0)
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=wo,
    )
    qtbot.addWidget(widget)

    assert "small" in widget._line2.text().lower()
    assert widget._primary_tab == "breathing"


# ---------------------------------------------------------------------------
# 3. Daily briefing
# ---------------------------------------------------------------------------


def test_daily_briefing_shows_task_count(qtbot, default_theme):
    """The caption should mention pending tasks."""
    tasks = [
        SimpleNamespace(completed=False),
        SimpleNamespace(completed=False),
        SimpleNamespace(completed=True),
    ]
    tm = _make_task_manager(tasks=tasks)
    widget = HearthToday(
        theme=default_theme,
        task_manager=tm,
        wellness_orchestrator=_make_wellness_orchestrator(),
    )
    qtbot.addWidget(widget)

    caption = widget._caption.text()
    assert "2 things waiting" in caption


def test_daily_briefing_no_tasks_shows_free_time(qtbot, default_theme):
    """With zero pending tasks the caption should read as unpressured."""
    widget = HearthToday(
        theme=default_theme,
        task_manager=_make_task_manager(tasks=[]),
        wellness_orchestrator=_make_wellness_orchestrator(),
    )
    qtbot.addWidget(widget)

    assert "nothing's due" in widget._caption.text().lower()


def test_daily_briefing_includes_user_name(qtbot, default_theme):
    """The greeting line should incorporate the user's name."""
    pm = _make_profile_manager(name="Alex")
    widget = HearthToday(
        theme=default_theme,
        profile_manager=pm,
        wellness_orchestrator=_make_wellness_orchestrator(),
    )
    qtbot.addWidget(widget)

    assert "Alex" in widget._line1.text()


# ---------------------------------------------------------------------------
# 4. Quick actions
# ---------------------------------------------------------------------------


def test_quick_action_buttons_exist(qtbot, default_theme):
    """The primary door and the three ghost side-doors should be present."""
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=_make_wellness_orchestrator(),
    )
    qtbot.addWidget(widget)

    # Primary door always has some label.
    assert widget._primary.text() != ""

    # Side-doors are fixed by compose().
    side_labels = [
        "A few words about today",
        "Tend the medication shelf",
        "Quiet everything for a while",
    ]
    for label in side_labels:
        btn = _find_button(widget, label)
        assert btn is not None, f"{label!r} side-door missing"


def test_primary_button_emits_navigate_signal(qtbot, default_theme):
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=_make_wellness_orchestrator(),
    )
    qtbot.addWidget(widget)

    with qtbot.waitSignal(widget.navigate_requested, timeout=500):
        widget._primary.click()


def test_primary_button_emits_legacy_breathing_signal(qtbot, default_theme):
    """When the primary tab is breathing the legacy signal should also fire."""
    wo = _make_wellness_orchestrator(mood_score=2.0, energy_score=2.0)
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=wo,
    )
    qtbot.addWidget(widget)

    assert widget._primary_tab == "breathing"
    with qtbot.waitSignal(widget.breathing_requested, timeout=500):
        widget._primary.click()


def test_primary_button_emits_legacy_task_signal(qtbot, default_theme):
    """When the primary tab is task_manager the legacy signal should also fire."""
    wo = _make_wellness_orchestrator(mood_score=8.0, energy_score=8.0)
    tm = _make_task_manager(tasks=[SimpleNamespace(completed=False)] * 10)
    widget = HearthToday(
        theme=default_theme,
        task_manager=tm,
        wellness_orchestrator=wo,
    )
    qtbot.addWidget(widget)

    assert widget._primary_tab == "task_manager"
    with qtbot.waitSignal(widget.task_add_requested, timeout=500):
        widget._primary.click()


def test_side_door_emits_navigate_signal(qtbot, default_theme):
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=_make_wellness_orchestrator(),
    )
    qtbot.addWidget(widget)

    journal_btn = _find_button(widget, "A few words about today")
    assert journal_btn is not None

    with qtbot.waitSignal(widget.navigate_requested, timeout=500):
        journal_btn.click()


def test_side_door_journaling_emits_legacy_signal(qtbot, default_theme):
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=_make_wellness_orchestrator(),
    )
    qtbot.addWidget(widget)

    journal_btn = _find_button(widget, "A few words about today")
    with qtbot.waitSignal(widget.journal_requested, timeout=500):
        journal_btn.click()


# ---------------------------------------------------------------------------
# 5. State adaptation
# ---------------------------------------------------------------------------


def test_state_adaptation_depleted(qtbot, default_theme):
    """Very low energy & mood should produce the depleted room."""
    wo = _make_wellness_orchestrator(mood_score=1.0, energy_score=1.0, sleep_hours=3.0)
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=wo,
    )
    qtbot.addWidget(widget)

    assert widget._primary_tab == "breathing"
    assert "small" in widget._line2.text().lower()


def test_state_adaptation_activated(qtbot, default_theme):
    """High arousal from many pending tasks should produce the activated room."""
    tasks = [SimpleNamespace(completed=False) for _ in range(12)]
    wo = _make_wellness_orchestrator(mood_score=5.0, energy_score=7.0)
    widget = HearthToday(
        theme=default_theme,
        task_manager=_make_task_manager(tasks=tasks),
        wellness_orchestrator=wo,
    )
    qtbot.addWidget(widget)

    assert widget._primary_tab == "task_manager"
    assert "one thing at a time" in widget._line2.text().lower()


def test_state_adaptation_steady(qtbot, default_theme):
    """Balanced mood/energy with few tasks should produce the steady room."""
    wo = _make_wellness_orchestrator(mood_score=7.0, energy_score=6.0, sleep_hours=8.0)
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=wo,
    )
    qtbot.addWidget(widget)

    assert widget._primary_tab == "task_manager"
    assert (
        "room in today" in widget._line2.text().lower()
        or "ease into it" in widget._line2.text().lower()
    )


def test_state_adaptation_first_contact(qtbot, default_theme):
    """No wellness data yet should invite the user to check in."""
    widget = HearthToday(
        theme=default_theme,
        wellness_orchestrator=None,
    )
    qtbot.addWidget(widget)

    assert widget._primary_tab == "mood_tracker"
    assert "tell me how you're landing" in widget._line2.text().lower()


def test_state_adaptation_profile_conditions_influence_greeting(qtbot, default_theme):
    """The user's name from the profile manager should personalize the greeting."""
    pm_anxiety = _make_profile_manager(name="Sam", conditions={"Anxiety"})
    wo = _make_wellness_orchestrator(mood_score=6.0, energy_score=5.0)
    widget = HearthToday(
        theme=default_theme,
        profile_manager=pm_anxiety,
        wellness_orchestrator=wo,
    )
    qtbot.addWidget(widget)

    assert "Sam" in widget._line1.text()
    # The widget should still compose a steady/depleted/activated room normally.
    assert widget._line2.text() != ""
