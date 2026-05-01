"""
Refactored main window for Mindful Organizer.
Orchestrates all widget modules and manages application state.
"""
import sys
import json
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QScrollArea, QFrame, QGridLayout,
    QStatusBar, QMessageBox, QApplication, QSystemTrayIcon, QMenu,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence, QShortcut

from gui.themes import ThemeManager, THEMES
from core.task_manager import TaskManager
from core.system_optimizer import SystemOptimizer
from core.ai_optimizer import AISystemOptimizer
from core.file_organizer import FileOrganizer
from profiles.mental_health_profile_builder import (
    ProfileManager, Condition, TherapyType,
)

logger = logging.getLogger(__name__)


class AdaptiveMainWindow(QMainWindow):
    """Main window with adaptive features based on user's mental health profile."""

    # Signals for cross-widget communication
    theme_changed = pyqtSignal(str)
    profile_changed = pyqtSignal(object)
    energy_updated = pyqtSignal(int)
    mood_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mindful Organizer")
        self.setMinimumSize(1200, 800)
        self.setGeometry(100, 100, 1400, 900)

        # Initialize data directory (platform-aware)
        self.data_dir = self._get_data_dir()
        self.data_dir.mkdir(exist_ok=True, parents=True)

        # Initialize theme manager
        self.theme_manager = ThemeManager()

        # Initialize core managers
        self.profile_manager = ProfileManager(self.data_dir)
        self.task_manager = TaskManager(self.data_dir)
        self.file_organizer = FileOrganizer(self.data_dir)
        self.system_optimizer = SystemOptimizer(self.data_dir)
        self.ai_optimizer = AISystemOptimizer(self.data_dir)

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

        # Widget references
        self._widgets = {}

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
            from windows.platform_utils import get_data_directory
            return get_data_directory()
        except ImportError:
            if sys.platform == "win32":
                base = Path.home() / "AppData" / "Roaming"
            elif sys.platform == "darwin":
                base = Path.home() / "Library" / "Application Support"
            else:
                base = Path.home()
            return base / ".mindful_optimizer"

    def _load_settings(self):
        """Load application settings."""
        settings_file = self.data_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, "r") as f:
                    settings = json.load(f)
                self.theme_manager.set_theme(settings.get("theme", "light"))
                self.theme_manager.font_scale = settings.get("font_scale", 1.0)
                self.theme_manager.color_blind_mode = settings.get("color_blind_mode")
                self.theme_manager.reduced_motion = settings.get("reduced_motion", False)
                self.theme_manager.dyslexia_font = settings.get("dyslexia_font", False)
            except (json.JSONDecodeError, Exception) as e:
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
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    # === Lazy-loaded manager properties ===

    @property
    def sleep_tracker(self):
        if self._sleep_tracker is None:
            try:
                from core.sleep_tracker import SleepTracker
                self._sleep_tracker = SleepTracker(self.data_dir)
            except ImportError:
                logger.warning("SleepTracker not available")
        return self._sleep_tracker

    @property
    def medication_tracker(self):
        if self._medication_tracker is None:
            try:
                from core.medication_tracker import MedicationTracker
                self._medication_tracker = MedicationTracker(self.data_dir)
            except ImportError:
                logger.warning("MedicationTracker not available")
        return self._medication_tracker

    @property
    def mood_analytics(self):
        if self._mood_analytics is None:
            try:
                from core.mood_analytics import MoodAnalytics
                self._mood_analytics = MoodAnalytics()
            except ImportError:
                logger.warning("MoodAnalytics not available")
        return self._mood_analytics

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
                self._export_manager = ExportManager(self.data_dir)
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
    def gamification_manager(self):
        if self._gamification_manager is None:
            try:
                from file_organization.adhd_gamification import ADHDGameManager
                self._gamification_manager = ADHDGameManager(self.data_dir)
            except ImportError:
                logger.warning("ADHDGameManager not available")
        return self._gamification_manager

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
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLineEdit, QCheckBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Welcome to Mindful Organizer")
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

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(True)
        main_layout.addWidget(self.tabs)

        # Add core tabs
        self._add_tabs()

        # Status bar
        self._setup_status_bar()

        # Apply theme
        self._apply_theme()

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        # Start background timers
        self._setup_timers()

        self.show()

    def _setup_header(self, parent_layout: QVBoxLayout):
        """Setup the header bar with profile and theme controls."""
        header = QFrame()
        header.setMaximumHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)

        # App title
        title = QLabel("Mindful Organizer")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Profile info
        profile = self.profile_manager.current_profile
        profile_name = profile.name if profile else "User"
        profile_label = QLabel(f"Welcome, {profile_name}")
        profile_label.setFont(QFont("Segoe UI", 11))
        header_layout.addWidget(profile_label)

        # Theme selector
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Segoe UI", 11))
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
        therapy_types = profile.therapy_types if profile else set()

        # Core tabs (always present)
        self._add_tab("dashboard", "Dashboard")
        self._add_tab("task_manager", "Tasks")
        self._add_tab("mood_tracker", "Mood")
        self._add_tab("journaling", "Journal")
        self._add_tab("breathing", "Breathing")

        # Condition-specific tabs
        if Condition.OCD in conditions:
            self._add_tab("erp", "ERP")

        # Therapy tabs
        self._add_tab("meditation", "Meditation")
        self._add_tab("crisis", "Crisis Plan")

        # Tracking tabs
        self._add_tab("sleep", "Sleep")
        self._add_tab("medication", "Medication")

        # File organization
        self._add_tab("file_organizer", "Files")

        # Settings (always last)
        self._add_tab("settings", "Settings")

    def _add_tab(self, widget_name: str, display_name: str):
        """Add a tab, creating the widget with fallback to placeholder."""
        widget = self._create_widget(widget_name)
        if widget:
            self._widgets[widget_name] = widget
            self.tabs.addTab(widget, display_name)

    def _create_widget(self, name: str) -> Optional[QWidget]:
        """Create a widget by name with graceful fallback."""
        try:
            if name == "dashboard":
                from gui.widgets.dashboard import DashboardWidget
                return DashboardWidget(self)
            elif name == "task_manager":
                from gui.widgets.task_manager_widget import TaskManagerWidget
                return TaskManagerWidget(self)
            elif name == "mood_tracker":
                from gui.widgets.mood_tracker import MoodTrackerWidget
                return MoodTrackerWidget(self)
            elif name == "journaling":
                from gui.widgets.journaling_widget import JournalingWidget
                return JournalingWidget(self)
            elif name == "breathing":
                from gui.widgets.breathing_widget import BreathingWidget
                return BreathingWidget(self)
            elif name == "erp":
                from gui.widgets.erp_widget import ERPWidget
                return ERPWidget(self)
            elif name == "meditation":
                from gui.widgets.meditation_widget import MeditationWidget
                return MeditationWidget(self)
            elif name == "crisis":
                from gui.widgets.crisis_widget import CrisisWidget
                return CrisisWidget(self)
            elif name == "sleep":
                from gui.widgets.sleep_widget import SleepWidget
                return SleepWidget(self)
            elif name == "medication":
                from gui.widgets.medication_widget import MedicationWidget
                return MedicationWidget(self)
            elif name == "file_organizer":
                return self._create_file_organizer_fallback()
            elif name == "settings":
                from gui.widgets.settings_widget import SettingsWidget
                return SettingsWidget(self)
            elif name == "search":
                from gui.widgets.search_widget import SearchWidget
                return SearchWidget(self)
        except ImportError as e:
            logger.info(f"Widget '{name}' not available: {e}")
        except Exception as e:
            logger.error(f"Error creating widget '{name}': {e}")

        return self._create_placeholder_tab(name)

    def _create_placeholder_tab(self, name: str) -> QWidget:
        """Create a placeholder tab for unavailable widgets."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(f"{name.replace('_', ' ').title()}")
        label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        subtitle = QLabel("This module is loading...")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)

        return widget

    def _create_file_organizer_fallback(self) -> QWidget:
        """Create a basic file organizer tab."""
        from PyQt6.QtWidgets import QPushButton, QListWidget, QFileDialog

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
        """Setup the status bar with useful info."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        profile = self.profile_manager.current_profile
        if profile:
            conditions_text = ", ".join(c.value for c in profile.conditions) if profile.conditions else "General"
            self.status_bar.showMessage(f"Profile: {profile.name} | Conditions: {conditions_text} | All data stored locally")
        else:
            self.status_bar.showMessage("Mindful Organizer v1.0.0 | All data stored locally")

    # === Keyboard Shortcuts ===

    def _setup_shortcuts(self):
        """Setup global keyboard shortcuts."""
        shortcuts = {
            "Ctrl+N": lambda: self._switch_to_tab("task_manager"),
            "Ctrl+M": lambda: self._switch_to_tab("mood_tracker"),
            "Ctrl+B": lambda: self._switch_to_tab("breathing"),
            "Ctrl+J": lambda: self._switch_to_tab("journaling"),
            "Ctrl+F": self._show_search,
            "Ctrl+E": lambda: self._switch_to_tab("settings"),
            "F1": self._show_help,
        }

        for key, callback in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)

    def _switch_to_tab(self, name: str):
        """Switch to a named tab."""
        if name in self._widgets:
            widget = self._widgets[name]
            idx = self.tabs.indexOf(widget)
            if idx >= 0:
                self.tabs.setCurrentIndex(idx)

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
            "Mindful Organizer - Help",
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

    def _update_system_stats(self):
        """Update system statistics."""
        try:
            self.system_optimizer.get_system_stats()
        except Exception as e:
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
            except Exception:
                pass

    # === Window Events ===

    def closeEvent(self, event):
        """Handle window close - save all state."""
        self.save_settings()

        # Save any pending data in widgets
        for widget in self._widgets.values():
            if hasattr(widget, "save_state"):
                try:
                    widget.save_state()
                except Exception as e:
                    logger.error(f"Error saving widget state: {e}")

        event.accept()

    def resizeEvent(self, event):
        """Handle window resize."""
        super().resizeEvent(event)
        # Widgets can adapt to size changes via their own resize handling
