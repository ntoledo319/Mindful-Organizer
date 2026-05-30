"""
Wellness modules for the Mindful Organizer application.

Provides guided breathing exercises, grounding techniques, journaling,
crisis planning, ERP tracking, meditation, and coping strategy recommendations.
"""

from wellness.breathing import (
    BreathingExercise,
    BreathingExerciseType,
    BreathingManager,
    BreathingSession,
    BreathPhase,
    BreathPhaseData,
)
from wellness.coping_engine import (
    CopingCategory,
    CopingEngine,
    CopingStrategy,
    CrisisLevel,
    EnergyLevel,
    StrategyFeedback,
)
from wellness.crisis_plan import (
    CrisisPlan,
    CrisisPlanManager,
    ProfessionalContact,
    SupportContact,
)
from wellness.erp_tracker import (
    ERPTracker,
    ExposureSession,
    HierarchyItem,
    ResponsePreventionLog,
    SafetyBehavior,
)
from wellness.grounding import (
    GroundingManager,
    GroundingSession,
    GroundingTechnique,
    GroundingType,
)
from wellness.journaling import (
    JournalEntry,
    JournalingManager,
    JournalPrompt,
    PromptCategory,
)
from wellness.meditation import (
    MeditationManager,
    MeditationSession,
    MeditationType,
    TimerConfig,
)

__all__ = [
    # breathing
    "BreathingExerciseType",
    "BreathPhase",
    "BreathPhaseData",
    "BreathingExercise",
    "BreathingSession",
    "BreathingManager",
    # grounding
    "GroundingType",
    "GroundingTechnique",
    "GroundingSession",
    "GroundingManager",
    # journaling
    "PromptCategory",
    "JournalPrompt",
    "JournalEntry",
    "JournalingManager",
    # crisis_plan
    "SupportContact",
    "ProfessionalContact",
    "CrisisPlan",
    "CrisisPlanManager",
    # erp_tracker
    "HierarchyItem",
    "ExposureSession",
    "ResponsePreventionLog",
    "SafetyBehavior",
    "ERPTracker",
    # meditation
    "MeditationType",
    "TimerConfig",
    "MeditationSession",
    "MeditationManager",
    # coping_engine
    "CopingCategory",
    "EnergyLevel",
    "CrisisLevel",
    "CopingStrategy",
    "StrategyFeedback",
    "CopingEngine",
]
