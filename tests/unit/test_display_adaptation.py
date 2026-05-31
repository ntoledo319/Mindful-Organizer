"""Tests for the Display Adaptation Engine."""

from __future__ import annotations

from core.display_adaptation import DisplayAdaptationEngine, DisplayProfile
from core.platform_actions import StubBackend


class TestCircadianProfile:
    """Test time-of-day based display profiles."""

    def test_night_profile(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        profile = engine._circadian_profile(2)
        assert profile.brightness <= 25
        assert profile.night_shift_enabled is True
        assert profile.system_theme == "dark"

    def test_morning_profile(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        profile = engine._circadian_profile(10)
        assert profile.brightness >= 75
        assert profile.night_shift_enabled is False
        assert profile.system_theme == "light"

    def test_evening_profile(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        profile = engine._circadian_profile(19)
        assert profile.night_shift_enabled is True
        assert profile.system_theme == "dark"


class TestEnergyAdjustment:
    """Test energy-based display adjustments."""

    def test_high_energy_brightens(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        base = DisplayProfile(
            brightness=50, night_shift_intensity=30, night_shift_enabled=False, system_theme="light"
        )
        adjusted = engine._adjust_for_energy(base, 8)
        assert adjusted.brightness >= 75

    def test_low_energy_dims(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        base = DisplayProfile(
            brightness=50, night_shift_intensity=30, night_shift_enabled=False, system_theme="light"
        )
        adjusted = engine._adjust_for_energy(base, 2)
        assert adjusted.brightness <= 35


class TestMoodAdjustment:
    """Test mood-based display adjustments."""

    def test_low_mood_enables_warmth(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        base = DisplayProfile(
            brightness=50, night_shift_intensity=0, night_shift_enabled=False, system_theme="light"
        )
        adjusted = engine._adjust_for_mood(base, 2)
        assert adjusted.night_shift_enabled is True
        assert adjusted.night_shift_intensity >= 50

    def test_good_mood_reduces_warmth(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        base = DisplayProfile(
            brightness=50, night_shift_intensity=50, night_shift_enabled=True, system_theme="light"
        )
        adjusted = engine._adjust_for_mood(base, 9)
        assert adjusted.night_shift_intensity <= 20


class TestConditionPresets:
    """Test condition-specific display presets."""

    def test_anxiety_preset(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        profile = engine.adapt_for_condition("anxiety")
        assert profile.brightness <= 40
        assert profile.night_shift_enabled is True
        assert profile.system_theme == "dark"

    def test_adhd_focus_preset(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        profile = engine.adapt_for_condition("adhd_focus")
        assert profile.brightness >= 75
        assert profile.night_shift_enabled is False

    def test_sleep_prep_preset(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        profile = engine.adapt_for_condition("sleep_prep")
        assert profile.brightness <= 20
        assert profile.night_shift_intensity == 100

    def test_unknown_condition_fallback(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        profile = engine.adapt_for_condition("nonexistent")
        assert profile.system_theme == "light"  # default


class TestFullAdaptation:
    """Test the complete adaptation pipeline."""

    def test_anxiety_overrides_energy(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        profile = engine.adapt(
            energy_score=8,  # would normally be bright
            mood_score=7,
            anxiety_detected=True,
        )
        assert profile.brightness <= 35  # anxiety overrides high energy
        assert profile.system_theme == "dark"

    def test_sleep_debt_dims(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        profile = engine.adapt(
            energy_score=6,
            sleep_hours=3,
        )
        assert profile.brightness <= 30
        assert profile.night_shift_intensity == 100

    def test_manual_override_bypasses_computation(self):
        engine = DisplayAdaptationEngine(backend=StubBackend())
        manual = DisplayProfile(
            brightness=99, night_shift_intensity=0, night_shift_enabled=False, system_theme="light"
        )
        profile = engine.adapt(energy_score=2, manual_override=manual)
        assert profile.brightness == 99
