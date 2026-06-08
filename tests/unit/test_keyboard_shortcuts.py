"""Tests for keyboard shortcut management."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QWidget

from utils.keyboard_shortcuts import (
    _DEFAULT_SHORTCUTS,
    ShortcutConflict,
    ShortcutContext,
    ShortcutManager,
)


class TestShortcutManager:
    def test_instantiation_populates_defaults(self):
        sm = ShortcutManager()
        assert len(sm.get_all_actions()) == len(_DEFAULT_SHORTCUTS)

    def test_get_action(self):
        sm = ShortcutManager()
        action = sm.get_action("new_task")
        assert action is not None
        assert action.label == "New Task"

    def test_get_actions_for_context(self):
        sm = ShortcutManager()
        actions = sm.get_actions_for_context(ShortcutContext.TASKS)
        assert any(a.action_id == "new_task" for a in actions)
        assert any(a.action_id == "task_complete" for a in actions)

    def test_set_callback_and_trigger(self):
        sm = ShortcutManager()
        callback = MagicMock()
        sm.set_callback("new_task", callback)
        assert sm.trigger("new_task") is True
        callback.assert_called_once()

    def test_trigger_unknown_action(self):
        sm = ShortcutManager()
        assert sm.trigger("nonexistent") is False

    def test_trigger_disabled_action(self):
        sm = ShortcutManager()
        action = sm.get_action("new_task")
        action.enabled = False
        callback = MagicMock()
        sm.set_callback("new_task", callback)
        assert sm.trigger("new_task") is False
        callback.assert_not_called()

    def test_register_new_shortcut(self):
        sm = ShortcutManager()
        conflicts = sm.register("custom_action", "Custom", "Ctrl+Shift+X")
        assert not conflicts
        assert sm.get_action("custom_action") is not None

    def test_register_duplicate_conflict(self):
        sm = ShortcutManager()
        sm.register("action_a", "A", "Ctrl+Shift+Y")
        conflicts = sm.register("action_b", "B", "Ctrl+Shift+Y")
        assert len(conflicts) == 1
        assert isinstance(conflicts[0], ShortcutConflict)

    def test_unregister(self):
        sm = ShortcutManager()
        sm.register("temp", "Temp", "Ctrl+T")
        assert sm.get_action("temp") is not None
        sm.unregister("temp")
        assert sm.get_action("temp") is None

    def test_remap(self):
        sm = ShortcutManager()
        conflicts = sm.remap("new_task", "Ctrl+Shift+N")
        assert not conflicts
        assert sm.get_action("new_task").effective_key == "Ctrl+Shift+N"

    def test_remap_conflict(self):
        sm = ShortcutManager()
        # Force a conflict between two actions
        sm.remap("new_task", "Ctrl+M")
        conflicts = sm.remap("mood_entry", "Ctrl+M")
        assert len(conflicts) >= 1

    def test_detect_conflicts(self):
        sm = ShortcutManager()
        sm.remap("new_task", "Ctrl+M")
        sm.remap("mood_entry", "Ctrl+M")
        conflicts = sm.detect_conflicts()
        assert any(c.action_a == "new_task" and c.action_b == "mood_entry" for c in conflicts)

    def test_reset_action(self):
        sm = ShortcutManager()
        original = sm.get_action("new_task").default_key
        sm.remap("new_task", "Ctrl+Shift+N")
        sm.reset_action("new_task")
        assert sm.get_action("new_task").effective_key == original

    def test_reset_all(self):
        sm = ShortcutManager()
        sm.remap("new_task", "Ctrl+Shift+N")
        sm.remap("mood_entry", "Ctrl+Shift+M")
        sm.reset_all()
        assert sm.get_action("new_task").effective_key == sm.get_action("new_task").default_key
        assert sm.get_action("mood_entry").effective_key == sm.get_action("mood_entry").default_key

    def test_active_context(self):
        sm = ShortcutManager()
        assert sm.active_context == ShortcutContext.GLOBAL
        sm.active_context = ShortcutContext.TASKS
        assert sm.active_context == ShortcutContext.TASKS

    def test_overlay_text(self):
        sm = ShortcutManager()
        text = sm.overlay_text()
        assert "Keyboard Shortcuts" in text
        assert "New Task" in text

    def test_overlay_data(self):
        sm = ShortcutManager()
        data = sm.overlay_data()
        assert any(d["action_id"] == "new_task" for d in data)

    def test_save_and_load(self):
        sm = ShortcutManager()
        sm.remap("new_task", "Ctrl+Shift+N")
        sm.get_action("new_task").enabled = False

        db = MagicMock()
        db.get_setting.return_value = None
        sm.save(db)
        assert db.set_setting.called
        saved_json = db.set_setting.call_args[0][1]
        config = json.loads(saved_json)
        assert config["new_task"]["current_key"] == "Ctrl+Shift+N"
        assert config["new_task"]["enabled"] is False

        sm2 = ShortcutManager()
        db2 = MagicMock()
        db2.get_setting.return_value = saved_json
        sm2.load(db2)
        assert sm2.get_action("new_task").current_key == "Ctrl+Shift+N"
        assert sm2.get_action("new_task").enabled is False

    def test_save_to_file_and_load_from_file(self, tmp_path):
        sm = ShortcutManager()
        sm.remap("new_task", "Ctrl+Shift+N")
        path = sm.save_to_file(tmp_path / "shortcuts.json")
        assert path.exists()

        sm2 = ShortcutManager()
        sm2.load_from_file(path)
        assert sm2.get_action("new_task").current_key == "Ctrl+Shift+N"

    def test_load_from_file_missing(self, tmp_path):
        sm = ShortcutManager()
        with pytest.raises(FileNotFoundError):
            sm.load_from_file(tmp_path / "missing.json")

    def test_bind_to_widget(self, qtbot):
        widget = QWidget()
        qtbot.add_widget(widget)
        sm = ShortcutManager()
        sm.bind_to_widget(widget)
        assert len(sm._qt_shortcuts) > 0

    def test_unbind_all(self, qtbot):
        widget = QWidget()
        qtbot.add_widget(widget)
        sm = ShortcutManager()
        sm.bind_to_widget(widget)
        assert len(sm._qt_shortcuts) > 0
        sm.unbind_all()
        assert sm._qt_shortcuts == []

    def test_to_qt_key(self):
        import platform

        is_mac = platform.system().lower() == "darwin"
        result = ShortcutManager._to_qt_key("Ctrl+N")
        if is_mac:
            assert result == "Meta+N"
        else:
            assert result == "Ctrl+N"
