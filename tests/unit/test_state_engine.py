"""The State Engine composes the room to the person — the core differentiator."""

from dataclasses import dataclass
from datetime import datetime

from gui import state_engine


@dataclass
class _Snap:
    mood_score: float | None = None
    energy_score: float | None = None
    sleep_hours: float | None = None


def test_no_data_receives_without_interrogating():
    state = state_engine.compute_state(None, None, 0)
    assert state.has_data is False
    comp = state_engine.compose(state, "Alex")
    assert "Alex" in comp.line1
    assert comp.primary_tab == "mood_tracker"  # invite a first signal, gently


def test_depleted_state_keeps_it_small_and_dims():
    snap = _Snap(mood_score=3, energy_score=2, sleep_hours=5)
    state = state_engine.compute_state(snap, None, 2)
    assert state.is_depleted
    comp = state_engine.compose(state, "Alex", 2)
    assert "small" in comp.line2.lower()
    assert comp.primary_tab == "breathing"  # one soft thing, not a task list
    assert comp.glow < 0.5  # the room dims when energy is low


def test_steady_state_opens_the_day():
    snap = _Snap(mood_score=7, energy_score=7, sleep_hours=7)
    state = state_engine.compute_state(snap, None, 1)
    assert not state.is_depleted
    comp = state_engine.compose(state, "Alex", 1)
    assert comp.primary_tab == "task_manager"
    assert comp.glow > 0.5  # brighter ember when there's energy


def test_glow_tracks_energy():
    low = state_engine.compose(state_engine.compute_state(_Snap(5, 1, 7), None, 0)).glow
    high = state_engine.compose(state_engine.compute_state(_Snap(5, 10, 7), None, 0)).glow
    assert high > low


def test_night_greeting_reads_naturally():
    night = datetime(2026, 6, 4, 23, 30)
    state = state_engine.compute_state(_Snap(7, 7, 7), None, 0, now=night)
    assert state.part_of_day == "night"
    comp = state_engine.compose(state, "Alex")
    # never the ungrammatical "Good late"
    assert "good late" not in comp.line1.lower()


def test_caption_is_forgiving_about_pending_tasks():
    state = state_engine.compute_state(_Snap(6, 6, 7), None, 3)
    comp = state_engine.compose(state, "Alex", 3)
    assert "3" in comp.caption and "no rush" in comp.caption.lower()
    comp0 = state_engine.compose(state_engine.compute_state(_Snap(6, 6, 7), None, 0), "Alex", 0)
    assert "yours" in comp0.caption.lower()  # nothing due -> the time is yours
