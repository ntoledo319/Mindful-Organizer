"""
Comprehensive mindfulness and mental health manager for the Mindful Organizer application.
"""
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal
import random


class MoodLevel(Enum):
    VERY_LOW = 1
    LOW = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


class AnxietyLevel(Enum):
    NONE = 1
    MILD = 2
    MODERATE = 3
    HIGH = 4
    SEVERE = 5


class MindfulnessManager(QObject):
    """Manages comprehensive mindfulness and mental health features."""
    
    # Core signals
    breathing_updated = pyqtSignal(int)
    break_reminder = pyqtSignal(str)
    focus_updated = pyqtSignal(int)
    
    # Mental health signals
    mood_updated = pyqtSignal(dict)
    anxiety_updated = pyqtSignal(dict)
    journal_updated = pyqtSignal(dict)
    gratitude_updated = pyqtSignal(list)
    affirmation_updated = pyqtSignal(str)
    meditation_updated = pyqtSignal(dict)
    
    def __init__(self, data_dir: Path):
        super().__init__()
        self.data_dir = data_dir
        self.mindful_dir = data_dir / "mindfulness"
        self.mindful_dir.mkdir(exist_ok=True)
        
        # Core state
        self.breathing_active = False
        self.break_reminder_enabled = True
        self.focus_active = False
        self.last_break = datetime.now()
        self.break_interval = 30
        
        # Mental health state
        self.current_mood = MoodLevel.NEUTRAL
        self.current_anxiety = AnxietyLevel.NONE
        self.daily_journal = []
        self.gratitude_list = []
        self.meditation_minutes = 0
        self.coping_strategies = []
        self.mood_triggers = []
        self.daily_affirmation = ""
        
        # Load states
        self._load_state()
        self._load_mental_health_state()
        self._load_resources()
    
    def _load_state(self):
        """Load saved mindfulness state."""
        state_file = self.mindful_dir / "state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                state = json.load(f)
                self.break_reminder_enabled = state.get("break_reminder_enabled", True)
                self.break_interval = state.get("break_interval", 30)
                self.last_break = datetime.fromisoformat(state.get("last_break", datetime.now().isoformat()))
    
    def _load_mental_health_state(self):
        """Load mental health tracking data."""
        mh_file = self.mindful_dir / "mental_health.json"
        if mh_file.exists():
            with open(mh_file, "r") as f:
                data = json.load(f)
                self.mood_history = data.get("mood_history", [])
                self.anxiety_history = data.get("anxiety_history", [])
                self.coping_strategies = data.get("coping_strategies", [])
                self.mood_triggers = data.get("mood_triggers", [])
                self.meditation_history = data.get("meditation_history", [])
    
    def _load_resources(self):
        """Load mental health resources and exercises."""
        self.breathing_exercises = [
            {"name": "4-7-8 Breathing", "inhale": 4, "hold": 7, "exhale": 8},
            {"name": "Box Breathing", "inhale": 4, "hold": 4, "exhale": 4},
            {"name": "Deep Belly Breathing", "inhale": 5, "hold": 2, "exhale": 5}
        ]
        
        self.affirmations = [
            "I am capable and strong",
            "I choose to be confident",
            "I am in charge of my well-being",
            "I embrace the present moment",
            "I trust in my journey"
        ]
        
        self.meditation_guides = [
            {"name": "Body Scan", "duration": 10, "type": "mindfulness"},
            {"name": "Loving-Kindness", "duration": 15, "type": "compassion"},
            {"name": "Mindful Awareness", "duration": 20, "type": "awareness"}
        ]
        
        self.coping_techniques = [
            {"name": "5-4-3-2-1 Grounding", "type": "anxiety"},
            {"name": "Progressive Muscle Relaxation", "type": "stress"},
            {"name": "Mindful Walking", "type": "general"},
            {"name": "Thought Reframing", "type": "anxiety"}
        ]
    
    def _save_mental_health_state(self):
        """Save mental health tracking data."""
        mh_file = self.mindful_dir / "mental_health.json"
        data = {
            "mood_history": self.mood_history,
            "anxiety_history": self.anxiety_history,
            "coping_strategies": self.coping_strategies,
            "mood_triggers": self.mood_triggers,
            "meditation_history": self.meditation_history
        }
        with open(mh_file, "w") as f:
            json.dump(data, f)
    
    # Mood and Anxiety Tracking
    def log_mood(self, level: MoodLevel, notes: str = ""):
        """Log current mood with optional notes."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "notes": notes
        }
        self.mood_history.append(entry)
        self._save_mental_health_state()
        self.mood_updated.emit(entry)
    
    def log_anxiety(self, level: AnxietyLevel, triggers: List[str] = None):
        """Log anxiety level with optional triggers."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "triggers": triggers or []
        }
        self.anxiety_history.append(entry)
        self._save_mental_health_state()
        self.anxiety_updated.emit(entry)
    
    # Journaling
    def add_journal_entry(self, content: str, mood: Optional[MoodLevel] = None):
        """Add a journal entry with optional mood."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "mood": mood.value if mood else None
        }
        self.daily_journal.append(entry)
        self.journal_updated.emit(entry)
    
    # Gratitude Practice
    def add_gratitude(self, item: str):
        """Add a gratitude item."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "content": item
        }
        self.gratitude_list.append(entry)
        self.gratitude_updated.emit(self.gratitude_list)
    
    # Meditation
    def start_meditation(self, duration: int = 10, type: str = "mindfulness"):
        """Start a meditation session."""
        self.current_meditation = {
            "start_time": datetime.now().isoformat(),
            "duration": duration,
            "type": type
        }
        self.meditation_updated.emit(self.current_meditation)
    
    def end_meditation(self):
        """End current meditation session."""
        if hasattr(self, 'current_meditation'):
            end_time = datetime.now()
            self.current_meditation["end_time"] = end_time.isoformat()
            self.meditation_history.append(self.current_meditation)
            self._save_mental_health_state()
    
    # Coping Strategies
    def get_coping_strategy(self, type: str = None) -> Dict:
        """Get a random or specific type of coping strategy."""
        strategies = self.coping_techniques
        if type:
            strategies = [s for s in strategies if s["type"] == type]
        return random.choice(strategies)
    
    # Daily Affirmation
    def set_daily_affirmation(self, custom: str = None):
        """Set or generate daily affirmation."""
        self.daily_affirmation = custom or random.choice(self.affirmations)
        self.affirmation_updated.emit(self.daily_affirmation)
    
    # Core Features
    def start_breathing_exercise(self, exercise_name: str = None):
        """Start a guided breathing exercise."""
        if exercise_name:
            exercise = next((e for e in self.breathing_exercises if e["name"] == exercise_name), self.breathing_exercises[0])
        else:
            exercise = self.breathing_exercises[0]
            
        self.breathing_active = True
        self.current_exercise = exercise
        self.breathing_progress = 0
        self.breathing_updated.emit(0)
    
    def toggle_break_reminder(self, enabled: bool):
        """Enable or disable break reminders."""
        self.break_reminder_enabled = enabled
        self._save_state()
    
    def start_focus_session(self, duration: int = 25):
        """Start a focused work session."""
        self.focus_active = True
        self.focus_duration = duration
        self.focus_start = datetime.now()
        self.focus_updated.emit(duration)
    
    def update(self):
        """Update timers and check for reminders."""
        now = datetime.now()
        
        # Update breathing exercise
        if self.breathing_active:
            self.breathing_progress = (self.breathing_progress + 1) % 100
            self.breathing_updated.emit(self.breathing_progress)
        
        # Check for break reminder
        if self.break_reminder_enabled:
            time_since_break = now - self.last_break
            if time_since_break.total_seconds() / 60 >= self.break_interval:
                self.break_reminder.emit("Time for a mindful break!")
                self.last_break = now
                self._save_state()
        
        # Update focus session
        if self.focus_active:
            elapsed = (now - self.focus_start).total_seconds() / 60
            remaining = max(0, self.focus_duration - int(elapsed))
            self.focus_updated.emit(remaining)
            if remaining == 0:
                self.focus_active = False
                
    def get_mood_analysis(self) -> Dict:
        """Analyze mood patterns and trends."""
        if not self.mood_history:
            return {"average": None, "trend": None}
            
        recent_moods = self.mood_history[-7:]  # Last 7 entries
        avg_mood = sum(m["level"] for m in recent_moods) / len(recent_moods)
        
        trend = "stable"
        if len(recent_moods) > 1:
            if recent_moods[-1]["level"] > recent_moods[0]["level"]:
                trend = "improving"
            elif recent_moods[-1]["level"] < recent_moods[0]["level"]:
                trend = "declining"
                
        return {
            "average": avg_mood,
            "trend": trend,
            "triggers": self.mood_triggers
        }
        
    def get_anxiety_analysis(self) -> Dict:
        """Analyze anxiety patterns and common triggers."""
        if not self.anxiety_history:
            return {"level": None, "common_triggers": []}
            
        recent_anxiety = self.anxiety_history[-7:]  # Last 7 entries
        avg_level = sum(a["level"] for a in recent_anxiety) / len(recent_anxiety)
        
        # Analyze triggers
        all_triggers = [t for entry in recent_anxiety for t in entry["triggers"]]
        trigger_counts = {}
        for trigger in all_triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
            
        common_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "level": avg_level,
            "common_triggers": [t[0] for t in common_triggers]
        }
