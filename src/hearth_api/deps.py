"""Dependency injection — singleton managers shared across requests.

FastAPI's `Depends(...)` calls these to get the live manager instance.
Managers are created lazily on first request and reused thereafter.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from hearth_api.settings import get_settings


def _data_dir() -> Path:
    d = get_settings().data_dir
    d.mkdir(parents=True, exist_ok=True)
    return d


@lru_cache(maxsize=1)
def get_database():
    from core.database import DatabaseManager
    db = DatabaseManager()
    db.initialize()
    return db


@lru_cache(maxsize=1)
def get_task_manager():
    from core.task_manager import TaskManager
    return TaskManager(data_dir=_data_dir())


@lru_cache(maxsize=1)
def get_mood_manager():
    from core.mood_manager import MoodManager
    return MoodManager(data_dir=_data_dir())


@lru_cache(maxsize=1)
def get_sleep_tracker():
    from core.sleep_tracker import SleepTracker
    return SleepTracker(data_dir=_data_dir())


@lru_cache(maxsize=1)
def get_medication_tracker():
    from core.medication_tracker import MedicationTracker
    return MedicationTracker(data_dir=_data_dir())


@lru_cache(maxsize=1)
def get_diary_card_manager():
    from core.diary_card_manager import DiaryCardManager
    return DiaryCardManager(data_dir=_data_dir())


@lru_cache(maxsize=1)
def get_subscription_manager():
    from core.subscription_manager import SubscriptionManager
    return SubscriptionManager(data_dir=_data_dir())


@lru_cache(maxsize=1)
def get_automation_engine():
    from core.platform_actions import get_backend
    from core.system_automation import SystemAutomationEngine
    return SystemAutomationEngine(
        data_dir=_data_dir(),
        backend=get_backend(),
        subscription_manager=get_subscription_manager(),
    )


@lru_cache(maxsize=1)
def get_focus_manager():
    from core.focus_mode import FocusModeManager
    return FocusModeManager(data_dir=_data_dir())


@lru_cache(maxsize=1)
def get_wellness_orchestrator():
    from core.wellness_orchestrator import WellnessOrchestrator
    return WellnessOrchestrator(
        data_dir=_data_dir(),
        mood_manager=get_mood_manager(),
        sleep_tracker=get_sleep_tracker(),
        medication_tracker=get_medication_tracker(),
    )


@lru_cache(maxsize=1)
def get_state_bus():
    """Returns the singleton StateBus — same instance the managers emit on."""
    from core.state_bus import get_state_bus as _impl
    return _impl()


def reset_all() -> None:
    """Clear all cached managers — for tests."""
    for fn in (
        get_database,
        get_task_manager,
        get_mood_manager,
        get_sleep_tracker,
        get_medication_tracker,
        get_diary_card_manager,
        get_subscription_manager,
        get_automation_engine,
        get_focus_manager,
        get_wellness_orchestrator,
    ):
        fn.cache_clear()
