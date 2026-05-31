"""
Tests for DatabaseManager (src/core/database.py).

Covers schema creation, CRUD operations, query builder, settings,
transactions, migration bookkeeping, backup/restore, and export.
"""

import json

import pytest

from core.database import (
    CURRENT_SCHEMA_VERSION,
    DatabaseManager,
    QueryResult,
    TableName,
)


@pytest.fixture
def db(tmp_data_dir):
    database = DatabaseManager(db_path=tmp_data_dir / "test.db")
    database.initialize()
    yield database
    database.close()


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

class TestSchemaCreation:

    def test_initialize_creates_db_file(self, tmp_data_dir):
        db_path = tmp_data_dir / "init_test.db"
        db = DatabaseManager(db_path=db_path)
        db.initialize()
        assert db_path.exists()
        db.close()

    def test_schema_version_recorded(self, db):
        result = db.execute("SELECT MAX(version) AS v FROM schema_version")
        assert result.rows[0]["v"] == CURRENT_SCHEMA_VERSION

    def test_all_tables_exist(self, db):
        result = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        table_names = {r["name"] for r in result.rows}

        for tbl in TableName:
            assert tbl.value in table_names, f"Table {tbl.value} not found"

    def test_indexes_created(self, db):
        result = db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        )
        index_names = {r["name"] for r in result.rows}
        assert "idx_mood_timestamp" in index_names
        assert "idx_tasks_due" in index_names
        assert "idx_settings_category" in index_names

    def test_reinitialize_is_idempotent(self, db):
        db.initialize()
        db.initialize()
        # Should not raise or duplicate data
        result = db.execute("SELECT COUNT(*) AS cnt FROM schema_version")
        assert result.rows[0]["cnt"] >= 1

    def test_context_manager(self, tmp_data_dir):
        db_path = tmp_data_dir / "ctx_test.db"
        with DatabaseManager(db_path=db_path) as db:
            db.insert(TableName.MOOD_ENTRIES, mood_score=5)
            assert db.count(TableName.MOOD_ENTRIES) == 1
        # Connection should be closed; db_path should still exist
        assert db_path.exists()


# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------

class TestInsert:

    def test_insert_returns_id(self, db):
        row_id = db.insert(TableName.MOOD_ENTRIES, mood_score=7, notes="Good")
        assert isinstance(row_id, int)
        assert row_id >= 1

    def test_insert_auto_increment(self, db):
        id1 = db.insert(TableName.MOOD_ENTRIES, mood_score=5)
        id2 = db.insert(TableName.MOOD_ENTRIES, mood_score=6)
        assert id2 > id1

    def test_insert_no_data_raises(self, db):
        with pytest.raises(ValueError, match="No data"):
            db.insert(TableName.MOOD_ENTRIES)

    def test_insert_constraint_violation(self, db):
        import sqlite3
        with pytest.raises(sqlite3.IntegrityError):
            db.insert(TableName.MOOD_ENTRIES, mood_score=99)  # CHECK constraint 1-10

    def test_insert_task(self, db):
        row_id = db.insert(
            TableName.TASKS,
            title="Test task",
            priority="high",
            category="Work",
            energy_required=7,
        )
        task = db.get_by_id(TableName.TASKS, row_id)
        assert task is not None
        assert task["title"] == "Test task"
        assert task["completed"] == 0  # default


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------

class TestGetById:

    def test_get_existing(self, db):
        row_id = db.insert(TableName.MOOD_ENTRIES, mood_score=8, notes="Great")
        row = db.get_by_id(TableName.MOOD_ENTRIES, row_id)
        assert row is not None
        assert row["mood_score"] == 8
        assert row["notes"] == "Great"

    def test_get_nonexistent(self, db):
        row = db.get_by_id(TableName.MOOD_ENTRIES, 999999)
        assert row is None


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class TestUpdate:

    def test_update_row(self, db):
        row_id = db.insert(TableName.TASKS, title="Original", priority="low", category="Work")
        affected = db.update(TableName.TASKS, row_id, title="Updated", priority="high")
        assert affected == 1

        row = db.get_by_id(TableName.TASKS, row_id)
        assert row["title"] == "Updated"
        assert row["priority"] == "high"

    def test_update_no_data_raises(self, db):
        row_id = db.insert(TableName.TASKS, title="X", priority="low", category="Work")
        with pytest.raises(ValueError, match="No data"):
            db.update(TableName.TASKS, row_id)

    def test_update_nonexistent_returns_zero(self, db):
        affected = db.update(TableName.TASKS, 999999, title="Ghost")
        assert affected == 0


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class TestDelete:

    def test_delete_row(self, db):
        row_id = db.insert(TableName.MOOD_ENTRIES, mood_score=3)
        affected = db.delete(TableName.MOOD_ENTRIES, row_id)
        assert affected == 1
        assert db.get_by_id(TableName.MOOD_ENTRIES, row_id) is None

    def test_delete_nonexistent_returns_zero(self, db):
        affected = db.delete(TableName.MOOD_ENTRIES, 999999)
        assert affected == 0


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

class TestQuery:

    def test_query_all(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=5)
        db.insert(TableName.MOOD_ENTRIES, mood_score=8)

        result = db.query(TableName.MOOD_ENTRIES)
        assert isinstance(result, QueryResult)
        assert result.row_count == 2
        assert len(result.rows) == 2

    def test_query_with_where(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=3)
        db.insert(TableName.MOOD_ENTRIES, mood_score=9)

        result = db.query(
            TableName.MOOD_ENTRIES,
            where="mood_score >= ?",
            params=(5,),
        )
        assert result.row_count == 1
        assert result.rows[0]["mood_score"] == 9

    def test_query_with_order(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=3)
        db.insert(TableName.MOOD_ENTRIES, mood_score=9)
        db.insert(TableName.MOOD_ENTRIES, mood_score=6)

        result = db.query(
            TableName.MOOD_ENTRIES,
            order_by="mood_score DESC",
        )
        scores = [r["mood_score"] for r in result.rows]
        assert scores == [9, 6, 3]

    def test_query_with_limit(self, db):
        for i in range(5):
            db.insert(TableName.MOOD_ENTRIES, mood_score=i + 1)

        result = db.query(TableName.MOOD_ENTRIES, limit=2)
        assert result.row_count == 2

    def test_query_with_offset(self, db):
        for i in range(5):
            db.insert(TableName.MOOD_ENTRIES, mood_score=i + 1)

        result = db.query(
            TableName.MOOD_ENTRIES,
            order_by="mood_score ASC",
            limit=2,
            offset=3,
        )
        assert result.row_count == 2
        scores = [r["mood_score"] for r in result.rows]
        assert scores == [4, 5]

    def test_query_specific_columns(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=7, notes="hello")
        result = db.query(TableName.MOOD_ENTRIES, columns="mood_score, notes")
        row = result.rows[0]
        assert "mood_score" in row
        assert "notes" in row

    def test_query_empty_table(self, db):
        result = db.query(TableName.MOOD_ENTRIES)
        assert result.row_count == 0
        assert result.rows == []


# ---------------------------------------------------------------------------
# Count
# ---------------------------------------------------------------------------

class TestCount:

    def test_count_all(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=5)
        db.insert(TableName.MOOD_ENTRIES, mood_score=8)
        assert db.count(TableName.MOOD_ENTRIES) == 2

    def test_count_with_where(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=3)
        db.insert(TableName.MOOD_ENTRIES, mood_score=9)

        assert db.count(TableName.MOOD_ENTRIES, where="mood_score > ?", params=(5,)) == 1

    def test_count_empty(self, db):
        assert db.count(TableName.MOOD_ENTRIES) == 0


# ---------------------------------------------------------------------------
# Execute (raw SQL)
# ---------------------------------------------------------------------------

class TestExecute:

    def test_execute_select(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=7)
        result = db.execute("SELECT * FROM mood_entries WHERE mood_score = ?", (7,))
        assert result.row_count == 1

    def test_execute_insert(self, db):
        result = db.execute(
            "INSERT INTO mood_entries (mood_score) VALUES (?)", (6,)
        )
        assert result.last_row_id is not None


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class TestSettings:

    def test_set_and_get_setting(self, db):
        db.set_setting("theme", "dark")
        assert db.get_setting("theme") == "dark"

    def test_get_setting_default(self, db):
        assert db.get_setting("nonexistent") is None
        assert db.get_setting("nonexistent", "fallback") == "fallback"

    def test_update_setting(self, db):
        db.set_setting("theme", "light")
        db.set_setting("theme", "dark")
        assert db.get_setting("theme") == "dark"

    def test_setting_with_category(self, db):
        db.set_setting("font_size", "14", category="appearance")
        result = db.query(
            TableName.SETTINGS,
            where="key = ?",
            params=("font_size",),
        )
        assert result.rows[0]["category"] == "appearance"


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

class TestTransactions:

    def test_transaction_commits(self, db):
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO mood_entries (mood_score) VALUES (?)", (7,)
            )

        assert db.count(TableName.MOOD_ENTRIES) == 1

    def test_transaction_rollback_on_error(self, db):
        try:
            with db.transaction() as conn:
                conn.execute(
                    "INSERT INTO mood_entries (mood_score) VALUES (?)", (5,)
                )
                raise RuntimeError("Force rollback")
        except RuntimeError:
            pass

        assert db.count(TableName.MOOD_ENTRIES) == 0


# ---------------------------------------------------------------------------
# Backup & restore
# ---------------------------------------------------------------------------

class TestBackupRestore:

    def test_backup_creates_file(self, db, tmp_data_dir):
        db.insert(TableName.MOOD_ENTRIES, mood_score=7)
        backup_path = db.backup()

        assert backup_path.exists()
        assert backup_path.stat().st_size > 0

    def test_backup_custom_path(self, db, tmp_data_dir):
        custom_path = tmp_data_dir / "custom_backup.db"
        result = db.backup(backup_path=custom_path)
        assert result == custom_path
        assert custom_path.exists()

    def test_restore_from_backup(self, db, tmp_data_dir):
        # Insert data and backup
        db.insert(TableName.MOOD_ENTRIES, mood_score=7, notes="Before")
        backup_path = db.backup()

        # Add more data after backup
        db.insert(TableName.MOOD_ENTRIES, mood_score=3, notes="After")
        assert db.count(TableName.MOOD_ENTRIES) == 2

        # Restore
        db.restore(backup_path)
        assert db.count(TableName.MOOD_ENTRIES) == 1

        row = db.query(TableName.MOOD_ENTRIES).rows[0]
        assert row["notes"] == "Before"

    def test_restore_nonexistent_raises(self, db, tmp_data_dir):
        with pytest.raises(FileNotFoundError):
            db.restore(tmp_data_dir / "nonexistent.db")

    def test_restore_invalid_file_raises(self, db, tmp_data_dir):
        bad = tmp_data_dir / "bad.db"
        bad.write_text("not a database")
        with pytest.raises((ValueError, Exception)):
            db.restore(bad)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

class TestExport:

    def test_export_table_to_json(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=7, notes="test")
        json_str = db.export_table_to_json(TableName.MOOD_ENTRIES)

        data = json.loads(json_str)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["mood_score"] == 7

    def test_export_all_to_json(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=5)
        db.insert(TableName.TASKS, title="Task", priority="medium", category="Work")

        json_str = db.export_all_to_json()
        data = json.loads(json_str)

        assert "exported_at" in data
        assert "schema_version" in data
        assert "mood_entries" in data
        assert "tasks" in data
        assert len(data["mood_entries"]) == 1
        assert len(data["tasks"]) == 1

    def test_export_table_to_csv(self, db):
        db.insert(TableName.MOOD_ENTRIES, mood_score=7, notes="csv test")
        csv_str = db.export_table_to_csv(TableName.MOOD_ENTRIES)

        assert "mood_score" in csv_str  # header
        assert "7" in csv_str
        assert "csv test" in csv_str

    def test_export_empty_table_csv(self, db):
        csv_str = db.export_table_to_csv(TableName.MOOD_ENTRIES)
        assert csv_str == ""

    def test_export_all_to_file_json(self, db, tmp_data_dir):
        db.insert(TableName.MOOD_ENTRIES, mood_score=5)
        output = tmp_data_dir / "export.json"

        result = db.export_all_to_file(output, fmt="json")
        assert result.exists()

        data = json.loads(result.read_text())
        assert "mood_entries" in data

    def test_export_all_to_file_csv(self, db, tmp_data_dir):
        db.insert(TableName.MOOD_ENTRIES, mood_score=5)
        output = tmp_data_dir / "csv_export"

        result = db.export_all_to_file(output, fmt="csv")
        assert result.is_dir()

        csv_files = list(result.glob("*.csv"))
        assert len(csv_files) >= 1

    def test_export_unsupported_format(self, db, tmp_data_dir):
        with pytest.raises(ValueError, match="Unsupported"):
            db.export_all_to_file(tmp_data_dir / "out", fmt="xml")


# ---------------------------------------------------------------------------
# Lifecycle & repr
# ---------------------------------------------------------------------------

class TestLifecycle:

    def test_close_and_reopen(self, tmp_data_dir):
        db_path = tmp_data_dir / "lifecycle.db"
        db = DatabaseManager(db_path=db_path)
        db.initialize()
        db.insert(TableName.MOOD_ENTRIES, mood_score=5)
        db.close()

        db2 = DatabaseManager(db_path=db_path)
        db2.initialize()
        assert db2.count(TableName.MOOD_ENTRIES) == 1
        db2.close()

    def test_repr(self, db):
        r = repr(db)
        assert "DatabaseManager" in r
        assert "test.db" in r

    def test_db_path_property(self, db, tmp_data_dir):
        assert db.db_path == tmp_data_dir / "test.db"


# ---------------------------------------------------------------------------
# Multiple table CRUD
# ---------------------------------------------------------------------------

class TestMultiTableCrud:

    def test_journal_entry(self, db):
        row_id = db.insert(
            TableName.JOURNAL_ENTRIES,
            content="Today was good",
            title="Day 1",
            tags="mood,wellness",
        )
        entry = db.get_by_id(TableName.JOURNAL_ENTRIES, row_id)
        assert entry["content"] == "Today was good"
        assert entry["is_private"] == 1  # default

    def test_sleep_log(self, db):
        row_id = db.insert(
            TableName.SLEEP_LOGS,
            date="2026-04-05",
            bedtime="23:00",
            wake_time="07:00",
            quality=7,
            duration_hours=8.0,
        )
        log = db.get_by_id(TableName.SLEEP_LOGS, row_id)
        assert log["quality"] == 7
        assert log["duration_hours"] == 8.0

    def test_medication_log(self, db):
        row_id = db.insert(
            TableName.MEDICATION_LOGS,
            medication_name="Sertraline",
            dosage="50mg",
            frequency="daily",
            scheduled_time="08:00",
            status="taken",
        )
        log = db.get_by_id(TableName.MEDICATION_LOGS, row_id)
        assert log["medication_name"] == "Sertraline"
        assert log["status"] == "taken"

    def test_energy_reading(self, db):
        row_id = db.insert(
            TableName.ENERGY_READINGS,
            energy_level=7,
            activity="walking",
            caffeine=1,
        )
        reading = db.get_by_id(TableName.ENERGY_READINGS, row_id)
        assert reading["energy_level"] == 7

    def test_achievement(self, db):
        row_id = db.insert(
            TableName.ACHIEVEMENTS,
            name="First Task",
            description="Completed first task",
            category="productivity",
            progress=1.0,
            target=1.0,
        )
        ach = db.get_by_id(TableName.ACHIEVEMENTS, row_id)
        assert ach["name"] == "First Task"

    def test_crisis_plan(self, db):
        row_id = db.insert(
            TableName.CRISIS_PLANS,
            name="My Plan",
            warning_signs="racing thoughts",
            emergency_numbers="911",
        )
        plan = db.get_by_id(TableName.CRISIS_PLANS, row_id)
        assert plan["name"] == "My Plan"
        assert plan["is_active"] == 1  # default

    def test_breathing_session(self, db):
        row_id = db.insert(
            TableName.BREATHING_SESSIONS,
            technique="4-7-8",
            duration_seconds=120,
            cycles=4,
            pre_anxiety=7,
            post_anxiety=3,
        )
        session = db.get_by_id(TableName.BREATHING_SESSIONS, row_id)
        assert session["technique"] == "4-7-8"
        assert session["pre_anxiety"] == 7
