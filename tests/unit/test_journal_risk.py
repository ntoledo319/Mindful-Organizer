"""Risk-language detection in journal analysis must surface crisis resources."""

from wellness.journal_analyzer import JournalAnalyzer


def test_explicit_ideation_is_flagged_and_surfaces_988():
    analysis = JournalAnalyzer().analyze(
        "I feel like such a failure. Honestly some days I just want to die."
    )
    assert analysis.risk_flagged is True
    assert analysis.insights, "a risk-flagged entry must produce insights"
    # The crisis resource insight must come first and name 988.
    assert "988" in analysis.insights[0]


def test_self_harm_phrase_is_flagged():
    analysis = JournalAnalyzer().analyze("I keep thinking about hurting myself.")
    assert analysis.risk_flagged is True
    assert any("988" in i for i in analysis.insights)


def test_ordinary_negative_entry_is_not_risk_flagged():
    analysis = JournalAnalyzer().analyze(
        "Work was exhausting and I felt overwhelmed and frustrated all day."
    )
    assert analysis.risk_flagged is False
    assert all("988" not in i for i in analysis.insights)


def test_positive_entry_is_not_risk_flagged():
    analysis = JournalAnalyzer().analyze("Today was wonderful, I felt grateful and calm.")
    assert analysis.risk_flagged is False
