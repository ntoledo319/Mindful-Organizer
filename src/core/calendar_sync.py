"""
Calendar integration for Mindful Organizer.

Exports tasks as ICS (iCal) events and can read external calendars
to block focus time during predicted peak energy hours.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CalendarEvent:
    """A single calendar event."""
    uid: str
    summary: str
    description: str
    start: datetime
    end: datetime
    location: str = ""
    url: str = ""
    alarm_minutes_before: int = 15


# ---------------------------------------------------------------------------
# ICS generation
# ---------------------------------------------------------------------------

class CalendarSync:
    """Sync tasks with external calendars via ICS format."""

    def __init__(self, timezone: str = "UTC") -> None:
        self.timezone = timezone

    def tasks_to_ics(
        self,
        tasks: list[dict[str, Any]],
        include_energy: bool = True,
    ) -> str:
        """Convert tasks to an ICS calendar string.

        Parameters
        ----------
        tasks : list of dict
            Each dict should have at least ``title``, ``due_date`` (ISO),
            and optionally ``energy_required``, ``notes``.
        include_energy : bool
            Append energy level to the event description.
        """
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Mindful Organizer//Task Export//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]

        for task in tasks:
            event = self._task_to_event(task, include_energy)
            lines.extend(self._event_to_ics_lines(event))

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines)

    def _task_to_event(
        self,
        task: dict[str, Any],
        include_energy: bool,
    ) -> CalendarEvent:
        title = task.get("title", "Untitled Task")
        due_str = task.get("due_date", "")

        # Default to today 9am if no due date
        if due_str:
            try:
                start = datetime.fromisoformat(due_str)
                if start.time() == datetime.min.time():
                    start = start.replace(hour=9, minute=0)
            except ValueError:
                start = datetime.combine(date.today(), datetime.min.time().replace(hour=9))
        else:
            start = datetime.combine(date.today(), datetime.min.time().replace(hour=9))

        end = start + timedelta(hours=1)

        description_parts = [task.get("notes", "")]
        if include_energy:
            energy = task.get("energy_required", 5)
            description_parts.append(f"Energy required: {energy}/10")
            if energy <= 3:
                description_parts.append("Low energy — good for low-spoon days.")
            elif energy >= 8:
                description_parts.append("High energy — tackle during peak hours.")

        description = "\n".join(filter(None, description_parts))

        return CalendarEvent(
            uid=str(uuid.uuid4()),
            summary=title,
            description=description,
            start=start,
            end=end,
            alarm_minutes_before=30,
        )

    def _event_to_ics_lines(self, event: CalendarEvent) -> list[str]:
        lines = [
            "BEGIN:VEVENT",
            f"UID:{event.uid}",
            f"SUMMARY:{self._ics_escape(event.summary)}",
            f"DESCRIPTION:{self._ics_escape(event.description)}",
            f"DTSTART;TZID={self.timezone}:{event.start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND;TZID={self.timezone}:{event.end.strftime('%Y%m%dT%H%M%S')}",
        ]
        if event.location:
            lines.append(f"LOCATION:{self._ics_escape(event.location)}")
        if event.url:
            lines.append(f"URL:{event.url}")

        # Alarm
        lines.extend([
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:Reminder: {self._ics_escape(event.summary)}",
            f"TRIGGER:-PT{event.alarm_minutes_before}M",
            "END:VALARM",
        ])

        lines.append("END:VEVENT")
        return lines

    @staticmethod
    def _ics_escape(value: str) -> str:
        """Escape special characters for ICS format."""
        return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    def export_tasks_to_file(
        self,
        tasks: list[dict[str, Any]],
        output_path: Path,
        include_energy: bool = True,
    ) -> Path:
        """Export tasks to an .ics file."""
        ics_data = self.tasks_to_ics(tasks, include_energy)
        output_path.write_text(ics_data, encoding="utf-8")
        return output_path

    def suggest_focus_blocks(
        self,
        tasks: list[dict[str, Any]],
        peak_hours: list[int],
    ) -> list[dict[str, Any]]:
        """Suggest which tasks to schedule during peak energy hours.

        Returns a list of task dicts with a ``suggested_start`` key added.
        """
        if not peak_hours:
            return tasks

        high_energy_tasks = [
            t for t in tasks
            if not t.get("completed") and t.get("energy_required", 5) >= 7
        ]

        suggestions: list[dict[str, Any]] = []
        for i, task in enumerate(high_energy_tasks[: len(peak_hours)]):
            hour = peak_hours[i % len(peak_hours)]
            suggested = dict(task)
            suggested["suggested_start"] = datetime.combine(
                date.today(), datetime.min.time().replace(hour=hour)
            ).isoformat()
            suggestions.append(suggested)

        return suggestions
