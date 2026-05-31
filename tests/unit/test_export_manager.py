"""
Tests for ExportManager (src/core/export_manager.py).

Covers JSON export, CSV export, JSON import, settings export/import,
and selective export.
"""

import json
from datetime import date, timedelta

import pytest

from core.database import DatabaseManager, TableName
from core.export_manager import (
    DataCategory,
    ExportFormat,
    ExportManager,
    ExportOptions,
)


@pytest.fixture
def db(tmp_data_dir):
    database = DatabaseManager(db_path=tmp_data_dir / "test.db")
    database.initialize()
    yield database
    database.close()


@pytest.fixture
def em(db):
    return ExportManager(db)


@pytest.fixture
def populated_db(db):
    """Database with some sample data."""
    db.insert(TableName.MOOD_ENTRIES, mood_score=7, energy_level=6, notes="Good day")
    db.insert(TableName.MOOD_ENTRIES, mood_score=5, energy_level=4, notes="Meh day")
    db.insert(TableName.TASKS, title="Test task", priority="medium", category="Work")
    db.set_setting("theme", "dark", category="appearance")
    db.set_setting("font_size", "14", category="appearance")
    return db


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------


class TestExportJson:
    def test_export_json(self, em, populated_db, tmp_data_dir):
        output = tmp_data_dir / "export.json"
        opts = ExportOptions(format=ExportFormat.JSON, output_path=output)
        result_path = em.export(opts)

        assert result_path.exists()
        data = json.loads(result_path.read_text())
        assert "mood_entries" in data
        assert "exported_at" in data
        assert "schema_version" in data

    def test_export_json_with_date_range(self, em, populated_db, tmp_data_dir):
        output = tmp_data_dir / "export_range.json"
        opts = ExportOptions(
            format=ExportFormat.JSON,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
            output_path=output,
        )
        result_path = em.export(opts)
        assert result_path.exists()

    def test_export_json_anonymized(self, em, populated_db, tmp_data_dir):
        output = tmp_data_dir / "export_anon.json"
        opts = ExportOptions(
            format=ExportFormat.JSON,
            anonymize=True,
            output_path=output,
        )
        result_path = em.export(opts)
        data = json.loads(result_path.read_text())
        assert data["anonymized"] is True


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------


class TestExportCsv:
    def test_export_csv(self, em, populated_db, tmp_data_dir):
        output = tmp_data_dir / "csv_export"
        opts = ExportOptions(format=ExportFormat.CSV, output_path=output)
        result_path = em.export(opts)

        assert result_path.is_dir()
        csv_files = list(result_path.glob("*.csv"))
        assert len(csv_files) >= 1


# ---------------------------------------------------------------------------
# JSON import
# ---------------------------------------------------------------------------


class TestImportJson:
    def test_import_json(self, em, populated_db, tmp_data_dir):
        # First export
        export_path = tmp_data_dir / "for_import.json"
        opts = ExportOptions(format=ExportFormat.JSON, output_path=export_path)
        em.export(opts)

        # Create a fresh DB and import
        db2 = DatabaseManager(db_path=tmp_data_dir / "import_target.db")
        db2.initialize()
        try:
            em2 = ExportManager(db2)

            counts = em2.import_from_json(export_path)
            assert "mood_entries" in counts
            assert counts["mood_entries"] >= 2
        finally:
            db2.close()

    def test_import_validation_valid(self, em, populated_db, tmp_data_dir):
        export_path = tmp_data_dir / "valid_export.json"
        opts = ExportOptions(format=ExportFormat.JSON, output_path=export_path)
        em.export(opts)

        validation = em.validate_import(export_path)
        assert validation.is_valid is True
        assert len(validation.errors) == 0

    def test_import_validation_missing_file(self, em, tmp_data_dir):
        validation = em.validate_import(tmp_data_dir / "nonexistent.json")
        assert validation.is_valid is False
        assert any("not found" in e.lower() for e in validation.errors)

    def test_import_validation_invalid_json(self, em, tmp_data_dir):
        bad_file = tmp_data_dir / "bad.json"
        bad_file.write_text("{not valid json", encoding="utf-8")

        validation = em.validate_import(bad_file)
        assert validation.is_valid is False

    def test_import_validation_wrong_structure(self, em, tmp_data_dir):
        bad_file = tmp_data_dir / "bad_structure.json"
        bad_file.write_text('"just a string"', encoding="utf-8")

        validation = em.validate_import(bad_file)
        assert validation.is_valid is False

    def test_import_with_merge(self, em, populated_db, tmp_data_dir):
        export_path = tmp_data_dir / "merge_export.json"
        opts = ExportOptions(format=ExportFormat.JSON, output_path=export_path)
        em.export(opts)

        # Import again with merge
        counts = em.import_from_json(export_path, merge=True)
        assert counts.get("mood_entries", 0) >= 2


# ---------------------------------------------------------------------------
# Settings export / import
# ---------------------------------------------------------------------------


class TestSettingsExportImport:
    def test_export_settings(self, em, populated_db, tmp_data_dir):
        output = tmp_data_dir / "settings_export.json"
        result_path = em.export_settings(output_path=output)

        assert result_path.exists()
        data = json.loads(result_path.read_text())
        assert "settings" in data
        assert data["settings"]["theme"] == "dark"

    def test_import_settings(self, em, populated_db, tmp_data_dir):
        # Export first
        output = tmp_data_dir / "settings.json"
        em.export_settings(output_path=output)

        # Import into fresh db
        db2 = DatabaseManager(db_path=tmp_data_dir / "settings_target.db")
        db2.initialize()
        try:
            em2 = ExportManager(db2)

            count = em2.import_settings(output)
            assert count >= 2

            # Verify settings were applied
            assert db2.get_setting("theme") == "dark"
            assert db2.get_setting("font_size") == "14"
        finally:
            db2.close()


# ---------------------------------------------------------------------------
# Selective export
# ---------------------------------------------------------------------------


class TestSelectiveExport:
    def test_selective_categories(self, em, populated_db, tmp_data_dir):
        output = tmp_data_dir / "selective.json"
        opts = ExportOptions(
            format=ExportFormat.JSON,
            categories=[DataCategory.MOOD],
            output_path=output,
        )
        result_path = em.export(opts)

        data = json.loads(result_path.read_text())
        assert "mood_entries" in data
        # Tasks should NOT be included
        assert "tasks" not in data

    def test_multiple_categories(self, em, populated_db, tmp_data_dir):
        output = tmp_data_dir / "multi.json"
        opts = ExportOptions(
            format=ExportFormat.JSON,
            categories=[DataCategory.MOOD, DataCategory.TASKS],
            output_path=output,
        )
        result_path = em.export(opts)
        data = json.loads(result_path.read_text())

        assert "mood_entries" in data
        assert "tasks" in data


# ---------------------------------------------------------------------------
# Wellness report
# ---------------------------------------------------------------------------


class TestWellnessReport:
    def test_generate_wellness_report(self, em, populated_db):
        sections = em.generate_wellness_report(days=30)
        assert len(sections) >= 2  # at least overview + disclaimer

        titles = [s.title for s in sections]
        assert "Report Overview" in titles
        assert "Disclaimer" in titles

    def test_wellness_report_to_text(self, em, populated_db):
        sections = em.generate_wellness_report(days=30)
        text = em.wellness_report_to_text(sections)

        assert "WELLNESS REPORT" in text
        assert "Disclaimer" in text
