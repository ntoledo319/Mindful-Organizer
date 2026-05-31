"""
Tests for CopingEngine (src/wellness/coping_engine.py).

These tests exercise the real CopingEngine: ranked recommendations that
respect time/energy/crisis filters, condition-match scoring, the dedicated
emergency-strategy path (fast, low-energy, crisis-appropriate), and that
recorded feedback is learned and persists across reloads.
"""

from wellness.coping_engine import (
    CopingCategory,
    CopingEngine,
    CrisisLevel,
)

# ---------------------------------------------------------------------------
# Recommendation logic
# ---------------------------------------------------------------------------


class TestGetRecommendations:
    def test_returns_ranked_strategies(self, tmp_data_dir):
        engine = CopingEngine(tmp_data_dir)
        recs = engine.get_recommendations()

        assert len(recs) > 0
        assert len(recs) <= 10  # engine caps at top 10
        # Each item carries a real strategy and a numeric score.
        for rec in recs:
            assert "strategy" in rec
            assert "score" in rec
            assert "id" in rec["strategy"]
        # Sorted by score, descending.
        scores = [r["score"] for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_time_filter_excludes_long_strategies(self, tmp_data_dir):
        engine = CopingEngine(tmp_data_dir)
        recs = engine.get_recommendations(time_available=5)

        assert len(recs) > 0
        for rec in recs:
            assert rec["strategy"]["time_required_minutes"] <= 5

    def test_condition_match_boosts_score(self, tmp_data_dir):
        """Supplying a matching condition must raise the score of at least one
        strategy relative to the same run with no conditions, and never lower one."""
        engine = CopingEngine(tmp_data_dir)

        with_adhd = {
            r["strategy"]["id"]: r["score"]
            for r in engine.get_recommendations(conditions={"adhd"}, time_available=60)
        }
        without = {
            r["strategy"]["id"]: r["score"] for r in engine.get_recommendations(time_available=60)
        }

        common = set(with_adhd) & set(without)
        assert common, "the two runs should share at least one strategy to compare"
        boosted = [sid for sid in common if with_adhd[sid] > without[sid]]
        assert boosted, "a matching condition should boost at least one strategy's score"
        assert all(with_adhd[sid] >= without[sid] for sid in common)

    def test_low_energy_filters_out_high_energy_strategies(self, tmp_data_dir):
        engine = CopingEngine(tmp_data_dir)
        recs = engine.get_recommendations(energy=15, time_available=60)

        ids = {r["strategy"]["id"] for r in recs}
        # Intense exercise (phy_04) requires HIGH energy and must be excluded.
        assert "phy_04" not in ids


# ---------------------------------------------------------------------------
# Emergency mode
# ---------------------------------------------------------------------------


class TestEmergencyStrategies:
    def test_emergency_strategies_are_all_crisis_appropriate(self, tmp_data_dir):
        engine = CopingEngine(tmp_data_dir)
        recs = engine.get_emergency_strategies()

        assert len(recs) > 0
        for rec in recs:
            assert rec["strategy"]["crisis_appropriate"] is True

    def test_emergency_strategies_are_fast(self, tmp_data_dir):
        """Crisis help must be reachable in five minutes or less."""
        engine = CopingEngine(tmp_data_dir)
        recs = engine.get_emergency_strategies()

        for rec in recs:
            assert rec["strategy"]["time_required_minutes"] <= 5

    def test_severe_crisis_excludes_non_crisis_strategies(self, tmp_data_dir):
        engine = CopingEngine(tmp_data_dir)
        recs = engine.get_recommendations(
            time_available=60,
            crisis_level=CrisisLevel.CRISIS,
        )

        assert len(recs) > 0
        assert all(r["strategy"]["crisis_appropriate"] for r in recs)


# ---------------------------------------------------------------------------
# Feedback learning and persistence
# ---------------------------------------------------------------------------


class TestFeedbackLearning:
    def test_positive_feedback_raises_a_strategy_score(self, tmp_data_dir):
        engine = CopingEngine(tmp_data_dir)

        def score_for(sid):
            for r in engine.get_recommendations(time_available=60):
                if r["strategy"]["id"] == sid:
                    return r["score"]
            return None

        # Use whatever strategy currently ranks first, rather than a hard-coded id.
        top = engine.get_recommendations(time_available=60)[0]["strategy"]["id"]
        baseline = score_for(top)
        assert baseline is not None

        for _ in range(3):
            engine.record_feedback(top, helpfulness=5, notes="helped a lot")

        improved = score_for(top)
        assert improved is not None
        assert improved > baseline

    def test_feedback_persists_across_reload(self, tmp_data_dir):
        engine1 = CopingEngine(tmp_data_dir)
        engine1.record_feedback("cog_07", helpfulness=5)
        engine1.record_feedback("cog_07", helpfulness=4)

        engine2 = CopingEngine(tmp_data_dir)
        assert len(engine2.feedback_history) == 2

        stats = engine2.get_strategy_stats()
        assert stats["total_feedback_entries"] == 2
        used_ids = {entry["strategy_id"] for entry in stats["most_used"]}
        assert "cog_07" in used_ids

    def test_helpfulness_is_clamped_to_one_through_five(self, tmp_data_dir):
        engine = CopingEngine(tmp_data_dir)
        engine.record_feedback("phy_03", helpfulness=99)
        engine.record_feedback("phy_03", helpfulness=-5)

        recorded = [fb["helpfulness"] for fb in engine.feedback_history]
        assert recorded == [5, 1]


# ---------------------------------------------------------------------------
# Library access
# ---------------------------------------------------------------------------


class TestStrategyLibrary:
    def test_library_is_populated(self, tmp_data_dir):
        engine = CopingEngine(tmp_data_dir)
        all_strategies = engine.get_all_strategies()
        assert len(all_strategies) >= 40

        # IDs are unique across the library.
        ids = [s["id"] for s in all_strategies]
        assert len(ids) == len(set(ids))

    def test_filter_by_category(self, tmp_data_dir):
        engine = CopingEngine(tmp_data_dir)
        sensory = engine.get_strategies_by_category(CopingCategory.SENSORY)

        assert len(sensory) > 0
        assert all(s["category"] == CopingCategory.SENSORY.value for s in sensory)
