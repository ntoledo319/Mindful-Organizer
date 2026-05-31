"""
Wearable sync integration for Hearth.
Parses Apple Health XML and Google Fit CSV exports to sync sleep and energy data.
"""

from __future__ import annotations

import csv
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from core.database import DatabaseManager, TableName

logger = logging.getLogger(__name__)


@dataclass
class SleepData:
    start_time: datetime
    end_time: datetime
    duration_hours: float
    source: str


class WearableSyncManager:
    """Manages parsing and importing health data from wearable exports."""

    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        if db_manager is None:
            from core.database import DATA_DIR

            self.db = DatabaseManager(DATA_DIR / "mindful_organizer.db")
            self.db.initialize()
        else:
            self.db = db_manager

    @staticmethod
    def _parse_datetime(value: str) -> datetime | None:
        """Parse common Apple Health and Google Fit export timestamps."""
        raw = value.strip()
        if not raw:
            return None

        iso_value = raw.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(iso_value)
        except ValueError:
            pass

        for fmt in (
            "%Y-%m-%d %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%m/%d/%Y %I:%M:%S %p",
            "%m/%d/%Y %H:%M:%S",
        ):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        return None

    def _insert_sleep(self, start: datetime, end: datetime, source: str) -> bool:
        duration = (end - start).total_seconds() / 3600.0
        if duration <= 0:
            return False

        self.db.insert(
            TableName.SLEEP_LOGS,
            date=start.date().isoformat(),
            bedtime=start.strftime("%H:%M"),
            wake_time=end.strftime("%H:%M"),
            quality=7,  # Wearable exports often omit subjective sleep quality.
            duration_hours=round(duration, 2),
            notes=f"Imported from {source}",
        )
        return True

    def import_apple_health_xml(self, file_path: Path) -> int:
        """Parse Apple Health export.xml and import sleep analysis data.
        Returns the number of sleep records imported.
        """
        if not file_path.exists():
            raise FileNotFoundError("Apple Health XML file not found.")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            logger.error("Failed to parse Apple Health XML: %s", e)
            return 0

        sleep_records = 0
        for record in root.findall("Record"):
            if record.get("type") == "HKCategoryTypeIdentifierSleepAnalysis":
                start_str = record.get("startDate", "")
                end_str = record.get("endDate", "")
                val = record.get("value")
                # Usually HKCategoryValueSleepAnalysisAsleep is used for actual sleep
                if "Asleep" not in str(val):
                    continue

                start = self._parse_datetime(start_str)
                end = self._parse_datetime(end_str)
                if start and end and self._insert_sleep(start, end, "Apple Health"):
                    sleep_records += 1

        logger.info("Imported %d sleep records from Apple Health", sleep_records)
        return sleep_records

    def import_google_fit_csv(self, file_path: Path) -> int:
        """Parse Google Fit Sleep CSV export and import sleep data.
        Returns the number of sleep records imported.
        """
        if not file_path.exists():
            raise FileNotFoundError("Google Fit CSV file not found.")

        sleep_records = 0
        try:
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    start_str = row.get("Start time", "")
                    end_str = row.get("End time", "")
                    if not start_str or not end_str:
                        continue
                    start = self._parse_datetime(start_str)
                    end = self._parse_datetime(end_str)
                    if start and end and self._insert_sleep(start, end, "Google Fit"):
                        sleep_records += 1
        except Exception as e:
            logger.error("Failed to parse Google Fit CSV: %s", e)

        logger.info("Imported %d sleep records from Google Fit", sleep_records)
        return sleep_records

    def sync_all_available(self, export_dir: Path) -> dict[str, int]:
        """Auto-detect and import all valid wearable exports in a directory."""
        results = {"apple_health": 0, "google_fit": 0}

        if export_dir.is_file():
            if export_dir.name.lower() == "export.xml":
                results["apple_health"] = self.import_apple_health_xml(export_dir)
            elif export_dir.suffix.lower() == ".csv" and "sleep" in export_dir.name.lower():
                results["google_fit"] = self.import_google_fit_csv(export_dir)
            return results

        for apple_xml in export_dir.rglob("export.xml"):
            results["apple_health"] += self.import_apple_health_xml(apple_xml)

        for csv_file in export_dir.rglob("*.csv"):
            if "sleep" in csv_file.name.lower():
                results["google_fit"] += self.import_google_fit_csv(csv_file)

        return results
