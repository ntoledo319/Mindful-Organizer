"""
Tests for the TaskManager class (src/core/task_manager.py).

Covers CRUD operations, queries, persistence, undo/redo,
recurring tasks, templates, subtasks, tags, and statistics.
"""

from datetime import date, timedelta

import pytest

try:
    from src.core.task_manager import (
        RecurrenceConfig,
        RecurrencePattern,
        SubTask,
        Task,
        TaskCategory,
        TaskManager,
        TaskPriority,
    )
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="task_manager module not available")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(**overrides):
    """Create a Task with sensible defaults, accepting overrides."""
    defaults = {
        "title": "Test task",
        "priority": TaskPriority.Medium,
        "category": TaskCategory.Personal,
        "energy_required": 5,
    }
    defaults.update(overrides)
    return Task(**defaults)


# ---------------------------------------------------------------------------
# Basic CRUD
# ---------------------------------------------------------------------------

class TestAddTask:
    """Adding tasks to the manager."""

    def test_add_task(self, tmp_data_dir):
        """A task added via add_task appears in the task list."""
        tm = TaskManager(tmp_data_dir)
        task = _make_task(title="Buy milk")
        result = tm.add_task(task)

        assert result.title == "Buy milk"
        assert len(tm.tasks) == 1
        assert tm.tasks[0].id == task.id

    def test_add_task_generates_id(self, tmp_data_dir):
        """Tasks receive a unique UUID id on creation."""
        tm = TaskManager(tmp_data_dir)
        t1 = tm.add_task(_make_task(title="A"))
        t2 = tm.add_task(_make_task(title="B"))
        assert t1.id != t2.id

    def test_add_task_sets_created_at(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task())
        assert task.created_at  # non-empty


class TestCompleteTask:
    """Completing tasks."""

    def test_complete_task_by_id(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task())
        tm.complete_task(task.id)

        assert task.completed is True
        assert task.completed_at is not None

    def test_complete_task_by_object(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task())
        tm.complete_task(task)
        assert task.completed is True

    def test_complete_nonexistent_task_returns_none(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        assert tm.complete_task("no-such-id") is None

    def test_complete_recurring_task_creates_next(self, tmp_data_dir):
        """Completing a recurring task should generate the next instance."""
        tm = TaskManager(tmp_data_dir)
        today = date.today()
        task = _make_task(
            title="Daily standup",
            due_date=today.isoformat(),
            recurrence=RecurrenceConfig(pattern=RecurrencePattern.DAILY),
        )
        tm.add_task(task)
        tm.complete_task(task.id)

        incomplete = tm.get_tasks(completed=False)
        assert len(incomplete) == 1
        assert incomplete[0].due_date == (today + timedelta(days=1)).isoformat()


class TestDeleteTask:

    def test_delete_task(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task())
        deleted = tm.delete_task(task.id)

        assert deleted is not None
        assert deleted.title == task.title
        assert len(tm.tasks) == 0

    def test_delete_nonexistent_returns_none(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        assert tm.delete_task("nope") is None


class TestUpdateTask:

    def test_update_task_fields(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task(title="Old title"))
        tm.update_task(task.id, title="New title", energy_required=9)

        updated = tm.get_task_by_id(task.id)
        assert updated.title == "New title"
        assert updated.energy_required == 9

    def test_update_nonexistent_returns_none(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        assert tm.update_task("nope", title="X") is None


# ---------------------------------------------------------------------------
# Query methods
# ---------------------------------------------------------------------------

class TestGetTasksByPriority:

    def test_get_tasks_by_priority(self, tmp_data_dir, sample_tasks):
        tm = TaskManager(tmp_data_dir)
        for t in sample_tasks:
            tm.add_task(t)

        urgent = tm.get_tasks_by_priority(TaskPriority.Urgent)
        assert all(t.priority == TaskPriority.Urgent for t in urgent)
        assert len(urgent) == 1

    def test_empty_priority_returns_empty(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        assert tm.get_tasks_by_priority(TaskPriority.Urgent) == []


class TestGetTasksByCategory:

    def test_get_tasks_by_category(self, tmp_data_dir, sample_tasks):
        tm = TaskManager(tmp_data_dir)
        for t in sample_tasks:
            tm.add_task(t)

        work = tm.get_tasks_by_category(TaskCategory.Work)
        assert all(t.category == TaskCategory.Work for t in work)
        assert len(work) >= 1


class TestGetTasksByEnergy:

    def test_get_tasks_by_energy(self, tmp_data_dir, sample_tasks):
        tm = TaskManager(tmp_data_dir)
        for t in sample_tasks:
            tm.add_task(t)

        low_energy = tm.get_tasks_by_energy(4)
        assert all(t.energy_required <= 4 for t in low_energy)

    def test_max_energy_zero_returns_empty(self, tmp_data_dir, sample_tasks):
        tm = TaskManager(tmp_data_dir)
        for t in sample_tasks:
            tm.add_task(t)
        assert tm.get_tasks_by_energy(0) == []


class TestGetTasksByTag:

    def test_get_tasks_by_tag(self, tmp_data_dir, sample_tasks):
        tm = TaskManager(tmp_data_dir)
        for t in sample_tasks:
            tm.add_task(t)

        work_tagged = tm.get_tasks_by_tag("work")
        assert len(work_tagged) >= 1
        assert all("work" in t.tags for t in work_tagged)


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

class TestTaskPersistence:

    def test_task_persistence(self, tmp_data_dir):
        """Tasks survive manager reload."""
        tm1 = TaskManager(tmp_data_dir)
        tm1.add_task(_make_task(title="Persistent task", energy_required=7))
        del tm1

        tm2 = TaskManager(tmp_data_dir)
        assert len(tm2.tasks) == 1
        assert tm2.tasks[0].title == "Persistent task"
        assert tm2.tasks[0].energy_required == 7

    def test_persistence_preserves_all_fields(self, tmp_data_dir):
        tm1 = TaskManager(tmp_data_dir)
        task = _make_task(
            title="Full task",
            priority=TaskPriority.High,
            category=TaskCategory.Health,
            energy_required=8,
            due_date=date.today().isoformat(),
            notes="Important notes",
            tags={"health", "important"},
            estimated_duration=45,
        )
        tm1.add_task(task)
        task_id = task.id
        del tm1

        tm2 = TaskManager(tmp_data_dir)
        loaded = tm2.get_task_by_id(task_id)
        assert loaded is not None
        assert loaded.priority == TaskPriority.High
        assert loaded.category == TaskCategory.Health
        assert loaded.notes == "Important notes"
        assert loaded.estimated_duration == 45
        assert "health" in loaded.tags

    def test_completed_task_persists(self, tmp_data_dir):
        tm1 = TaskManager(tmp_data_dir)
        task = tm1.add_task(_make_task())
        tm1.complete_task(task.id)
        del tm1

        tm2 = TaskManager(tmp_data_dir)
        assert tm2.tasks[0].completed is True


class TestEmptyTaskList:

    def test_empty_task_list(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        assert tm.tasks == []
        assert tm.get_tasks(completed=False) == []
        assert tm.get_tasks(completed=True) == []

    def test_statistics_on_empty(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        stats = tm.get_statistics()
        assert stats["total_tasks"] == 0
        assert stats["completion_rate"] == 0.0


# ---------------------------------------------------------------------------
# Undo / Redo
# ---------------------------------------------------------------------------

class TestUndoRedo:

    def test_undo_add(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        tm.add_task(_make_task(title="Undo me"))
        assert len(tm.tasks) == 1

        desc = tm.undo_manager.undo()
        assert desc is not None
        assert len(tm.tasks) == 0

    def test_redo_add(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        tm.add_task(_make_task(title="Redo me"))
        tm.undo_manager.undo()
        assert len(tm.tasks) == 0

        tm.undo_manager.redo()
        assert len(tm.tasks) == 1

    def test_undo_complete(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task())
        tm.complete_task(task.id)
        assert task.completed is True

        tm.undo_manager.undo()
        reloaded = tm.get_task_by_id(task.id)
        assert reloaded.completed is False

    def test_undo_delete(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task(title="Delete and restore"))
        tm.delete_task(task.id)
        assert len(tm.tasks) == 0

        tm.undo_manager.undo()
        assert len(tm.tasks) == 1

    def test_can_undo_property(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        assert tm.undo_manager.can_undo is False
        tm.add_task(_make_task())
        assert tm.undo_manager.can_undo is True


# ---------------------------------------------------------------------------
# Subtasks
# ---------------------------------------------------------------------------

class TestSubtasks:

    def test_complete_subtask(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = _make_task(subtasks=[SubTask(title="Step 1"), SubTask(title="Step 2")])
        tm.add_task(task)

        result = tm.complete_subtask(task.id, 0)
        assert result is not None
        assert result.completed is True
        assert result.completed_at is not None

    def test_complete_subtask_invalid_index(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task())
        assert tm.complete_subtask(task.id, 99) is None


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

class TestTemplates:

    def test_save_and_create_from_template(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task(title="Template source", energy_required=7))
        tm.save_as_template(task.id, "my_template")

        assert "my_template" in tm.list_templates()

        new_task = tm.create_from_template("my_template")
        assert new_task is not None
        assert new_task.title == "Template source"
        assert new_task.energy_required == 7
        assert new_task.id != task.id

    def test_delete_template(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        task = tm.add_task(_make_task())
        tm.save_as_template(task.id, "to_delete")
        assert tm.delete_template("to_delete") is True
        assert "to_delete" not in tm.list_templates()

    def test_create_from_nonexistent_template(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        assert tm.create_from_template("nonexistent") is None


# ---------------------------------------------------------------------------
# Custom categories
# ---------------------------------------------------------------------------

class TestCustomCategories:

    def test_add_custom_category(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        tm.add_custom_category("Gardening")
        assert "Gardening" in tm.get_all_categories()

    def test_remove_custom_category(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        tm.add_custom_category("Temporary")
        assert tm.remove_custom_category("Temporary") is True
        assert "Temporary" not in tm.custom_categories

    def test_remove_nonexistent_category(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        assert tm.remove_custom_category("nope") is False


# ---------------------------------------------------------------------------
# Sorting and search
# ---------------------------------------------------------------------------

class TestSortingAndSearch:

    def test_sort_by_priority(self, tmp_data_dir, sample_tasks):
        tm = TaskManager(tmp_data_dir)
        for t in sample_tasks:
            tm.add_task(t)

        sorted_tasks = tm.sort_by_priority()
        priorities = [t.priority.value for t in sorted_tasks]
        assert priorities == sorted(priorities, reverse=True)

    def test_sort_by_energy(self, tmp_data_dir, sample_tasks):
        tm = TaskManager(tmp_data_dir)
        for t in sample_tasks:
            tm.add_task(t)

        sorted_tasks = tm.sort_by_energy()
        energies = [t.energy_required for t in sorted_tasks]
        assert energies == sorted(energies)

    def test_search_by_title(self, tmp_data_dir, sample_tasks):
        tm = TaskManager(tmp_data_dir)
        for t in sample_tasks:
            tm.add_task(t)

        results = tm.search("report")
        assert any("report" in t.title.lower() for t in results)

    def test_search_no_match(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        tm.add_task(_make_task(title="Hello"))
        assert tm.search("zzzzzzz") == []


# ---------------------------------------------------------------------------
# Batch operations
# ---------------------------------------------------------------------------

class TestBatchOperations:

    def test_batch_complete(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        ids = []
        for i in range(3):
            t = tm.add_task(_make_task(title=f"Task {i}"))
            ids.append(t.id)

        completed = tm.batch_complete(ids)
        assert len(completed) == 3
        assert all(t.completed for t in tm.tasks)

    def test_batch_delete(self, tmp_data_dir):
        tm = TaskManager(tmp_data_dir)
        ids = [tm.add_task(_make_task(title=f"Del {i}")).id for i in range(3)]

        deleted = tm.batch_delete(ids)
        assert len(deleted) == 3
        assert len(tm.tasks) == 0


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

class TestStatistics:

    def test_statistics(self, tmp_data_dir, sample_tasks):
        tm = TaskManager(tmp_data_dir)
        for t in sample_tasks:
            tm.add_task(t)

        tm.complete_task(sample_tasks[0].id)
        stats = tm.get_statistics()

        assert stats["total_tasks"] == 5
        assert stats["completed_tasks"] == 1
        assert stats["incomplete_tasks"] == 4
        assert stats["completion_rate"] == 20.0


# ---------------------------------------------------------------------------
# Task serialization edge cases
# ---------------------------------------------------------------------------

class TestTaskSerialization:

    def test_from_dict_legacy_priority_string(self):
        data = {"title": "Legacy", "priority": "High", "category": "Work", "energy_required": 5}
        task = Task.from_dict(data)
        assert task.priority == TaskPriority.High

    def test_from_dict_legacy_priority_int(self):
        data = {"title": "Legacy", "priority": 3, "category": "Work", "energy_required": 5}
        task = Task.from_dict(data)
        assert task.priority == TaskPriority.High

    def test_from_dict_invalid_priority_defaults_medium(self):
        data = {"title": "Bad", "priority": 999, "category": "Work", "energy_required": 5}
        task = Task.from_dict(data)
        assert task.priority == TaskPriority.Medium

    def test_from_dict_invalid_category_defaults_other(self):
        data = {"title": "Bad", "priority": 2, "category": "NonExistent", "energy_required": 5}
        task = Task.from_dict(data)
        assert task.category == TaskCategory.Other

    def test_round_trip_serialization(self):
        task = _make_task(
            title="Round trip",
            tags={"a", "b"},
            subtasks=[SubTask(title="Step 1")],
            recurrence=RecurrenceConfig(pattern=RecurrencePattern.WEEKLY),
        )
        d = task.to_dict()
        restored = Task.from_dict(d)
        assert restored.title == task.title
        assert restored.tags == task.tags
        assert len(restored.subtasks) == 1
        assert restored.recurrence.pattern == RecurrencePattern.WEEKLY


# ---------------------------------------------------------------------------
# RecurrenceConfig
# ---------------------------------------------------------------------------

class TestRecurrence:

    def test_daily_next_due(self):
        config = RecurrenceConfig(pattern=RecurrencePattern.DAILY)
        today = date(2026, 1, 15)
        assert config.next_due_date(today) == date(2026, 1, 16)

    def test_weekly_next_due(self):
        config = RecurrenceConfig(pattern=RecurrencePattern.WEEKLY)
        today = date(2026, 1, 15)
        assert config.next_due_date(today) == date(2026, 1, 22)

    def test_monthly_next_due(self):
        config = RecurrenceConfig(pattern=RecurrencePattern.MONTHLY)
        today = date(2026, 1, 15)
        assert config.next_due_date(today) == date(2026, 2, 15)

    def test_recurrence_with_end_date(self):
        config = RecurrenceConfig(
            pattern=RecurrencePattern.DAILY,
            end_date="2026-01-16",
        )
        assert config.next_due_date(date(2026, 1, 16)) is None

    def test_custom_days(self):
        config = RecurrenceConfig(
            pattern=RecurrencePattern.CUSTOM_DAYS,
            custom_days=[0, 2, 4],  # Mon, Wed, Fri
        )
        # date(2026, 1, 12) is a Monday (weekday 0)
        result = config.next_due_date(date(2026, 1, 12))
        assert result == date(2026, 1, 14)  # Wednesday
