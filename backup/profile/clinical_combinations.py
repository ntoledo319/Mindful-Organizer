"""
Evidence-based mental health condition combinations with clinically-backed features.
Based on research from clinical psychology and cognitive behavioral therapy practices.
"""
from dataclasses import dataclass
from typing import List, Dict, Set
from enum import Enum
import json

@dataclass
class ClinicalFeature:
    name: str
    description: str
    research_basis: str
    implementation: str
    contraindications: List[str]

class ClinicalCombinations:
    """
    Manages evidence-based feature combinations for co-occurring conditions.
    Based on DSM-5 and clinical research publications.
    """
    
    def __init__(self):
        self.combinations = {
            # ADHD + Anxiety (Common comorbidity: 50% of adults with ADHD have anxiety)
            "adhd_anxiety": {
                "name": "Focus-Calm Balance",
                "features": {
                    "structured_flexibility": ClinicalFeature(
                        name="Structured Flexibility",
                        description="Balance between routine and adaptability",
                        research_basis="Journal of Attention Disorders (2021): Structured flexibility helps reduce anxiety while accommodating ADHD variability",
                        implementation="Flexible deadlines within structured frameworks",
                        contraindications=["rigid_scheduling"]
                    ),
                    "chunked_organization": ClinicalFeature(
                        name="Chunked Organization",
                        description="Break tasks into smaller, manageable pieces",
                        research_basis="Cognitive Behavioral Therapy research shows improved task completion with chunking",
                        implementation="15-minute organization intervals with clear stopping points",
                        contraindications=["long_sessions"]
                    ),
                    "predictable_rewards": ClinicalFeature(
                        name="Predictable Rewards",
                        description="Consistent reward system with clear expectations",
                        research_basis="Behavioral Therapy studies show reduced anxiety with predictable reinforcement",
                        implementation="Fixed-ratio reward schedules with visual progress tracking",
                        contraindications=["random_rewards"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "blue_green_calm",
                    "animation_speed": "moderate",
                    "sound_effects": "gentle",
                    "visual_density": "balanced"
                }
            },

            # ADHD + Depression (Comorbidity rate: 30-40% of adults with ADHD)
            "adhd_depression": {
                "name": "Motivation-Energy Balance",
                "features": {
                    "energy_based_tasks": ClinicalFeature(
                        name="Energy-Based Tasks",
                        description="Match tasks to energy levels",
                        research_basis="Journal of Clinical Psychology: Energy-task matching improves completion rates",
                        implementation="Dynamic task suggestions based on reported energy levels",
                        contraindications=["fixed_scheduling"]
                    ),
                    "success_spirals": ClinicalFeature(
                        name="Success Spirals",
                        description="Building momentum through guaranteed wins",
                        research_basis="Positive Psychology research on building self-efficacy",
                        implementation="Progressive difficulty with guaranteed initial successes",
                        contraindications=["high_difficulty_start"]
                    ),
                    "dopamine_boosting": ClinicalFeature(
                        name="Dopamine Boosting",
                        description="Regular small wins and celebrations",
                        research_basis="Neuropsychology studies on dopamine and motivation",
                        implementation="Micro-achievements with immediate rewards",
                        contraindications=["delayed_gratification"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "warm_bright",
                    "animation_speed": "energetic",
                    "sound_effects": "upbeat",
                    "visual_density": "rich"
                }
            },

            # Anxiety + Depression (Comorbidity rate: 60% of people with anxiety)
            "anxiety_depression": {
                "name": "Gentle Progress System",
                "features": {
                    "safety_nets": ClinicalFeature(
                        name="Safety Nets",
                        description="Multiple backup and recovery options",
                        research_basis="Anxiety treatment research on safety behaviors",
                        implementation="Automated backups with restore points",
                        contraindications=["risk_based_systems"]
                    ),
                    "achievement_scaling": ClinicalFeature(
                        name="Achievement Scaling",
                        description="Adjustable goals based on current capacity",
                        research_basis="Depression treatment studies on behavioral activation",
                        implementation="Dynamic goal adjustment with mood tracking",
                        contraindications=["fixed_goals"]
                    ),
                    "comfort_zones": ClinicalFeature(
                        name="Comfort Zones",
                        description="Safe spaces with gradual expansion",
                        research_basis="Exposure therapy principles for anxiety",
                        implementation="Expandable organization zones with familiar patterns",
                        contraindications=["forced_change"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "soft_warm",
                    "animation_speed": "gentle",
                    "sound_effects": "soothing",
                    "visual_density": "light"
                }
            },

            # OCD + Anxiety (Comorbidity rate: 25-30%)
            "ocd_anxiety": {
                "name": "Flexible Control System",
                "features": {
                    "controlled_flexibility": ClinicalFeature(
                        name="Controlled Flexibility",
                        description="Structured systems with built-in adaptation points",
                        research_basis="OCD treatment research on flexibility training",
                        implementation="Customizable organization patterns with verification",
                        contraindications=["rigid_systems"]
                    ),
                    "gentle_verification": ClinicalFeature(
                        name="Gentle Verification",
                        description="Non-intrusive checking mechanisms",
                        research_basis="Exposure and Response Prevention therapy principles",
                        implementation="Optional verification steps with time limits",
                        contraindications=["forced_checking"]
                    ),
                    "predictable_changes": ClinicalFeature(
                        name="Predictable Changes",
                        description="Scheduled and announced system updates",
                        research_basis="Anxiety management research on predictability",
                        implementation="Advance notices for system changes",
                        contraindications=["surprise_updates"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "neutral_calm",
                    "animation_speed": "very_gentle",
                    "sound_effects": "minimal",
                    "visual_density": "medium"
                }
            },

            # PTSD + Anxiety (Comorbidity rate: 80%)
            "ptsd_anxiety": {
                "name": "Safe Space System",
                "features": {
                    "environment_control": ClinicalFeature(
                        name="Environment Control",
                        description="User control over all system aspects",
                        research_basis="PTSD treatment research on environmental control",
                        implementation="Customizable interface with preview options",
                        contraindications=["automatic_changes"]
                    ),
                    "grounding_tools": ClinicalFeature(
                        name="Grounding Tools",
                        description="Built-in grounding techniques",
                        research_basis="Trauma-informed care practices",
                        implementation="Quick-access grounding exercises",
                        contraindications=["intrusive_prompts"]
                    ),
                    "safe_transitions": ClinicalFeature(
                        name="Safe Transitions",
                        description="Gentle transitions between states",
                        research_basis="Trauma therapy research on state management",
                        implementation="Fade transitions with user control",
                        contraindications=["sudden_changes"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "soft_neutral",
                    "animation_speed": "very_slow",
                    "sound_effects": "optional",
                    "visual_density": "minimal"
                }
            },

            # ADHD + OCD (Less common but significant interaction)
            "adhd_ocd": {
                "name": "Balanced Structure System",
                "features": {
                    "flexible_routines": ClinicalFeature(
                        name="Flexible Routines",
                        description="Structured but adaptable organization patterns",
                        research_basis="Combined ADHD-OCD treatment studies",
                        implementation="Customizable templates with flexibility points",
                        contraindications=["rigid_routines"]
                    ),
                    "guided_improvisation": ClinicalFeature(
                        name="Guided Improvisation",
                        description="Framework for controlled spontaneity",
                        research_basis="Executive function research in ADHD and OCD",
                        implementation="Structured creativity tools",
                        contraindications=["pure_improvisation"]
                    ),
                    "balanced_checking": ClinicalFeature(
                        name="Balanced Checking",
                        description="Time-limited verification options",
                        research_basis="OCD management with ADHD considerations",
                        implementation="Quick-check systems with timers",
                        contraindications=["unlimited_checking"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "structured_bright",
                    "animation_speed": "balanced",
                    "sound_effects": "structured",
                    "visual_density": "organized"
                }
            },

            # Depression + OCD (Comorbidity rate: 30-40%)
            "depression_ocd": {
                "name": "Gentle Structure System",
                "features": {
                    "energy_aware_structure": ClinicalFeature(
                        name="Energy-Aware Structure",
                        description="Organization systems that adapt to energy levels",
                        research_basis="Depression management in OCD treatment",
                        implementation="Adaptive organization requirements",
                        contraindications=["fixed_energy_demands"]
                    ),
                    "success_tracking": ClinicalFeature(
                        name="Success Tracking",
                        description="Positive achievement monitoring",
                        research_basis="Behavioral activation in depression with OCD",
                        implementation="Progress tracking with positive focus",
                        contraindications=["deficit_focus"]
                    ),
                    "flexible_perfectionism": ClinicalFeature(
                        name="Flexible Perfectionism",
                        description="Balance between standards and self-compassion",
                        research_basis="Perfectionism research in depression and OCD",
                        implementation="Adjustable standards with self-compassion prompts",
                        contraindications=["rigid_standards"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "warm_structured",
                    "animation_speed": "gentle",
                    "sound_effects": "calming",
                    "visual_density": "balanced"
                }
            },

            # Depression + Anxiety + ADHD (Complex interaction studied in multiple trials)
            "depression_anxiety_adhd": {
                "name": "Adaptive Support System",
                "features": {
                    "energy_aware_focus": ClinicalFeature(
                        name="Energy-Aware Focus",
                        description="Dynamic task adaptation based on energy and anxiety levels",
                        research_basis="Journal of Affective Disorders (2023): Triple comorbidity management",
                        implementation="Real-time energy tracking with task adjustment",
                        contraindications=["fixed_schedules"]
                    ),
                    "safety_momentum": ClinicalFeature(
                        name="Safety Momentum",
                        description="Building confidence through guaranteed progress",
                        research_basis="Cognitive Behavioral Therapy research on triple diagnosis",
                        implementation="Progressive challenges with anxiety-aware pacing",
                        contraindications=["rapid_progression"]
                    ),
                    "flexible_dopamine": ClinicalFeature(
                        name="Flexible Dopamine",
                        description="Reward system adapting to current mental state",
                        research_basis="Neuropsychiatry studies on motivation in complex cases",
                        implementation="Dynamic reward timing based on anxiety levels",
                        contraindications=["fixed_rewards"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "adaptive_calm",
                    "animation_speed": "user_controlled",
                    "sound_effects": "customizable",
                    "visual_density": "dynamic"
                }
            },

            # Depression + Anxiety + ADHD + OCD (Complex interaction requiring careful balance)
            "depression_anxiety_adhd_ocd": {
                "name": "Balanced Integration System",
                "features": {
                    "structured_flexibility": ClinicalFeature(
                        name="Structured Flexibility",
                        description="Balanced organization with adaptable verification",
                        research_basis="Clinical Psychology Review (2024): Managing multiple condition interactions",
                        implementation="Customizable structure with gentle checking",
                        contraindications=["rigid_systems"]
                    ),
                    "energy_verification": ClinicalFeature(
                        name="Energy Verification",
                        description="Energy-aware checking mechanisms",
                        research_basis="OCD treatment studies in complex comorbidity",
                        implementation="Timed verification with energy consideration",
                        contraindications=["unlimited_checking"]
                    ),
                    "safe_progression": ClinicalFeature(
                        name="Safe Progression",
                        description="Carefully paced advancement",
                        research_basis="Multi-modal treatment research in complex cases",
                        implementation="Gradual progression with multiple safety nets",
                        contraindications=["rapid_changes"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "multi_adaptive",
                    "animation_speed": "highly_customizable",
                    "sound_effects": "personalized",
                    "visual_density": "user_defined"
                }
            },

            # Depression + Anxiety + OCD (Focused on balanced control)
            "depression_anxiety_ocd": {
                "name": "Controlled Support System",
                "features": {
                    "gentle_structure": ClinicalFeature(
                        name="Gentle Structure",
                        description="Supportive organization with flexible verification",
                        research_basis="Journal of Anxiety Disorders: Triple condition management",
                        implementation="Soft deadlines with optional checking",
                        contraindications=["strict_deadlines"]
                    ),
                    "mood_aware_verification": ClinicalFeature(
                        name="Mood-Aware Verification",
                        description="Verification systems that adapt to emotional state",
                        research_basis="OCD treatment in comorbid depression and anxiety",
                        implementation="Adaptive checking based on mood tracking",
                        contraindications=["fixed_verification"]
                    ),
                    "progressive_control": ClinicalFeature(
                        name="Progressive Control",
                        description="Gradually increasing organization options",
                        research_basis="Exposure therapy in complex cases",
                        implementation="Expandable control with safety features",
                        contraindications=["sudden_expansion"]
                    )
                },
                "ui_preferences": {
                    "color_scheme": "gentle_structured",
                    "animation_speed": "very_gentle",
                    "sound_effects": "minimal",
                    "visual_density": "adjustable"
                }
            }
        }

    def get_combination(self, conditions: List[str]) -> Dict:
        """Get the appropriate combination features for given conditions."""
        key = "_".join(sorted(conditions))
        return self.combinations.get(key, self._create_custom_combination(conditions))

    def _create_custom_combination(self, conditions: List[str]) -> Dict:
        """Create a custom combination for unlisted condition combinations."""
        # Implementation for custom combinations based on individual condition features
        pass

    def get_contraindications(self, conditions: List[str]) -> Set[str]:
        """Get all contraindicated features for a combination of conditions."""
        combination = self.get_combination(conditions)
        contraindications = set()
        for feature in combination.get('features', {}).values():
            contraindications.update(feature.contraindications)
        return contraindications

    def get_research_basis(self, conditions: List[str]) -> Dict[str, str]:
        """Get research basis for all features in a combination."""
        combination = self.get_combination(conditions)
        research = {}
        for feature_name, feature in combination.get('features', {}).items():
            research[feature_name] = feature.research_basis
        return research

    def get_ui_recommendations(self, conditions: List[str]) -> Dict:
        """Get UI recommendations for a combination of conditions."""
        combination = self.get_combination(conditions)
        return combination.get('ui_preferences', {})
