"""
Unified SQLite database manager for Mindful Organizer.

Replaces scattered JSON files with a single, thread-safe SQLite database
supporting migrations, CRUD operations, backup/restore, and data export.
"""

import csv
import io
import json
import logging
import shutil
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple, Union

logger = logging.getLogger(__name__)

DATA_DIR = Path.home() / ".mindful_optimizer"
DB_FILE = DATA_DIR / "mindful_organizer.db"

CURRENT_SCHEMA_VERSION = 1

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER NOT NULL,
    applied_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS mood_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL DEFAULT (datetime('now')),
    mood_score      INTEGER NOT NULL CHECK (mood_score BETWEEN 1 AND 10),
    energy_level    INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    anxiety_level   INTEGER CHECK (anxiety_level BETWEEN 0 AND 10),
    irritability    INTEGER CHECK (irritability BETWEEN 0 AND 10),
    emotions        TEXT,
    triggers        TEXT,
    notes           TEXT,
    context         TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT    NOT NULL,
    description     TEXT,
    priority        TEXT    NOT NULL DEFAULT 'medium',
    category        TEXT    NOT NULL DEFAULT 'Other',
    energy_required INTEGER DEFAULT 5,
    due_date        TEXT,
    completed       INTEGER NOT NULL DEFAULT 0,
    completed_at    TEXT,
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sleep_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL,
    bedtime         TEXT    NOT NULL,
    wake_time       TEXT    NOT NULL,
    quality         INTEGER NOT NULL CHECK (quality BETWEEN 1 AND 10),
    duration_hours  REAL,
    interruptions   INTEGER DEFAULT 0,
    interruption_details TEXT,
    sleep_aids      TEXT,
    dreams          TEXT,
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS medication_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_name TEXT    NOT NULL,
    dosage          TEXT    NOT NULL,
    frequency       TEXT    NOT NULL,
    scheduled_time  TEXT    NOT NULL,
    taken_time      TEXT,
    status          TEXT    NOT NULL DEFAULT 'pending' CHECK (status IN ('taken','missed','late','skipped','pending')),
    side_effects    TEXT,
    notes           TEXT,
    supply_count    INTEGER,
    prescriber      TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL DEFAULT (datetime('now')),
    title           TEXT,
    content         TEXT    NOT NULL,
    mood_score      INTEGER CHECK (mood_score BETWEEN 1 AND 10),
    tags            TEXT,
    prompt          TEXT,
    is_private      INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS energy_readings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL DEFAULT (datetime('now')),
    energy_level    INTEGER NOT NULL CHECK (energy_level BETWEEN 1 AND 10),
    activity        TEXT,
    food_intake     TEXT,
    caffeine        INTEGER DEFAULT 0,
    exercise        INTEGER DEFAULT 0,
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS achievements (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    description     TEXT,
    category        TEXT,
    earned_at       TEXT,
    progress        REAL    NOT NULL DEFAULT 0.0,
    target          REAL    NOT NULL DEFAULT 1.0,
    icon            TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notifications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    type            TEXT    NOT NULL,
    title           TEXT    NOT NULL,
    message         TEXT    NOT NULL,
    priority        TEXT    NOT NULL DEFAULT 'medium',
    scheduled_at    TEXT    NOT NULL,
    delivered_at    TEXT,
    read_at         TEXT,
    dismissed_at    TEXT,
    snoozed_until   TEXT,
    recurring       TEXT,
    metadata        TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS crisis_plans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    warning_signs   TEXT,
    coping_strategies TEXT,
    support_contacts TEXT,
    professional_contacts TEXT,
    safe_environment TEXT,
    emergency_numbers TEXT,
    personal_notes  TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS breathing_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL DEFAULT (datetime('now')),
    technique       TEXT    NOT NULL,
    duration_seconds INTEGER NOT NULL,
    cycles          INTEGER,
    pre_anxiety     INTEGER CHECK (pre_anxiety BETWEEN 0 AND 10),
    post_anxiety    INTEGER CHECK (post_anxiety BETWEEN 0 AND 10),
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS settings (
    key             TEXT PRIMARY KEY,
    value           TEXT    NOT NULL,
    category        TEXT    NOT NULL DEFAULT 'general',
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_mood_timestamp ON mood_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_sleep_date ON sleep_logs(date);
CREATE INDEX IF NOT EXISTS idx_medication_status ON medication_logs(status);
CREATE INDEX IF NOT EXISTS idx_journal_timestamp ON journal_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_energy_timestamp ON energy_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_notifications_scheduled ON notifications(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_breathing_timestamp ON breathing_sessions(timestamp);
CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category);
"""

# Migration definitions: each key is the target version,
# value is a list of SQL statements to run.
_MIGRATIONS: Dict[int, List[str]] = {
    # Version 1 is the initial schema created by _SCHEMA_SQL.
    # Future migrations go here, e.g.:
    # 2: [
    #     "ALTER TABLE mood_entries ADD COLUMN location TEXT;",
    # ],
}


class TableName(Enum):
    """Valid table names for type-safe references."""
    MOOD_ENTRIES = "mood_entries"
    TASKS = "tasks"
    SLEEP_LOGS = "sleep_logs"
    MEDICATION_LOGS = "medication_logs"
    JOURNAL_ENTRIES = "journal_entries"
    ENERGY_READINGS = "energy_readings"
    ACHIEVEMENTS = "achievements"
    NOTIFICATIONS = "notifications"
    CRISIS_PLANS = "crisis_plans"
    BREATHING_SESSIONS = "breathing_sessions"
    SETTINGS = "settings"


@dataclass
class QueryResult:
    """Container for query results."""
    rows: List[Dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    last_row_id: Optional[int] = None


class DatabaseManager:
    """Thread-safe SQLite database manager with migration support.

    Usage::

        db = DatabaseManager()
        db.initialize()

        # Insert
        db.insert(TableName.MOOD_ENTRIES, mood_score=7, notes="Good day")

        # Query
        results = db.query(TableName.MOOD_ENTRIES, where="mood_score >= ?", params=(5,))

        # Transaction context manager
        with db.transaction() as conn:
            conn.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))

        db.close()
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self._db_path = db_path or DB_FILE
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def _get_connection(self) -> sqlite3.Connection:
        """Return a thread-local connection, creating one if necessary."""
        conn: Optional[sqlite3.Connection] = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(str(self._db_path), timeout=30)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            self._local.conn = conn
        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager that wraps a block in a SQLite transaction.

        Commits on clean exit, rolls back on exception.
        """
        conn = self._get_connection()
        with self._lock:
            try:
                conn.execute("BEGIN")
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    # ------------------------------------------------------------------
    # Initialization & migration
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Create schema and run any pending migrations."""
        conn = self._get_connection()
        with self._lock:
            conn.executescript(_SCHEMA_SQL)
            self._apply_migrations(conn)
        logger.info("Database initialized at %s", self._db_path)

    def _current_version(self, conn: sqlite3.Connection) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(version), 0) AS v FROM schema_version"
        ).fetchone()
        return int(row["v"]) if row else 0

    def _apply_migrations(self, conn: sqlite3.Connection) -> None:
        current = self._current_version(conn)
        if current >= CURRENT_SCHEMA_VERSION:
            # Record initial version if table is empty
            if current == 0:
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (CURRENT_SCHEMA_VERSION,),
                )
                conn.commit()
            return

        for version in sorted(_MIGRATIONS.keys()):
            if version <= current:
                continue
            logger.info("Applying migration to version %d", version)
            for sql in _MIGRATIONS[version]:
                conn.execute(sql)
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)", (version,)
            )
            conn.commit()

        # Ensure we always mark the current version
        if self._current_version(conn) < CURRENT_SCHEMA_VERSION:
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (CURRENT_SCHEMA_VERSION,),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def insert(self, table: TableName, **data: Any) -> int:
        """Insert a row and return the new row id."""
        if not data:
            raise ValueError("No data provided for insert")
        cols = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        sql = f"INSERT INTO {table.value} ({cols}) VALUES ({placeholders})"
        conn = self._get_connection()
        with self._lock:
            cursor = conn.execute(sql, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid  # type: ignore[return-value]

    def update(
        self,
        table: TableName,
        row_id: int,
        **data: Any,
    ) -> int:
        """Update a row by id. Returns number of rows affected."""
        if not data:
            raise ValueError("No data provided for update")
        set_clause = ", ".join(f"{k} = ?" for k in data)
        sql = f"UPDATE {table.value} SET {set_clause} WHERE id = ?"
        conn = self._get_connection()
        with self._lock:
            cursor = conn.execute(sql, (*data.values(), row_id))
            conn.commit()
            return cursor.rowcount

    def delete(self, table: TableName, row_id: int) -> int:
        """Delete a row by id. Returns number of rows affected."""
        sql = f"DELETE FROM {table.value} WHERE id = ?"
        conn = self._get_connection()
        with self._lock:
            cursor = conn.execute(sql, (row_id,))
            conn.commit()
            return cursor.rowcount

    def get_by_id(self, table: TableName, row_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single row by id."""
        sql = f"SELECT * FROM {table.value} WHERE id = ?"
        conn = self._get_connection()
        row = conn.execute(sql, (row_id,)).fetchone()
        return dict(row) if row else None

    def query(
        self,
        table: TableName,
        columns: str = "*",
        where: str = "",
        params: Sequence[Any] = (),
        order_by: str = "",
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> QueryResult:
        """Flexible query builder returning a QueryResult."""
        sql = f"SELECT {columns} FROM {table.value}"
        if where:
            sql += f" WHERE {where}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {limit}"
        if offset:
            sql += f" OFFSET {offset}"

        conn = self._get_connection()
        rows = conn.execute(sql, params).fetchall()
        return QueryResult(
            rows=[dict(r) for r in rows],
            row_count=len(rows),
        )

    def execute(self, sql: str, params: Sequence[Any] = ()) -> QueryResult:
        """Execute arbitrary SQL. Use with caution."""
        conn = self._get_connection()
        with self._lock:
            cursor = conn.execute(sql, params)
            if cursor.description:
                rows = cursor.fetchall()
                result = QueryResult(
                    rows=[dict(r) for r in rows],
                    row_count=len(rows),
                    last_row_id=cursor.lastrowid,
                )
            else:
                conn.commit()
                result = QueryResult(
                    row_count=cursor.rowcount,
                    last_row_id=cursor.lastrowid,
                )
            return result

    def count(self, table: TableName, where: str = "", params: Sequence[Any] = ()) -> int:
        """Return row count for a table, optionally filtered."""
        sql = f"SELECT COUNT(*) AS cnt FROM {table.value}"
        if where:
            sql += f" WHERE {where}"
        conn = self._get_connection()
        row = conn.execute(sql, params).fetchone()
        return int(row["cnt"]) if row else 0

    # ------------------------------------------------------------------
    # Settings convenience
    # ------------------------------------------------------------------

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a setting value by key."""
        conn = self._get_connection()
        row = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str, category: str = "general") -> None:
        """Insert or update a setting."""
        conn = self._get_connection()
        now = datetime.now().isoformat()
        with self._lock:
            conn.execute(
                "INSERT INTO settings (key, value, category, updated_at) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, "
                "category=excluded.category, updated_at=excluded.updated_at",
                (key, value, category, now),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Backup & restore
    # ------------------------------------------------------------------

    def backup(self, backup_path: Optional[Path] = None) -> Path:
        """Create a backup of the database file.

        Returns the path to the backup file.
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self._db_path.parent / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"mindful_organizer_{timestamp}.db"

        conn = self._get_connection()
        with self._lock:
            backup_conn = sqlite3.connect(str(backup_path))
            conn.backup(backup_conn)
            backup_conn.close()

        logger.info("Database backed up to %s", backup_path)
        return backup_path

    def restore(self, backup_path: Path) -> None:
        """Restore the database from a backup file.

        Closes the current connection, replaces the database, and reconnects.
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        # Validate the backup
        try:
            test_conn = sqlite3.connect(str(backup_path))
            test_conn.execute("SELECT * FROM schema_version LIMIT 1")
            test_conn.close()
        except sqlite3.Error as exc:
            raise ValueError(f"Invalid backup file: {exc}") from exc

        self.close()
        shutil.copy2(str(backup_path), str(self._db_path))
        self.initialize()
        logger.info("Database restored from %s", backup_path)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_table_to_json(self, table: TableName) -> str:
        """Export a single table to a JSON string."""
        result = self.query(table)
        return json.dumps(result.rows, indent=2, default=str)

    def export_all_to_json(self) -> str:
        """Export all tables to a single JSON string."""
        data: Dict[str, Any] = {
            "exported_at": datetime.now().isoformat(),
            "schema_version": CURRENT_SCHEMA_VERSION,
        }
        for tbl in TableName:
            result = self.query(tbl)
            data[tbl.value] = result.rows
        return json.dumps(data, indent=2, default=str)

    def export_table_to_csv(self, table: TableName) -> str:
        """Export a single table to a CSV string."""
        result = self.query(table)
        if not result.rows:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=result.rows[0].keys())
        writer.writeheader()
        writer.writerows(result.rows)
        return output.getvalue()

    def export_all_to_file(self, output_path: Path, fmt: str = "json") -> Path:
        """Export all data to a file. Supports 'json' and 'csv' formats.

        For CSV, creates a directory with one CSV per table.
        Returns the output path.
        """
        if fmt == "json":
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(self.export_all_to_json(), encoding="utf-8")
        elif fmt == "csv":
            output_path.mkdir(parents=True, exist_ok=True)
            for tbl in TableName:
                csv_data = self.export_table_to_csv(tbl)
                if csv_data:
                    (output_path / f"{tbl.value}.csv").write_text(
                        csv_data, encoding="utf-8"
                    )
        else:
            raise ValueError(f"Unsupported export format: {fmt}")

        logger.info("Exported all data to %s (%s)", output_path, fmt)
        return output_path

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the thread-local connection if open."""
        conn: Optional[sqlite3.Connection] = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None

    @property
    def db_path(self) -> Path:
        return self._db_path

    def __enter__(self) -> "DatabaseManager":
        self.initialize()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"DatabaseManager(db_path={self._db_path!r})"
