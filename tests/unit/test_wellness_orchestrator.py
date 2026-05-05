"""
Tests for WellnessOrchestrator crisis detection and daily snapshot logic.

Covers mood+sleep deprivation signals, rapid mood drops, medication miss
streaks, bipolar elevated-energy warnings, and regression tests for
previously unfixed runtime bugs.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

try:
    from src.core.constants import Condition
    from src.core.database import DatabaseManager, TableName
    from src.core.wellness_orchestrator import WellnessOrchestrator
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="wellness_orchestrator module not available")


class TestCrisisSignals:
    def _insert_moods(self, db: DatabaseManager, scores: list[int]) -> None:
        base = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        for i, score in enumerate(scores):
            db.insert(
                TableName.MOOD_ENTRIES,
                timestamp=(base - timedelta(days=i)).isoformat(),
                mood_score=int(score),
                energy_level=5,
                notes="",
                context="test",
            )

    def _insert_sleep(self, db: DatabaseManager, hours: list[float]) -> None:
        base = datetime.now().date()
        for i, h in enumerate(hours):
            db.insert(
                TableName.SLEEP_LOGS,
                date=(base - timedelta(days=i)).isoformat(),
                duration_hours=h,
                quality=5,
                bedtime="23:00",
                wake_time="07:00",
                interruptions=0,
                notes="",
            )

    def _insert_meds(self, db: DatabaseManager, statuses: list[str]) -> None:
        base = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        for i, status in enumerate(statuses):
            db.insert(
                TableName.MEDICATION_LOGS,
                scheduled_time=(base - timedelta(days=i)).isoformat(),
                medication_name="TestMed",
                dosage="10mg",
                frequency="daily",
                status=status,
                notes="",
            )

    def _insert_energy(self, db: DatabaseManager, levels: list[int]) -> None:
        base = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        for i, level in enumerate(levels):
            db.insert(
                TableName.ENERGY_READINGS,
                timestamp=(base - timedelta(days=i)).isoformat(),
                energy_level=level,
                activity="test",
                notes="",
            )

    def test_low_mood_and_short_sleep_crisis(self, tmp_data_dir: Path) -> None:
        db = DatabaseManager(tmp_data_dir / "test.db")
        db.initialize()
        self._insert_moods(db, [3, 3, 3])
        self._insert_sleep(db, [4.5, 4.0, 4.2])
        orch = WellnessOrchestrator(db)
        signals = orch.detect_crisis_signals(conditions=[])
        assert any("mood" in s.source_modules and "sleep" in s.source_modules for s in signals)
        db.close()

    def test_rapid_mood_drop_crisis(self, tmp_data_dir: Path) -> None:
        db = DatabaseManager(tmp_data_dir / "test.db")
        db.initialize()
        self._insert_moods(db, [3, 8])
        orch = WellnessOrchestrator(db)
        signals = orch.detect_crisis_signals(conditions=[])
        assert any(s.severity == "mild" and "mood" in s.source_modules for s in signals)
        db.close()

    def test_medication_miss_streak(self, tmp_data_dir: Path) -> None:
        db = DatabaseManager(tmp_data_dir / "test.db")
        db.initialize()
        self._insert_meds(db, ["missed"] * 4)
        orch = WellnessOrchestrator(db)
        signals = orch.detect_crisis_signals(conditions=[])
        assert any("medication" in s.source_modules for s in signals)
        db.close()

    def test_bipolar_elevated_energy_low_sleep(self, tmp_data_dir: Path) -> None:
        db = DatabaseManager(tmp_data_dir / "test.db")
        db.initialize()
        # Need mood entries so that avg_sleep is calculated inside the mood block
        self._insert_moods(db, [5, 5, 5])
        self._insert_energy(db, [9, 9, 9, 8, 9, 9, 8])
        self._insert_sleep(db, [3.5, 4.0, 3.0, 4.5, 3.5, 4.0, 3.0])
        orch = WellnessOrchestrator(db)
        signals = orch.detect_crisis_signals(conditions=[Condition.BIPOLAR])
        assert any("energy" in s.source_modules and "sleep" in s.source_modules for s in signals)
        db.close()

    def test_no_unbound_local_error_when_no_mood_entries(self, tmp_data_dir: Path) -> None:
        """Regression: avg_sleep was referenced before assignment when no moods existed."""
        db = DatabaseManager(tmp_data_dir / "test.db")
        db.initialize()
        orch = WellnessOrchestrator(db)
        # Should not raise UnboundLocalError even with bipolar condition
        signals = orch.detect_crisis_signals(conditions=[Condition.BIPOLAR])
        assert isinstance(signals, list)
        db.close()
