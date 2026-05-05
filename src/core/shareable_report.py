"""Self-contained HTML report generator.

Replaces PDF export with a single-file HTML timeline that can be
opened in any browser, shared via cloud storage, or pasted into Notion.
"""

from __future__ import annotations

import json
import logging
import random
import string
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _random_id(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@dataclass
class ReportSection:
    title: str
    html: str
    order: int = 0


class ShareableReport:
    """Generate a self-contained, themed HTML wellness report.

    Usage::

        report = ShareableReport("My Wellness", theme={"accent": "#4a90d9"})
        report.add_mood_timeline(entries)
        report.add_diary_card_summary(cards)
        report.add_sleep_summary(sleep_logs)
        path = report.export("/tmp/my_report.html")
    """

    def __init__(self, title: str, theme: dict[str, str] | None = None) -> None:
        self._title = title
        self._theme = theme or {}
        self._sections: list[ReportSection] = []
        self._accent = self._theme.get("accent", "#4a90d9")
        self._bg = self._theme.get("background", "#f8f9fa")
        self._card_bg = self._theme.get("card_bg", "#ffffff")
        self._text = self._theme.get("text", "#212529")
        self._secondary = self._theme.get("secondary", "#6c757d")

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def add_header(self, subtitle: str = "", date_range: tuple[date, date] | None = None) -> None:
        range_str = ""
        if date_range:
            range_str = f"{date_range[0].isoformat()} → {date_range[1].isoformat()}"
        html = f"""
        <div class="report-header">
            <h1>{self._title}</h1>
            {"<p class='subtitle'>" + subtitle + "</p>" if subtitle else ""}
            {"<p class='date-range'>" + range_str + "</p>" if range_str else ""}
            <p class="disclaimer">This report is for personal reflection only. It is not medical advice, diagnosis, or treatment.</p>
        </div>
        """
        self._sections.append(ReportSection("header", html, order=-100))

    def add_mood_timeline(self, entries: list[dict[str, Any]]) -> None:
        if not entries:
            return
        entries = sorted(entries, key=lambda e: e.get("timestamp", ""))
        labels = [e.get("timestamp", "")[:10] for e in entries]
        scores = [e.get("mood_score", 0) for e in entries]
        chart_id = _random_id()
        html = f"""
        <div class="section">
            <h2>Mood Timeline</h2>
            <div class="chart-container">
                <canvas id="{chart_id}"></canvas>
            </div>
            <script>
            (function() {{
                const ctx = document.getElementById('{chart_id}').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(labels)},
                        datasets: [{{
                            label: 'Mood Score',
                            data: {json.dumps(scores)},
                            borderColor: '{self._accent}',
                            backgroundColor: '{self._accent}20',
                            fill: true,
                            tension: 0.3,
                            pointRadius: 4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{ min: 1, max: 10, grid: {{ color: '#e9ecef' }} }},
                            x: {{ grid: {{ display: false }} }}
                        }},
                        plugins: {{ legend: {{ display: false }} }}
                    }}
                }});
            }})();
            </script>
        </div>
        """
        self._sections.append(ReportSection("mood_timeline", html, order=10))

    def add_diary_card_summary(self, cards: list[dict[str, Any]], days: int = 14) -> None:
        if not cards:
            return
        cards = sorted(cards, key=lambda c: c.get("date", ""))
        labels = [c.get("date", "") for c in cards]
        moods = [c.get("mood_score", 0) for c in cards]
        effs = [c.get("skills_effectiveness", 0) for c in cards]
        chart_id = _random_id()

        # Skill usage counts
        skill_counts: dict[str, int] = {}
        for c in cards:
            for s in c.get("skills_used", []):
                skill_counts[s] = skill_counts.get(s, 0) + 1
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Target behavior counts
        target_counts: dict[str, int] = {}
        for c in cards:
            for t, v in c.get("target_behaviors", {}).items():
                if v > 0:
                    target_counts[t] = target_counts.get(t, 0) + v
        top_targets = sorted(target_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        html = f"""
        <div class="section">
            <h2>Diary Card Summary (last {days} days)</h2>
            <div class="chart-container">
                <canvas id="{chart_id}"></canvas>
            </div>
            <script>
            (function() {{
                const ctx = document.getElementById('{chart_id}').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(labels)},
                        datasets: [
                            {{
                                label: 'Mood',
                                data: {json.dumps(moods)},
                                backgroundColor: '{self._accent}',
                                yAxisID: 'y'
                            }},
                            {{
                                label: 'Skill Effectiveness',
                                data: {json.dumps(effs)},
                                backgroundColor: '#20c997',
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{ min: 1, max: 10, position: 'left', grid: {{ color: '#e9ecef' }} }},
                            y1: {{ min: 1, max: 5, position: 'right', grid: {{ display: false }} }},
                            x: {{ grid: {{ display: false }} }}
                        }}
                    }}
                }});
            }})();
            </script>
            <div class="two-col">
                <div class="col">
                    <h3>Top Skills Used</h3>
                    <ul>{"".join(f"<li>{s} ({n}×)</li>" for s, n in top_skills)}</ul>
                </div>
                <div class="col">
                    <h3>Target Behaviors</h3>
                    <ul>{"".join(f"<li>{t} ({n} days)</li>" for t, n in top_targets)}</ul>
                </div>
            </div>
        </div>
        """
        self._sections.append(ReportSection("diary_card", html, order=20))

    def add_sleep_summary(self, logs: list[dict[str, Any]]) -> None:
        if not logs:
            return
        logs = sorted(logs, key=lambda x: x.get("date", ""))
        labels = [l.get("date", "") for l in logs]
        qualities = [l.get("quality", 0) for l in logs]
        durations = [l.get("duration_hours", 0) for l in logs]
        chart_id = _random_id()
        avg_q = sum(qualities) / len(qualities) if qualities else 0
        avg_d = sum(durations) / len(durations) if durations else 0
        html = f"""
        <div class="section">
            <h2>Sleep Summary</h2>
            <div class="metrics">
                <div class="metric">
                    <span class="metric-value">{avg_q:.1f}</span>
                    <span class="metric-label">Avg Quality</span>
                </div>
                <div class="metric">
                    <span class="metric-value">{avg_d:.1f}h</span>
                    <span class="metric-label">Avg Duration</span>
                </div>
                <div class="metric">
                    <span class="metric-value">{len(logs)}</span>
                    <span class="metric-label">Nights Logged</span>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="{chart_id}"></canvas>
            </div>
            <script>
            (function() {{
                const ctx = document.getElementById('{chart_id}').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(labels)},
                        datasets: [
                            {{
                                label: 'Quality',
                                data: {json.dumps(qualities)},
                                borderColor: '#6f42c1',
                                backgroundColor: '#6f42c120',
                                fill: true,
                                tension: 0.3,
                                yAxisID: 'y'
                            }},
                            {{
                                label: 'Duration (h)',
                                data: {json.dumps(durations)},
                                borderColor: '#fd7e14',
                                backgroundColor: 'transparent',
                                tension: 0.3,
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{ min: 1, max: 10, position: 'left', grid: {{ color: '#e9ecef' }} }},
                            y1: {{ position: 'right', grid: {{ display: false }} }},
                            x: {{ grid: {{ display: false }} }}
                        }}
                    }}
                }});
            }})();
            </script>
        </div>
        """
        self._sections.append(ReportSection("sleep", html, order=30))

    def add_journal_highlights(self, entries: list[dict[str, Any]]) -> None:
        if not entries:
            return
        entries = sorted(entries, key=lambda e: e.get("timestamp", ""), reverse=True)
        items = ""
        for e in entries[:7]:
            ts = e.get("timestamp", "")[:16].replace("T", " ")
            title = e.get("title", "Untitled")
            content = e.get("content", "")[:200].replace("\n", " ")
            if len(e.get("content", "")) > 200:
                content += "…"
            items += f"""
            <div class="journal-item">
                <div class="journal-meta">{ts} — <strong>{title}</strong></div>
                <div class="journal-body">{content}</div>
            </div>
            """
        html = f"""
        <div class="section">
            <h2>Recent Journal Entries</h2>
            {items}
        </div>
        """
        self._sections.append(ReportSection("journal", html, order=40))

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export(self, path: str | Path) -> Path:
        """Write the report to *path* and return the Path."""
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        sections = sorted(self._sections, key=lambda s: s.order)
        body = "\n".join(s.html for s in sections)
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self._title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root {{
    --accent: {self._accent};
    --bg: {self._bg};
    --card-bg: {self._card_bg};
    --text: {self._text};
    --secondary: {self._secondary};
}}
* {{ box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 24px;
    line-height: 1.6;
}}
.report-header {{
    text-align: center;
    padding: 32px 16px;
    margin-bottom: 24px;
    border-bottom: 3px solid var(--accent);
}}
.report-header h1 {{ margin: 0 0 8px; font-size: 2rem; }}
.report-header .subtitle {{ margin: 0; color: var(--secondary); font-size: 1.1rem; }}
.report-header .date-range {{ margin: 8px 0 0; color: var(--secondary); font-size: 0.9rem; }}
.report-header .disclaimer {{
    margin-top: 16px;
    font-size: 0.8rem;
    color: var(--secondary);
    font-style: italic;
}}
.section {{
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.section h2 {{
    margin: 0 0 16px;
    font-size: 1.3rem;
    color: var(--accent);
}}
.section h3 {{ margin: 16px 0 8px; font-size: 1rem; }}
.chart-container {{ position: relative; height: 280px; margin: 16px 0; }}
.two-col {{ display: flex; gap: 24px; flex-wrap: wrap; }}
.col {{ flex: 1; min-width: 220px; }}
.col ul {{ padding-left: 18px; margin: 0; }}
.col li {{ margin-bottom: 4px; }}
.metrics {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }}
.metric {{
    background: var(--bg);
    border-radius: 8px;
    padding: 16px 24px;
    text-align: center;
    flex: 1;
    min-width: 120px;
}}
.metric-value {{ display: block; font-size: 1.6rem; font-weight: 700; color: var(--accent); }}
.metric-label {{ display: block; font-size: 0.8rem; color: var(--secondary); margin-top: 4px; }}
.journal-item {{ padding: 12px 0; border-bottom: 1px solid #e9ecef; }}
.journal-item:last-child {{ border-bottom: none; }}
.journal-meta {{ font-size: 0.85rem; color: var(--secondary); margin-bottom: 4px; }}
.journal-body {{ font-size: 0.95rem; }}
.footer {{
    text-align: center;
    padding: 24px;
    color: var(--secondary);
    font-size: 0.8rem;
}}
@media print {{
    body {{ padding: 0; }}
    .section {{ box-shadow: none; border: 1px solid #e9ecef; break-inside: avoid; }}
}}
</style>
</head>
<body>
{body}
<div class="footer">
    Generated by Mindful Organizer on {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>
</body>
</html>"""
        out.write_text(html, encoding="utf-8")
        logger.info("Shareable report written to %s", out)
        return out
