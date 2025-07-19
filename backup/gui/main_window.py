#!/usr/bin/env python3

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTabWidget, QListWidget, QTextEdit, QLineEdit,
    QCalendarWidget, QProgressBar, QScrollArea, QFrame,
    QCheckBox, QComboBox, QSpinBox, QTimeEdit, QDialog,
    QDialogButtonBox, QSystemTrayIcon, QMenu, QMessageBox,
    QDateEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from mindful_organizer.core.ai_optimizer import AISystemOptimizer
from mindful_organizer.core.energy_tracker import EnergyTracker
from mindful_organizer.core.file_organizer import FileOrganizer
from mindful_organizer.core.mental_health_guide import MentalHealthGuide
from mindful_organizer.core.mindfulness_manager import MindfulnessManager
from mindful_organizer.core.profile_manager import ProfileManager
from mindful_organizer.core.system_optimizer import SystemOptimizer
from mindful_organizer.core.system_recognition import SystemRecognition
from mindful_organizer.core.task_manager import TaskManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mindful Organizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.ai_optimizer = AISystemOptimizer()
        self.energy_tracker = EnergyTracker()
        self.file_organizer = FileOrganizer()
        self.mental_health_guide = MentalHealthGuide()
        self.mindfulness_manager = MindfulnessManager()
        self.profile_manager = ProfileManager()
        self.system_optimizer = SystemOptimizer()
        self.system_recognition = SystemRecognition()
        self.task_manager = TaskManager()
        
        # Set up UI
        self.setup_ui()
        
    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Add tabs
        tabs.addTab(self.create_mindfulness_tab(), "Mindfulness")
        tabs.addTab(self.create_gratitude_tab(), "Gratitude")
        tabs.addTab(self.create_journal_tab(), "Journal")
        tabs.addTab(self.create_tasks_tab(), "Tasks")
        tabs.addTab(self.create_energy_tab(), "Energy")
        tabs.addTab(self.create_system_tab(), "System")
        
    def create_mindfulness_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add meditation timer
        timer_label = QLabel("Meditation Timer")
        timer_spinbox = QSpinBox()
        timer_spinbox.setRange(1, 120)
        timer_spinbox.setValue(10)
        timer_spinbox.setSuffix(" minutes")
        
        start_button = QPushButton("Start Meditation")
        
        layout.addWidget(timer_label)
        layout.addWidget(timer_spinbox)
        layout.addWidget(start_button)
        layout.addStretch()
        
        return widget
        
    def create_gratitude_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add gratitude journal
        journal_label = QLabel("Today's Gratitude")
        journal_text = QTextEdit()
        
        save_button = QPushButton("Save Entry")
        
        layout.addWidget(journal_label)
        layout.addWidget(journal_text)
        layout.addWidget(save_button)
        
        return widget
        
    def create_journal_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add journal entry
        date_label = QLabel("Date:")
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        
        mood_label = QLabel("Mood:")
        mood_combo = QComboBox()
        mood_combo.addItems(["Great", "Good", "Neutral", "Low", "Bad"])
        
        entry_label = QLabel("Journal Entry:")
        entry_text = QTextEdit()
        
        save_button = QPushButton("Save Entry")
        
        layout.addWidget(date_label)
        layout.addWidget(date_edit)
        layout.addWidget(mood_label)
        layout.addWidget(mood_combo)
        layout.addWidget(entry_label)
        layout.addWidget(entry_text)
        layout.addWidget(save_button)
        
        return widget
        
    def create_tasks_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add task list
        task_list = QListWidget()
        add_button = QPushButton("Add Task")
        complete_button = QPushButton("Complete Task")
        
        layout.addWidget(task_list)
        layout.addWidget(add_button)
        layout.addWidget(complete_button)
        
        return widget
        
    def create_energy_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add energy tracking
        energy_label = QLabel("Current Energy Level:")
        energy_slider = QProgressBar()
        energy_slider.setRange(0, 100)
        energy_slider.setValue(70)
        
        update_button = QPushButton("Update Energy")
        
        layout.addWidget(energy_label)
        layout.addWidget(energy_slider)
        layout.addWidget(update_button)
        layout.addStretch()
        
        return widget
        
    def create_system_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add system optimization
        cpu_label = QLabel("CPU Usage:")
        cpu_progress = QProgressBar()
        
        memory_label = QLabel("Memory Usage:")
        memory_progress = QProgressBar()
        
        optimize_button = QPushButton("Optimize System")
        
        layout.addWidget(cpu_label)
        layout.addWidget(cpu_progress)
        layout.addWidget(memory_label)
        layout.addWidget(memory_progress)
        layout.addWidget(optimize_button)
        layout.addStretch()
        
        return widget
