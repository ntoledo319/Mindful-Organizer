"""
Tests for MedicationTracker (src/core/medication_tracker.py).

Covers adding medications, tracking adherence, refill reminders,
and side-effect logging.
"""

from datetime import datetime

import pytest

from core.database import DatabaseManager
from core.medication_tracker import (
    Frequency,
    Medication,
    MedicationTracker,
)


@pytest.fixture
def db(tmp_data_dir):
    database = DatabaseManager(db_path=tmp_data_dir / "test.db")
    database.initialize()
    yield database
    database.close()


@pytest.fixture
def tracker(db):
    return MedicationTracker(db)


# ---------------------------------------------------------------------------
# Add medication (log_dose)
# ---------------------------------------------------------------------------

class TestAddMedication:

    def test_log_dose(self, tracker):
        row_id = tracker.log_dose(
            medication_name="Sertraline",
            dosage="50mg",
            frequency="once_daily",
            scheduled_time="08:00",
            status="taken",
            taken_time=datetime.now().isoformat(),
        )
        assert row_id > 0

    def test_log_dose_defaults_to_pending(self, tracker):
        row_id = tracker.log_dose(
            medication_name="Lexapro",
            dosage="10mg",
            frequency="once_daily",
            scheduled_time="09:00",
        )
        log = tracker.get_log(row_id)
        assert log.status == "pending"

    def test_log_with_supply_count(self, tracker):
        row_id = tracker.log_dose(
            medication_name="Wellbutrin",
            dosage="150mg",
            frequency="once_daily",
            scheduled_time="08:00",
            status="taken",
            supply_count=28,
        )
        log = tracker.get_log(row_id)
        assert log.supply_count == 28

    def test_get_medications_list(self, tracker):
        tracker.log_dose("Med A", "10mg", "once_daily", "08:00", status="taken")
        tracker.log_dose("Med B", "20mg", "twice_daily", "08:00", status="taken")
        tracker.log_dose("Med A", "10mg", "once_daily", "20:00", status="taken")

        meds = tracker.get_medications()
        assert "Med A" in meds
        assert "Med B" in meds

    def test_mark_taken(self, tracker):
        row_id = tracker.log_dose("TestMed", "5mg", "once_daily", "08:00")
        tracker.mark_taken(row_id)

        log = tracker.get_log(row_id)
        assert log.status == "taken"
        assert log.taken_time is not None

    def test_mark_missed(self, tracker):
        row_id = tracker.log_dose("TestMed", "5mg", "once_daily", "08:00")
        tracker.mark_missed(row_id)

        log = tracker.get_log(row_id)
        assert log.status == "missed"

    def test_mark_skipped(self, tracker):
        row_id = tracker.log_dose("TestMed", "5mg", "once_daily", "08:00")
        tracker.mark_skipped(row_id, notes="Side effects")

        log = tracker.get_log(row_id)
        assert log.status == "skipped"
        assert log.notes == "Side effects"

    def test_delete_log(self, tracker):
        row_id = tracker.log_dose("TestMed", "5mg", "once_daily", "08:00")
        affected = tracker.delete_log(row_id)
        assert affected == 1
        assert tracker.get_log(row_id) is None


# ---------------------------------------------------------------------------
# Track adherence
# ---------------------------------------------------------------------------

class TestTrackAdherence:

    def test_adherence_all_taken(self, tracker):
        for _ in range(10):
            tracker.log_dose("Med", "10mg", "once_daily", "08:00", status="taken")

        stats = tracker.adherence("Med", days=30)
        assert stats.adherence_percent == 100.0
        assert stats.taken == 10

    def test_adherence_mixed(self, tracker):
        for i in range(10):
            status = "taken" if i < 7 else "missed"
            tracker.log_dose("Med", "10mg", "once_daily", "08:00", status=status)

        stats = tracker.adherence("Med", days=30)
        assert stats.taken == 7
        assert stats.missed == 3
        assert stats.adherence_percent == 70.0

    def test_adherence_empty(self, tracker):
        stats = tracker.adherence("NonExistent", days=30)
        assert stats.total_logs == 0
        assert stats.adherence_percent == 0.0

    def test_adherence_includes_late_as_adherent(self, tracker):
        tracker.log_dose("Med", "10mg", "once_daily", "08:00", status="taken")
        tracker.log_dose("Med", "10mg", "once_daily", "08:00", status="late")

        stats = tracker.adherence("Med", days=30)
        # Both taken and late count as adherent
        assert stats.adherence_percent == 100.0

    def test_adherence_trend(self, tracker):
        for i in range(14):
            status = "taken" if i % 3 != 0 else "missed"
            tracker.log_dose("Med", "10mg", "once_daily", "08:00", status=status)

        trend = tracker.adherence_trend("Med", days=30, window=7)
        assert isinstance(trend, list)


# ---------------------------------------------------------------------------
# Refill reminder
# ---------------------------------------------------------------------------

class TestRefillReminder:

    def test_days_until_refill(self, tracker):
        tracker.log_dose(
            "Sertraline", "50mg", "once_daily", "08:00",
            status="taken", supply_count=14,
        )
        days = tracker.days_until_refill("Sertraline")
        assert days == 14  # once daily, 14 pills

    def test_days_until_refill_with_override(self, tracker):
        tracker.log_dose(
            "Sertraline", "50mg", "once_daily", "08:00",
            status="taken",
        )
        days = tracker.days_until_refill("Sertraline", current_supply=7)
        assert days == 7

    def test_needs_refill_true(self, tracker):
        tracker.log_dose(
            "Sertraline", "50mg", "once_daily", "08:00",
            status="taken", supply_count=3,
        )
        assert tracker.needs_refill("Sertraline", threshold_days=7) is True

    def test_needs_refill_false(self, tracker):
        tracker.log_dose(
            "Sertraline", "50mg", "once_daily", "08:00",
            status="taken", supply_count=30,
        )
        assert tracker.needs_refill("Sertraline", threshold_days=7) is False

    def test_needs_refill_no_data(self, tracker):
        assert tracker.needs_refill("Unknown") is False

    def test_days_until_refill_no_supply(self, tracker):
        tracker.log_dose("NoSupply", "5mg", "once_daily", "08:00", status="taken")
        assert tracker.days_until_refill("NoSupply") is None

    def test_get_refill_alerts(self, tracker):
        tracker.log_dose("LowMed", "5mg", "once_daily", "08:00",
                         status="taken", supply_count=3)
        tracker.log_dose("OkMed", "10mg", "once_daily", "08:00",
                         status="taken", supply_count=60)

        alerts = tracker.get_refill_alerts(threshold_days=7)
        names = [a["medication_name"] for a in alerts]
        assert "LowMed" in names
        assert "OkMed" not in names


# ---------------------------------------------------------------------------
# Side-effect logging
# ---------------------------------------------------------------------------

class TestSideEffectLogging:

    def test_log_side_effect(self, tracker):
        row_id = tracker.log_side_effect(
            medication_name="Sertraline",
            dosage="50mg",
            frequency="once_daily",
            scheduled_time="08:00",
            side_effects="nausea, dizziness",
        )
        log = tracker.get_log(row_id)
        assert "nausea" in log.side_effects
        assert "dizziness" in log.side_effects

    def test_side_effect_summary(self, tracker):
        for effects in ["nausea", "nausea, headache", "headache"]:
            tracker.log_side_effect(
                "Med", "10mg", "once_daily", "08:00",
                side_effects=effects,
            )

        summary = tracker.side_effect_summary("Med", days=90)
        assert summary.total_reports == 3
        assert summary.effects["nausea"] == 2
        assert summary.effects["headache"] == 2

    def test_side_effect_summary_empty(self, tracker):
        summary = tracker.side_effect_summary("Unknown", days=90)
        assert summary.total_reports == 0
        assert summary.effects == {}


# ---------------------------------------------------------------------------
# Daily schedule
# ---------------------------------------------------------------------------

class TestDailySchedule:

    def test_create_daily_schedule(self, tracker):
        meds = [
            Medication(name="MedA", dosage="10mg", frequency="once_daily", scheduled_time="08:00"),
            Medication(name="MedB", dosage="20mg", frequency="twice_daily", scheduled_time="12:00"),
        ]
        ids = tracker.create_daily_schedule(meds)
        assert len(ids) == 2

    def test_frequency_doses_per_day(self):
        assert Frequency.ONCE_DAILY.doses_per_day == 1.0
        assert Frequency.TWICE_DAILY.doses_per_day == 2.0
        assert Frequency.WEEKLY.doses_per_day == pytest.approx(1 / 7, rel=0.01)
        assert Frequency.AS_NEEDED.doses_per_day == 0.0


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

class TestExport:

    def test_export_history(self, tracker, tmp_data_dir):
        tracker.log_dose("Med", "10mg", "once_daily", "08:00", status="taken")
        output = tmp_data_dir / "med_export.json"
        result_path = tracker.export_history(output_path=output, days=30)

        assert result_path.exists()
        import json
        data = json.loads(result_path.read_text())
        assert "disclaimer" in data
        assert "medications" in data
