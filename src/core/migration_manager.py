"""
Data migration manager — safely migrates legacy JSON files to SQLite.

Provides a progress-tracking, rollback-capable migration for each
wellness module that currently stores data in JSON.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from core.database import DatabaseManager, TableName

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MigrationResult:
    """Result of a single migration step."""
    module: str
    success: bool
    records_migrated: int = 0
    error: str | None = None


@dataclass
class MigrationReport:
    """Complete migration report."""
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: datetime | None = None
    results: list[MigrationResult] = field(default_factory=list)
    rollback_available: bool = True

    @property
    def all_success(self) -> bool:
        return all(r.success for r in self.results)

    @property
    def total_records(self) -> int:
        return sum(r.records_migrated for r in self.results)


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class MigrationManager:
    """Migrate legacy JSON wellness data to SQLite with safety guarantees."""

    def __init__(
        self,
        data_dir: Path,
        db: DatabaseManager | None = None,
    ) -> None:
        self.data_dir = data_dir
        self.db = db or DatabaseManager()
        self.db.initialize()
        self.backup_dir = data_dir / "migration_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # -- public API -------------------------------------------------------

    def migrate_all(self) -> MigrationReport:
        """Run all available migrations."""
        report = MigrationReport()

        report.results.append(self._migrate_tasks())
        report.results.append(self._migrate_mood_entries())
        report.results.append(self._migrate_energy_readings())
        report.results.append(self._migrate_sleep_logs())
        report.results.append(self._migrate_medication_logs())
        report.results.append(self._migrate_journal_entries())
        report.results.append(self._migrate_breathing_sessions())

        report.finished_at = datetime.now()
        return report

    def rollback(self, report: MigrationReport) -> bool:
        """Restore JSON backups if migration failed.

        Returns True if rollback succeeded.
        """
        if not report.rollback_available:
            logger.warning("Rollback not available for this report")
            return False

        try:
            for result in report.results:
                src = self.backup_dir / f"{result.module}_pre_migration.json"
                dst = self.data_dir / f"{result.module}.json"
                if src.exists():
                    shutil.copy2(str(src), str(dst))
                    logger.info("Rolled back %s", result.module)
            return True
        except (OSError, shutil.Error) as exc:
            logger.error("Rollback failed: %s", exc)
            return False

    # -- individual migrations --------------------------------------------

    def _migrate_tasks(self) -> MigrationResult:
        return self._migrate_json_file(
            module="tasks",
            table=TableName.TASKS,
            transform=self._transform_task,
        )

    def _migrate_mood_entries(self) -> MigrationResult:
        return self._migrate_json_file(
            module="mood_data",
            table=TableName.MOOD_ENTRIES,
            transform=self._transform_mood_entry,
        )

    def _migrate_energy_readings(self) -> MigrationResult:
        return self._migrate_json_file(
            module="energy_data",
            table=TableName.ENERGY_READINGS,
            transform=self._transform_energy_reading,
        )

    def _migrate_sleep_logs(self) -> MigrationResult:
        return self._migrate_json_file(
            module="sleep_data",
            table=TableName.SLEEP_LOGS,
            transform=self._transform_sleep_log,
        )

    def _migrate_medication_logs(self) -> MigrationResult:
        return self._migrate_json_file(
            module="medication_data",
            table=TableName.MEDICATION_LOGS,
            transform=self._transform_medication_log,
        )

    def _migrate_journal_entries(self) -> MigrationResult:
        return self._migrate_json_file(
            module="journal_data",
            table=TableName.JOURNAL_ENTRIES,
            transform=self._transform_journal_entry,
        )

    def _migrate_breathing_sessions(self) -> MigrationResult:
        return self._migrate_json_file(
            module="breathing_data",
            table=TableName.BREATHING_SESSIONS,
            transform=self._transform_breathing_session,
        )

    # -- generic migration helper -----------------------------------------

    def _migrate_json_file(
        self,
        module: str,
        table: TableName,
        transform: Any,
    ) -> MigrationResult:
        json_path = self.data_dir / f"{module}.json"
        if not json_path.exists():
            return MigrationResult(module=module, success=True, records_migrated=0)

        # Backup
        backup_path = self.backup_dir / f"{module}_pre_migration.json"
        try:
            shutil.copy2(str(json_path), str(backup_path))
        except (OSError, shutil.Error) as exc:
            return MigrationResult(
                module=module, success=False, error=f"Backup failed: {exc}"
            )

        # Migrate
        try:
            with open(json_path) as f:
                data = json.load(f)

            if not isinstance(data, list):
                data = [data] if data else []

            migrated = 0
            for item in data:
                row = transform(item)
                if row:
                    self.db.insert(table, **row)
                    migrated += 1

            # Archive original
            archive = self.data_dir / f"{module}_migrated_{datetime.now():%Y%m%d_%H%M%S}.json"
            json_path.rename(archive)

            return MigrationResult(
                module=module, success=True, records_migrated=migrated
            )
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            return MigrationResult(
                module=module, success=False, error=str(exc)
            )

    # -- transformers -----------------------------------------------------

    def _transform_task(self, item: dict[str, Any]) -> dict[str, Any] | None:
        return {
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "priority": item.get("priority", "medium"),
            "category": item.get("category", "Other"),
            "energy_required": item.get("energy_required", 5),
            "due_date": item.get("due_date"),
            "completed": 1 if item.get("completed") else 0,
            "completed_at": item.get("completed_at"),
            "notes": item.get("notes", ""),
            "created_at": item.get("created_at", datetime.now().isoformat()),
        }

    def _transform_mood_entry(self, item: dict[str, Any]) -> dict[str, Any] | None:
        return {
            "timestamp": item.get("timestamp", datetime.now().isoformat()),
            "mood_score": item.get("mood_score", 5),
            "energy_level": item.get("energy_level"),
            "anxiety_level": item.get("anxiety_level"),
            "notes": item.get("notes", ""),
        }

    def _transform_energy_reading(self, item: dict[str, Any]) -> dict[str, Any] | None:
        return {
            "timestamp": item.get("timestamp", datetime.now().isoformat()),
            "energy_level": item.get("energy_level", 5),
            "activity": item.get("activity", ""),
            "notes": item.get("notes", ""),
        }

    def _transform_sleep_log(self, item: dict[str, Any]) -> dict[str, Any] | None:
        return {
            "date": item.get("date", datetime.now().date().isoformat()),
            "bedtime": item.get("bedtime", "22:00"),
            "wake_time": item.get("wake_time", "07:00"),
            "quality": item.get("quality", 5),
            "duration_hours": item.get("duration_hours"),
            "notes": item.get("notes", ""),
        }

    def _transform_medication_log(self, item: dict[str, Any]) -> dict[str, Any] | None:
        return {
            "medication_name": item.get("name", "Unknown"),
            "dosage": item.get("dosage", ""),
            "frequency": item.get("frequency", ""),
            "scheduled_time": item.get("scheduled_time", datetime.now().isoformat()),
            "taken_time": item.get("taken_time"),
            "status": item.get("status", "pending"),
            "side_effects": item.get("side_effects", ""),
        }

    def _transform_journal_entry(self, item: dict[str, Any]) -> dict[str, Any] | None:
        return {
            "timestamp": item.get("timestamp", datetime.now().isoformat()),
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "mood_score": item.get("mood_score"),
            "tags": ",".join(item.get("tags", [])),
            "prompt": item.get("prompt", ""),
        }

    def _transform_breathing_session(self, item: dict[str, Any]) -> dict[str, Any] | None:
        return {
            "timestamp": item.get("timestamp", datetime.now().isoformat()),
            "technique": item.get("technique", "unknown"),
            "duration_seconds": item.get("duration_seconds", 0),
            "cycles": item.get("cycles"),
            "pre_anxiety": item.get("pre_anxiety"),
            "post_anxiety": item.get("post_anxiety"),
            "notes": item.get("notes", ""),
        }
