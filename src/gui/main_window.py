"""
Refactored main window for Hearth.
Orchestrates all widget modules and manages application state.
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import cast

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app_metadata import APP_VERSION
from core.ai_optimizer import AISystemOptimizer
from core.constants import Condition
from core.file_organizer import FileOrganizer
from core.system_automation import SystemAutomationEngine
from core.system_optimizer import SystemOptimizer
from core.task_manager import TaskManager
from gui.state_bus import StateBus, set_state_bus
from gui.system_tray import SystemTrayController
from gui.themes import ThemeManager
from profiles.mental_health_profile_builder import ProfileManager
from utils.accessibility import AccessibilityManager
from utils.global_hotkeys import GlobalHotkeyManager
from utils.keyboard_shortcuts import ShortcutManager

logger = logging.getLogger(__name__)


class StatusMessageSink:
    """Stores transient status text without adding permanent window chrome."""

    def __init__(self) -> None:
        self.message = ""

    def showMessage(self, message: str, timeout: int = 0) -> None:  # noqa: N802
        self.message = message


class AdaptiveMainWindow(QMainWindow):
    """Main window with adaptive features based on user's mental health profile."""

    # Signals for cross-widget communication
    theme_changed = pyqtSignal(str)
    profile_changed = pyqtSignal(object)
    energy_updated = pyqtSignal(int)
    mood_updated = pyqtSignal(str)

    SECONDARY_TABS = {"sleep", "medication", "automation", "file_organizer"}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hearth")
        self.setMinimumSize(1200, 800)
        self.setGeometry(100, 100, 1400, 900)

        # Initialize data directory (platform-aware)
        self.data_dir = self._get_data_dir()
        self.data_dir.mkdir(exist_ok=True, parents=True)

        # Initialize theme manager
        self.theme_manager = ThemeManager()

        # One shared database for the whole app. Every DB-backed manager is
        # injected with this instance so tasks, moods, sleep, medication, and
        # the wellness orchestrator all read and write the SAME SQLite file.
        # (Previously some managers fell back to their own default path, which
        # silently split a user's data across multiple databases.)
        from core.database import DatabaseManager
        self.db = DatabaseManager(self.data_dir / "mindful_organizer.db")
        self.db.initialize()

        # Initialize core managers
        self.profile_manager = ProfileManager(self.data_dir)
        self.task_manager = TaskManager(self.data_dir, db_manager=self.db)
        self.file_organizer = FileOrganizer(self.data_dir, profile=self.profile_manager.current_profile)
        self.system_optimizer = SystemOptimizer(self.data_dir)
        self.ai_optimizer = AISystemOptimizer(self.data_dir)

        # Initialize wellness orchestrator (cross-module intelligence)
        self._wellness_orchestrator = None

        # Initialize reactive state bus
        self.state_bus = StateBus()
        set_state_bus(self.state_bus)

        # Initialize accessibility
        self.accessibility_manager = AccessibilityManager()
        self.accessibility_manager.auto_detect()
        app = QApplication.instance()
        if app:
            self.accessibility_manager.apply(app)

        # Initialize shortcut manager
        self.shortcut_manager = ShortcutManager()
        self._setup_shortcut_callbacks()

        # Initialize optional managers (lazy loaded)
        self._sleep_tracker = None
        self._medication_tracker = None
        self._mood_analytics = None
        self._energy_predictor = None
        self._nlp_parser = None
        self._task_decomposer = None
        self._notification_manager = None
        self._export_manager = None
        self._spoon_manager = None
        self._breathing_manager = None
        self._grounding_manager = None
        self._journaling_manager = None
        self._crisis_plan_manager = None
        self._erp_tracker = None
        self._meditation_manager = None
        self._coping_engine = None
        self._gamification_manager = None
        self._keyboard_shortcuts = None
        self._subscription_manager = None
        self._auto_updater = None
        self._onboarding_analytics = None
        self._diary_card_manager = None
        self._mood_manager = None

        # System Automation Engine (the "pro" feature)
        self._system_automation: SystemAutomationEngine | None = None
        self._system_tray: SystemTrayController | None = None
        self._global_hotkeys: GlobalHotkeyManager | None = None

        # Widget references
        self._widgets = {}
        self._nav_buttons: dict[str, QPushButton] = {}

        # Load settings
        self._load_settings()

        # Show onboarding or initialize
        if not self.profile_manager.current_profile:
            self._show_onboarding()
        else:
            self._initialize_ui()

    def _get_data_dir(self) -> Path:
        """Get platform-appropriate data directory."""
        try:
            from windows.platform_utils import get_data_dir
            return cast(Path, get_data_dir())
        except ImportError:
            if sys.platform == "win32":
                base = Path.home() / "AppData" / "Roaming"
            elif sys.platform == "darwin":
                base = Path.home() / "Library" / "Application Support"
            else:
                base = Path.home()
            return base / ".mindful_organizer"

    def _load_settings(self):
        """Load application settings."""
        settings_file = self.data_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    settings = json.load(f)
                saved_theme = settings.get("theme", "ember")
                legacy_theme_map = {
                    "light": "linen",
                    "dark": "ember",
                    "calm": "linen",
                    "warm": "linen",
                    "gentle": "linen",
                    "focus": "ember",
                    "structured": "linen",
                    "high_contrast": "quiet",
                }
                self.theme_manager.set_theme(legacy_theme_map.get(saved_theme, saved_theme))
                self.theme_manager.font_scale = settings.get("font_scale", 1.0)
                self.theme_manager.color_blind_mode = settings.get("color_blind_mode")
                self.theme_manager.reduced_motion = settings.get("reduced_motion", False)
                self.theme_manager.dyslexia_font = settings.get("dyslexia_font", False)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load settings: {e}")

    def save_settings(self):
        """Save application settings."""
        settings = {
            "theme": self.theme_manager.current_theme_name,
            "font_scale": self.theme_manager.font_scale,
            "color_blind_mode": self.theme_manager.color_blind_mode,
            "reduced_motion": self.theme_manager.reduced_motion,
            "dyslexia_font": self.theme_manager.dyslexia_font,
        }
        settings_file = self.data_dir / "settings.json"
        try:
            with open(settings_file, "w") as f:
                json.dump(settings, f, indent=2)
        except (OSError, TypeError) as e:
            logger.error(f"Failed to save settings: {e}")

    # === Lazy-loaded manager properties ===

    @property
    def sleep_tracker(self):
        if self._sleep_tracker is None:
            try:
                from core.sleep_tracker import SleepTracker
                self._sleep_tracker = SleepTracker(self.db)
            except ImportError:
                logger.warning("SleepTracker not available")
        return self._sleep_tracker

    @property
    def medication_tracker(self):
        if self._medication_tracker is None:
            try:
                from core.medication_tracker import MedicationTracker
                self._medication_tracker = MedicationTracker(self.db)
            except ImportError:
                logger.warning("MedicationTracker not available")
        return self._medication_tracker

    @property
    def mood_analytics(self):
        # Built fresh from the mood manager's current entries each access — a
        # cached analytics object would go stale as new moods are logged, and
        # MoodAnalytics() with no entries raised a TypeError the callers swallowed.
        try:
            from core.mood_analytics import MoodAnalytics
            mgr = self.mood_manager
            entries = list(mgr.entries) if mgr else []
            return MoodAnalytics(entries)
        except Exception as exc:  # noqa: BLE001
            logger.warning("MoodAnalytics not available: %s", exc)
            return None

    @property
    def energy_predictor(self):
        if self._energy_predictor is None:
            try:
                from core.energy_predictor import EnergyPredictor
                self._energy_predictor = EnergyPredictor(self.data_dir)
            except ImportError:
                logger.warning("EnergyPredictor not available")
        return self._energy_predictor

    @property
    def diary_card_manager(self):
        if self._diary_card_manager is None:
            try:
                from core.diary_card_manager import DiaryCardManager
                self._diary_card_manager = DiaryCardManager(self.db)
            except Exception as exc:
                logger.warning("DiaryCardManager not available: %s", exc)
        return self._diary_card_manager

    @property
    def mood_manager(self):
        if self._mood_manager is None:
            try:
                from core.mood_manager import MoodManager
                self._mood_manager = MoodManager(self.db)
            except Exception as exc:
                logger.warning("MoodManager not available: %s", exc)
        return self._mood_manager

    @property
    def nlp_parser(self):
        if self._nlp_parser is None:
            try:
                from core.nlp_parser import NLPTaskParser
                self._nlp_parser = NLPTaskParser()
            except ImportError:
                logger.warning("NLPTaskParser not available")
        return self._nlp_parser

    @property
    def task_decomposer(self):
        if self._task_decomposer is None:
            try:
                from core.smart_task_decomposer import SmartTaskDecomposer
                self._task_decomposer = SmartTaskDecomposer()
            except ImportError:
                logger.warning("SmartTaskDecomposer not available")
        return self._task_decomposer

    @property
    def notification_manager(self):
        if self._notification_manager is None:
            try:
                from core.notification_manager import NotificationManager
                self._notification_manager = NotificationManager(self.data_dir)
            except ImportError:
                logger.warning("NotificationManager not available")
        return self._notification_manager

    @property
    def export_manager(self):
        if self._export_manager is None:
            try:
                from core.export_manager import ExportManager
                # Must receive the shared DatabaseManager — passing a Path made
                # every export/import raise AttributeError and silently fall back
                # to exporting only loose JSON files (zero SQLite health data).
                self._export_manager = ExportManager(self.db)
            except ImportError:
                logger.warning("ExportManager not available")
        return self._export_manager

    @property
    def spoon_manager(self):
        if self._spoon_manager is None:
            try:
                from profiles.spoon_theory import SpoonManager
                conditions = set()
                if self.profile_manager.current_profile:
                    conditions = self.profile_manager.current_profile.conditions
                self._spoon_manager = SpoonManager(self.data_dir, conditions)
            except ImportError:
                logger.warning("SpoonManager not available")
        return self._spoon_manager

    @property
    def breathing_manager(self):
        if self._breathing_manager is None:
            try:
                from wellness.breathing import BreathingManager
                self._breathing_manager = BreathingManager(self.data_dir)
            except ImportError:
                logger.warning("BreathingManager not available")
        return self._breathing_manager

    @property
    def grounding_manager(self):
        if self._grounding_manager is None:
            try:
                from wellness.grounding import GroundingManager
                self._grounding_manager = GroundingManager(self.data_dir)
            except ImportError:
                logger.warning("GroundingManager not available")
        return self._grounding_manager

    @property
    def journaling_manager(self):
        if self._journaling_manager is None:
            try:
                from wellness.journaling import JournalingManager
                self._journaling_manager = JournalingManager(self.data_dir)
            except ImportError:
                logger.warning("JournalingManager not available")
        return self._journaling_manager

    @property
    def crisis_plan_manager(self):
        if self._crisis_plan_manager is None:
            try:
                from wellness.crisis_plan import CrisisPlanManager
                self._crisis_plan_manager = CrisisPlanManager(self.data_dir)
            except ImportError:
                logger.warning("CrisisPlanManager not available")
        return self._crisis_plan_manager

    @property
    def erp_tracker(self):
        if self._erp_tracker is None:
            try:
                from wellness.erp_tracker import ERPTracker
                self._erp_tracker = ERPTracker(self.data_dir)
            except ImportError:
                logger.warning("ERPTracker not available")
        return self._erp_tracker

    @property
    def meditation_manager(self):
        if self._meditation_manager is None:
            try:
                from wellness.meditation import MeditationManager
                self._meditation_manager = MeditationManager(self.data_dir)
            except ImportError:
                logger.warning("MeditationManager not available")
        return self._meditation_manager

    @property
    def coping_engine(self):
        if self._coping_engine is None:
            try:
                from wellness.coping_engine import CopingEngine
                self._coping_engine = CopingEngine(self.data_dir)
            except ImportError:
                logger.warning("CopingEngine not available")
        return self._coping_engine

    @property
    def wellness_orchestrator(self):
        if self._wellness_orchestrator is None:
            try:
                from core.wellness_orchestrator import WellnessOrchestrator
                self._wellness_orchestrator = WellnessOrchestrator(db=self.db)
            except ImportError:
                logger.warning("WellnessOrchestrator not available")
        return self._wellness_orchestrator

    @property
    def gamification_manager(self):
        if self._gamification_manager is None:
            try:
                from file_organization.adhd_gamification import ADHDGameManager
                self._gamification_manager = ADHDGameManager(self.data_dir)
            except ImportError:
                logger.warning("ADHDGameManager not available")
        return self._gamification_manager

    @property
    def subscription_manager(self):
        if self._subscription_manager is None:
            try:
                from core.subscription_manager import SubscriptionManager
                self._subscription_manager = SubscriptionManager(self.data_dir)
            except ImportError:
                logger.warning("SubscriptionManager not available")
        return self._subscription_manager

    @property
    def auto_updater(self):
        if self._auto_updater is None:
            try:
                import importlib.metadata

                from core.auto_updater import AutoUpdater
                try:
                    version = importlib.metadata.version("mindful-organizer")
                except importlib.metadata.PackageNotFoundError:
                    version = APP_VERSION
                self._auto_updater = AutoUpdater(version)
            except ImportError:
                logger.warning("AutoUpdater not available")
        return self._auto_updater

    @property
    def onboarding_analytics(self):
        if self._onboarding_analytics is None:
            try:
                from core.onboarding_analytics import OnboardingAnalytics
                self._onboarding_analytics = OnboardingAnalytics(self.data_dir)
            except ImportError:
                logger.warning("OnboardingAnalytics not available")
        return self._onboarding_analytics

    @property
    def system_automation(self):
        if self._system_automation is None:
            try:
                self._system_automation = SystemAutomationEngine(
                    data_dir=self.data_dir,
                    wellness_orchestrator=self.wellness_orchestrator,
                    ai_optimizer=self.ai_optimizer,
                )
                profile = self.profile_manager.current_profile
                if profile and profile.conditions:
                    self._system_automation.set_user_conditions(profile.conditions)
            except Exception as exc:
                logger.warning("SystemAutomationEngine not available: %s", exc)
        return self._system_automation

    # === UI Setup ===

    def _show_onboarding(self):
        """Show the onboarding wizard for new users."""
        try:
            from gui.widgets.onboarding import OnboardingWizard
            wizard = OnboardingWizard(self.profile_manager, self.data_dir, parent=self)
            if wizard.exec():
                self._initialize_ui()
            else:
                # User cancelled - create minimal profile
                self._create_default_profile()
                self._initialize_ui()
        except ImportError:
            logger.warning("Onboarding wizard not available, using basic setup")
            self._show_basic_profile_setup()

    def _create_default_profile(self):
        """Create a default profile for users who skip onboarding."""
        self.profile_manager.create_profile(
            name="User",
            conditions=set(),
        )

    def _show_basic_profile_setup(self):
        """Fallback profile setup if onboarding widget is unavailable."""
        from PyQt6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QLineEdit
        dialog = QDialog(self)
        dialog.setWindowTitle("Welcome to Hearth")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)

        welcome = QLabel("Let's set up your profile")
        welcome.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(welcome)

        name_label = QLabel("Your Name:")
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter your name...")
        layout.addWidget(name_label)
        layout.addWidget(name_input)

        conditions_label = QLabel("Select any conditions (optional):")
        layout.addWidget(conditions_label)

        condition_checks = {}
        for condition in Condition:
            check = QCheckBox(condition.value)
            layout.addWidget(check)
            condition_checks[condition] = check

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            conditions = {c for c, check in condition_checks.items() if check.isChecked()}
            self.profile_manager.create_profile(
                name=name_input.text() or "User",
                conditions=conditions,
            )
        else:
            self._create_default_profile()

        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize the full UI with all tabs."""
        # Set up central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header bar
        self._setup_header(main_layout)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addLayout(content_layout)

        self._setup_navigation(content_layout)

        # The tab widget remains the compatibility content stack. Its visual
        # tabs are hidden because navigation is owned by the side rail.
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)
        self.tabs.tabBar().hide()
        self.tabs.currentChanged.connect(self._sync_navigation)
        content_layout.addWidget(self.tabs, stretch=1)

        # Add core tabs
        self._add_tabs()
        self._nav_layout.addStretch()
        self._sync_navigation(self.tabs.currentIndex())

        # Status bar
        self._setup_status_bar()

        # Apply theme
        self._apply_theme()

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        # Initialize system automation, tray, hotkeys
        self._setup_system_automation()

        # Start background timers
        self._setup_timers()

        self.show()

    def _setup_navigation(self, parent_layout: QHBoxLayout) -> None:
        """Create the persistent navigation rail."""
        self._nav_frame = QFrame()
        self._nav_frame.setObjectName("sideNav")
        self._nav_frame.setFixedWidth(176)
        self._nav_layout = QVBoxLayout(self._nav_frame)
        self._nav_layout.setContentsMargins(14, 18, 14, 18)
        self._nav_layout.setSpacing(4)

        self._nav_header = QLabel("Spaces")
        self._nav_header.setObjectName("sideNavHeader")
        self._nav_layout.addWidget(self._nav_header)

        parent_layout.addWidget(self._nav_frame)

    def _setup_header(self, parent_layout: QVBoxLayout):
        """Setup the header bar with profile and theme controls."""
        header = QFrame()
        header.setObjectName("appHeader")
        header.setMaximumHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 10, 24, 10)
        header_layout.setSpacing(12)

        # App title
        title = QLabel("Hearth")
        title.setFont(QFont(self.font().family(), 17, QFont.Weight.DemiBold))
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Profile info
        profile = self.profile_manager.current_profile
        profile_name = profile.name if profile else "User"
        profile_label = QLabel(profile_name)
        profile_label.setFont(QFont(self.font().family(), 11))
        header_layout.addWidget(profile_label)

        # Theme selector
        theme_label = QLabel("Theme")
        theme_label.setFont(QFont(self.font().family(), 11))
        header_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(140)
        for name, display_name, _ in self.theme_manager.get_theme_names():
            self.theme_combo.addItem(display_name, name)
        current_idx = self.theme_combo.findData(self.theme_manager.current_theme_name)
        if current_idx >= 0:
            self.theme_combo.setCurrentIndex(current_idx)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        header_layout.addWidget(self.theme_combo)

        parent_layout.addWidget(header)

    def _add_tabs(self):
        """Add all tabs based on user profile."""
        profile = self.profile_manager.current_profile
        conditions = profile.conditions if profile else set()

        # Core tabs (always present)
        self._add_tab("dashboard", "Today")
        self._add_tab("task_manager", "Tasks")
        self._add_tab("journaling", "Journal")
        self._add_tab("mood_tracker", "Mood")
        self._add_tab("diary_card", "Diary")
        self._add_tab("breathing", "Breathe")
        self._add_tab("meditation", "Meditate")

        # Condition-specific tabs
        if Condition.OCD in conditions:
            self._add_tab("erp", "ERP")
        if Condition.PANIC in conditions or Condition.ANXIETY in conditions or Condition.PTSD in conditions:
            self._add_tab("panic_tracker", "Panic Log")

        # Tracking tabs
        self._add_tab("sleep", "Sleep")
        self._add_tab("medication", "Medication")

        # System Automation (available to all, gated internally)
        self._add_tab("automation", "Focus")

        # Secondary but still available in the tabbed PyQt shell.
        self._add_tab("file_organizer", "Library")
        self._add_tab("crisis", "Crisis")
        self._add_tab("settings", "Profile")

        # Check for updates after UI is ready
        QTimer.singleShot(2000, self._check_for_updates)

    def _add_tab(self, widget_name: str, display_name: str):
        """Add a tab, creating the widget with fallback to placeholder."""
        widget = self._create_widget(widget_name)
        if widget:
            self._widgets[widget_name] = widget
            self.tabs.addTab(widget, display_name)
            self._add_nav_button(widget_name, display_name)

    def _add_nav_button(self, widget_name: str, display_name: str) -> None:
        """Add a side navigation button for a tab."""
        if not hasattr(self, "_nav_layout"):
            return
        if widget_name in self.SECONDARY_TABS and not getattr(self, "_secondary_nav_added", False):
            self._add_nav_divider()
            self._secondary_nav_added = True
        if widget_name == "crisis" and not getattr(self, "_support_nav_added", False):
            self._add_nav_divider()
            self._support_nav_added = True

        button = QPushButton(display_name)
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setProperty("class", "navItem")
        if widget_name == "crisis":
            button.setProperty("tone", "danger")
        button.clicked.connect(lambda _checked=False, name=widget_name: self._switch_to_tab(name))
        self._nav_buttons[widget_name] = button
        self._nav_layout.addWidget(button)

    def _add_nav_divider(self) -> None:
        divider = QFrame()
        divider.setObjectName("sideNavDivider")
        divider.setFixedHeight(1)
        self._nav_layout.addWidget(divider)

    def _create_widget(self, name: str) -> QWidget | None:
        """Create a widget by name with graceful fallback."""
        theme = self.theme_manager.get_colors()
        widget: QWidget | None = None
        try:
            if name == "dashboard":
                from gui.widgets.dashboard import DashboardWidget
                widget = DashboardWidget(
                    theme,
                    task_manager=self.task_manager,
                    profile_manager=self.profile_manager,
                    mood_manager=self.mood_manager,
                    energy_predictor=self.energy_predictor,
                    gamification_manager=self.gamification_manager,
                    wellness_orchestrator=self.wellness_orchestrator,
                    subscription_manager=self.subscription_manager,
                )
                # Wire the "Today" quick-action buttons to real navigation.
                # (These signals previously had zero receivers — dead buttons.)
                widget.mood_track_requested.connect(
                    lambda: self._switch_to_tab("mood_tracker"))
                widget.task_add_requested.connect(
                    lambda: self._switch_to_tab("task_manager"))
                widget.breathing_requested.connect(
                    lambda: self._switch_to_tab("breathing"))
                widget.journal_requested.connect(
                    lambda: self._switch_to_tab("journaling"))
                widget.stats_requested.connect(
                    lambda: self._switch_to_tab("mood_tracker"))
            elif name == "task_manager":
                from gui.widgets.task_manager_widget import TaskManagerWidget
                widget = TaskManagerWidget(
                    theme,
                    task_manager=self.task_manager,
                    nlp_parser=self.nlp_parser,
                )
            elif name == "mood_tracker":
                from gui.widgets.mood_tracker import MoodTrackerWidget
                widget = MoodTrackerWidget(
                    theme,
                    mood_manager=self.mood_manager,
                    profile_manager=self.profile_manager,
                )
            elif name == "diary_card":
                from gui.widgets.diary_card_widget import DiaryCardWidget
                widget = DiaryCardWidget(
                    theme,
                    diary_card_manager=self.diary_card_manager,
                    profile_manager=self.profile_manager,
                )
            elif name == "journaling":
                from gui.widgets.journaling_widget import JournalingWidget
                widget = JournalingWidget(
                    theme,
                    journal_manager=self.journaling_manager,
                    profile_manager=self.profile_manager,
                )
                # If an entry trips self-harm/ideation detection, let the user
                # jump straight to crisis resources.
                widget.crisis_requested.connect(
                    lambda: self._switch_to_tab("crisis"))
            elif name == "breathing":
                from gui.widgets.breathing_widget import BreathingWidget
                widget = BreathingWidget(
                    theme,
                    breathing_manager=self.breathing_manager,
                    profile_manager=self.profile_manager,
                )
            elif name == "erp":
                from gui.widgets.erp_widget import ERPWidget
                widget = ERPWidget(self)
            elif name == "meditation":
                from gui.widgets.meditation_widget import MeditationWidget
                widget = MeditationWidget(self)
            elif name == "crisis":
                from gui.widgets.crisis_widget import CrisisWidget
                widget = CrisisWidget(self)
            elif name == "panic_tracker":
                from gui.widgets.panic_tracker_widget import PanicTrackerWidget
                widget = PanicTrackerWidget(self)
            elif name == "sleep":
                from gui.widgets.sleep_widget import SleepWidget
                widget = SleepWidget(self)
            elif name == "medication":
                from gui.widgets.medication_widget import MedicationWidget
                widget = MedicationWidget(self)
            elif name == "file_organizer":
                from gui.widgets.file_organizer_widget import FileOrganizerWidget
                widget = FileOrganizerWidget(
                    theme,
                    file_organizer=self.file_organizer,
                    profile_manager=self.profile_manager,
                )
            elif name == "settings":
                from gui.widgets.settings_widget import SettingsWidget
                widget = SettingsWidget(self)
            elif name == "automation":
                from gui.widgets.automation_widget import AutomationWidget
                widget = AutomationWidget(
                    theme,
                    automation_engine=self.system_automation,
                    subscription_manager=self.subscription_manager,
                )
            elif name == "search":
                from gui.widgets.search_widget import SearchWidget
                widget = SearchWidget(self)
        except ImportError as e:
            logger.info(f"Widget '{name}' not available: {e}")
        except Exception as e:
            logger.error(f"Error creating widget '{name}': {e}")

        if widget is None:
            widget = self._create_placeholder_tab(name)
        return widget

    def _create_placeholder_tab(self, name: str) -> QWidget:
        """Create a placeholder tab for unavailable widgets."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(f"{name.replace('_', ' ').title()}")
        label.setFont(QFont(self.font().family(), 18, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        subtitle = QLabel("This module is loading...")
        subtitle.setFont(QFont(self.font().family(), 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)

        return widget

    def _create_upsell_tab(self, feature_key: str, display_name: str, required_tier: str) -> QWidget:
        """Create an upsell placeholder for gated features."""
        from core.subscription_manager import FEATURE_DISPLAY_NAMES

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(display_name)
        title.setFont(QFont(self.font().family(), 20, QFont.Weight.DemiBold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            f"{FEATURE_DISPLAY_NAMES.get(feature_key, display_name)} is available "
            f"with the {required_tier} plan."
        )
        desc.setWordWrap(True)
        desc.setFont(QFont(self.font().family(), 12))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666; padding: 12px 40px;")
        layout.addWidget(desc)

        trial_btn = QPushButton("Start 14-day trial")
        trial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        trial_btn.setStyleSheet(
            "QPushButton { background-color: #A8845F; color: #18130F; "
            "border-radius: 5px; padding: 10px 20px; font-weight: 500; font-size: 13px; }"
            "QPushButton:hover { background-color: #B89472; }"
        )
        trial_btn.clicked.connect(lambda: self._start_trial_from_upsell(feature_key))
        layout.addWidget(trial_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        maybe_later = QLabel("Continue with free features")
        maybe_later.setAlignment(Qt.AlignmentFlag.AlignCenter)
        maybe_later.setStyleSheet("color: #aaa; font-size: 11px; padding-top: 12px;")
        layout.addWidget(maybe_later)

        return widget

    def _start_trial_from_upsell(self, feature_key: str) -> None:
        """Handle trial start from an upsell tab."""
        if self.subscription_manager:
            try:
                self.subscription_manager.start_trial()
            except Exception as e:
                logger.info("Trial start from upsell: %s", e)

    def _create_file_organizer_fallback(self) -> QWidget:
        """Create a basic file organizer tab."""
        from PyQt6.QtWidgets import QListWidget, QPushButton

        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("File Organizer")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        organize_btn = QPushButton("Organize Directory")
        organize_btn.clicked.connect(self._organize_files_action)
        btn_layout.addWidget(organize_btn)

        stats_btn = QPushButton("View Statistics")
        btn_layout.addWidget(stats_btn)
        layout.addLayout(btn_layout)

        self._file_list = QListWidget()
        layout.addWidget(self._file_list)

        stats = self.file_organizer.get_organization_stats()
        self._file_list.addItem(f"Total files organized: {stats.get('total_files_moved', 0)}")
        for cat, count in stats.get("files_by_category", {}).items():
            self._file_list.addItem(f"  {cat}: {count} files")

        return widget

    def _organize_files_action(self):
        """Handle file organization action."""
        from PyQt6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory", str(Path.home()))
        if dir_path:
            summary = self.file_organizer.organize_files(Path(dir_path))
            QMessageBox.information(
                self, "Organization Complete",
                f"Moved: {summary['moved']}\nSkipped: {summary['skipped']}\nErrors: {summary['errors']}"
            )

    # === Theme Management ===

    def _on_theme_changed(self, index: int):
        """Handle theme selection change."""
        theme_name = self.theme_combo.itemData(index)
        if theme_name:
            self.theme_manager.set_theme(theme_name)
            self._apply_theme()
            self.save_settings()
            self.theme_changed.emit(theme_name)

    def _apply_theme(self):
        """Apply the current theme stylesheet."""
        stylesheet = self.theme_manager.generate_stylesheet()
        self.setStyleSheet(stylesheet)

    def change_theme(self, theme_name: str):
        """Programmatically change the theme."""
        self.theme_manager.set_theme(theme_name)
        idx = self.theme_combo.findData(theme_name)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        self._apply_theme()
        self.save_settings()

    # === Status Bar ===

    def _setup_status_bar(self):
        """Create a status target without adding persistent visual chrome."""
        self.status_bar = StatusMessageSink()

        profile = self.profile_manager.current_profile
        if profile:
            conditions_text = ", ".join(c.value for c in profile.conditions) if profile.conditions else "General"
            self.status_bar.showMessage(f"Profile: {profile.name} | Conditions: {conditions_text} | All data stored locally")
        else:
            self.status_bar.showMessage(f"Hearth v{APP_VERSION} | All data stored locally")

    # === Keyboard Shortcuts ===

    def _setup_shortcut_callbacks(self):
        """Register callbacks with ShortcutManager."""
        self.shortcut_manager.set_callback(
            "new_task", lambda: self._switch_to_tab("task_manager")
        )
        self.shortcut_manager.set_callback(
            "mood_entry", lambda: self._switch_to_tab("mood_tracker")
        )
        self.shortcut_manager.set_callback(
            "breathing_exercise", lambda: self._switch_to_tab("breathing")
        )
        self.shortcut_manager.set_callback(
            "journal_entry", lambda: self._switch_to_tab("journaling")
        )
        self.shortcut_manager.set_callback("global_search", self._show_search)
        self.shortcut_manager.set_callback("help", self._show_help)

    def _setup_shortcuts(self):
        """Bind ShortcutManager actions to the main window."""
        self.shortcut_manager.bind_to_widget(self)

    def _switch_to_tab(self, name: str):
        """Switch to a named tab."""
        if name in self._widgets:
            widget = self._widgets[name]
            idx = self.tabs.indexOf(widget)
            if idx >= 0:
                self.tabs.setCurrentIndex(idx)

    def _sync_navigation(self, index: int) -> None:
        """Keep the side navigation selection aligned with the content stack."""
        if index < 0:
            return
        current_widget = self.tabs.widget(index)
        for name, widget in self._widgets.items():
            button = self._nav_buttons.get(name)
            if button is not None:
                button.setChecked(widget is current_widget)

    def _show_crisis(self) -> None:
        """Keep the crisis plan reachable from every screen."""
        self._switch_to_tab("crisis")

    def _show_search(self):
        """Show the global search overlay."""
        try:
            from gui.widgets.search_widget import SearchWidget
            search = SearchWidget(self)
            search.show()
        except ImportError:
            logger.info("Search widget not available")

    def _show_help(self):
        """Show help dialog."""
        QMessageBox.information(
            self,
            "Hearth — Help",
            "Keyboard Shortcuts:\n\n"
            "Ctrl+N - New Task / Tasks Tab\n"
            "Ctrl+M - Mood Tracker\n"
            "Ctrl+B - Breathing Exercises\n"
            "Ctrl+J - Journal\n"
            "Ctrl+F - Search\n"
            "Ctrl+E - Settings\n"
            "F1 - This Help\n\n"
            "All your data is stored locally on your device.\n"
            "Visit Settings to customize your experience.\n\n"
            "This app is a supplement to professional care, not a replacement."
        )

    # === Background Timers ===

    def _setup_timers(self):
        """Setup background update timers."""
        # System stats update (every 60s)
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self._update_system_stats)
        self.system_timer.start(60000)

        # Notification check (every 5 min)
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self._check_notifications)
        self.notification_timer.start(300000)

        # Automation state evaluation (every 10 min)
        self.automation_timer = QTimer()
        self.automation_timer.timeout.connect(self._evaluate_automation)
        self.automation_timer.start(600000)

        # Focus mode duration check (every 1 min)
        self.focus_check_timer = QTimer()
        self.focus_check_timer.timeout.connect(self._check_focus_duration)
        self.focus_check_timer.start(60000)

    def _update_system_stats(self):
        """Update system statistics."""
        try:
            self.system_optimizer.get_system_stats()
        except (OSError, ValueError, TypeError) as e:
            logger.debug(f"System stats update error: {e}")

    def _check_notifications(self):
        """Check for pending notifications."""
        if self.notification_manager:
            try:
                pending = self.notification_manager.get_pending()
                for notif in pending[:3]:
                    self.status_bar.showMessage(
                        f"Reminder: {notif.get('message', '')}", 10000
                    )
            except (OSError, ValueError, TypeError) as e:
                logger.debug(f"Notification check error: {e}")

    # === Update checking ===

    def _check_for_updates(self) -> None:
        """Background check for app updates."""
        updater = self.auto_updater
        if not updater:
            return
        try:
            release = updater.check()
            if release and not updater.is_skipped(release.version):
                from PyQt6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "Update Available",
                    f"Hearth {release.version} is available.\n\n"
                    f"Released: {release.published_at.strftime('%B %d, %Y')}\n\n"
                    "Would you like to open the download page?",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
                    | QMessageBox.StandardButton.Ignore,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    updater.open_download_page()
                elif reply == QMessageBox.StandardButton.Ignore:
                    updater.skip_version(release.version)
        except Exception:
            logger.debug("Update check failed silently")

    # === System Automation Setup ===

    def _setup_system_automation(self):
        """Initialize system tray, global hotkeys, and automation engine."""
        # System tray
        try:
            self._system_tray = SystemTrayController(self)
            self._system_tray.show_main_window.connect(self.showNormal)
            self._system_tray.show_main_window.connect(self.raise_)
            self._system_tray.show_main_window.connect(self.activateWindow)
            self._system_tray.focus_mode_toggle.connect(self._on_tray_focus_toggle)
            self._system_tray.crisis_mode_trigger.connect(self._on_tray_crisis)
            self._system_tray.grounding_trigger.connect(self._on_tray_grounding)
            self._system_tray.quick_mood_log.connect(self._on_tray_mood)
            self._system_tray.quick_energy_log.connect(self._on_tray_energy)
            self._system_tray.daily_briefing_request.connect(self._show_daily_briefing)
            self._system_tray.quit_app.connect(self._quit_from_tray)
        except Exception as exc:
            logger.warning("System tray init failed: %s", exc)

        # Global hotkeys
        try:
            self._global_hotkeys = GlobalHotkeyManager(self)
            self._global_hotkeys.focus_toggle.connect(self._on_tray_focus_toggle)
            self._global_hotkeys.crisis_trigger.connect(self._on_tray_crisis)
            self._global_hotkeys.grounding_trigger.connect(self._on_tray_grounding)
        except Exception as exc:
            logger.warning("Global hotkeys init failed: %s", exc)

        # Initial automation state sync
        if self.system_automation:
            QTimer.singleShot(5000, self._evaluate_automation)

    def _evaluate_automation(self):
        """Evaluate current psychological state and trigger system automations."""
        if not self.system_automation:
            return
        try:
            results = self.system_automation.evaluate_current_state()
            if results:
                executed = [r for r in results if r.get("status") == "executed"]
                if executed and self._system_tray:
                    names = ", ".join(r["rule"] for r in executed[:3])
                    self._system_tray.set_status(f"Automation active: {names}")
        except Exception as exc:
            logger.debug("Automation evaluation error: %s", exc)

    def _check_focus_duration(self):
        """Check if focus mode has exceeded its planned duration."""
        if not self.system_automation:
            return
        focus = self.system_automation.focus
        if focus.state.name == "ACTIVE" and focus.current_session:
            session = focus.current_session
            if session.duration_minutes > 0:
                elapsed = (datetime.now() - session.started_at).total_seconds() // 60
                if elapsed >= session.duration_minutes and self._system_tray:
                    self._system_tray.show_notification(
                        "Focus Complete",
                        f"Your {int(session.duration_minutes)}-minute focus session is done.",
                    )

    # --- Tray / hotkey handlers ---

    def _on_tray_focus_toggle(self):
        if not self.system_automation:
            return
        focus = self.system_automation.focus
        if focus.state.name == "ACTIVE":
            focus.deactivate()
            if self._system_tray:
                self._system_tray.set_focus_indicator(False)
                self._system_tray.show_notification("Focus Mode", "Focus mode ended.")
        else:
            result = self.system_automation.manual_focus()
            if result.get("focus_mode", {}).get("status") == "activated" and self._system_tray:
                self._system_tray.set_focus_indicator(True)
                self._system_tray.show_notification("Focus Mode", "Focus mode activated.")

    def _on_tray_crisis(self):
        if self.system_automation:
            self.system_automation.manual_crisis()
        self._switch_to_tab("crisis")
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_tray_grounding(self):
        if self.system_automation:
            self.system_automation.manual_grounding()
        self._switch_to_tab("breathing")
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_tray_mood(self, score: int):
        """Quick mood log from tray."""
        self._switch_to_tab("mood_tracker")
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_tray_energy(self, score: int):
        """Quick energy log from tray."""
        self._switch_to_tab("mood_tracker")
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _show_daily_briefing(self):
        """Show daily briefing from tray request."""
        try:
            briefing = self.wellness_orchestrator.daily_briefing()
            lines = [
                f"Energy: {briefing.energy_forecast or 'Not logged yet'}",
            ]
            if briefing.suggested_skill:
                lines.append(f"Suggested skill: {briefing.suggested_skill}")
            if briefing.crisis_signals:
                lines.append(f"Attention: {briefing.crisis_signals[0].description}")
            msg = "\n".join(lines)
            if self._system_tray:
                self._system_tray.show_notification("Briefing", msg, 8000)
        except Exception as exc:
            logger.debug("Daily briefing error: %s", exc)

    def _quit_from_tray(self):
        """Graceful quit initiated from system tray."""
        if self._global_hotkeys:
            self._global_hotkeys.stop()
        self.close()

    # === Window Events ===

    def closeEvent(self, event):  # noqa: N802
        """Handle window close — minimize to tray or quit."""
        if self._system_tray and self._system_tray.isVisible():
            event.ignore()
            self.hide()
            self._system_tray.show_notification(
                "Hearth",
                "Running in background. Click the tray icon to restore.",
                3000,
            )
            return

        self.save_settings()

        # Save any pending data in widgets
        for widget in self._widgets.values():
            if hasattr(widget, "save_state"):
                try:
                    widget.save_state()
                except Exception as e:
                    logger.error(f"Error saving widget state: {e}")

        if self._global_hotkeys:
            self._global_hotkeys.stop()

        event.accept()

    def resizeEvent(self, event):  # noqa: N802
        """Handle window resize."""
        super().resizeEvent(event)
        # Widgets can adapt to size changes via their own resize handling
