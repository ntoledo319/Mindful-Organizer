"""
Notification system for gentle, mental-health-aware reminders.

Supports scheduling (one-time and recurring), priority levels,
condition-aware delivery styles, snooze/dismiss, and SQLite persistence.
"""

import contextlib
import json
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from core.paths import get_data_dir

logger = logging.getLogger(__name__)

DATA_DIR = get_data_dir(create=False)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NotificationType(Enum):
    """Categories of notifications the app can send."""
    MOOD_CHECKIN = "mood_checkin"
    TASK_DEADLINE = "task_deadline"
    MEDICATION_REMINDER = "medication_reminder"
    MEDITATION_BREAK = "meditation_break"
    BREATHING_EXERCISE = "breathing_exercise"
    ENERGY_CHECK = "energy_check"
    STREAK_REMINDER = "streak_reminder"
    CUSTOM = "custom"


class Priority(Enum):
    """Notification urgency levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    @property
    def weight(self) -> int:
        return {"low": 1, "medium": 2, "high": 3, "urgent": 4}[self.value]


class DeliveryStyle(Enum):
    """How a notification should be presented to the user."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    NON_INTRUSIVE = "non_intrusive"
    SILENT = "silent"


class NotificationStatus(Enum):
    """Lifecycle status of a notification."""
    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    SNOOZED = "snoozed"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RecurringPattern:
    """Cron-like recurring schedule.

    Fields mirror simplified cron: minute, hour, day_of_week (0=Mon..6=Sun),
    day_of_month, interval_minutes.  ``None`` means "any / not set".
    """
    minute: int | None = None
    hour: int | None = None
    day_of_week: int | None = None          # 0=Monday .. 6=Sunday
    day_of_month: int | None = None
    interval_minutes: int | None = None     # simple repeat every N minutes

    def to_json(self) -> str:
        return json.dumps({
            "minute": self.minute,
            "hour": self.hour,
            "day_of_week": self.day_of_week,
            "day_of_month": self.day_of_month,
            "interval_minutes": self.interval_minutes,
        })

    @classmethod
    def from_json(cls, raw: str) -> "RecurringPattern":
        data = json.loads(raw)
        return cls(**data)

    def next_occurrence(self, after: datetime) -> datetime:
        """Calculate the next occurrence of this pattern after *after*.

        For ``interval_minutes`` patterns, returns ``after + interval``.
        For field-based patterns, walks forward minute-by-minute (capped at
        7 days) until all specified fields match.
        """
        if self.interval_minutes is not None:
            return after + timedelta(minutes=self.interval_minutes)

        candidate = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
        limit = after + timedelta(days=7)
        while candidate < limit:
            if self.minute is not None and candidate.minute != self.minute:
                candidate += timedelta(minutes=1)
                continue
            if self.hour is not None and candidate.hour != self.hour:
                candidate += timedelta(hours=1)
                candidate = candidate.replace(minute=self.minute or 0)
                continue
            if self.day_of_week is not None and candidate.weekday() != self.day_of_week:
                candidate += timedelta(days=1)
                candidate = candidate.replace(
                    hour=self.hour or 0, minute=self.minute or 0
                )
                continue
            if self.day_of_month is not None and candidate.day != self.day_of_month:
                candidate += timedelta(days=1)
                candidate = candidate.replace(
                    hour=self.hour or 0, minute=self.minute or 0
                )
                continue
            return candidate
        return after + timedelta(days=1)


@dataclass
class Notification:
    """In-memory representation of a notification."""
    id: int | None = None
    type: NotificationType = NotificationType.CUSTOM
    title: str = ""
    message: str = ""
    priority: Priority = Priority.MEDIUM
    scheduled_at: datetime | None = None
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    dismissed_at: datetime | None = None
    snoozed_until: datetime | None = None
    recurring: RecurringPattern | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None

    @property
    def status(self) -> NotificationStatus:
        now = datetime.now()
        if self.dismissed_at is not None:
            return NotificationStatus.DISMISSED
        if self.snoozed_until is not None and self.snoozed_until > now:
            return NotificationStatus.SNOOZED
        if self.read_at is not None:
            return NotificationStatus.READ
        if self.delivered_at is not None:
            return NotificationStatus.DELIVERED
        return NotificationStatus.PENDING

    def is_due(self) -> bool:
        if self.status in (
            NotificationStatus.DISMISSED,
            NotificationStatus.READ,
        ):
            return False
        now = datetime.now()
        if self.snoozed_until and self.snoozed_until > now:
            return False
        return self.scheduled_at is not None and self.scheduled_at <= now


# ---------------------------------------------------------------------------
# Condition-aware delivery logic
# ---------------------------------------------------------------------------

# Maps mental-health condition labels to preferred delivery styles per type.
_CONDITION_DELIVERY: dict[str, dict[NotificationType, DeliveryStyle]] = {
    "ANXIETY": {
        NotificationType.MOOD_CHECKIN: DeliveryStyle.SCHEDULED,
        NotificationType.TASK_DEADLINE: DeliveryStyle.SCHEDULED,
        NotificationType.MEDICATION_REMINDER: DeliveryStyle.SCHEDULED,
        NotificationType.MEDITATION_BREAK: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.BREATHING_EXERCISE: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.ENERGY_CHECK: DeliveryStyle.SCHEDULED,
        NotificationType.STREAK_REMINDER: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.CUSTOM: DeliveryStyle.SCHEDULED,
    },
    "ADHD": {
        NotificationType.MOOD_CHECKIN: DeliveryStyle.IMMEDIATE,
        NotificationType.TASK_DEADLINE: DeliveryStyle.IMMEDIATE,
        NotificationType.MEDICATION_REMINDER: DeliveryStyle.IMMEDIATE,
        NotificationType.MEDITATION_BREAK: DeliveryStyle.IMMEDIATE,
        NotificationType.BREATHING_EXERCISE: DeliveryStyle.IMMEDIATE,
        NotificationType.ENERGY_CHECK: DeliveryStyle.IMMEDIATE,
        NotificationType.STREAK_REMINDER: DeliveryStyle.IMMEDIATE,
        NotificationType.CUSTOM: DeliveryStyle.IMMEDIATE,
    },
    "PTSD": {
        NotificationType.MOOD_CHECKIN: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.TASK_DEADLINE: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.MEDICATION_REMINDER: DeliveryStyle.SCHEDULED,
        NotificationType.MEDITATION_BREAK: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.BREATHING_EXERCISE: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.ENERGY_CHECK: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.STREAK_REMINDER: DeliveryStyle.SILENT,
        NotificationType.CUSTOM: DeliveryStyle.NON_INTRUSIVE,
    },
    "DEPRESSION": {
        NotificationType.MOOD_CHECKIN: DeliveryStyle.SCHEDULED,
        NotificationType.TASK_DEADLINE: DeliveryStyle.SCHEDULED,
        NotificationType.MEDICATION_REMINDER: DeliveryStyle.IMMEDIATE,
        NotificationType.MEDITATION_BREAK: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.BREATHING_EXERCISE: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.ENERGY_CHECK: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.STREAK_REMINDER: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.CUSTOM: DeliveryStyle.SCHEDULED,
    },
    "OCD": {
        NotificationType.MOOD_CHECKIN: DeliveryStyle.SCHEDULED,
        NotificationType.TASK_DEADLINE: DeliveryStyle.SCHEDULED,
        NotificationType.MEDICATION_REMINDER: DeliveryStyle.SCHEDULED,
        NotificationType.MEDITATION_BREAK: DeliveryStyle.SCHEDULED,
        NotificationType.BREATHING_EXERCISE: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.ENERGY_CHECK: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.STREAK_REMINDER: DeliveryStyle.NON_INTRUSIVE,
        NotificationType.CUSTOM: DeliveryStyle.SCHEDULED,
    },
}

_DEFAULT_DELIVERY: dict[NotificationType, DeliveryStyle] = dict.fromkeys(NotificationType, DeliveryStyle.SCHEDULED)


def delivery_style_for(
    condition: str | None,
    notification_type: NotificationType,
) -> DeliveryStyle:
    """Return the recommended delivery style for a condition + type pair."""
    if condition and condition.upper() in _CONDITION_DELIVERY:
        return _CONDITION_DELIVERY[condition.upper()].get(
            notification_type, DeliveryStyle.SCHEDULED
        )
    return _DEFAULT_DELIVERY.get(notification_type, DeliveryStyle.SCHEDULED)


# ---------------------------------------------------------------------------
# NotificationManager
# ---------------------------------------------------------------------------

class NotificationManager:
    """Manages the full lifecycle of user notifications.

    Persists to the ``notifications`` table via the supplied database manager
    (or any object matching the ``DatabaseManager`` interface).

    Usage::

        from core.database import DatabaseManager, TableName
        db = DatabaseManager()
        db.initialize()
        nm = NotificationManager(db)

        # Schedule a notification
        nm.schedule(
            type=NotificationType.MOOD_CHECKIN,
            title="Time for a check-in",
            message="How are you feeling right now?",
            scheduled_at=datetime.now() + timedelta(hours=1),
        )

        # Process pending notifications
        due = nm.get_due_notifications()
        for n in due:
            nm.mark_delivered(n.id)
    """

    def __init__(self, db: Any, condition: str | None = None) -> None:
        """
        Args:
            db: A ``DatabaseManager`` instance (from ``src.core.database``).
            condition: Primary mental-health condition label (e.g. "ADHD").
                       Used to choose delivery style.
        """
        self._db = db
        self._condition = condition
        self._listeners: list[Callable[[Notification], None]] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Listener registration (observer pattern)
    # ------------------------------------------------------------------

    def add_listener(self, callback: Callable[[Notification], None]) -> None:
        """Register a callback invoked when a notification is delivered."""
        with self._lock:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[Notification], None]) -> None:
        with self._lock:
            self._listeners = [cb for cb in self._listeners if cb is not callback]

    def _notify_listeners(self, notification: Notification) -> None:
        with self._lock:
            listeners = list(self._listeners)
        for cb in listeners:
            try:
                cb(notification)
            except Exception:
                logger.exception("Notification listener raised an error")

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _row_to_notification(self, row: dict[str, Any]) -> Notification:
        """Convert a database row dict to a ``Notification`` object."""
        recurring = None
        if row.get("recurring"):
            with contextlib.suppress(json.JSONDecodeError, TypeError):
                recurring = RecurringPattern.from_json(row["recurring"])

        metadata: dict[str, Any] = {}
        if row.get("metadata"):
            with contextlib.suppress(json.JSONDecodeError, TypeError):
                metadata = json.loads(row["metadata"])

        def _parse_dt(val: Any) -> datetime | None:
            if val is None:
                return None
            if isinstance(val, datetime):
                return val
            try:
                return datetime.fromisoformat(str(val))
            except (ValueError, TypeError):
                return None

        return Notification(
            id=row.get("id"),
            type=NotificationType(row["type"]) if row.get("type") else NotificationType.CUSTOM,
            title=row.get("title", ""),
            message=row.get("message", ""),
            priority=Priority(row["priority"]) if row.get("priority") else Priority.MEDIUM,
            scheduled_at=_parse_dt(row.get("scheduled_at")),
            delivered_at=_parse_dt(row.get("delivered_at")),
            read_at=_parse_dt(row.get("read_at")),
            dismissed_at=_parse_dt(row.get("dismissed_at")),
            snoozed_until=_parse_dt(row.get("snoozed_until")),
            recurring=recurring,
            metadata=metadata,
            created_at=_parse_dt(row.get("created_at")),
        )

    def _table(self) -> Any:
        """Return the TableName enum value for notifications."""
        # Avoid a hard import; works with any object that has a .value == 'notifications'
        from core.database import TableName
        return TableName.NOTIFICATIONS

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def schedule(
        self,
        type: NotificationType = NotificationType.CUSTOM,
        title: str = "",
        message: str = "",
        priority: Priority = Priority.MEDIUM,
        scheduled_at: datetime | None = None,
        recurring: RecurringPattern | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Notification:
        """Create and persist a new notification.

        Returns the created ``Notification`` with its database id set.
        """
        if scheduled_at is None:
            scheduled_at = datetime.now()

        row_id = self._db.insert(
            self._table(),
            type=type.value,
            title=title,
            message=message,
            priority=priority.value,
            scheduled_at=scheduled_at.isoformat(),
            recurring=recurring.to_json() if recurring else None,
            metadata=json.dumps(metadata) if metadata else None,
        )

        notification = Notification(
            id=row_id,
            type=type,
            title=title,
            message=message,
            priority=priority,
            scheduled_at=scheduled_at,
            recurring=recurring,
            metadata=metadata or {},
        )
        logger.info("Scheduled notification #%d: %s", row_id, title)
        return notification

    def get_by_id(self, notification_id: int) -> Notification | None:
        """Retrieve a single notification by its id."""
        row = self._db.get_by_id(self._table(), notification_id)
        if row is None:
            return None
        return self._row_to_notification(row)

    def get_due_notifications(self) -> list[Notification]:
        """Return all pending notifications whose scheduled time has passed."""
        now = datetime.now().isoformat()
        result = self._db.query(
            self._table(),
            where=(
                "scheduled_at <= ? AND delivered_at IS NULL AND dismissed_at IS NULL "
                "AND (snoozed_until IS NULL OR snoozed_until <= ?)"
            ),
            params=(now, now),
            order_by="scheduled_at ASC",
        )
        return [self._row_to_notification(r) for r in result.rows]

    def get_pending(self) -> list[Notification]:
        """Return all notifications that have not yet been delivered or dismissed."""
        result = self._db.query(
            self._table(),
            where="delivered_at IS NULL AND dismissed_at IS NULL",
            order_by="scheduled_at ASC",
        )
        return [self._row_to_notification(r) for r in result.rows]

    def get_history(
        self,
        limit: int = 50,
        offset: int = 0,
        type_filter: NotificationType | None = None,
    ) -> list[Notification]:
        """Return delivered / dismissed notifications, most recent first."""
        where = "delivered_at IS NOT NULL OR dismissed_at IS NOT NULL"
        params: list[Any] = []
        if type_filter is not None:
            where += " AND type = ?"
            params.append(type_filter.value)
        result = self._db.query(
            self._table(),
            where=where,
            params=params,
            order_by="COALESCE(delivered_at, dismissed_at) DESC",
            limit=limit,
            offset=offset,
        )
        return [self._row_to_notification(r) for r in result.rows]

    # ------------------------------------------------------------------
    # Delivery
    # ------------------------------------------------------------------

    def mark_delivered(self, notification_id: int) -> Notification | None:
        """Mark a notification as delivered and fire listeners."""
        now = datetime.now().isoformat()
        self._db.update(self._table(), notification_id, delivered_at=now)
        notification = self.get_by_id(notification_id)
        if notification:
            self._notify_listeners(notification)
            self._handle_recurring(notification)
        return notification

    def mark_read(self, notification_id: int) -> None:
        """Mark a notification as read by the user."""
        now = datetime.now().isoformat()
        self._db.update(self._table(), notification_id, read_at=now)

    # ------------------------------------------------------------------
    # Snooze & dismiss
    # ------------------------------------------------------------------

    def snooze(
        self,
        notification_id: int,
        duration: timedelta = timedelta(minutes=15),
    ) -> None:
        """Snooze a notification for *duration*."""
        snooze_until = (datetime.now() + duration).isoformat()
        self._db.update(
            self._table(), notification_id,
            snoozed_until=snooze_until,
            delivered_at=None,  # reset so it appears due again
        )
        logger.info("Notification #%d snoozed until %s", notification_id, snooze_until)

    def dismiss(self, notification_id: int) -> None:
        """Permanently dismiss a notification."""
        now = datetime.now().isoformat()
        self._db.update(self._table(), notification_id, dismissed_at=now)
        logger.info("Notification #%d dismissed", notification_id)

    # ------------------------------------------------------------------
    # Recurring
    # ------------------------------------------------------------------

    def _handle_recurring(self, notification: Notification) -> None:
        """If the notification has a recurring pattern, schedule the next one."""
        if notification.recurring is None:
            return
        next_at = notification.recurring.next_occurrence(datetime.now())
        self.schedule(
            type=notification.type,
            title=notification.title,
            message=notification.message,
            priority=notification.priority,
            scheduled_at=next_at,
            recurring=notification.recurring,
            metadata=notification.metadata,
        )
        logger.info("Recurring notification re-scheduled for %s", next_at.isoformat())

    # ------------------------------------------------------------------
    # Condition-aware delivery
    # ------------------------------------------------------------------

    def get_delivery_style(self, notification_type: NotificationType) -> DeliveryStyle:
        """Return the delivery style appropriate for the user's condition."""
        return delivery_style_for(self._condition, notification_type)

    def set_condition(self, condition: str | None) -> None:
        """Update the user's primary condition for delivery-style decisions."""
        self._condition = condition

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def dismiss_all_pending(self) -> int:
        """Dismiss every pending notification. Returns count dismissed."""
        now = datetime.now().isoformat()
        result = self._db.execute(
            "UPDATE notifications SET dismissed_at = ? "
            "WHERE delivered_at IS NULL AND dismissed_at IS NULL",
            (now,),
        )
        return int(result.row_count)

    def delete_old(self, older_than_days: int = 90) -> int:
        """Delete notifications older than the given number of days."""
        cutoff = (datetime.now() - timedelta(days=older_than_days)).isoformat()
        result = self._db.execute(
            "DELETE FROM notifications WHERE created_at < ? AND dismissed_at IS NOT NULL",
            (cutoff,),
        )
        return int(result.row_count)

    # ------------------------------------------------------------------
    # Convenience schedulers
    # ------------------------------------------------------------------

    def schedule_mood_checkin(
        self,
        at: datetime | None = None,
        recurring: RecurringPattern | None = None,
    ) -> Notification:
        """Schedule a gentle mood check-in."""
        return self.schedule(
            type=NotificationType.MOOD_CHECKIN,
            title="Mood Check-in",
            message="Take a moment to notice how you're feeling right now.",
            priority=Priority.LOW,
            scheduled_at=at or datetime.now() + timedelta(hours=2),
            recurring=recurring,
        )

    def schedule_medication_reminder(
        self,
        medication_name: str,
        at: datetime,
        recurring: RecurringPattern | None = None,
    ) -> Notification:
        """Schedule a medication reminder."""
        return self.schedule(
            type=NotificationType.MEDICATION_REMINDER,
            title=f"Medication: {medication_name}",
            message=f"Time to take {medication_name}.",
            priority=Priority.HIGH,
            scheduled_at=at,
            recurring=recurring,
            metadata={"medication_name": medication_name},
        )

    def schedule_breathing_exercise(
        self,
        at: datetime | None = None,
        technique: str = "box_breathing",
    ) -> Notification:
        """Schedule a breathing exercise reminder."""
        return self.schedule(
            type=NotificationType.BREATHING_EXERCISE,
            title="Breathing Break",
            message="A short breathing exercise can help reset your focus.",
            priority=Priority.LOW,
            scheduled_at=at or datetime.now() + timedelta(hours=1),
            metadata={"technique": technique},
        )

    def schedule_task_deadline(
        self,
        task_title: str,
        deadline: datetime,
        advance_minutes: int = 30,
    ) -> Notification:
        """Schedule a task deadline reminder (default: 30 min before)."""
        remind_at = deadline - timedelta(minutes=advance_minutes)
        return self.schedule(
            type=NotificationType.TASK_DEADLINE,
            title=f"Upcoming: {task_title}",
            message=f"'{task_title}' is due in {advance_minutes} minutes.",
            priority=Priority.MEDIUM,
            scheduled_at=remind_at,
            metadata={"task_title": task_title, "deadline": deadline.isoformat()},
        )


    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        """Return summary statistics about notifications."""
        total = self._db.count(self._table())
        pending = self._db.count(
            self._table(),
            where="delivered_at IS NULL AND dismissed_at IS NULL",
        )
        delivered = self._db.count(
            self._table(),
            where="delivered_at IS NOT NULL",
        )
        dismissed = self._db.count(
            self._table(),
            where="dismissed_at IS NOT NULL",
        )
        snoozed = self._db.count(
            self._table(),
            where="snoozed_until IS NOT NULL AND snoozed_until > datetime('now')",
        )
        return {
            "total": total,
            "pending": pending,
            "delivered": delivered,
            "dismissed": dismissed,
            "snoozed": snoozed,
        }
