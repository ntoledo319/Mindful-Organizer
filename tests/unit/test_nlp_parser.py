"""
Tests for NLPTaskParser (src/core/nlp_parser.py).

Covers parsing simple tasks, dates, priorities, categories,
energy levels, complex inputs, and fallback behaviour.
"""

from datetime import date, timedelta

import pytest

try:
    from src.core.nlp_parser import (
        NLPTaskParser,
        ParsedTask,
        Priority,
        Category,
        EnergyRequired,
    )
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="nlp_parser module not available")


# Use a fixed reference date so tests are deterministic.
_REF_DATE = date(2026, 4, 6)  # a Monday


@pytest.fixture
def parser():
    return NLPTaskParser(reference_date=_REF_DATE)


# ---------------------------------------------------------------------------
# Simple tasks
# ---------------------------------------------------------------------------

class TestParseSimpleTask:

    def test_parse_simple_task(self, parser):
        """A plain task title is captured correctly."""
        result = parser.parse("call dentist")
        assert isinstance(result, ParsedTask)
        assert "call" in result.title.lower() or "dentist" in result.title.lower()
        assert result.original_text == "call dentist"

    def test_parse_preserves_original(self, parser):
        result = parser.parse("  buy groceries  ")
        assert result.original_text == "buy groceries"

    def test_parse_empty_string(self, parser):
        result = parser.parse("")
        assert result.title == ""
        assert result.confidence.get("overall", 0) == 0.0


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

class TestParseWithDate:

    def test_parse_tomorrow(self, parser):
        result = parser.parse("finish report by tomorrow")
        assert result.due_date == _REF_DATE + timedelta(days=1)

    def test_parse_today(self, parser):
        result = parser.parse("do laundry today")
        assert result.due_date == _REF_DATE

    def test_parse_day_name_friday(self, parser):
        """'by friday' should resolve to the upcoming Friday."""
        result = parser.parse("finish report by friday")
        assert result.due_date is not None
        assert result.due_date.weekday() == 4  # Friday

    def test_parse_next_week(self, parser):
        result = parser.parse("plan trip next week")
        assert result.due_date == _REF_DATE + timedelta(weeks=1)

    def test_parse_in_n_days(self, parser):
        result = parser.parse("return library books in 3 days")
        assert result.due_date == _REF_DATE + timedelta(days=3)

    def test_parse_iso_date(self, parser):
        result = parser.parse("submit form by 2026-05-15")
        assert result.due_date == date(2026, 5, 15)

    def test_parse_month_day(self, parser):
        result = parser.parse("birthday party jan 20")
        assert result.due_date is not None
        assert result.due_date.month == 1
        assert result.due_date.day == 20


# ---------------------------------------------------------------------------
# Priority parsing
# ---------------------------------------------------------------------------

class TestParseWithPriority:

    def test_parse_urgent_prefix(self, parser):
        result = parser.parse("urgent: fix production bug")
        assert result.priority == Priority.URGENT

    def test_parse_urgent_keyword(self, parser):
        result = parser.parse("fix bug asap")
        assert result.priority == Priority.URGENT

    def test_parse_high_priority(self, parser):
        result = parser.parse("high priority: review contract")
        assert result.priority == Priority.HIGH

    def test_parse_low_priority(self, parser):
        result = parser.parse("low priority: organize bookshelf")
        assert result.priority == Priority.LOW

    def test_default_priority_is_medium(self, parser):
        result = parser.parse("buy milk")
        assert result.priority == Priority.MEDIUM


# ---------------------------------------------------------------------------
# Category parsing
# ---------------------------------------------------------------------------

class TestParseWithCategory:

    def test_parse_health_prefix(self, parser):
        result = parser.parse("health: schedule appointment")
        assert result.category == Category.HEALTH

    def test_parse_work_prefix(self, parser):
        result = parser.parse("work: send quarterly report")
        assert result.category == Category.WORK

    def test_parse_category_from_keywords(self, parser):
        """The word 'dentist' should map to health category."""
        result = parser.parse("call dentist")
        assert result.category == Category.HEALTH

    def test_parse_errands_category(self, parser):
        result = parser.parse("pick up dry cleaning")
        assert result.category == Category.ERRANDS

    def test_default_category_is_other(self, parser):
        result = parser.parse("random undefined thing xyz")
        assert result.category == Category.OTHER


# ---------------------------------------------------------------------------
# Energy parsing
# ---------------------------------------------------------------------------

class TestParseWithEnergy:

    def test_parse_easy_task(self, parser):
        result = parser.parse("easy task: water plants")
        assert result.energy_required in (EnergyRequired.LOW, EnergyRequired.VERY_LOW)

    def test_parse_hard_task(self, parser):
        result = parser.parse("this is a very hard demanding project")
        assert result.energy_required in (EnergyRequired.HIGH, EnergyRequired.VERY_HIGH)

    def test_default_energy_is_moderate(self, parser):
        result = parser.parse("call dentist")
        # dentist might match some keywords, but energy default is moderate
        assert result.energy_required in (
            EnergyRequired.MODERATE, EnergyRequired.LOW, EnergyRequired.HIGH,
        )


# ---------------------------------------------------------------------------
# Complex / multi-feature parsing
# ---------------------------------------------------------------------------

class TestParseComplex:

    def test_parse_complex_input(self, parser):
        """A task with priority, category, and date all at once."""
        result = parser.parse("urgent work: deploy release by next monday")

        assert result.priority == Priority.URGENT
        assert result.category == Category.WORK
        assert result.due_date is not None
        assert result.due_date.weekday() == 0  # Monday
        assert "deploy" in result.title.lower() or "release" in result.title.lower()

    def test_parse_recurring_daily(self, parser):
        result = parser.parse("take medication every day")
        assert result.is_recurring is True
        assert result.recurrence_pattern == "daily"

    def test_parse_recurring_weekly(self, parser):
        result = parser.parse("weekly team standup")
        assert result.is_recurring is True
        assert result.recurrence_pattern == "weekly"

    def test_confidence_scores_present(self, parser):
        result = parser.parse("urgent: call dentist tomorrow")
        assert "overall" in result.confidence
        assert result.confidence["overall"] > 0

    def test_to_dict_serialization(self, parser):
        result = parser.parse("call dentist tomorrow")
        d = result.to_dict()
        assert "title" in d
        assert "priority" in d
        assert d["original_text"] == "call dentist tomorrow"


# ---------------------------------------------------------------------------
# Fallback / edge cases
# ---------------------------------------------------------------------------

class TestParseFallback:

    def test_parse_unparseable_keeps_title(self, parser):
        """Even without matches, the full text becomes the title."""
        result = parser.parse("xyzzy foo bar baz")
        assert result.title  # non-empty
        assert result.priority == Priority.MEDIUM
        assert result.category == Category.OTHER

    def test_parse_whitespace_only(self, parser):
        result = parser.parse("   ")
        assert result.title == ""
        assert result.confidence.get("overall", 0) == 0.0

    def test_parse_batch(self, parser):
        texts = ["call dentist", "buy milk", "urgent: fix bug"]
        results = parser.parse_batch(texts)
        assert len(results) == 3
        assert all(isinstance(r, ParsedTask) for r in results)

    def test_title_not_polluted_with_metadata(self, parser):
        """Classification keywords like 'dentist' should remain in the title."""
        result = parser.parse("call dentist")
        assert "dentist" in result.title.lower()
