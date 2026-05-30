"""
Tests for wearable sleep import (src/core/wearable_sync.py).

Covers Apple Health XML, Google Fit CSV, and recursive export-directory
auto-detection.
"""

from __future__ import annotations

import pytest

try:
    from src.core.database import DatabaseManager, TableName
    from src.core.wearable_sync import WearableSyncManager

    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="wearable_sync module not available")


@pytest.fixture
def db(tmp_data_dir):
    database = DatabaseManager(db_path=tmp_data_dir / "wearable.db")
    database.initialize()
    yield database
    database.close()


def test_import_apple_health_xml_imports_asleep_records(db, tmp_path):
    export = tmp_path / "export.xml"
    export.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<HealthData>
  <Record type="HKCategoryTypeIdentifierSleepAnalysis"
          value="HKCategoryValueSleepAnalysisAsleepCore"
          startDate="2026-05-28 22:30:00 -0400"
          endDate="2026-05-29 06:00:00 -0400" />
  <Record type="HKCategoryTypeIdentifierSleepAnalysis"
          value="HKCategoryValueSleepAnalysisInBed"
          startDate="2026-05-28 22:00:00 -0400"
          endDate="2026-05-29 06:30:00 -0400" />
</HealthData>
""",
        encoding="utf-8",
    )

    imported = WearableSyncManager(db).import_apple_health_xml(export)

    assert imported == 1
    rows = db.query(TableName.SLEEP_LOGS).rows
    assert rows[0]["date"] == "2026-05-28"
    assert rows[0]["bedtime"] == "22:30"
    assert rows[0]["wake_time"] == "06:00"
    assert rows[0]["duration_hours"] == 7.5
    assert rows[0]["notes"] == "Imported from Apple Health"


def test_import_google_fit_csv_imports_sleep_rows(db, tmp_path):
    export = tmp_path / "Daily Sleep.csv"
    export.write_text(
        "Start time,End time\n"
        "2026-05-28T23:00:00Z,2026-05-29T06:30:00Z\n"
        "missing-end,\n",
        encoding="utf-8",
    )

    imported = WearableSyncManager(db).import_google_fit_csv(export)

    assert imported == 1
    rows = db.query(TableName.SLEEP_LOGS).rows
    assert rows[0]["date"] == "2026-05-28"
    assert rows[0]["bedtime"] == "23:00"
    assert rows[0]["wake_time"] == "06:30"
    assert rows[0]["duration_hours"] == 7.5
    assert rows[0]["notes"] == "Imported from Google Fit"


def test_sync_all_available_detects_nested_exports(db, tmp_path):
    apple_dir = tmp_path / "apple_health_export"
    apple_dir.mkdir()
    (apple_dir / "export.xml").write_text(
        """<HealthData>
  <Record type="HKCategoryTypeIdentifierSleepAnalysis"
          value="HKCategoryValueSleepAnalysisAsleepREM"
          startDate="2026-05-27 23:15:00"
          endDate="2026-05-28 01:15:00" />
</HealthData>
""",
        encoding="utf-8",
    )

    google_dir = tmp_path / "Takeout" / "Fit"
    google_dir.mkdir(parents=True)
    (google_dir / "Sleep Sessions.csv").write_text(
        "Start time,End time\n"
        "2026-05-28 23:00:00,2026-05-29 05:00:00\n",
        encoding="utf-8",
    )

    results = WearableSyncManager(db).sync_all_available(tmp_path)

    assert results == {"apple_health": 1, "google_fit": 1}
    assert db.count(TableName.SLEEP_LOGS) == 2
