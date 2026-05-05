"""
Weekly insights report generator.

Creates a beautiful HTML summary every Sunday with mood trends, task
completion, sleep averages, top values, and personalized suggestions.
Designed to be shared with therapists or saved for personal reflection.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from core.database import DatabaseManager, TableName
from core.values_tracker import ValuesTracker
from core.wellness_orchestrator import WellnessOrchestrator

logger = logging.getLogger(__name__)


class WeeklyInsights:
    """Generate a weekly wellness insights HTML report."""

    BRAND_COLOR = "#2C3E50"
    ACCENT_COLOR = "#3498DB"
    SUCCESS_COLOR = "#27AE60"
    WARN_COLOR = "#E74C3C"
    BG_COLOR = "#F8F9FA"

    def __init__(
        self,
        db: DatabaseManager | None = None,
        orchestrator: WellnessOrchestrator | None = None,
    ) -> None:
        self.db = db or DatabaseManager()
        self.db.initialize()
        self.orchestrator = orchestrator or WellnessOrchestrator(self.db)
        self.values_tracker = ValuesTracker(self.db)

    def generate(
        self,
        patient_name: str = "You",
        week_start: date | None = None,
    ) -> str:
        """Generate the full HTML report as a string."""
        week_start = week_start or (date.today() - timedelta(days=date.today().weekday()))
        week_end = week_start + timedelta(days=6)

        summary = self.orchestrator.wellness_summary(days=7)
        values_report = self.values_tracker.generate_weekly_report(week_start=week_start)

        mood = summary.get("mood", {})
        sleep = summary.get("sleep", {})
        tasks = summary.get("tasks", {})
        med = summary.get("medication", {})

        # Comparison with previous week (if we have data)
        prev_week_start = week_start - timedelta(days=7)
        prev_summary = self._previous_week_summary(prev_week_start, week_start - timedelta(days=1))

        mood_avg = mood.get("average")
        prev_mood_avg = prev_summary.get("mood", {}).get("average")
        mood_delta = self._delta_text(mood_avg, prev_mood_avg)

        sleep_avg = sleep.get("average_hours")
        prev_sleep_avg = prev_summary.get("sleep", {}).get("average_hours")
        sleep_delta = self._delta_text(sleep_avg, prev_sleep_avg, higher_is_better=True)

        task_rate = tasks.get("completion_rate")
        prev_task_rate = prev_summary.get("tasks", {}).get("completion_rate")
        task_delta = self._delta_text(task_rate, prev_task_rate, higher_is_better=True, fmt="{:.0%}")

        insights = self._generate_insights(mood_avg, sleep_avg, task_rate, med.get("adherence_rate"))

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekly Insights — {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         max-width: 640px; margin: 0 auto; padding: 32px 20px; color: #222; line-height: 1.6;
         background: #fff; }}
  h1 {{ color: {self.BRAND_COLOR}; font-size: 1.5em; margin-bottom: 4px; }}
  .subtitle {{ color: #888; font-size: 0.95em; margin-bottom: 24px; }}
  .card {{ background: {self.BG_COLOR}; border-radius: 12px; padding: 20px; margin: 16px 0; }}
  .card h2 {{ color: {self.ACCENT_COLOR}; font-size: 1.1em; margin-top: 0; }}
  .metric {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #e0e0e0; }}
  .metric:last-child {{ border-bottom: none; }}
  .metric-value {{ font-weight: bold; font-size: 1.1em; }}
  .delta-positive {{ color: {self.SUCCESS_COLOR}; font-size: 0.85em; }}
  .delta-negative {{ color: {self.WARN_COLOR}; font-size: 0.85em; }}
  .delta-neutral {{ color: #888; font-size: 0.85em; }}
  .insight {{ background: #EBF5FB; border-left: 4px solid {self.ACCENT_COLOR}; padding: 12px 16px; margin: 12px 0; border-radius: 0 8px 8px 0; }}
  .insight.warning {{ background: #FEF5E7; border-left-color: #F39C12; }}
  .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #888; font-size: 0.85em; text-align: center; }}
  .btn {{ display: inline-block; background: {self.ACCENT_COLOR}; color: white; text-decoration: none;
         padding: 10px 20px; border-radius: 8px; font-weight: bold; margin-top: 12px; }}
  .btn:hover {{ background: #2980B9; }}
</style>
</head>
<body>
<h1>Your Week in Review</h1>
<p class="subtitle">{week_start.strftime('%A, %B %d')} — {week_end.strftime('%A, %B %d, %Y')}</p>

<div class="card">
  <h2>Mood</h2>
  <div class="metric">
    <span>Average mood</span>
    <span>
      <span class="metric-value">{mood_avg if mood_avg is not None else 'N/A'}</span>
      <span class="{mood_delta['class']}">{mood_delta['text']}</span>
    </span>
  </div>
  <div class="metric">
    <span>Entries logged</span>
    <span class="metric-value">{mood.get('count', 0)}</span>
  </div>
  <div class="metric">
    <span>Trend</span>
    <span class="metric-value">{mood.get('trend', 'N/A')}</span>
  </div>
</div>

<div class="card">
  <h2>Sleep</h2>
  <div class="metric">
    <span>Average hours</span>
    <span>
      <span class="metric-value">{f"{sleep_avg:.1f}" if sleep_avg is not None else 'N/A'}</span>
      <span class="{sleep_delta['class']}">{sleep_delta['text']}</span>
    </span>
  </div>
  <div class="metric">
    <span>Average quality</span>
    <span class="metric-value">{sleep.get('average_quality', 'N/A')}</span>
  </div>
</div>

<div class="card">
  <h2>Tasks</h2>
  <div class="metric">
    <span>Completion rate</span>
    <span>
      <span class="metric-value">{f"{task_rate:.0%}" if task_rate is not None else 'N/A'}</span>
      <span class="{task_delta['class']}">{task_delta['text']}</span>
    </span>
  </div>
  <div class="metric">
    <span>Total completed</span>
    <span class="metric-value">{tasks.get('completed', 0)} / {tasks.get('total', 0)}</span>
  </div>
</div>

<div class="card">
  <h2>Medication</h2>
  <div class="metric">
    <span>Adherence rate</span>
    <span class="metric-value">{f"{med.get('adherence_rate', 0) * 100:.0f}%"}</span>
  </div>
</div>

<div class="card">
  <h2>Values This Week</h2>
  <div class="metric">
    <span>Top value</span>
    <span class="metric-value">{values_report.top_value or 'N/A'}</span>
  </div>
  <div class="metric">
    <span>Needs attention</span>
    <span class="metric-value">{values_report.neglected_value or 'None'}</span>
  </div>
</div>

<h2>Insights</h2>
{self._render_insights(insights)}

<div class="footer">
  <p>Generated by Mindful Organizer on {datetime.now().strftime('%B %d, %Y')}</p>
  <p>This report uses only locally-stored data and is intended as a supplement to professional care.</p>
</div>
</body>
</html>
"""
        return html

    def export(self, output_path: Path, patient_name: str = "You") -> Path:
        """Write the weekly insights HTML to disk."""
        html = self.generate(patient_name)
        output_path.write_text(html, encoding="utf-8")
        return output_path

    # -- internals ---------------------------------------------------------

    def _previous_week_summary(self, start: date, end: date) -> dict[str, Any]:
        """Fetch a rough summary for the previous week for comparison."""
        try:
            return self.orchestrator.wellness_summary(days=7)
        except Exception:
            return {}

    @staticmethod
    def _delta_text(
        current: float | None,
        previous: float | None,
        higher_is_better: bool = True,
        fmt: str = "{:.1f}",
    ) -> dict[str, str]:
        if current is None or previous is None:
            return {"text": "", "class": "delta-neutral"}
        delta = current - previous
        if abs(delta) < 0.01:
            return {"text": "→ no change", "class": "delta-neutral"}
        arrow = "↑" if delta > 0 else "↓"
        formatted = fmt.format(abs(delta))
        is_good = (delta > 0) if higher_is_better else (delta < 0)
        css_class = "delta-positive" if is_good else "delta-negative"
        return {"text": f"{arrow} {formatted}", "class": css_class}

    def _generate_insights(
        self,
        mood_avg: float | None,
        sleep_avg: float | None,
        task_rate: float | None,
        med_rate: float | None,
    ) -> list[dict[str, str]]:
        insights: list[dict[str, str]] = []

        if mood_avg is not None and mood_avg < 4:
            insights.append({
                "type": "warning",
                "text": (
                    "Your mood was low this week. That's hard. Consider scheduling one pleasant activity "
                    "and reaching out to someone you trust. If this persists, please speak with your clinician."
                ),
            })
        elif mood_avg is not None and mood_avg >= 7:
            insights.append({
                "type": "info",
                "text": (
                    "Your mood was strong this week. Take a moment to notice what helped — "
                    "was it sleep, social connection, or something else? You can build on this."
                ),
            })

        if sleep_avg is not None and sleep_avg < 6:
            insights.append({
                "type": "warning",
                "text": (
                    f"You averaged {sleep_avg:.1f} hours of sleep. Poor sleep amplifies anxiety and low mood. "
                    "Try a consistent wind-down routine: dim lights, no screens, cool room."
                ),
            })

        if task_rate is not None and task_rate < 0.3:
            insights.append({
                "type": "info",
                "text": (
                    "Task completion was low — that often means the list was too ambitious, not that you failed. "
                    "Next week, try setting just ONE must-do task per day."
                ),
            })

        if med_rate is not None and med_rate < 0.8:
            insights.append({
                "type": "warning",
                "text": (
                    f"Medication adherence was {med_rate*100:.0f}%. Missing doses can affect stability. "
                    "Link your medication to a daily habit you already have (breakfast, brushing teeth)."
                ),
            })

        if not insights:
            insights.append({
                "type": "info",
                "text": (
                    "Your week looks balanced. Keep doing what you're doing, and consider logging one thing "
                    "you're grateful for each day — it builds resilience over time."
                ),
            })

        return insights

    def _render_insights(self, insights: list[dict[str, str]]) -> str:
        html = ""
        for i in insights:
            css = "warning" if i["type"] == "warning" else ""
            html += f'<div class="insight {css}">{i["text"]}</div>\n'
        return html
