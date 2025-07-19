"""
Modern, adaptive GUI for the Mindful Optimizer with mental health support features.
"""
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QPushButton, QComboBox,
                           QStackedWidget, QScrollArea, QFrame, QLineEdit,
                           QCheckBox, QProgressBar, QSlider, QSpinBox,
                           QCalendarWidget, QTimeEdit, QTextEdit, QListWidget,
                           QListWidgetItem, QDialog, QDialogButtonBox,
                           QGridLayout, QRadioButton, QButtonGroup, QFileDialog,
                           QGroupBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDateTime, QDate
from PyQt6.QtGui import QColor, QPalette, QIcon, QFont
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, time
import logging

from core.task_manager import TaskManager, Task, TaskPriority, TaskCategory
from core.system_optimizer import SystemOptimizer
from core.ai_optimizer import AISystemOptimizer
from profile.mental_health_profile_builder import ProfileManager, Profile, Condition, TherapyType, TherapySkill
from core.file_organizer import FileOrganizer

class AdaptiveMainWindow(QMainWindow):
    """Main window with adaptive features based on user's mental health profile."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mindful Organizer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize core components
        self.data_dir = Path.home() / ".mindful_optimizer"
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize all managers
        self.profile_manager = ProfileManager(self.data_dir)
        self.task_manager = TaskManager(self.data_dir)
        self.file_organizer = FileOrganizer(self.data_dir)
        self.system_optimizer = SystemOptimizer(self.data_dir)
        self.ai_optimizer = AISystemOptimizer(self.data_dir)
        
        # Start system monitoring
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_system_state)
        self.monitor_timer.start(60000)  # Update every minute
        
        # Create central widget with scroll area
        self.scroll_area = QScrollArea()
        self.setCentralWidget(self.scroll_area)
        self.central_widget = QWidget()
        self.scroll_area.setWidget(self.central_widget)
        self.scroll_area.setWidgetResizable(True)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Show profile setup if no profile exists
        if not self.profile_manager.current_profile:
            self._show_profile_setup()
        else:
            self._initialize_with_profile(self.profile_manager.current_profile)
            
    def _show_profile_setup(self):
        """Show the profile setup wizard."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Welcome to Mindful Organizer")
        dialog.setMinimumWidth(600)
        layout = QVBoxLayout(dialog)
        
        # Welcome message
        welcome = QLabel("Let's set up your mental health profile")
        welcome.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(welcome)
        
        # Name input
        name_label = QLabel("Your Name:")
        name_label.setFont(QFont("Arial", 12))
        name_input = QLineEdit()
        name_input.setFont(QFont("Arial", 12))
        layout.addWidget(name_label)
        layout.addWidget(name_input)
        
        # Conditions selection
        conditions_label = QLabel("Select Your Conditions:")
        conditions_label.setFont(QFont("Arial", 12))
        layout.addWidget(conditions_label)
        
        condition_checks = {}
        for condition in Condition:
            check = QCheckBox(condition.value)
            check.setFont(QFont("Arial", 12))
            layout.addWidget(check)
            condition_checks[condition] = check
        
        # Therapy types
        therapy_label = QLabel("Select Preferred Therapy Types:")
        therapy_label.setFont(QFont("Arial", 12))
        layout.addWidget(therapy_label)
        
        therapy_checks = {}
        for therapy in TherapyType:
            check = QCheckBox(therapy.value)
            check.setFont(QFont("Arial", 12))
            layout.addWidget(check)
            therapy_checks[therapy] = check
            
        # File organization
        org_label = QLabel("File Organization:")
        org_label.setFont(QFont("Arial", 12))
        layout.addWidget(org_label)
        
        root_dir_label = QLabel("Select Root Directory for Files:")
        root_dir_label.setFont(QFont("Arial", 12))
        root_dir_layout = QHBoxLayout()
        root_dir_input = QLineEdit()
        root_dir_input.setFont(QFont("Arial", 12))
        root_dir_btn = QPushButton("Browse")
        root_dir_btn.setFont(QFont("Arial", 12))
        
        def browse_dir():
            dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
            if dir_path:
                root_dir_input.setText(dir_path)
                
        root_dir_btn.clicked.connect(browse_dir)
        root_dir_layout.addWidget(root_dir_input)
        root_dir_layout.addWidget(root_dir_btn)
        layout.addWidget(root_dir_label)
        layout.addLayout(root_dir_layout)
        
        # Organization preferences
        org_prefs_label = QLabel("Organization Preferences:")
        org_prefs_label.setFont(QFont("Arial", 12))
        layout.addWidget(org_prefs_label)
        
        org_prefs = {
            "auto_categorize": QCheckBox("Automatically categorize files"),
            "use_tags": QCheckBox("Use tags for organization"),
            "track_progress": QCheckBox("Track progress and generate reports"),
            "backup_enabled": QCheckBox("Enable automatic backups"),
            "notification_enabled": QCheckBox("Enable notifications")
        }
        
        for pref in org_prefs.values():
            pref.setFont(QFont("Arial", 12))
            pref.setChecked(True)
            layout.addWidget(pref)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Create profile
            conditions = {cond for cond, check in condition_checks.items() 
                        if check.isChecked()}
            
            profile = self.profile_manager.create_profile(
                name=name_input.text(),
                conditions=conditions
            )
            
            # Initialize file organizer
            root_dir = Path(root_dir_input.text())
            self.file_organizer = FileOrganizer(root_dir, profile)
            
            # Save organization preferences
            profile.organization_preferences = {
                name: check.isChecked() 
                for name, check in org_prefs.items()
            }
            
            self.profile_manager.save_profile(profile)
            self._initialize_with_profile(profile)
        else:
            self.close()
            
    def _initialize_with_profile(self, profile: Profile):
        """Initialize the application with the given profile."""
        # Initialize file organizer if not already done
        if not self.file_organizer:
            root_dir = Path(self.data_dir) / "files"
            self.file_organizer = FileOrganizer(root_dir, profile)
            
        # Create folder structure
        self.file_organizer.setup_folder_structure()
        
        # Setup UI
        self.setup_ui()
        
        # Apply theme
        self.apply_theme("light")
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(60000)

    def setup_ui(self):
        """Setup the main UI components."""
        self._setup_header()
        self._setup_tabs()
        
    def _setup_header(self):
        """Setup the header section with profile and theme controls."""
        header = QWidget()
        header_layout = QGridLayout(header)
        header_layout.setSpacing(15)  # Increased spacing
        
        # Profile selector with larger size
        profile_label = QLabel("Mental Health Profile:")
        profile_label.setFont(QFont("Arial", 12))
        self.profile_combo = QComboBox()
        self.profile_combo.setFont(QFont("Arial", 12))
        self.profile_combo.setMinimumWidth(200)  # Increased width
        self.profile_combo.addItems([
            "General",
            "Bipolar Disorder",
            "ADHD",
            "Anxiety",
            "Depression",
            "OCD",
            "ADHD + Anxiety",
            "Depression + Anxiety",
            "Custom..."
        ])
        
        # Theme selector
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Arial", 12))
        self.theme_combo = QComboBox()
        self.theme_combo.setFont(QFont("Arial", 12))
        self.theme_combo.setMinimumWidth(150)  # Increased width
        self.theme_combo.addItems(list(self.themes.keys()))
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        
        # Current mood with DBT-based scale
        mood_label = QLabel("Current Mood:")
        mood_label.setFont(QFont("Arial", 12))
        self.mood_combo = QComboBox()
        self.mood_combo.setFont(QFont("Arial", 12))
        self.mood_combo.setMinimumWidth(200)  # Increased width
        self.mood_combo.addItems([
            "Euphoric (Mania)",
            "Extremely Elevated",
            "Elevated",
            "Slightly Elevated",
            "Stable",
            "Slightly Low",
            "Low",
            "Very Low",
            "Severely Depressed"
        ])
        
        # Symptom tracking
        symptoms_label = QLabel("Current Symptoms:")
        symptoms_label.setFont(QFont("Arial", 12))
        self.symptoms_frame = QFrame()
        symptoms_layout = QGridLayout(self.symptoms_frame)
        
        # Common symptoms for various conditions
        self.symptom_checks = {}
        symptoms = [
            "Racing Thoughts",
            "Decreased Need for Sleep",
            "Increased Energy",
            "Impulsivity",
            "Irritability",
            "Anxiety",
            "Depression",
            "Fatigue",
            "Difficulty Concentrating",
            "Sleep Problems"
        ]
        
        row = 0
        col = 0
        for symptom in symptoms:
            check = QCheckBox(symptom)
            check.setFont(QFont("Arial", 11))
            symptoms_layout.addWidget(check, row, col)
            self.symptom_checks[symptom] = check
            col += 1
            if col > 4:  # 5 symptoms per row
                col = 0
                row += 1
        
        # Add widgets to header grid layout
        header_layout.addWidget(profile_label, 0, 0)
        header_layout.addWidget(self.profile_combo, 0, 1)
        header_layout.addWidget(theme_label, 0, 2)
        header_layout.addWidget(self.theme_combo, 0, 3)
        header_layout.addWidget(mood_label, 1, 0)
        header_layout.addWidget(self.mood_combo, 1, 1)
        header_layout.addWidget(symptoms_label, 2, 0)
        header_layout.addWidget(self.symptoms_frame, 3, 0, 1, 4)
        
        self.main_layout.addWidget(header)
        
    def _setup_tabs(self):
        """Setup the main tab widget with different sections."""
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 12))
        self.tabs.setStyleSheet("QTabBar::tab { height: 40px; }")  # Taller tabs
        
        # Add tabs based on profile
        self.tabs.addTab(self._create_dashboard_tab(), "Dashboard")
        self.tabs.addTab(self._create_mood_tracker_tab(), "Mood Tracker")
        self.tabs.addTab(self._create_task_manager_tab(), "Task Manager")
        self.tabs.addTab(self._create_file_organizer_tab(), "File Organizer")
        
        # Add condition-specific tabs
        profile = self.profile_manager.current_profile
        if profile:
            if TherapyType.DBT in profile.therapy_types:
                self.tabs.addTab(self._create_dbt_skills_tab(), "DBT Skills")
            if TherapyType.CBT in profile.therapy_types:
                self.tabs.addTab(self._create_cbt_skills_tab(), "CBT Skills")
            if TherapyType.ERP in profile.therapy_types:
                self.tabs.addTab(self._create_erp_tab(), "ERP Work")
            if TherapyType.ACT in profile.therapy_types:
                self.tabs.addTab(self._create_act_tab(), "ACT Skills")
                
        self.tabs.addTab(self._create_settings_tab(), "Settings")
        
        self.main_layout.addWidget(self.tabs)
        
    def _create_dashboard_tab(self) -> QWidget:
        """Create the dashboard tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Welcome message
        welcome = QLabel("Welcome to Your Mental Health Dashboard")
        welcome.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(welcome)
        
        # Quick actions section
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        actions_layout = QHBoxLayout(actions_frame)
        
        # Create action buttons with icons and larger size
        buttons = [
            ("Track Mood", self._show_mood_dialog),
            ("Add Task", self._show_add_task_dialog),
            ("DBT Skills", self._show_dbt_skills_dialog),
            ("View Stats", self._show_stats_dialog)
        ]
        
        for text, slot in buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("Arial", 12))
            btn.setMinimumSize(150, 50)  # Larger buttons
            btn.clicked.connect(slot)
            actions_layout.addWidget(btn)
        
        layout.addWidget(actions_frame)
        
        # Daily overview section
        overview_frame = QFrame()
        overview_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        overview_layout = QGridLayout(overview_frame)
        
        # Mood history chart (placeholder)
        mood_chart = QFrame()
        mood_chart.setMinimumHeight(200)
        mood_chart.setStyleSheet("background-color: #F0F0F0; border: 1px solid #CCCCCC;")
        overview_layout.addWidget(QLabel("Today's Mood Pattern"), 0, 0)
        overview_layout.addWidget(mood_chart, 1, 0)
        
        # Task progress
        task_progress = QProgressBar()
        task_progress.setMinimumWidth(300)
        task_progress.setMinimumHeight(30)
        task_progress.setValue(70)
        overview_layout.addWidget(QLabel("Task Progress"), 0, 1)
        overview_layout.addWidget(task_progress, 1, 1)
        
        layout.addWidget(overview_frame)
        
        # Suggestions section
        suggestions_frame = QFrame()
        suggestions_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        suggestions_layout = QVBoxLayout(suggestions_frame)
        
        suggestions_label = QLabel("Personalized Suggestions")
        suggestions_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        suggestions_layout.addWidget(suggestions_label)
        
        suggestions_list = QListWidget()
        suggestions_list.setFont(QFont("Arial", 12))
        suggestions_list.addItems([
            "Your energy seems low - Consider using the 'PLEASE' skill",
            "You have 3 high-priority tasks pending",
            "Great job using mindfulness skills today!",
            "Remember to take your medication",
            "Time for a short meditation break?"
        ])
        suggestions_layout.addWidget(suggestions_list)
        
        layout.addWidget(suggestions_frame)
        
        # System status section
        system_group = QGroupBox("AI System Optimization")
        system_group.setFont(QFont("Arial", 12))
        system_layout = QGridLayout(system_group)
        
        # CPU Usage
        self.cpu_label = QLabel("CPU Usage:")
        self.cpu_label.setFont(QFont("Arial", 11))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        system_layout.addWidget(self.cpu_label, 0, 0)
        system_layout.addWidget(self.cpu_progress, 0, 1)
        
        # Memory Usage
        self.memory_label = QLabel("Memory Usage:")
        self.memory_label.setFont(QFont("Arial", 11))
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        system_layout.addWidget(self.memory_label, 1, 0)
        system_layout.addWidget(self.memory_progress, 1, 1)
        
        # Disk Usage
        self.disk_label = QLabel("Disk Usage:")
        self.disk_label.setFont(QFont("Arial", 11))
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)
        system_layout.addWidget(self.disk_label, 2, 0)
        system_layout.addWidget(self.disk_progress, 2, 1)
        
        # Battery Status
        self.battery_label = QLabel("Battery:")
        self.battery_label.setFont(QFont("Arial", 11))
        self.battery_progress = QProgressBar()
        self.battery_progress.setRange(0, 100)
        system_layout.addWidget(self.battery_label, 3, 0)
        system_layout.addWidget(self.battery_progress, 3, 1)
        
        # Anomaly Score
        self.anomaly_label = QLabel("System Health:")
        self.anomaly_label.setFont(QFont("Arial", 11))
        self.anomaly_progress = QProgressBar()
        self.anomaly_progress.setRange(-100, 0)  # Anomaly scores are negative
        system_layout.addWidget(self.anomaly_label, 4, 0)
        system_layout.addWidget(self.anomaly_progress, 4, 1)
        
        # AI Suggestions
        self.system_suggestions = QTextEdit()
        self.system_suggestions.setReadOnly(True)
        self.system_suggestions.setFont(QFont("Arial", 11))
        self.system_suggestions.setMinimumHeight(150)
        system_layout.addWidget(QLabel("AI Optimization Suggestions:"), 5, 0)
        system_layout.addWidget(self.system_suggestions, 5, 1)
        
        # Optimize button
        optimize_btn = QPushButton("Run AI Optimization")
        optimize_btn.setFont(QFont("Arial", 11))
        optimize_btn.clicked.connect(self._optimize_system)
        system_layout.addWidget(optimize_btn, 6, 1)
        
        layout.addWidget(system_group)
        
        return tab
        
    def _create_mood_tracker_tab(self) -> QWidget:
        """Create the mood tracker tab with condition-specific features."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Calendar for selecting date
        calendar = QCalendarWidget()
        calendar.setMinimumHeight(300)
        calendar.setFont(QFont("Arial", 12))
        layout.addWidget(calendar)
        
        # Mood entry section
        entry_frame = QFrame()
        entry_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        entry_layout = QGridLayout(entry_frame)
        
        # Time selection
        time_label = QLabel("Time:")
        time_label.setFont(QFont("Arial", 12))
        time_edit = QTimeEdit()
        time_edit.setFont(QFont("Arial", 12))
        entry_layout.addWidget(time_label, 0, 0)
        entry_layout.addWidget(time_edit, 0, 1)
        
        # Get current profile and conditions
        profile = self.profile_manager.current_profile
        conditions = profile.conditions if profile else set()
        
        # Condition-specific tracking sections
        row = 1
        
        if Condition.BIPOLAR in conditions:
            # Mood scale for bipolar
            mood_label = QLabel("Mood (-5 to +5):")
            mood_label.setFont(QFont("Arial", 12))
            mood_slider = QSlider(Qt.Orientation.Horizontal)
            mood_slider.setRange(-5, 5)
            mood_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            mood_slider.setTickInterval(1)
            entry_layout.addWidget(mood_label, row, 0)
            entry_layout.addWidget(mood_slider, row, 1)
            row += 1
            
            # Mania symptoms
            mania_label = QLabel("Mania Symptoms:")
            mania_label.setFont(QFont("Arial", 12))
            mania_frame = QFrame()
            mania_layout = QGridLayout(mania_frame)
            mania_symptoms = [
                "Racing thoughts",
                "Decreased need for sleep",
                "Increased energy",
                "Risk-taking behavior",
                "Grandiose thoughts",
                "Pressured speech",
                "Goal-directed activity",
                "Distractibility"
            ]
            self._add_symptom_checkboxes(mania_layout, mania_symptoms)
            entry_layout.addWidget(mania_label, row, 0)
            entry_layout.addWidget(mania_frame, row, 1)
            row += 1
            
        if Condition.DEPRESSION in conditions:
            # Depression symptoms
            depression_label = QLabel("Depression Symptoms:")
            depression_label.setFont(QFont("Arial", 12))
            depression_frame = QFrame()
            depression_layout = QGridLayout(depression_frame)
            depression_symptoms = [
                "Low mood",
                "Loss of interest",
                "Sleep changes",
                "Appetite changes",
                "Fatigue",
                "Worthlessness",
                "Concentration issues",
                "Suicidal thoughts"
            ]
            self._add_symptom_checkboxes(depression_layout, depression_symptoms)
            entry_layout.addWidget(depression_label, row, 0)
            entry_layout.addWidget(depression_frame, row, 1)
            row += 1
            
        if Condition.ANXIETY in conditions:
            # Anxiety symptoms
            anxiety_label = QLabel("Anxiety Symptoms:")
            anxiety_label.setFont(QFont("Arial", 12))
            anxiety_frame = QFrame()
            anxiety_layout = QGridLayout(anxiety_frame)
            anxiety_symptoms = [
                "Worry",
                "Restlessness",
                "Physical tension",
                "Racing heart",
                "Sweating",
                "Trembling",
                "Panic attacks",
                "Avoidance"
            ]
            self._add_symptom_checkboxes(anxiety_layout, anxiety_symptoms)
            entry_layout.addWidget(anxiety_label, row, 0)
            entry_layout.addWidget(anxiety_frame, row, 1)
            row += 1
            
        if Condition.OCD in conditions:
            # OCD tracking
            ocd_label = QLabel("OCD Symptoms:")
            ocd_label.setFont(QFont("Arial", 12))
            ocd_frame = QFrame()
            ocd_layout = QGridLayout(ocd_frame)
            
            # Obsessions and compulsions
            obsessions_label = QLabel("Obsessions:")
            obsessions_label.setFont(QFont("Arial", 11))
            obsessions_input = QSpinBox()
            obsessions_input.setRange(0, 10)
            obsessions_input.setPrefix("Frequency: ")
            
            compulsions_label = QLabel("Compulsions:")
            compulsions_label.setFont(QFont("Arial", 11))
            compulsions_input = QSpinBox()
            compulsions_input.setRange(0, 10)
            compulsions_input.setPrefix("Frequency: ")
            
            resistance_label = QLabel("Resistance:")
            resistance_label.setFont(QFont("Arial", 11))
            resistance_input = QSpinBox()
            resistance_input.setRange(0, 10)
            resistance_input.setPrefix("Strength: ")
            
            ocd_layout.addWidget(obsessions_label, 0, 0)
            ocd_layout.addWidget(obsessions_input, 0, 1)
            ocd_layout.addWidget(compulsions_label, 1, 0)
            ocd_layout.addWidget(compulsions_input, 1, 1)
            ocd_layout.addWidget(resistance_label, 2, 0)
            ocd_layout.addWidget(resistance_input, 2, 1)
            
            entry_layout.addWidget(ocd_label, row, 0)
            entry_layout.addWidget(ocd_frame, row, 1)
            row += 1
            
        if Condition.ADHD in conditions:
            # ADHD tracking
            adhd_label = QLabel("ADHD Symptoms:")
            adhd_label.setFont(QFont("Arial", 12))
            adhd_frame = QFrame()
            adhd_layout = QGridLayout(adhd_frame)
            adhd_symptoms = [
                "Difficulty focusing",
                "Hyperactivity",
                "Impulsivity",
                "Task switching issues",
                "Time management issues",
                "Procrastination",
                "Forgetfulness",
                "Disorganization"
            ]
            self._add_symptom_checkboxes(adhd_layout, adhd_symptoms)
            entry_layout.addWidget(adhd_label, row, 0)
            entry_layout.addWidget(adhd_frame, row, 1)
            row += 1
            
        # Therapy skills used
        if profile and profile.therapy_types:
            skills_label = QLabel("Skills Used:")
            skills_label.setFont(QFont("Arial", 12))
            skills_frame = QFrame()
            skills_layout = QGridLayout(skills_frame)
            
            all_skills = []
            if TherapyType.DBT in profile.therapy_types:
                all_skills.extend([
                    "Mindfulness",
                    "Distress Tolerance",
                    "Emotion Regulation",
                    "Interpersonal Skills"
                ])
            if TherapyType.CBT in profile.therapy_types:
                all_skills.extend([
                    "Thought Records",
                    "Behavioral Activation",
                    "Exposure Practice",
                    "Problem Solving"
                ])
            if TherapyType.ACT in profile.therapy_types:
                all_skills.extend([
                    "Acceptance",
                    "Cognitive Defusion",
                    "Present Moment",
                    "Values Work"
                ])
            if TherapyType.ERP in profile.therapy_types:
                all_skills.extend([
                    "Exposure Tasks",
                    "Response Prevention",
                    "Anxiety Hierarchy",
                    "Ritual Prevention"
                ])
                
            self._add_symptom_checkboxes(skills_layout, all_skills)
            entry_layout.addWidget(skills_label, row, 0)
            entry_layout.addWidget(skills_frame, row, 1)
            row += 1
            
        # Notes section
        notes_label = QLabel("Notes:")
        notes_label.setFont(QFont("Arial", 12))
        notes_edit = QTextEdit()
        notes_edit.setFont(QFont("Arial", 12))
        notes_edit.setMinimumHeight(100)
        entry_layout.addWidget(notes_label, row, 0)
        entry_layout.addWidget(notes_edit, row, 1)
        
        layout.addWidget(entry_frame)
        
        # Add record button
        add_btn = QPushButton("Add Mood Record")
        add_btn.setFont(QFont("Arial", 12))
        add_btn.setMinimumHeight(40)
        layout.addWidget(add_btn)
        
        return tab
        
    def _add_symptom_checkboxes(self, layout: QGridLayout, symptoms: List[str], cols: int = 2):
        """Helper method to add symptom checkboxes to a layout."""
        for i, symptom in enumerate(symptoms):
            check = QCheckBox(symptom)
            check.setFont(QFont("Arial", 11))
            row = i // cols
            col = i % cols
            layout.addWidget(check, row, col)

    def _create_dbt_skills_tab(self) -> QWidget:
        """Create the DBT skills reference tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search DBT skills...")
        search_input.setFont(QFont("Arial", 12))
        search_btn = QPushButton("Search")
        search_btn.setFont(QFont("Arial", 12))
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Skills categories
        categories_frame = QFrame()
        categories_layout = QVBoxLayout(categories_frame)
        
        categories = {
            "Mindfulness": [
                "Observe",
                "Describe",
                "Participate",
                "Non-judgmentally",
                "One-mindfully",
                "Effectively"
            ],
            "Distress Tolerance": [
                "TIPP Skills",
                "STOP Skill",
                "Pros and Cons",
                "Radical Acceptance",
                "Self-Soothing"
            ],
            "Emotion Regulation": [
                "ABC PLEASE",
                "Check the Facts",
                "Opposite Action",
                "Problem Solving",
                "Build Mastery"
            ],
            "Interpersonal Effectiveness": [
                "DEAR MAN",
                "GIVE",
                "FAST",
                "Validation"
            ]
        }
        
        for category, skills in categories.items():
            group_box = QFrame()
            group_box.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
            group_layout = QVBoxLayout(group_box)
            
            # Category header
            header = QLabel(category)
            header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            group_layout.addWidget(header)
            
            # Skills list
            skills_list = QListWidget()
            skills_list.setFont(QFont("Arial", 12))
            skills_list.addItems(skills)
            skills_list.setMinimumHeight(len(skills) * 35)  # Adjust height based on number of items
            group_layout.addWidget(skills_list)
            
            categories_layout.addWidget(group_box)
        
        # Add categories to scrollable area
        scroll = QScrollArea()
        scroll.setWidget(categories_frame)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return tab
        
    def _create_task_manager_tab(self) -> QWidget:
        """Create the task manager tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Task filters section
        filters_frame = QFrame()
        filters_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(15)
        
        # Priority filter
        priority_label = QLabel("Priority:")
        priority_label.setFont(QFont("Arial", 12))
        priority_combo = QComboBox()
        priority_combo.setFont(QFont("Arial", 12))
        priority_combo.setMinimumWidth(150)
        priority_combo.addItems(["All"] + [p.name for p in TaskPriority])
        filters_layout.addWidget(priority_label)
        filters_layout.addWidget(priority_combo)
        
        # Category filter
        category_label = QLabel("Category:")
        category_label.setFont(QFont("Arial", 12))
        category_combo = QComboBox()
        category_combo.setFont(QFont("Arial", 12))
        category_combo.setMinimumWidth(150)
        category_combo.addItems(["All"] + [c.value for c in TaskCategory])
        filters_layout.addWidget(category_label)
        filters_layout.addWidget(category_combo)
        
        # Energy level filter
        energy_label = QLabel("Max Energy Required:")
        energy_label.setFont(QFont("Arial", 12))
        energy_spin = QSpinBox()
        energy_spin.setFont(QFont("Arial", 12))
        energy_spin.setRange(1, 5)
        energy_spin.setValue(5)
        filters_layout.addWidget(energy_label)
        filters_layout.addWidget(energy_spin)
        
        # Add task button
        add_task_btn = QPushButton("Add Task")
        add_task_btn.setFont(QFont("Arial", 12))
        add_task_btn.setMinimumSize(120, 40)
        add_task_btn.clicked.connect(self._show_add_task_dialog)
        filters_layout.addWidget(add_task_btn)
        
        layout.addWidget(filters_frame)
        
        # Tasks section
        tasks_frame = QFrame()
        tasks_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        tasks_layout = QVBoxLayout(tasks_frame)
        
        # Tasks header
        tasks_header = QLabel("Tasks")
        tasks_header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        tasks_layout.addWidget(tasks_header)
        
        # Tasks list
        self.tasks_list = QListWidget()
        self.tasks_list.setFont(QFont("Arial", 12))
        self.tasks_list.setMinimumHeight(400)
        self.tasks_list.itemChanged.connect(self._task_status_changed)
        tasks_layout.addWidget(self.tasks_list)
        
        layout.addWidget(tasks_frame)
        
        # Task details section
        details_frame = QFrame()
        details_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        details_layout = QGridLayout(details_frame)
        
        # Task details
        title_label = QLabel("Selected Task:")
        title_label.setFont(QFont("Arial", 12))
        self.task_title = QLabel()
        self.task_title.setFont(QFont("Arial", 12))
        
        priority_label = QLabel("Priority:")
        priority_label.setFont(QFont("Arial", 12))
        self.task_priority = QLabel()
        self.task_priority.setFont(QFont("Arial", 12))
        
        category_label = QLabel("Category:")
        category_label.setFont(QFont("Arial", 12))
        self.task_category = QLabel()
        self.task_category.setFont(QFont("Arial", 12))
        
        energy_label = QLabel("Energy Required:")
        energy_label.setFont(QFont("Arial", 12))
        self.task_energy = QLabel()
        self.task_energy.setFont(QFont("Arial", 12))
        
        # Add details to grid
        details_layout.addWidget(title_label, 0, 0)
        details_layout.addWidget(self.task_title, 0, 1)
        details_layout.addWidget(priority_label, 1, 0)
        details_layout.addWidget(self.task_priority, 1, 1)
        details_layout.addWidget(category_label, 2, 0)
        details_layout.addWidget(self.task_category, 2, 1)
        details_layout.addWidget(energy_label, 3, 0)
        details_layout.addWidget(self.task_energy, 3, 1)
        
        layout.addWidget(details_frame)
        
        # Update task list
        self._update_task_list()
        
        return tab
        
    def _create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Notification settings
        notif_frame = QFrame()
        notif_layout = QVBoxLayout(notif_frame)
        
        self.enable_notifications = QCheckBox("Enable Notifications")
        self.enable_sounds = QCheckBox("Enable Sounds")
        self.enable_animations = QCheckBox("Enable Animations")
        
        notif_layout.addWidget(self.enable_notifications)
        notif_layout.addWidget(self.enable_sounds)
        notif_layout.addWidget(self.enable_animations)
        
        layout.addWidget(notif_frame)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
        
        return tab
        
    def _create_file_organizer_tab(self) -> QWidget:
        """Create the file organizer tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # File management section
        manage_frame = QFrame()
        manage_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        manage_layout = QVBoxLayout(manage_frame)
        
        # File actions
        actions_layout = QHBoxLayout()
        
        import_btn = QPushButton("Import Files")
        import_btn.setFont(QFont("Arial", 12))
        import_btn.clicked.connect(self._import_files)
        
        organize_btn = QPushButton("Organize Files")
        organize_btn.setFont(QFont("Arial", 12))
        organize_btn.clicked.connect(self._organize_files)
        
        backup_btn = QPushButton("Create Backup")
        backup_btn.setFont(QFont("Arial", 12))
        backup_btn.clicked.connect(lambda: self.file_organizer.create_backup())
        
        actions_layout.addWidget(import_btn)
        actions_layout.addWidget(organize_btn)
        actions_layout.addWidget(backup_btn)
        manage_layout.addLayout(actions_layout)
        
        # Category view
        categories_label = QLabel("Categories:")
        categories_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        manage_layout.addWidget(categories_label)
        
        categories_list = QListWidget()
        categories_list.setFont(QFont("Arial", 12))
        
        # Add categories from profile
        for category, subfolders in self.profile_manager.current_profile.folder_structure.items():
            category_item = QListWidgetItem(category)
            category_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            categories_list.addItem(category_item)
            
            for subfolder in subfolders:
                subfolder_item = QListWidgetItem(f"  • {subfolder}")
                subfolder_item.setFont(QFont("Arial", 12))
                categories_list.addItem(subfolder_item)
                
        manage_layout.addWidget(categories_list)
        
        # Search section
        search_frame = QFrame()
        search_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        search_layout = QVBoxLayout(search_frame)
        
        search_label = QLabel("Search Files:")
        search_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        search_layout.addWidget(search_label)
        
        search_input = QLineEdit()
        search_input.setFont(QFont("Arial", 12))
        search_input.setPlaceholderText("Enter search term...")
        
        search_btn = QPushButton("Search")
        search_btn.setFont(QFont("Arial", 12))
        
        def perform_search():
            results = self.file_organizer.search_files(search_input.text())
            results_list.clear()
            for result in results:
                item = QListWidgetItem(str(result))
                item.setFont(QFont("Arial", 12))
                results_list.addItem(item)
                
        search_btn.clicked.connect(perform_search)
        
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        
        results_list = QListWidget()
        results_list.setFont(QFont("Arial", 12))
        search_layout.addWidget(results_list)
        
        # Add frames to layout
        layout.addWidget(manage_frame)
        layout.addWidget(search_frame)
        
        return tab
        
    def _add_task(self):
        """Add a new task."""
        title = self.task_input.text()
        if not title:
            return
            
        task = Task(
            title=title,
            priority=TaskPriority[self.priority_combo.currentText()],
            category=TaskCategory[self.category_combo.currentText()],
            energy_required=self.energy_spin.value()
        )
        
        self.task_manager.add_task(task)
        self._update_task_list()
        self.task_input.clear()
        
    def _update_task_list(self):
        """Update the task list display."""
        self.tasks_list.clear()
        for task in self.task_manager.get_tasks():
            item = QListWidgetItem(f"{task.title} ({task.priority.name}, Energy: {task.energy_required})")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if task.completed else Qt.CheckState.Unchecked)
            self.tasks_list.addItem(item)
            
    def _task_status_changed(self, item: QListWidgetItem):
        """Handle task status changes."""
        task_title = item.text().split(" (")[0]
        if item.checkState() == Qt.CheckState.Checked:
            self.task_manager.complete_task(task_title)
        self._update_task_list()
        
    def _add_energy_record(self):
        """Add a new energy record."""
        record = EnergyRecord(
            timestamp=datetime.now(),
            energy_level=self.energy_input.value(),
            mood=MoodLevel[self.mood_input.currentText().replace(" ", "_")],
            notes=self.notes_input.toPlainText() if self.notes_input.toPlainText() else None
        )
        
        self.energy_tracker.add_record(record)
        self._update_energy_pattern()
        self.notes_input.clear()
        
    def _update_energy_pattern(self):
        """Update the energy pattern display."""
        self.pattern_display.clear()
        pattern = self.energy_tracker.get_daily_pattern()
        
        for period, energy in pattern.items():
            self.pattern_display.addItem(f"{period}: {energy:.1f}%")
            
    def _energy_changed(self, value: int):
        """Handle energy level changes."""
        self._update_suggestions()
        
    def _mood_changed(self, mood: str):
        """Handle mood changes."""
        self._update_suggestions()
        
    def _update_suggestions(self):
        """Update task and break suggestions."""
        # Update task suggestions
        self.task_suggestions.clear()
        current_energy = self.energy_slider.value()
        for task in self.task_manager.get_task_suggestions(current_energy):
            self.task_suggestions.addItem(f"{task.title} (Energy: {task.energy_required})")
            
        # Update break suggestions
        self.break_suggestions.clear()
        for suggestion in self.energy_tracker.get_break_suggestions(current_energy):
            self.break_suggestions.addItem(suggestion)
            
    def _save_settings(self):
        """Save user settings."""
        settings = {
            "notifications": self.enable_notifications.isChecked(),
            "sounds": self.enable_sounds.isChecked(),
            "animations": self.enable_animations.isChecked(),
            "theme": self.theme_combo.currentText()
        }
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.data_dir / "settings.json", "w") as f:
            json.dump(settings, f, indent=2)
            
    def update_displays(self):
        """Update all dynamic displays."""
        self._update_task_list()
        self._update_energy_pattern()
        self._update_suggestions()
        
    def apply_theme(self, theme_name: str):
        """Apply the selected theme to the application."""
        if theme_name not in self.themes:
            return
            
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Create and apply stylesheet
        stylesheet = f"""
            QMainWindow {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QLabel {{
                color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['accent']};
                color: {theme['text']};
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {theme['accent']}CC;
            }}
            QComboBox {{
                background-color: {theme['background']};
                color: {theme['text']};
                border: 1px solid {theme['accent']};
                padding: 5px;
                border-radius: 3px;
            }}
            QTabWidget::pane {{
                border: 1px solid {theme['accent']};
                background-color: {theme['background']};
            }}
            QTabBar::tab {{
                background-color: {theme['background']};
                color: {theme['text']};
                padding: 8px 20px;
                border: 1px solid {theme['accent']};
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme['accent']};
            }}
            QListWidget {{
                background-color: {theme['background']};
                color: {theme['text']};
                border: 1px solid {theme['accent']};
                border-radius: 3px;
            }}
            QTextEdit {{
                background-color: {theme['background']};
                color: {theme['text']};
                border: 1px solid {theme['accent']};
                border-radius: 3px;
            }}
            QLineEdit {{
                background-color: {theme['background']};
                color: {theme['text']};
                border: 1px solid {theme['accent']};
                padding: 5px;
                border-radius: 3px;
            }}
            QProgressBar {{
                border: 1px solid {theme['accent']};
                border-radius: 3px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {theme['accent']};
            }}
        """
        self.setStyleSheet(stylesheet)

    def _show_add_task_dialog(self):
        """Show dialog for adding a new task."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Task")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # Task title
        title_label = QLabel("Task Title:")
        title_label.setFont(QFont("Arial", 12))
        title_input = QLineEdit()
        title_input.setFont(QFont("Arial", 12))
        title_input.setPlaceholderText("Enter task title...")
        layout.addWidget(title_label)
        layout.addWidget(title_input)
        
        # Priority selection
        priority_label = QLabel("Priority:")
        priority_label.setFont(QFont("Arial", 12))
        priority_combo = QComboBox()
        priority_combo.setFont(QFont("Arial", 12))
        priority_combo.addItems([p.name for p in TaskPriority])
        layout.addWidget(priority_label)
        layout.addWidget(priority_combo)
        
        # Category selection
        category_label = QLabel("Category:")
        category_label.setFont(QFont("Arial", 12))
        category_combo = QComboBox()
        category_combo.setFont(QFont("Arial", 12))
        category_combo.addItems([c.value for c in TaskCategory])
        layout.addWidget(category_label)
        layout.addWidget(category_combo)
        
        # Energy required
        energy_label = QLabel("Energy Required (1-5):")
        energy_label.setFont(QFont("Arial", 12))
        energy_spin = QSpinBox()
        energy_spin.setFont(QFont("Arial", 12))
        energy_spin.setRange(1, 5)
        layout.addWidget(energy_label)
        layout.addWidget(energy_spin)
        
        # Due date
        due_label = QLabel("Due Date (Optional):")
        due_label.setFont(QFont("Arial", 12))
        due_calendar = QCalendarWidget()
        due_calendar.setFont(QFont("Arial", 12))
        layout.addWidget(due_label)
        layout.addWidget(due_calendar)
        
        # Notes
        notes_label = QLabel("Notes (Optional):")
        notes_label.setFont(QFont("Arial", 12))
        notes_edit = QTextEdit()
        notes_edit.setFont(QFont("Arial", 12))
        notes_edit.setMaximumHeight(100)
        layout.addWidget(notes_label)
        layout.addWidget(notes_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task = Task(
                title=title_input.text(),
                priority=TaskPriority[priority_combo.currentText()],
                category=TaskCategory[category_combo.currentText()],  # Fixed syntax error
                energy_required=energy_spin.value(),
                due_date=due_calendar.selectedDate().toPyDate(),
                notes=notes_edit.toPlainText() if notes_edit.toPlainText() else None
            )
            self.task_manager.add_task(task)
            self._update_task_list()

    def _show_energy_dialog(self):
        """Show dialog for recording energy levels."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Track Energy")
        layout = QVBoxLayout(dialog)
        
        # Energy level input
        energy_label = QLabel("Energy Level (0-100):")
        energy_slider = QSlider(Qt.Orientation.Horizontal)
        energy_slider.setRange(0, 100)
        
        # Mood selection
        mood_label = QLabel("Current Mood:")
        mood_combo = QComboBox()
        mood_combo.addItems([mood.name.replace("_", " ") for mood in MoodLevel])
        
        # Notes
        notes_label = QLabel("Notes:")
        notes_input = QTextEdit()
        notes_input.setMaximumHeight(100)
        
        # Add record button
        add_record_btn = QPushButton("Add Record")
        add_record_btn.clicked.connect(dialog.accept)
        
        # Add widgets to layout
        layout.addWidget(energy_label)
        layout.addWidget(energy_slider)
        layout.addWidget(mood_label)
        layout.addWidget(mood_combo)
        layout.addWidget(notes_label)
        layout.addWidget(notes_input)
        layout.addWidget(add_record_btn)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            record = EnergyRecord(
                timestamp=datetime.now(),
                energy_level=energy_slider.value(),
                mood=MoodLevel[mood_combo.currentText().replace(" ", "_")],
                notes=notes_input.toPlainText() if notes_input.toPlainText() else None
            )
            self.energy_tracker.add_record(record)
            self._update_energy_pattern()
            self._update_suggestions()

    def _show_stats_dialog(self):
        """Show dialog with statistics and patterns."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Statistics")
        layout = QVBoxLayout(dialog)
        
        # Energy pattern
        pattern_label = QLabel("Daily Energy Pattern")
        pattern_label.setFont(QFont("Arial", 14))
        layout.addWidget(pattern_label)
        
        pattern_list = QListWidget()
        pattern = self.energy_tracker.get_daily_pattern()
        for period, energy in pattern.items():
            pattern_list.addItem(f"{period}: {energy:.1f}%")
        layout.addWidget(pattern_list)
        
        # Optimal work hours
        hours_label = QLabel("Optimal Work Hours")
        hours_label.setFont(QFont("Arial", 14))
        layout.addWidget(hours_label)
        
        hours_list = QListWidget()
        optimal_hours = self.energy_tracker.get_optimal_work_hours()
        for hour in optimal_hours:
            hours_list.addItem(f"{hour.strftime('%I:%M %p')}")
        layout.addWidget(hours_list)
        
        # Task completion stats
        stats_label = QLabel("Task Statistics")
        stats_label.setFont(QFont("Arial", 14))
        layout.addWidget(stats_label)
        
        total_tasks = len(self.task_manager.get_tasks())
        completed_tasks = len([t for t in self.task_manager.get_tasks() if t.completed])
        
        stats_text = f"""
        Total Tasks: {total_tasks}
        Completed Tasks: {completed_tasks}
        Completion Rate: {(completed_tasks/total_tasks*100 if total_tasks else 0):.1f}%
        """
        stats_info = QLabel(stats_text)
        layout.addWidget(stats_info)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def _show_mood_dialog(self):
        """Show dialog for recording mood and symptoms."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Track Mood")
        dialog.setMinimumWidth(600)
        layout = QVBoxLayout(dialog)
        
        # Time selection
        time_label = QLabel("Time:")
        time_label.setFont(QFont("Arial", 12))
        time_edit = QTimeEdit()
        time_edit.setFont(QFont("Arial", 12))
        time_edit.setTime(datetime.now().time())
        layout.addWidget(time_label)
        layout.addWidget(time_edit)
        
        # Mood selection
        mood_label = QLabel("Current Mood:")
        mood_label.setFont(QFont("Arial", 12))
        mood_combo = QComboBox()
        mood_combo.setFont(QFont("Arial", 12))
        mood_combo.addItems([
            "Euphoric (Mania)",
            "Extremely Elevated",
            "Elevated",
            "Slightly Elevated",
            "Stable",
            "Slightly Low",
            "Low",
            "Very Low",
            "Severely Depressed"
        ])
        layout.addWidget(mood_label)
        layout.addWidget(mood_combo)
        
        # Symptoms
        symptoms_label = QLabel("Current Symptoms:")
        symptoms_label.setFont(QFont("Arial", 12))
        symptoms_frame = QFrame()
        symptoms_layout = QGridLayout(symptoms_frame)
        
        symptoms = [
            "Racing Thoughts",
            "Decreased Need for Sleep",
            "Increased Energy",
            "Impulsivity",
            "Irritability",
            "Anxiety",
            "Depression",
            "Fatigue",
            "Difficulty Concentrating",
            "Sleep Problems"
        ]
        
        symptom_checks = {}
        row = 0
        col = 0
        for symptom in symptoms:
            check = QCheckBox(symptom)
            check.setFont(QFont("Arial", 11))
            symptoms_layout.addWidget(check, row, col)
            symptom_checks[symptom] = check
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        layout.addWidget(symptoms_label)
        layout.addWidget(symptoms_frame)
        
        # DBT skills used
        skills_label = QLabel("DBT Skills Used:")
        skills_label.setFont(QFont("Arial", 12))
        skills_frame = QFrame()
        skills_layout = QGridLayout(skills_frame)
        
        skills = [
            "Mindfulness",
            "Distress Tolerance",
            "Emotion Regulation",
            "Interpersonal Effectiveness",
            "PLEASE",
            "TIPP",
            "FAST",
            "GIVE"
        ]
        
        skill_checks = {}
        row = 0
        col = 0
        for skill in skills:
            check = QCheckBox(skill)
            check.setFont(QFont("Arial", 11))
            skills_layout.addWidget(check, row, col)
            skill_checks[skill] = check
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        layout.addWidget(skills_label)
        layout.addWidget(skills_frame)
        
        # Notes
        notes_label = QLabel("Notes:")
        notes_label.setFont(QFont("Arial", 12))
        notes_edit = QTextEdit()
        notes_edit.setFont(QFont("Arial", 12))
        notes_edit.setMinimumHeight(100)
        layout.addWidget(notes_label)
        layout.addWidget(notes_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save mood record
            active_symptoms = [s for s, c in symptom_checks.items() if c.isChecked()]
            active_skills = [s for s, c in skill_checks.items() if c.isChecked()]
            
            record = {
                'timestamp': datetime.combine(QDate.currentDate(), time_edit.time().toPyTime()),
                'mood': mood_combo.currentText(),
                'symptoms': active_symptoms,
                'skills_used': active_skills,
                'notes': notes_edit.toPlainText()
            }
            
            # TODO: Save record to database
            self._update_mood_displays()

    def _show_dbt_skills_dialog(self):
        """Show dialog with DBT skills reference and practice."""
        dialog = QDialog(self)
        dialog.setWindowTitle("DBT Skills")
        dialog.setMinimumSize(800, 600)
        layout = QVBoxLayout(dialog)
        
        # Tabs for different skill categories
        tabs = QTabWidget()
        tabs.setFont(QFont("Arial", 12))
        
        categories = {
            "Mindfulness": [
                ("What", "Observe, Describe, Participate"),
                ("How", "Non-judgmentally, One-mindfully, Effectively"),
                ("Practice", "Focus on your breath for 1 minute")
            ],
            "Distress Tolerance": [
                ("TIPP", "Temperature, Intense exercise, Paced breathing, Progressive muscle relaxation"),
                ("STOP", "Stop, Take a step back, Observe, Proceed mindfully"),
                ("Practice", "Hold an ice cube or take a cold shower")
            ],
            "Emotion Regulation": [
                ("ABC", "Accumulate positive experiences, Build mastery, Cope ahead"),
                ("PLEASE", "Treat PhysicaL illness, Eat balanced, Avoid mood-altering drugs, Sleep balanced, Exercise"),
                ("Practice", "List 3 things you're looking forward to")
            ],
            "Interpersonal": [
                ("DEAR MAN", "Describe, Express, Assert, Reinforce, Mindful, Appear confident, Negotiate"),
                ("GIVE", "Gentle, Interested, Validate, Easy manner"),
                ("Practice", "Role-play a difficult conversation")
            ]
        }
        
        for category, skills in categories.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            for title, description in skills:
                group = QFrame()
                group.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
                group_layout = QVBoxLayout(group)
                
                title_label = QLabel(title)
                title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                desc_label = QLabel(description)
                desc_label.setFont(QFont("Arial", 12))
                desc_label.setWordWrap(True)
                
                group_layout.addWidget(title_label)
                group_layout.addWidget(desc_label)
                tab_layout.addWidget(group)
            
            tabs.addTab(tab, category)
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def _update_mood_displays(self):
        """Update all mood-related displays."""
        # TODO: Implement mood history chart and statistics
        pass

    def _import_files(self):
        """Import files to be organized."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Import",
            str(Path.home()),
            "All Files (*.*)"
        )
        
        if files:
            for file_path in files:
                src_path = Path(file_path)
                if src_path.exists():
                    self.file_organizer.categorize_file(src_path)
                    
            # Update the file organizer tab
            self.tabs.setCurrentWidget(self._create_file_organizer_tab())
            
    def _organize_files(self):
        """Organize files in the selected directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Organize",
            str(Path.home())
        )
        
        if dir_path:
            src_dir = Path(dir_path)
            if src_dir.exists():
                for file_path in src_dir.glob("*"):
                    if file_path.is_file():
                        self.file_organizer.categorize_file(file_path)
                        
            # Update the file organizer tab
            self.tabs.setCurrentWidget(self._create_file_organizer_tab())

    def _update_system_state(self):
        """Update system status displays with AI analysis."""
        try:
            # Get system stats with AI analysis
            stats = self.ai_optimizer.get_system_stats()
            
            # Update progress bars
            self.cpu_progress.setValue(int(stats['cpu_percent']))
            self.memory_progress.setValue(int(stats['memory_percent']))
            self.disk_progress.setValue(int(stats['disk_percent']))
            
            if stats.get('battery_percent') is not None:
                self.battery_progress.setValue(int(stats['battery_percent']))
                self.battery_progress.setVisible(True)
                self.battery_label.setVisible(True)
            else:
                self.battery_progress.setVisible(False)
                self.battery_label.setVisible(False)
                
            # Update anomaly score
            anomaly_score = int(stats['anomaly_score'] * 100)  # Convert to percentage
            self.anomaly_progress.setValue(anomaly_score)
            
            # Update AI suggestions
            suggestions = self.ai_optimizer.get_ai_suggestions()
            self.system_suggestions.setText("\n".join(suggestions))
            
        except Exception as e:
            logging.error(f"Error updating system state: {str(e)}")
            
    def _optimize_system(self):
        """Run AI-powered system optimization."""
        try:
            actions = self.ai_optimizer.optimize_system()
            self.system_suggestions.setText("AI Optimization complete!\n\n" + "\n".join(actions))
        except Exception as e:
            logging.error(f"Error optimizing system: {str(e)}")
            self.system_suggestions.setText(f"Error during optimization: {str(e)}")
