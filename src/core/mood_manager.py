"""Mood manager — bridges mood tracker widget to SQLite.

Stores mood entries in the mood_entries table and provides
analytics access compatible with the MoodTrackerWidget expectations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from core.database import DatabaseManager, TableName
from core.mood_analytics import MoodAnalytics, MoodEntry

logger = logging.getLogger(__name__)


@dataclass
class MoodTrend:
    """Simple trend result for widget compatibility."""
    direction: Any  # TrendDirection enum from mood_analytics
    moving_avg_7: float | None = None


class MoodManager:
    """CRUD for mood entries with analytics delegation."""

    def __init__(self, db: DatabaseManager | None = None) -> None:
        self._db = db or DatabaseManager()
        self._entries: list[MoodEntry] = []
        self._load_entries()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_entries(self) -> None:
        """Hydrate in-memory list from DB."""
        try:
            rows = self._db.query(TableName.MOOD_ENTRIES, order_by="timestamp DESC", limit=1000)
        except Exception as exc:
            logger.debug(f"Mood entries load error: {exc}")
            return
        self._entries.clear()
        for row in rows:
            try:
                ts = datetime.fromisoformat(row["timestamp"])
                me = MoodEntry(
                    timestamp=ts,
                    mood_score=float(row["mood_score"]),
                    energy_score=float(row["energy_level"] or 5),
                    symptoms=[s.strip() for s in (row["emotions"] or "").split(",") if s.strip()],
                    notes=row["notes"] or "",
                    activities=[a.strip() for a in (row["context"] or "").split(",") if a.strip()],
                )
                self._entries.append(me)
            except Exception as exc:
                logger.debug(f"Mood entry parse error: {exc}")

    def add_entry(self, entry: dict[str, Any]) -> int:
        """Insert a mood entry into the database."""
        ts = entry.get("timestamp")
        if isinstance(ts, datetime):
            ts = ts.isoformat()
        emotions = ", ".join(entry.get("symptoms", []))
        context = ", ".join(entry.get("therapy_skills", []))
        row_id = self._db.insert(
            TableName.MOOD_ENTRIES,
            timestamp=ts,
            mood_score=entry.get("mood_score", 5),
            energy_level=entry.get("energy_score", 50) // 10,
            emotions=emotions,
            notes=entry.get("notes", ""),
            context=context,
        )
        # Re-hydrate in-memory list
        self._load_entries()
        return row_id

    # ------------------------------------------------------------------
    # Analytics delegation
    # ------------------------------------------------------------------

    def mood_trend(self) -> MoodTrend:
        """Return a simple trend object for widget compatibility."""
        from core.mood_analytics import TrendDirection
        if not self._entries:
            return MoodTrend(direction=TrendDirection.STABLE)
        ma = MoodAnalytics(self._entries, [])
        trend = ma.mood_trend()
        return MoodTrend(
            direction=trend.direction,
            moving_avg_7=trend.moving_avg_7,
        )

    def mood_volatility(self) -> float:
        if not self._entries:
            return 0.0
        return MoodAnalytics(self._entries, []).volatility()

    def identify_triggers(self) -> list[Any]:
        if not self._entries:
            return []
        return MoodAnalytics(self._entries, []).identify_triggers()
