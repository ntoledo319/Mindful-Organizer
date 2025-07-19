"""
Task management system with mental health awareness.
"""
from dataclasses import dataclass
from datetime import datetime, time
from typing import List, Optional
from enum import Enum
import json
from pathlib import Path

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class TaskCategory(Enum):
    WORK = "Work"
    PERSONAL = "Personal"
    HEALTH = "Health"
    ROUTINE = "Daily Routine"
    CREATIVE = "Creative"
    LEARNING = "Learning"

@dataclass
class Task:
    title: str
    priority: TaskPriority
    energy_required: int  # 1-5 scale
    category: TaskCategory
    due_date: Optional[datetime] = None
    completed: bool = False
    notes: Optional[str] = None
    time_estimate: Optional[int] = None  # in minutes
    best_time: Optional[time] = None
    breaks_needed: Optional[int] = None

class TaskManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.tasks_file = data_dir / "tasks.json"
        self.tasks: List[Task] = []
        self._load_tasks()

    def _load_tasks(self):
        """Load tasks from JSON file."""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                tasks_data = json.load(f)
                self.tasks = [self._deserialize_task(t) for t in tasks_data]

    def _save_tasks(self):
        """Save tasks to JSON file."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.tasks_file, 'w') as f:
            tasks_data = [self._serialize_task(t) for t in self.tasks]
            json.dump(tasks_data, f, indent=2)

    def _serialize_task(self, task: Task) -> dict:
        """Convert Task object to dictionary for JSON serialization."""
        return {
            'title': task.title,
            'priority': task.priority.name,
            'energy_required': task.energy_required,
            'category': task.category.value,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'completed': task.completed,
            'notes': task.notes,
            'time_estimate': task.time_estimate,
            'best_time': task.best_time.isoformat() if task.best_time else None,
            'breaks_needed': task.breaks_needed
        }

    def _deserialize_task(self, data: dict) -> Task:
        """Convert dictionary to Task object."""
        if data.get('due_date'):
            data['due_date'] = datetime.fromisoformat(data['due_date'])
        if data.get('best_time'):
            data['best_time'] = datetime.fromisoformat(data['best_time']).time()
        return Task(
            title=data['title'],
            priority=TaskPriority[data['priority']],
            energy_required=data['energy_required'],
            category=TaskCategory(data['category']),
            due_date=data.get('due_date'),
            completed=data.get('completed', False),
            notes=data.get('notes'),
            time_estimate=data.get('time_estimate'),
            best_time=data.get('best_time'),
            breaks_needed=data.get('breaks_needed')
        )

    def add_task(self, task: Task):
        """Add a new task."""
        self.tasks.append(task)
        self._save_tasks()

    def complete_task(self, task_title: str):
        """Mark a task as completed."""
        for task in self.tasks:
            if task.title == task_title:
                task.completed = True
                break
        self._save_tasks()

    def remove_task(self, task_title: str):
        """Remove a task."""
        self.tasks = [t for t in self.tasks if t.title != task_title]
        self._save_tasks()

    def get_tasks(self, category: Optional[TaskCategory] = None,
                 completed: Optional[bool] = None) -> List[Task]:
        """Get tasks, optionally filtered by category and completion status."""
        tasks = self.tasks
        if category:
            tasks = [t for t in tasks if t.category == category]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return sorted(tasks, key=lambda t: (t.priority.value, t.energy_required), reverse=True)

    def get_task_suggestions(self, current_energy: int) -> List[Task]:
        """Get task suggestions based on current energy level."""
        incomplete_tasks = [t for t in self.tasks if not t.completed]
        suitable_tasks = [t for t in incomplete_tasks if t.energy_required <= current_energy]
        return sorted(suitable_tasks, key=lambda t: abs(t.energy_required - current_energy))

    def get_daily_plan(self, energy_pattern: dict) -> List[Task]:
        """Create a daily plan based on energy pattern."""
        tasks = [t for t in self.tasks if not t.completed]
        plan = []
        
        # Morning tasks (high energy)
        morning_tasks = [t for t in tasks if t.energy_required > 3]
        plan.extend(morning_tasks[:energy_pattern.get('morning', 2)])
        
        # Afternoon tasks (medium energy)
        afternoon_tasks = [t for t in tasks if 2 <= t.energy_required <= 3]
        plan.extend(afternoon_tasks[:energy_pattern.get('afternoon', 3)])
        
        # Evening tasks (lower energy)
        evening_tasks = [t for t in tasks if t.energy_required < 2]
        plan.extend(evening_tasks[:energy_pattern.get('evening', 2)])
        
        return plan
