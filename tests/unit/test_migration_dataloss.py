"""Regression tests for the v2->v4 task-migration data-integrity bug.

A legacy (pre-guid) task migrated from schema v2 used to keep guid=NULL on disk
while TaskManager assigned it a fresh in-memory UUID. The first edit/complete then
INSERTed a duplicate row instead of updating, silently doubling tasks on upgrade.
The v4 migration backfills guids; these tests build a *genuine* v2 tasks table
(not a cosmetically downgraded latest-schema DB) and prove no duplication occurs.
"""

import sqlite3

from core.database import DatabaseManager
from core.task_manager import TaskManager

_V2_TASKS_DDL = """
CREATE TABLE schema_version (version INTEGER PRIMARY KEY, applied_at TEXT);
INSERT INTO schema_version(version) VALUES (2);
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT,
    priority TEXT DEFAULT 'medium', category TEXT DEFAULT 'Other',
    energy_required INTEGER DEFAULT 5, due_date TEXT, completed INTEGER DEFAULT 0,
    completed_at TEXT, notes TEXT,
    created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now'))
);
"""


def _make_v2_db(path, titles):
    con = sqlite3.connect(path)
    con.executescript(_V2_TASKS_DDL)
    con.executemany("INSERT INTO tasks(title) VALUES (?)", [(t,) for t in titles])
    con.commit()
    con.close()


def test_v4_migration_backfills_guids(tmp_path):
    dbp = tmp_path / "mindful_organizer.db"
    _make_v2_db(dbp, ["Legacy A", "Legacy B", "Legacy C"])

    DatabaseManager(db_path=dbp).initialize()

    rows = sqlite3.connect(dbp).execute("SELECT guid FROM tasks").fetchall()
    assert len(rows) == 3
    guids = [r[0] for r in rows]
    assert all(g for g in guids), "every migrated task must have a non-null guid"
    assert len(set(guids)) == 3, "backfilled guids must be unique"


def test_completing_migrated_task_does_not_duplicate(tmp_path):
    dbp = tmp_path / "mindful_organizer.db"
    _make_v2_db(dbp, ["Legacy A", "Legacy B", "Legacy C"])
    db = DatabaseManager(db_path=dbp)
    db.initialize()

    tm = TaskManager(data_dir=tmp_path, db_manager=db)
    assert len(tm.tasks) == 3

    for task in list(tm.tasks):
        tm.complete_task(task.id)

    con = sqlite3.connect(dbp)
    count = con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed = con.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1").fetchone()[0]
    assert count == 3, f"completing migrated tasks must not duplicate rows (got {count})"
    assert completed == 3, "all three migrated tasks should be marked complete in place"


def test_editing_migrated_task_twice_is_stable(tmp_path):
    """Editing the same migrated task repeatedly must never grow the table."""
    dbp = tmp_path / "mindful_organizer.db"
    _make_v2_db(dbp, ["Legacy A"])
    db = DatabaseManager(db_path=dbp)
    db.initialize()

    tm = TaskManager(data_dir=tmp_path, db_manager=db)
    task_id = tm.tasks[0].id
    tm.update_task(task_id, notes="first edit")
    tm.update_task(task_id, notes="second edit")

    count = sqlite3.connect(dbp).execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    assert count == 1
