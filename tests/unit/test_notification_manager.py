"""
Tests for NotificationManager (src/core/notification_manager.py).

Covers creating notifications, recurring schedules, condition-aware
delivery, snooze, and dismiss operations.
"""

from datetime import datetime, timedelta

import pytest

try:
    from src.core.notification_manager import (
        NotificationManager,
        NotificationType,
        Priority,
        DeliveryStyle,
        RecurringPattern,
        Notification,
        NotificationStatus,
        delivery_style_for,
    )
    from src.core.database import DatabaseManager, TableName
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="notification_manager module not available")


@pytest.fixture
def db(tmp_data_dir):
    database = DatabaseManager(db_path=tmp_data_dir / "test.db")
    database.initialize()
    yield database
    database.close()


@pytest.fixture
def nm(db):
    return NotificationManager(db)


# ---------------------------------------------------------------------------
# Create notification
# ---------------------------------------------------------------------------

class TestCreateNotification:

    def test_schedule_notification(self, nm):
        n = nm.schedule(
            type=NotificationType.CUSTOM,
            title="Test",
            message="Hello",
            scheduled_at=datetime.now() + timedelta(hours=1),
        )
        assert n.id is not None
        assert n.title == "Test"

    def test_schedule_with_priority(self, nm):
        n = nm.schedule(
            type=NotificationType.TASK_DEADLINE,
            title="Deadline",
            message="Due soon",
            priority=Priority.URGENT,
            scheduled_at=datetime.now(),
        )
        assert n.priority == Priority.URGENT

    def test_schedule_with_metadata(self, nm):
        n = nm.schedule(
            title="Med reminder",
            message="Take pills",
            metadata={"medication": "Sertraline"},
            scheduled_at=datetime.now(),
        )
        assert n.metadata["medication"] == "Sertraline"

    def test_get_by_id(self, nm):
        n = nm.schedule(title="Find me", message="Test", scheduled_at=datetime.now())
        found = nm.get_by_id(n.id)
        assert found is not None
        assert found.title == "Find me"

    def test_get_by_id_nonexistent(self, nm):
        assert nm.get_by_id(999999) is None

    def test_convenience_mood_checkin(self, nm):
        n = nm.schedule_mood_checkin()
        assert n.type == NotificationType.MOOD_CHECKIN
        assert n.id is not None

    def test_convenience_medication_reminder(self, nm):
        n = nm.schedule_medication_reminder("Sertraline", at=datetime.now())
        assert n.type == NotificationType.MEDICATION_REMINDER
        assert "Sertraline" in n.title

    def test_convenience_breathing_exercise(self, nm):
        n = nm.schedule_breathing_exercise()
        assert n.type == NotificationType.BREATHING_EXERCISE

    def test_convenience_task_deadline(self, nm):
        n = nm.schedule_task_deadline("Finish report", datetime.now() + timedelta(hours=2))
        assert n.type == NotificationType.TASK_DEADLINE

    def test_convenience_energy_check(self, nm):
        n = nm.schedule_energy_check()
        assert n.type == NotificationType.ENERGY_CHECK


# ---------------------------------------------------------------------------
# Recurring notifications
# ---------------------------------------------------------------------------

class TestScheduleRecurring:

    def test_schedule_recurring_interval(self, nm):
        pattern = RecurringPattern(interval_minutes=60)
        n = nm.schedule(
            title="Hourly check",
            message="Check in",
            scheduled_at=datetime.now(),
            recurring=pattern,
        )
        assert n.recurring is not None
        assert n.recurring.interval_minutes == 60

    def test_recurring_next_occurrence(self):
        pattern = RecurringPattern(interval_minutes=30)
        now = datetime(2026, 4, 6, 10, 0)
        next_at = pattern.next_occurrence(now)

        assert next_at == datetime(2026, 4, 6, 10, 30)

    def test_recurring_by_hour_minute(self):
        pattern = RecurringPattern(hour=9, minute=0)
        now = datetime(2026, 4, 6, 8, 30)
        next_at = pattern.next_occurrence(now)

        assert next_at.hour == 9
        assert next_at.minute == 0

    def test_recurring_by_day_of_week(self):
        pattern = RecurringPattern(day_of_week=0, hour=10, minute=0)  # Monday
        now = datetime(2026, 4, 6, 12, 0)  # Monday afternoon
        next_at = pattern.next_occurrence(now)

        assert next_at.weekday() == 0  # Monday
        assert next_at > now

    def test_recurring_pattern_serialization(self):
        pattern = RecurringPattern(interval_minutes=45)
        json_str = pattern.to_json()
        restored = RecurringPattern.from_json(json_str)
        assert restored.interval_minutes == 45

    def test_handle_recurring_creates_next(self, nm):
        pattern = RecurringPattern(interval_minutes=60)
        n = nm.schedule(
            title="Recurring",
            message="Again",
            scheduled_at=datetime.now() - timedelta(minutes=5),
            recurring=pattern,
        )
        nm.mark_delivered(n.id)

        # After delivery, a new notification should be created
        pending = nm.get_pending()
        assert any(p.title == "Recurring" for p in pending)


# ---------------------------------------------------------------------------
# Condition-aware delivery
# ---------------------------------------------------------------------------

class TestConditionAwareDelivery:

    def test_adhd_delivery_immediate(self):
        style = delivery_style_for("ADHD", NotificationType.TASK_DEADLINE)
        assert style == DeliveryStyle.IMMEDIATE

    def test_anxiety_delivery_scheduled(self):
        style = delivery_style_for("ANXIETY", NotificationType.TASK_DEADLINE)
        assert style == DeliveryStyle.SCHEDULED

    def test_ptsd_delivery_non_intrusive(self):
        style = delivery_style_for("PTSD", NotificationType.MOOD_CHECKIN)
        assert style == DeliveryStyle.NON_INTRUSIVE

    def test_depression_medication_immediate(self):
        style = delivery_style_for("DEPRESSION", NotificationType.MEDICATION_REMINDER)
        assert style == DeliveryStyle.IMMEDIATE

    def test_no_condition_defaults(self):
        style = delivery_style_for(None, NotificationType.CUSTOM)
        assert style == DeliveryStyle.SCHEDULED

    def test_set_condition(self, nm):
        nm.set_condition("ADHD")
        style = nm.get_delivery_style(NotificationType.TASK_DEADLINE)
        assert style == DeliveryStyle.IMMEDIATE


# ---------------------------------------------------------------------------
# Snooze
# ---------------------------------------------------------------------------

class TestSnooze:

    def test_snooze_notification(self, nm):
        n = nm.schedule(
            title="Snooze me",
            message="Test",
            scheduled_at=datetime.now() - timedelta(minutes=5),
        )
        nm.mark_delivered(n.id)
        nm.snooze(n.id, duration=timedelta(minutes=15))

        snoozed = nm.get_by_id(n.id)
        assert snoozed.snoozed_until is not None
        assert snoozed.status == NotificationStatus.SNOOZED


# ---------------------------------------------------------------------------
# Dismiss
# ---------------------------------------------------------------------------

class TestDismiss:

    def test_dismiss_notification(self, nm):
        n = nm.schedule(title="Dismiss me", message="Test", scheduled_at=datetime.now())
        nm.dismiss(n.id)

        dismissed = nm.get_by_id(n.id)
        assert dismissed.status == NotificationStatus.DISMISSED

    def test_dismiss_all_pending(self, nm):
        for i in range(3):
            nm.schedule(title=f"N{i}", message="Test", scheduled_at=datetime.now())

        count = nm.dismiss_all_pending()
        assert count == 3

    def test_mark_read(self, nm):
        n = nm.schedule(title="Read me", message="Test", scheduled_at=datetime.now())
        nm.mark_delivered(n.id)
        nm.mark_read(n.id)

        read = nm.get_by_id(n.id)
        assert read.status == NotificationStatus.READ


# ---------------------------------------------------------------------------
# Stats and listeners
# ---------------------------------------------------------------------------

class TestStatsAndListeners:

    def test_stats(self, nm):
        nm.schedule(title="A", message="X", scheduled_at=datetime.now())
        nm.schedule(title="B", message="Y", scheduled_at=datetime.now())

        stats = nm.stats()
        assert stats["total"] >= 2
        assert stats["pending"] >= 2

    def test_listener_called_on_delivery(self, nm):
        delivered = []
        nm.add_listener(lambda n: delivered.append(n))

        n = nm.schedule(title="Listen", message="X", scheduled_at=datetime.now())
        nm.mark_delivered(n.id)

        assert len(delivered) == 1
        assert delivered[0].title == "Listen"

    def test_remove_listener(self, nm):
        delivered = []
        cb = lambda n: delivered.append(n)
        nm.add_listener(cb)
        nm.remove_listener(cb)

        n = nm.schedule(title="No listen", message="X", scheduled_at=datetime.now())
        nm.mark_delivered(n.id)
        assert len(delivered) == 0


# ---------------------------------------------------------------------------
# Notification status logic
# ---------------------------------------------------------------------------

class TestNotificationStatus:

    def test_pending_status(self):
        n = Notification(scheduled_at=datetime.now() + timedelta(hours=1))
        assert n.status == NotificationStatus.PENDING

    def test_is_due(self):
        n = Notification(scheduled_at=datetime.now() - timedelta(minutes=1))
        assert n.is_due() is True

    def test_not_due_future(self):
        n = Notification(scheduled_at=datetime.now() + timedelta(hours=1))
        assert n.is_due() is False

    def test_dismissed_not_due(self):
        n = Notification(
            scheduled_at=datetime.now() - timedelta(minutes=1),
            dismissed_at=datetime.now(),
        )
        assert n.is_due() is False
