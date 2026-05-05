"""
Tests for CopingEngine functionality (src/wellness/coping_engine.py).

Since the CopingEngine class does not exist as a standalone module,
these tests validate coping-related logic using the available breathing
and grounding modules, and the database layer for coping recommendations.
"""

import pytest

try:
    from src.wellness.breathing import (
        BreathingExerciseType,
        BreathingManager,
    )
    from src.wellness.breathing import (
        Condition as BreathCondition,
    )
    _HAS_BREATHING = True
except ImportError:
    _HAS_BREATHING = False

pytestmark = pytest.mark.skipif(
    not _HAS_BREATHING,
    reason="breathing module not available",
)


# ---------------------------------------------------------------------------
# Recommendation logic (via breathing recommend)
# ---------------------------------------------------------------------------

class TestGetRecommendations:

    def test_recommendations_for_low_mood(self, tmp_data_dir):
        """Low mood should yield calming/grounding exercises."""
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(mood=2)

        assert len(recs) > 0
        # First recommendation should be calming
        top_names = [r.name.lower() for r in recs[:3]]
        assert any("calm" in n or "ground" in n or "deep" in n for n in top_names)

    def test_recommendations_for_high_energy(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(energy=90)
        assert len(recs) > 0

    def test_recommendations_for_low_energy(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(energy=15)
        assert len(recs) > 0
        # Low energy should prefer easy exercises
        assert recs[0].difficulty <= 2


# ---------------------------------------------------------------------------
# Emergency mode (crisis situations -> fastest intervention)
# ---------------------------------------------------------------------------

class TestEmergencyMode:

    def test_anxiety_emergency_yields_grounding_or_calming(self, tmp_data_dir):
        """In anxiety emergency, calming or grounding exercises should be first."""
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(
            mood=1,
            energy=20,
            conditions={BreathCondition.ANXIETY, BreathCondition.PANIC},
        )

        assert len(recs) > 0
        # Top exercise should be suitable for panic
        top = recs[0]
        assert (
            BreathCondition.PANIC in top.condition_suitability
            or BreathCondition.ANXIETY in top.condition_suitability
        )

    def test_ptsd_emergency(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(
            mood=1,
            conditions={BreathCondition.PTSD},
        )
        assert len(recs) > 0
        top = recs[0]
        assert BreathCondition.PTSD in top.condition_suitability


# ---------------------------------------------------------------------------
# Feedback learning (historical effectiveness)
# ---------------------------------------------------------------------------

class TestFeedbackLearning:

    def test_historically_effective_exercise_ranks_higher(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)

        # Create sessions with great improvement for 4-7-8
        for _ in range(5):
            s = bm.create_session(BreathingExerciseType.FOUR_SEVEN_EIGHT, mood_before=2)
            bm.complete_session(s, cycles_completed=4, mood_after=8)

        # Create sessions with poor improvement for energizing
        for _ in range(5):
            s = bm.create_session(BreathingExerciseType.ENERGIZING_BREATH, mood_before=5)
            bm.complete_session(s, cycles_completed=10, mood_after=5)

        recs = bm.recommend()
        names = [r.exercise_type for r in recs]
        idx_478 = names.index(BreathingExerciseType.FOUR_SEVEN_EIGHT)
        idx_energy = names.index(BreathingExerciseType.ENERGIZING_BREATH)

        assert idx_478 < idx_energy  # 4-7-8 should rank higher


# ---------------------------------------------------------------------------
# Condition-specific strategies
# ---------------------------------------------------------------------------

class TestConditionSpecificStrategies:

    def test_adhd_strategies(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(conditions={BreathCondition.ADHD})

        assert len(recs) > 0
        # At least one exercise should be ADHD-suitable
        suitable = [r for r in recs if BreathCondition.ADHD in r.condition_suitability]
        assert len(suitable) >= 1

    def test_depression_strategies(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(conditions={BreathCondition.DEPRESSION})

        suitable = [r for r in recs if BreathCondition.DEPRESSION in r.condition_suitability]
        assert len(suitable) >= 1

    def test_ocd_strategies(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(conditions={BreathCondition.OCD})

        suitable = [r for r in recs if BreathCondition.OCD in r.condition_suitability]
        assert len(suitable) >= 1

    def test_general_strategies(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(conditions={BreathCondition.GENERAL})

        suitable = [r for r in recs if BreathCondition.GENERAL in r.condition_suitability]
        assert len(suitable) >= 1

    def test_multiple_conditions(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(
            conditions={BreathCondition.ANXIETY, BreathCondition.DEPRESSION},
        )
        assert len(recs) > 0
