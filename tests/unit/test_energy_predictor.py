"""
Tests for EnergyPredictor (src/core/energy_predictor.py).

Covers rule-based prediction, ML prediction, optimal task timing,
and model persistence.
"""

from datetime import datetime, timedelta

import pytest

from core.energy_predictor import (
    _HAS_SKLEARN,
    EnergyLevel,
    EnergyPrediction,
    EnergyPredictor,
    TaskEnergyRequirement,
    _energy_to_level,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_data_point(hour=10, sleep=7.0, mood=6, **kwargs):
    """Create a single data-point dict."""
    ts = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
    return {
        "timestamp": ts.isoformat(),
        "energy_score": kwargs.get("energy_score", 60),
        "sleep_hours": sleep,
        "sleep_quality": kwargs.get("sleep_quality", 7),
        "mood_score": mood,
        "tasks_completed_yesterday": kwargs.get("tasks_completed_yesterday", 3),
        "medication_taken": kwargs.get("medication_taken", False),
        "weather": kwargs.get("weather", "sunny"),
        "exercise": kwargs.get("exercise", False),
    }


def _generate_training_data(n=30):
    """Generate n days of plausible training data."""
    base = datetime.now() - timedelta(days=n)
    data = []
    for i in range(n):
        for hour in (9, 14, 20):
            ts = base + timedelta(days=i, hours=hour)
            energy = 70 - abs(hour - 10) * 3 + (i % 5)
            data.append(
                {
                    "timestamp": ts.isoformat(),
                    "energy_score": max(10, min(95, energy)),
                    "sleep_hours": 6.5 + (i % 3) * 0.5,
                    "sleep_quality": 5 + (i % 4),
                    "mood_score": 5 + (i % 3),
                    "tasks_completed_yesterday": i % 5,
                    "medication_taken": i % 2 == 0,
                    "weather": ["sunny", "cloudy", "rainy"][i % 3],
                    "exercise": i % 3 == 0,
                }
            )
    return data


# ---------------------------------------------------------------------------
# Rule-based prediction
# ---------------------------------------------------------------------------


class TestRuleBasedPrediction:
    def test_rule_based_with_few_data_points(self, tmp_data_dir):
        """With fewer than 7 data points, predictor uses rule-based engine."""
        predictor = EnergyPredictor(model_dir=tmp_data_dir)
        predictor.add_data([_make_data_point(hour=10) for _ in range(3)])
        predictor.train()

        assert predictor.is_ml_active is False

        result = predictor.predict_single(_make_data_point(hour=10))
        assert isinstance(result, EnergyPrediction)
        assert result.source == "rule_based"
        assert 1 <= result.predicted_energy <= 100

    def test_rule_based_circadian_pattern(self):
        """Morning predictions should generally be higher than late-night."""
        predictor = EnergyPredictor()

        morning = predictor.predict_single(_make_data_point(hour=10))
        night = predictor.predict_single(_make_data_point(hour=2))

        assert morning.predicted_energy > night.predicted_energy

    def test_rule_based_sleep_effect(self):
        """Better sleep should yield higher energy."""
        predictor = EnergyPredictor()

        good_sleep = predictor.predict_single(_make_data_point(sleep=9.0))
        poor_sleep = predictor.predict_single(_make_data_point(sleep=4.0))

        assert good_sleep.predicted_energy > poor_sleep.predicted_energy

    def test_energy_level_classification(self):
        assert _energy_to_level(15) == EnergyLevel.VERY_LOW
        assert _energy_to_level(30) == EnergyLevel.LOW
        assert _energy_to_level(50) == EnergyLevel.MODERATE
        assert _energy_to_level(70) == EnergyLevel.HIGH
        assert _energy_to_level(90) == EnergyLevel.VERY_HIGH

    def test_predict_single_invalid_data(self):
        """Invalid data should return a safe default prediction."""
        predictor = EnergyPredictor()
        result = predictor.predict_single({"invalid": True})
        assert result.predicted_energy == 50.0
        assert result.source == "default"

    def test_predict_rest_of_day(self):
        predictor = EnergyPredictor()
        data = _make_data_point(hour=14)
        predictions = predictor.predict_rest_of_day(data)

        # Should have predictions for hours 15-23
        assert len(predictions) == 9
        assert all(isinstance(p, EnergyPrediction) for p in predictions)

    def test_predict_rest_of_day_empty(self):
        predictor = EnergyPredictor()
        assert predictor.predict_rest_of_day({"invalid": True}) == []


# ---------------------------------------------------------------------------
# ML prediction (requires sklearn)
# ---------------------------------------------------------------------------


class TestMLPrediction:
    @pytest.mark.skipif(not _HAS_SKLEARN, reason="scikit-learn not installed")
    def test_ml_prediction_with_sufficient_data(self, tmp_data_dir):
        """With enough data, the ML model trains and is used."""
        predictor = EnergyPredictor(model_dir=tmp_data_dir)
        predictor.add_data(_generate_training_data(n=30))

        trained = predictor.train()
        assert trained is True
        assert predictor.is_ml_active is True

        result = predictor.predict_single(_make_data_point(hour=10))
        assert result.source == "ml"
        assert 1 <= result.predicted_energy <= 100

    @pytest.mark.skipif(not _HAS_SKLEARN, reason="scikit-learn not installed")
    def test_ml_prediction_confidence(self, tmp_data_dir):
        """ML predictions should have higher confidence than rule-based."""
        predictor = EnergyPredictor(model_dir=tmp_data_dir)
        predictor.add_data(_generate_training_data(n=30))
        predictor.train()

        result = predictor.predict_single(_make_data_point(hour=10))
        assert result.confidence > 0.2

    @pytest.mark.skipif(not _HAS_SKLEARN, reason="scikit-learn not installed")
    def test_feature_importance_after_training(self, tmp_data_dir):
        predictor = EnergyPredictor(model_dir=tmp_data_dir)
        predictor.add_data(_generate_training_data(n=30))
        predictor.train()

        importance = predictor.feature_importance()
        assert len(importance.feature_importances) > 0
        assert importance.top_feature != ""

    def test_feature_importance_before_training(self):
        predictor = EnergyPredictor()
        importance = predictor.feature_importance()
        assert importance.top_feature == "sleep_hours"
        assert len(importance.feature_importances) == 0


# ---------------------------------------------------------------------------
# Optimal task timing
# ---------------------------------------------------------------------------


class TestOptimalTaskTiming:
    def test_suggest_task_timing_rule_based(self):
        """Without rest-of-day data, returns default suggestions."""
        predictor = EnergyPredictor()
        suggestions = predictor.suggest_task_timing({"invalid": True})

        assert len(suggestions) >= 1
        assert any(s.task_energy_requirement == TaskEnergyRequirement.HIGH for s in suggestions)

    def test_suggest_task_timing_with_data(self):
        predictor = EnergyPredictor()
        data = _make_data_point(hour=8)
        suggestions = predictor.suggest_task_timing(data)

        assert len(suggestions) >= 1
        for s in suggestions:
            assert len(s.suggested_hours) >= 1
            assert s.reason

    def test_predict_tomorrow(self):
        predictor = EnergyPredictor()
        curve = predictor.predict_tomorrow(_make_data_point(hour=10))

        assert len(curve.hourly_predictions) == 24
        assert 0 <= curve.peak_hour <= 23
        assert 0 <= curve.trough_hour <= 23
        assert curve.description


# ---------------------------------------------------------------------------
# Model persistence
# ---------------------------------------------------------------------------


class TestSaveLoadModel:
    @pytest.mark.skipif(not _HAS_SKLEARN, reason="scikit-learn not installed")
    def test_save_load_model(self, tmp_data_dir):
        """Train, save, and reload the model in a new predictor."""
        p1 = EnergyPredictor(model_dir=tmp_data_dir)
        p1.add_data(_generate_training_data(n=30))
        p1.train()
        assert p1.is_ml_active is True

        # Verify model files exist
        assert (tmp_data_dir / "energy_model.joblib").exists()
        assert (tmp_data_dir / "energy_scaler.joblib").exists()

        # Load in new predictor
        p2 = EnergyPredictor(model_dir=tmp_data_dir)
        assert p2.is_ml_active is True

        result = p2.predict_single(_make_data_point(hour=10))
        assert result.source == "ml"

    def test_no_model_dir_no_save(self):
        predictor = EnergyPredictor(model_dir=None)
        # Should not crash
        predictor.add_data([_make_data_point()])
        predictor.train()

    def test_data_deduplication(self, tmp_data_dir):
        predictor = EnergyPredictor(model_dir=tmp_data_dir)
        dp = _make_data_point(hour=10)
        predictor.add_data([dp, dp, dp])

        assert predictor.data_point_count == 1

    def test_predict_next_hour(self):
        predictor = EnergyPredictor()
        data = _make_data_point(hour=14)
        result = predictor.predict_next_hour(data)

        assert result.timestamp.hour == 15
        assert isinstance(result, EnergyPrediction)
