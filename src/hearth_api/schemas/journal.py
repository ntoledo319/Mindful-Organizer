"""Journal entry schemas — the unified surface for mood, diary card, free-form
writing, and panic-log entries per `docs/design/03-information-architecture.md`.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class EntryType(str, Enum):
    MOOD = "mood"
    DIARY = "diary"
    WRITING = "writing"
    PANIC = "panic"
    TRIGGER = "trigger"


class JournalEntryBase(BaseModel):
    type: EntryType
    timestamp: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)


class MoodEntryCreate(JournalEntryBase):
    type: Literal[EntryType.MOOD] = EntryType.MOOD
    score: int = Field(ge=1, le=10)
    note: str | None = None


class DiaryEntryCreate(JournalEntryBase):
    type: Literal[EntryType.DIARY] = EntryType.DIARY
    emotions: dict[str, int]  # emotion_name -> intensity 0-5
    urges: dict[str, int]
    skills_used: list[str]
    target_behaviors: dict[str, int]
    medication_taken: bool
    substance_use: bool = False
    notes: str | None = None


class WritingEntryCreate(JournalEntryBase):
    type: Literal[EntryType.WRITING] = EntryType.WRITING
    body: str
    prompt: str | None = None


class PanicEntryCreate(JournalEntryBase):
    type: Literal[EntryType.PANIC] = EntryType.PANIC
    intensity: int = Field(ge=1, le=10)
    trigger: str | None = None
    duration_minutes: int
    skills_used: list[str] = Field(default_factory=list)
    notes: str | None = None


JournalEntryCreate = (
    MoodEntryCreate | DiaryEntryCreate | WritingEntryCreate | PanicEntryCreate
)


class JournalEntry(BaseModel):
    """Read shape — server-assigned id + canonical fields."""
    id: str
    type: EntryType
    timestamp: datetime
    preview: str  # first ~140 chars for list display
    payload: dict  # full entry data, type-dependent
    tags: list[str] = Field(default_factory=list)


class JournalListResponse(BaseModel):
    entries: list[JournalEntry]
    total: int
    has_more: bool
