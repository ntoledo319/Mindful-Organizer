"""
Adaptive profile builder that creates personalized organization systems
based on combinations of mental health considerations.
"""
from dataclasses import dataclass
from enum import Flag, auto, Enum
from typing import List, Dict, Set, Optional
from pathlib import Path
import json

class MentalHealthFlags(Flag):
    """Flags for different mental health considerations."""
    NONE = 0
    ADHD = auto()
    ANXIETY = auto()
    DEPRESSION = auto()
    OCD = auto()
    PTSD = auto()

class Condition(Enum):
    """Mental health conditions."""
    ADHD = "ADHD"
    ANXIETY = "Anxiety"
    DEPRESSION = "Depression"
    OCD = "OCD"
    PTSD = "PTSD"

class TherapyType(Enum):
    """Types of therapy."""
    CBT = "Cognitive Behavioral Therapy"
    DBT = "Dialectical Behavior Therapy"
    ACT = "Acceptance and Commitment Therapy"
    MINDFULNESS = "Mindfulness-Based Therapy"

class TherapySkill(Enum):
    """Specific therapy skills."""
    BREATHING = "Deep Breathing"
    GROUNDING = "Grounding Techniques"
    MEDITATION = "Meditation"
    JOURNALING = "Journaling"
    VISUALIZATION = "Visualization"

@dataclass
class UIPreference:
    """UI preferences based on mental health profile."""
    color_scheme: str
    contrast_level: str
    animation_speed: str
    notification_style: str
    layout_density: str
    font_size: str
    use_icons: bool
    use_sound: bool

@dataclass
class OrganizationPreference:
    """Organization preferences based on mental health profile."""
    folder_depth: int
    naming_convention: str
    sort_priority: List[str]
    automation_level: str
    backup_frequency: str
    reminder_frequency: str

@dataclass
class Profile:
    """User mental health profile."""
    name: str
    conditions: Set[Condition]
    therapy_types: Set[TherapyType]
    therapy_skills: Set[TherapySkill]
    ui_preferences: UIPreference
    organization_preferences: OrganizationPreference
    created_at: str
    updated_at: str
    notes: Optional[str] = None

class ProfileManager:
    """Builds and manages customized profiles based on mental health combinations."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.profiles_dir = data_dir / "profiles"
        self.profiles_dir.mkdir(exist_ok=True, parents=True)
        self.current_profile_file = self.data_dir / "current_profile.json"
        self._current_profile = None
        self.mental_health_flags = MentalHealthFlags.NONE
        self._load_research_based_settings()
        self._load_current_profile()

    def _load_research_based_settings(self):
        """Load evidence-based settings for different conditions."""
        self.condition_settings = {
            MentalHealthFlags.ADHD: {
                "ui": {
                    "color_scheme": "high_contrast",
                    "animation_speed": "reduced",
                    "notification_style": "immediate",
                    "layout_density": "spacious",
                    "use_icons": True,
                    "use_sound": True
                },
                "organization": {
                    "folder_depth": 2,
                    "naming_convention": "action_based",
                    "automation_level": "high",
                    "reminder_frequency": "frequent"
                },
                "features": [
                    "gamification",
                    "quick_wins",
                    "visual_progress",
                    "dopamine_boosters"
                ]
            },
            MentalHealthFlags.ANXIETY: {
                "ui": {
                    "color_scheme": "calm",
                    "animation_speed": "gentle",
                    "notification_style": "scheduled",
                    "layout_density": "comfortable",
                    "use_icons": True,
                    "use_sound": False
                },
                "organization": {
                    "folder_depth": 4,
                    "naming_convention": "detailed",
                    "automation_level": "medium",
                    "backup_frequency": "frequent"
                },
                "features": [
                    "predictable_structure",
                    "backup_assurance",
                    "progress_tracking",
                    "calming_interface"
                ]
            },
            MentalHealthFlags.DEPRESSION: {
                "ui": {
                    "color_scheme": "uplifting",
                    "animation_speed": "normal",
                    "notification_style": "encouraging",
                    "layout_density": "balanced",
                    "use_icons": True,
                    "use_sound": True
                },
                "organization": {
                    "folder_depth": 3,
                    "naming_convention": "simple",
                    "automation_level": "high",
                    "reminder_frequency": "moderate"
                },
                "features": [
                    "achievement_celebration",
                    "positive_reinforcement",
                    "manageable_chunks",
                    "progress_visualization"
                ]
            },
            MentalHealthFlags.OCD: {
                "ui": {
                    "color_scheme": "minimal",
                    "animation_speed": "configurable",
                    "notification_style": "structured",
                    "layout_density": "compact",
                    "use_icons": False,
                    "use_sound": False
                },
                "organization": {
                    "folder_depth": 5,
                    "naming_convention": "systematic",
                    "automation_level": "configurable",
                    "backup_frequency": "scheduled"
                },
                "features": [
                    "customizable_structure",
                    "verification_steps",
                    "consistent_patterns",
                    "clear_boundaries"
                ]
            },
            MentalHealthFlags.PTSD: {
                "ui": {
                    "color_scheme": "soothing",
                    "animation_speed": "gentle",
                    "notification_style": "non_intrusive",
                    "layout_density": "spacious",
                    "use_icons": True,
                    "use_sound": False
                },
                "organization": {
                    "folder_depth": 3,
                    "naming_convention": "clear",
                    "automation_level": "medium",
                    "reminder_frequency": "gentle"
                },
                "features": [
                    "predictable_environment",
                    "gentle_notifications",
                    "safe_space_creation",
                    "control_options"
                ]
            }
        }

    def _load_current_profile(self):
        """Load the current profile if it exists."""
        if self.current_profile_file.exists():
            with open(self.current_profile_file, 'r') as f:
                data = json.load(f)
                self._current_profile = Profile(**data)

    def _save_current_profile(self):
        """Save the current profile."""
        if self._current_profile:
            with open(self.current_profile_file, 'w') as f:
                json.dump(vars(self._current_profile), f, default=str)

    @property
    def current_profile(self) -> Optional[Profile]:
        """Get the current profile."""
        return self._current_profile

    @current_profile.setter
    def current_profile(self, profile: Profile):
        """Set the current profile."""
        self._current_profile = profile
        self._save_current_profile()

    def set_conditions(self, conditions: List[str]):
        """Set the mental health conditions for the profile."""
        self.mental_health_flags = MentalHealthFlags.NONE
        for condition in conditions:
            if hasattr(MentalHealthFlags, condition.upper()):
                self.mental_health_flags |= getattr(MentalHealthFlags, condition.upper())

    def _resolve_conflicts(self, settings: Dict) -> Dict:
        """Resolve conflicts between different condition settings."""
        if (MentalHealthFlags.ADHD in self.mental_health_flags and 
            MentalHealthFlags.ANXIETY in self.mental_health_flags):
            # Balance ADHD's quick pace with anxiety's need for structure
            settings.update({
                "animation_speed": "moderate",
                "notification_style": "structured_immediate",
                "folder_depth": 3,
                "automation_level": "medium_high"
            })

        if (MentalHealthFlags.OCD in self.mental_health_flags and 
            MentalHealthFlags.ADHD in self.mental_health_flags):
            # Balance OCD's detail with ADHD's need for simplicity
            settings.update({
                "folder_depth": 3,
                "naming_convention": "structured_simple",
                "automation_level": "high_with_verification"
            })

        if (MentalHealthFlags.DEPRESSION in self.mental_health_flags and 
            MentalHealthFlags.ANXIETY in self.mental_health_flags):
            # Combine encouraging elements with calming features
            settings.update({
                "color_scheme": "calming_positive",
                "notification_style": "gentle_encouraging",
                "reminder_frequency": "balanced"
            })

        return settings

    def build_profile(self) -> Dict:
        """Build a profile based on the selected conditions."""
        if self.mental_health_flags == MentalHealthFlags.NONE:
            return self._get_default_profile()

        combined_settings = {
            "ui": {},
            "organization": {},
            "features": set()
        }

        # Gather settings from all selected conditions
        for flag in MentalHealthFlags:
            if flag in self.mental_health_flags and flag != MentalHealthFlags.NONE:
                settings = self.condition_settings[flag]
                combined_settings["ui"].update(settings["ui"])
                combined_settings["organization"].update(settings["organization"])
                combined_settings["features"].update(settings["features"])

        # Resolve any conflicts
        resolved_settings = self._resolve_conflicts(combined_settings)

        # Add combination-specific features
        resolved_settings["features"] = list(resolved_settings["features"])
        resolved_settings["features"].extend(self._get_combination_features())

        return resolved_settings

    def _get_combination_features(self) -> List[str]:
        """Get additional features specific to condition combinations."""
        features = []
        
        if (MentalHealthFlags.ADHD in self.mental_health_flags and 
            MentalHealthFlags.ANXIETY in self.mental_health_flags):
            features.extend([
                "structured_gamification",
                "predictable_rewards",
                "anxiety_aware_notifications"
            ])

        if (MentalHealthFlags.DEPRESSION in self.mental_health_flags and 
            MentalHealthFlags.ADHD in self.mental_health_flags):
            features.extend([
                "motivational_gamification",
                "energy_aware_tasks",
                "achievement_focused"
            ])

        if (MentalHealthFlags.ANXIETY in self.mental_health_flags and 
            MentalHealthFlags.OCD in self.mental_health_flags):
            features.extend([
                "flexible_structure",
                "gentle_verification",
                "customizable_patterns"
            ])

        return features

    def _get_default_profile(self) -> Dict:
        """Get default profile settings."""
        return {
            "ui": {
                "color_scheme": "neutral",
                "animation_speed": "normal",
                "notification_style": "standard",
                "layout_density": "medium",
                "use_icons": True,
                "use_sound": True
            },
            "organization": {
                "folder_depth": 3,
                "naming_convention": "standard",
                "automation_level": "medium",
                "reminder_frequency": "normal"
            },
            "features": [
                "basic_organization",
                "standard_notifications",
                "simple_backup",
                "help_system"
            ]
        }

    def get_feature_explanations(self) -> Dict[str, str]:
        """Get detailed explanations of enabled features."""
        all_features = {
            "structured_gamification": "Combines game elements with predictable patterns",
            "predictable_rewards": "Regular, expected rewards for organization",
            "anxiety_aware_notifications": "Gentle, non-startling notifications",
            "motivational_gamification": "Game elements focused on building motivation",
            "energy_aware_tasks": "Tasks adapted to current energy levels",
            "achievement_focused": "Emphasis on completing and celebrating tasks",
            "flexible_structure": "Structured but adaptable organization",
            "gentle_verification": "Soft confirmation of actions without pressure",
            "customizable_patterns": "User-defined organizational patterns"
        }
        
        enabled_features = {}
        profile = self.build_profile()
        for feature in profile["features"]:
            if feature in all_features:
                enabled_features[feature] = all_features[feature]
        
        return enabled_features

    def save_profile(self, filepath: Path):
        """Save the current profile to a file."""
        profile = self.build_profile()
        with open(filepath, 'w') as f:
            json.dump(profile, f, indent=2)

    def load_profile(self, filepath: Path):
        """Load a profile from a file."""
        with open(filepath, 'r') as f:
            profile = json.load(f)
        return profile
