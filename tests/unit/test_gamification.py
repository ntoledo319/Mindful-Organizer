"""
Tests for the ADHD gamification system (src/file_organization/adhd_gamification.py).

Exercises the real classes: ADHDGameManager (XP/leveling, combos, task and
wellness rewards, achievements, streaks, challenges, statistics, persistence)
and RewardSystem (point-gated unlockable rewards). There is no separate file
tracker class; the manager owns all reward logic.
"""

from datetime import datetime, timedelta

from file_organization.adhd_gamification import (
    LEVEL_NAMES,
    Achievement,
    ADHDGameManager,
    RewardSystem,
    xp_for_level,
)

# ---------------------------------------------------------------------------
# XP and leveling
# ---------------------------------------------------------------------------

class TestXPAndLeveling:

    def test_add_xp_increases_total_and_points(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        result = gm.add_xp(50, "test")

        assert gm.total_xp == 50
        assert gm.points == 50
        assert result["xp_gained"] == 50
        # No combo yet, so multiplier is 1.0.
        assert result["multiplier"] == 1.0

    def test_enough_xp_triggers_level_up(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        # Level 1 needs xp_for_level(0) + xp_for_level(1) total XP.
        needed = xp_for_level(0) + xp_for_level(1)
        result = gm.add_xp(needed, "test")

        assert gm.level >= 1
        assert len(result["level_ups"]) >= 1
        assert result["level_ups"][0]["name"] == LEVEL_NAMES[gm.level]

    def test_level_progress_reports_current_level_name(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        progress = gm.get_level_progress()

        assert progress["level"] == 0
        assert progress["level_name"] == LEVEL_NAMES[0]
        assert 0 <= progress["progress_percent"] <= 100

    def test_progress_visualization_shows_level(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        viz = gm.get_progress_visualization()
        assert "Lv.0" in viz
        assert LEVEL_NAMES[0] in viz


# ---------------------------------------------------------------------------
# Combos
# ---------------------------------------------------------------------------

class TestCombos:

    def test_rapid_actions_build_combo_multiplier(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        assert gm._get_combo_multiplier() == 1.0

        # Two quick actions in a row should push the multiplier above 1x.
        gm.register_action()
        gm.register_action()
        assert gm._get_combo_multiplier() > 1.0

    def test_combo_multiplier_caps_at_three(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        for _ in range(20):
            gm.register_action()
        assert gm._get_combo_multiplier() == 3.0

    def test_stale_action_resets_combo(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        gm.register_action()
        gm.register_action()
        assert gm.combo_count >= 2

        # Last action was more than 5 minutes ago -> combo restarts at 1.
        gm.combo_last_time = datetime.now() - timedelta(minutes=10)
        gm.register_action()
        assert gm.combo_count == 1


# ---------------------------------------------------------------------------
# Task and wellness rewards
# ---------------------------------------------------------------------------

class TestRewards:

    def test_task_completion_awards_xp_by_priority(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        before = gm.total_xp
        result = gm.reward_task_completion({"priority": 4})

        # Priority 4 base XP is 50 (plus possible combo multiplier).
        assert gm.total_xp >= before + 50
        assert result["tasks_today"] == 1
        assert gm.tasks_completed_total == 1
        assert isinstance(result["message"], str) and result["message"]

    def test_quick_organization_scales_with_speed(self, tmp_data_dir):
        fast = ADHDGameManager(tmp_data_dir / "a")
        (tmp_data_dir / "a").mkdir()
        slow = ADHDGameManager(tmp_data_dir / "b")
        (tmp_data_dir / "b").mkdir()

        fast.reward_quick_organization(time_taken=10)
        slow.reward_quick_organization(time_taken=120)

        # Sub-30s organization earns more than a slow one.
        assert fast.total_xp > slow.total_xp

    def test_wellness_action_awards_xp_and_unlocks_achievement(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        before = gm.total_xp
        result = gm.reward_wellness_action("meditation")

        assert gm.total_xp > before
        assert "XP" in result["message"]
        assert Achievement.MEDITATION_MASTER.name in gm.achievements


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------

class TestAchievements:

    def test_first_task_achievement_unlocks(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        gm.reward_task_completion()
        assert Achievement.FIRST_TASK.name in gm.achievements

    def test_get_achievements_reports_unlock_status(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        gm.reward_wellness_action("mood_tracking")

        achievements = gm.get_achievements()
        assert len(achievements) == len(Achievement)
        mood = next(a for a in achievements if a["key"] == "MOOD_TRACKER")
        assert mood["unlocked"] is True
        journal = next(a for a in achievements if a["key"] == "JOURNAL_STARTER")
        assert journal["unlocked"] is False

    def test_achievement_not_duplicated(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        gm.reward_wellness_action("breathing")
        first_count = len(gm.achievements)
        gm.reward_wellness_action("breathing")
        # Re-earning the same achievement does not add a duplicate.
        assert Achievement.BREATHING_PRO.name in gm.achievements
        assert len(gm.achievements) == first_count


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------

class TestChallenges:

    def test_daily_challenges_are_well_formed(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        challenges = gm.generate_daily_challenges()

        assert len(challenges) == 3
        titles = {c["title"] for c in challenges}
        assert len(titles) == 3  # distinct
        for c in challenges:
            assert c["title"]
            assert c["description"]
            assert c["xp"] > 0

    def test_weekly_challenges_are_well_formed(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        challenges = gm.generate_weekly_challenges()

        assert len(challenges) == 2
        for c in challenges:
            assert c["xp"] > 0


# ---------------------------------------------------------------------------
# Statistics and dopamine boosts
# ---------------------------------------------------------------------------

class TestStatistics:

    def test_statistics_reflect_activity(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        gm.reward_task_completion({"priority": 2})

        stats = gm.get_statistics()
        assert stats["tasks_completed_total"] == 1
        assert stats["total_xp"] > 0
        assert stats["achievements_total"] == len(Achievement)
        assert stats["achievements_unlocked"] >= 1
        assert stats["level_name"] == LEVEL_NAMES[gm.level]

    def test_dopamine_boost_is_nonempty_string(self, tmp_data_dir):
        gm = ADHDGameManager(tmp_data_dir)
        boost = gm.get_random_dopamine_boost()
        assert isinstance(boost, str)
        assert len(boost) > 0


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

class TestPersistence:

    def test_xp_and_achievements_survive_reload(self, tmp_data_dir):
        gm1 = ADHDGameManager(tmp_data_dir)
        gm1.add_xp(200, "test")
        gm1.reward_wellness_action("journaling")
        saved_xp = gm1.total_xp

        gm2 = ADHDGameManager(tmp_data_dir)
        assert gm2.total_xp == saved_xp
        assert Achievement.JOURNAL_STARTER.name in gm2.achievements


# ---------------------------------------------------------------------------
# RewardSystem
# ---------------------------------------------------------------------------

class TestRewardSystem:

    def test_available_rewards_are_point_gated(self):
        rs = RewardSystem()
        available = rs.get_available_rewards(1500)
        assert all(r.points <= 1500 for r in available)
        assert len(available) >= 2

    def test_no_rewards_with_zero_points(self):
        rs = RewardSystem()
        assert rs.get_available_rewards(0) == []

    def test_claim_reward_succeeds_with_enough_points(self):
        rs = RewardSystem()
        reward = rs.get_available_rewards(5000)[0]
        assert rs.claim_reward(reward, 5000) is True
        assert reward.unlocked is True

    def test_claim_reward_fails_when_too_poor(self):
        rs = RewardSystem()
        most_expensive = rs.rewards[-1]
        assert rs.claim_reward(most_expensive, 0) is False
        assert most_expensive.unlocked is False
