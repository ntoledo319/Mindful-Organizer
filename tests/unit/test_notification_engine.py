"""
Tests for SmartNotificationEngine.

Covers energy-based notifications, sleep-debt alerts, and safe behaviour
when wellness data is missing or ambiguous.
"""

from dataclasses import dataclass

import pytest

try:
    from src.core.notification_engine import SmartNotification, SmartNotificationEngine
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="notification_engine module not available")


@dataclass
class _FakeSnapshot:
    energy_score: int | None = None
    sleep_hours: float | None = None
    tasks_pending: int = 0
    tasks_completed_today: int = 0
    medication_adherence: float | None = None


class TestGenerateNotifications:
    def test_energy_peak_suggests_tasks(self) -> None:
        engine = SmartNotificationEngine(db=None, orchestrator=None)  # type: ignore[arg-type]
        engine.orchestrator = None  # bypass real orchestrator
        snapshot = _FakeSnapshot(energy_score=8, tasks_pending=2)
        # Patch snapshot method
        engine.orchestrator = type("FakeOrchestrator", (), {"snapshot": lambda self, now: snapshot})()
        notes = engine.generate_notifications(conditions=[])
        assert any(n.id == "energy_peak_task" for n in notes)

    def test_low_energy_gentle_mode(self) -> None:
        engine = SmartNotificationEngine(db=None, orchestrator=None)  # type: ignore[arg-type]
        snapshot = _FakeSnapshot(energy_score=2, tasks_pending=5)
        engine.orchestrator = type("FakeOrchestrator", (), {"snapshot": lambda self, now: snapshot})()
        notes = engine.generate_notifications(conditions=[])
        assert any(n.id == "energy_low_trim" for n in notes)

    def test_sleep_debt_alert(self) -> None:
        engine = SmartNotificationEngine(db=None, orchestrator=None)  # type: ignore[arg-type]
        snapshot = _FakeSnapshot(sleep_hours=4.0)
        engine.orchestrator = type("FakeOrchestrator", (), {"snapshot": lambda self, now: snapshot})()
        notes = engine.generate_notifications(conditions=[])
        assert any(n.id == "sleep_debt" for n in notes)

    def test_no_notifications_when_data_missing(self) -> None:
        engine = SmartNotificationEngine(db=None, orchestrator=None)  # type: ignore[arg-type]
        snapshot = _FakeSnapshot(energy_score=None, sleep_hours=None)
        engine.orchestrator = type("FakeOrchestrator", (), {"snapshot": lambda self, now: snapshot})()
        notes = engine.generate_notifications(conditions=[])
        # With no energy or sleep data, only general notifications might appear
        sleep_or_energy = [n for n in notes if n.category in ("energy", "sleep")]
        assert len(sleep_or_energy) == 0

    def test_notification_structure(self) -> None:
        engine = SmartNotificationEngine(db=None, orchestrator=None)  # type: ignore[arg-type]
        snapshot = _FakeSnapshot(energy_score=9, tasks_pending=1)
        engine.orchestrator = type("FakeOrchestrator", (), {"snapshot": lambda self, now: snapshot})()
        notes = engine.generate_notifications(conditions=[])
        assert len(notes) > 0
        for n in notes:
            assert isinstance(n, SmartNotification)
            assert n.id
            assert n.title
            assert n.message
            assert n.priority in ("info", "mild", "moderate", "urgent")
            assert n.category in ("energy", "sleep", "medication", "task", "crisis", "general")
