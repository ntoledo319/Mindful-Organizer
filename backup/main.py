#!/usr/bin/env python3
"""
Mindful Organizer - macOS Edition
A supportive tool for ADHD and anxiety management through mindful organization.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTabWidget, 
                            QListWidget, QTextEdit, QLineEdit, QCalendarWidget,
                            QProgressBar, QScrollArea, QFrame, QCheckBox,
                            QSpacerItem, QSizePolicy, QGroupBox, QComboBox,
                            QTimeEdit, QDialog, QDialogButtonBox, QSystemTrayIcon, QMenu, QMessageBox,
                            QSpinBox, QDateEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
import psutil
from mindful_organizer.core.ai_optimizer import AISystemOptimizer
from mindful_organizer.core.mindfulness_manager import MindfulnessManager
from mindful_organizer.core.mental_health_guide import MentalHealthGuide
from mindful_organizer.core.system_recognition import SystemRecognition

class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Task")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Task name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Task name")
        layout.addWidget(self.name_edit)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Urgent"])
        layout.addWidget(self.priority_combo)
        
        # Energy level
        self.energy_combo = QComboBox()
        self.energy_combo.addItems(["Low Energy", "Medium Energy", "High Energy"])
        layout.addWidget(self.energy_combo)
        
        # Time estimate
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        layout.addWidget(self.time_edit)
        
        # Due date
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Additional notes...")
        layout.addWidget(self.notes_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mindful Organizer")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize components
        self.data_dir = Path.home() / ".mindful_organizer"
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize all managers
        self.optimizer = AISystemOptimizer(self.data_dir)
        self.mindfulness = MindfulnessManager(self.data_dir)
        self.mental_health_guide = MentalHealthGuide(self.data_dir)
        self.system_recognition = SystemRecognition(self.data_dir)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Add all tabs
        tabs.addTab(self._create_dashboard_tab(), "Dashboard")
        tabs.addTab(self._create_task_manager_tab(), "Task Manager")
        tabs.addTab(self._create_mindfulness_tab(), "Mindfulness")
        tabs.addTab(self._create_optimization_tab(), "System Optimization")
        tabs.addTab(self._create_energy_tab(), "Energy Tracking")
        tabs.addTab(self._create_anxiety_tab(), "Anxiety Support")
        tabs.addTab(self._create_routines_tab(), "Daily Routines")
        tabs.addTab(self._create_mental_health_tab(), "Mental Health Guide")
        tabs.addTab(self._create_system_recognition_tab(), "System Recognition")
        tabs.addTab(self._create_meditation_tab(), "Meditation")
        tabs.addTab(self._create_gratitude_tab(), "Gratitude")
        tabs.addTab(self._create_journal_tab(), "Journal")
        tabs.addTab(self._create_settings_tab(), "Settings")
        
        # Create system tray
        self._create_system_tray()
        
        # Start update timers
        self._start_timers()

    def _create_dashboard_tab(self):
        """Create dashboard with both mindfulness and system stats."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Mindfulness Summary
        mindful_group = QGroupBox("Mindfulness Overview")
        mindful_layout = QVBoxLayout(mindful_group)
        
        self.mindful_summary = QLabel()
        self.breathing_timer = QLabel()
        self.next_break = QLabel()
        
        mindful_layout.addWidget(self.mindful_summary)
        mindful_layout.addWidget(self.breathing_timer)
        mindful_layout.addWidget(self.next_break)
        
        # System Stats
        stats_group = QGroupBox("System Health")
        stats_layout = QGridLayout(stats_group)
        
        self.cpu_bar = QProgressBar()
        self.memory_bar = QProgressBar()
        self.disk_bar = QProgressBar()
        
        stats_layout.addWidget(QLabel("CPU Usage:"), 0, 0)
        stats_layout.addWidget(self.cpu_bar, 0, 1)
        stats_layout.addWidget(QLabel("Memory Usage:"), 1, 0)
        stats_layout.addWidget(self.memory_bar, 1, 1)
        stats_layout.addWidget(QLabel("Disk Usage:"), 2, 0)
        stats_layout.addWidget(self.disk_bar, 2, 1)
        
        layout.addWidget(mindful_group)
        layout.addWidget(stats_group)
        layout.addStretch()
        
        return tab

    def _create_mindfulness_tab(self):
        """Create mindfulness features tab with comprehensive mental health tracking."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Mood and Anxiety Tracking
        tracking_group = QGroupBox("Mood & Anxiety Tracking")
        tracking_layout = QGridLayout(tracking_group)
        
        # Mood tracking
        mood_label = QLabel("Current Mood:")
        self.mood_combo = QComboBox()
        for mood in MoodLevel:
            self.mood_combo.addItem(mood.name)
        self.mood_notes = QTextEdit()
        self.mood_notes.setPlaceholderText("Add notes about your mood...")
        self.log_mood_btn = QPushButton("Log Mood")
        self.log_mood_btn.clicked.connect(self._log_mood)
        
        tracking_layout.addWidget(mood_label, 0, 0)
        tracking_layout.addWidget(self.mood_combo, 0, 1)
        tracking_layout.addWidget(self.mood_notes, 1, 0, 1, 2)
        tracking_layout.addWidget(self.log_mood_btn, 2, 0, 1, 2)
        
        # Anxiety tracking
        anxiety_label = QLabel("Anxiety Level:")
        self.anxiety_combo = QComboBox()
        for anxiety in AnxietyLevel:
            self.anxiety_combo.addItem(anxiety.name)
        self.anxiety_triggers = QLineEdit()
        self.anxiety_triggers.setPlaceholderText("Enter triggers (comma-separated)")
        self.log_anxiety_btn = QPushButton("Log Anxiety")
        self.log_anxiety_btn.clicked.connect(self._log_anxiety)
        
        tracking_layout.addWidget(anxiety_label, 3, 0)
        tracking_layout.addWidget(self.anxiety_combo, 3, 1)
        tracking_layout.addWidget(self.anxiety_triggers, 4, 0, 1, 2)
        tracking_layout.addWidget(self.log_anxiety_btn, 5, 0, 1, 2)
        
        # Journaling
        journal_group = QGroupBox("Daily Journal")
        journal_layout = QVBoxLayout(journal_group)
        
        self.journal_entry = QTextEdit()
        self.journal_entry.setPlaceholderText("Write your thoughts...")
        self.save_journal_btn = QPushButton("Save Entry")
        self.save_journal_btn.clicked.connect(self._save_journal_entry)
        
        journal_layout.addWidget(self.journal_entry)
        journal_layout.addWidget(self.save_journal_btn)
        
        # Gratitude Practice
        gratitude_group = QGroupBox("Gratitude Practice")
        gratitude_layout = QVBoxLayout(gratitude_group)
        
        self.gratitude_entry = QLineEdit()
        self.gratitude_entry.setPlaceholderText("What are you grateful for today?")
        self.add_gratitude_btn = QPushButton("Add Gratitude")
        self.add_gratitude_btn.clicked.connect(self._add_gratitude)
        self.gratitude_list = QListWidget()
        
        gratitude_layout.addWidget(self.gratitude_entry)
        gratitude_layout.addWidget(self.add_gratitude_btn)
        gratitude_layout.addWidget(self.gratitude_list)
        
        # Meditation
        meditation_group = QGroupBox("Meditation")
        meditation_layout = QVBoxLayout(meditation_group)
        
        self.meditation_combo = QComboBox()
        for guide in self.mindfulness.meditation_guides:
            self.meditation_combo.addItem(f"{guide['name']} ({guide['duration']} min)")
        
        self.start_meditation_btn = QPushButton("Start Meditation")
        self.start_meditation_btn.clicked.connect(self._start_meditation)
        self.meditation_timer = QLabel("0:00")
        
        meditation_layout.addWidget(self.meditation_combo)
        meditation_layout.addWidget(self.start_meditation_btn)
        meditation_layout.addWidget(self.meditation_timer)
        
        # Coping Strategies
        coping_group = QGroupBox("Coping Strategies")
        coping_layout = QVBoxLayout(coping_group)
        
        self.strategy_type = QComboBox()
        self.strategy_type.addItems(["All", "Anxiety", "Stress", "General"])
        self.get_strategy_btn = QPushButton("Get Coping Strategy")
        self.get_strategy_btn.clicked.connect(self._get_coping_strategy)
        self.current_strategy = QLabel("Click to get a coping strategy...")
        
        coping_layout.addWidget(self.strategy_type)
        coping_layout.addWidget(self.get_strategy_btn)
        coping_layout.addWidget(self.current_strategy)
        
        # Daily Affirmation
        affirmation_group = QGroupBox("Daily Affirmation")
        affirmation_layout = QVBoxLayout(affirmation_group)
        
        self.current_affirmation = QLabel("Your daily affirmation will appear here...")
        self.current_affirmation.setWordWrap(True)
        self.new_affirmation_btn = QPushButton("New Affirmation")
        self.new_affirmation_btn.clicked.connect(lambda: self.mindfulness.set_daily_affirmation())
        
        affirmation_layout.addWidget(self.current_affirmation)
        affirmation_layout.addWidget(self.new_affirmation_btn)
        
        # Breathing Exercises (enhanced)
        breathing_group = QGroupBox("Breathing Exercises")
        breathing_layout = QVBoxLayout(breathing_group)
        
        self.breathing_combo = QComboBox()
        for exercise in self.mindfulness.breathing_exercises:
            self.breathing_combo.addItem(exercise["name"])
        
        self.breathing_label = QLabel("Take a mindful breath...")
        self.breathing_progress = QProgressBar()
        self.start_breathing_btn = QPushButton("Start Breathing Exercise")
        self.start_breathing_btn.clicked.connect(self._start_breathing)
        
        breathing_layout.addWidget(self.breathing_combo)
        breathing_layout.addWidget(self.breathing_label)
        breathing_layout.addWidget(self.breathing_progress)
        breathing_layout.addWidget(self.start_breathing_btn)
        
        # Add all groups to main layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        scroll_layout.addWidget(tracking_group)
        scroll_layout.addWidget(journal_group)
        scroll_layout.addWidget(gratitude_group)
        scroll_layout.addWidget(meditation_group)
        scroll_layout.addWidget(coping_group)
        scroll_layout.addWidget(affirmation_group)
        scroll_layout.addWidget(breathing_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return tab
        
    def _log_mood(self):
        """Log current mood with notes."""
        mood = MoodLevel[self.mood_combo.currentText()]
        notes = self.mood_notes.toPlainText()
        self.mindfulness.log_mood(mood, notes)
        self.mood_notes.clear()
        
    def _log_anxiety(self):
        """Log anxiety level with triggers."""
        anxiety = AnxietyLevel[self.anxiety_combo.currentText()]
        triggers = [t.strip() for t in self.anxiety_triggers.text().split(",") if t.strip()]
        self.mindfulness.log_anxiety(anxiety, triggers)
        self.anxiety_triggers.clear()
        
    def _save_journal_entry(self):
        """Save journal entry."""
        content = self.journal_entry.toPlainText()
        if content:
            self.mindfulness.add_journal_entry(content)
            self.journal_entry.clear()
        
    def _add_gratitude(self):
        """Add gratitude item."""
        item = self.gratitude_entry.text()
        if item:
            self.mindfulness.add_gratitude(item)
            self.gratitude_entry.clear()
            self.gratitude_list.addItem(item)
        
    def _start_meditation(self):
        """Start meditation session."""
        guide = self.mindfulness.meditation_guides[self.meditation_combo.currentIndex()]
        self.mindfulness.start_meditation(guide["duration"], guide["type"])
        
    def _get_coping_strategy(self):
        """Get and display coping strategy."""
        strategy_type = self.strategy_type.currentText().lower()
        if strategy_type == "all":
            strategy_type = None
        strategy = self.mindfulness.get_coping_strategy(strategy_type)
        self.current_strategy.setText(f"{strategy['name']}")
        
    def _start_breathing(self):
        """Start breathing exercise."""
        exercise_name = self.breathing_combo.currentText()
        self.mindfulness.start_breathing_exercise(exercise_name)

    def _create_optimization_tab(self):
        """Create the system optimization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Mode selection
        modes_group = QWidget()
        modes_layout = QHBoxLayout(modes_group)
        
        performance_btn = QPushButton("⚡ Performance Mode")
        performance_btn.clicked.connect(lambda: self._set_optimization_mode('performance'))
        modes_layout.addWidget(performance_btn)
        
        balanced_btn = QPushButton("⚖️ Balanced Mode")
        balanced_btn.clicked.connect(lambda: self._set_optimization_mode('balanced'))
        modes_layout.addWidget(balanced_btn)
        
        power_saving_btn = QPushButton("🌙 Power Saving Mode")
        power_saving_btn.clicked.connect(lambda: self._set_optimization_mode('power_saving'))
        modes_layout.addWidget(power_saving_btn)
        
        layout.addWidget(modes_group)
        
        # Resource monitoring
        monitoring_group = QWidget()
        monitoring_layout = QVBoxLayout(monitoring_group)
        
        self.resource_text = QTextEdit()
        self.resource_text.setReadOnly(True)
        monitoring_layout.addWidget(self.resource_text)
        
        layout.addWidget(monitoring_group)
        
        # Optimization history
        history_group = QWidget()
        history_layout = QVBoxLayout(history_group)
        
        history_label = QLabel("Optimization History")
        history_layout.addWidget(history_label)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        history_layout.addWidget(self.history_text)
        
        layout.addWidget(history_group)
        
        return tab
        
    def _create_settings_tab(self):
        """Create the settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Optimization settings
        optimization_group = QWidget()
        optimization_layout = QVBoxLayout(optimization_group)
        
        optimization_label = QLabel("Optimization Settings")
        optimization_layout.addWidget(optimization_label)
        
        # Add optimization settings controls here
        
        layout.addWidget(optimization_group)
        
        # Mindfulness settings
        mindfulness_group = QWidget()
        mindfulness_layout = QVBoxLayout(mindfulness_group)
        
        mindfulness_label = QLabel("Mindfulness Settings")
        mindfulness_layout.addWidget(mindfulness_label)
        
        # Add mindfulness settings controls here
        
        layout.addWidget(mindfulness_group)
        
        return tab
        
    def _create_task_manager_tab(self):
        """Create the task manager tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Task Categories
        categories_group = QGroupBox("Task Categories")
        categories_layout = QHBoxLayout(categories_group)
        
        for category in ["All Tasks", "High Priority", "Medium Priority", "Low Priority", "Completed"]:
            btn = QPushButton(category)
            categories_layout.addWidget(btn)
            
        layout.addWidget(categories_group)
        
        # Task List
        tasks_group = QGroupBox("Tasks")
        tasks_layout = QVBoxLayout(tasks_group)
        
        self.task_list = QListWidget()
        tasks_layout.addWidget(self.task_list)
        
        # Task Controls
        controls = QHBoxLayout()
        add_btn = QPushButton("Add Task")
        add_btn.clicked.connect(self.show_add_task_dialog)
        edit_btn = QPushButton("Edit Task")
        delete_btn = QPushButton("Delete Task")
        
        for btn in [add_btn, edit_btn, delete_btn]:
            controls.addWidget(btn)
            
        tasks_layout.addLayout(controls)
        layout.addWidget(tasks_group)
        
        return tab
        
    def _create_energy_tab(self):
        """Create the energy tracking tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Current Energy
        energy_group = QGroupBox("Current Energy Level")
        energy_layout = QVBoxLayout(energy_group)
        
        energy_slider = QProgressBar()
        energy_slider.setMinimum(0)
        energy_slider.setMaximum(100)
        energy_slider.setValue(70)
        energy_layout.addWidget(energy_slider)
        
        energy_buttons = QHBoxLayout()
        for level in ["Low", "Medium", "High"]:
            btn = QPushButton(level)
            energy_buttons.addWidget(btn)
        energy_layout.addLayout(energy_buttons)
        
        layout.addWidget(energy_group)
        
        # Energy History
        history_group = QGroupBox("Energy History")
        history_layout = QVBoxLayout(history_group)
        
        # Placeholder for energy history graph
        history_placeholder = QLabel("Energy level history graph will be displayed here")
        history_layout.addWidget(history_placeholder)
        
        layout.addWidget(history_group)
        
        # Task Suggestions
        suggestions_group = QGroupBox("Task Suggestions for Current Energy Level")
        suggestions_layout = QVBoxLayout(suggestions_group)
        
        self.suggestions_list = QListWidget()
        suggestions_layout.addWidget(self.suggestions_list)
        
        layout.addWidget(suggestions_group)
        
        return tab
        
    def _create_anxiety_tab(self):
        """Create the anxiety support tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Anxiety Check-in
        checkin_group = QGroupBox("Anxiety Check-in")
        checkin_layout = QVBoxLayout(checkin_group)
        
        anxiety_label = QLabel("How are you feeling right now?")
        checkin_layout.addWidget(anxiety_label)
        
        anxiety_buttons = QHBoxLayout()
        for level in ["Calm", "Slight", "Moderate", "High"]:
            btn = QPushButton(level)
            anxiety_buttons.addWidget(btn)
        checkin_layout.addLayout(anxiety_buttons)
        
        layout.addWidget(checkin_group)
        
        # Coping Strategies
        coping_group = QGroupBox("Coping Strategies")
        coping_layout = QVBoxLayout(coping_group)
        
        strategies_list = QListWidget()
        strategies = [
            "Take 5 deep breaths",
            "Go for a short walk",
            "Write down your thoughts",
            "Progressive muscle relaxation",
            "5-4-3-2-1 grounding exercise"
        ]
        strategies_list.addItems(strategies)
        coping_layout.addWidget(strategies_list)
        
        layout.addWidget(coping_group)
        
        # Anxiety Journal
        journal_group = QGroupBox("Anxiety Journal")
        journal_layout = QVBoxLayout(journal_group)
        
        self.journal_entry = QTextEdit()
        self.journal_entry.setPlaceholderText("Write about what's on your mind...")
        journal_layout.addWidget(self.journal_entry)
        
        save_entry = QPushButton("Save Entry")
        journal_layout.addWidget(save_entry)
        
        layout.addWidget(journal_group)
        
        return tab
        
    def _create_routines_tab(self):
        """Create the daily routines tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Morning Routine
        morning_group = QGroupBox("Morning Routine")
        morning_layout = QVBoxLayout(morning_group)
        
        self.morning_list = QListWidget()
        morning_layout.addWidget(self.morning_list)
        
        morning_controls = QHBoxLayout()
        add_morning = QPushButton("Add Step")
        edit_morning = QPushButton("Edit Step")
        morning_controls.addWidget(add_morning)
        morning_controls.addWidget(edit_morning)
        morning_layout.addLayout(morning_controls)
        
        layout.addWidget(morning_group)
        
        # Evening Routine
        evening_group = QGroupBox("Evening Routine")
        evening_layout = QVBoxLayout(evening_group)
        
        self.evening_list = QListWidget()
        evening_layout.addWidget(self.evening_list)
        
        evening_controls = QHBoxLayout()
        add_evening = QPushButton("Add Step")
        edit_evening = QPushButton("Edit Step")
        evening_controls.addWidget(add_evening)
        evening_controls.addWidget(edit_evening)
        evening_layout.addLayout(evening_controls)
        
        layout.addWidget(evening_group)
        
        return tab
        
    def _create_mental_health_tab(self):
        """Create mental health guidance tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Crisis Resources
        crisis_group = QGroupBox("Crisis Resources")
        crisis_layout = QVBoxLayout(crisis_group)
        
        resources = self.mental_health_guide.get_crisis_resources()
        for name, number in resources.items():
            label = QLabel(f"{name.replace('_', ' ').title()}: {number}")
            crisis_layout.addWidget(label)
        
        # Guided Interventions
        intervention_group = QGroupBox("Guided Interventions")
        intervention_layout = QVBoxLayout(intervention_group)
        
        self.intervention_text = QTextEdit()
        self.intervention_text.setReadOnly(True)
        intervention_layout.addWidget(self.intervention_text)
        
        # Therapeutic Exercises
        exercise_group = QGroupBox("Therapeutic Exercises")
        exercise_layout = QVBoxLayout(exercise_group)
        
        self.exercise_combo = QComboBox()
        self.exercise_combo.addItems(["Cognitive Restructuring", "Emotional Regulation"])
        
        self.exercise_text = QTextEdit()
        self.exercise_text.setReadOnly(True)
        
        exercise_layout.addWidget(self.exercise_combo)
        exercise_layout.addWidget(self.exercise_text)
        
        # Pattern Analysis
        pattern_group = QGroupBox("Pattern Analysis")
        pattern_layout = QVBoxLayout(pattern_group)
        
        self.pattern_text = QTextEdit()
        self.pattern_text.setReadOnly(True)
        pattern_layout.addWidget(self.pattern_text)
        
        # Add all groups
        layout.addWidget(crisis_group)
        layout.addWidget(intervention_group)
        layout.addWidget(exercise_group)
        layout.addWidget(pattern_group)
        
        return tab
        
    def _create_system_recognition_tab(self):
        """Create system recognition and analysis tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Usage Patterns
        patterns_group = QGroupBox("System Usage Patterns")
        patterns_layout = QVBoxLayout(patterns_group)
        
        self.patterns_text = QTextEdit()
        self.patterns_text.setReadOnly(True)
        patterns_layout.addWidget(self.patterns_text)
        
        # App Usage
        apps_group = QGroupBox("Application Usage")
        apps_layout = QVBoxLayout(apps_group)
        
        self.apps_list = QListWidget()
        apps_layout.addWidget(self.apps_list)
        
        # Recommendations
        recommendations_group = QGroupBox("Recommendations")
        recommendations_layout = QVBoxLayout(recommendations_group)
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        recommendations_layout.addWidget(self.recommendations_text)
        
        # Add all groups
        layout.addWidget(patterns_group)
        layout.addWidget(apps_group)
        layout.addWidget(recommendations_group)
        
        return tab

    def _create_meditation_tab(self):
        """Create meditation features tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Meditation Timer
        timer_group = QGroupBox("Meditation Timer")
        timer_layout = QVBoxLayout(timer_group)
        
        self.meditation_time = QSpinBox()
        self.meditation_time.setRange(1, 120)
        self.meditation_time.setValue(10)
        self.meditation_time.setSuffix(" minutes")
        
        self.meditation_timer_label = QLabel("00:00")
        self.meditation_timer_label.setAlignment(Qt.AlignCenter)
        self.meditation_timer_label.setStyleSheet("font-size: 48px;")
        
        start_meditation = QPushButton("Start Meditation")
        start_meditation.clicked.connect(self._start_meditation)
        
        timer_layout.addWidget(self.meditation_time)
        timer_layout.addWidget(self.meditation_timer_label)
        timer_layout.addWidget(start_meditation)
        
        # Meditation Guides
        guides_group = QGroupBox("Meditation Guides")
        guides_layout = QVBoxLayout(guides_group)
        
        self.guide_list = QListWidget()
        self.guide_list.addItems([
            "Mindful Breathing",
            "Body Scan",
            "Loving-Kindness",
            "Walking Meditation",
            "Mindful Observation",
            "Sound Meditation"
        ])
        
        guides_layout.addWidget(self.guide_list)
        
        # Progress Tracking
        progress_group = QGroupBox("Meditation Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.meditation_calendar = QCalendarWidget()
        self.meditation_stats = QLabel("Total Sessions: 0\nTotal Minutes: 0")
        
        progress_layout.addWidget(self.meditation_calendar)
        progress_layout.addWidget(self.meditation_stats)
        
        # Add all groups
        layout.addWidget(timer_group)
        layout.addWidget(guides_group)
        layout.addWidget(progress_group)
        
        return tab

    def _create_gratitude_tab(self):
        """Create gratitude practice tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Daily Gratitude
        daily_group = QGroupBox("Daily Gratitude")
        daily_layout = QVBoxLayout(daily_group)
        
        self.gratitude_edit = QTextEdit()
        self.gratitude_edit.setPlaceholderText("What are you grateful for today?")
        
        add_gratitude = QPushButton("Add Gratitude")
        add_gratitude.clicked.connect(self._add_gratitude)
        
        daily_layout.addWidget(self.gratitude_edit)
        daily_layout.addWidget(add_gratitude)
        
        # Gratitude List
        list_group = QGroupBox("Gratitude Journal")
        list_layout = QVBoxLayout(list_group)
        
        self.gratitude_list = QListWidget()
        list_layout.addWidget(self.gratitude_list)
        
        # Gratitude Prompts
        prompts_group = QGroupBox("Gratitude Prompts")
        prompts_layout = QVBoxLayout(prompts_group)
        
        self.prompt_label = QLabel("Today's Prompt: What made you smile today?")
        next_prompt = QPushButton("Next Prompt")
        
        prompts_layout.addWidget(self.prompt_label)
        prompts_layout.addWidget(next_prompt)
        
        # Add all groups
        layout.addWidget(daily_group)
        layout.addWidget(list_group)
        layout.addWidget(prompts_group)
        
        return tab

    def _create_journal_tab(self):
        """Create journaling tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Journal Entry
        entry_group = QGroupBox("New Journal Entry")
        entry_layout = QVBoxLayout(entry_group)
        
        self.journal_date = QDateEdit()
        self.journal_date.setDate(QDate.currentDate())
        
        self.journal_mood = QComboBox()
        self.journal_mood.addItems(["😊 Happy", "😐 Neutral", "😢 Sad", "😠 Angry", "😨 Anxious"])
        
        self.journal_edit = QTextEdit()
        self.journal_edit.setPlaceholderText("Write your thoughts here...")
        
        save_entry = QPushButton("Save Entry")
        save_entry.clicked.connect(self._save_journal_entry)
        
        entry_layout.addWidget(self.journal_date)
        entry_layout.addWidget(self.journal_mood)
        entry_layout.addWidget(self.journal_edit)
        entry_layout.addWidget(save_entry)
        
        # Journal History
        history_group = QGroupBox("Journal History")
        history_layout = QVBoxLayout(history_group)
        
        self.journal_list = QListWidget()
        self.journal_view = QTextEdit()
        self.journal_view.setReadOnly(True)
        
        history_layout.addWidget(self.journal_list)
        history_layout.addWidget(self.journal_view)
        
        # Add all groups
        layout.addWidget(entry_group)
        layout.addWidget(history_group)
        
        return tab

    def _setup_system_tray(self):
        """Setup system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(QIcon("path_to_icon.png"))  # Add icon path
        
        # Create tray menu
        tray_menu = QMenu()
        
        optimize_action = tray_menu.addAction("Optimize System")
        optimize_action.triggered.connect(self._optimize_system)
        
        show_action = tray_menu.addAction("Show Window")
        show_action.triggered.connect(self.show)
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def _start_timers(self):
        """Start timers for system stats and mindfulness updates."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_stats)
        self.update_timer.start(1000)  # Update every second
        
        self.mindfulness_timer = QTimer()
        self.mindfulness_timer.timeout.connect(self.mindfulness.update)
        self.mindfulness_timer.start(60000)  # Update every minute
        
    def _update_stats(self):
        """Update all stats and analysis."""
        # Update system stats
        metrics = self.optimizer.resource_monitor.get_metrics()
        
        # Update progress bars
        self.cpu_bar.setValue(int(metrics.cpu_usage))
        self.memory_bar.setValue(int(metrics.memory_usage))
        self.disk_bar.setValue(int(metrics.io_usage))
        
        # Track system usage
        self.system_recognition.track_system_usage({
            "cpu_percent": metrics.cpu_usage,
            "memory_percent": metrics.memory_usage,
            "disk_percent": metrics.io_usage,
            "network_usage": metrics.network_usage
        })
        
        # Update pattern analysis
        patterns = self.system_recognition.analyze_patterns()
        if patterns:
            pattern_text = ""
            for pattern in patterns:
                pattern_text += f"Pattern: {pattern.pattern_type}\n"
                pattern_text += f"Impact: {pattern.impact}\n"
                pattern_text += f"Recommendations:\n"
                for rec in pattern.recommendations:
                    pattern_text += f"- {rec}\n"
                pattern_text += "\n"
            self.pattern_text.setText(pattern_text)
        
        # Update recommendations
        recommendations = self.system_recognition.get_recommendations()
        self.recommendations_text.setText("\n".join(f"• {rec}" for rec in recommendations))
        
        # Update app usage
        usage_summary = self.system_recognition.get_usage_summary()
        self.apps_list.clear()
        if "most_used_apps" in usage_summary:
            for app, usage in usage_summary["most_used_apps"]:
                self.apps_list.addItem(f"{app}: {usage['total_time']/60:.1f} minutes")
                
        # Update mental health patterns
        mood_data = self.mindfulness.mood_history if hasattr(self.mindfulness, 'mood_history') else []
        anxiety_data = self.mindfulness.anxiety_history if hasattr(self.mindfulness, 'anxiety_history') else []
        
        patterns = self.mental_health_guide.analyze_patterns(mood_data, anxiety_data)
        if patterns:
            for pattern in patterns:
                intervention = self.mental_health_guide.get_guided_intervention(pattern)
                if intervention:
                    self.intervention_text.setText(
                        f"Recommended Intervention:\n"
                        f"• {intervention['immediate_steps']['name']}\n"
                        f"• Duration: {intervention['immediate_steps']['duration']}\n"
                        f"\nSteps:\n" + 
                        "\n".join(f"• {step}" for step in intervention['immediate_steps']['steps'])
                    )
        
    def _optimize_system(self):
        """Run system optimization."""
        actions = self.optimizer.optimize_system()
        
        # Update suggestions text
        self.suggestions_text.setText("\n".join(actions))
        
        # Add to history
        current_history = self.history_text.toPlainText()
        self.history_text.setText(f"[{datetime.now().strftime('%H:%M:%S')}] Optimization performed:\n" +
                                "\n".join(actions) + "\n\n" + current_history)
        
    def _set_optimization_mode(self, mode: str):
        """Set the optimization mode."""
        self.optimization_label.setText(f"Current Optimization Mode: {mode.title()}")
        self._optimize_system()
        
    def closeEvent(self, event):
        """Handle window close event."""
        event.ignore()
        self.hide()
        
    def show_add_task_dialog(self):
        """Show dialog for adding a new task."""
        dialog = TaskDialog(self)
        if dialog.exec():
            task_name = dialog.name_edit.text()
            priority = dialog.priority_combo.currentText()
            energy = dialog.energy_combo.currentText()
            due_date = dialog.calendar.selectedDate().toString()
            notes = dialog.notes_edit.toPlainText()
            
            task_text = f"{task_name} - {priority} - {energy} - Due: {due_date}"
            self.tasks_list.addItem(task_text)
            self.task_list.addItem(task_text)
        
def main():
    """Main application entry point."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
