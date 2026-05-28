"""Diary Card manager — DBT-style daily tracking.

Stores one card per day with emotions, urges, skills used,
effectiveness ratings, target behaviors, and medication adherence.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from core.constants import Condition
from core.database import DatabaseManager, TableName

logger = logging.getLogger(__name__)


@dataclass
class DiaryCard:
    """A single day's DBT diary card."""

    id: int | None = None
    date: date = field(default_factory=date.today)
    mood_score: int = 5
    emotions: list[str] = field(default_factory=list)
    urges: dict[str, int] = field(default_factory=dict)
    skills_used: list[str] = field(default_factory=list)
    skills_effectiveness: int = 3
    target_behaviors: dict[str, int] = field(default_factory=dict)
    substances_used: str = ""
    medications_taken: bool = True
    notes: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_row(cls, row: Any) -> DiaryCard:
        """Build from a sqlite3.Row."""
        return cls(
            id=row["id"],
            date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
            mood_score=row["mood_score"],
            emotions=json.loads(row["emotions"] or "[]"),
            urges=json.loads(row["urges_json"] or "{}"),
            skills_used=json.loads(row["skills_used_json"] or "[]"),
            skills_effectiveness=row["skills_effectiveness"] or 3,
            target_behaviors=json.loads(row["target_behaviors_json"] or "{}"),
            substances_used=row["substances_used"] or "",
            medications_taken=bool(row["medications_taken"]),
            notes=row["notes"] or "",
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )

    def to_db_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "mood_score": self.mood_score,
            "emotions": json.dumps(self.emotions),
            "urges_json": json.dumps(self.urges),
            "skills_used_json": json.dumps(self.skills_used),
            "skills_effectiveness": self.skills_effectiveness,
            "target_behaviors_json": json.dumps(self.target_behaviors),
            "substances_used": self.substances_used,
            "medications_taken": 1 if self.medications_taken else 0,
            "notes": self.notes,
            "updated_at": datetime.now().isoformat(),
        }


# ---------------------------------------------------------------------------
# Default content packs keyed by condition
# ---------------------------------------------------------------------------

DEFAULT_EMOTIONS = [
    "Joy", "Sadness", "Anger", "Fear", "Shame", "Guilt", "Disgust",
    "Love", "Envy", "Anxiety", "Hope", "Loneliness", "Gratitude",
]

CONDITION_EMOTIONS: dict[str, list[str]] = {
    "ADHD": ["Frustration", "Boredom", "Excitement", "Overwhelm"],
    "Anxiety": ["Dread", "Panic", "Worry", "Nervousness"],
    "Depression": ["Numbness", "Hopelessness", "Apathy", "Despair"],
    "OCD": ["Doubt", "Urgency", "Relief", "Disgust"],
    "PTSD": ["Hypervigilance", "Detachment", "Terror", "Grief"],
}

DEFAULT_URGES = {
    "Self-harm": 0,
    "Suicide": 0,
    "Substance use": 0,
    "Binge/purge": 0,
    "Aggression": 0,
}

CONDITION_URGES: dict[str, dict[str, int]] = {
    "ADHD": {"Impulsive spending": 0, "Interrupting": 0, "Risky behavior": 0},
    "Anxiety": {"Avoidance": 0, "Reassurance seeking": 0, "Safety behavior": 0},
    "Depression": {"Isolation": 0, "Self-neglect": 0, "Hopelessness act": 0},
    "OCD": {"Checking": 0, "Washing": 0, "Mental compulsion": 0, "Reassurance": 0},
    "PTSD": {"Dissociation": 0, "Substance use": 0, "Avoidance": 0},
}

DEFAULT_SKILLS = [
    "Mindfulness", "Opposite Action", "Check the Facts", "TIPP",
    "Radical Acceptance", "Self-Soothe", "IMPROVE", "DEAR MAN",
    "Chain Analysis", "Pros & Cons",
]

CONDITION_SKILLS: dict[str, list[str]] = {
    "ADHD": ["Pomodoro", "Body Double", "Externalize", "Break It Down"],
    "Anxiety": ["Progressive Relaxation", "Worry Time", "Exposure", "Grounding"],
    "Depression": ["Behavioral Activation", "Opposite Action", "Pleasant Events", "Values"],
    "OCD": ["ERP", "Delay Ritual", "Mindfulness", "Uncertainty Tolerance"],
    "PTSD": ["Grounding", "Safe Place Imagery", "Container", "Window of Tolerance"],
}

DEFAULT_TARGETS = {
    "Skipped meals": 0,
    "Missed medication": 0,
    "Sleep disruption": 0,
    "Social withdrawal": 0,
}

CONDITION_TARGETS: dict[str, dict[str, int]] = {
    "ADHD": {"Missed deadlines": 0, "Lost items": 0, "Hyperfocus neglect": 0},
    "Anxiety": {"Avoided situation": 0, "Safety ritual": 0, "Reassurance seeking": 0},
    "Depression": {"Skipped hygiene": 0, "Missed obligations": 0, "Isolation": 0},
    "OCD": {"Compulsion": 0, "Avoidance": 0, "Mental review": 0},
    "PTSD": {"Flashback": 0, "Nightmare": 0, "Hypervigilance": 0, "Dissociation": 0},
}


class DiaryCardManager:
    """CRUD and analytics for DBT diary cards."""

    def __init__(self, db: DatabaseManager | None = None) -> None:
        self._db = db or DatabaseManager()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save(self, card: DiaryCard) -> int:
        """Insert or update a diary card. Returns row id."""
        existing = self.get(card.date)
        data = card.to_db_dict()
        if existing and existing.id is not None:
            self._db.update(TableName.DIARY_CARDS, existing.id, **data)
            return existing.id
        return self._db.insert(TableName.DIARY_CARDS, **data)

    def get(self, day: date) -> DiaryCard | None:
        """Fetch the card for a specific day."""
        rows = self._db.query(
            TableName.DIARY_CARDS, where="date = ?", params=(day.isoformat(),)
        )
        if rows:
            return DiaryCard.from_row(rows[0])
        return None

    def list_range(self, start: date, end: date) -> list[DiaryCard]:
        """Fetch cards in a date range, ordered by date."""
        rows = self._db.query(
            TableName.DIARY_CARDS,
            where="date BETWEEN ? AND ?",
            params=(start.isoformat(), end.isoformat()),
            order_by="date ASC",
        )
        return [DiaryCard.from_row(r) for r in rows]

    def delete(self, day: date) -> bool:
        """Delete a card for a specific day."""
        existing = self.get(day)
        if not existing or existing.id is None:
            return False
        return self._db.delete(TableName.DIARY_CARDS, existing.id) > 0

    # ------------------------------------------------------------------
    # Content helpers
    # ------------------------------------------------------------------

    @staticmethod
    def emotions_for_conditions(conditions: list[Condition]) -> list[str]:
        base = list(DEFAULT_EMOTIONS)
        seen = set(base)
        for cond in conditions:
            for e in CONDITION_EMOTIONS.get(cond.value, []):
                if e not in seen:
                    seen.add(e)
                    base.append(e)
        return base

    @staticmethod
    def urges_for_conditions(conditions: list[Condition]) -> dict[str, int]:
        result = dict(DEFAULT_URGES)
        for cond in conditions:
            result.update(CONDITION_URGES.get(cond.value, {}))
        return result

    @staticmethod
    def skills_for_conditions(conditions: list[Condition]) -> list[str]:
        base = list(DEFAULT_SKILLS)
        seen = set(base)
        for cond in conditions:
            for s in CONDITION_SKILLS.get(cond.value, []):
                if s not in seen:
                    seen.add(s)
                    base.append(s)
        return base

    @staticmethod
    def targets_for_conditions(conditions: list[Condition]) -> dict[str, int]:
        result = dict(DEFAULT_TARGETS)
        for cond in conditions:
            result.update(CONDITION_TARGETS.get(cond.value, {}))
        return result

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def skill_effectiveness(self, days: int = 30) -> dict[str, list[int]]:
        """Map skill name -> list of effectiveness scores for days that skill was used."""
        from datetime import timedelta
        end = date.today()
        start = end - timedelta(days=days)
        cards = self.list_range(start, end)
        out: dict[str, list[int]] = {}
        for card in cards:
            for skill in card.skills_used:
                out.setdefault(skill, []).append(card.skills_effectiveness)
        return out

    def urge_trend(self, days: int = 14) -> dict[str, list[tuple[str, int]]]:
        """Map urge name -> [(date_str, intensity), ...]."""
        from datetime import timedelta
        end = date.today()
        start = end - timedelta(days=days)
        cards = self.list_range(start, end)
        out: dict[str, list[tuple[str, int]]] = {}
        for card in cards:
            for urge, intensity in card.urges.items():
                out.setdefault(urge, []).append((card.date.isoformat(), intensity))
        return out

    def target_frequency(self, days: int = 30) -> dict[str, int]:
        """Count how many days each target behavior occurred (>0)."""
        from datetime import timedelta
        end = date.today()
        start = end - timedelta(days=days)
        cards = self.list_range(start, end)
        out: dict[str, int] = {}
        for card in cards:
            for target, count in card.target_behaviors.items():
                if count > 0:
                    out[target] = out.get(target, 0) + 1
        return out

    def mood_trend(self, days: int = 14) -> list[tuple[str, int]]:
        """List of (date_str, mood_score) for the range."""
        from datetime import timedelta
        end = date.today()
        start = end - timedelta(days=days)
        cards = self.list_range(start, end)
        return [(c.date.isoformat(), c.mood_score) for c in cards]

    def streak_medication(self) -> int:
        """Consecutive days with medications_taken=True, up to today."""
        cards = self.list_range(date.today() - __import__("datetime").timedelta(days=365), date.today())
        streak = 0
        for card in reversed(cards):
            if card.medications_taken:
                streak += 1
            else:
                break
        return streak
