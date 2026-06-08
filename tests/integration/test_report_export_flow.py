"""
Integration tests for the Diary Card Save → Report Generation → PDF Export flow.

Validates that mood and diary data can be compiled into a shareable HTML report
and exported to PDF (or HTML fallback) with non-empty output files.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from core.database import DatabaseManager, TableName
from core.diary_card_manager import DiaryCard, DiaryCardManager
from core.pdf_export import WellnessPDFExporter
from core.shareable_report import ShareableReport
from core.wellness_orchestrator import WellnessOrchestrator


@pytest.fixture
def report_db(tmp_data_dir):
    """Fresh database with schema for report generation tests."""
    db = DatabaseManager(db_path=tmp_data_dir / "report.db")
    db.initialize()
    yield db
    db.close()


@pytest.fixture
def sample_mood_data(report_db):
    """Insert 7 days of mood entries into the database."""
    base = datetime.now() - timedelta(days=7)
    for i in range(7):
        ts = (base + timedelta(days=i)).isoformat()
        report_db.insert(
            TableName.MOOD_ENTRIES,
            mood_score=4 + (i % 4),
            energy_level=5 + (i % 3),
            timestamp=ts,
            notes=f"Day {i + 1}",
        )
    return report_db


@pytest.fixture
def sample_diary_cards(report_db):
    """Insert 5 diary cards into the database."""
    manager = DiaryCardManager(db=report_db)
    for i in range(5):
        card = DiaryCard(
            date=date.today() - timedelta(days=i),
            mood_score=5 + (i % 3),
            emotions=["anxiety", "hope"],
            skills_used=["Mindfulness", "TIPP"],
            skills_effectiveness=4,
            target_behaviors={"Skipped meals": 0, "Missed medication": i % 2},
            medications_taken=i % 2 == 0,
            notes=f"Diary day {i + 1}",
        )
        manager.save(card)
    return manager


@pytest.mark.integration
class TestReportExportFlow:
    def test_shareable_html_report_created(self, sample_mood_data, tmp_data_dir):
        """A ShareableReport with mood data should write a non-empty HTML file."""
        # Fetch entries as dicts for the report builder
        rows = sample_mood_data.query(
            TableName.MOOD_ENTRIES,
            order_by="timestamp ASC",
        ).rows
        entries = [
            {
                "timestamp": r["timestamp"],
                "mood_score": r["mood_score"],
                "energy_score": r["energy_level"] * 10 if r["energy_level"] else 50,
            }
            for r in rows
        ]

        report = ShareableReport(title="My Wellness Report", theme={"accent": "#4a90d9"})
        report.add_header(subtitle="Weekly Summary")
        report.add_mood_timeline(entries)

        out_path = tmp_data_dir / "wellness_report.html"
        result = report.export(out_path)

        assert result.exists()
        assert result.stat().st_size > 0
        content = result.read_text()
        assert "My Wellness Report" in content
        assert "Mood Timeline" in content
        assert "chart.js" in content.lower() or "Chart" in content

    def test_pdf_export_from_summary(self, sample_mood_data, tmp_data_dir):
        """WellnessPDFExporter should produce a non-empty file from wellness data."""
        orchestrator = WellnessOrchestrator(db=sample_mood_data)
        summary = orchestrator.wellness_summary(days=7)

        exporter = WellnessPDFExporter()
        out_path = tmp_data_dir / "wellness_report.pdf"
        result = exporter.export(summary, output_path=out_path, user_name="Test User")

        assert result.exists()
        assert result.stat().st_size > 0
        # If reportlab/weasyprint are unavailable it falls back to HTML;
        # in that case we still verify the file is non-empty and contains report text.
        content = result.read_text() if result.suffix == ".html" else ""
        if content:
            assert "Wellness Report" in content or "Mood Trends" in content

    def test_diary_card_to_html_report(self, sample_diary_cards, tmp_data_dir):
        """Diary card data should be renderable in a shareable HTML report."""
        cards = sample_diary_cards.list_range(
            start=date.today() - timedelta(days=7),
            end=date.today(),
        )
        card_dicts = [
            {
                "date": c.date.isoformat(),
                "mood_score": c.mood_score,
                "skills_used": c.skills_used,
                "skills_effectiveness": c.skills_effectiveness,
                "target_behaviors": c.target_behaviors,
            }
            for c in cards
        ]

        report = ShareableReport(title="Diary Card Report")
        report.add_header(subtitle="Last 7 Days")
        report.add_diary_card_summary(card_dicts, days=7)

        out_path = tmp_data_dir / "diary_report.html"
        result = report.export(out_path)

        assert result.exists()
        assert result.stat().st_size > 0
        content = result.read_text()
        assert "Diary Card Summary" in content
        assert "Top Skills Used" in content

    def test_pdf_export_html_fallback(self, sample_mood_data, tmp_data_dir, monkeypatch):
        """When PDF libraries are unavailable, export should fall back to HTML gracefully."""
        orchestrator = WellnessOrchestrator(db=sample_mood_data)
        summary = orchestrator.wellness_summary(days=7)

        exporter = WellnessPDFExporter()
        # Force HTML fallback by pretending reportlab is missing
        monkeypatch.setattr("core.pdf_export._HAS_REPORTLAB", False)
        monkeypatch.setattr("core.pdf_export._HAS_WEASYPRINT", False)

        out_path = tmp_data_dir / "fallback_report.pdf"
        result = exporter.export(summary, output_path=out_path, user_name="User")

        # Fallback changes suffix to .html
        assert result.exists()
        assert result.stat().st_size > 0
        assert result.suffix == ".html"
        assert "Wellness Report" in result.read_text()

    def test_report_with_crisis_signals(self, report_db, tmp_data_dir):
        """A report generated during a crisis period should include signal sections."""
        # Insert very low mood to trigger crisis signals
        for i in range(3):
            report_db.insert(
                TableName.MOOD_ENTRIES,
                mood_score=1,
                energy_level=1,
                timestamp=(datetime.now() - timedelta(days=i)).isoformat(),
            )

        orchestrator = WellnessOrchestrator(db=report_db)
        summary = orchestrator.wellness_summary(days=7)

        assert len(summary["crisis_signals"]) > 0

        exporter = WellnessPDFExporter()
        out_path = tmp_data_dir / "crisis_report.pdf"
        result = exporter.export(summary, output_path=out_path)

        assert result.exists()
        assert result.stat().st_size > 0
