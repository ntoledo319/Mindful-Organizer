"""
AI-powered mental health guidance system.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
import random
from dataclasses import dataclass
from enum import Enum


class SeverityLevel(Enum):
    MILD = 1
    MODERATE = 2
    SEVERE = 3


@dataclass
class MentalHealthPattern:
    pattern_type: str
    severity: SeverityLevel
    frequency: int
    triggers: List[str]
    impact_areas: List[str]


class MentalHealthGuide:
    """AI-powered mental health guidance and support system."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.guide_dir = data_dir / "mental_health_guide"
        self.guide_dir.mkdir(exist_ok=True)
        
        # Load resources
        self._load_resources()
        self._load_user_history()
    
    def _load_resources(self):
        """Load mental health resources and guidance materials."""
        self.crisis_resources = {
            "emergency": "911",
            "suicide_prevention": "1-800-273-8255",
            "crisis_text": "Text HOME to 741741",
            "domestic_violence": "1-800-799-7233",
            "lgbtq_support": "1-866-488-7386"
        }
        
        self.coping_techniques = {
            "anxiety": [
                {
                    "name": "Progressive Muscle Relaxation",
                    "steps": [
                        "Find a quiet place",
                        "Start with your toes",
                        "Tense each muscle group for 5 seconds",
                        "Release and feel the tension flow away",
                        "Move up through your body"
                    ],
                    "duration": "15 minutes"
                },
                {
                    "name": "Grounding Exercise",
                    "steps": [
                        "Name 5 things you can see",
                        "Name 4 things you can touch",
                        "Name 3 things you can hear",
                        "Name 2 things you can smell",
                        "Name 1 thing you can taste"
                    ],
                    "duration": "5 minutes"
                }
            ],
            "depression": [
                {
                    "name": "Behavioral Activation",
                    "steps": [
                        "Make a list of activities you enjoy",
                        "Start with small, achievable tasks",
                        "Schedule one activity daily",
                        "Track your mood before and after",
                        "Gradually increase activity level"
                    ],
                    "duration": "Ongoing"
                }
            ],
            "stress": [
                {
                    "name": "Mindful Walking",
                    "steps": [
                        "Find a peaceful place to walk",
                        "Focus on each step",
                        "Notice the sensation in your feet",
                        "Observe your surroundings",
                        "Let thoughts pass without judgment"
                    ],
                    "duration": "10-20 minutes"
                }
            ]
        }
        
        self.therapeutic_exercises = {
            "cognitive_restructuring": [
                {
                    "name": "Thought Record",
                    "steps": [
                        "Identify the situation",
                        "Note your automatic thoughts",
                        "Identify cognitive distortions",
                        "Generate alternative thoughts",
                        "Rate your belief in each thought"
                    ]
                }
            ],
            "emotional_regulation": [
                {
                    "name": "PLEASE Skills",
                    "steps": [
                        "PL - Treat PhysicaL illness",
                        "E - Eat healthy",
                        "A - Avoid mood-altering drugs",
                        "S - Sleep well",
                        "E - Exercise"
                    ]
                }
            ]
        }
        
        self.mindfulness_exercises = [
            {
                "name": "Body Scan",
                "duration": 15,
                "guidance": [
                    "Find a comfortable position",
                    "Close your eyes",
                    "Focus on your breath",
                    "Scan from toes to head",
                    "Notice sensations without judgment"
                ]
            },
            {
                "name": "Mindful Observation",
                "duration": 10,
                "guidance": [
                    "Choose an object",
                    "Observe as if seeing for first time",
                    "Notice details and features",
                    "Stay present with the object",
                    "Let curiosity guide you"
                ]
            }
        ]
    
    def _load_user_history(self):
        """Load user's mental health history and patterns."""
        history_file = self.guide_dir / "history.json"
        if history_file.exists():
            with open(history_file, "r") as f:
                self.user_history = json.load(f)
        else:
            self.user_history = {
                "patterns": [],
                "interventions": [],
                "progress": []
            }
    
    def analyze_patterns(self, mood_data: List[Dict], anxiety_data: List[Dict]) -> List[MentalHealthPattern]:
        """Analyze mental health patterns from mood and anxiety data."""
        patterns = []
        
        # Analyze mood patterns
        if mood_data:
            recent_moods = mood_data[-14:]  # Last 2 weeks
            avg_mood = sum(m["level"] for m in recent_moods) / len(recent_moods)
            
            if avg_mood <= 2:  # Low mood pattern
                pattern = MentalHealthPattern(
                    pattern_type="low_mood",
                    severity=SeverityLevel.MODERATE if avg_mood < 2 else SeverityLevel.MILD,
                    frequency=len([m for m in recent_moods if m["level"] <= 2]),
                    triggers=[note.get("notes", "") for note in recent_moods if note.get("notes")],
                    impact_areas=["mood", "energy", "motivation"]
                )
                patterns.append(pattern)
        
        # Analyze anxiety patterns
        if anxiety_data:
            recent_anxiety = anxiety_data[-14:]  # Last 2 weeks
            avg_anxiety = sum(a["level"] for a in recent_anxiety) / len(recent_anxiety)
            
            if avg_anxiety >= 3:  # High anxiety pattern
                pattern = MentalHealthPattern(
                    pattern_type="high_anxiety",
                    severity=SeverityLevel.SEVERE if avg_anxiety > 4 else SeverityLevel.MODERATE,
                    frequency=len([a for a in recent_anxiety if a["level"] >= 3]),
                    triggers=[t for entry in recent_anxiety for t in entry.get("triggers", [])],
                    impact_areas=["anxiety", "stress", "sleep"]
                )
                patterns.append(pattern)
        
        return patterns
    
    def get_guided_intervention(self, pattern: MentalHealthPattern) -> Dict:
        """Get personalized intervention based on identified pattern."""
        if pattern.pattern_type == "low_mood":
            techniques = self.coping_techniques["depression"]
            exercises = [ex for ex in self.mindfulness_exercises if ex["duration"] <= 15]
            therapeutic = self.therapeutic_exercises["cognitive_restructuring"]
        elif pattern.pattern_type == "high_anxiety":
            techniques = self.coping_techniques["anxiety"]
            exercises = [ex for ex in self.mindfulness_exercises if "breathing" in ex["name"].lower()]
            therapeutic = self.therapeutic_exercises["emotional_regulation"]
        else:
            techniques = self.coping_techniques["stress"]
            exercises = self.mindfulness_exercises
            therapeutic = []
        
        return {
            "immediate_steps": random.choice(techniques),
            "mindfulness": random.choice(exercises) if exercises else None,
            "therapeutic": random.choice(therapeutic) if therapeutic else None,
            "severity_level": pattern.severity.name,
            "crisis_resources": self.crisis_resources if pattern.severity == SeverityLevel.SEVERE else None
        }
    
    def track_intervention_progress(self, intervention_id: str, effectiveness: int, notes: str = ""):
        """Track the effectiveness of an intervention."""
        progress = {
            "intervention_id": intervention_id,
            "timestamp": datetime.now().isoformat(),
            "effectiveness": effectiveness,
            "notes": notes
        }
        self.user_history["progress"].append(progress)
        self._save_user_history()
    
    def _save_user_history(self):
        """Save user's mental health history."""
        history_file = self.guide_dir / "history.json"
        with open(history_file, "w") as f:
            json.dump(self.user_history, f)
    
    def get_crisis_resources(self) -> Dict[str, str]:
        """Get emergency mental health resources."""
        return self.crisis_resources
