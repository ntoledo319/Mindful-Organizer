"""
Enhanced gamification system for ADHD-friendly productivity.
Features levels, XP curves, combos, power-ups, weekly challenges,
and condition-specific motivational content.
"""
import json
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# === Level System ===

LEVEL_NAMES = [
    "Novice Organizer",        # 0
    "Apprentice Sorter",       # 1
    "File Wrangler",           # 2
    "Task Tamer",              # 3
    "Focus Fighter",           # 4
    "Productivity Scout",      # 5
    "Organization Knight",     # 6
    "Efficiency Warrior",      # 7
    "Master Planner",          # 8
    "Mind Marshal",            # 9
    "Focus Sage",              # 10
    "Zen Organizer",           # 11
    "Clarity Champion",        # 12
    "Mental Architect",        # 13
    "Mindful Commander",       # 14
    "Legendary Achiever",      # 15
    "Transcendent Planner",    # 16
    "Cosmic Organizer",        # 17
    "Infinite Focus Master",   # 18
    "Legendary Mind Master",   # 19
]


def xp_for_level(level: int) -> int:
    """XP required to reach a given level (exponential curve)."""
    return int(100 * (1.5 ** level))


class Achievement(Enum):
    SPEED_DEMON = "Speed Demon"
    CLEAN_STREAK = "Clean Streak"
    FOLDER_MASTER = "Folder Master"
    DECLUTTER_HERO = "Declutter Hero"
    CONSISTENCY_KING = "Consistency King"
    QUICK_FINDER = "Quick Finder"
    FIRST_TASK = "First Task"
    TEN_TASKS = "Ten Tasks Done"
    FIFTY_TASKS = "Fifty Tasks Done"
    HUNDRED_TASKS = "Century Club"
    MOOD_TRACKER = "Mood Tracker"
    JOURNAL_STARTER = "Journal Starter"
    BREATHING_PRO = "Breathing Pro"
    MEDITATION_MASTER = "Meditation Master"
    WEEK_STREAK = "Week Warrior"
    MONTH_STREAK = "Monthly Marvel"
    COMBO_KING = "Combo King"
    POWER_USER = "Power User"
    EARLY_BIRD = "Early Bird"
    NIGHT_OWL = "Night Owl"


@dataclass
class Reward:
    title: str
    description: str
    points: int
    icon: str
    unlocked: bool = False


@dataclass
class PowerUp:
    name: str
    description: str
    multiplier: float
    duration_minutes: int
    cost_points: int
    active: bool = False
    activated_at: str | None = None


class ADHDGameManager:
    """Enhanced gamification manager with levels, combos, and condition-aware features."""

    def __init__(self, user_data_path: Path):
        self.user_data_path = user_data_path
        self.points: int = 0
        self.total_xp: int = 0
        self.level: int = 0
        self.streak_days: int = 0
        self.last_activity: datetime | None = None
        self.achievements: set[str] = set()
        self.combo_count: int = 0
        self.combo_last_time: datetime | None = None
        self.tasks_completed_total: int = 0
        self.tasks_completed_today: int = 0
        self.today_date: str | None = None
        self.power_ups: list[dict] = []
        self.milestones: list[dict] = []
        self.personal_bests: dict[str, int] = {}
        self.load_user_data()

    def load_user_data(self):
        data_file = self.user_data_path / "adhd_game_data.json"
        if data_file.exists():
            try:
                with open(data_file) as f:
                    data = json.load(f)
                self.points = data.get("points", 0)
                self.total_xp = data.get("total_xp", 0)
                self.level = data.get("level", 0)
                self.streak_days = data.get("streak_days", 0)
                self.achievements = set(data.get("achievements", []))
                self.tasks_completed_total = data.get("tasks_completed_total", 0)
                self.personal_bests = data.get("personal_bests", {})
                self.milestones: list[dict] = data.get("milestones", [])
                self.combo_count = data.get("combo_count", 0)
                self.today_date = data.get("today_date")
                self.tasks_completed_today = data.get("tasks_completed_today", 0)
                last = data.get("last_activity")
                self.last_activity = datetime.fromisoformat(last) if last else None
            except (json.JSONDecodeError, Exception):
                pass

    def save_user_data(self):
        data_file = self.user_data_path / "adhd_game_data.json"
        data = {
            "points": self.points,
            "total_xp": self.total_xp,
            "level": self.level,
            "streak_days": self.streak_days,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "achievements": list(self.achievements),
            "tasks_completed_total": self.tasks_completed_total,
            "tasks_completed_today": self.tasks_completed_today,
            "today_date": self.today_date,
            "personal_bests": self.personal_bests,
            "milestones": self.milestones,
            "combo_count": self.combo_count,
        }
        with open(data_file, "w") as f:
            json.dump(data, f, indent=2)

    # === XP and Leveling ===

    def add_xp(self, amount: int, source: str = "") -> dict:
        """Add XP and check for level up."""
        # Apply combo multiplier
        multiplier = self._get_combo_multiplier()
        actual_xp = int(amount * multiplier)

        self.total_xp += actual_xp
        self.points += actual_xp
        result: dict[str, Any] = {"xp_gained": actual_xp, "multiplier": multiplier, "level_ups": []}

        # Check for level up
        while self.level < len(LEVEL_NAMES) - 1:
            if self.total_xp >= sum(xp_for_level(i) for i in range(self.level + 2)):
                self.level += 1
                level_name = LEVEL_NAMES[self.level]
                result["level_ups"].append({
                    "new_level": self.level,
                    "name": level_name,
                    "message": f"Level Up! You are now a {level_name}!",
                })
                self.milestones.append({
                    "type": "level_up",
                    "level": self.level,
                    "name": level_name,
                    "date": datetime.now().isoformat(),
                })
            else:
                break

        self.save_user_data()
        return result

    def get_level_progress(self) -> dict:
        """Get current level progress."""
        current_threshold = sum(xp_for_level(i) for i in range(self.level + 1))
        next_threshold = sum(xp_for_level(i) for i in range(self.level + 2))
        progress_xp = self.total_xp - current_threshold
        needed_xp = next_threshold - current_threshold

        return {
            "level": self.level,
            "level_name": LEVEL_NAMES[min(self.level, len(LEVEL_NAMES) - 1)],
            "current_xp": progress_xp,
            "needed_xp": needed_xp,
            "progress_percent": min(100, int(progress_xp / max(needed_xp, 1) * 100)),
            "total_xp": self.total_xp,
        }

    # === Combo System ===

    def _get_combo_multiplier(self) -> float:
        """Get current combo multiplier."""
        if self.combo_count <= 0:
            return 1.0
        return min(1.0 + (self.combo_count * 0.25), 3.0)  # Max 3x

    def register_action(self):
        """Register an action for combo tracking."""
        now = datetime.now()
        if self.combo_last_time:
            gap = (now - self.combo_last_time).total_seconds()
            if gap < 300:  # Within 5 minutes
                self.combo_count += 1
                if self.combo_count >= 5:
                    self._check_achievement("combo", "COMBO_KING")
            else:
                self.combo_count = 1
        else:
            self.combo_count = 1
        self.combo_last_time = now

    # === Task Rewards ===

    def reward_task_completion(self, task_data: dict | None = None) -> dict:
        """Reward completing a task."""
        self.register_action()

        # Update daily tracking
        today = datetime.now().strftime("%Y-%m-%d")
        if self.today_date != today:
            self.today_date = today
            self.tasks_completed_today = 0
        self.tasks_completed_today += 1
        self.tasks_completed_total += 1

        # Base XP by priority
        priority = task_data.get("priority", 2) if task_data else 2
        base_xp = {1: 10, 2: 20, 3: 35, 4: 50}.get(priority, 20)

        result = self.add_xp(base_xp, "task_completion")

        # Check achievements
        self._check_task_achievements()

        # Update streak
        self._update_streak()

        # Dopamine boost message
        result["message"] = self.get_random_dopamine_boost()
        result["tasks_today"] = self.tasks_completed_today

        self.save_user_data()
        return result

    def reward_quick_organization(self, time_taken: float) -> dict:
        """Reward quick file organization."""
        self.register_action()
        if time_taken < 30:
            result = self.add_xp(20, "quick_org")
            result["message"] = "Lightning fast organization!"
        elif time_taken < 60:
            result = self.add_xp(10, "quick_org")
            result["message"] = "Quick organization!"
        else:
            result = self.add_xp(5, "org")
            result["message"] = "Files organized!"
        return result

    def reward_wellness_action(self, action_type: str) -> dict:
        """Reward wellness activities (breathing, meditation, journaling)."""
        self.register_action()
        xp_map = {
            "breathing": 15,
            "meditation": 20,
            "journaling": 15,
            "mood_tracking": 10,
            "sleep_logging": 10,
            "grounding": 15,
        }
        xp = xp_map.get(action_type, 10)
        result = self.add_xp(xp, action_type)
        result["message"] = f"Great self-care! +{xp} XP"

        # Check wellness achievements
        if action_type == "mood_tracking":
            self._check_achievement("mood", "MOOD_TRACKER")
        elif action_type == "journaling":
            self._check_achievement("journal", "JOURNAL_STARTER")
        elif action_type == "breathing":
            self._check_achievement("breathing", "BREATHING_PRO")
        elif action_type == "meditation":
            self._check_achievement("meditation", "MEDITATION_MASTER")

        self.save_user_data()
        return result

    # === Streaks ===

    def _update_streak(self):
        now = datetime.now()
        if self.last_activity:
            days_since = (now.date() - self.last_activity.date()).days
            if days_since == 1:
                self.streak_days += 1
                if self.streak_days >= 7:
                    self._check_achievement("streak", "WEEK_STREAK")
                if self.streak_days >= 30:
                    self._check_achievement("streak", "MONTH_STREAK")
            elif days_since > 1:
                self.streak_days = 1
        else:
            self.streak_days = 1
        self.last_activity = now

    # === Achievements ===

    def _check_task_achievements(self):
        if self.tasks_completed_total >= 1:
            self._check_achievement("tasks", "FIRST_TASK")
        if self.tasks_completed_total >= 10:
            self._check_achievement("tasks", "TEN_TASKS")
        if self.tasks_completed_total >= 50:
            self._check_achievement("tasks", "FIFTY_TASKS")
        if self.tasks_completed_total >= 100:
            self._check_achievement("tasks", "HUNDRED_TASKS")

    def _check_achievement(self, category: str, achievement_name: str):
        if achievement_name not in self.achievements:
            self.achievements.add(achievement_name)
            self.milestones.append({
                "type": "achievement",
                "achievement": achievement_name,
                "date": datetime.now().isoformat(),
            })

    def get_achievements(self) -> list[dict]:
        """Get all achievements with unlock status."""
        all_achievements = []
        for ach in Achievement:
            all_achievements.append({
                "name": ach.value,
                "key": ach.name,
                "unlocked": ach.name in self.achievements,
            })
        return all_achievements

    # === Challenges ===

    def generate_daily_challenges(self) -> list[dict]:
        """Generate daily challenges."""
        challenges = [
            {"title": "Speed Sort", "description": "Sort 10 files in under 2 minutes", "xp": 50, "icon": "lightning"},
            {"title": "Folder Focus", "description": "Create and organize a new folder", "xp": 30, "icon": "folder"},
            {"title": "Clean Sweep", "description": "Remove or archive 5 old files", "xp": 40, "icon": "broom"},
            {"title": "Task Blitz", "description": "Complete 5 tasks today", "xp": 60, "icon": "target"},
            {"title": "Mood Check", "description": "Log your mood 3 times today", "xp": 35, "icon": "heart"},
            {"title": "Breathing Break", "description": "Complete 2 breathing exercises", "xp": 30, "icon": "wind"},
            {"title": "Journal Time", "description": "Write a journal entry", "xp": 25, "icon": "book"},
            {"title": "Mindful Minute", "description": "Complete a 5-minute meditation", "xp": 30, "icon": "lotus"},
        ]
        rng = random.Random(datetime.now().strftime("%Y%m%d"))
        return rng.sample(challenges, min(3, len(challenges)))

    def generate_weekly_challenges(self) -> list[dict]:
        """Generate weekly challenges."""
        challenges = [
            {"title": "Consistency Champion", "description": "Complete tasks 5 out of 7 days", "xp": 200, "icon": "trophy"},
            {"title": "Wellness Week", "description": "Do a wellness activity daily for 7 days", "xp": 250, "icon": "star"},
            {"title": "Organization Marathon", "description": "Organize 50 files this week", "xp": 150, "icon": "medal"},
            {"title": "Mood Mapper", "description": "Track mood every day this week", "xp": 175, "icon": "chart"},
        ]
        week_num = datetime.now().isocalendar()[1]
        rng = random.Random(week_num)
        return rng.sample(challenges, min(2, len(challenges)))

    # === Dopamine Boosts ===

    def get_random_dopamine_boost(self) -> str:
        boosts = [
            "Perfect shot! Keep that momentum going!",
            "You're on fire! Look at you go!",
            "That was awesome! You're crushing it!",
            "Blast off! Incredible progress!",
            "You're a champion!",
            "Magic happens when you're this focused!",
            "Unstoppable! Nothing can hold you back!",
            "Your brain just leveled up!",
            "That's the kind of progress that changes lives!",
            "You make productivity look easy!",
        ]
        return random.choice(boosts)

    # === Statistics ===

    def get_statistics(self) -> dict:
        return {
            "total_xp": self.total_xp,
            "level": self.level,
            "level_name": LEVEL_NAMES[min(self.level, len(LEVEL_NAMES) - 1)],
            "points_balance": self.points,
            "streak_days": self.streak_days,
            "tasks_completed_total": self.tasks_completed_total,
            "tasks_completed_today": self.tasks_completed_today,
            "achievements_unlocked": len(self.achievements),
            "achievements_total": len(Achievement),
            "current_combo": self.combo_count,
            "combo_multiplier": self._get_combo_multiplier(),
            "personal_bests": self.personal_bests,
        }

    def get_progress_visualization(self) -> str:
        progress = self.get_level_progress()
        bar_filled = progress["progress_percent"] // 10
        bar_empty = 10 - bar_filled
        bar = "=" * bar_filled + "-" * bar_empty
        return f"Lv.{progress['level']} {progress['level_name']} [{bar}] {progress['progress_percent']}%"


class RewardSystem:
    """Manages unlockable rewards."""

    def __init__(self):
        self.rewards = [
            Reward("Theme Unlocked", "New calm color theme", 500, "palette"),
            Reward("Custom Icons", "Custom folder icons pack", 1000, "target"),
            Reward("Power User", "Advanced organization features", 2000, "lightning"),
            Reward("Sound Pack", "Custom notification sounds", 1500, "music"),
            Reward("Organization Guru", "Special folder templates", 3000, "trophy"),
            Reward("Master Badge", "Display badge on dashboard", 5000, "award"),
        ]

    def get_available_rewards(self, points: int) -> list[Reward]:
        return [r for r in self.rewards if r.points <= points]

    def claim_reward(self, reward: Reward, points: int) -> bool:
        if points >= reward.points:
            reward.unlocked = True
            return True
        return False
