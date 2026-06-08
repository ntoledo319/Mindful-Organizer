"""pytest-qt tests for the AutomationWidget ("The Hearthroom")."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QAbstractButton

from core.automation_config import ExecutionMode
from gui.widgets.automation_widget import AutomationWidget


@pytest.fixture
def fake_engine():
    """Return a lightweight automation engine stand-in."""
    engine = MagicMock()
    engine.is_enabled = False
    engine._can_execute_system_actions = False
    engine.config.active_profile.execution_mode = ExecutionMode.SUGGESTIONS_ONLY
    engine.config.active_profile_id = "default"
    engine.focus.state.name = "INACTIVE"
    engine.list_rules.return_value = [
        {"enabled": True, "in_profile": True, "name": "focus_block"},
        {"enabled": True, "in_profile": True, "name": "grounding"},
    ]
    return engine


@pytest.fixture
def fake_subscription():
    """Return a lightweight subscription manager stand-in."""
    sub = MagicMock()
    sub.current_tier = SimpleNamespace(value="free")
    sub.has_feature.return_value = False
    return sub


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot, fake_engine, fake_subscription):
    widget = AutomationWidget(
        theme={},
        automation_engine=fake_engine,
        subscription_manager=fake_subscription,
    )
    qtbot.addWidget(widget)
    assert widget is not None


def test_focus_button_exists(qtbot, fake_engine, fake_subscription):
    widget = AutomationWidget(
        theme={},
        automation_engine=fake_engine,
        subscription_manager=fake_subscription,
    )
    qtbot.addWidget(widget)

    btn = _find_button(widget, "Guard a focus block")
    assert btn is not None


def test_grounding_button_exists(qtbot, fake_engine, fake_subscription):
    widget = AutomationWidget(
        theme={},
        automation_engine=fake_engine,
        subscription_manager=fake_subscription,
    )
    qtbot.addWidget(widget)

    btn = _find_button(widget, "Help me settle")
    assert btn is not None


def test_crisis_button_exists(qtbot, fake_engine, fake_subscription):
    widget = AutomationWidget(
        theme={},
        automation_engine=fake_engine,
        subscription_manager=fake_subscription,
    )
    qtbot.addWidget(widget)

    btn = _find_button(widget, "When it's bad")
    assert btn is not None


def test_rule_list_loaded_in_feed(qtbot, fake_engine, fake_subscription):
    widget = AutomationWidget(
        theme={},
        automation_engine=fake_engine,
        subscription_manager=fake_subscription,
    )
    qtbot.addWidget(widget)

    summary = widget._watch_summary()
    assert "2" in summary
    fake_engine.list_rules.assert_called()


def test_toggle_protection_emits_signal(qtbot, fake_engine, fake_subscription):
    widget = AutomationWidget(
        theme={},
        automation_engine=fake_engine,
        subscription_manager=fake_subscription,
    )
    qtbot.addWidget(widget)

    # Start disabled; click to enable
    with qtbot.waitSignal(widget.protection_changed, timeout=1000):
        widget._on_toggle_protection()

    fake_engine.enable.assert_called()
    assert fake_engine.enable.called
