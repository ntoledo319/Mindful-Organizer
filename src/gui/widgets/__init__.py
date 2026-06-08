"""
Mindful Organizer GUI widget modules.

Each widget is a self-contained QWidget designed for tab or component
embedding in the main application window.
"""

from gui.widgets.automation_widget import AutomationWidget
from gui.widgets.breathing_widget import BreathingWidget
from gui.widgets.crisis_widget import CrisisWidget
from gui.widgets.diary_card_widget import DiaryCardWidget
from gui.widgets.erp_widget import ERPWidget
from gui.widgets.file_organizer_widget import FileOrganizerWidget
from gui.widgets.focus_session_widget import FocusSessionWidget
from gui.widgets.hearth_today import HearthToday
from gui.widgets.journaling_widget import JournalingWidget
from gui.widgets.medication_widget import MedicationWidget
from gui.widgets.meditation_widget import MeditationWidget
from gui.widgets.mood_tracker import MoodTrackerWidget
from gui.widgets.onboarding import OnboardingWizard
from gui.widgets.panic_tracker_widget import PanicTrackerWidget
from gui.widgets.search_widget import SearchWidget
from gui.widgets.settings_widget import SettingsWidget
from gui.widgets.sleep_widget import SleepWidget
from gui.widgets.task_manager_widget import TaskManagerWidget
from gui.widgets.voice_journal_widget import VoiceJournalWidget

__all__ = [
    "AutomationWidget",
    "DiaryCardWidget",
    "FileOrganizerWidget",
    "HearthToday",
    "MoodTrackerWidget",
    "TaskManagerWidget",
    "BreathingWidget",
    "FocusSessionWidget",
    "JournalingWidget",
    "VoiceJournalWidget",
    "CrisisWidget",
    "ERPWidget",
    "SettingsWidget",
    "OnboardingWizard",
    "SearchWidget",
    "MeditationWidget",
    "SleepWidget",
    "MedicationWidget",
    "PanicTrackerWidget",
]
