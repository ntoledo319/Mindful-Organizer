"""
Tests for ERPTracker (Exposure and Response Prevention) functionality.

Since ERPTracker does not exist as a standalone module in the codebase,
these tests exercise ERP-related data tracking through the DatabaseManager.
Covers hierarchy items, exposure sessions, SUDS tracking, habituation
analysis, and response prevention logging.
"""

import pytest

from core.database import DatabaseManager


@pytest.fixture
def db(tmp_data_dir):
    database = DatabaseManager(db_path=tmp_data_dir / "test.db")
    database.initialize()
    # Create an ERP-specific table for testing if not present
    database.execute("""
        CREATE TABLE IF NOT EXISTS erp_hierarchy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger_description TEXT NOT NULL,
            suds_initial INTEGER NOT NULL CHECK (suds_initial BETWEEN 0 AND 100),
            suds_current INTEGER CHECK (suds_current BETWEEN 0 AND 100),
            category TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    database.execute("""
        CREATE TABLE IF NOT EXISTS erp_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hierarchy_id INTEGER NOT NULL,
            suds_start INTEGER NOT NULL CHECK (suds_start BETWEEN 0 AND 100),
            suds_peak INTEGER CHECK (suds_peak BETWEEN 0 AND 100),
            suds_end INTEGER CHECK (suds_end BETWEEN 0 AND 100),
            duration_minutes INTEGER,
            response_prevented INTEGER DEFAULT 1,
            response_description TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    yield database
    database.close()


# ---------------------------------------------------------------------------
# Hierarchy items
# ---------------------------------------------------------------------------


class TestAddHierarchyItem:
    def test_add_item(self, db):
        result = db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial, category) "
            "VALUES (?, ?, ?)",
            ("Touching doorknob", 65, "contamination"),
        )
        assert result.last_row_id > 0

    def test_retrieve_item(self, db):
        db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
            ("Leaving door unlocked", 80),
        )
        result = db.execute(
            "SELECT * FROM erp_hierarchy WHERE trigger_description = ?", ("Leaving door unlocked",)
        )
        assert result.row_count == 1
        assert result.rows[0]["suds_initial"] == 80

    def test_multiple_items_ordered(self, db):
        items = [
            ("Minor trigger", 20),
            ("Severe trigger", 90),
            ("Moderate trigger", 55),
        ]
        for desc, suds in items:
            db.execute(
                "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
                (desc, suds),
            )

        result = db.execute("SELECT * FROM erp_hierarchy ORDER BY suds_initial ASC")
        assert result.row_count == 3
        suds_values = [r["suds_initial"] for r in result.rows]
        assert suds_values == sorted(suds_values)


# ---------------------------------------------------------------------------
# Exposure sessions
# ---------------------------------------------------------------------------


class TestRecordExposureSession:
    def test_record_session(self, db):
        # First create a hierarchy item
        h_result = db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
            ("Checking stove", 70),
        )
        h_id = h_result.last_row_id

        # Record an exposure session
        s_result = db.execute(
            "INSERT INTO erp_sessions (hierarchy_id, suds_start, suds_peak, suds_end, "
            "duration_minutes, response_prevented) VALUES (?, ?, ?, ?, ?, ?)",
            (h_id, 70, 85, 45, 30, 1),
        )
        assert s_result.last_row_id > 0

    def test_session_links_to_hierarchy(self, db):
        h_result = db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
            ("Symmetry", 50),
        )
        h_id = h_result.last_row_id

        db.execute(
            "INSERT INTO erp_sessions (hierarchy_id, suds_start, suds_peak, suds_end, "
            "duration_minutes) VALUES (?, ?, ?, ?, ?)",
            (h_id, 50, 60, 30, 20),
        )

        result = db.execute("SELECT * FROM erp_sessions WHERE hierarchy_id = ?", (h_id,))
        assert result.row_count == 1


# ---------------------------------------------------------------------------
# SUDS tracking
# ---------------------------------------------------------------------------


class TestSUDSTracking:
    def test_suds_decreases_over_sessions(self, db):
        """Multiple sessions should show SUDS habituation."""
        h_result = db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
            ("Contamination fear", 80),
        )
        h_id = h_result.last_row_id

        # Simulate 5 sessions with decreasing SUDS
        for i in range(5):
            suds_start = 80 - i * 8
            suds_end = 60 - i * 10
            db.execute(
                "INSERT INTO erp_sessions (hierarchy_id, suds_start, suds_end, "
                "duration_minutes) VALUES (?, ?, ?, ?)",
                (h_id, max(suds_start, 0), max(suds_end, 0), 25),
            )

        result = db.execute(
            "SELECT suds_end FROM erp_sessions WHERE hierarchy_id = ? ORDER BY id ASC",
            (h_id,),
        )
        ends = [r["suds_end"] for r in result.rows]
        # SUDS should generally decrease
        assert ends[-1] < ends[0]

    def test_suds_range_validation(self, db):
        """SUDS must be between 0 and 100."""
        import sqlite3

        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
                ("Invalid", 150),
            )


# ---------------------------------------------------------------------------
# Habituation analysis
# ---------------------------------------------------------------------------


class TestHabituationAnalysis:
    def test_habituation_detected(self, db):
        """Compute average SUDS reduction across sessions."""
        h_result = db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
            ("Ordering fear", 70),
        )
        h_id = h_result.last_row_id

        sessions_data = [(70, 40), (65, 35), (55, 25), (45, 20)]
        for start, end in sessions_data:
            db.execute(
                "INSERT INTO erp_sessions (hierarchy_id, suds_start, suds_end, "
                "duration_minutes) VALUES (?, ?, ?, ?)",
                (h_id, start, end, 20),
            )

        result = db.execute(
            "SELECT AVG(suds_start - suds_end) AS avg_reduction "
            "FROM erp_sessions WHERE hierarchy_id = ?",
            (h_id,),
        )
        avg_reduction = result.rows[0]["avg_reduction"]
        assert avg_reduction > 0

    def test_update_current_suds(self, db):
        """Update the hierarchy item's current SUDS after sessions."""
        h_result = db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial, suds_current) "
            "VALUES (?, ?, ?)",
            ("Checking", 80, 80),
        )
        h_id = h_result.last_row_id

        # After several sessions, update current SUDS
        db.execute(
            "UPDATE erp_hierarchy SET suds_current = ? WHERE id = ?",
            (45, h_id),
        )

        result = db.execute("SELECT * FROM erp_hierarchy WHERE id = ?", (h_id,))
        assert result.rows[0]["suds_current"] == 45
        assert result.rows[0]["suds_initial"] == 80  # original unchanged


# ---------------------------------------------------------------------------
# Response prevention log
# ---------------------------------------------------------------------------


class TestResponsePreventionLog:
    def test_response_prevented_logged(self, db):
        h_result = db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
            ("Washing hands", 75),
        )
        h_id = h_result.last_row_id

        db.execute(
            "INSERT INTO erp_sessions (hierarchy_id, suds_start, suds_end, "
            "response_prevented, response_description, duration_minutes) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (h_id, 75, 40, 1, "Did not wash hands for 30 minutes", 30),
        )

        result = db.execute("SELECT * FROM erp_sessions WHERE hierarchy_id = ?", (h_id,))
        session = result.rows[0]
        assert session["response_prevented"] == 1
        assert "Did not wash" in session["response_description"]

    def test_response_not_prevented(self, db):
        h_result = db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
            ("Checking lock", 60),
        )
        h_id = h_result.last_row_id

        db.execute(
            "INSERT INTO erp_sessions (hierarchy_id, suds_start, suds_end, "
            "response_prevented, response_description, duration_minutes) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (h_id, 60, 55, 0, "Checked lock once after 10 minutes", 15),
        )

        result = db.execute(
            "SELECT * FROM erp_sessions WHERE hierarchy_id = ? AND response_prevented = 0",
            (h_id,),
        )
        assert result.row_count == 1

    def test_prevention_rate(self, db):
        """Calculate percentage of sessions with successful prevention."""
        h_result = db.execute(
            "INSERT INTO erp_hierarchy (trigger_description, suds_initial) VALUES (?, ?)",
            ("Rituals", 65),
        )
        h_id = h_result.last_row_id

        for prevented in [1, 1, 1, 0, 1]:
            db.execute(
                "INSERT INTO erp_sessions (hierarchy_id, suds_start, suds_end, "
                "response_prevented, duration_minutes) VALUES (?, ?, ?, ?, ?)",
                (h_id, 65, 40, prevented, 20),
            )

        result = db.execute(
            "SELECT AVG(response_prevented) * 100 AS rate FROM erp_sessions WHERE hierarchy_id = ?",
            (h_id,),
        )
        rate = result.rows[0]["rate"]
        assert rate == 80.0
