"""
Shared fixtures for the Mindful Organizer test suite.

Provides reusable temporary directories, sample profiles, tasks,
and mood entries that can be composed across all test modules.
"""

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

# Ensure the src package is importable regardless of working directory.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_data_dir(tmp_path):
    """Return a temporary data directory, pre-created."""
    data_dir = tmp_path / "mindful_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def sample_profile():
    """A test Profile-like dict with ADHD + Anxiety conditions."""
    return {
        "name": "Test User",
        "conditions": {"ADHD", "Anxiety"},
        "therapy_types": {"CBT", "Mindfulness-Based Therapy"},
        "therapy_skills": {"Deep Breathing", "Grounding Techniques"},
        "notes": "Sample profile for testing",
    }


@pytest.fixture
def sample_tasks():
    """List of five Task objects with varying priorities and categories."""
    try:
        from src.core.task_manager import Task, TaskCategory, TaskPriority
    except ImportError:
        pytest.skip("task_manager module not available")

    return [
        Task(
            title="Write report",
            priority=TaskPriority.High,
            category=TaskCategory.Work,
            energy_required=8,
            due_date=(date.today() + timedelta(days=2)).isoformat(),
            tags={"work", "writing"},
        ),
        Task(
            title="Schedule dentist",
            priority=TaskPriority.Medium,
            category=TaskCategory.Health,
            energy_required=3,
            due_date=(date.today() + timedelta(days=7)).isoformat(),
            tags={"health"},
        ),
        Task(
            title="Buy groceries",
            priority=TaskPriority.Low,
            category=TaskCategory.Errands,
            energy_required=4,
            tags={"errands"},
        ),
        Task(
            title="Fix critical bug",
            priority=TaskPriority.Urgent,
            category=TaskCategory.Work,
            energy_required=9,
            due_date=date.today().isoformat(),
            tags={"work", "urgent"},
        ),
        Task(
            title="Meditate",
            priority=TaskPriority.Low,
            category=TaskCategory.Health,
            energy_required=2,
            tags={"health", "wellness"},
        ),
    ]


@pytest.fixture
def sample_mood_entries():
    """List of 10 mood-entry dicts spread over 10 days."""
    base = datetime(2026, 1, 1, 8, 0, 0) - timedelta(days=10)
    entries = []
    for i in range(10):
        ts = base + timedelta(days=i, hours=10)
        entries.append({
            "timestamp": ts.isoformat(),
            "mood_score": 4 + (i * 0.5),         # gradually improving 4 -> 8.5
            "energy_score": 30 + i * 5,           # 30 -> 75
            "symptoms": ["fatigue"] if i < 5 else [],
            "notes": f"Day {i + 1} mood entry",
            "activities": ["walking"] if i % 2 == 0 else [],
            "sleep_hours": 6.5 + (i * 0.2),
            "medication_taken": i % 2 == 0,
            "tasks_completed": i,
        })
    return entries
