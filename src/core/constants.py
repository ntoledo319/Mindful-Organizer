"""
Canonical constants and enums shared across the Mindful Organizer codebase.

This module exists to eliminate the duplication of domain concepts
(e.g. ``Condition``) that were previously redefined in 6+ files with
slight (and incompatible) variations.
"""

from enum import Enum


class Condition(Enum):
    """Canonical mental-health conditions used throughout the application.

    Values are human-readable display strings so that serialised profiles
    remain legible and backward-compatible with the original
    ``mental_health_profile_builder`` definitions.
    """

    ADHD = "ADHD"
    ANXIETY = "Anxiety"
    DEPRESSION = "Depression"
    OCD = "OCD"
    PTSD = "PTSD"
    BIPOLAR = "Bipolar Disorder"
    PANIC = "Panic Disorder"
    INSOMNIA = "Insomnia"
    GENERAL = "General Wellness"
    DISSOCIATION = "Dissociation"
    BPD = "BPD"
    CHRONIC_FATIGUE = "Chronic Fatigue"

    @classmethod
    def from_string(cls, value: str) -> "Condition":
        """Resolve a condition from a display name or canonical name.

        Matching is case-insensitive so that legacy lowercase strings
        (e.g. ``"adhd"``) are handled gracefully.
        """
        lowered = value.lower()
        for member in cls:
            if member.value.lower() == lowered or member.name.lower() == lowered:
                return member
        return cls.GENERAL


class TherapyType(Enum):
    """Evidence-based therapy modalities integrated in the app."""

    CBT = "Cognitive Behavioral Therapy"
    DBT = "Dialectical Behavior Therapy"
    ACT = "Acceptance and Commitment Therapy"
    MINDFULNESS = "Mindfulness-Based Therapy"
    ERP = "Exposure and Response Prevention"


class TherapySkill(Enum):
    """Specific therapeutic skills referenced across wellness modules."""

    BREATHING = "Deep Breathing"
    GROUNDING = "Grounding Techniques"
    MEDITATION = "Meditation"
    JOURNALING = "Journaling"
    VISUALIZATION = "Visualization"
