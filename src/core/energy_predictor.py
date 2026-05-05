"""
ML-based energy level prediction engine.

Uses a RandomForestRegressor trained on historical user data to predict
energy levels throughout the day.  Falls back to a rule-based heuristic
when fewer than 7 days of data are available.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

try:
    import joblib
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False


# ---------------------------------------------------------------------------
# Enums & data-classes
# ---------------------------------------------------------------------------

class EnergyLevel(Enum):
    """Coarse energy buckets used by the scheduler."""
    VERY_LOW = "very_low"      # 0-20
    LOW = "low"                # 21-40
    MODERATE = "moderate"      # 41-60
    HIGH = "high"              # 61-80
    VERY_HIGH = "very_high"    # 81-100


class TaskEnergyRequirement(Enum):
    """How much energy a task demands."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


@dataclass
class EnergyDataPoint:
    """A single historical observation used for training."""
    timestamp: datetime
    energy_score: float           # 1-100
    time_of_day: float            # 0-23.99
    day_of_week: int              # 0=Mon .. 6=Sun
    sleep_hours: float
    sleep_quality: float          # 1-10
    mood_score: float             # 1-10
    tasks_completed_yesterday: int
    medication_taken: bool
    weather: str | None = None  # "sunny", "cloudy", "rainy", "snowy"
    exercise: bool = False


@dataclass
class EnergyPrediction:
    """A single energy prediction with metadata."""
    timestamp: datetime
    predicted_energy: float
    confidence: float             # 0-1
    energy_level: EnergyLevel
    source: str                   # "ml" or "rule_based"


@dataclass
class DailyEnergyCurve:
    """Predicted energy levels for every hour of a day."""
    date: datetime
    hourly_predictions: list[EnergyPrediction]
    peak_hour: int
    trough_hour: int
    description: str


@dataclass
class TaskTimingSuggestion:
    """Recommendation for when to schedule a task."""
    task_energy_requirement: TaskEnergyRequirement
    suggested_hours: list[int]
    reason: str


@dataclass
class FeatureImportanceResult:
    """Which features matter most for this user's energy."""
    feature_importances: dict[str, float]
    top_feature: str
    description: str


# ---------------------------------------------------------------------------
# Feature engineering helpers
# ---------------------------------------------------------------------------

_WEATHER_MAP = {"sunny": 0.0, "cloudy": 1.0, "rainy": 2.0, "snowy": 3.0}

_FEATURE_NAMES = [
    "time_of_day_sin",
    "time_of_day_cos",
    "day_of_week_sin",
    "day_of_week_cos",
    "sleep_hours",
    "sleep_quality",
    "mood_score",
    "tasks_completed_yesterday",
    "medication_taken",
    "weather_code",
    "exercise",
]


def _encode_features(dp: EnergyDataPoint) -> np.ndarray:
    """Convert a data point into a numeric feature vector."""
    hour_angle = 2 * np.pi * dp.time_of_day / 24.0
    dow_angle = 2 * np.pi * dp.day_of_week / 7.0

    return np.array([
        np.sin(hour_angle),
        np.cos(hour_angle),
        np.sin(dow_angle),
        np.cos(dow_angle),
        dp.sleep_hours,
        dp.sleep_quality,
        dp.mood_score,
        float(dp.tasks_completed_yesterday),
        1.0 if dp.medication_taken else 0.0,
        _WEATHER_MAP.get(dp.weather or "sunny", 0.0),
        1.0 if dp.exercise else 0.0,
    ], dtype=np.float64)


def _energy_to_level(energy: float) -> EnergyLevel:
    """Map a 1-100 energy score to a coarse level."""
    if energy <= 20:
        return EnergyLevel.VERY_LOW
    if energy <= 40:
        return EnergyLevel.LOW
    if energy <= 60:
        return EnergyLevel.MODERATE
    if energy <= 80:
        return EnergyLevel.HIGH
    return EnergyLevel.VERY_HIGH


def _parse_data_points(raw: Sequence[dict[str, Any]]) -> list[EnergyDataPoint]:
    """Convert a list of dicts into validated EnergyDataPoint objects."""
    points: list[EnergyDataPoint] = []
    for d in raw:
        ts = d.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif not isinstance(ts, datetime):
            continue

        points.append(EnergyDataPoint(
            timestamp=ts,
            energy_score=float(max(1, min(100, d.get("energy_score", 50)))),
            time_of_day=ts.hour + ts.minute / 60.0,
            day_of_week=ts.weekday(),
            sleep_hours=float(d.get("sleep_hours", 7.0)),
            sleep_quality=float(max(1, min(10, d.get("sleep_quality", 5)))),
            mood_score=float(max(1, min(10, d.get("mood_score", 5)))),
            tasks_completed_yesterday=int(d.get("tasks_completed_yesterday", 0)),
            medication_taken=bool(d.get("medication_taken", False)),
            weather=d.get("weather"),
            exercise=bool(d.get("exercise", False)),
        ))
    points.sort(key=lambda p: p.timestamp)
    return points


# ---------------------------------------------------------------------------
# Rule-based fallback predictor
# ---------------------------------------------------------------------------

class _RuleBasedPredictor:
    """Simple heuristic predictor used when ML model is unavailable."""

    # Typical circadian energy curve (hour -> multiplier 0-1)
    _CIRCADIAN = {
        0: 0.15, 1: 0.10, 2: 0.08, 3: 0.08, 4: 0.10, 5: 0.20,
        6: 0.40, 7: 0.55, 8: 0.70, 9: 0.80, 10: 0.90, 11: 0.85,
        12: 0.75, 13: 0.65, 14: 0.60, 15: 0.65, 16: 0.70, 17: 0.72,
        18: 0.65, 19: 0.55, 20: 0.45, 21: 0.35, 22: 0.25, 23: 0.18,
    }

    def predict(self, dp: EnergyDataPoint) -> float:
        """Predict energy using heuristics."""
        hour = int(dp.time_of_day) % 24
        base = self._CIRCADIAN.get(hour, 0.5) * 100

        # Sleep adjustment
        sleep_delta = (dp.sleep_hours - 7.0) * 3.0  # +-3 per hour away from 7
        base += sleep_delta

        # Sleep quality adjustment
        base += (dp.sleep_quality - 5.0) * 2.0

        # Mood influence
        base += (dp.mood_score - 5.0) * 1.5

        # Exercise boost
        if dp.exercise:
            base += 8.0

        # Medication (mild boost if taken)
        if dp.medication_taken:
            base += 3.0

        # Weather
        weather_adjust = {"sunny": 3.0, "cloudy": 0.0, "rainy": -3.0, "snowy": -2.0}
        base += weather_adjust.get(dp.weather or "sunny", 0.0)

        return float(max(1, min(100, base)))


# ---------------------------------------------------------------------------
# Main predictor
# ---------------------------------------------------------------------------

class EnergyPredictor:
    """Predict energy levels using ML with rule-based fallback.

    Parameters
    ----------
    model_dir : Path or str, optional
        Directory where trained models are persisted.
    min_samples_for_ml : int
        Minimum number of data points before the ML model is used.
    """

    MIN_SAMPLES_ML = 7  # 7 days worth of data

    def __init__(
        self,
        model_dir: Path | None = None,
        min_samples_for_ml: int = MIN_SAMPLES_ML,
    ) -> None:
        self._model_dir = Path(model_dir) if model_dir else None
        self._min_samples = min_samples_for_ml
        self._model: Any | None = None  # RandomForestRegressor
        self._scaler: Any | None = None  # StandardScaler
        self._rule_predictor = _RuleBasedPredictor()
        self._training_data: list[EnergyDataPoint] = []
        self._is_trained = False

        if self._model_dir:
            self._try_load_model()

    # -- training --------------------------------------------------------------

    def add_data(self, raw_entries: Sequence[dict[str, Any]]) -> None:
        """Add historical data points for training."""
        new_points = _parse_data_points(raw_entries)
        self._training_data.extend(new_points)
        # Deduplicate by timestamp
        seen = set()
        unique: list[EnergyDataPoint] = []
        for p in self._training_data:
            key = p.timestamp.isoformat()
            if key not in seen:
                seen.add(key)
                unique.append(p)
        self._training_data = sorted(unique, key=lambda p: p.timestamp)

    def train(self) -> bool:
        """Train (or retrain) the model on accumulated data.

        Returns True if the ML model was trained, False if falling back to rules.
        """
        if len(self._training_data) < self._min_samples or not _HAS_SKLEARN:
            self._is_trained = False
            return False

        features_matrix = np.array([_encode_features(dp) for dp in self._training_data])
        targets = np.array([dp.energy_score for dp in self._training_data])

        self._scaler = StandardScaler()
        features_scaled = self._scaler.fit_transform(features_matrix)

        self._model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )
        self._model.fit(features_scaled, targets)
        self._is_trained = True

        if self._model_dir:
            self._save_model()

        return True

    # -- prediction ------------------------------------------------------------

    def predict_single(self, data: dict[str, Any]) -> EnergyPrediction:
        """Predict energy for a single data point."""
        points = _parse_data_points([data])
        if not points:
            now = datetime.now()
            return EnergyPrediction(
                timestamp=now,
                predicted_energy=50.0,
                confidence=0.0,
                energy_level=EnergyLevel.MODERATE,
                source="default",
            )
        dp = points[0]
        return self._predict_point(dp)

    def predict_next_hour(self, current_state: dict[str, Any]) -> EnergyPrediction:
        """Predict energy level one hour from now."""
        points = _parse_data_points([current_state])
        if not points:
            return self.predict_single(current_state)
        dp = points[0]
        # Shift time forward by 1 hour
        future_ts = dp.timestamp + timedelta(hours=1)
        future_dp = EnergyDataPoint(
            timestamp=future_ts,
            energy_score=dp.energy_score,
            time_of_day=future_ts.hour + future_ts.minute / 60.0,
            day_of_week=future_ts.weekday(),
            sleep_hours=dp.sleep_hours,
            sleep_quality=dp.sleep_quality,
            mood_score=dp.mood_score,
            tasks_completed_yesterday=dp.tasks_completed_yesterday,
            medication_taken=dp.medication_taken,
            weather=dp.weather,
            exercise=dp.exercise,
        )
        pred = self._predict_point(future_dp)
        pred.timestamp = future_ts
        return pred

    def predict_rest_of_day(self, current_state: dict[str, Any]) -> list[EnergyPrediction]:
        """Predict energy for each remaining hour of the day."""
        points = _parse_data_points([current_state])
        if not points:
            return []
        dp = points[0]
        current_hour = int(dp.time_of_day)
        predictions: list[EnergyPrediction] = []

        for h in range(current_hour + 1, 24):
            future_ts = dp.timestamp.replace(hour=h, minute=0, second=0, microsecond=0)
            future_dp = EnergyDataPoint(
                timestamp=future_ts,
                energy_score=dp.energy_score,
                time_of_day=float(h),
                day_of_week=dp.day_of_week,
                sleep_hours=dp.sleep_hours,
                sleep_quality=dp.sleep_quality,
                mood_score=dp.mood_score,
                tasks_completed_yesterday=dp.tasks_completed_yesterday,
                medication_taken=dp.medication_taken,
                weather=dp.weather,
                exercise=dp.exercise,
            )
            predictions.append(self._predict_point(future_dp))
        return predictions

    def predict_tomorrow(self, current_state: dict[str, Any]) -> DailyEnergyCurve:
        """Predict a full energy curve for tomorrow."""
        points = _parse_data_points([current_state])
        if not points:
            tomorrow = datetime.now() + timedelta(days=1)
            return DailyEnergyCurve(
                date=tomorrow,
                hourly_predictions=[],
                peak_hour=10,
                trough_hour=3,
                description="Insufficient data to predict tomorrow's energy.",
            )
        dp = points[0]
        tomorrow = dp.timestamp + timedelta(days=1)
        tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        predictions: list[EnergyPrediction] = []

        for h in range(24):
            ts = tomorrow_start.replace(hour=h)
            future_dp = EnergyDataPoint(
                timestamp=ts,
                energy_score=dp.energy_score,
                time_of_day=float(h),
                day_of_week=ts.weekday(),
                sleep_hours=dp.sleep_hours,
                sleep_quality=dp.sleep_quality,
                mood_score=dp.mood_score,
                tasks_completed_yesterday=dp.tasks_completed_yesterday,
                medication_taken=dp.medication_taken,
                weather=dp.weather,
                exercise=dp.exercise,
            )
            predictions.append(self._predict_point(future_dp))

        energies = [p.predicted_energy for p in predictions]
        peak_hour = int(np.argmax(energies))
        trough_hour = int(np.argmin(energies))

        return DailyEnergyCurve(
            date=tomorrow_start,
            hourly_predictions=predictions,
            peak_hour=peak_hour,
            trough_hour=trough_hour,
            description=(
                f"Tomorrow your energy is predicted to peak around {peak_hour}:00 "
                f"({energies[peak_hour]:.0f}/100) and dip around {trough_hour}:00 "
                f"({energies[trough_hour]:.0f}/100)."
            ),
        )

    # -- scheduling suggestions -----------------------------------------------

    def suggest_task_timing(
        self,
        current_state: dict[str, Any],
    ) -> list[TaskTimingSuggestion]:
        """Suggest optimal hours for tasks at different energy levels."""
        rest_of_day = self.predict_rest_of_day(current_state)
        if not rest_of_day:
            return [
                TaskTimingSuggestion(
                    TaskEnergyRequirement.HIGH, [10, 11],
                    "Default suggestion: mornings tend to be best for demanding tasks.",
                ),
                TaskTimingSuggestion(
                    TaskEnergyRequirement.MODERATE, [14, 15, 16],
                    "Default suggestion: afternoons for moderate tasks.",
                ),
                TaskTimingSuggestion(
                    TaskEnergyRequirement.LOW, [20, 21],
                    "Default suggestion: evenings for light tasks.",
                ),
            ]

        hour_energy = {p.timestamp.hour: p.predicted_energy for p in rest_of_day}
        sorted_hours = sorted(hour_energy.keys(), key=lambda h: hour_energy[h], reverse=True)

        high_hours = [h for h in sorted_hours if hour_energy[h] >= 65][:4]
        mod_hours = [h for h in sorted_hours if 35 <= hour_energy[h] < 65][:4]
        low_hours = [h for h in sorted_hours if hour_energy[h] < 35][:4]

        suggestions = []
        if high_hours:
            suggestions.append(TaskTimingSuggestion(
                TaskEnergyRequirement.HIGH,
                sorted(high_hours),
                f"Your energy is predicted to be highest around {high_hours[0]}:00. "
                "Schedule demanding tasks then.",
            ))
        if mod_hours:
            suggestions.append(TaskTimingSuggestion(
                TaskEnergyRequirement.MODERATE,
                sorted(mod_hours),
                "These hours are predicted to have moderate energy — "
                "good for routine tasks.",
            ))
        if low_hours:
            suggestions.append(TaskTimingSuggestion(
                TaskEnergyRequirement.LOW,
                sorted(low_hours),
                "Energy is predicted to dip during these hours — "
                "save easy, low-focus tasks.",
            ))

        return suggestions

    # -- feature importance ----------------------------------------------------

    def feature_importance(self) -> FeatureImportanceResult:
        """Return which features most affect this user's energy predictions."""
        if not self._is_trained or self._model is None:
            return FeatureImportanceResult(
                feature_importances={},
                top_feature="sleep_hours",
                description="Model not yet trained. Sleep is generally the top predictor.",
            )

        importances = self._model.feature_importances_
        imp_dict: dict[str, float] = {}
        for name, val in zip(_FEATURE_NAMES, importances, strict=False):
            imp_dict[name] = round(float(val), 4)

        # Sort descending
        imp_dict = dict(sorted(imp_dict.items(), key=lambda kv: kv[1], reverse=True))
        top = next(iter(imp_dict))

        readable = top.replace("_sin", "").replace("_cos", "").replace("_", " ").title()
        return FeatureImportanceResult(
            feature_importances=imp_dict,
            top_feature=top,
            description=f"The feature that most affects your energy is '{readable}'.",
        )

    # -- confidence -----------------------------------------------------------

    def _prediction_confidence(self, dp: EnergyDataPoint) -> float:
        """Estimate confidence in a prediction.

        Based on amount of training data and whether conditions match
        historical patterns.
        """
        n = len(self._training_data)
        if n == 0:
            return 0.2

        # Base confidence from data volume (max at 90 data points)
        base = min(n / 90.0, 1.0) * 0.7

        # Bonus for ML model
        if self._is_trained:
            base += 0.15

        # Check how many training points share the same day-of-week
        same_dow = sum(1 for p in self._training_data if p.day_of_week == dp.day_of_week)
        if same_dow >= 4:
            base += 0.1

        # Check how many training points are in the same time-of-day window
        same_tod = sum(
            1 for p in self._training_data
            if abs(p.time_of_day - dp.time_of_day) < 2.0
        )
        if same_tod >= 4:
            base += 0.05

        return min(base, 1.0)

    # -- internal prediction ---------------------------------------------------

    def _predict_point(self, dp: EnergyDataPoint) -> EnergyPrediction:
        """Run prediction through ML or rule-based engine."""
        confidence = self._prediction_confidence(dp)

        if self._is_trained and self._model is not None and self._scaler is not None:
            features = _encode_features(dp).reshape(1, -1)
            features_scaled = self._scaler.transform(features)
            raw_pred = self._model.predict(features_scaled)[0]
            energy = float(max(1, min(100, raw_pred)))
            source = "ml"
        else:
            energy = self._rule_predictor.predict(dp)
            source = "rule_based"

        return EnergyPrediction(
            timestamp=dp.timestamp,
            predicted_energy=round(energy, 1),
            confidence=round(confidence, 2),
            energy_level=_energy_to_level(energy),
            source=source,
        )

    # -- persistence -----------------------------------------------------------

    def _model_path(self) -> Path:
        if self._model_dir is None:
            raise ValueError("No model directory configured.")
        return self._model_dir / "energy_model.joblib"

    def _scaler_path(self) -> Path:
        if self._model_dir is None:
            raise ValueError("No model directory configured.")
        return self._model_dir / "energy_scaler.joblib"

    def _save_model(self) -> None:
        """Persist the trained model and scaler to disk."""
        if not _HAS_SKLEARN or self._model_dir is None:
            return
        self._model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, self._model_path())
        joblib.dump(self._scaler, self._scaler_path())

    def _try_load_model(self) -> None:
        """Load a previously saved model if it exists."""
        if not _HAS_SKLEARN or self._model_dir is None:
            return
        model_path = self._model_path()
        scaler_path = self._scaler_path()
        if model_path.exists() and scaler_path.exists():
            try:
                self._model = joblib.load(model_path)
                self._scaler = joblib.load(scaler_path)
                self._is_trained = True
            except (OSError, ValueError):
                self._is_trained = False

    @property
    def is_ml_active(self) -> bool:
        """Whether the ML model is currently being used for predictions."""
        return self._is_trained

    @property
    def data_point_count(self) -> int:
        """Number of training data points loaded."""
        return len(self._training_data)
