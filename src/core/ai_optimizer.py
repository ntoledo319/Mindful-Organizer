"""
AI-powered system optimization, adaptive task scheduling, and burnout/hypomania detection.
"""
import contextlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

try:
    import joblib
    from sklearn.ensemble import RandomForestRegressor
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class AISystemOptimizer:
    """AI-powered optimizer for task scheduling, system resources, and mental health pattern detection."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.model_file = data_dir / "ai_model.joblib"
        self.history_file = data_dir / "optimization_history.json"
        self.productivity_file = data_dir / "productivity_data.json"
        self.model = RandomForestRegressor(n_estimators=50, random_state=42) if HAS_SKLEARN else None
        self._model_fitted = False
        self.history: list[dict] = []
        self.productivity_data: list[dict] = []
        self._load_data()
        self._load_model()

    def _load_data(self):
        """Load history and productivity data."""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    self.history = json.load(f)
            except (OSError, json.JSONDecodeError):
                self.history = []

        if self.productivity_file.exists():
            try:
                with open(self.productivity_file) as f:
                    self.productivity_data = json.load(f)
            except (OSError, json.JSONDecodeError):
                self.productivity_data = []

    def _save_history(self):
        """Save optimization history."""
        with open(self.history_file, "w") as f:
            json.dump(self.history[-500:], f, default=str, indent=2)

    def _save_productivity(self):
        """Save productivity data."""
        with open(self.productivity_file, "w") as f:
            json.dump(self.productivity_data[-1000:], f, default=str, indent=2)

    def _load_model(self):
        """Load fitted model if available."""
        if HAS_SKLEARN and self.model_file.exists():
            try:
                self.model = joblib.load(self.model_file)
                self._model_fitted = True
            except (OSError, ValueError):
                self.model = RandomForestRegressor(n_estimators=50, random_state=42)

    def _save_model(self):
        """Save fitted model."""
        if HAS_SKLEARN and self._model_fitted:
            with contextlib.suppress(Exception):
                joblib.dump(self.model, self.model_file)

    # === Productivity Tracking ===

    def record_task_completion(self, task_data: dict):
        """Record when a task was completed for productivity analysis."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "energy_required": task_data.get("energy_required", 3),
            "priority": task_data.get("priority", 2),
            "duration_minutes": task_data.get("duration_minutes", 30),
            "category": task_data.get("category", "Other"),
            "mood_score": task_data.get("mood_score", 5),
            "energy_level": task_data.get("energy_level", 50),
        }
        self.productivity_data.append(entry)
        self._save_productivity()
        self._retrain_if_enough_data()

    def _retrain_if_enough_data(self):
        """Retrain the model if we have enough data."""
        if not HAS_SKLEARN or len(self.productivity_data) < 20:
            return

        try:
            x_matrix, targets = self._prepare_training_data()
            if len(x_matrix) >= 10:
                self.model.fit(x_matrix, targets)
                self._model_fitted = True
                self._save_model()
        except (ValueError, TypeError):
            logger = logging.getLogger(__name__)
            logger.exception("Model retraining failed")

    def _prepare_training_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Prepare training data from productivity history."""
        features = []
        targets = []
        for entry in self.productivity_data:
            features.append([
                entry.get("hour", 12),
                entry.get("day_of_week", 0),
                entry.get("energy_required", 3),
                entry.get("energy_level", 50),
                entry.get("mood_score", 5),
            ])
            # Target: task efficiency (inverse of duration for energy level)
            duration = max(entry.get("duration_minutes", 30), 1)
            targets.append(100.0 / duration)
        return np.array(features), np.array(targets)

    # === Peak Hour Analysis ===

    def get_peak_productivity_hours(self) -> list[dict]:
        """Analyze when the user is most productive."""
        if len(self.productivity_data) < 5:
            return self._default_peak_hours()

        hourly_counts: dict[int, list[float]] = {}
        for entry in self.productivity_data:
            hour = entry.get("hour", 12)
            duration = max(entry.get("duration_minutes", 30), 1)
            efficiency = 100.0 / duration
            hourly_counts.setdefault(hour, []).append(efficiency)

        peak_hours: list[dict[str, Any]] = []
        for hour, efficiencies in sorted(hourly_counts.items()):
            avg_eff = np.mean(efficiencies)
            count = len(efficiencies)
            peak_hours.append({
                "hour": hour,
                "average_efficiency": round(float(avg_eff), 2),
                "tasks_completed": count,
                "label": f"{hour:02d}:00",
            })

        peak_hours.sort(key=lambda x: x["average_efficiency"], reverse=True)
        return peak_hours

    def _default_peak_hours(self) -> list[dict]:
        """Default peak hours when insufficient data."""
        return [
            {"hour": 10, "average_efficiency": 80, "tasks_completed": 0, "label": "10:00 (estimated)"},
            {"hour": 14, "average_efficiency": 70, "tasks_completed": 0, "label": "14:00 (estimated)"},
            {"hour": 9, "average_efficiency": 75, "tasks_completed": 0, "label": "09:00 (estimated)"},
        ]

    # === Smart Task Ordering ===

    def suggest_task_order(self, tasks: list[dict], current_energy: int = 50, current_mood: int = 5) -> list[dict]:
        """Suggest optimal task ordering for the day based on energy and patterns."""
        current_hour = datetime.now().hour
        peak_hours = self.get_peak_productivity_hours()
        peak_hour_set = {h["hour"] for h in peak_hours[:3]}

        scored_tasks = []
        for task in tasks:
            score = 0.0
            energy_req = task.get("energy_required", 3)
            priority_val = task.get("priority", 2)

            # Priority boost
            score += priority_val * 20

            # Energy matching: high-energy tasks for high-energy times
            if current_hour in peak_hour_set and energy_req >= 3:
                score += 30
            elif current_hour not in peak_hour_set and energy_req <= 2:
                score += 25

            # Energy feasibility
            if energy_req * 20 <= current_energy:
                score += 20
            elif energy_req * 20 > current_energy:
                score -= 30

            # Due date urgency
            due_date = task.get("due_date")
            if due_date:
                try:
                    if isinstance(due_date, str):
                        due = datetime.fromisoformat(due_date).date()
                    else:
                        due = due_date
                    days_left = (due - datetime.now().date()).days
                    if days_left <= 0:
                        score += 50  # Overdue
                    elif days_left <= 1:
                        score += 40
                    elif days_left <= 3:
                        score += 20
                except (ValueError, TypeError):
                    pass

            scored_tasks.append({**task, "_score": score})

        scored_tasks.sort(key=lambda x: x["_score"], reverse=True)
        return scored_tasks

    def generate_daily_plan(self, tasks: list[dict], energy_level: int = 50, mood: int = 5) -> list[dict]:
        """Generate a suggested daily plan with time slots."""
        ordered = self.suggest_task_order(tasks, energy_level, mood)
        plan = []
        current_hour = max(datetime.now().hour, 8)

        for task in ordered[:8]:  # Max 8 tasks per day
            est_duration = task.get("estimated_minutes", 30)
            plan.append({
                "task": task.get("title", "Unknown"),
                "suggested_time": f"{current_hour:02d}:00",
                "estimated_duration": est_duration,
                "energy_required": task.get("energy_required", 3),
                "priority": task.get("priority", 2),
            })
            current_hour += max(1, est_duration // 60 + 1)
            if current_hour >= 22:
                break

        return plan

    # === Burnout Detection ===

    def detect_burnout_risk(self, recent_days: int = 7) -> dict:
        """Detect burnout risk based on task load and patterns."""
        cutoff = datetime.now() - timedelta(days=recent_days)
        recent = [
            e for e in self.productivity_data
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ] if self.productivity_data else []

        if not recent:
            return {"risk_level": "unknown", "score": 0, "message": "Not enough data to assess burnout risk."}

        daily_counts: dict[str, int] = {}
        daily_energy: dict[str, list[int]] = {}
        for entry in recent:
            day = entry["timestamp"][:10]
            daily_counts[day] = daily_counts.get(day, 0) + 1
            daily_energy.setdefault(day, []).append(entry.get("energy_level", 50))

        avg_tasks_per_day = np.mean(list(daily_counts.values())) if daily_counts else 0
        avg_energy = np.mean([np.mean(v) for v in daily_energy.values()]) if daily_energy else 50

        # Burnout score: high tasks + low energy = burnout
        score = 0
        if avg_tasks_per_day > 8:
            score += 30
        if avg_tasks_per_day > 12:
            score += 20
        if avg_energy < 30:
            score += 30
        if avg_energy < 20:
            score += 20

        # Check for declining energy trend
        energy_values = [np.mean(v) for v in daily_energy.values()]
        if len(energy_values) >= 3:
            trend = np.polyfit(range(len(energy_values)), energy_values, 1)[0]
            if trend < -3:
                score += 20

        if score >= 60:
            risk = "high"
            msg = "High burnout risk detected. Consider reducing your task load, taking breaks, and prioritizing self-care."
        elif score >= 30:
            risk = "moderate"
            msg = "Moderate burnout risk. Monitor your energy levels and take regular breaks."
        else:
            risk = "low"
            msg = "Burnout risk is low. Keep maintaining good balance."

        return {"risk_level": risk, "score": min(score, 100), "message": msg}

    # === Hypomania Detection (Bipolar Support) ===

    def detect_hypomania_signs(self, recent_days: int = 5) -> dict:
        """Detect potential hypomanic patterns for bipolar users."""
        cutoff = datetime.now() - timedelta(days=recent_days)
        recent = [
            e for e in self.productivity_data
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ] if self.productivity_data else []

        if len(recent) < 3:
            return {"detected": False, "score": 0, "message": "Not enough data."}

        signs = []
        score = 0

        # Unusually high task completion
        daily_counts: dict[str, int] = {}
        for entry in recent:
            day = entry["timestamp"][:10]
            daily_counts[day] = daily_counts.get(day, 0) + 1

        if daily_counts:
            max_daily = max(daily_counts.values())
            avg_daily = np.mean(list(daily_counts.values()))

            if max_daily > 15:
                score += 25
                signs.append("Unusually high number of tasks completed in a single day")

            if avg_daily > 10:
                score += 20
                signs.append("Sustained high productivity over multiple days")

        # Late-night activity
        late_night = [e for e in recent if e.get("hour", 12) >= 23 or e.get("hour", 12) <= 4]
        if len(late_night) > 3:
            score += 25
            signs.append("Significant late-night/early-morning activity")

        # Rapid task switching (many tasks in short time)
        timestamps = sorted([datetime.fromisoformat(e["timestamp"]) for e in recent])
        if len(timestamps) >= 5:
            gaps = [(timestamps[i+1] - timestamps[i]).seconds / 60 for i in range(len(timestamps)-1)]
            if np.mean(gaps) < 10:
                score += 15
                signs.append("Very rapid task switching")

        detected = score >= 40
        if detected:
            msg = ("Patterns consistent with elevated mood/hypomania detected. "
                   "This is informational - please discuss with your mental health provider. "
                   "Signs: " + "; ".join(signs))
        else:
            msg = "No concerning patterns detected."

        return {"detected": detected, "score": min(score, 100), "signs": signs, "message": msg}

    # === System Optimization (Original Features) ===

    def record_optimization(self, stats: dict, action: str, result: dict):
        """Record an optimization action."""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "action": action,
            "result": result,
        })
        self._save_history()

    def get_optimization_suggestions(self, current_stats: dict) -> list[str]:
        """Get system and task optimization suggestions."""
        suggestions = []

        # System resource suggestions
        cpu = current_stats.get("cpu_percent", 0)
        mem = current_stats.get("memory_percent", 0)
        disk = current_stats.get("disk_percent", 0)

        if cpu > 80:
            suggestions.append("High CPU usage detected. Consider closing resource-intensive applications.")
        if mem > 80:
            suggestions.append("High memory usage. Consider closing unused applications or browser tabs.")
        if disk > 90:
            suggestions.append("Low disk space. Consider cleaning up unnecessary files.")

        # Task-based suggestions
        task_count = current_stats.get("task_count", 0)
        if task_count > 10:
            suggestions.append("You have many pending tasks. Consider prioritizing or breaking them down.")
        if task_count > 20:
            suggestions.append("Task overload detected. Focus on your top 3 priorities today.")

        # Burnout check
        burnout = self.detect_burnout_risk()
        if burnout["risk_level"] in ("moderate", "high"):
            suggestions.append(burnout["message"])

        # Time-based suggestions
        hour = datetime.now().hour
        if hour >= 21:
            suggestions.append("It's getting late. Consider wrapping up and preparing for rest.")
        elif hour >= 14 and hour <= 15:
            suggestions.append("Afternoon energy dip is common. A short walk or breathing exercise can help.")

        if not suggestions:
            suggestions.append("Everything looks good! Keep up the great work.")

        return suggestions

    def predict_resource_usage(self, task_features: list[float]) -> float:
        """Predict resource usage for a task."""
        if not HAS_SKLEARN or not self._model_fitted or self.model is None:
            return 50.0

        try:
            x_matrix = np.array(task_features).reshape(1, -1)
            prediction = self.model.predict(x_matrix)[0]
            return float(np.clip(prediction, 0, 100))
        except (ValueError, TypeError):
            return 50.0

    def get_confidence_score(self) -> float:
        """Get confidence score for predictions based on data volume."""
        n = len(self.productivity_data)
        if n < 10:
            return 0.1
        elif n < 50:
            return 0.3 + (n - 10) * 0.01
        elif n < 200:
            return 0.7 + (n - 50) * 0.001
        else:
            return min(0.95, 0.85 + (n - 200) * 0.0001)
