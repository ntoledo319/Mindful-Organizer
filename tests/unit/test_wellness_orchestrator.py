"""
Tests for WellnessOrchestrator crisis detection and daily snapshot logic.

Covers mood+sleep deprivation signals, rapid mood drops, medication miss
streaks, bipolar elevated-energy warnings, and regression tests for
previously unfixed runtime bugs.
"""

from datetime import datetime, timedelta
from pathlib import Path

from core.constants import Condition
from core.database import DatabaseManager, TableName
from core.wellness_orchestrator import WellnessOrchestrator


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
        self._insert_moods(db, [3, 8])  # a 5-point slide landing at 3
        orch = WellnessOrchestrator(db)
        signals = orch.detect_crisis_signals(conditions=[])
        mood_signals = [s for s in signals if "mood" in s.source_modules]
        assert mood_signals, "a 5-point mood drop must produce a signal"
        # Severity scales with magnitude: a 5-point drop is at least 'moderate',
        # never the old under-reacting 'mild'.
        assert all(s.severity in {"moderate", "urgent"} for s in mood_signals)
        db.close()

    def test_severe_mood_crash_is_urgent_and_surfaces_crisis_line(
        self, tmp_data_dir: Path
    ) -> None:
        db = DatabaseManager(tmp_data_dir / "test.db")
        db.initialize()
        self._insert_moods(db, [2, 9])  # catastrophic 7-point crash to 2/10
        orch = WellnessOrchestrator(db)
        signals = orch.detect_crisis_signals(conditions=[])
        urgent = [s for s in signals if s.severity == "urgent"]
        assert urgent, "a crash to 2/10 must be urgent, not mild"
        assert any("988" in s.recommendation for s in urgent), (
            "urgent signals must surface the 988 crisis line"
        )
        db.close()

    def test_signals_are_ordered_most_severe_first(self, tmp_data_dir: Path) -> None:
        """When a moderate and an urgent signal co-occur (mood crashed AND not
        sleeping), the urgent 988 signal must be first so every consumer surfaces
        it — not whichever heuristic happened to append first."""
        db = DatabaseManager(tmp_data_dir / "test.db")
        db.initialize()
        self._insert_moods(db, [2, 3, 3])          # latest 2/10 -> urgent absolute-low
        self._insert_sleep(db, [4.0, 4.0, 4.0])    # avg <5h -> moderate mood+sleep
        orch = WellnessOrchestrator(db)
        signals = orch.detect_crisis_signals(conditions=[])

        assert len(signals) >= 2
        assert signals[0].severity == "urgent"
        assert "988" in signals[0].recommendation
        rank = {"urgent": 0, "moderate": 1, "mild": 2, "info": 3}
        ranks = [rank[s.severity] for s in signals]
        assert ranks == sorted(ranks), "signals must be sorted by descending severity"
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
