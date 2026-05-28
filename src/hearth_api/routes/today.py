"""Today endpoint — the data backing the home screen."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from hearth_api.deps import (
    get_mood_manager,
    get_sleep_tracker,
    get_task_manager,
    get_wellness_orchestrator,
)
from hearth_api.schemas.today import (
    NextAction,
    OpenLoop,
    RightNowState,
    TimelineEntry,
    TodayResponse,
)

router = APIRouter(prefix="/today", tags=["today"])
WELLNESS_ORCHESTRATOR_DEP = Depends(get_wellness_orchestrator)
MOOD_MANAGER_DEP = Depends(get_mood_manager)
SLEEP_TRACKER_DEP = Depends(get_sleep_tracker)
TASK_MANAGER_DEP = Depends(get_task_manager)


@router.get("/", response_model=TodayResponse)
async def today(
    orchestrator=WELLNESS_ORCHESTRATOR_DEP,
    mood_mgr=MOOD_MANAGER_DEP,
    sleep=SLEEP_TRACKER_DEP,
    tasks=TASK_MANAGER_DEP,
) -> TodayResponse:
    """Assemble the Today view — replaces the legacy Dashboard."""
    now = datetime.now()
    snapshot = orchestrator.get_snapshot()

    right_now = RightNowState(
        text=_right_now_sentence(snapshot),
        detected_at=now,
        energy_label=_energy_label(snapshot.energy_level),
        confidence=getattr(snapshot, "confidence", 0.75),
    )

    next_action = _pick_next_action(snapshot, mood_mgr, tasks)

    timeline = _build_timeline(now, mood_mgr, sleep, tasks)

    open_loops = _gather_open_loops(tasks)

    return TodayResponse(
        day_header=_greeting(now),
        day_date=now.strftime("%B %-d · %-I:%M %p"),
        right_now=right_now,
        next_action=next_action,
        timeline=timeline,
        open_loops=open_loops,
    )


def _greeting(now: datetime) -> str:
    hour = now.hour
    day = now.strftime("%A")
    if hour < 12:
        return f"{day} morning."
    if hour < 17:
        return f"{day} afternoon."
    if hour < 22:
        return f"{day} evening."
    return f"Late {day.lower()}."


def _energy_label(level):
    """Map orchestrator energy (0-100) to one of the five labels."""
    if level is None:
        return None
    if level < 20:
        return "very-low"
    if level < 40:
        return "low"
    if level < 60:
        return "mid"
    if level < 80:
        return "high"
    return "peak"


def _right_now_sentence(snapshot) -> str:
    """Render snapshot into one quiet sentence — per the design brief."""
    energy = _energy_label(snapshot.energy_level) or "mid"
    parts = []
    if energy == "very-low":
        parts.append("Energy is very low.")
    elif energy == "low":
        parts.append("Energy reads below baseline.")
    elif energy == "peak":
        parts.append("Energy is peaking.")
    elif energy == "high":
        parts.append("Energy is solid.")
    else:
        parts.append("Energy reads mid-baseline.")

    if getattr(snapshot, "sleep_deficit_minutes", 0) > 30:
        m = snapshot.sleep_deficit_minutes
        parts.append(f"Sleep came in short by {m} minutes.")

    open_count = getattr(snapshot, "open_task_count", None)
    if open_count:
        parts.append(
            f"{open_count} open loop{'s' if open_count != 1 else ''} from yesterday."
        )

    return " ".join(parts)


def _pick_next_action(snapshot, mood_mgr, tasks) -> NextAction:
    """Heuristic — replaced with ML rec in a later phase."""
    energy = _energy_label(snapshot.energy_level)

    if energy in ("very-low", "low"):
        return NextAction(
            title="Five minutes of box breathing.",
            rationale=(
                "Suggested because your morning energy ran low after a short "
                "sleep two days in a row."
            ),
            action_type="practice",
            target_id="breathing.box",
        )

    if getattr(snapshot, "last_mood_age_hours", 99) > 6:
        return NextAction(
            title="Log how you feel right now.",
            rationale="It's been a while since your last check-in.",
            action_type="log",
            target_id="mood.quick",
        )

    open_tasks = tasks.get_tasks() if hasattr(tasks, "get_tasks") else []
    if open_tasks:
        first = open_tasks[0]
        return NextAction(
            title=first.title,
            rationale="Your top open loop.",
            action_type="task",
            target_id=first.id,
        )

    return NextAction(
        title="You're caught up.",
        rationale="Nothing pressing. Consider a short walk.",
        action_type="rest",
    )


def _build_timeline(now, mood_mgr, sleep, tasks) -> list[TimelineEntry]:
    """Today's significant entries — sleep, meds, mood, focus sessions."""
    entries: list[TimelineEntry] = []
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if hasattr(sleep, "get_last_entry"):
        last_sleep = sleep.get_last_entry()
        if last_sleep and last_sleep.wake_time >= today_start:
            entries.append(
                TimelineEntry(
                    id=last_sleep.id,
                    timestamp=last_sleep.wake_time,
                    type="sleep",
                    summary=f"Woke up — slept {last_sleep.duration_label}, quality {last_sleep.quality}/10",
                )
            )

    if hasattr(mood_mgr, "get_entries_since"):
        for m in mood_mgr.get_entries_since(today_start):
            entries.append(
                TimelineEntry(
                    id=m.id,
                    timestamp=m.timestamp,
                    type="mood",
                    summary=f"Logged mood {m.score}" + (f" — \"{m.note}\"" if m.note else ""),
                )
            )

    entries.sort(key=lambda e: e.timestamp)
    return entries


def _gather_open_loops(tasks) -> list[OpenLoop]:
    """Top 5 actionable items from across the system."""
    loops: list[OpenLoop] = []
    if hasattr(tasks, "get_tasks"):
        for t in tasks.get_tasks()[:5]:
            loops.append(
                OpenLoop(
                    id=t.id,
                    title=t.title,
                    age_label=_age_label(t),
                    type="task",
                )
            )
    return loops


def _age_label(task) -> str:
    """Human age string for an open task."""
    from datetime import datetime as _dt
    try:
        created = _dt.fromisoformat(task.created_at)
        days = (datetime.now() - created).days
    except Exception:
        return "soon"
    if days == 0:
        return "today"
    if days == 1:
        return "1d"
    if days < 7:
        return f"{days}d"
    return "1w+"
