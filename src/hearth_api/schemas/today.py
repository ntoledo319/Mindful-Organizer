"""Today screen schemas — drives the home view per the IA spec."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class RightNowState(BaseModel):
    """One-sentence summary of current psychological state."""
    text: str
    detected_at: datetime
    energy_label: Literal["very-low", "low", "mid", "high", "peak"] | None = None
    confidence: float  # 0-1, how confident the orchestrator is


class NextAction(BaseModel):
    """The single most-actionable thing in the next 5 minutes."""
    title: str
    rationale: str
    action_type: Literal[
        "practice",        # start breathing / grounding
        "log",             # log mood / diary card
        "focus",           # start focus session
        "task",            # complete a specific task
        "rest",            # take a break / nothing to do
    ]
    target_id: str | None = None  # task id, practice id, etc


class TimelineEntry(BaseModel):
    id: str
    timestamp: datetime
    type: Literal["mood", "sleep", "focus", "medication", "diary", "writing", "panic"]
    summary: str  # one-line description


class OpenLoop(BaseModel):
    id: str
    title: str
    age_label: str  # "1d", "soon", "2d"
    type: Literal["task", "medication", "diary", "automation_pending"]


class TodayResponse(BaseModel):
    day_header: str  # e.g. "Saturday morning."
    day_date: str    # e.g. "May 24 · 8:42 AM"
    right_now: RightNowState
    next_action: NextAction
    timeline: list[TimelineEntry]
    open_loops: list[OpenLoop]
