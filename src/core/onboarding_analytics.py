"""
Privacy-respecting onboarding analytics.

Tracks completion rates per onboarding step so developers can identify
drop-off points. No health data, no PII, no IP — just step-level funnel
metrics stored locally in JSON.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from core.paths import get_data_dir

logger = logging.getLogger(__name__)

DATA_DIR = get_data_dir(create=False)
ANALYTICS_FILE = DATA_DIR / "onboarding_analytics.json"


class OnboardingStep(Enum):
    WELCOME = "welcome"
    NAME = "name"
    CONDITIONS = "conditions"
    THERAPY_TYPES = "therapy_types"
    THEME = "theme"
    FIRST_TASK = "first_task"
    FIRST_MOOD = "first_mood"
    COMPLETE = "complete"


@dataclass
class StepEvent:
    step: str
    event: str  # "started" | "completed" | "skipped" | "abandoned"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_seconds: float = 0.0


@dataclass
class OnboardingFunnel:
    session_id: str
    started_at: str
    completed_at: str | None = None
    steps: list[StepEvent] = field(default_factory=list)
    source: str = "organic"


class OnboardingAnalytics:
    """Track onboarding funnel without collecting PII or health data."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or DATA_DIR
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._file = self._data_dir / "onboarding_analytics.json"
        self._sessions: list[OnboardingFunnel] = []
        self._current: OnboardingFunnel | None = None
        self._load()

    # -- persistence -------------------------------------------------------

    def _load(self) -> None:
        if self._file.exists():
            try:
                raw = json.loads(self._file.read_text(encoding="utf-8"))
                self._sessions = [OnboardingFunnel(**s) for s in raw.get("sessions", [])]
            except (json.JSONDecodeError, TypeError):
                self._sessions = []
        else:
            self._sessions = []

    def _save(self) -> None:
        try:
            data = {
                "version": 1,
                "updated_at": datetime.now().isoformat(),
                "sessions": [asdict(s) for s in self._sessions],
            }
            self._file.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        except OSError:
            logger.exception("Failed to save onboarding analytics")

    # -- session management ------------------------------------------------

    def start_session(self, source: str = "organic") -> None:
        import uuid

        self._current = OnboardingFunnel(
            session_id=str(uuid.uuid4())[:8],
            started_at=datetime.now().isoformat(),
            source=source,
        )
        logger.info("Onboarding session %s started", self._current.session_id)

    def log_step(self, step: OnboardingStep, event: str, duration_seconds: float = 0.0) -> None:
        if self._current is None:
            self.start_session()
        assert self._current is not None
        self._current.steps.append(StepEvent(
            step=step.value,
            event=event,
            duration_seconds=duration_seconds,
        ))
        if step == OnboardingStep.COMPLETE and event == "completed":
            self._current.completed_at = datetime.now().isoformat()
            self._sessions.append(self._current)
            self._current = None
            self._save()
            logger.info("Onboarding completed")
        elif event in ("abandoned", "skipped"):
            # Save incomplete sessions too for drop-off analysis
            self._sessions.append(self._current)
            self._current = None
            self._save()

    def complete(self) -> None:
        self.log_step(OnboardingStep.COMPLETE, "completed")

    def abandon(self) -> None:
        self.log_step(OnboardingStep.COMPLETE, "abandoned")

    # -- reporting ---------------------------------------------------------

    def funnel_report(self) -> dict[str, Any]:
        """Return completion rates per step."""
        if not self._sessions:
            return {}

        total = len(self._sessions)
        step_counts: dict[str, dict[str, int]] = {}

        for session in self._sessions:
            seen_steps = set()
            for ev in session.steps:
                if ev.step not in step_counts:
                    step_counts[ev.step] = {"started": 0, "completed": 0, "skipped": 0}
                if ev.event == "completed" and ev.step not in seen_steps:
                    step_counts[ev.step]["completed"] += 1
                    seen_steps.add(ev.step)
                elif ev.event == "started":
                    step_counts[ev.step]["started"] += 1
                elif ev.event == "skipped":
                    step_counts[ev.step]["skipped"] += 1

        report: dict[str, Any] = {
            "total_sessions": total,
            "completion_rate": sum(1 for s in self._sessions if s.completed_at is not None) / total,
            "steps": {},
        }
        for step in OnboardingStep:
            counts = step_counts.get(step.value, {"started": 0, "completed": 0, "skipped": 0})
            report["steps"][step.value] = {
                **counts,
                "completion_rate": counts["completed"] / max(counts["started"], 1),
            }
        return report

    def export_report(self, path: Path) -> Path:
        """Export funnel report as JSON."""
        report = self.funnel_report()
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return path
