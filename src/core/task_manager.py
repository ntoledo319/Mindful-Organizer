"""
Task management system for organizing and prioritizing tasks.
Supports recurring tasks, subtasks, dependencies, templates, undo/redo,
tags, values alignment, and comprehensive statistics.
"""
import json
import uuid
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class TaskPriority(Enum):
    """Priority levels for tasks."""
    Low = 1
    Medium = 2
    High = 3
    Urgent = 4


class TaskCategory(Enum):
    """Built-in categories for tasks."""
    Work = "Work"
    Personal = "Personal"
    Health = "Health"
    Learning = "Learning"
    Social = "Social"
    Errands = "Errands"
    Other = "Other"


class RecurrencePattern(Enum):
    """Recurrence patterns for recurring tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM_DAYS = "custom_days"


@dataclass
class SubTask:
    """A subtask belonging to a parent task."""
    title: str
    completed: bool = False
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize subtask to dictionary."""
        return {
            "title": self.title,
            "completed": self.completed,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SubTask":
        """Deserialize subtask from dictionary."""
        return cls(
            title=data["title"],
            completed=data.get("completed", False),
            completed_at=data.get("completed_at"),
        )


@dataclass
class RecurrenceConfig:
    """Configuration for recurring tasks."""
    pattern: RecurrencePattern
    custom_days: list[int] | None = None  # 0=Mon..6=Sun for CUSTOM_DAYS
    end_date: str | None = None  # ISO date string or None for no end

    def to_dict(self) -> dict[str, Any]:
        """Serialize recurrence configuration to dictionary."""
        return {
            "pattern": self.pattern.value,
            "custom_days": self.custom_days,
            "end_date": self.end_date,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecurrenceConfig":
        """Deserialize recurrence configuration from dictionary."""
        return cls(
            pattern=RecurrencePattern(data["pattern"]),
            custom_days=data.get("custom_days"),
            end_date=data.get("end_date"),
        )

    def next_due_date(self, current_due: date) -> date | None:
        """Calculate the next due date from the current one."""
        if self.end_date:
            end = date.fromisoformat(self.end_date)
            if current_due >= end:
                return None

        if self.pattern == RecurrencePattern.DAILY:
            return current_due + timedelta(days=1)
        elif self.pattern == RecurrencePattern.WEEKLY:
            return current_due + timedelta(weeks=1)
        elif self.pattern == RecurrencePattern.BIWEEKLY:
            return current_due + timedelta(weeks=2)
        elif self.pattern == RecurrencePattern.MONTHLY:
            month = current_due.month % 12 + 1
            year = current_due.year + (1 if current_due.month == 12 else 0)
            day = min(current_due.day, 28)
            return date(year, month, day)
        elif self.pattern == RecurrencePattern.CUSTOM_DAYS:
            if not self.custom_days:
                return None
            current_weekday = current_due.weekday()
            sorted_days = sorted(self.custom_days)
            for d in sorted_days:
                if d > current_weekday:
                    return current_due + timedelta(days=d - current_weekday)
            # Wrap around to next week
            return current_due + timedelta(days=7 - current_weekday + sorted_days[0])
        return None


@dataclass
class Task:
    """A task with full metadata."""
    title: str
    priority: TaskPriority
    category: TaskCategory
    energy_required: int
    id: str = ""
    due_date: str | None = None
    completed: bool = False
    notes: str | None = None
    created_at: str = ""
    completed_at: str | None = None
    subtasks: list[SubTask] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)
    custom_category: str | None = None
    recurrence: RecurrenceConfig | None = None
    blocked_by: list[str] = field(default_factory=list)
    estimated_duration: int | None = None  # minutes
    actual_duration: int | None = None  # minutes
    values_alignment: str | None = None  # ACT therapy personal value
    reminder: str | None = None  # ISO datetime string

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if isinstance(self.tags, list):
            self.tags = set(self.tags)

    def to_dict(self) -> dict[str, Any]:
        """Serialize task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority.value if isinstance(self.priority, TaskPriority) else self.priority,
            "category": self.category.value if isinstance(self.category, TaskCategory) else self.category,
            "energy_required": self.energy_required,
            "due_date": self.due_date,
            "completed": self.completed,
            "notes": self.notes,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "tags": list(self.tags),
            "custom_category": self.custom_category,
            "recurrence": self.recurrence.to_dict() if self.recurrence else None,
            "blocked_by": self.blocked_by,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "values_alignment": self.values_alignment,
            "reminder": self.reminder,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Deserialize task from dictionary, handling legacy formats."""
        # Handle priority
        priority_val = data.get("priority", 2)
        if isinstance(priority_val, str):
            try:
                priority = TaskPriority[priority_val]
            except KeyError:
                priority = TaskPriority.Medium
        elif isinstance(priority_val, int):
            try:
                priority = TaskPriority(priority_val)
            except ValueError:
                priority = TaskPriority.Medium
        else:
            priority = priority_val if isinstance(priority_val, TaskPriority) else TaskPriority.Medium

        # Handle category
        cat_val = data.get("category", "Other")
        if isinstance(cat_val, str):
            try:
                category = TaskCategory(cat_val)
            except ValueError:
                category = TaskCategory.Other
        else:
            category = cat_val if isinstance(cat_val, TaskCategory) else TaskCategory.Other

        # Handle subtasks
        subtasks_data = data.get("subtasks", [])
        subtasks = [SubTask.from_dict(s) if isinstance(s, dict) else s for s in subtasks_data]

        # Handle recurrence
        recurrence_data = data.get("recurrence")
        recurrence = RecurrenceConfig.from_dict(recurrence_data) if recurrence_data else None

        # Handle tags
        tags_data = data.get("tags", [])
        tags = set(tags_data) if isinstance(tags_data, list) else set()

        # Handle due_date - convert date objects to string
        due_date = data.get("due_date")
        if isinstance(due_date, date) and not isinstance(due_date, datetime):
            due_date = due_date.isoformat()
        elif isinstance(due_date, datetime):
            due_date = due_date.date().isoformat()

        # Handle created_at/completed_at
        created_at = data.get("created_at", "")
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        elif not created_at:
            created_at = datetime.now().isoformat()

        completed_at = data.get("completed_at")
        if isinstance(completed_at, datetime):
            completed_at = completed_at.isoformat()

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            priority=priority,
            category=category,
            energy_required=data.get("energy_required", 5),
            due_date=due_date,
            completed=data.get("completed", False),
            notes=data.get("notes"),
            created_at=created_at,
            completed_at=completed_at,
            subtasks=subtasks,
            tags=tags,
            custom_category=data.get("custom_category"),
            recurrence=recurrence,
            blocked_by=data.get("blocked_by", []),
            estimated_duration=data.get("estimated_duration"),
            actual_duration=data.get("actual_duration"),
            values_alignment=data.get("values_alignment"),
            reminder=data.get("reminder"),
        )


@dataclass
class TaskTemplate:
    """A reusable task template."""
    name: str
    title: str
    priority: int
    category: str
    energy_required: int
    tags: list[str] = field(default_factory=list)
    subtasks: list[dict[str, Any]] = field(default_factory=list)
    estimated_duration: int | None = None
    values_alignment: str | None = None
    custom_category: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize template to dictionary."""
        return {
            "name": self.name,
            "title": self.title,
            "priority": self.priority,
            "category": self.category,
            "energy_required": self.energy_required,
            "tags": self.tags,
            "subtasks": self.subtasks,
            "estimated_duration": self.estimated_duration,
            "values_alignment": self.values_alignment,
            "custom_category": self.custom_category,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskTemplate":
        """Deserialize template from dictionary."""
        return cls(**data)

    def create_task(self) -> Task:
        """Create a new Task from this template."""
        subtasks = [SubTask.from_dict(s) for s in self.subtasks]
        try:
            priority = TaskPriority(self.priority)
        except ValueError:
            priority = TaskPriority.Medium
        try:
            category = TaskCategory(self.category)
        except ValueError:
            category = TaskCategory.Other

        return Task(
            title=self.title,
            priority=priority,
            category=category,
            energy_required=self.energy_required,
            tags=set(self.tags),
            subtasks=subtasks,
            estimated_duration=self.estimated_duration,
            values_alignment=self.values_alignment,
            custom_category=self.custom_category,
            notes=self.notes,
        )


class UndoAction:
    """Represents a single undoable action."""

    def __init__(self, description: str, undo_fn: Callable[[], None], redo_fn: Callable[[], None]):
        self.description = description
        self.undo_fn = undo_fn
        self.redo_fn = redo_fn
        self.timestamp = datetime.now().isoformat()


class UndoManager:
    """Manages undo/redo history for task operations."""

    def __init__(self, max_history: int = 50):
        self._undo_stack: list[UndoAction] = []
        self._redo_stack: list[UndoAction] = []
        self.max_history = max_history

    def push(self, action: UndoAction) -> None:
        """Record a new action. Clears redo stack."""
        self._undo_stack.append(action)
        if len(self._undo_stack) > self.max_history:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> str | None:
        """Undo the last action. Returns description or None."""
        if not self._undo_stack:
            return None
        action = self._undo_stack.pop()
        action.undo_fn()
        self._redo_stack.append(action)
        return action.description

    def redo(self) -> str | None:
        """Redo the last undone action. Returns description or None."""
        if not self._redo_stack:
            return None
        action = self._redo_stack.pop()
        action.redo_fn()
        self._undo_stack.append(action)
        return action.description

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    @property
    def undo_description(self) -> str | None:
        """Description of the action that would be undone."""
        return self._undo_stack[-1].description if self._undo_stack else None

    @property
    def redo_description(self) -> str | None:
        """Description of the action that would be redone."""
        return self._redo_stack[-1].description if self._redo_stack else None


class TaskManager:
    """Manages tasks with persistence, undo/redo, templates, and statistics."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = data_dir / "tasks.json"
        self.templates_file = data_dir / "task_templates.json"
        self.custom_categories_file = data_dir / "custom_categories.json"
        self.tasks: list[Task] = []
        self.templates: dict[str, TaskTemplate] = {}
        self.custom_categories: list[str] = []
        self.undo_manager = UndoManager()
        self._load_tasks()
        self._load_templates()
        self._load_custom_categories()

    # ── Persistence ───────────────────────────────────────────────

    def _load_tasks(self) -> None:
        """Load tasks from JSON file, migrating legacy format if needed."""
        if not self.tasks_file.exists():
            self.tasks = []
            return
        with open(self.tasks_file) as f:
            tasks_data = json.load(f)
        self.tasks = [Task.from_dict(t) for t in tasks_data]

    def _save_tasks(self) -> None:
        """Persist tasks to JSON."""
        with open(self.tasks_file, "w") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2, default=str)

    def _load_templates(self) -> None:
        """Load task templates."""
        if not self.templates_file.exists():
            self.templates = {}
            return
        with open(self.templates_file) as f:
            data = json.load(f)
        self.templates = {k: TaskTemplate.from_dict(v) for k, v in data.items()}

    def _save_templates(self) -> None:
        """Persist templates to JSON."""
        with open(self.templates_file, "w") as f:
            json.dump({k: v.to_dict() for k, v in self.templates.items()}, f, indent=2)

    def _load_custom_categories(self) -> None:
        """Load user-defined custom categories."""
        if not self.custom_categories_file.exists():
            self.custom_categories = []
            return
        with open(self.custom_categories_file) as f:
            self.custom_categories = json.load(f)

    def _save_custom_categories(self) -> None:
        """Persist custom categories to JSON."""
        with open(self.custom_categories_file, "w") as f:
            json.dump(self.custom_categories, f, indent=2)

    # ── Custom Categories ─────────────────────────────────────────

    def add_custom_category(self, name: str) -> None:
        """Add a user-defined category."""
        if name not in self.custom_categories:
            self.custom_categories.append(name)
            self._save_custom_categories()

    def remove_custom_category(self, name: str) -> bool:
        """Remove a custom category. Returns True if it existed."""
        if name in self.custom_categories:
            self.custom_categories.remove(name)
            self._save_custom_categories()
            return True
        return False

    def get_all_categories(self) -> list[str]:
        """Return built-in category values plus custom categories."""
        built_in = [c.value for c in TaskCategory]
        return built_in + self.custom_categories

    # ── CRUD Operations ───────────────────────────────────────────

    def add_task(self, task: Task) -> Task:
        """Add a task with undo support."""
        self.tasks.append(task)
        self._save_tasks()

        # Emit state change
        try:
            from core.state_bus import get_state_bus
            bus = get_state_bus()
            bus.emit_task_changed("added", task_id=task.id, title=task.title)
        except RuntimeError:
            pass

        task_copy = deepcopy(task)

        def undo():
            self.tasks = [t for t in self.tasks if t.id != task_copy.id]
            self._save_tasks()

        def redo():
            self.tasks.append(deepcopy(task_copy))
            self._save_tasks()

        self.undo_manager.push(UndoAction(f"Add task: {task.title}", undo, redo))
        return task

    def delete_task(self, task_id: str) -> Task | None:
        """Delete a task by ID with undo support."""
        task = self.get_task_by_id(task_id)
        if task is None:
            return None
        task_copy = deepcopy(task)
        idx = next(i for i, t in enumerate(self.tasks) if t.id == task_id)
        self.tasks.pop(idx)
        self._save_tasks()

        def undo():
            self.tasks.insert(idx, deepcopy(task_copy))
            self._save_tasks()

        def redo():
            self.tasks = [t for t in self.tasks if t.id != task_copy.id]
            self._save_tasks()

        self.undo_manager.push(UndoAction(f"Delete task: {task_copy.title}", undo, redo))
        return task_copy

    def update_task(self, task_id: str, **kwargs: Any) -> Task | None:
        """Update task fields by ID with undo support."""
        task = self.get_task_by_id(task_id)
        if task is None:
            return None
        old_values: dict[str, Any] = {}
        for key, value in kwargs.items():
            if hasattr(task, key):
                old_values[key] = deepcopy(getattr(task, key))
                setattr(task, key, value)
        self._save_tasks()

        def undo():
            t = self.get_task_by_id(task_id)
            if t:
                for key, val in old_values.items():
                    setattr(t, key, val)
                self._save_tasks()

        def redo():
            t = self.get_task_by_id(task_id)
            if t:
                for key, val in kwargs.items():
                    if hasattr(t, key):
                        setattr(t, key, val)
                self._save_tasks()

        self.undo_manager.push(UndoAction(f"Update task: {task.title}", undo, redo))
        return task

    def complete_task(self, task_or_id: Any) -> Task | None:
        """Mark a task as completed. Accepts a Task object or task ID string."""
        task = self.get_task_by_id(task_or_id) if isinstance(task_or_id, str) else task_or_id

        if task is None:
            return None

        old_completed = task.completed
        old_completed_at = task.completed_at
        task.completed = True
        task.completed_at = datetime.now().isoformat()
        self._save_tasks()

        # Emit state change
        try:
            from core.state_bus import get_state_bus
            bus = get_state_bus()
            bus.emit_task_changed("completed", task_id=task.id, title=task.title)
        except RuntimeError:
            pass

        task_id = task.id

        def undo():
            t = self.get_task_by_id(task_id)
            if t:
                t.completed = old_completed
                t.completed_at = old_completed_at
                self._save_tasks()

        def redo():
            t = self.get_task_by_id(task_id)
            if t:
                t.completed = True
                t.completed_at = datetime.now().isoformat()
                self._save_tasks()

        self.undo_manager.push(UndoAction(f"Complete task: {task.title}", undo, redo))

        # Handle recurring task generation
        if task.recurrence and task.due_date:
            self._generate_next_recurring(task)

        return task

    def _generate_next_recurring(self, completed_task: Task) -> Task | None:
        """Create the next instance of a recurring task."""
        if completed_task.due_date is None or completed_task.recurrence is None:
            return None
        current_due = date.fromisoformat(completed_task.due_date)
        next_due = completed_task.recurrence.next_due_date(current_due)
        if next_due is None:
            return None

        new_task = Task(
            title=completed_task.title,
            priority=completed_task.priority,
            category=completed_task.category,
            energy_required=completed_task.energy_required,
            due_date=next_due.isoformat(),
            notes=completed_task.notes,
            subtasks=[SubTask(title=s.title) for s in completed_task.subtasks],
            tags=set(completed_task.tags),
            custom_category=completed_task.custom_category,
            recurrence=deepcopy(completed_task.recurrence),
            blocked_by=[],
            estimated_duration=completed_task.estimated_duration,
            values_alignment=completed_task.values_alignment,
            reminder=None,
        )
        self.tasks.append(new_task)
        self._save_tasks()
        return new_task

    def complete_subtask(self, task_id: str, subtask_index: int) -> SubTask | None:
        """Complete a subtask by index within a task."""
        task = self.get_task_by_id(task_id)
        if task is None or subtask_index >= len(task.subtasks):
            return None
        subtask = task.subtasks[subtask_index]
        subtask.completed = True
        subtask.completed_at = datetime.now().isoformat()
        self._save_tasks()
        return subtask

    def get_task_by_id(self, task_id: str) -> Task | None:
        """Find a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    # ── Query Methods ─────────────────────────────────────────────

    def get_tasks(self, completed: bool = False) -> list[Task]:
        """Get tasks filtered by completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def get_tasks_by_priority(self, priority: TaskPriority) -> list[Task]:
        """Get incomplete tasks of a given priority."""
        return [t for t in self.tasks if t.priority == priority and not t.completed]

    def get_tasks_by_category(self, category: TaskCategory) -> list[Task]:
        """Get incomplete tasks of a given category."""
        return [t for t in self.tasks if t.category == category and not t.completed]

    def get_tasks_by_custom_category(self, custom_category: str) -> list[Task]:
        """Get incomplete tasks with a specific custom category."""
        return [t for t in self.tasks if t.custom_category == custom_category and not t.completed]

    def get_tasks_by_energy(self, max_energy: int) -> list[Task]:
        """Get incomplete tasks requiring at most the given energy level."""
        return [t for t in self.tasks if t.energy_required <= max_energy and not t.completed]

    def get_tasks_by_tag(self, tag: str) -> list[Task]:
        """Get incomplete tasks containing a specific tag."""
        return [t for t in self.tasks if tag in t.tags and not t.completed]

    def get_tasks_by_value(self, value: str) -> list[Task]:
        """Get tasks aligned with a specific personal value (ACT therapy)."""
        return [t for t in self.tasks if t.values_alignment == value and not t.completed]

    def get_blocked_tasks(self) -> list[Task]:
        """Get tasks that are currently blocked by unfinished dependencies."""
        completed_ids = {t.id for t in self.tasks if t.completed}
        blocked = []
        for t in self.tasks:
            if not t.completed and t.blocked_by and not all(dep_id in completed_ids for dep_id in t.blocked_by):
                blocked.append(t)
        return blocked

    def get_unblocked_tasks(self) -> list[Task]:
        """Get incomplete tasks that are not blocked."""
        completed_ids = {t.id for t in self.tasks if t.completed}
        unblocked = []
        for t in self.tasks:
            if not t.completed and (not t.blocked_by or all(dep_id in completed_ids for dep_id in t.blocked_by)):
                unblocked.append(t)
        return unblocked

    def get_overdue_tasks(self) -> list[Task]:
        """Get incomplete tasks past their due date."""
        today_str = date.today().isoformat()
        return [
            t for t in self.tasks
            if not t.completed and t.due_date and t.due_date < today_str
        ]

    def get_upcoming_reminders(self, within_minutes: int = 60) -> list[Task]:
        """Get tasks with reminders due within the given time window."""
        now = datetime.now()
        cutoff = now + timedelta(minutes=within_minutes)
        results = []
        for t in self.tasks:
            if not t.completed and t.reminder:
                try:
                    reminder_dt = datetime.fromisoformat(t.reminder)
                    if now <= reminder_dt <= cutoff:
                        results.append(t)
                except ValueError:
                    continue
        return results

    # ── Sorting ───────────────────────────────────────────────────

    def sort_by_priority(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by priority (Urgent first)."""
        target = tasks if tasks is not None else self.get_tasks(completed=False)
        return sorted(target, key=lambda t: t.priority.value, reverse=True)

    def sort_by_energy(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by energy required (lowest first)."""
        target = tasks if tasks is not None else self.get_tasks(completed=False)
        return sorted(target, key=lambda t: t.energy_required)

    def sort_by_due_date(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by due date (earliest first, None last)."""
        target = tasks if tasks is not None else self.get_tasks(completed=False)
        return sorted(target, key=lambda t: t.due_date or "9999-12-31")

    def sort_by_created(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by creation date (oldest first)."""
        target = tasks if tasks is not None else self.get_tasks(completed=False)
        return sorted(target, key=lambda t: t.created_at)

    # ── Search ────────────────────────────────────────────────────

    def search(self, query: str) -> list[Task]:
        """Search tasks by title, notes, and tags (case-insensitive)."""
        q = query.lower()
        results = []
        for t in self.tasks:
            if q in t.title.lower():
                results.append(t)
                continue
            if t.notes and q in t.notes.lower():
                results.append(t)
                continue
            if any(q in tag.lower() for tag in t.tags):
                results.append(t)
                continue
        return results

    # ── Batch Operations ──────────────────────────────────────────

    def batch_complete(self, task_ids: list[str]) -> list[Task]:
        """Complete multiple tasks at once."""
        completed = []
        for tid in task_ids:
            result = self.complete_task(tid)
            if result:
                completed.append(result)
        return completed

    def batch_delete(self, task_ids: list[str]) -> list[Task]:
        """Delete multiple tasks at once."""
        deleted = []
        for tid in task_ids:
            result = self.delete_task(tid)
            if result:
                deleted.append(result)
        return deleted

    # ── Templates ─────────────────────────────────────────────────

    def save_as_template(self, task_id: str, template_name: str) -> TaskTemplate | None:
        """Save an existing task as a reusable template."""
        task = self.get_task_by_id(task_id)
        if task is None:
            return None
        template = TaskTemplate(
            name=template_name,
            title=task.title,
            priority=task.priority.value,
            category=task.category.value,
            energy_required=task.energy_required,
            tags=list(task.tags),
            subtasks=[s.to_dict() for s in task.subtasks],
            estimated_duration=task.estimated_duration,
            values_alignment=task.values_alignment,
            custom_category=task.custom_category,
            notes=task.notes,
        )
        self.templates[template_name] = template
        self._save_templates()
        return template

    def create_from_template(self, template_name: str, **overrides: Any) -> Task | None:
        """Create a new task from a saved template with optional overrides."""
        template = self.templates.get(template_name)
        if template is None:
            return None
        task = template.create_task()
        for key, value in overrides.items():
            if hasattr(task, key):
                setattr(task, key, value)
        return self.add_task(task)

    def delete_template(self, template_name: str) -> bool:
        """Delete a template by name."""
        if template_name in self.templates:
            del self.templates[template_name]
            self._save_templates()
            return True
        return False

    def list_templates(self) -> list[str]:
        """List all saved template names."""
        return list(self.templates.keys())

    # ── Statistics ─────────────────────────────────────────────────

    def get_statistics(self) -> dict[str, Any]:
        """Compute comprehensive task statistics."""
        total = len(self.tasks)
        completed_tasks = [t for t in self.tasks if t.completed]
        incomplete_tasks = [t for t in self.tasks if not t.completed]
        completed_count = len(completed_tasks)

        # Completion rate
        completion_rate = (completed_count / total * 100) if total > 0 else 0.0

        # Average completion time (for tasks with both created_at and completed_at)
        completion_times: list[float] = []
        for t in completed_tasks:
            if t.created_at and t.completed_at:
                try:
                    created = datetime.fromisoformat(t.created_at)
                    done = datetime.fromisoformat(t.completed_at)
                    completion_times.append((done - created).total_seconds() / 3600)
                except ValueError:
                    continue
        avg_completion_hours = (
            sum(completion_times) / len(completion_times) if completion_times else 0.0
        )

        # Average actual duration
        actual_durations = [t.actual_duration for t in completed_tasks if t.actual_duration is not None]
        avg_actual_duration = (
            sum(actual_durations) / len(actual_durations) if actual_durations else 0.0
        )

        # Tasks by category
        by_category: dict[str, int] = {}
        for t in self.tasks:
            cat = t.custom_category or t.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        # Tasks by priority
        by_priority: dict[str, int] = {}
        for t in self.tasks:
            pname = t.priority.name
            by_priority[pname] = by_priority.get(pname, 0) + 1

        # Overdue count
        overdue_count = len(self.get_overdue_tasks())

        # Tags frequency
        tag_counts: dict[str, int] = {}
        for t in self.tasks:
            for tag in t.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            "total_tasks": total,
            "completed_tasks": completed_count,
            "incomplete_tasks": len(incomplete_tasks),
            "completion_rate": round(completion_rate, 1),
            "average_completion_time_hours": round(avg_completion_hours, 2),
            "average_actual_duration_minutes": round(avg_actual_duration, 1),
            "tasks_by_category": by_category,
            "tasks_by_priority": by_priority,
            "overdue_tasks": overdue_count,
            "tag_frequency": tag_counts,
        }
