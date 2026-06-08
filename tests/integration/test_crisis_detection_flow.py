"""
Integration tests for the Mood Entry → Wellness Orchestrator → Crisis Detection flow.

Tests that dangerously low mood combined with sleep deprivation triggers the
crisis heuristic and that the signal propagates to consumers via the state bus.
GUI components are mocked; only the backend flow is exercised.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from core.constants import Condition
from core.database import DatabaseManager, TableName
from core.state_bus import get_state_bus, reset_state_bus
from core.wellness_orchestrator import WellnessOrchestrator


@pytest.fixture
def crisis_db(tmp_data_dir):
    """Fresh database pre-seeded with schema."""
    db = DatabaseManager(db_path=tmp_data_dir / "crisis.db")
    db.initialize()
    yield db
    db.close()


@pytest.fixture(autouse=True)
def _clean_state_bus():
    """Reset the global state bus before every test in this module."""
    reset_state_bus()
    yield
    reset_state_bus()


@pytest.mark.integration
class TestCrisisDetectionFlow:
    def test_low_mood_and_sleep_deprivation_triggers_crisis(self, crisis_db):
        """Very low mood + <5h sleep average should produce a moderate crisis signal."""
        orchestrator = WellnessOrchestrator(db=crisis_db)

        # Insert 3 days of low mood and short sleep
        for i in range(3):
            ts = (datetime.now() - timedelta(days=i)).isoformat()
            crisis_db.insert(
                TableName.MOOD_ENTRIES,
                mood_score=2,
                energy_level=2,
                timestamp=ts,
            )
            crisis_db.insert(
                TableName.SLEEP_LOGS,
                date=(datetime.now() - timedelta(days=i)).date().isoformat(),
                bedtime="02:00",
                wake_time="06:00",
                quality=3,
                duration_hours=4.0,
            )

        signals = orchestrator.detect_crisis_signals(conditions=[Condition.DEPRESSION])

        assert len(signals) >= 1
        severities = {s.severity for s in signals}
        assert "urgent" in severities or "moderate" in severities

        # Verify the urgent signal references the very low mood
        urgent = [s for s in signals if s.severity == "urgent"]
        if urgent:
            assert (
                "very low" in urgent[0].description.lower()
                or "low" in urgent[0].description.lower()
            )

    def test_rapid_mood_drop_triggers_moderate_signal(self, crisis_db):
        """A 4+ point mood drop should trigger at least a moderate signal."""
        orchestrator = WellnessOrchestrator(db=crisis_db)

        # Latest mood is 2, previous was 7 -> 5-point drop
        for score, days_ago in [(7, 1), (2, 0)]:
            ts = (datetime.now() - timedelta(days=days_ago)).isoformat()
            crisis_db.insert(
                TableName.MOOD_ENTRIES,
                mood_score=score,
                energy_level=5,
                timestamp=ts,
            )

        signals = orchestrator.detect_crisis_signals()
        assert any(s.severity in ("urgent", "moderate") for s in signals)

    def test_crisis_signal_propagates_via_state_bus(self, crisis_db):
        """When crisis signals are detected, they can be emitted on the state bus."""
        orchestrator = WellnessOrchestrator(db=crisis_db)

        crisis_db.insert(
            TableName.MOOD_ENTRIES,
            mood_score=1,
            energy_level=1,
            timestamp=datetime.now().isoformat(),
        )

        bus = get_state_bus()
        mock_listener = MagicMock()
        bus.crisis_signal_detected.connect(mock_listener)

        signals = orchestrator.detect_crisis_signals()
        assert signals

        # Simulate what the dashboard layer does: emit the top signal
        top = signals[0]
        bus.emit_crisis_signal(
            {
                "severity": top.severity,
                "description": top.description,
                "recommendation": top.recommendation,
            }
        )

        mock_listener.assert_called_once()
        emitted = mock_listener.call_args[0][0]
        assert emitted["severity"] in ("urgent", "moderate", "mild", "info")
        assert "description" in emitted

    def test_no_false_positives_for_healthy_data(self, crisis_db):
        """Normal mood and sleep should not produce crisis signals."""
        orchestrator = WellnessOrchestrator(db=crisis_db)

        for i in range(3):
            ts = (datetime.now() - timedelta(days=i)).isoformat()
            crisis_db.insert(
                TableName.MOOD_ENTRIES,
                mood_score=7,
                energy_level=7,
                timestamp=ts,
            )
            crisis_db.insert(
                TableName.SLEEP_LOGS,
                date=(datetime.now() - timedelta(days=i)).date().isoformat(),
                bedtime="23:00",
                wake_time="07:00",
                quality=7,
                duration_hours=8.0,
            )

        signals = orchestrator.detect_crisis_signals()
        assert not signals

    def test_medication_miss_streak_detected(self, crisis_db):
        """3+ missed medications in a week should produce a mild signal."""
        orchestrator = WellnessOrchestrator(db=crisis_db)

        for i in range(4):
            crisis_db.insert(
                TableName.MEDICATION_LOGS,
                medication_name="Sertraline",
                dosage="50mg",
                frequency="daily",
                scheduled_time=(datetime.now() - timedelta(days=i)).isoformat(),
                status="missed",
            )

        signals = orchestrator.detect_crisis_signals()
        assert any(s.severity == "mild" and "medication" in s.description.lower() for s in signals)
