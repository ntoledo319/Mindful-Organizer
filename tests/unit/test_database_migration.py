"""
Tests for database schema migrations.

Validates that v1→v2 migration preserves existing data and creates
new tables correctly.
"""

import sqlite3
from pathlib import Path

from core.database import CURRENT_SCHEMA_VERSION, DatabaseManager, TableName


class TestV1ToV2Migration:
    def _create_v1_schema(self, db_path: Path) -> None:
        """Create a v1 schema by initializing with DatabaseManager, then removing
        the v2 additions (diary_cards) and resetting the version to 1."""
        db = DatabaseManager(db_path=db_path)
        db.initialize()
        conn = sqlite3.connect(str(db_path))
        conn.execute("DROP TABLE IF EXISTS diary_cards")
        conn.execute("DELETE FROM schema_version")
        conn.execute("INSERT INTO schema_version (version) VALUES (1)")
        conn.commit()
        conn.close()
        db.close()

    def _insert_v1_data(self, db_path: Path) -> None:
        conn = sqlite3.connect(str(db_path))
        conn.execute("INSERT INTO mood_entries (mood_score, notes) VALUES (7, 'Good day')")
        conn.execute("INSERT INTO tasks (title, completed) VALUES ('Buy milk', 0)")
        conn.commit()
        conn.close()

    def test_migration_creates_diary_cards_table(self, tmp_path: Path) -> None:
        db_path = tmp_path / "migrate_test.db"
        self._create_v1_schema(db_path)
        self._insert_v1_data(db_path)

        db = DatabaseManager(db_path=db_path)
        db.initialize()

        # diary_cards should now exist
        result = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='diary_cards'"
        )
        assert len(result.rows) == 1
        db.close()

    def test_migration_preserves_existing_data(self, tmp_path: Path) -> None:
        db_path = tmp_path / "migrate_test.db"
        self._create_v1_schema(db_path)
        self._insert_v1_data(db_path)

        db = DatabaseManager(db_path=db_path)
        db.initialize()

        moods = db.query(TableName.MOOD_ENTRIES)
        assert moods.row_count == 1
        assert moods.rows[0]["notes"] == "Good day"

        tasks = db.query(TableName.TASKS)
        assert tasks.row_count == 1
        assert tasks.rows[0]["title"] == "Buy milk"
        db.close()

    def test_migration_updates_schema_version(self, tmp_path: Path) -> None:
        db_path = tmp_path / "migrate_test.db"
        self._create_v1_schema(db_path)

        db = DatabaseManager(db_path=db_path)
        db.initialize()

        result = db.execute("SELECT MAX(version) AS v FROM schema_version")
        assert result.rows[0]["v"] == CURRENT_SCHEMA_VERSION
        db.close()

    def test_migration_is_idempotent(self, tmp_path: Path) -> None:
        db_path = tmp_path / "migrate_test.db"
        self._create_v1_schema(db_path)
        self._insert_v1_data(db_path)

        db = DatabaseManager(db_path=db_path)
        db.initialize()
        db.initialize()  # second call should be safe

        # Data should not be duplicated
        moods = db.query(TableName.MOOD_ENTRIES)
        assert moods.row_count == 1
        db.close()
