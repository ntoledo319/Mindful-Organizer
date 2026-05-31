"""
Display Adaptation Engine

Dynamically adjusts display settings (brightness, colour temperature,
system theme) based on:
- Time of day (circadian rhythm)
- Current energy level
- Current mood
- Detected psychological state (anxiety, burnout, etc.)

This is "f.lux that knows your mind" — not just the sun.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from core.platform_actions import PlatformBackend, get_backend

logger = logging.getLogger(__name__)


@dataclass
class DisplayProfile:
    """A complete display configuration."""

    brightness: int  # 0-100
    night_shift_intensity: int  # 0-100
    night_shift_enabled: bool
    system_theme: str  # "dark" | "light"
    reason: str = ""


class DisplayAdaptationEngine:
    """Adapts display settings based on psychological and temporal context."""

    def __init__(self, backend: PlatformBackend | None = None) -> None:
        self.backend = backend or get_backend()

    # -- public API -----------------------------------------------------------

    def adapt(
        self,
        energy_score: float | None = None,
        mood_score: float | None = None,
        anxiety_detected: bool = False,
        burnout_risk: str = "low",
        sleep_hours: float | None = None,
        manual_override: DisplayProfile | None = None,
    ) -> DisplayProfile:
        """Compute and apply the optimal display profile for current state.

        If *manual_override* is given, it is applied directly (for user
        customisation or scheduled profiles).
        """
        if manual_override is not None:
            profile = manual_override
        else:
            profile = self._compute_profile(
                energy_score, mood_score, anxiety_detected, burnout_risk, sleep_hours
            )

        self._apply_profile(profile)
        return profile

    def adapt_for_condition(self, condition: str) -> DisplayProfile:
        """Apply a display preset tailored to a specific condition."""
        presets: dict[str, DisplayProfile] = {
            "anxiety": DisplayProfile(
                brightness=35,
                night_shift_intensity=90,
                night_shift_enabled=True,
                system_theme="dark",
                reason="Anxiety-sensitive: dim, warm, dark",
            ),
            "depression": DisplayProfile(
                brightness=60,
                night_shift_intensity=40,
                night_shift_enabled=True,
                system_theme="light",
                reason="Depression-supportive: bright, warm, light",
            ),
            "adhd_focus": DisplayProfile(
                brightness=80,
                night_shift_intensity=0,
                night_shift_enabled=False,
                system_theme="dark",
                reason="ADHD focus: bright, cool, dark",
            ),
            "ptsd": DisplayProfile(
                brightness=30,
                night_shift_intensity=95,
                night_shift_enabled=True,
                system_theme="dark",
                reason="PTSD-sensitive: very dim, very warm",
            ),
            "sleep_prep": DisplayProfile(
                brightness=15,
                night_shift_intensity=100,
                night_shift_enabled=True,
                system_theme="dark",
                reason="Sleep preparation: minimal blue light",
            ),
            "burnout": DisplayProfile(
                brightness=25,
                night_shift_intensity=85,
                night_shift_enabled=True,
                system_theme="dark",
                reason="Burnout recovery: minimal stimulation",
            ),
        }
        profile = presets.get(condition.lower(), self._default_profile())
        self._apply_profile(profile)
        return profile

    def restore_default(self) -> DisplayProfile:
        """Restore a sensible default display profile."""
        profile = self._default_profile()
        self._apply_profile(profile)
        return profile

    # -- computation ----------------------------------------------------------

    def _compute_profile(
        self,
        energy_score: float | None,
        mood_score: float | None,
        anxiety_detected: bool,
        burnout_risk: str,
        sleep_hours: float | None,
    ) -> DisplayProfile:
        now = datetime.now()
        hour = now.hour

        # Base profile from circadian rhythm
        profile = self._circadian_profile(hour)

        # Adjust for energy
        if energy_score is not None:
            profile = self._adjust_for_energy(profile, energy_score)

        # Adjust for mood
        if mood_score is not None:
            profile = self._adjust_for_mood(profile, mood_score)

        # Anxiety overrides everything toward calm
        if anxiety_detected:
            profile.brightness = min(profile.brightness, 35)
            profile.night_shift_intensity = max(profile.night_shift_intensity, 85)
            profile.night_shift_enabled = True
            profile.system_theme = "dark"
            profile.reason += " + anxiety override"

        # Burnout risk dims further
        if burnout_risk in ("moderate", "high"):
            profile.brightness = min(profile.brightness, 30)
            profile.night_shift_intensity = max(profile.night_shift_intensity, 80)
            profile.reason += f" + burnout ({burnout_risk})"

        # Sleep debt -> warmer, dimmer
        if sleep_hours is not None and sleep_hours < 5:
            profile.brightness = min(profile.brightness, 30)
            profile.night_shift_intensity = 100
            profile.reason += " + sleep debt"

        return profile

    def _circadian_profile(self, hour: int) -> DisplayProfile:
        """Base display profile based on time of day."""
        # Night: 22:00-06:00
        if hour >= 22 or hour < 6:
            return DisplayProfile(
                brightness=20,
                night_shift_intensity=90,
                night_shift_enabled=True,
                system_theme="dark",
                reason="Night time",
            )
        # Early morning: 06:00-09:00
        if 6 <= hour < 9:
            return DisplayProfile(
                brightness=50,
                night_shift_intensity=40,
                night_shift_enabled=True,
                system_theme="light",
                reason="Early morning",
            )
        # Morning: 09:00-12:00
        if 9 <= hour < 12:
            return DisplayProfile(
                brightness=80,
                night_shift_intensity=0,
                night_shift_enabled=False,
                system_theme="light",
                reason="Morning",
            )
        # Afternoon: 12:00-17:00
        if 12 <= hour < 17:
            return DisplayProfile(
                brightness=75,
                night_shift_intensity=10,
                night_shift_enabled=False,
                system_theme="light",
                reason="Afternoon",
            )
        # Evening: 17:00-22:00
        return DisplayProfile(
            brightness=50,
            night_shift_intensity=60,
            night_shift_enabled=True,
            system_theme="dark",
            reason="Evening",
        )

    def _adjust_for_energy(self, profile: DisplayProfile, energy: float) -> DisplayProfile:
        """Brighten for high energy, dim for low energy."""
        if energy >= 7:
            profile.brightness = max(profile.brightness, 75)
            profile.reason += f" + high energy ({energy:.0f})"
        elif energy <= 3:
            profile.brightness = min(profile.brightness, 35)
            profile.reason += f" + low energy ({energy:.0f})"
        return profile

    def _adjust_for_mood(self, profile: DisplayProfile, mood: float) -> DisplayProfile:
        """Warm display for low mood, bright for good mood."""
        if mood <= 3:
            # Low mood: warmer, slightly brighter than energy would suggest
            profile.night_shift_intensity = max(profile.night_shift_intensity, 50)
            profile.night_shift_enabled = True
            profile.reason += f" + low mood ({mood:.0f})"
        elif mood >= 8:
            # Good mood: crisp, bright
            profile.night_shift_intensity = min(profile.night_shift_intensity, 20)
            profile.reason += f" + good mood ({mood:.0f})"
        return profile

    def _default_profile(self) -> DisplayProfile:
        return DisplayProfile(
            brightness=60,
            night_shift_intensity=30,
            night_shift_enabled=False,
            system_theme="light",
            reason="Default",
        )

    # -- application ----------------------------------------------------------

    def _apply_profile(self, profile: DisplayProfile) -> None:
        logger.info("Applying display profile: %s", profile.reason)
        self.backend.set_display_brightness(profile.brightness)
        self.backend.set_night_shift(
            profile.night_shift_intensity,
            enabled=profile.night_shift_enabled,
        )
        self.backend.set_system_theme(profile.system_theme)
