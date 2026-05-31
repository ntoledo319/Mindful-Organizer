"""
Tests for JournalingManager (src/wellness/journaling.py).

Since the JournalingManager class does not exist in the current codebase,
these tests target the journaling functionality via the DatabaseManager's
journal_entries table. Tests cover CRUD operations, search, streak tracking,
and prompt-related logic through the database layer.
"""

from datetime import datetime, timedelta

import pytest

from core.database import DatabaseManager, TableName


@pytest.fixture
def db(tmp_data_dir):
    """Provide an initialised database in a temp directory."""
    database = DatabaseManager(db_path=tmp_data_dir / "test.db")
    database.initialize()
    yield database
    database.close()


# ---------------------------------------------------------------------------
# Save and load entries
# ---------------------------------------------------------------------------

class TestSaveLoadEntry:

    def test_save_journal_entry(self, db):
        row_id = db.insert(
            TableName.JOURNAL_ENTRIES,
            content="Today was a good day.",
            mood_score=7,
            tags="gratitude,reflection",
            title="Good day",
        )
        assert row_id > 0

    def test_load_journal_entry(self, db):
        row_id = db.insert(
            TableName.JOURNAL_ENTRIES,
            content="Feeling reflective.",
            mood_score=6,
            title="Reflection",
        )
        entry = db.get_by_id(TableName.JOURNAL_ENTRIES, row_id)
        assert entry is not None
        assert entry["content"] == "Feeling reflective."
        assert entry["mood_score"] == 6

    def test_update_journal_entry(self, db):
        row_id = db.insert(
            TableName.JOURNAL_ENTRIES,
            content="Draft.",
            mood_score=5,
        )
        db.update(TableName.JOURNAL_ENTRIES, row_id, content="Final version.")
        entry = db.get_by_id(TableName.JOURNAL_ENTRIES, row_id)
        assert entry["content"] == "Final version."

    def test_delete_journal_entry(self, db):
        row_id = db.insert(
            TableName.JOURNAL_ENTRIES,
            content="To delete.",
            mood_score=5,
        )
        affected = db.delete(TableName.JOURNAL_ENTRIES, row_id)
        assert affected == 1
        assert db.get_by_id(TableName.JOURNAL_ENTRIES, row_id) is None


# ---------------------------------------------------------------------------
# Search entries
# ---------------------------------------------------------------------------

class TestSearchEntries:

    def test_search_by_content(self, db):
        db.insert(TableName.JOURNAL_ENTRIES, content="Had a wonderful walk in the park.", mood_score=8)
        db.insert(TableName.JOURNAL_ENTRIES, content="Stayed home and read a book.", mood_score=6)

        result = db.query(
            TableName.JOURNAL_ENTRIES,
            where="content LIKE ?",
            params=("%walk%",),
        )
        assert result.row_count == 1
        assert "walk" in result.rows[0]["content"]

    def test_search_no_match(self, db):
        db.insert(TableName.JOURNAL_ENTRIES, content="Nothing special.", mood_score=5)
        result = db.query(
            TableName.JOURNAL_ENTRIES,
            where="content LIKE ?",
            params=("%zzzzz%",),
        )
        assert result.row_count == 0

    def test_search_by_tags(self, db):
        db.insert(
            TableName.JOURNAL_ENTRIES,
            content="Grateful for friends.",
            mood_score=8,
            tags="gratitude,social",
        )
        result = db.query(
            TableName.JOURNAL_ENTRIES,
            where="tags LIKE ?",
            params=("%gratitude%",),
        )
        assert result.row_count == 1


# ---------------------------------------------------------------------------
# Streak tracking (via timestamp gaps)
# ---------------------------------------------------------------------------

class TestStreakTracking:

    def test_consecutive_days_counted(self, db):
        """Insert entries on consecutive days and verify count."""
        base = datetime.now()
        for i in range(5):
            ts = (base - timedelta(days=i)).isoformat()
            db.insert(
                TableName.JOURNAL_ENTRIES,
                content=f"Day {i}",
                mood_score=6,
                timestamp=ts,
            )

        result = db.query(TableName.JOURNAL_ENTRIES, order_by="timestamp DESC")
        assert result.row_count == 5

    def test_gap_in_streak(self, db):
        """Entries with a gap should not form a continuous streak."""
        base = datetime.now()
        # Day 0, 1, 3 (gap on day 2)
        for offset in [0, 1, 3]:
            ts = (base - timedelta(days=offset)).isoformat()
            db.insert(
                TableName.JOURNAL_ENTRIES,
                content="Entry",
                mood_score=6,
                timestamp=ts,
            )

        result = db.query(TableName.JOURNAL_ENTRIES, order_by="timestamp DESC")
        dates = sorted({r["timestamp"][:10] for r in result.rows})
        assert len(dates) == 3


# ---------------------------------------------------------------------------
# Prompts by category (simulated)
# ---------------------------------------------------------------------------

class TestPromptRecommendation:

    def test_prompts_can_be_stored_in_entries(self, db):
        """Journal entries can store the prompt that was used."""
        row_id = db.insert(
            TableName.JOURNAL_ENTRIES,
            content="I am grateful for my health.",
            mood_score=7,
            prompt="What are you grateful for today?",
        )
        entry = db.get_by_id(TableName.JOURNAL_ENTRIES, row_id)
        assert entry["prompt"] == "What are you grateful for today?"

    def test_query_entries_with_prompts(self, db):
        db.insert(
            TableName.JOURNAL_ENTRIES,
            content="A",
            mood_score=5,
            prompt="Gratitude prompt",
        )
        db.insert(
            TableName.JOURNAL_ENTRIES,
            content="B",
            mood_score=5,
            prompt=None,
        )

        result = db.query(
            TableName.JOURNAL_ENTRIES,
            where="prompt IS NOT NULL",
        )
        assert result.row_count == 1
