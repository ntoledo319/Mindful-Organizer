"""
Tests for ADHDGameManager (src/file_organization/adhd_gamification.py).

Covers point management, streak tracking, achievements,
daily challenges, and progress visualization.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

try:
    from src.file_organization.adhd_gamification import (
        ADHDGameManager,
        Achievement,
        RewardSystem,
        ADHDFileTracker,
    )
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="adhd_gamification module not available")


@pytest.fixture
def game_manager(tmp_data_dir):
    return ADHDGameManager(tmp_data_dir)


# ---------------------------------------------------------------------------
# Add points
# ---------------------------------------------------------------------------

class TestAddPoints:

    def test_add_points(self, game_manager):
        initial = game_manager.points
        game_manager._add_points(50, "Test bonus")
        assert game_manager.points == initial + 50

    def test_reward_quick_organization_fast(self, game_manager):
        initial = game_manager.points
        game_manager.reward_quick_organization(time_taken=20)
        assert game_manager.points > initial

    def test_reward_quick_organization_medium(self, game_manager):
        initial = game_manager.points
        game_manager.reward_quick_organization(time_taken=45)
        assert game_manager.points > initial

    def test_reward_quick_organization_slow(self, game_manager):
        initial = game_manager.points
        game_manager.reward_quick_organization(time_taken=90)
        assert game_manager.points == initial  # no reward for slow


# ---------------------------------------------------------------------------
# Streak tracking
# ---------------------------------------------------------------------------

class TestStreakTracking:

    def test_streak_increments(self, game_manager):
        game_manager.last_activity = datetime.now() - timedelta(days=1)
        game_manager.streak_days = 3
        game_manager.reward_consistent_organization()

        assert game_manager.streak_days == 4

    def test_streak_resets_on_gap(self, game_manager):
        game_manager.last_activity = datetime.now() - timedelta(days=3)
        game_manager.streak_days = 5
        game_manager.reward_consistent_organization()

        assert game_manager.streak_days == 0

    def test_streak_bonus_points(self, game_manager):
        game_manager.last_activity = datetime.now() - timedelta(days=1)
        game_manager.streak_days = 5
        initial = game_manager.points
        game_manager.reward_consistent_organization()

        assert game_manager.points > initial

    def test_streak_bonus_capped(self, game_manager):
        game_manager.last_activity = datetime.now() - timedelta(days=1)
        game_manager.streak_days = 100  # very long streak
        initial = game_manager.points
        game_manager.reward_consistent_organization()

        # Max bonus is 50 points
        assert game_manager.points - initial <= 50


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------

class TestAchievements:

    def test_check_achievement_quick_sort(self, game_manager):
        initial_count = len(game_manager.achievements)
        game_manager.check_achievements("quick_sort")

        assert len(game_manager.achievements) == initial_count + 1
        assert Achievement.SPEED_DEMON.value in game_manager.achievements

    def test_check_achievement_streak(self, game_manager):
        game_manager.check_achievements("streak")
        assert Achievement.CLEAN_STREAK.value in game_manager.achievements

    def test_achievement_not_duplicated(self, game_manager):
        game_manager.check_achievements("quick_sort")
        initial_points = game_manager.points
        game_manager.check_achievements("quick_sort")

        # No extra points for duplicate achievement
        assert game_manager.points == initial_points

    def test_unknown_achievement_ignored(self, game_manager):
        initial_count = len(game_manager.achievements)
        game_manager.check_achievements("nonexistent")
        assert len(game_manager.achievements) == initial_count


# ---------------------------------------------------------------------------
# Daily challenges
# ---------------------------------------------------------------------------

class TestDailyChallenges:

    def test_generate_daily_challenges(self, game_manager):
        challenges = game_manager.generate_daily_challenges()
        assert len(challenges) == 2

        for c in challenges:
            assert "title" in c
            assert "description" in c
            assert "points" in c
            assert c["points"] > 0

    def test_challenges_vary(self, game_manager):
        """Generated challenges should come from the pool."""
        challenges = game_manager.generate_daily_challenges()
        titles = {c["title"] for c in challenges}
        assert len(titles) == 2  # two distinct challenges


# ---------------------------------------------------------------------------
# Progress visualization
# ---------------------------------------------------------------------------

class TestProgressVisualization:

    def test_get_progress_visualization(self, game_manager):
        game_manager.points = 2500
        viz = game_manager.get_progress_visualization()

        assert "Level 2" in viz
        assert "500/1000" in viz

    def test_progress_at_zero(self, game_manager):
        game_manager.points = 0
        viz = game_manager.get_progress_visualization()
        assert "Level 0" in viz

    def test_suggest_next_action(self, game_manager):
        suggestion = game_manager.suggest_next_action()
        assert "action" in suggestion
        assert "description" in suggestion
        assert "reward" in suggestion


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

class TestPersistence:

    def test_save_and_load(self, tmp_data_dir):
        gm1 = ADHDGameManager(tmp_data_dir)
        gm1._add_points(200, "Test")
        gm1.check_achievements("quick_sort")
        del gm1

        gm2 = ADHDGameManager(tmp_data_dir)
        assert gm2.points >= 200
        assert Achievement.SPEED_DEMON.value in gm2.achievements


# ---------------------------------------------------------------------------
# RewardSystem
# ---------------------------------------------------------------------------

class TestRewardSystem:

    def test_get_available_rewards(self):
        rs = RewardSystem()
        available = rs.get_available_rewards(1500)
        assert len(available) >= 2

    def test_get_available_rewards_none(self):
        rs = RewardSystem()
        available = rs.get_available_rewards(0)
        assert len(available) == 0

    def test_claim_reward_success(self):
        rs = RewardSystem()
        available = rs.get_available_rewards(5000)
        assert rs.claim_reward(available[0], 5000) is True

    def test_claim_reward_insufficient(self):
        rs = RewardSystem()
        all_rewards = rs.rewards
        assert rs.claim_reward(all_rewards[-1], 0) is False


# ---------------------------------------------------------------------------
# ADHDFileTracker
# ---------------------------------------------------------------------------

class TestADHDFileTracker:

    def test_track_file_move(self, tmp_path):
        tracker = ADHDFileTracker()
        result = tracker.track_file_move(
            tmp_path / "source.txt",
            tmp_path / "dest.txt",
        )
        assert result["files_organized"] == 1

    def test_session_summary(self):
        tracker = ADHDFileTracker()
        summary = tracker.get_session_summary()
        assert summary["total_files"] == 0

    def test_dopamine_boost(self, game_manager):
        boost = game_manager.get_random_dopamine_boost()
        assert isinstance(boost, str)
        assert len(boost) > 0
