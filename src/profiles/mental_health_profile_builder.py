"""
Enhanced adaptive profile builder with support for all conditions,
sensory profiles, values, emergency contacts, and profile switching.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Flag, auto
from pathlib import Path

from core.constants import Condition, TherapySkill, TherapyType


class MentalHealthFlags(Flag):
    """Legacy bit-field flags – retained for backward compatibility.

    New code should prefer the canonical :class:`core.constants.Condition`.
    """

    NONE = 0
    ADHD = auto()
    ANXIETY = auto()
    DEPRESSION = auto()
    OCD = auto()
    PTSD = auto()
    BIPOLAR = auto()


@dataclass
class SensoryProfile:
    """Sensory preferences for UI adaptation."""

    noise_sensitivity: int = 5  # 1-10
    light_sensitivity: int = 5  # 1-10
    motion_sensitivity: int = 5  # 1-10
    texture_sensitivity: int = 5  # 1-10
    color_preference: str = "neutral"  # warm, cool, neutral

    def to_dict(self) -> dict:
        return {
            "noise_sensitivity": self.noise_sensitivity,
            "light_sensitivity": self.light_sensitivity,
            "motion_sensitivity": self.motion_sensitivity,
            "texture_sensitivity": self.texture_sensitivity,
            "color_preference": self.color_preference,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SensoryProfile":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class EmergencyContact:
    """Emergency contact information."""

    name: str
    phone: str
    relationship: str

    def to_dict(self) -> dict:
        return {"name": self.name, "phone": self.phone, "relationship": self.relationship}

    @classmethod
    def from_dict(cls, data: dict) -> "EmergencyContact":
        return cls(
            name=data["name"], phone=data["phone"], relationship=data.get("relationship", "")
        )


@dataclass
class UIPreference:
    color_scheme: str = "neutral"
    contrast_level: str = "normal"
    animation_speed: str = "normal"
    notification_style: str = "standard"
    layout_density: str = "medium"
    font_size: str = "medium"
    use_icons: bool = True
    use_sound: bool = True

    def to_dict(self) -> dict:
        return {
            "color_scheme": self.color_scheme,
            "contrast_level": self.contrast_level,
            "animation_speed": self.animation_speed,
            "notification_style": self.notification_style,
            "layout_density": self.layout_density,
            "font_size": self.font_size,
            "use_icons": self.use_icons,
            "use_sound": self.use_sound,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UIPreference":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class OrganizationPreference:
    folder_depth: int = 3
    naming_convention: str = "standard"
    sort_priority: list[str] = field(default_factory=lambda: ["priority", "due_date"])
    automation_level: str = "medium"
    backup_frequency: str = "daily"
    reminder_frequency: str = "normal"

    def to_dict(self) -> dict:
        return {
            "folder_depth": self.folder_depth,
            "naming_convention": self.naming_convention,
            "sort_priority": self.sort_priority,
            "automation_level": self.automation_level,
            "backup_frequency": self.backup_frequency,
            "reminder_frequency": self.reminder_frequency,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrganizationPreference":
        fields = cls.__dataclass_fields__
        return cls(**{k: v for k, v in data.items() if k in fields})


@dataclass
class Profile:
    """User mental health profile with all preferences and settings."""

    id: str = ""
    name: str = ""
    conditions: set[Condition] = field(default_factory=set)
    therapy_types: set[TherapyType] = field(default_factory=set)
    therapy_skills: set[TherapySkill] = field(default_factory=set)
    ui_preferences: UIPreference = field(default_factory=UIPreference)
    organization_preferences: OrganizationPreference = field(default_factory=OrganizationPreference)
    sensory_profile: SensoryProfile = field(default_factory=SensoryProfile)
    personal_values: list[str] = field(default_factory=list)
    emergency_contacts: list[EmergencyContact] = field(default_factory=list)
    therapist_name: str = ""
    therapist_phone: str = ""
    daily_spoons: int = 12
    created_at: str = ""
    updated_at: str = ""
    notes: str | None = None
    folder_structure: dict = field(default_factory=dict)
    organization_preferences_dict: dict = field(default_factory=dict)
    version: int = 1

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "conditions": [c.value for c in self.conditions],
            "therapy_types": [t.value for t in self.therapy_types],
            "therapy_skills": [s.value for s in self.therapy_skills],
            "ui_preferences": self.ui_preferences.to_dict()
            if isinstance(self.ui_preferences, UIPreference)
            else self.ui_preferences,
            "organization_preferences": self.organization_preferences.to_dict()
            if isinstance(self.organization_preferences, OrganizationPreference)
            else self.organization_preferences,
            "sensory_profile": self.sensory_profile.to_dict()
            if isinstance(self.sensory_profile, SensoryProfile)
            else self.sensory_profile,
            "personal_values": self.personal_values,
            "emergency_contacts": [c.to_dict() for c in self.emergency_contacts],
            "therapist_name": self.therapist_name,
            "therapist_phone": self.therapist_phone,
            "daily_spoons": self.daily_spoons,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "notes": self.notes,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        """Deserialize a profile from dict with backward compatibility."""
        conditions = set()
        for c in data.get("conditions", []):
            try:
                if isinstance(c, str):
                    conditions.add(Condition(c))
                elif isinstance(c, Condition):
                    conditions.add(c)
            except (ValueError, KeyError):
                pass

        therapy_types = set()
        for t in data.get("therapy_types", []):
            try:
                if isinstance(t, str):
                    therapy_types.add(TherapyType(t))
                elif isinstance(t, TherapyType):
                    therapy_types.add(t)
            except (ValueError, KeyError):
                pass

        therapy_skills = set()
        for s in data.get("therapy_skills", []):
            try:
                if isinstance(s, str):
                    therapy_skills.add(TherapySkill(s))
                elif isinstance(s, TherapySkill):
                    therapy_skills.add(s)
            except (ValueError, KeyError):
                pass

        ui_pref = data.get("ui_preferences", {})
        ui = UIPreference.from_dict(ui_pref) if isinstance(ui_pref, dict) else UIPreference()

        org_pref = data.get("organization_preferences", {})
        org = (
            OrganizationPreference.from_dict(org_pref)
            if isinstance(org_pref, dict)
            else OrganizationPreference()
        )

        sensory = data.get("sensory_profile", {})
        sp = SensoryProfile.from_dict(sensory) if isinstance(sensory, dict) else SensoryProfile()

        contacts = []
        for c in data.get("emergency_contacts", []):
            if isinstance(c, dict):
                contacts.append(EmergencyContact.from_dict(c))

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "User"),
            conditions=conditions,
            therapy_types=therapy_types,
            therapy_skills=therapy_skills,
            ui_preferences=ui,
            organization_preferences=org,
            sensory_profile=sp,
            personal_values=data.get("personal_values", []),
            emergency_contacts=contacts,
            therapist_name=data.get("therapist_name", ""),
            therapist_phone=data.get("therapist_phone", ""),
            daily_spoons=data.get("daily_spoons", 12),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            notes=data.get("notes"),
            version=data.get("version", 1),
        )


# === Common Personal Values (ACT Therapy) ===
COMMON_VALUES = [
    "Family",
    "Friendship",
    "Health",
    "Career",
    "Education",
    "Creativity",
    "Adventure",
    "Spirituality",
    "Community",
    "Honesty",
    "Compassion",
    "Independence",
    "Growth",
    "Fun",
    "Nature",
    "Justice",
    "Loyalty",
    "Courage",
    "Gratitude",
    "Mindfulness",
    "Self-care",
    "Connection",
]


class ProfileManager:
    """Builds and manages customized profiles based on mental health combinations."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.profiles_dir = data_dir / "profiles"
        self.profiles_dir.mkdir(exist_ok=True, parents=True)
        self.current_profile_file = self.data_dir / "current_profile.json"
        self._current_profile: Profile | None = None
        self.mental_health_flags = MentalHealthFlags.NONE
        self._load_research_based_settings()
        self._load_current_profile()

    def _load_research_based_settings(self):
        self.condition_settings = {
            MentalHealthFlags.ADHD: {
                "ui": {
                    "color_scheme": "high_contrast",
                    "animation_speed": "reduced",
                    "notification_style": "immediate",
                    "layout_density": "spacious",
                    "use_icons": True,
                    "use_sound": True,
                },
                "organization": {
                    "folder_depth": 2,
                    "naming_convention": "action_based",
                    "automation_level": "high",
                    "reminder_frequency": "frequent",
                },
                "features": ["gamification", "quick_wins", "visual_progress", "dopamine_boosters"],
                "daily_spoons": 10,
            },
            MentalHealthFlags.ANXIETY: {
                "ui": {
                    "color_scheme": "calm",
                    "animation_speed": "gentle",
                    "notification_style": "scheduled",
                    "layout_density": "comfortable",
                    "use_icons": True,
                    "use_sound": False,
                },
                "organization": {
                    "folder_depth": 4,
                    "naming_convention": "detailed",
                    "automation_level": "medium",
                    "backup_frequency": "frequent",
                },
                "features": [
                    "predictable_structure",
                    "backup_assurance",
                    "progress_tracking",
                    "calming_interface",
                ],
                "daily_spoons": 10,
            },
            MentalHealthFlags.DEPRESSION: {
                "ui": {
                    "color_scheme": "uplifting",
                    "animation_speed": "normal",
                    "notification_style": "encouraging",
                    "layout_density": "balanced",
                    "use_icons": True,
                    "use_sound": True,
                },
                "organization": {
                    "folder_depth": 3,
                    "naming_convention": "simple",
                    "automation_level": "high",
                    "reminder_frequency": "moderate",
                },
                "features": [
                    "achievement_celebration",
                    "positive_reinforcement",
                    "manageable_chunks",
                    "progress_visualization",
                ],
                "daily_spoons": 8,
            },
            MentalHealthFlags.OCD: {
                "ui": {
                    "color_scheme": "minimal",
                    "animation_speed": "configurable",
                    "notification_style": "structured",
                    "layout_density": "compact",
                    "use_icons": False,
                    "use_sound": False,
                },
                "organization": {
                    "folder_depth": 5,
                    "naming_convention": "systematic",
                    "automation_level": "configurable",
                    "backup_frequency": "scheduled",
                },
                "features": [
                    "customizable_structure",
                    "verification_steps",
                    "consistent_patterns",
                    "clear_boundaries",
                ],
                "daily_spoons": 10,
            },
            MentalHealthFlags.PTSD: {
                "ui": {
                    "color_scheme": "soothing",
                    "animation_speed": "gentle",
                    "notification_style": "non_intrusive",
                    "layout_density": "spacious",
                    "use_icons": True,
                    "use_sound": False,
                },
                "organization": {
                    "folder_depth": 3,
                    "naming_convention": "clear",
                    "automation_level": "medium",
                    "reminder_frequency": "gentle",
                },
                "features": [
                    "predictable_environment",
                    "gentle_notifications",
                    "safe_space_creation",
                    "control_options",
                ],
                "daily_spoons": 8,
            },
            MentalHealthFlags.BIPOLAR: {
                "ui": {
                    "color_scheme": "balanced",
                    "animation_speed": "moderate",
                    "notification_style": "adaptive",
                    "layout_density": "balanced",
                    "use_icons": True,
                    "use_sound": True,
                },
                "organization": {
                    "folder_depth": 3,
                    "naming_convention": "standard",
                    "automation_level": "medium",
                    "reminder_frequency": "regular",
                },
                "features": [
                    "mood_tracking",
                    "energy_monitoring",
                    "hypomania_detection",
                    "stability_tools",
                ],
                "daily_spoons": 10,
            },
        }

    def _load_current_profile(self):
        if self.current_profile_file.exists():
            try:
                with open(self.current_profile_file) as f:
                    data = json.load(f)
                self._current_profile = Profile.from_dict(data)
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                self._current_profile = None

    def _save_current_profile(self):
        if self._current_profile:
            with open(self.current_profile_file, "w") as f:
                json.dump(self._current_profile.to_dict(), f, indent=2)

    @property
    def current_profile(self) -> Profile | None:
        return self._current_profile

    @current_profile.setter
    def current_profile(self, profile: Profile):
        self._current_profile = profile
        self._save_current_profile()

    def create_profile(
        self,
        name: str,
        conditions: set[Condition],
        therapy_types: set[TherapyType] | None = None,
        **kwargs,
    ) -> Profile:
        """Create a new profile with sensible defaults based on conditions."""
        now = datetime.now().isoformat()
        profile_id = str(uuid.uuid4())

        # Determine default therapy types from conditions
        if therapy_types is None:
            therapy_types = set()
            if Condition.OCD in conditions:
                therapy_types.add(TherapyType.ERP)
                therapy_types.add(TherapyType.CBT)
            if Condition.ANXIETY in conditions or Condition.DEPRESSION in conditions:
                therapy_types.add(TherapyType.CBT)
            if any(c in conditions for c in [Condition.ADHD, Condition.PTSD, Condition.BIPOLAR]):
                therapy_types.add(TherapyType.DBT)
            therapy_types.add(TherapyType.MINDFULNESS)

        # Determine daily spoons
        daily_spoons = 12
        for condition in conditions:
            flag = getattr(MentalHealthFlags, condition.name, None)
            if flag and flag in self.condition_settings:
                spoons = self.condition_settings[flag].get("daily_spoons", 12)
                daily_spoons = min(daily_spoons, spoons)

        profile = Profile(
            id=profile_id,
            name=name,
            conditions=conditions,
            therapy_types=therapy_types,
            daily_spoons=daily_spoons,
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k in Profile.__dataclass_fields__},
        )

        # Save profile
        self._current_profile = profile
        self._save_current_profile()

        # Also save to profiles directory
        profile_file = self.profiles_dir / f"{profile_id}.json"
        with open(profile_file, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)

        return profile

    def save_profile(self, profile_or_path=None):
        """Save the current profile."""
        if isinstance(profile_or_path, Profile):
            self._current_profile = profile_or_path
        self._save_current_profile()
        if self._current_profile:
            profile_file = self.profiles_dir / f"{self._current_profile.id}.json"
            with open(profile_file, "w") as f:
                json.dump(self._current_profile.to_dict(), f, indent=2)

    def list_profiles(self) -> list[dict]:
        """List all saved profiles."""
        profiles = []
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file) as f:
                    data = json.load(f)
                profiles.append(
                    {
                        "id": data.get("id", ""),
                        "name": data.get("name", "Unknown"),
                        "conditions": data.get("conditions", []),
                        "created_at": data.get("created_at", ""),
                    }
                )
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                continue
        return profiles

    def switch_profile(self, profile_id: str) -> Profile | None:
        """Switch to a different profile by ID."""
        profile_file = self.profiles_dir / f"{profile_id}.json"
        if profile_file.exists():
            try:
                with open(profile_file) as f:
                    data = json.load(f)
                self._current_profile = Profile.from_dict(data)
                self._save_current_profile()
                return self._current_profile
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                return None
        return None

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile (cannot delete current)."""
        if self._current_profile and self._current_profile.id == profile_id:
            return False
        profile_file = self.profiles_dir / f"{profile_id}.json"
        if profile_file.exists():
            profile_file.unlink()
            return True
        return False

    def export_profile(self) -> dict:
        """Export current profile as dict."""
        if self._current_profile:
            return self._current_profile.to_dict()
        return {}

    def import_profile(self, data: dict) -> Profile:
        """Import a profile from dict."""
        profile = Profile.from_dict(data)
        profile.id = str(uuid.uuid4())
        profile.updated_at = datetime.now().isoformat()
        self._current_profile = profile
        self._save_current_profile()
        self.save_profile(profile)
        return profile

    def get_profile_completeness(self) -> dict:
        """Check how complete the current profile is."""
        if not self._current_profile:
            return {"score": 0, "missing": ["No profile created"]}

        p = self._current_profile
        checks = {
            "name": bool(p.name and p.name != "User"),
            "conditions": bool(p.conditions),
            "therapy_types": bool(p.therapy_types),
            "personal_values": len(p.personal_values) >= 3,
            "emergency_contacts": len(p.emergency_contacts) >= 1,
            "therapist_info": bool(p.therapist_name),
            "sensory_profile_customized": (
                p.sensory_profile.noise_sensitivity != 5 or p.sensory_profile.light_sensitivity != 5
            ),
        }

        completed = sum(1 for v in checks.values() if v)
        total = len(checks)
        missing = [k.replace("_", " ").title() for k, v in checks.items() if not v]

        return {
            "score": int(completed / total * 100),
            "completed": completed,
            "total": total,
            "missing": missing,
        }

    def get_recommended_features(self) -> list[str]:
        """Get feature recommendations based on profile."""
        if not self._current_profile:
            return ["Complete your profile to get personalized recommendations"]

        features = set()
        conditions = self._current_profile.conditions

        if Condition.ADHD in conditions:
            features.update(["Gamification", "Task Decomposition", "Spoon Theory", "Focus Timer"])
        if Condition.ANXIETY in conditions:
            features.update(
                ["Breathing Exercises", "Grounding", "Worry Time Scheduler", "CBT Tools"]
            )
        if Condition.DEPRESSION in conditions:
            features.update(
                ["Behavioral Activation", "Journaling", "Mood Tracking", "Sleep Tracker"]
            )
        if Condition.OCD in conditions:
            features.update(["ERP Tracker", "Exposure Hierarchy", "Response Prevention Log"])
        if Condition.PTSD in conditions:
            features.update(["Crisis Plan", "Grounding", "Safe Place Visualization", "Meditation"])
        if Condition.BIPOLAR in conditions:
            features.update(
                ["Mood Tracking", "Sleep Tracker", "Hypomania Detection", "Medication Tracker"]
            )

        features.update(["Dashboard", "Task Manager", "Settings"])
        return sorted(features)

    # === Profile Building (Legacy Compatibility) ===

    def set_conditions(self, conditions: list[str]):
        self.mental_health_flags = MentalHealthFlags.NONE
        for condition in conditions:
            if hasattr(MentalHealthFlags, condition.upper()):
                self.mental_health_flags |= getattr(MentalHealthFlags, condition.upper())

    def build_profile(self) -> dict:
        if self.mental_health_flags == MentalHealthFlags.NONE:
            return self._get_default_profile()

        combined: dict[str, dict | set] = {"ui": {}, "organization": {}, "features": set()}
        for flag in MentalHealthFlags:
            if (
                flag != MentalHealthFlags.NONE
                and flag in self.mental_health_flags  # type: ignore[operator]
                and flag in self.condition_settings
            ):
                settings = self.condition_settings[flag]
                combined["ui"].update(settings["ui"])
                combined["organization"].update(settings["organization"])
                combined["features"].update(settings["features"])

        resolved = self._resolve_conflicts(combined)
        resolved["features"] = list(resolved.get("features", set()))
        return resolved

    def _resolve_conflicts(self, settings: dict) -> dict:
        if (
            MentalHealthFlags.ADHD in self.mental_health_flags
            and MentalHealthFlags.ANXIETY in self.mental_health_flags
        ):
            settings.update(
                {"animation_speed": "moderate", "notification_style": "structured_immediate"}
            )
        if (
            MentalHealthFlags.DEPRESSION in self.mental_health_flags
            and MentalHealthFlags.ANXIETY in self.mental_health_flags
        ):
            settings.update(
                {"color_scheme": "calming_positive", "notification_style": "gentle_encouraging"}
            )
        return settings

    def _get_default_profile(self) -> dict:
        return {
            "ui": {
                "color_scheme": "neutral",
                "animation_speed": "normal",
                "notification_style": "standard",
                "layout_density": "medium",
                "use_icons": True,
                "use_sound": True,
            },
            "organization": {
                "folder_depth": 3,
                "naming_convention": "standard",
                "automation_level": "medium",
                "reminder_frequency": "normal",
            },
            "features": [
                "basic_organization",
                "standard_notifications",
                "simple_backup",
                "help_system",
            ],
        }

    def get_feature_explanations(self) -> dict[str, str]:
        all_features = {
            "gamification": "Game elements to boost motivation and engagement",
            "quick_wins": "Small, achievable tasks to build momentum",
            "visual_progress": "Visual indicators of progress and achievement",
            "dopamine_boosters": "Reward mechanisms designed for ADHD brains",
            "predictable_structure": "Consistent, reliable organization patterns",
            "backup_assurance": "Frequent backups for peace of mind",
            "calming_interface": "Soothing colors and gentle animations",
            "achievement_celebration": "Celebratory feedback for completed tasks",
            "positive_reinforcement": "Encouraging messages and progress tracking",
            "manageable_chunks": "Tasks broken into small, achievable pieces",
            "customizable_structure": "Fully customizable organization system",
            "safe_space_creation": "Controlled, predictable environment",
            "mood_tracking": "Comprehensive mood and symptom tracking",
            "hypomania_detection": "Pattern detection for elevated mood states",
        }
        profile = self.build_profile()
        return {f: all_features[f] for f in profile.get("features", []) if f in all_features}

    def load_profile(self, filepath: Path):
        with open(filepath) as f:
            return json.load(f)
