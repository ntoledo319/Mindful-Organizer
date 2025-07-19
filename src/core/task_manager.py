"""
Task management system for organizing and prioritizing tasks.
"""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
from pathlib import Path
import json

class TaskPriority(Enum):
    Low = 1
    Medium = 2
    High = 3
    Urgent = 4

class TaskCategory(Enum):
    Work = "Work"
    Personal = "Personal"
    Health = "Health"
    Learning = "Learning"
    Social = "Social"
    Errands = "Errands"
    Other = "Other"

@dataclass
class Task:
    title: str
    priority: TaskPriority
    category: TaskCategory
    energy_required: int
    due_date: Optional[date] = None
    completed: bool = False
    notes: Optional[str] = None
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None

class TaskManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.tasks_file = data_dir / "tasks.json"
        self.tasks: List[Task] = []
        self._load_tasks()

    def _load_tasks(self):
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                tasks_data = json.load(f)
                self.tasks = [Task(**task) for task in tasks_data]

    def _save_tasks(self):
        with open(self.tasks_file, 'w') as f:
            json.dump([vars(task) for task in self.tasks], f, default=str)

    def add_task(self, task: Task):
        self.tasks.append(task)
        self._save_tasks()

    def complete_task(self, task: Task):
        task.completed = True
        task.completed_at = datetime.now()
        self._save_tasks()

    def get_tasks(self, completed: bool = False) -> List[Task]:
        return [task for task in self.tasks if task.completed == completed]

    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        return [task for task in self.tasks if task.priority == priority and not task.completed]

    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        return [task for task in self.tasks if task.category == category and not task.completed]

    def get_tasks_by_energy(self, max_energy: int) -> List[Task]:
        return [task for task in self.tasks if task.energy_required <= max_energy and not task.completed]
