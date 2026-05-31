"""
Tests for ShareableReport HTML generation.

Validates document structure, theme application, JSON payload embedding,
and section ordering.
"""

from datetime import date
from pathlib import Path

from core.shareable_report import ShareableReport


class TestReportStructure:
    def test_export_creates_html_file(self, tmp_path: Path) -> None:
        report = ShareableReport("Test Report")
        report.add_header(subtitle="Weekly Summary")
        out = report.export(tmp_path / "report.html")
        assert out.exists()
        assert out.stat().st_size > 0

    def test_html_contains_doctype_and_chartjs(self, tmp_path: Path) -> None:
        report = ShareableReport("Test Report")
        report.add_header()
        out = report.export(tmp_path / "report.html")
        html = out.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in html
        assert "chart.js" in html.lower()
        assert "<title>Test Report</title>" in html

    def test_disclaimer_present(self, tmp_path: Path) -> None:
        report = ShareableReport("Test Report")
        report.add_header()
        out = report.export(tmp_path / "report.html")
        html = out.read_text(encoding="utf-8")
        assert "not medical advice" in html

    def test_theme_colors_applied(self, tmp_path: Path) -> None:
        report = ShareableReport(
            "Themed Report",
            theme={"accent": "#ff0000", "background": "#000000", "card_bg": "#111111"},
        )
        report.add_header()
        out = report.export(tmp_path / "report.html")
        html = out.read_text(encoding="utf-8")
        assert "--accent: #ff0000" in html
        assert "--bg: #000000" in html
        assert "--card-bg: #111111" in html

    def test_date_range_in_header(self, tmp_path: Path) -> None:
        report = ShareableReport("Dated Report")
        report.add_header(date_range=(date(2026, 1, 1), date(2026, 1, 7)))
        out = report.export(tmp_path / "report.html")
        html = out.read_text(encoding="utf-8")
        assert "2026-01-01" in html
        assert "2026-01-07" in html


class TestMoodTimelineSection:
    def test_mood_timeline_embeds_json(self, tmp_path: Path) -> None:
        report = ShareableReport("Mood Report")
        entries = [
            {"timestamp": "2026-01-01T08:00:00", "mood_score": 5},
            {"timestamp": "2026-01-02T08:00:00", "mood_score": 7},
        ]
        report.add_mood_timeline(entries)
        out = report.export(tmp_path / "report.html")
        html = out.read_text(encoding="utf-8")
        # Labels should be ISO date prefixes
        assert "2026-01-01" in html
        assert "2026-01-02" in html
        # Scores should be present as JSON numbers
        assert "5" in html
        assert "7" in html

    def test_empty_mood_timeline_skipped(self, tmp_path: Path) -> None:
        report = ShareableReport("Empty Mood Report")
        report.add_mood_timeline([])
        out = report.export(tmp_path / "report.html")
        html = out.read_text(encoding="utf-8")
        assert "Mood Timeline" not in html


class TestSectionOrdering:
    def test_header_comes_before_sections(self, tmp_path: Path) -> None:
        report = ShareableReport("Ordered Report")
        report.add_mood_timeline([{"timestamp": "2026-01-01T08:00:00", "mood_score": 5}])
        report.add_header(subtitle="Should be first")
        out = report.export(tmp_path / "report.html")
        html = out.read_text(encoding="utf-8")
        header_pos = html.find("Should be first")
        timeline_pos = html.find("Mood Timeline")
        assert header_pos < timeline_pos
