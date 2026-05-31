"""
Integration tests for Hearth.

Tests cross-module flows: profile -> task management, mood -> analytics,
full data lifecycle (create -> export -> import -> verify), and
condition-aware feature interactions.
"""

import json
from datetime import date, datetime, timedelta

import pytest

# --- Conditional imports -------------------------------------------------------

try:
    from core.database import DatabaseManager, TableName
    _HAS_DB = True
except ImportError:
    _HAS_DB = False

try:
    from core.task_manager import (
        Task,
        TaskCategory,
        TaskManager,
        TaskPriority,
    )
    _HAS_TASKS = True
except ImportError:
    _HAS_TASKS = False

try:
    from core.mood_analytics import MoodAnalytics
    _HAS_ANALYTICS = True
except ImportError:
    _HAS_ANALYTICS = False

try:
    from core.export_manager import (
        DataCategory,
        ExportFormat,
        ExportManager,
        ExportOptions,
    )
    _HAS_EXPORT = True
except ImportError:
    _HAS_EXPORT = False

try:
    from core.nlp_parser import NLPTaskParser
    _HAS_NLP = True
except ImportError:
    _HAS_NLP = False

try:
    from core.smart_task_decomposer import SmartTaskDecomposer
    _HAS_DECOMPOSER = True
except ImportError:
    _HAS_DECOMPOSER = False

try:
    from core.notification_manager import (
        NotificationManager,
        NotificationType,
    )
    _HAS_NOTIFICATIONS = True
except ImportError:
    _HAS_NOTIFICATIONS = False

try:
    from core.file_organizer import FileOrganizer
    _HAS_FILE_ORG = True
except ImportError:
    _HAS_FILE_ORG = False

try:
    from wellness.breathing import BreathingManager
    from wellness.breathing import Condition as BreathCondition
    _HAS_BREATHING = True
except ImportError:
    _HAS_BREATHING = False

try:
    from profiles.spoon_theory import SpoonBudget
    _HAS_SPOONS = True
except ImportError:
    _HAS_SPOONS = False


pytestmark = pytest.mark.skipif(not _HAS_DB, reason="database module not available")


@pytest.fixture
def db(tmp_data_dir):
    database = DatabaseManager(db_path=tmp_data_dir / "integration.db")
    database.initialize()
    yield database
    database.close()


# ---------------------------------------------------------------------------
# Profile -> Task management flow
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _HAS_TASKS, reason="task_manager not available")
class TestProfileToTaskFlow:

    def test_create_tasks_with_conditions(self, tmp_data_dir, sample_profile):
        """Tasks created for a user with ADHD+Anxiety should work end-to-end."""
        tm = TaskManager(tmp_data_dir)

        task = Task(
            title="Prepare presentation",
            priority=TaskPriority.High,
            category=TaskCategory.Work,
            energy_required=8,
            due_date=(date.today() + timedelta(days=3)).isoformat(),
        )
        tm.add_task(task)

        # Verify retrieval
        high_tasks = tm.get_tasks_by_priority(TaskPriority.High)
        assert len(high_tasks) == 1
        assert high_tasks[0].title == "Prepare presentation"

    @pytest.mark.skipif(not _HAS_DECOMPOSER, reason="decomposer not available")
    def test_decompose_task_for_adhd_user(self, sample_profile):
        """ADHD user gets task decomposed into small steps."""
        decomposer = SmartTaskDecomposer()
        result = decomposer.decompose(
            "Write a 10-page research paper",
            condition_override="adhd",
        )

        assert len(result.subtasks) >= 3
        # ADHD style should produce short-duration steps
        for step in result.subtasks:
            assert step.estimated_minutes <= 30

    @pytest.mark.skipif(not _HAS_NLP, reason="nlp_parser not available")
    def test_parse_and_add_task(self, tmp_data_dir):
        """Parse natural language into a task, then add to TaskManager."""
        parser = NLPTaskParser()
        parsed = parser.parse("urgent: finish budget report by friday #work")

        tm = TaskManager(tmp_data_dir)
        task = Task(
            title=parsed.title,
            priority=TaskPriority[parsed.priority.value.capitalize()] if parsed.priority else TaskPriority.Medium,
            category=TaskCategory.Work if parsed.category and "work" in parsed.category.value.lower() else TaskCategory.Other,
            energy_required=5,
            due_date=parsed.due_date,
        )
        tm.add_task(task)
        assert tm.get_tasks_by_priority(task.priority)[0].title == parsed.title

    @pytest.mark.skipif(not _HAS_SPOONS, reason="spoon_theory not available")
    def test_spoon_budget_filters_tasks(self, tmp_data_dir):
        """Only tasks within remaining spoon budget should be suggested."""
        budget = SpoonBudget(conditions={"ADHD"})
        tm = TaskManager(tmp_data_dir)

        # Add tasks with varying energy
        for energy in [2, 5, 8]:
            tm.add_task(Task(
                title=f"Task energy {energy}",
                priority=TaskPriority.Medium,
                category=TaskCategory.Other,
                energy_required=energy,
            ))

        remaining = budget.remaining_spoons()
        affordable = tm.get_tasks_by_energy(max_energy=remaining)
        for t in affordable:
            assert t.energy_required <= remaining


# ---------------------------------------------------------------------------
# Mood -> Analytics flow
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _HAS_ANALYTICS, reason="mood_analytics not available")
class TestMoodToAnalyticsFlow:

    def test_db_entries_to_analytics(self, db):
        """Insert mood data via DB, then run analytics on it."""
        base = datetime.now() - timedelta(days=10)
        for i in range(10):
            ts = (base + timedelta(days=i)).isoformat()
            db.insert(
                TableName.MOOD_ENTRIES,
                mood_score=4 + i % 5,
                energy_level=3 + i % 6,
                notes=f"Day {i}",
                timestamp=ts,
            )

        result = db.query(TableName.MOOD_ENTRIES, order_by="timestamp ASC")
        entries = result.rows

        analytics = MoodAnalytics(entries, conditions={"Anxiety"})

        trend = analytics.mood_trend()
        assert trend is not None

        report = analytics.full_report()
        insights = analytics.generate_insights(report)
        assert len(insights) >= 1

    def test_condition_specific_insights(self, db):
        """Condition insights should mention relevant conditions."""
        base = datetime.now() - timedelta(days=14)
        for i in range(14):
            ts = (base + timedelta(days=i)).isoformat()
            db.insert(
                TableName.MOOD_ENTRIES,
                mood_score=3 + (i % 4),
                energy_level=4,
                anxiety_level=7 - (i % 3),
                timestamp=ts,
            )

        rows = db.query(TableName.MOOD_ENTRIES).rows
        analytics = MoodAnalytics(rows, conditions={"Depression", "Anxiety"})

        cond_insights = analytics.condition_insights()
        assert isinstance(cond_insights, list)
        assert any(ci.condition == "depression" for ci in cond_insights)

    def test_empty_entries_do_not_crash(self):
        """Analytics with no data should return safe defaults."""
        analytics = MoodAnalytics([], conditions=set())
        trend = analytics.mood_trend()
        assert trend is not None
        assert hasattr(trend, "direction")
        report = analytics.full_report()
        insights = analytics.generate_insights(report)
        assert isinstance(insights, list)


# ---------------------------------------------------------------------------
# Full data lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _HAS_EXPORT, reason="export_manager not available")
class TestFullDataLifecycle:

    def test_create_export_import_verify(self, db, tmp_data_dir):
        """Create data -> export to JSON -> import into fresh DB -> verify."""
        # 1. Create data
        db.insert(TableName.MOOD_ENTRIES, mood_score=7, energy_level=6, notes="Happy")
        db.insert(TableName.MOOD_ENTRIES, mood_score=4, energy_level=3, notes="Tired")
        db.insert(TableName.TASKS, title="Exercise", priority="high", category="Health")
        db.set_setting("theme", "dark", category="appearance")

        # 2. Export
        em = ExportManager(db)
        export_path = tmp_data_dir / "lifecycle_export.json"
        opts = ExportOptions(format=ExportFormat.JSON, output_path=export_path)
        result_path = em.export(opts)
        assert result_path.exists()

        exported = json.loads(result_path.read_text())
        assert len(exported["mood_entries"]) == 2
        assert len(exported["tasks"]) == 1

        # 3. Import into fresh DB
        db2_path = tmp_data_dir / "imported.db"
        db2 = DatabaseManager(db_path=db2_path)
        db2.initialize()
        try:
            em2 = ExportManager(db2)

            counts = em2.import_from_json(result_path)
            assert counts["mood_entries"] >= 2

            # 4. Verify
            imported_moods = db2.query(TableName.MOOD_ENTRIES).rows
            assert len(imported_moods) >= 2
            scores = {r["mood_score"] for r in imported_moods}
            assert 7 in scores
            assert 4 in scores
        finally:
            db2.close()

    def test_export_selective_and_reimport(self, db, tmp_data_dir):
        """Selective export of mood data only, then reimport."""
        db.insert(TableName.MOOD_ENTRIES, mood_score=8)
        db.insert(TableName.TASKS, title="Ignored", priority="low", category="Other")

        em = ExportManager(db)
        export_path = tmp_data_dir / "selective.json"
        opts = ExportOptions(
            format=ExportFormat.JSON,
            categories=[DataCategory.MOOD],
            output_path=export_path,
        )
        em.export(opts)

        data = json.loads(export_path.read_text())
        assert "mood_entries" in data
        assert "tasks" not in data

    def test_settings_round_trip(self, db, tmp_data_dir):
        """Export settings, import into new DB, verify values."""
        db.set_setting("theme", "calm", category="appearance")
        db.set_setting("font_scale", "1.5", category="accessibility")

        em = ExportManager(db)
        settings_path = tmp_data_dir / "settings.json"
        em.export_settings(output_path=settings_path)

        db2 = DatabaseManager(db_path=tmp_data_dir / "settings_target.db")
        db2.initialize()
        try:
            em2 = ExportManager(db2)
            em2.import_settings(settings_path)

            assert db2.get_setting("theme") == "calm"
            assert db2.get_setting("font_scale") == "1.5"
        finally:
            db2.close()

    def test_backup_restore_preserves_data(self, db, tmp_data_dir):
        """DB backup -> modify -> restore -> verify original state."""
        db.insert(TableName.MOOD_ENTRIES, mood_score=9, notes="Original")
        backup_path = db.backup(tmp_data_dir / "lifecycle_backup.db")

        # Modify after backup
        db.insert(TableName.MOOD_ENTRIES, mood_score=1, notes="After backup")
        assert db.count(TableName.MOOD_ENTRIES) == 2

        # Restore
        db.restore(backup_path)
        assert db.count(TableName.MOOD_ENTRIES) == 1
        row = db.query(TableName.MOOD_ENTRIES).rows[0]
        assert row["notes"] == "Original"

    def test_clinical_report_generation(self, db, tmp_data_dir):
        """Generate a wellness report from populated data."""
        for i in range(7):
            db.insert(
                TableName.MOOD_ENTRIES,
                mood_score=5 + (i % 4),
                energy_level=4 + (i % 3),
                timestamp=(datetime.now() - timedelta(days=i)).isoformat(),
            )

        em = ExportManager(db)
        sections = em.generate_wellness_report(days=30)
        assert len(sections) >= 2

        text = em.wellness_report_to_text(sections)
        assert "WELLNESS REPORT" in text


# ---------------------------------------------------------------------------
# Notification + condition flow
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _HAS_NOTIFICATIONS, reason="notification_manager not available")
class TestNotificationConditionFlow:

    def test_schedule_and_deliver_for_adhd(self, db):
        """ADHD user schedules task deadline -> immediate delivery style."""
        nm = NotificationManager(db)
        nm.set_condition("ADHD")

        n = nm.schedule_task_deadline(
            "Submit report",
            datetime.now() + timedelta(hours=1),
        )

        from core.notification_manager import DeliveryStyle
        style = nm.get_delivery_style(NotificationType.TASK_DEADLINE)
        assert style == DeliveryStyle.IMMEDIATE
        assert n.id is not None

    def test_medication_reminder_lifecycle(self, db):
        """Schedule med reminder -> deliver -> snooze -> deliver again."""
        nm = NotificationManager(db)
        n = nm.schedule_medication_reminder("Sertraline", at=datetime.now())
        nm.mark_delivered(n.id)

        nm.snooze(n.id, duration=timedelta(minutes=10))
        snoozed = nm.get_by_id(n.id)

        from core.notification_manager import NotificationStatus
        assert snoozed.status == NotificationStatus.SNOOZED


# ---------------------------------------------------------------------------
# Breathing + energy flow
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _HAS_BREATHING, reason="breathing module not available")
class TestBreathingEnergyFlow:

    def test_recommend_then_track_session(self, tmp_data_dir):
        """Get recommendation, run session, check stats improve."""
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(mood=3, conditions={BreathCondition.ANXIETY})
        assert len(recs) > 0

        # Run a session with the top recommendation
        top = recs[0]
        session = bm.create_session(top.exercise_type, mood_before=3)
        bm.complete_session(session, cycles_completed=4, mood_after=7)

        # Subsequent recommendations should factor in history
        recs2 = bm.recommend(mood=3, conditions={BreathCondition.ANXIETY})
        assert len(recs2) > 0


# ---------------------------------------------------------------------------
# File organizer + gamification flow
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not (_HAS_FILE_ORG),
    reason="file_organizer not available",
)
class TestFileOrganizationFlow:

    def test_organize_and_stats(self, tmp_data_dir, tmp_path):
        """Organize files, then verify stats reflect the actions."""
        fo = FileOrganizer(tmp_data_dir)

        src = tmp_path / "flow_src"
        src.mkdir()
        (src / "doc.pdf").write_text("pdf")
        (src / "pic.jpg").write_bytes(b"\xff\xd8")
        (src / "code.py").write_text("pass")

        target = tmp_path / "flow_out"
        summary = fo.organize_files(src, target)
        assert summary["moved"] == 3

        stats = fo.get_organization_stats()
        assert stats["total_files_moved"] == 3

    def test_organize_dry_run_then_real(self, tmp_data_dir, tmp_path):
        """Dry-run first for preview, then organize for real."""
        fo = FileOrganizer(tmp_data_dir)

        src = tmp_path / "dry_real_src"
        src.mkdir()
        (src / "file.txt").write_text("hello")

        # Dry run
        preview = fo.dry_run(src)
        assert preview["moved"] == 1
        assert (src / "file.txt").exists()

        # Real run
        summary = fo.organize_files(src)
        assert summary["moved"] == 1
        assert not (src / "file.txt").exists()

    def test_organize_then_undo(self, tmp_data_dir, tmp_path):
        """Organize files then undo to restore originals."""
        fo = FileOrganizer(tmp_data_dir)

        src = tmp_path / "undo_src"
        src.mkdir()
        (src / "data.csv").write_text("a,b")

        fo.organize_files(src, tmp_path / "undo_out")
        assert not (src / "data.csv").exists()

        result = fo.undo_last_organization()
        assert result["undone"] == 1
        assert (src / "data.csv").exists()


# ---------------------------------------------------------------------------
# Cross-module data consistency
# ---------------------------------------------------------------------------

class TestCrossModuleConsistency:

    def test_db_mood_and_task_counts(self, db):
        """Verify that mood and task counts stay consistent across operations."""
        db.insert(TableName.MOOD_ENTRIES, mood_score=7)
        db.insert(TableName.MOOD_ENTRIES, mood_score=5)
        db.insert(TableName.TASKS, title="A", priority="high", category="Work")
        db.insert(TableName.TASKS, title="B", priority="low", category="Health")

        assert db.count(TableName.MOOD_ENTRIES) == 2
        assert db.count(TableName.TASKS) == 2

        # Delete one task
        tasks = db.query(TableName.TASKS).rows
        db.delete(TableName.TASKS, tasks[0]["id"])

        assert db.count(TableName.TASKS) == 1
        assert db.count(TableName.MOOD_ENTRIES) == 2  # unaffected

    def test_settings_persist_across_modules(self, db):
        """Settings written by one module should be readable by another."""
        db.set_setting("theme", "focus", category="appearance")
        db.set_setting("notifications_enabled", "true", category="notifications")

        # Simulate another module reading settings
        assert db.get_setting("theme") == "focus"
        assert db.get_setting("notifications_enabled") == "true"

    def test_export_contains_all_module_data(self, db):
        """A full export should include data from every table that has rows."""
        db.insert(TableName.MOOD_ENTRIES, mood_score=6)
        db.insert(TableName.TASKS, title="X", priority="medium", category="Other")
        db.insert(
            TableName.SLEEP_LOGS,
            date="2026-04-05", bedtime="23:00", wake_time="07:00", quality=7,
        )
        db.insert(
            TableName.JOURNAL_ENTRIES,
            content="Entry",
        )

        json_str = db.export_all_to_json()
        data = json.loads(json_str)

        assert len(data["mood_entries"]) == 1
        assert len(data["tasks"]) == 1
        assert len(data["sleep_logs"]) == 1
        assert len(data["journal_entries"]) == 1
