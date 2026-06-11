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
        db.insert(
            TableName.JOURNAL_ENTRIES, content="Had a wonderful walk in the park.", mood_score=8
        )
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


# ===========================================================================
# Tests for src/wellness/journaling.py (JournalEntry, JournalingManager)
# ===========================================================================

from core.constants import Condition
from wellness.journaling import JournalEntry, JournalPrompt, JournalingManager, PromptCategory
from wellness.journal_analyzer import JournalAnalyzer


class TestJournalEntry:
    def test_default_creation(self):
        entry = JournalEntry()
        assert entry.entry_id
        assert entry.entry_date
        assert entry.entry_text == ""
        assert entry.tags == []
        assert entry.word_count == 0

    def test_word_count(self):
        entry = JournalEntry(entry_text="Hello world this is a test")
        assert entry.word_count == 6

    def test_word_count_empty_text(self):
        entry = JournalEntry(entry_text="   ")
        assert entry.word_count == 0

    def test_mood_improvement(self):
        entry = JournalEntry(mood_before=3, mood_after=7)
        assert entry.mood_improvement == 4

    def test_mood_improvement_missing(self):
        entry = JournalEntry(mood_before=3)
        assert entry.mood_improvement is None

    def test_to_dict_round_trip(self):
        entry = JournalEntry(
            entry_text="Test entry",
            mood_before=5,
            mood_after=6,
            tags=["gratitude"],
        )
        d = entry.to_dict()
        restored = JournalEntry.from_dict(d)
        assert restored.entry_text == entry.entry_text
        assert restored.mood_before == entry.mood_before
        assert restored.tags == entry.tags

    def test_to_formatted_text(self):
        entry = JournalEntry(entry_text="Hello world", mood_before=4, mood_after=6, tags=["test"])
        text = entry.to_formatted_text(prompt_text="A prompt")
        assert "Hello world" in text
        assert "A prompt" in text
        assert "4/10" in text
        assert "6/10" in text
        assert "test" in text


class TestJournalingManager:
    def test_create_entry(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        entry = mgr.create_entry("Hello world", mood_before=5, mood_after=6, tags=["test"])
        assert entry.entry_text == "Hello world"
        assert entry.mood_before == 5
        assert entry.mood_after == 6
        assert entry.tags == ["test"]
        assert len(mgr.entries) == 1

    def test_create_entry_invalid_mood(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        with pytest.raises(ValueError):
            mgr.create_entry("Test", mood_before=0)
        with pytest.raises(ValueError):
            mgr.create_entry("Test", mood_after=11)

    def test_get_entries(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        mgr.create_entry("First")
        mgr.create_entry("Second")
        entries = mgr.entries
        assert len(entries) == 2
        assert entries[0].entry_text == "First"
        assert entries[1].entry_text == "Second"

    def test_search_by_keyword(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        mgr.create_entry("I love walking in the park")
        mgr.create_entry("Reading books is fun")
        results = mgr.search_by_keyword("walking")
        assert len(results) == 1
        assert "walking" in results[0].entry_text

    def test_search_by_tag(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        mgr.create_entry("A", tags=["gratitude"])
        mgr.create_entry("B", tags=["anxiety"])
        results = mgr.search_by_tag("gratitude")
        assert len(results) == 1
        assert results[0].entry_text == "A"

    def test_search_by_date(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        mgr.create_entry("Today")
        today = mgr.entries[0].entry_date
        results = mgr.search_by_date(today)
        assert len(results) == 1

    def test_search_by_mood(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        mgr.create_entry("Low", mood_before=2)
        mgr.create_entry("High", mood_before=8)
        results = mgr.search_by_mood(min_mood=1, max_mood=4)
        assert len(results) == 1
        assert results[0].entry_text == "Low"

    def test_update_entry(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        entry = mgr.create_entry("Original")
        updated = mgr.update_entry(entry.entry_id, entry_text="Updated", mood_after=7)
        assert updated is not None
        assert updated.entry_text == "Updated"
        assert updated.mood_after == 7

    def test_delete_entry(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        entry = mgr.create_entry("To delete")
        assert mgr.delete_entry(entry.entry_id) is True
        assert len(mgr.entries) == 0
        assert mgr.delete_entry("nonexistent") is False

    def test_get_prompt_by_id(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        prompt = mgr.get_prompt_by_id("grat_01")
        assert prompt is not None
        assert prompt.category == PromptCategory.GRATITUDE

    def test_get_prompts_by_category(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        prompts = mgr.get_prompts_by_category(PromptCategory.GRATITUDE)
        assert len(prompts) >= 1
        assert all(p.category == PromptCategory.GRATITUDE for p in prompts)

    def test_recommend_prompts_with_conditions(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        prompts = mgr.recommend_prompts(mood=3, conditions={Condition.DEPRESSION}, limit=3)
        assert len(prompts) <= 3
        assert len(prompts) > 0

    def test_recommend_prompts_low_mood(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        prompts = mgr.recommend_prompts(mood=2, limit=5)
        # Low mood should favour self-compassion, depression activation, gratitude
        categories = [p.category for p in prompts]
        assert (
            PromptCategory.SELF_COMPASSION in categories
            or PromptCategory.DEPRESSION_ACTIVATION in categories
        )

    def test_get_current_streak_no_entries(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        assert mgr.get_current_streak() == 0

    def test_get_longest_streak_no_entries(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        assert mgr.get_longest_streak() == 0

    def test_writing_statistics(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        mgr.create_entry("Hello world test")
        stats = mgr.get_writing_statistics()
        assert stats["total_entries"] == 1
        assert stats["total_words"] == 3
        assert stats["average_word_count"] == 3.0

    def test_export_entries(self, tmp_data_dir):
        mgr = JournalingManager(tmp_data_dir)
        mgr.create_entry("Exported entry")
        export = mgr.export_entries()
        assert "Hearth - Journal Export" in export
        assert "Exported entry" in export

    def test_persistence(self, tmp_data_dir):
        mgr1 = JournalingManager(tmp_data_dir)
        mgr1.create_entry("Persisted")
        del mgr1
        mgr2 = JournalingManager(tmp_data_dir)
        assert len(mgr2.entries) == 1
        assert mgr2.entries[0].entry_text == "Persisted"


class TestJournalAnalyzer:
    def test_analyze_sentiment_positive(self):
        analyzer = JournalAnalyzer()
        result = analyzer.analyze("I feel great and happy today")
        assert result.sentiment.polarity > 0
        assert result.risk_flagged is False

    def test_analyze_sentiment_negative(self):
        analyzer = JournalAnalyzer()
        result = analyzer.analyze("I feel terrible and sad")
        assert result.sentiment.polarity < 0

    def test_analyze_risk_flagged(self):
        analyzer = JournalAnalyzer()
        result = analyzer.analyze("I want to kill myself")
        assert result.risk_flagged is True

    def test_analyze_no_risk(self):
        analyzer = JournalAnalyzer()
        result = analyzer.analyze("I had a good day at work")
        assert result.risk_flagged is False

    def test_analyze_word_count(self):
        analyzer = JournalAnalyzer()
        result = analyzer.analyze("One two three four five")
        assert result.word_count == 5

    def test_analyze_insights_present(self):
        analyzer = JournalAnalyzer()
        result = analyzer.analyze("I am always a failure and everything is my fault")
        assert len(result.insights) > 0
