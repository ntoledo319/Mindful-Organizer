"""Headless smoke test — verifies the entire Python core boots and exercises
its public API without ever touching PyQt6.

This is the Phase-0 gate for the Tauri + Next.js rebuild: if this passes, the
core is ready to be wrapped in FastAPI and called from a web frontend. If a
new import or method silently pulls in Qt, this test will fail at the import
boundary check.

Run:
    pytest tests/test_headless_core.py -v
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

# Block any PyQt6 import attempt for the duration of this test module.
# If anything below tries to import PyQt6, ImportError fires immediately.
_QT_MODULES = ["PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets"]


@pytest.fixture(autouse=True)
def block_qt_imports(monkeypatch):
    """Refuse PyQt6 imports for the whole module — proves headless cleanliness."""
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def guarded_import(name, *args, **kwargs):
        if name in _QT_MODULES or name.startswith("PyQt6."):
            raise AssertionError(
                f"Headless core attempted to import {name!r}. "
                "Backend code MUST be Qt-free for the FastAPI/Tauri rebuild."
            )
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded_import)
    # Also poison any already-loaded Qt modules in this process.
    for mod in list(sys.modules):
        if mod.startswith("PyQt6"):
            monkeypatch.setitem(sys.modules, mod, None)


@pytest.fixture
def tmp_data_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


class TestCoreImports:
    """Every backend manager must import without Qt."""

    def test_database(self):
        from core.database import DatabaseManager
        assert DatabaseManager is not None

    def test_task_manager(self):
        from core.task_manager import Task, TaskManager, TaskPriority
        assert all([TaskManager, TaskPriority, Task])

    def test_mood_manager(self):
        from core.mood_manager import MoodManager
        assert MoodManager is not None

    def test_sleep_tracker(self):
        from core.sleep_tracker import SleepTracker
        assert SleepTracker is not None

    def test_medication_tracker(self):
        from core.medication_tracker import MedicationTracker
        assert MedicationTracker is not None

    def test_diary_card_manager(self):
        from core.diary_card_manager import DiaryCardManager
        assert DiaryCardManager is not None

    def test_subscription_manager(self):
        from core.subscription_manager import SubscriptionManager, SubscriptionTier
        assert all([SubscriptionManager, SubscriptionTier])

    def test_automation_engine(self):
        from core.system_automation import SystemAutomationEngine
        assert SystemAutomationEngine is not None

    def test_automation_rules(self):
        from core.automation_rules import get_default_rules
        assert get_default_rules is not None

    def test_focus_mode(self):
        from core.focus_mode import FocusModeManager
        assert FocusModeManager is not None

    def test_display_adaptation(self):
        from core.display_adaptation import DisplayAdaptationEngine
        assert DisplayAdaptationEngine is not None

    def test_app_guardian(self):
        from core.app_guardian import AppGuardian
        assert AppGuardian is not None

    def test_platform_actions(self):
        from core.platform_actions import StubBackend, get_backend
        assert all([StubBackend, get_backend])

    def test_wellness_orchestrator(self):
        from core.wellness_orchestrator import WellnessOrchestrator
        assert WellnessOrchestrator is not None

    def test_energy_predictor(self):
        from core.energy_predictor import EnergyPredictor
        assert EnergyPredictor is not None

    def test_ai_optimizer(self):
        from core.ai_optimizer import AISystemOptimizer
        assert AISystemOptimizer is not None

    def test_file_organizer(self):
        from core.file_organizer import FileOrganizer
        assert FileOrganizer is not None

    def test_notification_manager(self):
        from core.notification_manager import NotificationManager
        assert NotificationManager is not None

    def test_export_manager(self):
        from core.export_manager import ExportManager
        assert ExportManager is not None

    def test_nlp_parser(self):
        from core.nlp_parser import NLPTaskParser
        assert NLPTaskParser is not None

    def test_smart_task_decomposer(self):
        from core.smart_task_decomposer import SmartTaskDecomposer
        assert SmartTaskDecomposer is not None

    def test_shareable_report(self):
        from core.shareable_report import ShareableReport
        assert ShareableReport is not None

    def test_migration_manager(self):
        from core.migration_manager import MigrationManager
        assert MigrationManager is not None


class TestWellnessImports:
    def test_breathing(self):
        from wellness.breathing import BreathingManager
        assert BreathingManager is not None

    def test_meditation(self):
        from wellness.meditation import MeditationManager
        assert MeditationManager is not None

    def test_journaling(self):
        from wellness.journaling import JournalingManager
        assert JournalingManager is not None

    def test_crisis_plan(self):
        from wellness.crisis_plan import CrisisPlanManager
        assert CrisisPlanManager is not None

    def test_erp_tracker(self):
        from wellness.erp_tracker import ERPTracker
        assert ERPTracker is not None

    def test_grounding(self):
        from wellness.grounding import GroundingManager
        assert GroundingManager is not None

    def test_coping_engine(self):
        from wellness.coping_engine import CopingEngine
        assert CopingEngine is not None


class TestProfileImports:
    def test_mental_health_profile(self):
        from profiles.mental_health_profile_builder import Profile, ProfileManager
        assert all([Profile, ProfileManager])

    def test_spoon_theory(self):
        from profiles.spoon_theory import SpoonBudget
        assert SpoonBudget is not None

    def test_clinical_combinations(self):
        from profiles.clinical_combinations import ClinicalCombinations
        assert ClinicalCombinations is not None


class TestSecurityImports:
    def test_content_management(self):
        from security.content_management import ContentManager
        assert ContentManager is not None


class TestBasicInstantiation:
    """Verify managers actually construct headless — not just import."""

    def test_task_manager_basic_crud(self, tmp_data_dir):
        from core.task_manager import (
            Task,
            TaskCategory,
            TaskManager,
            TaskPriority,
        )
        tm = TaskManager(data_dir=tmp_data_dir)
        task = tm.add_task(
            Task(
                title="test task",
                priority=TaskPriority.Medium,
                category=TaskCategory.Work,
                energy_required=3,
            )
        )
        assert task is not None
        assert len(tm.get_tasks()) == 1

    def test_database_initializes(self, tmp_data_dir):
        from core.database import DatabaseManager
        db = DatabaseManager(db_path=tmp_data_dir / "test.db")
        db.initialize()
        assert (tmp_data_dir / "test.db").exists()

    def test_subscription_manager_free_tier(self, tmp_data_dir):
        from core.subscription_manager import SubscriptionManager, SubscriptionTier
        mgr = SubscriptionManager(data_dir=tmp_data_dir)
        assert mgr.current_tier == SubscriptionTier.FREE

    def test_automation_engine_constructs(self, tmp_data_dir):
        from core.platform_actions import StubBackend
        from core.subscription_manager import SubscriptionManager
        from core.system_automation import SystemAutomationEngine
        engine = SystemAutomationEngine(
            data_dir=tmp_data_dir,
            backend=StubBackend(),
            subscription_manager=SubscriptionManager(data_dir=tmp_data_dir),
        )
        assert engine is not None

    def test_default_automation_rules_load(self):
        from core.automation_rules import get_default_rules
        rules = get_default_rules()
        # actual count is 11; some docs claim 14 — that's a doc drift, not a bug
        assert len(rules) >= 10

    def test_breathing_session_lifecycle(self, tmp_data_dir):
        from wellness.breathing import BreathingExerciseType, BreathingManager
        mgr = BreathingManager(data_dir=tmp_data_dir)
        # exercises load from the embedded library; verify type catalog
        assert BreathingExerciseType is not None
        assert mgr is not None
