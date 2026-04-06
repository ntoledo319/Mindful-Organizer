"""
Mindful Organizer GUI widget modules.

Each widget is a self-contained QWidget designed for tab or component
embedding in the main application window.
"""

from gui.widgets.dashboard import DashboardWidget
from gui.widgets.mood_tracker import MoodTrackerWidget
from gui.widgets.task_manager_widget import TaskManagerWidget
from gui.widgets.breathing_widget import BreathingWidget
from gui.widgets.journaling_widget import JournalingWidget
from gui.widgets.crisis_widget import CrisisWidget
from gui.widgets.erp_widget import ERPWidget
from gui.widgets.settings_widget import SettingsWidget
from gui.widgets.onboarding import OnboardingWizard
from gui.widgets.search_widget import SearchWidget
from gui.widgets.meditation_widget import MeditationWidget
from gui.widgets.sleep_widget import SleepWidget
from gui.widgets.medication_widget import MedicationWidget

__all__ = [
    "DashboardWidget",
    "MoodTrackerWidget",
    "TaskManagerWidget",
    "BreathingWidget",
    "JournalingWidget",
    "CrisisWidget",
    "ERPWidget",
    "SettingsWidget",
    "OnboardingWizard",
    "SearchWidget",
    "MeditationWidget",
    "SleepWidget",
    "MedicationWidget",
]
