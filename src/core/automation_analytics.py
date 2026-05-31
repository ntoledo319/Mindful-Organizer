"""
Automation Analytics — measure the effectiveness of system automations.

Tracks:
- Rule firing frequency and success rate
- Focus mode session stats (duration, interruption rate, peak times)
- App guardian activity (top disruptors, most closed apps)
- Display adaptation events
- Correlation between automation and productivity/energy
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from core.paths import get_data_dir

logger = logging.getLogger(__name__)


@dataclass
class RuleEffectiveness:
    """Analytics for a single automation rule."""

    rule_name: str
    times_fired: int = 0
    times_cooldown_blocked: int = 0
    actions_succeeded: int = 0
    actions_failed: int = 0
    last_fired: str | None = None
    avg_actions_per_fire: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "times_fired": self.times_fired,
            "times_cooldown_blocked": self.times_cooldown_blocked,
            "actions_succeeded": self.actions_succeeded,
            "actions_failed": self.actions_failed,
            "last_fired": self.last_fired,
            "avg_actions_per_fire": round(self.avg_actions_per_fire, 2),
        }


@dataclass
class DailyAutomationSummary:
    """A single day's automation activity."""

    date: str
    focus_sessions: int = 0
    total_focus_minutes: int = 0
    focus_interruptions: int = 0
    apps_closed: int = 0
    display_adaptations: int = 0
    rules_fired: int = 0
    peak_focus_hour: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "focus_sessions": self.focus_sessions,
            "total_focus_minutes": self.total_focus_minutes,
            "focus_interruptions": self.focus_interruptions,
            "apps_closed": self.apps_closed,
            "display_adaptations": self.display_adaptations,
            "rules_fired": self.rules_fired,
            "peak_focus_hour": self.peak_focus_hour,
        }


class AutomationAnalytics:
    """Collects and reports on automation effectiveness."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.analytics_file = self.data_dir / "automation_analytics.json"

        self.rule_stats: dict[str, RuleEffectiveness] = defaultdict(
            lambda: RuleEffectiveness(rule_name="")
        )
        self.daily_summaries: dict[str, DailyAutomationSummary] = {}
        self._total_display_adaptations = 0
        self._total_apps_closed = 0

        self._load()

    # -- persistence ----------------------------------------------------------

    def _load(self) -> None:
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file) as f:
                    data = json.load(f)
                for name, stats in data.get("rule_stats", {}).items():
                    self.rule_stats[name] = RuleEffectiveness(
                        rule_name=stats["rule_name"],
                        times_fired=stats.get("times_fired", 0),
                        times_cooldown_blocked=stats.get("times_cooldown_blocked", 0),
                        actions_succeeded=stats.get("actions_succeeded", 0),
                        actions_failed=stats.get("actions_failed", 0),
                        last_fired=stats.get("last_fired"),
                        avg_actions_per_fire=stats.get("avg_actions_per_fire", 0.0),
                    )
                for date, summary in data.get("daily_summaries", {}).items():
                    self.daily_summaries[date] = DailyAutomationSummary(
                        date=summary["date"],
                        focus_sessions=summary.get("focus_sessions", 0),
                        total_focus_minutes=summary.get("total_focus_minutes", 0),
                        focus_interruptions=summary.get("focus_interruptions", 0),
                        apps_closed=summary.get("apps_closed", 0),
                        display_adaptations=summary.get("display_adaptations", 0),
                        rules_fired=summary.get("rules_fired", 0),
                        peak_focus_hour=summary.get("peak_focus_hour"),
                    )
                self._total_display_adaptations = data.get("total_display_adaptations", 0)
                self._total_apps_closed = data.get("total_apps_closed", 0)
            except (json.JSONDecodeError, OSError, KeyError) as exc:
                logger.warning("Failed to load automation analytics: %s", exc)

    def _save(self) -> None:
        data = {
            "rule_stats": {k: v.to_dict() for k, v in self.rule_stats.items()},
            "daily_summaries": {k: v.to_dict() for k, v in self.daily_summaries.items()},
            "total_display_adaptations": self._total_display_adaptations,
            "total_apps_closed": self._total_apps_closed,
            "saved_at": datetime.now().isoformat(),
        }
        with open(self.analytics_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    # -- event recording ------------------------------------------------------

    def record_rule_fired(self, rule_name: str, actions_succeeded: int, actions_failed: int) -> None:
        stats = self.rule_stats[rule_name]
        stats.rule_name = rule_name
        stats.times_fired += 1
        stats.actions_succeeded += actions_succeeded
        stats.actions_failed += actions_failed
        stats.last_fired = datetime.now().isoformat()
        total_actions = stats.actions_succeeded + stats.actions_failed
        if stats.times_fired > 0:
            stats.avg_actions_per_fire = total_actions / stats.times_fired

        self._today().rules_fired += 1
        self._save()

    def record_rule_cooldown(self, rule_name: str) -> None:
        stats = self.rule_stats[rule_name]
        stats.rule_name = rule_name
        stats.times_cooldown_blocked += 1
        self._save()

    def record_focus_session(self, duration_minutes: int, interrupted: bool) -> None:
        day = self._today()
        day.focus_sessions += 1
        day.total_focus_minutes += duration_minutes
        if interrupted:
            day.focus_interruptions += 1
        self._save()

    def record_display_adaptation(self) -> None:
        self._total_display_adaptations += 1
        self._today().display_adaptations += 1
        self._save()

    def record_apps_closed(self, count: int) -> None:
        self._total_apps_closed += count
        self._today().apps_closed += count
        self._save()

    def _today(self) -> DailyAutomationSummary:
        date_str = datetime.now().strftime("%Y-%m-%d")
        if date_str not in self.daily_summaries:
            self.daily_summaries[date_str] = DailyAutomationSummary(date=date_str)
        return self.daily_summaries[date_str]

    # -- reporting ------------------------------------------------------------

    def get_rule_effectiveness(self, days: int = 30) -> list[dict[str, Any]]:
        """Return effectiveness stats for all rules, sorted by most fired."""
        cutoff = datetime.now() - timedelta(days=days)
        results: list[dict[str, Any]] = []
        for _name, stats in sorted(self.rule_stats.items(), key=lambda x: x[1].times_fired, reverse=True):
            if stats.last_fired and datetime.fromisoformat(stats.last_fired) >= cutoff:
                total = stats.actions_succeeded + stats.actions_failed
                success_rate = stats.actions_succeeded / total if total > 0 else 0.0
                results.append({
                    **stats.to_dict(),
                    "success_rate": round(success_rate, 2),
                })
        return results

    def get_focus_trends(self, days: int = 30) -> dict[str, Any]:
        """Return focus mode trends over time."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [
            s for s in self.daily_summaries.values()
            if datetime.strptime(s.date, "%Y-%m-%d") >= cutoff
        ]
        if not recent:
            return {
                "total_sessions": 0,
                "total_minutes": 0,
                "avg_duration": 0,
                "interruption_rate": 0.0,
                "most_productive_day": None,
            }

        total_sessions = sum(s.focus_sessions for s in recent)
        total_minutes = sum(s.total_focus_minutes for s in recent)
        interruptions = sum(s.focus_interruptions for s in recent)
        best_day = max(recent, key=lambda s: s.total_focus_minutes)

        return {
            "total_sessions": total_sessions,
            "total_minutes": total_minutes,
            "avg_duration": round(total_minutes / total_sessions, 1) if total_sessions else 0,
            "interruption_rate": round(interruptions / total_sessions, 2) if total_sessions else 0.0,
            "most_productive_day": best_day.date,
            "most_productive_minutes": best_day.total_focus_minutes,
        }

    def get_weekly_summary(self) -> dict[str, Any]:
        """Return a 7-day summary for display in the UI."""
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        return {
            "dates": dates,
            "focus_minutes": [self.daily_summaries.get(d, DailyAutomationSummary(date=d)).total_focus_minutes for d in dates],
            "rules_fired": [self.daily_summaries.get(d, DailyAutomationSummary(date=d)).rules_fired for d in dates],
            "apps_closed": [self.daily_summaries.get(d, DailyAutomationSummary(date=d)).apps_closed for d in dates],
        }

    def get_overall_stats(self) -> dict[str, Any]:
        return {
            "total_rules_fired": sum(s.times_fired for s in self.rule_stats.values()),
            "total_display_adaptations": self._total_display_adaptations,
            "total_apps_closed": self._total_apps_closed,
            "unique_rules_used": len(self.rule_stats),
            "active_days": len(self.daily_summaries),
        }
