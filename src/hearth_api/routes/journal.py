"""Journal endpoints — unified entry surface (mood / diary / writing / panic).

Backed by:
  - MoodManager           (SQLite mood_entries)
  - DiaryCardManager      (SQLite diary_cards)
  - JournalingManager     (file-based journal entries)
  - (panic entries reuse mood_entries with type='panic' for now)
"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query

from hearth_api.deps import (
    get_diary_card_manager,
    get_mood_manager,
)
from hearth_api.schemas.journal import (
    DiaryEntryCreate,
    EntryType,
    JournalEntry,
    JournalEntryCreate,
    JournalListResponse,
    MoodEntryCreate,
    PanicEntryCreate,
    WritingEntryCreate,
)

router = APIRouter(prefix="/journal", tags=["journal"])
TYPES_QUERY = Query(default=None)
LIMIT_QUERY = Query(default=50, le=200)
MOOD_MANAGER_DEP = Depends(get_mood_manager)
DIARY_CARD_MANAGER_DEP = Depends(get_diary_card_manager)


def _truncate(text: str, n: int = 140) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


@router.get("/", response_model=JournalListResponse)
async def list_entries(
    types: list[EntryType] | None = TYPES_QUERY,
    since: datetime | None = None,
    limit: int = LIMIT_QUERY,
    mood_mgr=MOOD_MANAGER_DEP,
    diary_mgr=DIARY_CARD_MANAGER_DEP,
) -> JournalListResponse:
    """Return entries merged across all sources, newest first."""
    since = since or datetime.now() - timedelta(days=30)
    entries: list[JournalEntry] = []

    if not types or EntryType.MOOD in types:
        for e in mood_mgr.get_entries_since(since):
            entries.append(
                JournalEntry(
                    id=e.id,
                    type=EntryType.MOOD,
                    timestamp=e.timestamp,
                    preview=f"{e.score} — {_truncate(e.note or '', 110)}".strip(" —"),
                    payload={"score": e.score, "note": e.note},
                    tags=list(e.tags or []),
                )
            )

    if not types or EntryType.DIARY in types:
        for c in diary_mgr.get_cards_since(since):
            entries.append(
                JournalEntry(
                    id=c.id,
                    type=EntryType.DIARY,
                    timestamp=c.timestamp,
                    preview=_diary_preview(c),
                    payload=c.to_dict(),
                    tags=list(c.tags or []),
                )
            )

    entries.sort(key=lambda e: e.timestamp, reverse=True)
    sliced = entries[:limit]
    return JournalListResponse(
        entries=sliced,
        total=len(entries),
        has_more=len(entries) > limit,
    )


@router.post("/", response_model=JournalEntry, status_code=201)
async def create_entry(
    entry: JournalEntryCreate,
    mood_mgr=MOOD_MANAGER_DEP,
    diary_mgr=DIARY_CARD_MANAGER_DEP,
) -> JournalEntry:
    """Create an entry of any type. Routes to the appropriate manager."""
    if isinstance(entry, MoodEntryCreate):
        saved = mood_mgr.log_mood(
            score=entry.score,
            note=entry.note or "",
            timestamp=entry.timestamp,
            tags=entry.tags,
        )
        return JournalEntry(
            id=saved.id,
            type=EntryType.MOOD,
            timestamp=saved.timestamp,
            preview=f"{saved.score} — {_truncate(saved.note, 110)}".strip(" —"),
            payload={"score": saved.score, "note": saved.note},
            tags=list(saved.tags or []),
        )
    if isinstance(entry, DiaryEntryCreate):
        saved = diary_mgr.save_card(entry.model_dump())
        return JournalEntry(
            id=saved.id,
            type=EntryType.DIARY,
            timestamp=saved.timestamp,
            preview=_diary_preview(saved),
            payload=saved.to_dict(),
            tags=list(saved.tags or []),
        )
    if isinstance(entry, (WritingEntryCreate, PanicEntryCreate)):
        # Writing + panic routing TBD — wire to JournalingManager + a panic
        # extension on MoodManager in Phase 3.
        raise HTTPException(
            status_code=501,
            detail=f"{entry.type} entry creation is implemented in Phase 3.",
        )

    raise HTTPException(status_code=400, detail="Unknown entry type")


def _diary_preview(card) -> str:
    """Single-line summary of a diary card for list display."""
    emo = ", ".join(f"{k} {v}" for k, v in list(card.emotions.items())[:2])
    skills = (
        f"skills: {', '.join(card.skills_used[:2])}" if card.skills_used else ""
    )
    return _truncate(" · ".join(part for part in (emo, skills) if part), 140)
