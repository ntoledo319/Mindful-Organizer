"""
Gamification features for ADHD-friendly file organization.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
import json
import random
from typing import List, Dict, Optional

class Achievement(Enum):
    SPEED_DEMON = "Speed Demon"  # Quick file organization
    CLEAN_STREAK = "Clean Streak"  # Maintaining organization
    FOLDER_MASTER = "Folder Master"  # Creating efficient structures
    DECLUTTER_HERO = "Declutter Hero"  # Removing unnecessary files
    CONSISTENCY_KING = "Consistency King"  # Regular organization
    QUICK_FINDER = "Quick Finder"  # Fast file location

@dataclass
class Reward:
    title: str
    description: str
    points: int
    icon: str

class ADHDGameManager:
    """Manages gamification features for ADHD users."""
    
    def __init__(self, user_data_path: Path):
        self.user_data_path = user_data_path
        self.points = 0
        self.streak_days = 0
        self.last_activity = None
        self.achievements = set()
        self.daily_challenges = []
        self.load_user_data()

    def load_user_data(self):
        """Load user's gamification data."""
        data_file = self.user_data_path / "adhd_game_data.json"
        if data_file.exists():
            with open(data_file, "r") as f:
                data = json.load(f)
                self.points = data.get("points", 0)
                self.streak_days = data.get("streak_days", 0)
                self.last_activity = datetime.fromisoformat(data.get("last_activity", datetime.now().isoformat()))
                self.achievements = set(data.get("achievements", []))

    def save_user_data(self):
        """Save user's gamification data."""
        data_file = self.user_data_path / "adhd_game_data.json"
        data = {
            "points": self.points,
            "streak_days": self.streak_days,
            "last_activity": datetime.now().isoformat(),
            "achievements": list(self.achievements)
        }
        with open(data_file, "w") as f:
            json.dump(data, f, indent=2)

    def generate_daily_challenges(self) -> List[Dict]:
        """Generate daily organization challenges."""
        challenges = [
            {
                "title": "Speed Sort",
                "description": "Sort 10 files in under 2 minutes",
                "points": 50,
                "time_limit": 120,
                "icon": "⚡"
            },
            {
                "title": "Folder Focus",
                "description": "Create and organize a new project folder structure",
                "points": 30,
                "icon": "📁"
            },
            {
                "title": "Clean Sweep",
                "description": "Remove or archive old files",
                "points": 40,
                "icon": "🧹"
            }
        ]
        return random.sample(challenges, 2)  # Return 2 random challenges

    def reward_quick_organization(self, time_taken: float):
        """Reward quick file organization actions."""
        if time_taken < 30:  # Under 30 seconds
            self._add_points(20, "Lightning fast organization! ⚡")
        elif time_taken < 60:  # Under 1 minute
            self._add_points(10, "Quick organization! 🚀")

    def reward_consistent_organization(self):
        """Reward consistent organization habits."""
        if self.last_activity:
            days_since_last = (datetime.now() - self.last_activity).days
            if days_since_last == 1:
                self.streak_days += 1
                streak_bonus = min(self.streak_days * 5, 50)
                self._add_points(streak_bonus, f"Daily streak bonus! 🔥 {self.streak_days} days!")
            elif days_since_last > 1:
                self.streak_days = 0

    def get_random_dopamine_boost(self) -> str:
        """Get random encouraging messages for dopamine boost."""
        boosts = [
            "🎯 Perfect shot! Keep that momentum going!",
            "⚡ You're on fire! Look at you go!",
            "🌟 That was awesome! You're crushing it!",
            "🚀 Blast off! You're making incredible progress!",
            "💪 You're a file organizing champion!",
            "✨ Magic happens when you're this organized!"
        ]
        return random.choice(boosts)

    def check_achievements(self, action_type: str):
        """Check and award achievements based on actions."""
        achievements = {
            "quick_sort": (Achievement.SPEED_DEMON, "Organized 50 files quickly"),
            "streak": (Achievement.CLEAN_STREAK, "Maintained organization for 7 days"),
            "structure": (Achievement.FOLDER_MASTER, "Created 10 efficient folder structures"),
            "declutter": (Achievement.DECLUTTER_HERO, "Cleaned up 100 unnecessary files"),
        }
        
        if action_type in achievements:
            achievement, description = achievements[action_type]
            if achievement.value not in self.achievements:
                self.achievements.add(achievement.value)
                self._add_points(100, f"🏆 New Achievement: {achievement.value}!")

    def get_progress_visualization(self) -> str:
        """Generate a visual representation of progress."""
        level = self.points // 1000
        progress = self.points % 1000
        progress_bar = "█" * (progress // 100) + "░" * (10 - progress // 100)
        return f"Level {level} [{progress_bar}] {progress}/1000"

    def suggest_next_action(self) -> Dict:
        """Suggest the next organization action based on user patterns."""
        suggestions = [
            {
                "action": "Quick Sort",
                "description": "Sort 5 files into their proper folders",
                "estimated_time": "2 minutes",
                "reward": "20 points",
                "icon": "⚡"
            },
            {
                "action": "Power Hour",
                "description": "Organize one project folder completely",
                "estimated_time": "15 minutes",
                "reward": "50 points",
                "icon": "🎯"
            },
            {
                "action": "Maintenance Mode",
                "description": "Review and update file names in one folder",
                "estimated_time": "5 minutes",
                "reward": "30 points",
                "icon": "🔄"
            }
        ]
        return random.choice(suggestions)

    def _add_points(self, points: int, message: str):
        """Add points and display a motivating message."""
        self.points += points
        print(f"{message} +{points} points!")
        if random.random() < 0.3:  # 30% chance of extra encouragement
            print(self.get_random_dopamine_boost())
        self.save_user_data()

class RewardSystem:
    """Manages rewards and incentives for file organization."""
    
    def __init__(self):
        self.rewards = [
            Reward("Theme Unlocked", "New color theme for your folders", 500, "🎨"),
            Reward("Custom Icons", "Custom folder icons pack", 1000, "🎯"),
            Reward("Power User", "Advanced organization features", 2000, "⚡"),
            Reward("Organization Guru", "Special folder templates", 3000, "🏆")
        ]

    def get_available_rewards(self, points: int) -> List[Reward]:
        """Get list of rewards available for the current points."""
        return [r for r in self.rewards if r.points <= points]

    def claim_reward(self, reward: Reward, points: int) -> bool:
        """Attempt to claim a reward."""
        if points >= reward.points:
            return True
        return False

class ADHDFileTracker:
    """Tracks file organization progress and provides instant feedback."""
    
    def __init__(self):
        self.organized_files = 0
        self.start_time = datetime.now()
        self.session_achievements = []

    def track_file_move(self, file_path: Path, destination: Path):
        """Track file organization action and provide immediate feedback."""
        self.organized_files += 1
        time_taken = (datetime.now() - self.start_time).total_seconds()
        
        if self.organized_files % 5 == 0:  # Every 5 files
            print(f"🎯 You've organized {self.organized_files} files! Keep going!")
            
        if time_taken < 30:
            print("⚡ Super quick! You're on fire!")
        
        return {
            "files_organized": self.organized_files,
            "time_taken": time_taken,
            "efficiency_score": self.organized_files / (time_taken + 1)
        }

    def get_session_summary(self) -> Dict:
        """Get a summary of the organization session."""
        return {
            "total_files": self.organized_files,
            "total_time": (datetime.now() - self.start_time).total_seconds(),
            "achievements": self.session_achievements,
            "efficiency_rating": "🌟" * min(5, self.organized_files // 10)
        }
