"""
Tests for BreathingManager (src/wellness/breathing.py).

Covers exercise listing, phase data, session tracking,
mood improvement statistics, and condition-based recommendations.
"""

import pytest

from wellness.breathing import (
BreathingExercise,
BreathingExerciseType,
BreathingManager,
BreathingSession,
BreathPhase,
Condition,
)

# ---------------------------------------------------------------------------
# Exercise access
# ---------------------------------------------------------------------------

class TestGetExercises:

    def test_list_exercises(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        exercises = bm.list_exercises()

        assert len(exercises) >= 6
        assert all(isinstance(e, BreathingExercise) for e in exercises)

    def test_get_exercise_by_type(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        box = bm.get_exercise(BreathingExerciseType.BOX_BREATHING)

        assert box.name == "Box Breathing"
        assert len(box.phases) == 4

    def test_get_unknown_exercise_raises(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        # Passing an invalid key should raise KeyError
        with pytest.raises(KeyError):
            bm.get_exercise("totally_fake")

    def test_all_exercises_have_phases(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        for ex in bm.list_exercises():
            assert len(ex.phases) >= 2
            assert ex.cycle_duration_seconds > 0
            assert ex.total_duration_seconds > 0


# ---------------------------------------------------------------------------
# Exercise phases
# ---------------------------------------------------------------------------

class TestExercisePhases:

    def test_box_breathing_phases(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        box = bm.get_exercise(BreathingExerciseType.BOX_BREATHING)

        phase_types = [p.phase for p in box.phases]
        assert BreathPhase.INHALE in phase_types
        assert BreathPhase.EXHALE in phase_types
        assert BreathPhase.HOLD_IN in phase_types

    def test_cycle_duration(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        box = bm.get_exercise(BreathingExerciseType.BOX_BREATHING)

        # Box breathing: 4+4+4+4 = 16 seconds per cycle
        assert box.cycle_duration_seconds == 16.0

    def test_timer_data_generation(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        box = bm.get_exercise(BreathingExerciseType.BOX_BREATHING)

        timer = box.get_timer_data(cycles=2)
        assert len(timer) == len(box.phases) * 2
        assert timer[0]["cycle"] == 1
        assert timer[-1]["cycle"] == 2
        assert timer[0]["start_at"] == 0.0

    def test_timer_data_default_cycles(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        box = bm.get_exercise(BreathingExerciseType.BOX_BREATHING)

        timer = box.get_timer_data()
        assert len(timer) == len(box.phases) * box.default_cycles


# ---------------------------------------------------------------------------
# Session tracking
# ---------------------------------------------------------------------------

class TestSessionTracking:

    def test_create_session(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        session = bm.create_session(BreathingExerciseType.BOX_BREATHING, mood_before=5)

        assert session.started_at is not None
        assert session.mood_before == 5
        assert session.completed is False

    def test_complete_session(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        session = bm.create_session(BreathingExerciseType.BOX_BREATHING, mood_before=4)
        bm.complete_session(session, cycles_completed=4, mood_after=7)

        assert session.completed is True
        assert session.mood_after == 7
        assert session.ended_at is not None

    def test_session_persists(self, tmp_data_dir):
        bm1 = BreathingManager(tmp_data_dir)
        session = bm1.create_session(BreathingExerciseType.DEEP_BELLY, mood_before=3)
        bm1.complete_session(session, cycles_completed=6, mood_after=6)
        del bm1

        bm2 = BreathingManager(tmp_data_dir)
        assert len(bm2.sessions) == 1
        assert bm2.sessions[0].mood_before == 3

    def test_partial_completion(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        session = bm.create_session(
            BreathingExerciseType.BOX_BREATHING,
            cycles=4,
            mood_before=5,
        )
        bm.complete_session(session, cycles_completed=2, mood_after=6)

        assert session.completed is False  # 2 < 4

    def test_mood_validation(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        with pytest.raises(ValueError):
            bm.create_session(BreathingExerciseType.BOX_BREATHING, mood_before=0)

        with pytest.raises(ValueError):
            bm.create_session(BreathingExerciseType.BOX_BREATHING, mood_before=11)


# ---------------------------------------------------------------------------
# Mood improvement stats
# ---------------------------------------------------------------------------

class TestMoodImprovementStats:

    def test_mood_improvement_calculated(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        session = bm.create_session(BreathingExerciseType.BOX_BREATHING, mood_before=3)
        bm.complete_session(session, cycles_completed=4, mood_after=7)

        assert session.mood_improvement == 4

    def test_mood_improvement_none_without_data(self):
        session = BreathingSession()
        assert session.mood_improvement is None

    def test_statistics_with_sessions(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)

        for mood_before, mood_after, cycles in [(3, 6, 4), (4, 7, 4), (5, 6, 3)]:
            session = bm.create_session(BreathingExerciseType.BOX_BREATHING, mood_before=mood_before)
            bm.complete_session(session, cycles_completed=cycles, mood_after=mood_after)

        stats = bm.get_statistics()
        assert stats["total_sessions"] == 3
        assert stats["completed_sessions"] == 2  # two have cycles >= target
        assert stats["average_mood_improvement"] is not None
        assert stats["average_mood_improvement"] > 0
        assert stats["total_minutes"] > 0

    def test_statistics_empty(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        stats = bm.get_statistics()

        assert stats["total_sessions"] == 0
        assert stats["favorite_exercise"] is None
        assert stats["average_mood_improvement"] is None


# ---------------------------------------------------------------------------
# Condition-based recommendations
# ---------------------------------------------------------------------------

class TestConditionRecommendations:

    def test_recommend_for_anxiety(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(conditions={Condition.ANXIETY})

        assert len(recs) > 0
        # Calming exercises should score higher for anxiety
        top = recs[0]
        assert Condition.ANXIETY in top.condition_suitability or Condition.GENERAL in top.condition_suitability

    def test_recommend_for_depression(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(conditions={Condition.DEPRESSION})

        assert len(recs) > 0

    def test_recommend_with_low_energy(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(energy=20)

        assert len(recs) > 0
        # Low energy should favour low-difficulty exercises
        assert recs[0].difficulty <= 2

    def test_recommend_with_low_mood(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend(mood=2)

        assert len(recs) > 0

    def test_recommend_no_conditions(self, tmp_data_dir):
        bm = BreathingManager(tmp_data_dir)
        recs = bm.recommend()

        assert len(recs) > 0

    def test_recommendation_uses_historical_data(self, tmp_data_dir):
        """Exercises with good past mood improvement should rank higher."""
        bm = BreathingManager(tmp_data_dir)

        # Create sessions with great improvement for deep belly
        for _ in range(3):
            s = bm.create_session(BreathingExerciseType.DEEP_BELLY, mood_before=2)
            bm.complete_session(s, cycles_completed=6, mood_after=9)

        recs = bm.recommend()
        # Deep belly should be near the top due to historical effectiveness
        names = [r.exercise_type for r in recs[:3]]
        assert BreathingExerciseType.DEEP_BELLY in names


# ---------------------------------------------------------------------------
# Session serialization
# ---------------------------------------------------------------------------

class TestSessionSerialization:

    def test_session_round_trip(self):
        session = BreathingSession(
            exercise_type=BreathingExerciseType.BOX_BREATHING,
            cycles_target=4,
            cycles_completed=3,
            mood_before=5,
            mood_after=7,
        )
        d = session.to_dict()
        restored = BreathingSession.from_dict(d)

        assert restored.exercise_type == session.exercise_type
        assert restored.mood_before == 5
        assert restored.mood_after == 7
