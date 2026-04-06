"""
Wellness modules for the Mindful Organizer application.

Provides guided breathing exercises, grounding techniques, journaling,
crisis planning, ERP tracking, meditation, and coping strategy recommendations.
"""

from src.wellness.breathing import (
    BreathingExerciseType,
    BreathPhase,
    BreathPhaseData,
    BreathingExercise,
    BreathingSession,
    BreathingManager,
)
from src.wellness.grounding import (
    GroundingType,
    GroundingTechnique,
    GroundingSession,
    GroundingManager,
)
from src.wellness.journaling import (
    PromptCategory,
    JournalPrompt,
    JournalEntry,
    JournalingManager,
)
from src.wellness.crisis_plan import (
    SupportContact,
    ProfessionalContact,
    CrisisPlan,
    CrisisPlanManager,
)
from src.wellness.erp_tracker import (
    HierarchyItem,
    ExposureSession,
    ResponsePreventionLog,
    SafetyBehavior,
    ERPTracker,
)
from src.wellness.meditation import (
    MeditationType,
    TimerConfig,
    MeditationSession,
    MeditationManager,
)
from src.wellness.coping_engine import (
    CopingCategory,
    EnergyLevel,
    CrisisLevel,
    CopingStrategy,
    StrategyFeedback,
    CopingEngine,
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
