"""
Profile management system for customizing mental health tracking and organization.
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Set, Optional
import json
from pathlib import Path

class Condition(Enum):
    ADHD = "ADHD"
    DEPRESSION = "Depression"
    BIPOLAR = "Bipolar Disorder"
    OCD = "OCD"
    ANXIETY = "Anxiety"

class TherapyType(Enum):
    CBT = "Cognitive Behavioral Therapy"
    DBT = "Dialectical Behavior Therapy"
    ACT = "Acceptance and Commitment Therapy"
    ERP = "Exposure and Response Prevention"

class SymptomCategory(Enum):
    MOOD = "Mood"
    ATTENTION = "Attention"
    ANXIETY = "Anxiety"
    COMPULSION = "Compulsion"
    ENERGY = "Energy"
    SLEEP = "Sleep"
    SOCIAL = "Social"
    PRODUCTIVITY = "Productivity"

@dataclass
class TherapySkill:
    name: str
    description: str
    therapy_type: TherapyType
    conditions: List[Condition]
    category: str
    practice_steps: List[str]

@dataclass
class Profile:
    name: str
    conditions: Set[Condition]
    therapy_types: Set[TherapyType]
    tracked_symptoms: Dict[SymptomCategory, List[str]]
    custom_symptoms: List[str]
    organization_preferences: Dict[str, bool]
    folder_structure: Dict[str, List[str]]

class ProfileManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.profiles_file = data_dir / "profiles.json"
        self.current_profile: Optional[Profile] = None
        self.therapy_skills: Dict[str, TherapySkill] = self._init_therapy_skills()
        self._load_profiles()

    def _init_therapy_skills(self) -> Dict[str, TherapySkill]:
        """Initialize therapy skills database."""
        skills = {}
        
        # CBT Skills
        skills["thought_record"] = TherapySkill(
            name="Thought Record",
            description="Track and challenge negative thoughts",
            therapy_type=TherapyType.CBT,
            conditions=[Condition.DEPRESSION, Condition.ANXIETY],
            category="Cognitive Restructuring",
            practice_steps=[
                "Identify the situation",
                "Record your automatic thoughts",
                "Identify emotions and their intensity",
                "Find evidence for and against the thought",
                "Generate alternative perspectives",
                "Re-rate emotion intensity"
            ]
        )
        
        # DBT Skills
        skills["wise_mind"] = TherapySkill(
            name="Wise Mind",
            description="Balance emotional and rational mind",
            therapy_type=TherapyType.DBT,
            conditions=[Condition.BIPOLAR, Condition.DEPRESSION],
            category="Mindfulness",
            practice_steps=[
                "Notice your emotional mind",
                "Notice your rational mind",
                "Find the middle path",
                "Make decisions from wise mind"
            ]
        )
        
        # ERP Skills
        skills["exposure_hierarchy"] = TherapySkill(
            name="Exposure Hierarchy",
            description="Create and work through fear ladder",
            therapy_type=TherapyType.ERP,
            conditions=[Condition.OCD, Condition.ANXIETY],
            category="Exposure",
            practice_steps=[
                "List anxiety-provoking situations",
                "Rate anxiety level for each",
                "Order from least to most anxiety-provoking",
                "Start with easier exposures",
                "Progress gradually"
            ]
        )
        
        # ADHD Strategies
        skills["task_breakdown"] = TherapySkill(
            name="Task Breakdown",
            description="Break large tasks into manageable steps",
            therapy_type=TherapyType.CBT,
            conditions=[Condition.ADHD],
            category="Task Management",
            practice_steps=[
                "Identify the main task",
                "Break it into smaller subtasks",
                "Estimate time for each subtask",
                "Set specific deadlines",
                "Use timers and reminders"
            ]
        )
        
        return skills

    def _get_default_symptoms(self, conditions: Set[Condition]) -> Dict[SymptomCategory, List[str]]:
        """Get default symptoms to track based on conditions."""
        symptoms = {category: [] for category in SymptomCategory}
        
        condition_symptoms = {
            Condition.ADHD: {
                SymptomCategory.ATTENTION: [
                    "Difficulty focusing",
                    "Easily distracted",
                    "Task switching issues",
                    "Hyperfocus episodes"
                ],
                SymptomCategory.PRODUCTIVITY: [
                    "Task completion rate",
                    "Organization level",
                    "Time management",
                    "Procrastination"
                ]
            },
            Condition.DEPRESSION: {
                SymptomCategory.MOOD: [
                    "Depressed mood",
                    "Loss of interest",
                    "Feelings of worthlessness",
                    "Suicidal thoughts"
                ],
                SymptomCategory.ENERGY: [
                    "Fatigue level",
                    "Motivation level",
                    "Physical activity"
                ]
            },
            Condition.BIPOLAR: {
                SymptomCategory.MOOD: [
                    "Mood elevation",
                    "Irritability",
                    "Racing thoughts",
                    "Grandiosity"
                ],
                SymptomCategory.ENERGY: [
                    "Energy level",
                    "Sleep needed",
                    "Activity level"
                ]
            },
            Condition.OCD: {
                SymptomCategory.ANXIETY: [
                    "Intrusive thoughts frequency",
                    "Anxiety level",
                    "Avoidance behaviors"
                ],
                SymptomCategory.COMPULSION: [
                    "Compulsion frequency",
                    "Resistance to compulsions",
                    "Time spent on rituals"
                ]
            },
            Condition.ANXIETY: {
                SymptomCategory.ANXIETY: [
                    "Anxiety level",
                    "Panic attacks",
                    "Physical symptoms",
                    "Worry frequency"
                ],
                SymptomCategory.SOCIAL: [
                    "Social avoidance",
                    "Performance anxiety",
                    "Social interaction quality"
                ]
            }
        }
        
        for condition in conditions:
            if condition in condition_symptoms:
                for category, symps in condition_symptoms[condition].items():
                    symptoms[category].extend(symps)
        
        return symptoms

    def _get_default_folder_structure(self, conditions: Set[Condition]) -> Dict[str, List[str]]:
        """Get default folder structure based on conditions."""
        structure = {
            "Documents": [
                "Medical Records",
                "Therapy Notes",
                "Treatment Plans",
                "Progress Reports"
            ],
            "Resources": [
                "Coping Strategies",
                "Educational Materials",
                "Support Groups",
                "Crisis Information"
            ],
            "Tracking": [
                "Mood Logs",
                "Symptom Records",
                "Medication Records",
                "Progress Charts"
            ],
            "Personal": [
                "Journal Entries",
                "Goals",
                "Achievements",
                "Self-Care Plans"
            ]
        }
        
        # Add condition-specific folders
        for condition in conditions:
            if condition == Condition.ADHD:
                structure["Task Management"] = [
                    "Project Breakdowns",
                    "Time Tracking",
                    "Focus Sessions",
                    "Routine Templates"
                ]
            elif condition == Condition.BIPOLAR:
                structure["Mood Management"] = [
                    "Trigger Tracking",
                    "Episode Records",
                    "Sleep Logs",
                    "Early Warning Signs"
                ]
            elif condition == Condition.OCD:
                structure["ERP Work"] = [
                    "Exposure Hierarchies",
                    "Progress Logs",
                    "Ritual Records",
                    "Success Stories"
                ]
            elif condition == Condition.ANXIETY:
                structure["Anxiety Management"] = [
                    "Worry Records",
                    "Relaxation Techniques",
                    "Exposure Logs",
                    "Safety Behaviors"
                ]
        
        return structure

    def create_profile(self, name: str, conditions: Set[Condition]) -> Profile:
        """Create a new profile with default settings based on conditions."""
        therapy_types = {
            TherapyType.CBT,  # Always include CBT
            TherapyType.DBT if Condition.BIPOLAR in conditions else None,
            TherapyType.ERP if Condition.OCD in conditions else None,
            TherapyType.ACT if Condition.ANXIETY in conditions else None
        }
        therapy_types.discard(None)
        
        profile = Profile(
            name=name,
            conditions=conditions,
            therapy_types=therapy_types,
            tracked_symptoms=self._get_default_symptoms(conditions),
            custom_symptoms=[],
            organization_preferences={
                "auto_categorize": True,
                "use_tags": True,
                "track_progress": True,
                "backup_enabled": True,
                "notification_enabled": True
            },
            folder_structure=self._get_default_folder_structure(conditions)
        )
        
        return profile

    def save_profile(self, profile: Profile):
        """Save a profile to disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert profile to dictionary
        profile_data = {
            "name": profile.name,
            "conditions": [c.value for c in profile.conditions],
            "therapy_types": [t.value for t in profile.therapy_types],
            "tracked_symptoms": {k.value: v for k, v in profile.tracked_symptoms.items()},
            "custom_symptoms": profile.custom_symptoms,
            "organization_preferences": profile.organization_preferences,
            "folder_structure": profile.folder_structure
        }
        
        # Save to file
        with open(self.profiles_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
    
    def _load_profiles(self):
        """Load profiles from disk."""
        if not self.profiles_file.exists():
            return
        
        with open(self.profiles_file, 'r') as f:
            data = json.load(f)
            
        # Convert dictionary back to Profile
        self.current_profile = Profile(
            name=data["name"],
            conditions={Condition(c) for c in data["conditions"]},
            therapy_types={TherapyType(t) for t in data["therapy_types"]},
            tracked_symptoms={SymptomCategory(k): v for k, v in data["tracked_symptoms"].items()},
            custom_symptoms=data["custom_symptoms"],
            organization_preferences=data["organization_preferences"],
            folder_structure=data["folder_structure"]
        )
